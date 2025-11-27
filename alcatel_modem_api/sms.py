"""
SMS management module for Alcatel modems
Handles sending, receiving, and managing SMS messages
"""

import datetime
import time
from typing import Any

from .api import AlcatelModemAPI
from .auth import AuthenticationError


class SMSManager:
  """Manages SMS operations for Alcatel modems"""

  # SMS send status codes
  SMS_STATUS_NONE = 0
  SMS_STATUS_SENDING = 1
  SMS_STATUS_SUCCESS = 2
  SMS_STATUS_FAIL_SENDING = 3
  SMS_STATUS_FULL = 4
  SMS_STATUS_FAILED = 5

  def __init__(self, api: AlcatelModemAPI):
    """
    Initialize SMS manager

    Args:
        api: AlcatelModemAPI instance
    """
    self.api = api

  def send_sms(self, phone_number: str, message: str, timeout: int = 30) -> bool:
    """
    Send SMS message

    Args:
        phone_number: Recipient phone number
        message: Message text
        timeout: Maximum wait time in seconds (default: 30)

    Returns:
        True if SMS sent successfully, False otherwise

    Raises:
        AuthenticationError: If authentication is required but failed
    """
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send SMS command
    try:
      self.api.run(
        "SendSMS",
        SMSId=-1,
        SMSContent=message,
        PhoneNumber=[phone_number],
        SMSTime=timestamp,
      )
    except AuthenticationError:
      raise
    except Exception as e:
      raise Exception(f"Failed to send SMS: {str(e)}")

    # Wait a bit before checking status (as per IK40V implementation)
    time.sleep(1)

    # Poll for send status
    start_time = time.time()
    while time.time() - start_time < timeout:
      status_result = self.get_send_status()
      status = status_result.get("SendStatus", self.SMS_STATUS_NONE)

      if status == self.SMS_STATUS_SUCCESS:
        return True
      elif status >= self.SMS_STATUS_FAIL_SENDING:
        error_msg = self._get_status_message(status)
        raise Exception(f"SMS send failed: {error_msg}")

      time.sleep(0.5)

    raise Exception(f"SMS send timeout after {timeout} seconds")

  def get_send_status(self) -> dict[Any, Any]:
    """
    Get SMS send status

    Returns:
        Status dictionary with SendStatus field
    """
    return self.api.run("GetSendSMSResult")

  def get_sms_list(self, contact_number: str | None = None) -> list[dict[Any, Any]]:
    """
    Get SMS list

    Args:
        contact_number: Optional contact number to filter by

    Returns:
        List of SMS messages
    """
    if contact_number:
      result = self.api.run("GetSMSListByContactNum", ContactNum=contact_number)
    else:
      # Try without parameters first
      try:
        result = self.api.run("GetSMSListByContactNum")
      except Exception:
        # If that fails, try with empty ContactNum
        result = self.api.run("GetSMSListByContactNum", ContactNum="")

    # Result might be a dict with a list inside, or directly a list
    if isinstance(result, dict):
      # Look for common keys that might contain the list
      for key in ["SMSList", "List", "Messages", "SMS"]:
        if key in result and isinstance(result[key], list):
          return result[key]
      # If no list found, return the dict itself
      return [result] if result else []

    return result if isinstance(result, list) else []

  def get_sms_contact_list(self) -> list[dict[Any, Any]]:
    """Get SMS contact list"""
    result = self.api.run("GetSMSContactList")
    # Handle different response formats
    if isinstance(result, list):
      return result
    elif isinstance(result, dict):
      # Some modems return dict with list inside
      for key in ["ContactList", "List", "Contacts"]:
        if key in result and isinstance(result[key], list):
          return result[key]
      # If no list found, return empty list
      return []
    return []

  def get_single_sms(self, sms_id: int) -> dict[Any, Any]:
    """
    Get a single SMS by ID

    Args:
        sms_id: SMS ID

    Returns:
        SMS message dictionary
    """
    return self.api.run("GetSingleSMS", SMSId=sms_id)

  def get_sms_storage_state(self) -> dict[Any, Any]:
    """Get SMS storage state"""
    return self.api.run("GetSMSStorageState")

  def get_sms_settings(self) -> dict[Any, Any]:
    """Get SMS settings"""
    return self.api.run("GetSMSSettings")

  def get_sms_content_list(self, contact_id: int, page: int = 0) -> dict[Any, Any]:
    """
    Get SMS content list for a specific contact (requires login)

    Based on web interface JavaScript: SDK.SMS.GetSMSContentList(Page, ContactId)
    Returns: {
        "PhoneNumber": [...],  # Array of phone numbers
        "SMSContentList": [...],  # Array of SMS messages
        "TotalPageCount": int  # Optional: total pages
    }

    Args:
        contact_id: Contact ID from GetSMSContactList
        page: Page number (default: 0)

    Returns:
        Dict with PhoneNumber, SMSContentList, and optionally TotalPageCount
    """
    result = self.api.run("GetSMSContentList", Page=page, ContactId=contact_id)
    # Handle different response formats
    if isinstance(result, dict):
      # Web interface format: PhoneNumber, SMSContentList
      if "SMSContentList" in result:
        return result
      # Alternative format: SMSList
      elif "SMSList" in result:
        return {
          "PhoneNumber": result.get("PhoneNumber", []),
          "SMSContentList": result["SMSList"] if isinstance(result["SMSList"], list) else [],
          "TotalPageCount": result.get("TotalPageCount", 1),
        }
      # Return as-is if already in correct format
      return result
    elif isinstance(result, list):
      # If result is directly a list, wrap it
      return {"PhoneNumber": [], "SMSContentList": result, "TotalPageCount": 1}
    return {"PhoneNumber": [], "SMSContentList": [], "TotalPageCount": 0}

  def delete_sms(self, del_flag: int = 0, contact_id: str = "", sms_id: str = "") -> dict[Any, Any]:
    """
    Delete SMS messages (requires login)

    Args:
        del_flag: Delete flag (0=all, 1=by contact, 2=by SMS ID)
        contact_id: Contact ID to delete (if del_flag=1)
        sms_id: SMS ID to delete (if del_flag=2)

    Returns:
        Delete result
    """
    return self.api.run("DeleteSMS", DelFlag=del_flag, ContactId=contact_id, SMSId=sms_id)

  def save_sms_draft(self, phone_numbers: list[str], message: str, sms_id: int = -1) -> dict[Any, Any]:
    """
    Save SMS as draft (requires login)

    Based on web interface JavaScript: SDK.SMS.SaveSMS(SMSId, SMSContent, PhoneNumber, SMSTime)

    Args:
        phone_numbers: List of phone numbers
        message: Message text
        sms_id: SMS ID (-1 for new draft, existing ID to update)

    Returns:
        Save result
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return self.api.run(
      "SaveSMS",
      SMSId=sms_id,
      SMSContent=message,
      PhoneNumber=phone_numbers,
      SMSTime=timestamp,
    )

  def _get_status_message(self, status: int) -> str:
    """Get human-readable status message"""
    status_messages = {
      self.SMS_STATUS_NONE: "No status",
      self.SMS_STATUS_SENDING: "Sending",
      self.SMS_STATUS_SUCCESS: "Success",
      self.SMS_STATUS_FAIL_SENDING: "Failed while sending",
      self.SMS_STATUS_FULL: "Memory full",
      self.SMS_STATUS_FAILED: "Failed",
    }
    return status_messages.get(status, f"Unknown status: {status}")
