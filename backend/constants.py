"""
AeroSanctuary AI - Scientific & Meteorological Constants.
Central repository for all empirical constants, emission factors, and threshold definitions.
All values are annotated with authoritative scientific, atmospheric, or regulatory sources.
"""

# ============================================================================
# 1. Atmospheric & Particulate Thresholds (Source: WHO & CPCB India)
# ============================================================================

# World Health Organization 24-hour PM2.5 Guideline limit (ug/m3)
# Source: WHO Global Air Quality Guidelines (2021)
WHO_PM25_24HR_SAFE_LIMIT_UG_M3: float = 15.0

# Central Pollution Control Board (India) 24-hour National Ambient Air Quality Standard (ug/m3)
# Source: CPCB NAAQS Gazette Notification (2009)
CPCB_PM25_24HR_STANDARD_UG_M3: float = 60.0

# Typical adult daily respiratory minute volume (alveolar ventilation) in m3/day
# Source: US EPA Exposure Factors Handbook (Chapter 6 - Inhalation Rates, 2011)
# 12.0 m3/day corresponds to ~0.5 m3/hr at rest and ~1.2 m3/hr light activity
ADULT_DAILY_ALVEOLAR_VENTILATION_M3: float = 12.0

# ============================================================================
# 2. Human Respiratory Ventilation & Exposure Assumptions
# ============================================================================

# Human respiratory ventilation rate profiles (m3 / hour)
# Source: US EPA Exposure Factors Handbook (Chapter 6 - Inhalation Rates, 2011)
VENTILATION_RATE_RESTING_INDOORS_M3_PER_HR: float = 0.48  # ~8 liters/min at sleep/rest
VENTILATION_RATE_LIGHT_ACTIVITY_M3_PER_HR: float = 0.90  # ~15 liters/min light domestic activity
VENTILATION_RATE_OUTDOOR_COMMUTE_M3_PER_HR: float = 1.20  # ~20 liters/min transit/active movement

# Baseline indoor particle infiltration ratio without active mechanical filtration (I/O ratio)
# Source: ASHRAE Guideline 24 / CPCB indoor-to-outdoor particulate studies in urban masonry buildings (~0.65)
BASELINE_INDOOR_INFILTRATION_RATIO: float = 0.65

# Baseline unprotected exposure durations (hours/day)
# Typical urban resident: 3.0 hours outdoor transit/exposure + 21.0 hours indoor dwelling
BASELINE_OUTDOOR_EXPOSURE_HOURS: float = 3.0
BASELINE_INDOOR_EXPOSURE_HOURS: float = 21.0

# Protected exposure durations under optimized diurnal schedule (hours/day)
# Scheduled transit shifts reduce outdoor exposure to 1.5 hours + 22.5 hours protected indoor shelter
PROTECTED_OUTDOOR_EXPOSURE_HOURS: float = 1.5
PROTECTED_INDOOR_EXPOSURE_HOURS: float = 22.5

# Outdoor particulate mitigation limits
# Maximum outdoor mitigation efficiency ceiling via certified N95 masking and inversion avoidance
# Source: NIOSH 42 CFR Part 84 filtration standards + diurnal solar dispersion window shift
MAX_OUTDOOR_MITIGATION_FRACTION: float = 0.85
OUTDOOR_SCHEDULE_MITIGATION_SCALE: float = 0.90

# Default baseline vehicle emission factor for fallback (ICE passenger car kg CO2e/km)
DEFAULT_BASELINE_CAR_EMISSION_FACTOR: float = 0.192

# Clean transit commute reduction factor for non-ICE modes
TRANSIT_MODE_SWITCH_SAVINGS_RATIO: float = 0.50

# ============================================================================
# 3. Berkeley Earth Cigarette Equivalence Model
# ============================================================================

# Micrograms of PM2.5 inhaled equivalent to smoking one cigarette
# Source: Berkeley Earth (Muller & Rohde, 2015: "Air Pollution and Cigarette Equivalence")
# Empirical derivation: 1 cigarette per day is roughly equivalent to ambient PM2.5 of 22 ug/m3
# (22 ug/m3 * 18 m3/day breathing volume = ~396 ug inhaled PM2.5 per cigarette)
BERKELEY_EARTH_UG_PER_CIGARETTE: float = 396.0

# ============================================================================
# 3. Vehicle Greenhouse Gas Emission Factors (kg CO2e per passenger-km)
# ============================================================================

# Source: UK Department for Energy Security and Net Zero (DESNZ) / DEFRA 2023 Conversion Factors
# and CPCB vehicular emission inventory models for urban transit modalities.
EMISSION_FACTORS_KG_CO2E_PER_KM: dict[str, float] = {
    "ice_car": 0.192,  # Single-occupancy petrol / diesel internal combustion engine
    "motorcycle_scooter": 0.085,  # 2-wheeler petrol motor scooter
    "metro_public_transit": 0.028,  # Urban electric metro / electrified bus per passenger-km
    "electric_vehicle": 0.045,  # Grid-charged battery electric vehicle (Indian grid average)
    "shared_carpool": 0.064,  # 3-person shared occupancy commuter car
    "walking_cycling": 0.0,  # Active non-motorized transport
    "remote_wfh": 0.0,  # Zero commute transit emission
}

# Baseline clean commute factor against which savings are measured (metro rail standard)
CLEAN_TRANSIT_BASELINE_FACTOR: float = 0.028

# ============================================================================
# 4. Hourly Routine Reduction Factors & Time Windows
# ============================================================================

# Routine exposure reduction percentages by shifting windows away from temperature inversions
# Source: Atmospheric Environment Journal (Thermal Inversion & Boundary Layer Stagnation)
MORNING_INVERSION_EXPOSURE_REDUCTION_PCT: float = 78.5
MIDDAY_VENTILATION_EXPOSURE_REDUCTION_PCT: float = 65.0
EVENING_RUSH_EXPOSURE_REDUCTION_PCT: float = 74.0
DEFAULT_ADOPTED_ROUTINE_REDUCTION_PCT: float = 70.0

# Diurnal Time Slots
TIME_SLOT_MORNING: str = "06:00 AM - 08:30 AM"
TIME_SLOT_MIDDAY: str = "12:30 PM - 03:00 PM"
TIME_SLOT_EVENING: str = "05:30 PM - 08:00 PM"
TIME_SLOT_NIGHT: str = "09:30 PM - 06:00 AM"

# Midday Solar Inversion Breakup ventilation window
SAFEST_VENTILATION_WINDOW_DEFAULT: str = "12:30 PM - 03:30 PM"

# ============================================================================
# 5. Security & Rate Limiting Constants
# ============================================================================

# Maximum allowable HTTP request body size in bytes (10 KB)
# Enforces OWASP API Security Top 10 (Improper Assets & Resource Consumption protection)
MAX_REQUEST_BODY_BYTES: int = 10 * 1024

# Sliding window rate limit per client IP
MAX_REQUESTS_PER_MINUTE_LIMIT: int = 60

# Maximum valid commute distance constraint in kilometers
MIN_COMMUTE_DISTANCE_KM: float = 0.0
MAX_COMMUTE_DISTANCE_KM: float = 200.0

# Community scaling factor: number of households in neighborhood multiplier
COMMUNITY_HOUSEHOLD_SCALE: int = 100
DAYS_PER_YEAR: int = 365
