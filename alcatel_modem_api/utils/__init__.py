"""
Utility functions for Alcatel Modem API
"""

from .encryption import ENCRYPT_ADMIN_KEY, encrypt_admin, encrypt_token

__all__ = ["encrypt_admin", "encrypt_token", "ENCRYPT_ADMIN_KEY"]

