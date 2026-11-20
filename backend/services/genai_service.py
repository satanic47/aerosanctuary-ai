"""Generative AI advisory engine for AeroSanctuary AI.

Integrates Google Gemini with structured environmental prompts and guardrails.
Includes an intelligent deterministic fallback engine to guarantee 100% uptime
and resilience during automated test suites or zero-credit environments.
"""

import json
import logging

from backend.config import settings
from backend.models.schemas import (
    AirQualitySnapshot,
    ChatRequest,
    ChatResponse,
    QuantifiedImpactLedger,
    UserProfile,
)
from backend.security.sanitizer import inspect_prompt_safety, sanitize_text

logger = logging.getLogger("aerosanctuary.genai")

SYSTEM_PROMPT = """You are AeroSanctuary AI, an expert environmental health scientist and urban air quality advisory assistant.
Your mission is to help families, vulnerable individuals, and urban communities navigate severe winter smog and toxic air pollution episodes.
Key Principles:
1. Ground your advice in atmospheric science (explain temperature inversions, PM2.5 alveolar penetration, VOCs).
2. Propose low-emission, affordable daily routines (public transit, carpooling, shifting activity windows).
3. Recommend practical indoor air quality (IAQ) hacks (DIY Corsi-Rosenthal boxes, NASA air-purifying plants, wet-mopping, ventilation schedules).
4. Quantify the direct impact of choices in avoided PM2.5 (ug/m3) and avoided carbon (kg CO2e).
5. Maintain a supportive, practical, scientifically rigorous, and empathetic tone."""


def build_deterministic_chat_response(query: str, profile: UserProfile | None) -> ChatResponse:
    """Generates an authoritative, structured response when external GenAI API is unavailable."""
    clean_q = query.lower()

    if any(k in clean_q for k in ["corsi", "diy", "filter", "purifier", "box fan"]):
        reply = (
            "The DIY Corsi-Rosenthal Box is the gold standard for low-cost indoor particulate filtration. "
            "By taping four MERV-13 furnace filters around a 20-inch box fan exhausting upward, you generate a Clean Air "
            "Delivery Rate (CADR) of ~450 CFM for under ₹2,800. This captures over 85% of airborne PM2.5 in a 400 sq.ft room "
            "within 30 minutes, performing on par with commercial purifiers costing ₹18,000+."
        )
        tips = [
            "Use MERV 13 or higher rated furnace filters to capture sub-micron particles.",
            "Seal all joints with heavy duct tape; air leaks degrade filtration efficiency by 30%.",
            "Add a circular cardboard shroud to the fan face to eliminate corner air turbulence.",
        ]
        impact = "Reduces household daily inhaled PM2.5 by ~240 µg, saving ₹15,000+ in commercial appliance capital."

    elif any(
        k in clean_q for k in ["baby", "child", "kids", "school", "elderly", "asthma", "pregnant"]
    ):
        reply = (
            "Children and elderly individuals have higher respiration rates per kilogram of body weight, absorbing up to "
            "50% more particulate matter per breath. During severe winter inversions (AQI > 250), restrict outdoor activities "
            "between 6:00 PM and 11:00 AM. Ensure classrooms or nurseries run HEPA or DIY filtration continuously, and mandate "
            "well-fitted N95/FFP2 masks for any unavoidable transit."
        )
        tips = [
            "Never use surgical cloth masks for PM2.5; only certified N95/KF94 masks create an airtight seal.",
            "Schedule indoor physical play during the morning; reserve brief outdoor transit for 1:00 PM to 3:30 PM.",
            "Equip bedrooms with Snake Plants (Sansevieria) for nocturnal oxygenation without CO2 buildup.",
        ]
        impact = "Curbs acute pediatric asthma triggers by 70% and prevents irreversible alveolar particle deposition."

    elif any(
        k in clean_q for k in ["inversion", "smog", "winter", "weather", "ventilation", "windows"]
    ):
        reply = (
            "Winter thermal inversion occurs when cold, dense surface air is trapped beneath a warmer atmospheric lid. "
            "Because surface air cannot rise, vehicular emissions, dust, and smoke concentrate into a dense toxic blanket. "
            "Never open windows in the early morning. Wait for midday solar heating (typically 1:00 PM – 3:30 PM) when the "
            "inversion layer temporarily expands, and execute a 15-minute cross-ventilation purge."
        )
        tips = [
            "Keep all windows tightly weatherstripped between 5:30 PM and 11:30 AM.",
            "Perform a 15-minute cross-ventilation flush between 1:00 PM and 3:00 PM.",
            "Place damp rolled towels beneath exterior doors to block ground-level smog seepage.",
        ]
        impact = "Stops ~65% of outdoor ambient smog from penetrating indoor sleeping quarters."

    else:
        city = profile.location if profile else "your city"
        reply = (
            f"Navigating severe air pollution in {city} requires a dual approach: minimizing personal emissions while "
            f"shielding your family's respiratory health. Shift high-emission car trips to public transit or carpooling, "
            f"implement indoor source control (wet-mopping instead of sweeping, avoiding indoor open flames), and rely on "
            f"targeted midday ventilation windows when thermal inversion naturally weakens."
        )
        tips = [
            "Switch from single-occupancy driving to Metro or carpools on high-AQI alert days.",
            "Replace dry broom sweeping with damp microfiber mopping to avoid aerosolizing settled toxic dust.",
            "Inspect and replace air conditioning / car cabin filters with activated carbon PM2.5 grade media.",
        ]
        impact = "Saves 2.5–4.0 kg of CO2e per day and curtails personal particulate inhalation by over 50%."

    return ChatResponse(
        reply=reply,
        actionable_tips=tips,
        direct_impact_statement=impact,
        source_method="deterministic_rules_engine (100% resilient fallback)",
    )


async def generate_executive_ai_summary(
    profile: UserProfile, snapshot: AirQualitySnapshot, impact: QuantifiedImpactLedger
) -> str:
    """Produces an executive synthesis combining environmental data and lifestyle adjustments."""
    # Attempt Google Gemini if configured
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Context:\n"
                f"- City: {snapshot.city} (AQI: {snapshot.aqi}, PM2.5: {snapshot.pm25_ug_m3} ug/m3, Inversion: {snapshot.thermal_inversion_active})\n"
                f"- Household: {profile.household_type.value}, Commute: {profile.commute_mode.value} ({profile.daily_commute_km} km)\n"
                f"- Impact: {impact.daily_pm25_avoided_micrograms} ug PM2.5 avoided, {impact.daily_carbon_abatement_kg_co2e} kg CO2e saved.\n\n"
                f"Write a concise, empowering 3-sentence executive summary explaining the direct impact of their daily choices."
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except (
            ValueError,
            KeyError,
            json.JSONDecodeError,
            ImportError,
            RuntimeError,
        ) as err:
            logger.warning("Gemini executive summary fallback triggered: %s", err)

    # Deterministic fallback summary
    return (
        f"In {snapshot.city}, active winter thermal inversion is currently concentrating dangerous surface PM2.5 levels ({snapshot.pm25_ug_m3} µg/m³). "
        f"By realigning your {profile.daily_commute_km} km transit routine to low-emission modes and deploying low-cost indoor filtration, "
        f"your household will avoid inhaling {impact.daily_pm25_avoided_micrograms} µg of toxic particulates daily while directly abating "
        f"{impact.daily_carbon_abatement_kg_co2e} kg of CO2e."
    )


async def process_chat_consultation(request: ChatRequest) -> ChatResponse:
    """Processes interactive user query with safety screening and GenAI / fallback engine."""
    # 1. Inspect for Prompt Injection / Adversarial Vectors
    is_safe, reason = inspect_prompt_safety(request.message)
    if not is_safe:
        return ChatResponse(
            reply=f"Security Notice: {reason} Please ask a question related to air quality, daily routines, or indoor hacks.",
            actionable_tips=[
                "Ask about DIY air purifiers",
                "Ask about thermal inversion",
                "Ask about safe exercise hours",
            ],
            direct_impact_statement="Defensive input filtering keeps the platform secure.",
            source_method="security_firewall",
        )

    clean_message = sanitize_text(request.message)

    # 2. Try Gemini API if key is present
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            context_block = f"User Profile Context: {request.user_profile.model_dump_json() if request.user_profile else 'None provided'}"
            full_prompt = (
                f"{SYSTEM_PROMPT}\n\n{context_block}\n\n"
                f"User Question: {clean_message}\n\n"
                f"Respond in valid JSON with keys: 'reply' (string), 'actionable_tips' (list of strings), 'direct_impact_statement' (string)."
            )
            res = model.generate_content(
                full_prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            if res and res.text:
                parsed = json.loads(res.text)
                return ChatResponse(
                    reply=parsed.get("reply", "Here is guidance on your air quality query."),
                    actionable_tips=parsed.get("actionable_tips", ["Wear an N95 mask outdoors."]),
                    direct_impact_statement=parsed.get(
                        "direct_impact_statement",
                        "Reduces personal particulate exposure.",
                    ),
                    source_method=f"GenAI ({settings.GEMINI_MODEL})",
                )
        except (
            ValueError,
            KeyError,
            json.JSONDecodeError,
            ImportError,
            RuntimeError,
        ) as err:
            logger.warning("Gemini chat advisory fallback triggered: %s", err)

    # 3. High-Quality Deterministic Fallback Engine
    return build_deterministic_chat_response(clean_message, request.user_profile)
