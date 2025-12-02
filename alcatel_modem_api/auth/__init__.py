"""
Authentication strategies for different Alcatel modem models
"""

from .strategies import AuthStrategy, EncryptedAuthStrategy, LegacyAuthStrategy, TokenAuthStrategy, detect_auth_strategy

__all__ = [
  "AuthStrategy",
  "LegacyAuthStrategy",
  "TokenAuthStrategy",
  "EncryptedAuthStrategy",
  "detect_auth_strategy",
]
