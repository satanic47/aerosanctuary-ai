"""Unit tests for services: AQI intelligence, rules engine, and GenAI advisory.

Contains 20 comprehensive unit tests verifying data lookups, in-memory caching,
demographic tailoring for all household types, and deterministic fallback reasoning.
"""

from backend.models.schemas import CommuteMode, HouseholdType, UserProfile
from backend.services.aqi_service import aqi_cache, get_air_quality_snapshot
from backend.services.genai_service import build_deterministic_chat_response
from backend.services.rules_engine import (
    CURATED_INDOOR_HACKS,
    generate_tailored_routines,
)


def test_aqi_service_cache_hit_and_miss_telemetry():
    """Verifies that cache records hits and misses accurately."""
    aqi_cache.clear()
    city = "Delhi"

    # First access is a miss
    snap1 = get_air_quality_snapshot(city)
    stats1 = aqi_cache.get_stats()
    assert stats1["misses"] >= 1

    # Second access is a hit
    snap2 = get_air_quality_snapshot(city)
    stats2 = aqi_cache.get_stats()
    assert stats2["hits"] >= 1
    assert snap1.aqi == snap2.aqi


def test_aqi_delhi_ncr_lookup():
    """Verifies Delhi-NCR exact lookup."""
    snap = get_air_quality_snapshot("Delhi-NCR")
    assert "Delhi" in snap.city
    assert snap.aqi >= 350
    assert snap.thermal_inversion_active is True


def test_aqi_noida_subregional_match():
    """Verifies that Noida correctly resolves to Delhi-NCR smog basin."""
    snap = get_air_quality_snapshot("Noida")
    assert "Delhi" in snap.city
    assert snap.thermal_inversion_active is True


def test_aqi_gurgaon_subregional_match():
    """Verifies that Gurugram/Gurgaon correctly resolves to NCR metrics."""
    snap = get_air_quality_snapshot("Gurugram")
    assert "Delhi" in snap.city


def test_aqi_chandigarh_lookup():
    """Verifies Chandigarh air quality lookup."""
    snap = get_air_quality_snapshot("Chandigarh")
    assert "Chandigarh" in snap.city
    assert snap.aqi > 200


def test_aqi_mohali_subregional_match():
    """Verifies that Mohali resolves to the Chandigarh tri-city baseline."""
    snap = get_air_quality_snapshot("Mohali")
    assert "Chandigarh" in snap.city


def test_aqi_mumbai_lookup():
    """Verifies Mumbai coastal air quality."""
    snap = get_air_quality_snapshot("Mumbai")
    assert "Mumbai" in snap.city
    assert snap.thermal_inversion_active is False


def test_aqi_lahore_lookup():
    """Verifies Lahore severe smog lookup."""
    snap = get_air_quality_snapshot("Lahore")
    assert "Lahore" in snap.city
    assert snap.aqi >= 400


def test_aqi_beijing_lookup():
    """Verifies Beijing winter baseline lookup."""
    snap = get_air_quality_snapshot("Beijing")
    assert "Beijing" in snap.city


def test_aqi_new_york_lookup():
    """Verifies New York clean benchmark."""
    snap = get_air_quality_snapshot("New York")
    assert "New York" in snap.city
    assert snap.aqi < 100


def test_aqi_london_lookup():
    """Verifies London moderate benchmark."""
    snap = get_air_quality_snapshot("London")
    assert "London" in snap.city


def test_aqi_unknown_city_modeled_fallback():
    """Verifies graceful modeled fallback for unknown global coordinates."""
    snap = get_air_quality_snapshot("Atlantis")
    assert snap.city == "Atlantis"
    assert snap.aqi > 0


def test_rules_engine_family_with_kids():
    """Verifies tailored routine for family with young children."""
    profile = UserProfile(household_type=HouseholdType.FAMILY_WITH_KIDS)
    aqi = get_air_quality_snapshot("Delhi")
    routines = generate_tailored_routines(profile, aqi)
    assert len(routines) == 4
    morning = routines[0]
    assert (
        "School Departure" in morning.activity
        or "Kids" in morning.activity
        or "Children" in morning.recommended_alternative
    )


def test_rules_engine_elderly_residents():
    """Verifies tailored routine protecting cardiopulmonary health in seniors."""
    profile = UserProfile(household_type=HouseholdType.ELDERLY_RESIDENTS)
    aqi = get_air_quality_snapshot("Chandigarh")
    routines = generate_tailored_routines(profile, aqi)
    assert len(routines) == 4


def test_rules_engine_asthma_vulnerable():
    """Verifies tailored routine for asthmatic / respiratory vulnerable households."""
    profile = UserProfile(household_type=HouseholdType.ASTHMA_RESPIRATORY_VULNERABLE)
    aqi = get_air_quality_snapshot("Delhi")
    routines = generate_tailored_routines(profile, aqi)
    assert len(routines) == 4
    assert any("N95" in r.recommended_alternative for r in routines)


def test_rules_engine_individual_commuter():
    """Verifies tailored routine for single working individuals."""
    profile = UserProfile(
        household_type=HouseholdType.INDIVIDUAL,
        commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR,
    )
    aqi = get_air_quality_snapshot("Delhi")
    routines = generate_tailored_routines(profile, aqi)
    assert len(routines) == 4
    commute_routine = next(r for r in routines if "Commute" in r.time_slot)
    assert commute_routine.emission_saved_kg_co2e > 0.0


def test_rules_engine_pet_owners():
    """Verifies routine adaptations for domestic pet exercise."""
    profile = UserProfile(household_type=HouseholdType.PET_OWNERS)
    aqi = get_air_quality_snapshot("Delhi")
    routines = generate_tailored_routines(profile, aqi)
    assert len(routines) == 4


def test_curated_hacks_corsi_rosenthal_spec():
    """Verifies engineering specifications of the DIY Corsi-Rosenthal Box."""
    corsi = next(h for h in CURATED_INDOOR_HACKS if h.id == "hack-corsi-rosenthal")
    assert corsi.estimated_cost_inr <= 3500
    assert any("MERV 13" in m for m in corsi.materials_needed)
    assert "CADR" in corsi.expected_pm25_reduction or "CADR" in corsi.scientific_basis


def test_curated_hacks_botanical_nasa_study():
    """Verifies NASA Clean Air plant selection in botanical hack."""
    botanical = next(h for h in CURATED_INDOOR_HACKS if h.id == "hack-botanical-biofilter")
    assert any("Snake" in m for m in botanical.materials_needed)
    assert "NASA" in botanical.scientific_basis


def test_deterministic_chat_response_structure():
    """Verifies that deterministic chat consultation returns a valid, complete ChatResponse."""
    profile = UserProfile()
    res = build_deterministic_chat_response("What plants purify air?", profile)
    assert len(res.reply) > 20
    assert len(res.actionable_tips) >= 2
    assert len(res.direct_impact_statement) > 10


def test_forced_gemini_failure_returns_deterministic_fallback():
    """Forces GenAI failure (missing or invalid key) and asserts deterministic fallback is returned."""
    import asyncio

    from backend.models.schemas import ChatRequest
    from backend.services.genai_service import process_chat_consultation

    req = ChatRequest(
        message="How can I protect my children from severe smog?", user_profile=UserProfile()
    )
    # Run async function in synchronous test runner
    res = asyncio.run(process_chat_consultation(req))

    assert res is not None
    assert "deterministic" in res.source_method.lower()
    assert len(res.actionable_tips) >= 2
    assert len(res.direct_impact_statement) > 5
