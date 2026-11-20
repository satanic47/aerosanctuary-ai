"""
Data schemas and Pydantic models for AeroSanctuary AI.

Defines domain models for user profiles, real-time air quality metrics,
low-emission daily routines, indoor air quality hacks, and direct impact quantification.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HouseholdType(str, Enum):
    """Classification of household composition for tailored health vulnerability."""

    INDIVIDUAL = "individual"
    FAMILY_WITH_KIDS = "family_with_kids"
    ELDERLY_RESIDENTS = "elderly_residents"
    ASTHMA_RESPIRATORY_VULNERABLE = "asthma_respiratory_vulnerable"
    PET_OWNERS = "pet_owners"


class CommuteMode(str, Enum):
    """Primary daily commute modality."""

    METRO_PUBLIC_TRANSIT = "metro_public_transit"
    WALKING_CYCLING = "walking_cycling"
    ELECTRIC_VEHICLE = "electric_vehicle"
    SHARED_CARPOOL = "shared_carpool"
    INTERNAL_COMBUSTION_CAR = "ice_car"
    TWO_WHEELER = "motorcycle_scooter"
    REMOTE_WFH = "remote_wfh"


class HeatingSource(str, Enum):
    """Winter domestic heating technology."""

    ELECTRIC_HEAT_PUMP = "electric_heat_pump"
    PIPED_NATURAL_GAS = "piped_natural_gas"
    FIREWOOD_BIOMASS = "firewood_biomass"
    COAL_BRIQUETTES = "coal_briquettes"
    NONE_PASSIVE = "none_passive"


class AQISeverity(str, Enum):
    """Standardized air quality severity classification (US EPA & CPCB aligned)."""

    GOOD = "Good (0-50)"
    MODERATE = "Moderate (51-100)"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups (101-150)"
    UNHEALTHY = "Unhealthy (151-200)"
    VERY_UNHEALTHY = "Very Unhealthy (201-300)"
    HAZARDOUS_SEVERE = "Hazardous / Severe (301-500+)"


class AirQualitySnapshot(BaseModel):
    """Real-time urban air quality snapshot."""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(..., min_length=1, max_length=100, description="Target urban center")
    aqi: int = Field(..., ge=0, le=1000, description="Air Quality Index value")
    severity: AQISeverity = Field(..., description="Severity category")
    pm25_ug_m3: float = Field(..., ge=0.0, description="PM2.5 concentration in ug/m3")
    pm10_ug_m3: float = Field(..., ge=0.0, description="PM10 concentration in ug/m3")
    no2_ppb: float = Field(default=24.5, ge=0.0, description="Nitrogen dioxide concentration")
    temperature_celsius: float = Field(default=16.0, description="Ambient surface temperature")
    thermal_inversion_active: bool = Field(
        default=True,
        description="Indicates whether meteorological winter thermal inversion is trapping ground-level smog",
    )
    safest_outdoor_window: str = Field(
        default="12:30 PM - 3:30 PM",
        description="Optimal daylight window when solar radiation disperses the inversion layer",
    )


class UserProfile(BaseModel):
    """User and community environmental lifestyle profile."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    location: str = Field(
        default="Delhi-NCR",
        min_length=2,
        max_length=100,
        description="City or district",
    )
    household_type: HouseholdType = Field(default=HouseholdType.FAMILY_WITH_KIDS)
    commute_mode: CommuteMode = Field(default=CommuteMode.INTERNAL_COMBUSTION_CAR)
    daily_commute_km: float = Field(
        default=18.0, ge=0.0, le=200.0, description="Roundtrip commute distance in km"
    )
    heating_source: HeatingSource = Field(default=HeatingSource.NONE_PASSIVE)
    ventilation_habits: str = Field(default="Morning open windows (8:00 AM)")
    air_purifier_owned: bool = Field(default=False)

    @field_validator("location")
    @classmethod
    def clean_location(cls, v: str) -> str:
        """Sanitize location string and reject empty or whitespace-only values."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Location cannot be empty or whitespace-only.")
        return stripped


class RoutineRecommendation(BaseModel):
    """Specific routine adjustment recommended for winter pollution navigation."""

    model_config = ConfigDict(extra="forbid")

    time_slot: str = Field(..., description="e.g. Early Morning (06:00 - 08:30 AM)")
    activity: str = Field(
        ...,
        description="Routine activity (e.g., Morning jog, School run, Office commute)",
    )
    hazard_rationale: str = Field(
        ..., description="Why current behavior causes high exposure or emission"
    )
    recommended_alternative: str = Field(
        ..., description="Sustainable / protective low-emission adaptation"
    )
    pm25_exposure_reduction_percent: float = Field(..., ge=0.0, le=100.0)
    emission_saved_kg_co2e: float = Field(..., ge=0.0)


class IndoorHack(BaseModel):
    """Low-cost, accessible Indoor Air Quality (IAQ) hack or DIY solution."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    category: str = Field(
        ...,
        description="diy_filtration | botanical | ventilation_timing | source_control",
    )
    problem_addressed: str
    materials_needed: list[str]
    estimated_cost_inr: int = Field(ge=0, description="Estimated cost in INR")
    step_by_step_instructions: list[str]
    expected_pm25_reduction: str
    scientific_basis: str


class QuantifiedImpactLedger(BaseModel):
    """Mathematical computation of avoided health hazards and carbon abatement."""

    model_config = ConfigDict(extra="forbid")

    daily_pm25_avoided_micrograms: float = Field(
        ...,
        description="Calculated quantity of fine particulate matter prevented from entering alveolar tract",
    )
    cigarette_smoke_equivalents_avoided: float = Field(
        ...,
        description="Equivalence in passively inhaled cigarette smoke avoided (Berkeley Earth standard)",
    )
    daily_carbon_abatement_kg_co2e: float = Field(
        ...,
        description="Daily greenhouse gas emission avoided through suggested low-emission routines",
    )
    respiratory_stress_index_reduction: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage reduction in cardiorespiratory inflammatory stress",
    )
    annualized_community_co2_savings_kg: float = Field(
        ...,
        description="Potential annual savings if adopted across 100 neighborhood households",
    )
    impact_narrative: str = Field(
        ..., description="Direct, transparent explanation of personal impact"
    )


class AssistantPlanResponse(BaseModel):
    """Comprehensive urban air quality action plan."""

    model_config = ConfigDict(extra="forbid")

    air_quality_snapshot: AirQualitySnapshot
    user_profile: UserProfile
    daily_routine_schedule: list[RoutineRecommendation]
    indoor_air_hacks: list[IndoorHack]
    impact_ledger: QuantifiedImpactLedger
    genai_executive_summary: str
    generated_at_timestamp: str


class ChatMessage(BaseModel):
    """Single chat interaction message."""

    model_config = ConfigDict(extra="forbid")

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    """Interactive GenAI chat consultation payload."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(..., min_length=1, max_length=1500)
    user_profile: UserProfile | None = None
    history: list[ChatMessage] = Field(default_factory=list)

    @field_validator("message")
    @classmethod
    def clean_message(cls, v: str) -> str:
        """Reject empty or whitespace-only messages."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Chat message cannot be empty or whitespace-only.")
        return stripped


class ChatResponse(BaseModel):
    """GenAI structured advisory response."""

    model_config = ConfigDict(extra="forbid")

    reply: str
    actionable_tips: list[str]
    direct_impact_statement: str
    source_method: str = Field(
        default="gemini-1.5-flash",
        description="Execution pathway (GenAI or Fallback Engine)",
    )
