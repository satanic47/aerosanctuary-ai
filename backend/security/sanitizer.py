"""
Defensive security and prompt sanitization layer for AeroSanctuary AI.

Enforces:
1. Regex-based prompt injection detection (DAN, jailbreaks, system prompt dumps).
2. HTML entity sanitization to mitigate XSS vectors.
3. Per-IP sliding-window rate limiting to throttle denial-of-service attempts.
4. Request payload body size limits (10 KB max per OWASP API Security).
5. Hardened HTTP defense headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).
"""

import html
import re
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.constants import MAX_REQUEST_BODY_BYTES

# ============================================================================
# Adversarial Prompt Patterns (Jailbreak / Injection Detection)
# ============================================================================

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt\s*(reveal|leak|output|dump|print)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a\s+)?(dan|jailbreak|unfiltered)", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),
    re.compile(r"developer\s+mode\s+(enabled|active)", re.IGNORECASE),
    re.compile(r"<\s*script[^>]*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"exec\s*\(\s*['\"]", re.IGNORECASE),
    re.compile(r"__import__\s*\(", re.IGNORECASE),
    re.compile(r"eval\s*\(\s*['\"]", re.IGNORECASE),
    re.compile(r"prompt\s+injection", re.IGNORECASE),
]


def inspect_prompt_safety(text: str) -> tuple[bool, str]:
    """Inspects incoming user queries for known prompt injection and adversarial patterns.

    Args:
        text: Raw user input text.

    Returns:
        Tuple of (is_safe: bool, reason: str).
    """
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return (
                False,
                f"Adversarial signature detected matching security filter: [{pattern.pattern}].",
            )
    return True, "Input cleared safety checks."


def sanitize_text(text: str) -> str:
    """Sanitizes text by stripping control characters and escaping dangerous HTML entities.

    Args:
        text: Raw text string.

    Returns:
        Sanitized safe string.
    """
    # Remove null bytes and non-printable control characters
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Escape HTML special characters (&, <, >, ", ')
    return html.escape(cleaned, quote=True)


# ============================================================================
# Sliding-Window In-Memory Rate Limiter
# ============================================================================


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window rate limiter per client IP address."""

    def __init__(self, limit_per_minute: int = 60) -> None:
        """Initializes rate limiter with threshold capacity."""
        self.limit = limit_per_minute
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, ip: str) -> bool:
        """Checks whether an IP address is within its allowable rate threshold.

        Args:
            ip: Client IP address string.

        Returns:
            True if request is allowed, False if rate exceeded.
        """
        now = time.time()
        one_minute_ago = now - 60.0

        if ip not in self.requests:
            self.requests[ip] = []

        # Filter out timestamps older than 60 seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > one_minute_ago]

        if len(self.requests[ip]) >= self.limit:
            return False

        self.requests[ip].append(now)

        # Cleanup dormant IP addresses periodically
        if len(self.requests) > 1000:
            self._cleanup_dormant(one_minute_ago)

        return True

    def _cleanup_dormant(self, cutoff: float) -> None:
        """Removes stale IP addresses to prevent memory ballooning."""
        stale_keys = [
            ip
            for ip, timestamps in self.requests.items()
            if not timestamps or timestamps[-1] < cutoff
        ]
        for ip in stale_keys:
            self.requests.pop(ip, None)


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter(limit_per_minute=settings.MAX_REQUESTS_PER_MINUTE)


async def rate_limiting_middleware(request: Request, call_next):
    """FastAPI middleware enforcing payload body limits, per-IP rate limiting, and hardened CSP headers."""
    # 1. Enforce 10 KB Payload Size Limit (OWASP API Security Top 10)
    if request.method in ("POST", "PUT", "PATCH"):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={
                    "detail": f"Payload too large. Maximum allowable body size is {MAX_REQUEST_BODY_BYTES // 1024} KB."
                },
            )

    # 2. Per-IP Sliding-Window Rate Limiting
    client_ip = request.client.host if request.client else "127.0.0.1"
    path = request.url.path
    is_exempt = path.startswith(("/css", "/js")) or path in {
        "/health",
        "/",
        "/api/health",
    }
    if not is_exempt and not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please wait a minute before making further requests."
            },
        )

    response = await call_next(request)

    # 3. Hardened Defense-in-Depth Security Headers (OWASP & Mozilla Observatory standard)
    # Note: script-src 'self' strictly prohibits inline scripts to prevent XSS execution.
    # style-src retains 'unsafe-inline' alongside Google Fonts to support dynamic CSS custom property transitions.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none';"
    )
    return response
