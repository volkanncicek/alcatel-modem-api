"""
Alcatel Modem API - Generic Python library for Alcatel LTE modems
"""

from .api import (
  AlcatelAPIError,
  AlcatelConnectionError,
  AlcatelModemAPI,
  AlcatelTimeoutError,
)
from .auth import AuthenticationError, FileTokenStorage, MemoryTokenStorage, TokenStorageProtocol
from .constants import (
  CONNECTION_STATUSES,
  NETWORK_TYPES,
  PUBLIC_VERBS,
  RESTRICTED_VERBS,
  SMS_SEND_STATUS,
  get_connection_status,
  get_network_type,
  get_sms_send_status,
)
from .models import ConnectionState, ExtendedStatus, NetworkInfo, SMSMessage, SystemStatus
from .sms import SMSManager

__version__ = "1.0.0"
__all__ = [
  "AlcatelModemAPI",
  "SMSManager",
  "AuthenticationError",
  "AlcatelConnectionError",
  "AlcatelAPIError",
  "AlcatelTimeoutError",
  "NETWORK_TYPES",
  "CONNECTION_STATUSES",
  "SMS_SEND_STATUS",
  "PUBLIC_VERBS",
  "RESTRICTED_VERBS",
  "get_network_type",
  "get_connection_status",
  "get_sms_send_status",
  # Token storage
  "TokenStorageProtocol",
  "FileTokenStorage",
  "MemoryTokenStorage",
  # Typed models
  "SystemStatus",
  "ExtendedStatus",
  "NetworkInfo",
  "ConnectionState",
  "SMSMessage",
]
