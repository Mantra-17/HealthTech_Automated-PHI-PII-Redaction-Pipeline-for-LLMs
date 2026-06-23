class VaultError(Exception):
    """Base exception for Vault operations."""
    pass

class TokenNotFoundError(VaultError):
    """Raised when a requested token cannot be found in the Vault."""
    pass

class VaultConfigurationError(VaultError):
    """Raised when the Vault is misconfigured."""
    pass
