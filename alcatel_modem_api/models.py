"""
Pydantic models for Alcatel Modem API responses
Provides better IDE autocompletion, type safety, and data validation
"""

from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def coerce_int_or_none(v: Any) -> Union[int, None]:
  """
  Coerce value to int or None
  Handles empty strings, "N/A", None, and invalid values
  """
  if v is None:
    return None
  if isinstance(v, str):
    v = v.strip()
    if v == "" or v.upper() in ("N/A", "NA", "NULL", "NONE"):
      return None
    try:
      return int(v)
    except (ValueError, TypeError):
      return None
  if isinstance(v, (int, float)):
    # Check if original value is a sentinel before conversion
    # Sentinel values: -999, -1 (0 is allowed as valid)
    if v == -999 or v == -1:
      return None
    value = int(v)
    return value
  return None


def coerce_str_or_none(v: Any) -> Union[str, None]:
  """
  Coerce value to str or None
  Handles empty strings, "N/A", None
  """
  if v is None:
    return None
  if isinstance(v, str):
    stripped: str = v.strip()
    if stripped == "" or stripped.upper() in ("N/A", "NA", "NULL", "NONE"):
      return None
    return stripped
  if v:
    return str(v)
  return None


class SystemStatus(BaseModel):
  """System status information"""

  connection_status: int = Field(alias="ConnectionStatus", default=0)
  signal_strength: int = Field(alias="SignalStrength", default=0)
  network_name: Union[str, None] = Field(alias="NetworkName", default=None, validate_default=True)
  network_type: int = Field(alias="NetworkType", default=0)
  imei: Union[str, None] = Field(alias="IMEI", default=None, validate_default=True)
  iccid: Union[str, None] = Field(alias="ICCID", default=None, validate_default=True)
  device: Union[str, None] = Field(alias="DeviceName", default=None, validate_default=True)

  @field_validator("network_name", "imei", "iccid", "device", mode="before")
  @classmethod
  def validate_string_fields(cls, v: Any) -> Union[str, None]:
    """Normalize string fields, converting empty strings and N/A to None"""
    return coerce_str_or_none(v)

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
  ipv4_addr: Union[str, None] = Field(default=None, validate_default=True)
  ipv6_addr: Union[str, None] = Field(default=None, validate_default=True)
  network_name: Union[str, None] = Field(default=None, validate_default=True)
  network_type: int = Field(default=0)
  strength: int = Field(default=0)
  rssi: Union[int, None] = Field(default=None, validate_default=True)
  rsrp: Union[int, None] = Field(default=None, validate_default=True)
  sinr: Union[int, None] = Field(default=None, validate_default=True)
  rsrq: Union[int, None] = Field(default=None, validate_default=True)

  @field_validator("ipv4_addr", "ipv6_addr", "network_name", mode="before")
  @classmethod
  def validate_string_fields(cls, v: Any) -> Union[str, None]:
    """Normalize string fields, converting empty strings and N/A to None"""
    return coerce_str_or_none(v)

  @field_validator("rssi", "rsrp", "sinr", "rsrq", mode="before")
  @classmethod
  def validate_signal_metrics(cls, v: Any) -> Union[int, None]:
    """Convert signal metrics to int or None, handling empty strings and N/A"""
    return coerce_int_or_none(v)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "ExtendedStatus":
    """Create ExtendedStatus from API response dict"""
    return cls.model_validate(data)


class SMSMessage(BaseModel):
  """SMS message information"""

  sms_id: int = Field(alias="SMSId", default=-1)
  phone_number: str = Field(alias="PhoneNumber", default="")
  content: str = Field(alias="SMSContent", default="")
  timestamp: Union[str, None] = Field(alias="SMSTime", default=None)
  status: Union[int, None] = Field(alias="Status", default=None)
  read: Union[bool, None] = Field(alias="Read", default=None)

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

  network_name: Union[str, None] = Field(alias="NetworkName", default=None)
  network_type: int = Field(alias="NetworkType", default=0)
  signal_strength: int = Field(alias="SignalStrength", default=0)
  rssi: Union[int, None] = Field(alias="RSSI", default=None)
  rsrp: Union[int, None] = Field(alias="RSRP", default=None)
  sinr: Union[int, None] = Field(alias="SINR", default=None)
  rsrq: Union[int, None] = Field(alias="RSRQ", default=None)

  @field_validator("rssi", "rsrp", "sinr", "rsrq", mode="before")
  @classmethod
  def validate_signal_metric(cls, v: Any) -> Union[int, None]:
    """Convert signal metrics to int or None, handling empty strings and N/A"""
    return coerce_int_or_none(v)

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
  ipv4_addr: Union[str, None] = Field(alias="IPv4Adrress", default=None, validate_default=True)
  ipv6_addr: Union[str, None] = Field(alias="IPv6Adrress", default=None, validate_default=True)

  @field_validator("ipv4_addr", "ipv6_addr", mode="before")
  @classmethod
  def validate_string_fields(cls, v: Any) -> Union[str, None]:
    """Normalize string fields, converting empty strings and N/A to None"""
    return coerce_str_or_none(v)

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
