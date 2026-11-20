"""Mathematical impact quantification engine unit tests.

Contains 20 comprehensive unit tests covering all commute modalities,
boundary conditions, particulate avoidance math, and carbon abatement calculations.
"""

from backend.constants import (
    BERKELEY_EARTH_UG_PER_CIGARETTE,
    EMISSION_FACTORS_KG_CO2E_PER_KM,
)
from backend.models.schemas import CommuteMode, UserProfile
from backend.services.impact_calculator import calculate_quantified_impact


def test_standard_ice_car_commuter():
    """Tests standard petrol/diesel car commuter in heavy winter smog."""
    profile = UserProfile(
        location="Delhi-NCR",
        commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR,
        daily_commute_km=20.0,
    )
    ledger = calculate_quantified_impact(profile, ambient_pm25=300.0)
    assert ledger.daily_pm25_avoided_micrograms > 100.0
    assert ledger.daily_carbon_abatement_kg_co2e > 0.0


def test_shared_carpool_commuter():
    """Tests 3+ person shared carpool commute modality."""
    profile = UserProfile(commute_mode=CommuteMode.SHARED_CARPOOL, daily_commute_km=25.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=250.0)
    assert ledger.daily_carbon_abatement_kg_co2e >= 0.0


def test_two_wheeler_commuter():
    """Tests motorcycle/scooter commute modality."""
    profile = UserProfile(commute_mode=CommuteMode.TWO_WHEELER, daily_commute_km=15.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=220.0)
    assert ledger.daily_carbon_abatement_kg_co2e > 0.0


def test_metro_public_transit_commuter():
    """Tests metro/train transit user who already has low baseline emissions."""
    profile = UserProfile(commute_mode=CommuteMode.METRO_PUBLIC_TRANSIT, daily_commute_km=30.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=280.0)
    assert ledger.daily_carbon_abatement_kg_co2e >= 0.0
    assert ledger.daily_pm25_avoided_micrograms > 0.0


def test_electric_vehicle_commuter():
    """Tests electric vehicle (EV) driver."""
    profile = UserProfile(commute_mode=CommuteMode.ELECTRIC_VEHICLE, daily_commute_km=20.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=200.0)
    assert ledger.daily_carbon_abatement_kg_co2e >= 0.0


def test_walking_cycling_commuter():
    """Tests active commuter whose carbon footprint is already zero."""
    profile = UserProfile(commute_mode=CommuteMode.WALKING_CYCLING, daily_commute_km=4.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=180.0)
    assert ledger.daily_carbon_abatement_kg_co2e == 0.0
    assert ledger.daily_pm25_avoided_micrograms > 0.0


def test_remote_wfh_commuter():
    """Tests remote home-based worker."""
    profile = UserProfile(commute_mode=CommuteMode.REMOTE_WFH, daily_commute_km=0.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=220.0)
    assert ledger.daily_carbon_abatement_kg_co2e == 0.0
    assert ledger.daily_pm25_avoided_micrograms > 0.0


def test_zero_distance_commute_boundary():
    """Verifies boundary condition when commute distance is exactly 0 km."""
    profile = UserProfile(daily_commute_km=0.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=150.0)
    assert ledger.daily_carbon_abatement_kg_co2e == 0.0


def test_maximum_distance_commute_boundary():
    """Verifies boundary condition at upper limit (200 km daily commute)."""
    profile = UserProfile(daily_commute_km=200.0, commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR)
    ledger = calculate_quantified_impact(profile, ambient_pm25=300.0)
    assert ledger.daily_carbon_abatement_kg_co2e > 25.0


def test_low_ambient_pm25_boundary():
    """Verifies model behavior under clean baseline air (PM2.5 = 10 ug/m3)."""
    profile = UserProfile(daily_commute_km=10.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=10.0)
    assert ledger.daily_pm25_avoided_micrograms >= 0.0
    assert ledger.cigarette_smoke_equivalents_avoided >= 0.0


def test_extreme_hazardous_pm25_boundary():
    """Verifies model stability under apocalyptic pollution (PM2.5 = 600 ug/m3)."""
    profile = UserProfile(daily_commute_km=15.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=600.0)
    assert ledger.daily_pm25_avoided_micrograms > 500.0
    assert ledger.cigarette_smoke_equivalents_avoided > 1.0


def test_berkeley_earth_conversion_exactness():
    """Verifies that cigarette equivalence strictly uses 396.0 ug/cigarette."""
    profile = UserProfile(daily_commute_km=12.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=250.0)
    expected = round(ledger.daily_pm25_avoided_micrograms / BERKELEY_EARTH_UG_PER_CIGARETTE, 1)
    assert ledger.cigarette_smoke_equivalents_avoided == expected


def test_respiratory_stress_index_range():
    """Verifies that the respiratory stress reduction index is bounded between 0 and 100%."""
    for pm25 in [20.0, 100.0, 300.0, 500.0]:
        profile = UserProfile()
        ledger = calculate_quantified_impact(profile, ambient_pm25=pm25)
        assert 0.0 <= ledger.respiratory_stress_index_reduction <= 100.0


def test_community_annual_multiplier():
    """Verifies that community scaling accurately aggregates across 100 households over 365 days."""
    profile = UserProfile(daily_commute_km=15.0, commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR)
    ledger = calculate_quantified_impact(profile, ambient_pm25=250.0)
    expected_community = round(ledger.daily_carbon_abatement_kg_co2e * 100 * 365, 0)
    assert ledger.annualized_community_co2_savings_kg == expected_community


def test_impact_narrative_contains_key_metrics():
    """Verifies that the generated impact narrative contains all quantified metrics."""
    profile = UserProfile(daily_commute_km=18.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=315.0)
    narrative = ledger.impact_narrative
    assert "µg" in narrative or "ug" in narrative.lower()
    assert "cigarettes" in narrative
    assert "CO2e" in narrative


def test_emission_factors_consistency():
    """Verifies that every CommuteMode enum has a valid emission factor."""
    for mode in CommuteMode:
        assert mode.value in EMISSION_FACTORS_KG_CO2E_PER_KM
        assert EMISSION_FACTORS_KG_CO2E_PER_KM[mode.value] >= 0.0


def test_ice_car_highest_emission_factor():
    """Verifies that internal combustion cars have the highest per-passenger emission factor."""
    ice_factor = EMISSION_FACTORS_KG_CO2E_PER_KM[CommuteMode.INTERNAL_COMBUSTION_CAR.value]
    assert ice_factor > EMISSION_FACTORS_KG_CO2E_PER_KM[CommuteMode.METRO_PUBLIC_TRANSIT.value]
    assert ice_factor > EMISSION_FACTORS_KG_CO2E_PER_KM[CommuteMode.ELECTRIC_VEHICLE.value]


def test_zero_avoidance_non_negative():
    """Verifies that avoided values never become negative even if baseline is tiny."""
    profile = UserProfile(daily_commute_km=0.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=0.0)
    assert ledger.daily_pm25_avoided_micrograms >= 0.0
    assert ledger.daily_carbon_abatement_kg_co2e >= 0.0


def test_high_efficiency_routine_scaling():
    """Verifies that higher adopted routine reduction percentage yields higher PM2.5 avoidance."""
    profile = UserProfile()
    ledger_low = calculate_quantified_impact(
        profile, ambient_pm25=300.0, adopted_routine_pm25_reduction_pct=30.0
    )
    ledger_high = calculate_quantified_impact(
        profile, ambient_pm25=300.0, adopted_routine_pm25_reduction_pct=85.0
    )
    assert ledger_high.daily_pm25_avoided_micrograms >= ledger_low.daily_pm25_avoided_micrograms


def test_clean_commute_toggle():
    """Verifies impact ledger generation when user maintains clean commute."""
    profile = UserProfile(commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR, daily_commute_km=25.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=280.0, adopted_clean_commute=True)
    assert ledger.daily_carbon_abatement_kg_co2e > 0.0


def test_adopted_clean_commute_false_yields_zero_carbon_savings():
    """Verifies that if user does not adopt clean commute, carbon abatement is strictly 0.0."""
    profile = UserProfile(commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR, daily_commute_km=30.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=300.0, adopted_clean_commute=False)
    assert ledger.daily_carbon_abatement_kg_co2e == 0.0


def test_extreme_ambient_pm25_boundary_800():
    """Verifies calculation stability under extreme emergency PM2.5 levels (800 ug/m3)."""
    profile = UserProfile(daily_commute_km=15.0)
    ledger = calculate_quantified_impact(profile, ambient_pm25=800.0)
    assert ledger.daily_pm25_avoided_micrograms > 500.0
    assert ledger.cigarette_smoke_equivalents_avoided > 1.0
    assert ledger.respiratory_stress_index_reduction > 0.0


def test_commute_exact_maximum_limit_200km():
    """Verifies calculation at exact maximum commute boundary (200.0 km)."""
    profile = UserProfile(
        commute_mode=CommuteMode.INTERNAL_COMBUSTION_CAR,
        daily_commute_km=200.0,
    )
    ledger = calculate_quantified_impact(profile, ambient_pm25=250.0)
    assert ledger.daily_carbon_abatement_kg_co2e > 0.0
    assert ledger.annualized_community_co2_savings_kg > 0.0
