"""
Custom exception classes for the AI Portal Automation Platform.

This module defines all custom exceptions used throughout the application,
providing consistent error handling and meaningful error messages.
"""


class AIPortalException(Exception):
    """Base exception for all AI Portal Automation Platform errors."""

    def __init__(self, message: str = None, error_code: str = None, details: dict = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
        """
        self.message = message or "An error occurred"
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(AIPortalException):
    """Raised when authentication fails."""

    pass


class AuthorizationException(AIPortalException):
    """Raised when user lacks required permissions."""

    pass


class ValidationException(AIPortalException):
    """Raised when input validation fails."""

    pass


class ResourceNotFoundException(AIPortalException):
    """Raised when a requested resource is not found."""

    pass


class DatabaseException(AIPortalException):
    """Raised when database operations fail."""

    pass


class WorkflowException(AIPortalException):
    """Raised when workflow execution fails."""

    pass


class PortalException(AIPortalException):
    """Raised when portal integration fails."""

    pass


class TenantException(AIPortalException):
    """Raised when multi-tenant operations fail."""

    pass


class ConfigurationException(AIPortalException):
    """Raised when configuration is invalid."""

    pass


class AuditException(AIPortalException):
    """Raised when audit logging fails."""

    pass


class CredentialException(AIPortalException):
    """Raised when credential handling fails."""

    pass


class RateLimitException(AIPortalException):
    """Raised when rate limit is exceeded."""

    pass


class DocumentException(AIPortalException):
    """Raised when document processing fails."""

    pass


class AIProviderException(AIPortalException):
    """Raised when AI provider operations fail."""

    pass


class APIException(AIPortalException):
    """Raised when API operations fail."""

    pass
