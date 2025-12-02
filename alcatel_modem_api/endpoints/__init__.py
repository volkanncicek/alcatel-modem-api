"""
Endpoint namespaces for Alcatel Modem API
"""

from .device import DeviceEndpoint
from .network import NetworkEndpoint
from .sms import SMSEndpoint
from .system import SystemEndpoint
from .wlan import WLANEndpoint

__all__ = [
  "SMSEndpoint",
  "NetworkEndpoint",
  "WLANEndpoint",
  "DeviceEndpoint",
  "SystemEndpoint",
]

