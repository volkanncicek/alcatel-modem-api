"""
Pydantic models for Alcatel Modem API responses
Provides better IDE autocompletion, type safety, and data validation
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SystemStatus(BaseModel):
  """System status information"""

  connection_status: int = Field(alias="ConnectionStatus", default=0)
  signal_strength: int = Field(alias="SignalStrength", default=0)
  network_name: str | None = Field(alias="NetworkName", default=None)
  network_type: int = Field(alias="NetworkType", default=0)
  imei: str | None = Field(alias="IMEI", default=None)
  iccid: str | None = Field(alias="ICCID", default=None)
  device: str | None = Field(alias="DeviceName", default=None)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "SystemStatus":
    """Create SystemStatus from API response dict"""
    return cls.model_validate(data)

  model_config = ConfigDict(populate_by_name=True)


class ExtendedStatus(BaseModel):
  """Extended status information (requires login)"""

  imei: str = Field(default="")
  iccid: str = Field(default="")
  device: str = Field(default="")
  connection_status: int = Field(default=0)
  bytes_in: int = Field(default=0)
  bytes_out: int = Field(default=0)
  bytes_in_rate: int = Field(default=0)
  bytes_out_rate: int = Field(default=0)
  ipv4_addr: str | None = Field(default=None)
  ipv6_addr: str | None = Field(default=None)
  network_name: str | None = Field(default=None)
  network_type: int = Field(default=0)
  strength: int = Field(default=0)
  rssi: int | None = Field(default=None)
  rsrp: int | None = Field(default=None)
  sinr: int | None = Field(default=None)
  rsrq: int | None = Field(default=None)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "ExtendedStatus":
    """Create ExtendedStatus from API response dict"""
    return cls.model_validate(data)


class SMSMessage(BaseModel):
  """SMS message information"""

  sms_id: int = Field(alias="SMSId", default=-1)
  phone_number: str = Field(alias="PhoneNumber", default="")
  content: str = Field(alias="SMSContent", default="")
  timestamp: str | None = Field(alias="SMSTime", default=None)
  status: int | None = Field(alias="Status", default=None)
  read: bool | None = Field(alias="Read", default=None)

  @model_validator(mode="before")
  @classmethod
  def handle_alternative_keys(cls, data: Any) -> Any:
    """Handle alternative field names in the data dict"""
    if isinstance(data, dict):
      # Handle alternative key names
      if "Id" in data and "SMSId" not in data:
        data["SMSId"] = data["Id"]
      if "Phone" in data and "PhoneNumber" not in data:
        data["PhoneNumber"] = data["Phone"]
      if "Content" in data and "SMSContent" not in data:
        data["SMSContent"] = data["Content"]
      if "Time" in data and "SMSTime" not in data:
        data["SMSTime"] = data["Time"]
      if "IsRead" in data and "Read" not in data:
        data["Read"] = data["IsRead"]
    return data

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "SMSMessage":
    """Create SMSMessage from API response dict"""
    return cls.model_validate(data)

  model_config = ConfigDict(populate_by_name=True)


class NetworkInfo(BaseModel):
  """Network information"""

  network_name: str | None = Field(alias="NetworkName", default=None)
  network_type: int = Field(alias="NetworkType", default=0)
  signal_strength: int = Field(alias="SignalStrength", default=0)
  rssi: int | None = Field(alias="RSSI", default=None)
  rsrp: int | None = Field(alias="RSRP", default=None)
  sinr: int | None = Field(alias="SINR", default=None)
  rsrq: int | None = Field(alias="RSRQ", default=None)

  @field_validator("rssi", "rsrp", "sinr", "rsrq", mode="before")
  @classmethod
  def validate_signal_metric(cls, v: Any) -> int | None:
    """Convert signal metrics to int or None"""
    if v is None:
      return None
    if isinstance(v, (int, float)):
      value = int(v)
      return value if value != -999 else None
    return None

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "NetworkInfo":
    """Create NetworkInfo from API response dict"""
    return cls.model_validate(data)

  @property
  def signal_quality_percent(self) -> int:
    """
    Estimate signal quality percentage based on RSRP/RSSI

    Returns:
        Signal quality percentage (0-100)
    """
    if self.rsrp is not None:
      # RSRP mapping: -140 (0%) to -44 (100%)
      val = max(-140, min(-44, self.rsrp))
      return int((val + 140) * (100 / 96))
    if self.rssi is not None:
      # Fallback to RSSI: -113 (0%) to -51 (100%)
      val = max(-113, min(-51, self.rssi))
      return int((val + 113) * (100 / 62))
    return 0

  model_config = ConfigDict(populate_by_name=True)


class ConnectionState(BaseModel):
  """Connection state information"""

  connection_status: int = Field(alias="ConnectionStatus", default=0)
  bytes_in: int = Field(alias="DlBytes", default=0)
  bytes_out: int = Field(alias="UlBytes", default=0)
  bytes_in_rate: int = Field(alias="DlRate", default=0)
  bytes_out_rate: int = Field(alias="UlRate", default=0)
  ipv4_addr: str | None = Field(alias="IPv4Adrress", default=None)
  ipv6_addr: str | None = Field(alias="IPv6Adrress", default=None)

  @model_validator(mode="before")
  @classmethod
  def handle_alternative_keys(cls, data: Any) -> Any:
    """Handle alternative field names in the data dict"""
    if isinstance(data, dict):
      # Handle alternative key names for IPv4
      if "IPv4Address" in data and "IPv4Adrress" not in data:
        data["IPv4Adrress"] = data["IPv4Address"]
      # Handle alternative key names for IPv6
      if "IPv6Address" in data and "IPv6Adrress" not in data:
        data["IPv6Adrress"] = data["IPv6Address"]
    return data

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "ConnectionState":
    """Create ConnectionState from API response dict"""
    return cls.model_validate(data)

  model_config = ConfigDict(populate_by_name=True)