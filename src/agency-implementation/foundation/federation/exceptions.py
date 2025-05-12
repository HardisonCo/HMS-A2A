"""
Exceptions for the Federation Framework.

This module defines a hierarchy of exceptions used throughout the federation system.
"""

class FederationError(Exception):
    """Base exception for all federation-related errors."""
    pass


class ConfigurationError(FederationError):
    """Error raised when there's an issue with configuration."""
    pass


class ConnectionError(FederationError):
    """Error raised when there's an issue connecting to a partner agency."""
    pass


class QueryError(FederationError):
    """Error raised when there's an issue executing a federated query."""
    pass


class SynchronizationError(FederationError):
    """Error raised when there's an issue with data synchronization."""
    pass


class SecurityError(FederationError):
    """Error raised when there's a security-related issue."""
    pass


class AuthorizationError(SecurityError):
    """Error raised when a request is not authorized."""
    pass


class AuthenticationError(SecurityError):
    """Error raised when authentication fails."""
    pass


class IdentityError(FederationError):
    """Error raised when there's an issue with identity federation."""
    pass


class SchemaError(FederationError):
    """Error raised when there's an issue with data schemas."""
    pass


class ValidationError(FederationError):
    """Error raised when data fails validation."""
    pass


class AuditError(FederationError):
    """Error raised when there's an issue with audit logging."""
    pass


class GovernanceError(FederationError):
    """Error raised when there's an issue with governance policies."""
    pass


class TimeoutError(FederationError):
    """Error raised when an operation times out."""
    pass


class NotFoundError(FederationError):
    """Error raised when a requested resource is not found."""
    pass


class DuplicateError(FederationError):
    """Error raised when there's a duplicate resource."""
    pass