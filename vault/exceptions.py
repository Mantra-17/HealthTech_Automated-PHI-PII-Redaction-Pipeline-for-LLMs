"""
vault/exceptions.py
-------------------
Custom exception hierarchy for the Vault pseudonymisation engine.

All Vault exceptions inherit from :class:`VaultError` so callers can catch
either the base class (broad) or a specific subclass (precise) depending on
how granular their error handling needs to be.
"""


class VaultError(Exception):
    """Base exception for Vault operations."""
    pass

class TokenNotFoundError(VaultError):
    """Raised when a requested token cannot be found in the Vault."""
    pass

class VaultConfigurationError(VaultError):
    """
    Raised when the Vault is misconfigured.

    Reserved for future configuration validation (e.g. missing encryption key,
    invalid TTL value, or unsupported Redis version).
    """
    pass
    
