"""
vault
-----
Session-scoped PHI/PII pseudonymisation engine backed by Redis.

Primary entry point: :class:`vault.vault.Vault`
"""

from vault.vault import Vault

__all__ = ["Vault"]
