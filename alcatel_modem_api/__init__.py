"""
Alcatel Modem API - Generic Python library for Alcatel LTE modems
Modern namespace-based API with async support
"""

from .client import AlcatelClient, FileTokenStorage, MemoryTokenStorage, TokenStorageProtocol
from .endpoints import DeviceEndpoint, NetworkEndpoint, SMSEndpoint, SystemEndpoint, WLANEndpoint
from .exceptions import (
  AlcatelAPIError,
  AlcatelConnectionError,
  AlcatelError,
  AlcatelFeatureNotSupportedError,
  AlcatelSimMissingError,
  AlcatelSystemBusyError,
  AlcatelTimeoutError,
  AuthenticationError,
  UnsupportedModemError,
)
from .models import ConnectionState, ExtendedStatus, NetworkInfo, SMSMessage, SystemStatus

__version__ = "0.1.0"

__all__ = [
  # Main client class
  "AlcatelClient",
  # Endpoints
  "SMSEndpoint",
  "NetworkEndpoint",
  "WLANEndpoint",
  "DeviceEndpoint",
  "SystemEndpoint",
  # Exceptions
  "AlcatelError",
  "AlcatelConnectionError",
  "AlcatelAPIError",
  "AlcatelTimeoutError",
  "AlcatelSystemBusyError",
  "AlcatelSimMissingError",
  "AlcatelFeatureNotSupportedError",
  "AuthenticationError",
  "UnsupportedModemError",
  # Models
  "SystemStatus",
  "ExtendedStatus",
  "NetworkInfo",
  "ConnectionState",
  "SMSMessage",
  # Token storage
  "TokenStorageProtocol",
  "FileTokenStorage",
  "MemoryTokenStorage",
]
