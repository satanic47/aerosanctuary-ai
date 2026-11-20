"""
Deterministic rules engine and peer-reviewed indoor air quality (IAQ) hacks.

Provides scientifically validated interventions based on atmospheric physics,
building science, and environmental medicine guidelines.
"""

from backend.constants import (
    CLEAN_TRANSIT_BASELINE_FACTOR,
    EMISSION_FACTORS_KG_CO2E_PER_KM,
    EVENING_RUSH_EXPOSURE_REDUCTION_PCT,
    MIDDAY_VENTILATION_EXPOSURE_REDUCTION_PCT,
    MORNING_INVERSION_EXPOSURE_REDUCTION_PCT,
    TIME_SLOT_EVENING,
    TIME_SLOT_MIDDAY,
    TIME_SLOT_MORNING,
)
from backend.models.schemas import (
    AirQualitySnapshot,
    CommuteMode,
    HouseholdType,
    IndoorHack,
    RoutineRecommendation,
    UserProfile,
)

# ============================================================================
# Curated, Peer-Reviewed Indoor Air Quality (IAQ) Hacks
# ============================================================================

CURATED_INDOOR_HACKS: list[IndoorHack] = [
    IndoorHack(
        id="hack-corsi-rosenthal",
        title="DIY Corsi-Rosenthal Cube Air Purifier",
        category="diy_filtration",
        problem_addressed="Commercial HEPA air purifiers are expensive (₹15,000 - ₹35,000) and have small Clean Air Delivery Rates (CADR) for large living areas.",
        materials_needed=[
            "1x 20-inch standard box fan (₹1,400)",
            "4x MERV 13 furnace filters (20x20x2 inch) (₹1,600 total)",
            "1x 20x20 cardboard sheet for bottom seal",
            "Duct tape / Gorilla tape for airtight perimeter sealing",
            "Cardboard shroud cutout (14-inch diameter circle)",
        ],
        estimated_cost_inr=3000,
        step_by_step_instructions=[
            "Assemble the four MERV 13 filters into a square cube with airflow direction arrows pointing INWARD.",
            "Tape all four vertical corners securely using duct tape, ensuring zero gaps for unfiltered air bypass.",
            "Tape the bottom cardboard base securely to seal the cube.",
            "Mount the 20-inch box fan on top, blowing UPWARD (exhausting clean air into the room).",
            "Tape the circular cardboard shroud onto the fan face to eliminate blade-tip aerodynamic recirculation.",
            "Run continuously on medium speed; cleans a 500 sq ft living room with ~550 m³/h CADR.",
        ],
        expected_pm25_reduction="85% - 92% CADR equivalent indoor PM2.5 reduction within 45 minutes of operation",
        scientific_basis="UC Davis Department of Civil and Environmental Engineering & US EPA peer-reviewed bioaerosol filtration testing (2021).",
    ),
    IndoorHack(
        id="hack-botanical-biofilter",
        title="Targeted NASA Phytoremediation Botanical Arrangement",
        category="botanical",
        problem_addressed="Stagnant indoor air accumulates volatile organic compounds (VOCs), formaldehyde, and benzene during winter window lockdown.",
        materials_needed=[
            "3x Snake Plants (Sansevieria trifasciata) per bedroom (₹600)",
            "2x Areca Palms (Dypsis lutescens) per living area (₹700)",
            "Damp microfiber dusting cloth for weekly leaf stomata cleaning",
        ],
        estimated_cost_inr=1300,
        step_by_step_instructions=[
            "Place Sansevieria inside bedrooms; it performs Crassulacean Acid Metabolism (CAM), absorbing CO2 and releasing oxygen during nocturnal sleep hours.",
            "Position Areca Palms in living quarters with ambient daylight to transpire moisture and capture coarse suspended dust particles.",
            "Wipe plant leaves gently with clean damp microfiber cloth every 5 days; settled particulate crust blocks stomatal gas exchange.",
            "Avoid overwatering in winter to prevent indoor mold and fungal spore proliferation.",
        ],
        expected_pm25_reduction="Aids VOC removal (20-30%) and naturally optimizes relative humidity to settle airborne dust.",
        scientific_basis="NASA Clean Air Study (Wolverton et al., 1989) on phytoremediation of indoor air pollutants.",
    ),
    IndoorHack(
        id="hack-inversion-ventilation",
        title="Solar Midday Inversion Breakup Ventilation Window",
        category="ventilation_timing",
        problem_addressed="Opening windows at dawn or during morning rush hour introduces peak nocturnal radiation inversion pollution directly into indoor rooms.",
        materials_needed=[
            "Weatherstripping rubber foam tape for door/window frames (₹250)",
            "Door draft stopper snakes (₹200)",
        ],
        estimated_cost_inr=450,
        step_by_step_instructions=[
            "Keep all windows and external doors strictly sealed between 06:00 AM and 11:30 AM when radiation inversion holds ground pollution captive.",
            "Open opposite-facing windows for 15-20 minutes strictly between 12:30 PM and 03:00 PM when solar ground heating expands the atmospheric boundary layer.",
            "Reseal all windows firmly before 04:30 PM before evening temperature drops initiate the secondary nocturnal inversion.",
            "Inspect and replace door draft stoppers to stop cold outdoor draft infiltration.",
        ],
        expected_pm25_reduction="Prevents indoor PM2.5 spikes of 250+ ug/m3 from early morning ventilation mistakes.",
        scientific_basis="Atmospheric Boundary Layer (ABL) thermal mixing dynamics and radiation inversion physics.",
    ),
    IndoorHack(
        id="hack-microfiber-damp-cleaning",
        title="Electrostatic Wet Microfiber Dust & PM2.5 Abatement",
        category="source_control",
        problem_addressed="Dry sweeping with traditional brooms resuspends toxic settled fine particles directly into breathing zones.",
        materials_needed=[
            "Microfiber flat mop with reusable washable pads (₹450)",
            "Diluted organic soap water or clean water",
        ],
        estimated_cost_inr=450,
        step_by_step_instructions=[
            "Ban dry broom sweeping entirely during severe winter AQI episodes.",
            "Use a damp electrostatic microfiber pad to capture fine particulate matter via electrostatic and capillary adhesion.",
            "Mop twice daily in high-traffic hallways and children's play areas.",
            "Launder microfiber pads immediately in hot water to permanently trap heavy metal particles.",
        ],
        expected_pm25_reduction="Prevents secondary airborne PM2.5 resuspension spikes of up to 120 ug/m3",
        scientific_basis="Aerosol Science and Technology empirical studies on indoor human-induced dust resuspension and aerodynamic particle detachment.",
    ),
]


# ============================================================================
# Modular Routine Recommendation Construction Helpers
# ============================================================================


def _create_routine(
    time_slot: str,
    activity: str,
    hazard_rationale: str,
    recommended_alternative: str,
    pm25_exposure_reduction_percent: float,
    emission_saved_kg_co2e: float = 0.0,
) -> RoutineRecommendation:
    """Factory helper to construct a valid, clean RoutineRecommendation object."""
    return RoutineRecommendation(
        time_slot=time_slot,
        activity=activity,
        hazard_rationale=hazard_rationale,
        recommended_alternative=recommended_alternative,
        pm25_exposure_reduction_percent=pm25_exposure_reduction_percent,
        emission_saved_kg_co2e=emission_saved_kg_co2e,
    )


def _build_morning_routine(profile: UserProfile) -> RoutineRecommendation:
    """Constructs morning routine adapted to household vulnerability."""
    is_vulnerable = profile.household_type in [
        HouseholdType.FAMILY_WITH_KIDS,
        HouseholdType.ASTHMA_RESPIRATORY_VULNERABLE,
        HouseholdType.ELDERLY_RESIDENTS,
    ]

    if is_vulnerable:
        return _create_routine(
            time_slot=TIME_SLOT_MORNING,
            activity="Morning Exercise / School Departure (Kids & Vulnerable)",
            hazard_rationale="Peak nocturnal thermal inversion traps vehicle exhaust and biomass smoke at surface level; outdoor exercise increases PM2.5 intake tenfold.",
            recommended_alternative="Shift aerobic cardio indoors using air-filtered space. Equip school children with certified N95 masks; avoid open e-rickshaws or walking beside high-traffic arterials.",
            pm25_exposure_reduction_percent=MORNING_INVERSION_EXPOSURE_REDUCTION_PCT,
            emission_saved_kg_co2e=0.0,
        )

    return _create_routine(
        time_slot=TIME_SLOT_MORNING,
        activity="Morning Jog / Outdoor Fitness",
        hazard_rationale="Deep breathing during inversion peaks deposits ultra-fine particles directly into bloodstream capillary beds.",
        recommended_alternative="Replace outdoor morning run with home bodyweight/yoga workout or indoor stationary cycling.",
        pm25_exposure_reduction_percent=90.0,
        emission_saved_kg_co2e=0.0,
    )


def _build_commute_routine(profile: UserProfile) -> RoutineRecommendation:
    """Constructs morning commute routine adapted to transit modality."""
    commute_key = profile.commute_mode.value
    baseline_factor = EMISSION_FACTORS_KG_CO2E_PER_KM.get(commute_key, 0.192)

    is_high_emission_commute = profile.commute_mode in [
        CommuteMode.INTERNAL_COMBUSTION_CAR,
        CommuteMode.TWO_WHEELER,
    ]

    if is_high_emission_commute:
        saved_co2 = round(
            max(0.0, profile.daily_commute_km * (baseline_factor - CLEAN_TRANSIT_BASELINE_FACTOR)),
            2,
        )
        return _create_routine(
            time_slot="Morning Commute (08:30 - 10:00 AM)",
            activity=f"Work Transit ({profile.daily_commute_km} km single occupancy)",
            hazard_rationale="Idling in congested winter traffic exposes commuters to acute NO2 and black carbon plumes inside vehicular micro-environments.",
            recommended_alternative="Shift to Metro/electric transit or coordinate a 3-person neighborhood carpool. Set vehicle AC to internal recirculation mode.",
            pm25_exposure_reduction_percent=65.0,
            emission_saved_kg_co2e=saved_co2,
        )

    return _create_routine(
        time_slot="Morning Commute (08:30 - 10:00 AM)",
        activity="Transit to Work / Study",
        hazard_rationale="Exposure at open platforms or bus stops during rush-hour congestion.",
        recommended_alternative="Maintain your low-emission commute mode (Metro/EV/WFH). Wear a snug N95 respirator on platforms.",
        pm25_exposure_reduction_percent=70.0,
        emission_saved_kg_co2e=0.5,
    )


def _build_afternoon_ventilation_routine(air_quality: AirQualitySnapshot) -> RoutineRecommendation:
    """Constructs midday ventilation and outdoor movement routine."""
    return _create_routine(
        time_slot=f"Midday Dispersion Window ({TIME_SLOT_MIDDAY})",
        activity="Outdoor Errands, Walking & Air Refresh",
        hazard_rationale="Indoor CO2 builds up when rooms remain sealed all day, causing cognitive fatigue and lethargy.",
        recommended_alternative=f"Take advantage of the solar boundary layer expansion ({air_quality.safest_outdoor_window}) for essential outdoor tasks and a 15-minute cross-ventilation air flush.",
        pm25_exposure_reduction_percent=MIDDAY_VENTILATION_EXPOSURE_REDUCTION_PCT,
        emission_saved_kg_co2e=0.1,
    )


def _build_evening_domestic_routine() -> RoutineRecommendation:
    """Constructs evening domestic protection and cooking routine."""
    return _create_routine(
        time_slot=f"Evening Domestic Hours ({TIME_SLOT_EVENING})",
        activity="Cooking, Heating & Window Sealing",
        hazard_rationale="Temperature plunges initiate the second nocturnal inversion. Deep frying or biomass heating can spike indoor PM2.5 past 600 ug/m3.",
        recommended_alternative="Seal all exterior windows by 5:30 PM. Use induction cooking or keep kitchen exhaust fans on high with kitchen doors closed. Avoid incense and mosquito coils.",
        pm25_exposure_reduction_percent=EVENING_RUSH_EXPOSURE_REDUCTION_PCT,
        emission_saved_kg_co2e=0.8,
    )


def generate_tailored_routines(
    profile: UserProfile, air_quality: AirQualitySnapshot
) -> list[RoutineRecommendation]:
    """Assembles chronologically sequenced low-emission, health-protective routines.

    Args:
        profile: Family profile, vulnerability tier, and commute modality.
        air_quality: Ambient air quality and inversion state.

    Returns:
        Chronological list of four targeted diurnal recommendations.
    """
    return [
        _build_morning_routine(profile),
        _build_commute_routine(profile),
        _build_afternoon_ventilation_routine(air_quality),
        _build_evening_domestic_routine(),
    ]
