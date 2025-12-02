"""
Pydantic models for diagnostic reports with automatic field masking
"""

from typing import Any, Optional

from pydantic import BaseModel, field_serializer, field_validator


class DiagnosticReport(BaseModel):
  """
  Diagnostic report model with automatic sensitive data masking

  This model ensures sensitive information (passwords, IMEI, serial numbers)
  is automatically masked when serialized, preventing accidental exposure.
  """

  library_version: str
  python_version: str
  connection: dict[str, Any]
  modem_info: dict[str, Any]
  api_endpoints: dict[str, Any]
  errors: list[str]
  security: Optional[dict[str, Any]] = None

  @field_validator("connection", mode="before")
  @classmethod
  def mask_password_in_connection(cls, v: Any) -> Any:
    """Mask password in connection dict"""
    if isinstance(v, dict):
      result = v.copy()
      if "password" in result:
        result["password"] = "********"  # nosec B105  # This is a mask, not a real password
      if "password_provided" in result:
        # Keep the boolean, just mask the actual password
        pass
      return result
    return v

  @field_validator("modem_info", mode="before")
  @classmethod
  def mask_sensitive_modem_info(cls, v: Any) -> Any:
    """Mask IMEI, serial numbers, and other sensitive modem info"""
    if isinstance(v, dict):
      result = v.copy()
      sensitive_keys = ["IMEI", "imei", "SerialNumber", "serial_number", "MAC", "mac", "WifiPassword", "wifi_password"]
      for key in sensitive_keys:
        if key in result:
          result[key] = "********"
      return result
    return v

  @field_serializer("connection", "modem_info")
  def serialize_with_masking(self, value: Any, _info: Any) -> Any:
    """Ensure sensitive data is masked during serialization"""
    if isinstance(value, dict):
      result = value.copy()
      # Double-check for any password-like fields
      for key in list(result.keys()):
        if "password" in key.lower() or key in ["IMEI", "imei", "SerialNumber", "serial_number"]:
          if not isinstance(result[key], bool):  # Don't mask booleans
            result[key] = "********"
      return result
    return value

  def model_dump_safe(self) -> dict[str, Any]:
    """
    Dump model with all sensitive fields properly masked

    Returns:
        Dictionary representation with sensitive data masked
    """
    return self.model_dump(mode="json", exclude_none=True)
