"""
Typed data models for Alcatel Modem API responses
Provides better IDE autocompletion and type safety
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SystemStatus:
  """System status information"""

  connection_status: int
  signal_strength: int
  network_name: str | None
  network_type: int
  imei: str | None = None
  iccid: str | None = None
  device: str | None = None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "SystemStatus":
    """Create SystemStatus from API response dict"""
    return cls(
      connection_status=data.get("ConnectionStatus", 0),
      signal_strength=data.get("SignalStrength", 0),
      network_name=data.get("NetworkName"),
      network_type=data.get("NetworkType", 0),
      imei=data.get("IMEI"),
      iccid=data.get("ICCID"),
      device=data.get("DeviceName"),
    )


@dataclass
class ExtendedStatus:
  """Extended status information (requires login)"""

  imei: str
  iccid: str
  device: str
  connection_status: int
  bytes_in: int
  bytes_out: int
  bytes_in_rate: int
  bytes_out_rate: int
  ipv4_addr: str | None
  ipv6_addr: str | None
  network_name: str | None
  network_type: int
  strength: int
  rssi: int | None
  rsrp: int | None
  sinr: int | None
  rsrq: int | None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "ExtendedStatus":
    """Create ExtendedStatus from API response dict"""
    return cls(
      imei=data.get("imei", ""),
      iccid=data.get("iccid", ""),
      device=data.get("device", ""),
      connection_status=data.get("connection_status", 0),
      bytes_in=data.get("bytes_in", 0),
      bytes_out=data.get("bytes_out", 0),
      bytes_in_rate=data.get("bytes_in_rate", 0),
      bytes_out_rate=data.get("bytes_out_rate", 0),
      ipv4_addr=data.get("ipv4_addr"),
      ipv6_addr=data.get("ipv6_addr"),
      network_name=data.get("network_name"),
      network_type=data.get("network_type", 0),
      strength=data.get("strength", 0),
      rssi=data.get("rssi"),
      rsrp=data.get("rsrp"),
      sinr=data.get("sinr"),
      rsrq=data.get("rsrq"),
    )


@dataclass
class SMSMessage:
  """SMS message information"""

  sms_id: int
  phone_number: str
  content: str
  timestamp: str | None = None
  status: int | None = None
  read: bool | None = None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "SMSMessage":
    """Create SMSMessage from API response dict"""
    return cls(
      sms_id=data.get("SMSId", data.get("Id", -1)),
      phone_number=data.get("PhoneNumber", data.get("Phone", "")),
      content=data.get("SMSContent", data.get("Content", "")),
      timestamp=data.get("SMSTime", data.get("Time")),
      status=data.get("Status"),
      read=data.get("Read", data.get("IsRead", False)),
    )


@dataclass
class NetworkInfo:
  """Network information"""

  network_name: str | None
  network_type: int
  signal_strength: int
  rssi: int | None = None
  rsrp: int | None = None
  sinr: int | None = None
  rsrq: int | None = None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "NetworkInfo":
    """Create NetworkInfo from API response dict"""
    return cls(
      network_name=data.get("NetworkName"),
      network_type=data.get("NetworkType", 0),
      signal_strength=data.get("SignalStrength", 0),
      rssi=int(data.get("RSSI", -999)) if data.get("RSSI") is not None else None,
      rsrp=int(data.get("RSRP", -999)) if data.get("RSRP") is not None else None,
      sinr=int(data.get("SINR", -999)) if data.get("SINR") is not None else None,
      rsrq=int(data.get("RSRQ", -999)) if data.get("RSRQ") is not None else None,
    )


@dataclass
class ConnectionState:
  """Connection state information"""

  connection_status: int
  bytes_in: int
  bytes_out: int
  bytes_in_rate: int
  bytes_out_rate: int
  ipv4_addr: str | None = None
  ipv6_addr: str | None = None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "ConnectionState":
    """Create ConnectionState from API response dict"""
    return cls(
      connection_status=data.get("ConnectionStatus", 0),
      bytes_in=data.get("DlBytes", 0),
      bytes_out=data.get("UlBytes", 0),
      bytes_in_rate=data.get("DlRate", 0),
      bytes_out_rate=data.get("UlRate", 0),
      ipv4_addr=data.get("IPv4Adrress", data.get("IPv4Address")),
      ipv6_addr=data.get("IPv6Adrress", data.get("IPv6Address")),
    )
