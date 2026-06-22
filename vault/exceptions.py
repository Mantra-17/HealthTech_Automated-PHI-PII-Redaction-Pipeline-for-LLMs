"""
Custom exceptions for the Vault Engine.
"""

class VaultError(Exception):
    """Base exception for all Vault-related errors."""
    pass

class TokenNotFoundError(VaultError):
    """Raised when a requested token cannot be found in the token store."""
    pass
