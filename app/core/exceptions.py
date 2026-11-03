"""
Core Application Exceptions
Clean error hierarchy for consistent error handling and HTTP status mappings.
"""

from typing import Optional, Dict, Any


class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EntityNotFoundError(AppError):
    """Raised when a requested resource does not exist."""
    pass


class ValidationError(AppError):
    """Raised when domain or schema validation fails."""
    pass


class WebhookVerificationError(AppError):
    """Raised when webhook signature verification fails."""
    pass


class ExternalServiceError(AppError):
    """Raised when an external API (WhatsApp, Claude, Calendar) fails."""
    pass


class DuplicateEventError(AppError):
    """Raised when an idempotent event has already been processed."""
    pass


# Convenience aliases for service layers
EntityNotFoundException = EntityNotFoundError
ValidationException = ValidationError
ExternalServiceException = ExternalServiceError
AIIntegrationException = ExternalServiceError
WebhookVerificationException = WebhookVerificationError
