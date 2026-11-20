"""
Domain-specific exceptions for AeroSanctuary AI.
Provides clean architectural separation and explicit error handling.
"""


class AeroSanctuaryException(Exception):
    """Base exception for all AeroSanctuary domain errors."""


class AQIServiceError(AeroSanctuaryException):
    """Raised when air quality telemetry retrieval fails."""


class PlanGenerationError(AeroSanctuaryException):
    """Raised when action plan synthesis encounters a processing fault."""


class ChatAdvisoryError(AeroSanctuaryException):
    """Raised when conversational advisory fails."""


class SecuritySanitizationError(AeroSanctuaryException):
    """Raised when prompt injection or input malformation is detected."""
