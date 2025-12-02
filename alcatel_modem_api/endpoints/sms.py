"""
SMS endpoint namespace
Handles SMS operations: send, list, delete, contacts
"""

from __future__ import annotations

import datetime
import time
from collections.abc import Sequence
from typing import Any

from ..client import AlcatelClient
from ..exceptions import AlcatelAPIError, AlcatelTimeoutError, AuthenticationError
from ..models import SMSMessage


class SMSEndpoint:
  """SMS operations namespace"""

  # SMS send status codes
  SMS_STATUS_NONE = 0
  SMS_STATUS_SENDING = 1
  SMS_STATUS_SUCCESS = 2
  SMS_STATUS_FAIL_SENDING = 3
  SMS_STATUS_FULL = 4
  SMS_STATUS_FAILED = 5

  def __init__(self, client: AlcatelClient):
    """
    Initialize SMS endpoint

    Args:
        client: AlcatelClient instance
    """
    self._client = client

  def send(self, phone_number: str, message: str, timeout: int = 30) -> bool:
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
        AlcatelAPIError: If SMS send fails
        AlcatelTimeoutError: If timeout is reached
    """
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send SMS command
    try:
      self._client.run(
        "SendSMS",
        SMSId=-1,
        SMSContent=message,
        PhoneNumber=[phone_number],
        SMSTime=timestamp,
      )
    except AuthenticationError:
      raise
    except Exception as e:
      raise AlcatelAPIError(f"Failed to send SMS: {str(e)}")

    # Wait a bit before checking status
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
        raise AlcatelAPIError(f"SMS send failed: {error_msg}")

      time.sleep(0.5)

    raise AlcatelTimeoutError(f"SMS send timeout after {timeout} seconds")

  async def send_async(self, phone_number: str, message: str, timeout: int = 30) -> bool:
    """
    Send SMS message (async)

    Args:
        phone_number: Recipient phone number
        message: Message text
        timeout: Maximum wait time in seconds (default: 30)

    Returns:
        True if SMS sent successfully, False otherwise

    Raises:
        AuthenticationError: If authentication is required but failed
        AlcatelAPIError: If SMS send fails
        AlcatelTimeoutError: If timeout is reached
    """
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send SMS command
    try:
      await self._client.run_async(
        "SendSMS",
        SMSId=-1,
        SMSContent=message,
        PhoneNumber=[phone_number],
        SMSTime=timestamp,
      )
    except AuthenticationError:
      raise
    except Exception as e:
      raise AlcatelAPIError(f"Failed to send SMS: {str(e)}")

    # Wait a bit before checking status
    import asyncio

    await asyncio.sleep(1)

    # Poll for send status
    start_time = time.time()
    while time.time() - start_time < timeout:
      status_result = await self.get_send_status_async()
      status = status_result.get("SendStatus", self.SMS_STATUS_NONE)

      if status == self.SMS_STATUS_SUCCESS:
        return True
      elif status >= self.SMS_STATUS_FAIL_SENDING:
        error_msg = self._get_status_message(status)
        raise AlcatelAPIError(f"SMS send failed: {error_msg}")

      await asyncio.sleep(0.5)

    raise AlcatelTimeoutError(f"SMS send timeout after {timeout} seconds")

  def get_send_status(self) -> dict[str, Any]:
    """
    Get SMS send status

    Returns:
        Status dictionary with SendStatus field
    """
    return self._client.run("GetSendSMSResult")

  async def get_send_status_async(self) -> dict[str, Any]:
    """
    Get SMS send status (async)

    Returns:
        Status dictionary with SendStatus field
    """
    return await self._client.run_async("GetSendSMSResult")

  def list(self, contact_number: str | None = None) -> Sequence[SMSMessage]:
    """
    Get SMS list

    Args:
        contact_number: Optional contact number to filter by

    Returns:
        List of SMS messages

    Raises:
        AlcatelAPIError: If the API returns an error response
    """
    if contact_number:
      result = self._client.run("GetSMSListByContactNum", ContactNum=contact_number)
    else:
      # Try without parameters first
      try:
        result = self._client.run("GetSMSListByContactNum")
      except Exception:
        # If that fails, try with empty ContactNum
        result = self._client.run("GetSMSListByContactNum", ContactNum="")

    # Check if result is an error dict
    if isinstance(result, dict) and "error" in result:
      error_msg = result.get("error", {}).get("message", "Unknown error")
      raise AlcatelAPIError(f"SMS list retrieval failed: {error_msg}")

    # Result might be a dict with a list inside, or directly a list
    if isinstance(result, dict):
      # Look for common keys that might contain the list
      for key in ["SMSList", "List", "Messages", "SMS"]:
        if key in result and isinstance(result[key], list):
          return [SMSMessage.from_dict(msg) if isinstance(msg, dict) else msg for msg in result[key]]
      return []

    if isinstance(result, list):
      return [SMSMessage.from_dict(msg) if isinstance(msg, dict) else msg for msg in result]

    return []

  async def list_async(self, contact_number: str | None = None) -> Sequence[SMSMessage]:
    """
    Get SMS list (async)

    Args:
        contact_number: Optional contact number to filter by

    Returns:
        List of SMS messages

    Raises:
        AlcatelAPIError: If the API returns an error response
    """
    if contact_number:
      result = await self._client.run_async("GetSMSListByContactNum", ContactNum=contact_number)
    else:
      # Try without parameters first
      try:
        result = await self._client.run_async("GetSMSListByContactNum")
      except Exception:
        # If that fails, try with empty ContactNum
        result = await self._client.run_async("GetSMSListByContactNum", ContactNum="")

    # Check if result is an error dict
    if isinstance(result, dict) and "error" in result:
      error_msg = result.get("error", {}).get("message", "Unknown error")
      raise AlcatelAPIError(f"SMS list retrieval failed: {error_msg}")

    # Result might be a dict with a list inside, or directly a list
    if isinstance(result, dict):
      # Look for common keys that might contain the list
      for key in ["SMSList", "List", "Messages", "SMS"]:
        if key in result and isinstance(result[key], list):
          return [SMSMessage.from_dict(msg) if isinstance(msg, dict) else msg for msg in result[key]]
      return []

    if isinstance(result, list):
      return [SMSMessage.from_dict(msg) if isinstance(msg, dict) else msg for msg in result]

    return []

  def get_contact_list(self) -> Sequence[dict[str, Any]]:
    """Get SMS contact list"""
    result = self._client.run("GetSMSContactList")
    # Handle different response formats
    if isinstance(result, list):
      return result
    elif isinstance(result, dict):
      # Some modems return dict with list inside
      for key in ["ContactList", "List", "Contacts"]:
        if key in result and isinstance(result[key], list):
          return result[key]  # type: ignore[no-any-return]
      return []
    return []

  async def get_contact_list_async(self) -> Sequence[dict[str, Any]]:
    """Get SMS contact list (async)"""
    result = await self._client.run_async("GetSMSContactList")
    # Handle different response formats
    if isinstance(result, list):
      return result
    elif isinstance(result, dict):
      # Some modems return dict with list inside
      for key in ["ContactList", "List", "Contacts"]:
        if key in result and isinstance(result[key], list):
          return result[key]  # type: ignore[no-any-return]
      return []
    return []

  def get(self, sms_id: int) -> dict[str, Any]:
    """
    Get a single SMS by ID

    Args:
        sms_id: SMS ID

    Returns:
        SMS message dictionary
    """
    return self._client.run("GetSingleSMS", SMSId=sms_id)

  async def get_async(self, sms_id: int) -> dict[str, Any]:
    """
    Get a single SMS by ID (async)

    Args:
        sms_id: SMS ID

    Returns:
        SMS message dictionary
    """
    return await self._client.run_async("GetSingleSMS", SMSId=sms_id)

  def get_storage_state(self) -> dict[str, Any]:
    """Get SMS storage state"""
    return self._client.run("GetSMSStorageState")

  async def get_storage_state_async(self) -> dict[str, Any]:
    """Get SMS storage state (async)"""
    return await self._client.run_async("GetSMSStorageState")

  def get_settings(self) -> dict[str, Any]:
    """Get SMS settings"""
    return self._client.run("GetSMSSettings")

  async def get_settings_async(self) -> dict[str, Any]:
    """Get SMS settings (async)"""
    return await self._client.run_async("GetSMSSettings")

  def get_content_list(self, contact_id: int, page: int = 0) -> dict[str, Any]:
    """
    Get SMS content list for a specific contact (requires login)

    Args:
        contact_id: Contact ID from GetSMSContactList
        page: Page number (default: 0)

    Returns:
        Dict with PhoneNumber, SMSContentList, and optionally TotalPageCount
    """
    result = self._client.run("GetSMSContentList", Page=page, ContactId=contact_id)
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
      return result
    elif isinstance(result, list):
      # If result is directly a list, wrap it
      return {"PhoneNumber": [], "SMSContentList": result, "TotalPageCount": 1}
    return {"PhoneNumber": [], "SMSContentList": [], "TotalPageCount": 0}

  async def get_content_list_async(self, contact_id: int, page: int = 0) -> dict[str, Any]:
    """
    Get SMS content list for a specific contact (async)

    Args:
        contact_id: Contact ID from GetSMSContactList
        page: Page number (default: 0)

    Returns:
        Dict with PhoneNumber, SMSContentList, and optionally TotalPageCount
    """
    result = await self._client.run_async("GetSMSContentList", Page=page, ContactId=contact_id)
    # Handle different response formats
    if isinstance(result, dict):
      if "SMSContentList" in result:
        return result
      elif "SMSList" in result:
        return {
          "PhoneNumber": result.get("PhoneNumber", []),
          "SMSContentList": result["SMSList"] if isinstance(result["SMSList"], list) else [],
          "TotalPageCount": result.get("TotalPageCount", 1),
        }
      return result
    elif isinstance(result, list):
      return {"PhoneNumber": [], "SMSContentList": result, "TotalPageCount": 1}
    return {"PhoneNumber": [], "SMSContentList": [], "TotalPageCount": 0}

  def delete(self, del_flag: int = 0, contact_id: str = "", sms_id: str = "") -> dict[str, Any]:
    """
    Delete SMS messages (requires login)

    Args:
        del_flag: Delete flag (0=all, 1=by contact, 2=by SMS ID)
        contact_id: Contact ID to delete (if del_flag=1)
        sms_id: SMS ID to delete (if del_flag=2)

    Returns:
        Delete result
    """
    return self._client.run("DeleteSMS", DelFlag=del_flag, ContactId=contact_id, SMSId=sms_id)

  async def delete_async(self, del_flag: int = 0, contact_id: str = "", sms_id: str = "") -> dict[str, Any]:
    """
    Delete SMS messages (async)

    Args:
        del_flag: Delete flag (0=all, 1=by contact, 2=by SMS ID)
        contact_id: Contact ID to delete (if del_flag=1)
        sms_id: SMS ID to delete (if del_flag=2)

    Returns:
        Delete result
    """
    return await self._client.run_async("DeleteSMS", DelFlag=del_flag, ContactId=contact_id, SMSId=sms_id)

  def save_draft(self, phone_numbers: Sequence[str], message: str, sms_id: int = -1) -> dict[str, Any]:
    """
    Save SMS as draft (requires login)

    Args:
        phone_numbers: List of phone numbers
        message: Message text
        sms_id: SMS ID (-1 for new draft, existing ID to update)

    Returns:
        Save result
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return self._client.run(
      "SaveSMS",
      SMSId=sms_id,
      SMSContent=message,
      PhoneNumber=phone_numbers,
      SMSTime=timestamp,
    )

  async def save_draft_async(self, phone_numbers: Sequence[str], message: str, sms_id: int = -1) -> dict[str, Any]:
    """
    Save SMS as draft (async)

    Args:
        phone_numbers: List of phone numbers
        message: Message text
        sms_id: SMS ID (-1 for new draft, existing ID to update)

    Returns:
        Save result
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return await self._client.run_async(
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
