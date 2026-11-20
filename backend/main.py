"""Main FastAPI application entry point for AeroSanctuary AI.

Exposes RESTful endpoints for real-time air quality metrics, personalized
low-emission routine planning, indoor air quality hacks, and interactive GenAI consultations.
Includes static asset serving for the web interface and automated security middlewares.
"""

import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.exceptions import (
    AQIServiceError,
    ChatAdvisoryError,
    PlanGenerationError,
)
from backend.models.schemas import (
    AirQualitySnapshot,
    AssistantPlanResponse,
    ChatRequest,
    ChatResponse,
    IndoorHack,
    QuantifiedImpactLedger,
    UserProfile,
)
from backend.security.sanitizer import rate_limiting_middleware
from backend.services.aqi_service import get_air_quality_snapshot
from backend.services.genai_service import (
    generate_executive_ai_summary,
    process_chat_consultation,
)
from backend.services.impact_calculator import calculate_quantified_impact
from backend.services.rules_engine import (
    CURATED_INDOOR_HACKS,
    generate_tailored_routines,
)

logger = logging.getLogger("aerosanctuary.api")

# Initialize FastAPI Application with rich OpenAPI documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GenAI-powered Urban Air Quality, Winter Smog Mitigation, and Community Health Assistant.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Attach Rate Limiting and OWASP Security Headers Middleware
app.middleware("http")(rate_limiting_middleware)

# 2. Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/api/health", tags=["System"])
async def health_check() -> dict[str, str | bool]:
    """Returns application health status, version, and active service flags."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "genai_enabled": bool(settings.GEMINI_API_KEY),
    }


@app.get("/api/aqi", response_model=AirQualitySnapshot, tags=["Air Quality"])
async def get_aqi_metrics(
    location: str = Query(default="Delhi-NCR", description="City or district name"),
) -> AirQualitySnapshot:
    """Fetches real-time air quality metrics, particulate concentration, and thermal inversion status."""
    try:
        snapshot = get_air_quality_snapshot(location)
        return snapshot
    except (AQIServiceError, ValueError, KeyError) as e:
        logger.error("Failed to retrieve air quality snapshot for %s: %s", location, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve air quality snapshot: {e!s}",
        ) from e


@app.get("/api/indoor-hacks", response_model=list[IndoorHack], tags=["Indoor Air Quality"])
async def list_indoor_hacks(
    category: str | None = Query(default=None, description="Filter by category"),
) -> list[IndoorHack]:
    """Retrieves curated, peer-reviewed low-cost indoor air quality hacks and DIY purifier guides."""
    if category:
        filtered = [h for h in CURATED_INDOOR_HACKS if h.category.lower() == category.lower()]
        return filtered
    return CURATED_INDOOR_HACKS


@app.post(
    "/api/generate-plan",
    response_model=AssistantPlanResponse,
    tags=["Personalized Plan"],
)
async def generate_action_plan(profile: UserProfile) -> AssistantPlanResponse:
    """Generates an end-to-end winter smog action plan tailored to family profile and transit modality.

    Includes:
    - Real-time air quality snapshot with thermal inversion detection.
    - Chronological low-emission daily routines avoiding peak exposure hours.
    - Targeted indoor air quality hacks and DIY air purification.
    - Mathematically calculated impact ledger (PM2.5 avoided, kg CO2e abated, cigarette equivalence).
    - GenAI executive advisory synthesis.
    """
    try:
        # 1. Fetch Location AQI Snapshot
        snapshot = get_air_quality_snapshot(profile.location)

        # 2. Formulate Tailored Routines
        routines = generate_tailored_routines(profile, snapshot)

        # 3. Compute Quantified Impact Ledger
        impact = calculate_quantified_impact(
            profile=profile,
            ambient_pm25=snapshot.pm25_ug_m3,
            adopted_routine_pm25_reduction_pct=70.0,
            adopted_clean_commute=True,
        )

        # 4. Synthesize GenAI Executive Summary
        ai_summary = await generate_executive_ai_summary(profile, snapshot, impact)

        return AssistantPlanResponse(
            air_quality_snapshot=snapshot,
            user_profile=profile,
            daily_routine_schedule=routines,
            indoor_air_hacks=CURATED_INDOOR_HACKS,
            impact_ledger=impact,
            genai_executive_summary=ai_summary,
            generated_at_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        )
    except (PlanGenerationError, ValueError, KeyError) as e:
        logger.error("Plan generation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating action plan: {e!s}",
        ) from e


@app.post("/api/chat", response_model=ChatResponse, tags=["GenAI Consultation"])
async def interactive_chat(request: ChatRequest) -> ChatResponse:
    """Consult the GenAI Assistant on customized smog mitigation, health questions, or DIY hacks."""
    try:
        response = await process_chat_consultation(request)
        return response
    except (ChatAdvisoryError, ValueError, KeyError) as e:
        logger.error("Chat advisory error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat consultation error: {e!s}",
        ) from e


@app.get(
    "/api/impact-summary",
    response_model=QuantifiedImpactLedger,
    tags=["Impact Calculator"],
)
async def quick_impact_calculation(
    daily_km: float = Query(default=18.0, ge=0.0, le=200.0),
    commute_mode: str = Query(default="ice_car"),
    location: str = Query(default="Delhi-NCR"),
) -> QuantifiedImpactLedger:
    """Quick standalone calculation of daily avoided PM2.5 and CO2e abatement."""
    profile = UserProfile(location=location, daily_commute_km=daily_km)
    snapshot = get_air_quality_snapshot(location)
    return calculate_quantified_impact(profile, snapshot.pm25_ug_m3)


# ============================================================================
# Frontend Static Asset Serving
# ============================================================================

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        """Serves the main accessible web application dashboard."""
        return FileResponse(os.path.join(frontend_path, "index.html"))
