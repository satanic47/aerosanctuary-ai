"""
Mathematical impact quantification engine for AeroSanctuary AI.

Computes exact particulate matter (PM2.5) exposure avoidance,
cigarette equivalence, greenhouse gas abatement (kg CO2e),
and respiratory inflammatory risk reduction using empirical environmental health models.
"""

from backend.constants import (
    BASELINE_INDOOR_EXPOSURE_HOURS,
    BASELINE_INDOOR_INFILTRATION_RATIO,
    BASELINE_OUTDOOR_EXPOSURE_HOURS,
    BERKELEY_EARTH_UG_PER_CIGARETTE,
    CLEAN_TRANSIT_BASELINE_FACTOR,
    COMMUNITY_HOUSEHOLD_SCALE,
    DAYS_PER_YEAR,
    DEFAULT_ADOPTED_ROUTINE_REDUCTION_PCT,
    DEFAULT_BASELINE_CAR_EMISSION_FACTOR,
    EMISSION_FACTORS_KG_CO2E_PER_KM,
    MAX_OUTDOOR_MITIGATION_FRACTION,
    OUTDOOR_SCHEDULE_MITIGATION_SCALE,
    PROTECTED_INDOOR_EXPOSURE_HOURS,
    PROTECTED_OUTDOOR_EXPOSURE_HOURS,
    TRANSIT_MODE_SWITCH_SAVINGS_RATIO,
    VENTILATION_RATE_OUTDOOR_COMMUTE_M3_PER_HR,
    VENTILATION_RATE_RESTING_INDOORS_M3_PER_HR,
)
from backend.models.schemas import CommuteMode, QuantifiedImpactLedger, UserProfile


def calculate_quantified_impact(
    profile: UserProfile,
    ambient_pm25: float,
    adopted_routine_pm25_reduction_pct: float = DEFAULT_ADOPTED_ROUTINE_REDUCTION_PCT,
    adopted_clean_commute: bool = True,
) -> QuantifiedImpactLedger:
    """Calculates health and environmental outcomes resulting from adopted recommendations.

    Args:
        profile: The user's environmental profile and commute modality.
        ambient_pm25: Current ambient PM2.5 concentration in ug/m3.
        adopted_routine_pm25_reduction_pct: Percentage of indoor/outdoor exposure curtailed
            through schedule adjustments and DIY filtration (0.0 to 100.0).
        adopted_clean_commute: Whether user shifted to lower emission commute modes.

    Returns:
        QuantifiedImpactLedger with mathematically derived exposure reductions and carbon abatement.
    """
    # Clamp PM2.5 to non-negative range
    ambient_pm25 = max(0.0, ambient_pm25)

    # 1. Baseline Daily Inhalation (Unprotected Exposure):
    # Typical baseline: outdoor commute transit + indoor dwelling without active filtration
    baseline_indoor_pm25 = ambient_pm25 * BASELINE_INDOOR_INFILTRATION_RATIO
    unprotected_intake_ug = (
        BASELINE_OUTDOOR_EXPOSURE_HOURS * VENTILATION_RATE_OUTDOOR_COMMUTE_M3_PER_HR * ambient_pm25
    ) + (
        BASELINE_INDOOR_EXPOSURE_HOURS
        * VENTILATION_RATE_RESTING_INDOORS_M3_PER_HR
        * baseline_indoor_pm25
    )

    # 2. Protected Daily Inhalation with User-Adopted Routine & IAQ Hacks:
    # Wire adopted_routine_pm25_reduction_pct directly into exposure mitigation
    clamped_reduction_pct = min(100.0, max(0.0, adopted_routine_pm25_reduction_pct))
    reduction_fraction = clamped_reduction_pct / 100.0

    # Indoor concentration curtailed by filtration and window seals
    protected_indoor_pm25 = baseline_indoor_pm25 * (1.0 - reduction_fraction)
    # Outdoor transit exposure curtailed by certified N95 masking + midday solar inversion breakup shift
    outdoor_mitigation_fraction = min(
        MAX_OUTDOOR_MITIGATION_FRACTION,
        reduction_fraction * OUTDOOR_SCHEDULE_MITIGATION_SCALE,
    )
    protected_outdoor_pm25 = ambient_pm25 * (1.0 - outdoor_mitigation_fraction)

    # Active routine reduces outdoor exposure time to protected duration
    protected_intake_ug = (
        PROTECTED_OUTDOOR_EXPOSURE_HOURS
        * VENTILATION_RATE_OUTDOOR_COMMUTE_M3_PER_HR
        * protected_outdoor_pm25
    ) + (
        PROTECTED_INDOOR_EXPOSURE_HOURS
        * VENTILATION_RATE_RESTING_INDOORS_M3_PER_HR
        * protected_indoor_pm25
    )

    pm25_avoided_ug = max(0.0, round(unprotected_intake_ug - protected_intake_ug, 1))

    # Cigarette equivalence avoided via Berkeley Earth formula (396 ug PM2.5 = 1 cigarette)
    cigs_avoided = round(pm25_avoided_ug / BERKELEY_EARTH_UG_PER_CIGARETTE, 1)

    # 3. Daily Carbon Footprint Abatement (kg CO2e):
    # Wire adopted_clean_commute directly into vehicle emission delta
    commute_key = profile.commute_mode.value
    baseline_commute_factor = EMISSION_FACTORS_KG_CO2E_PER_KM.get(
        commute_key, DEFAULT_BASELINE_CAR_EMISSION_FACTOR
    )

    if adopted_clean_commute and profile.daily_commute_km > 0.0:
        if profile.commute_mode in [
            CommuteMode.INTERNAL_COMBUSTION_CAR,
            CommuteMode.TWO_WHEELER,
            CommuteMode.SHARED_CARPOOL,
        ]:
            target_factor = CLEAN_TRANSIT_BASELINE_FACTOR
        else:
            target_factor = baseline_commute_factor * TRANSIT_MODE_SWITCH_SAVINGS_RATIO

        emission_delta = max(0.0, baseline_commute_factor - target_factor)
        co2e_saved_kg = round(profile.daily_commute_km * emission_delta, 2)
    else:
        co2e_saved_kg = 0.0

    # 4. Respiratory Stress Reduction Index:
    if unprotected_intake_ug > 0.0:
        exposure_ratio = protected_intake_ug / unprotected_intake_ug
        stress_reduction_pct = round(max(0.0, min(100.0, (1.0 - exposure_ratio) * 100.0)), 1)
    else:
        stress_reduction_pct = 0.0

    # 5. Community 100-Household Annual Scaling:
    annual_community_co2_kg = round(co2e_saved_kg * COMMUNITY_HOUSEHOLD_SCALE * DAYS_PER_YEAR, 0)

    # 6. Concise Scientific Narrative Explanation:
    narrative = (
        f"By rescheduling outdoor activities away from nocturnal thermal inversion peaks and "
        f"deploying low-cost indoor filtration, your family prevents approximately {pm25_avoided_ug} µg "
        f"of toxic fine particulate matter from entering deep lung alveolar tissue daily—equivalent to "
        f"avoiding the passive inhalation of {cigs_avoided} cigarettes. Transitioning your {profile.daily_commute_km} km "
        f"commute saves {co2e_saved_kg} kg of CO2e today, scaling to {annual_community_co2_kg:,.0f} kg CO2e "
        f"if adopted by {COMMUNITY_HOUSEHOLD_SCALE} neighborhood families."
    )

    return QuantifiedImpactLedger(
        daily_pm25_avoided_micrograms=pm25_avoided_ug,
        cigarette_smoke_equivalents_avoided=cigs_avoided,
        daily_carbon_abatement_kg_co2e=co2e_saved_kg,
        respiratory_stress_index_reduction=stress_reduction_pct,
        annualized_community_co2_savings_kg=annual_community_co2_kg,
        impact_narrative=narrative,
    )
