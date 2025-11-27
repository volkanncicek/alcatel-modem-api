"""
Main API class for Alcatel modems
Provides unified interface for all Alcatel modem operations
"""

import json
from typing import Any

import requests

from .auth import AuthenticationError, TokenManager, encrypt_admin, encrypt_token


class AlcatelModemAPI:
  """
  Generic API client for Alcatel LTE modems

  Supports Alcatel modems that use the /jrd/webapi endpoint.
  See README.md for a list of tested models.
  """

  # Default headers for API requests
  DEFAULT_VERIFICATION_KEY = "KSDHSDFOGQ5WERYTUIQWERTYUISDFG1HJZXCVCXBN2GDSMNDHKVKFsVBNf"

  def __init__(
    self,
    url: str = "http://192.168.1.1",
    password: str | None = None,
    session_file: str | None = None,
  ):
    """
    Initialize Alcatel Modem API client

    Args:
        url: Base URL of the modem (default: http://192.168.1.1)
        password: Admin password (optional, required for protected commands)
        session_file: Path to session token file (optional)
    """
    self._url = url.rstrip("/")
    self._password = password
    self._token_manager = TokenManager(session_file if session_file else None)

    self.session = requests.Session()
    self.session.headers = {
      "_TclRequestVerificationKey": self.DEFAULT_VERIFICATION_KEY,
      "Referer": self._url,
      "Content-Type": "application/json",
      "Accept": "text/plain, */*; q=0.01",
      "X-Requested-With": "XMLHttpRequest",
    }

    # Restore token if available
    token = self._token_manager.get_token()
    if token:
      self.session.headers["_TclRequestVerificationToken"] = token

  def set_password(self, password: str) -> None:
    """Set admin password"""
    self._password = password

  def _get_login_state(self) -> bool:
    """Check if already logged in"""
    try:
      result = self._run_command("GetLoginState")
      logged_in = result.get("State") == 1

      if logged_in:
        token = self._token_manager.get_token()
        if token:
          self.session.headers["_TclRequestVerificationToken"] = token
          return True
        return False

      return False
    except Exception:
      return False

  def _login(self) -> None:
    """Login to modem with admin credentials"""
    if not self._password:
      raise AuthenticationError("Password is required for login")

    try:
      # MW40V1 için şifreleme gerekmiyor, direkt gönder
      # HH72 gibi modeller için şifreleme gerekli
      # Önce şifrelenmemiş dene (MW40V1)
      try:
        result = self._run_command("Login", UserName="admin", Password=self._password)
      except Exception:
        # Şifrelenmemiş çalışmadıysa şifrelenmiş dene (HH72)
        result = self._run_command(
          "Login",
          UserName=encrypt_admin("admin"),
          Password=encrypt_admin(self._password),
        )

      token = result["token"]

      # Check if param0 and param1 exist (HH72 style encryption)
      # If not, use token directly (MW40V1 style)
      if "param0" in result and "param1" in result:
        key = result["param0"]
        iv = result["param1"]
        encrypted_token = encrypt_token(token, key, iv)
      else:
        # MW40V1 and similar models use token directly
        encrypted_token = str(token)

      self._token_manager.save_token(encrypted_token)
      self.session.headers["_TclRequestVerificationToken"] = encrypted_token

    except Exception as e:
      if isinstance(e, AuthenticationError):
        raise
      raise AuthenticationError(f"Login failed: {str(e)}")

  def _run_command(self, command: str, **params) -> dict[Any, Any]:
    """
    Execute a JSON-RPC command on the modem

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Command result dictionary

    Raises:
        Exception: If command fails
    """
    # Handle empty params - use None instead of empty dict
    if not params:
      params_value = None
    else:
      params_value = params

    message = {
      "jsonrpc": "2.0",
      "method": command,
      "id": "1",
      "params": params_value,
    }

    api_url = f"{self._url}/jrd/webapi"
    resp = self.session.post(api_url, json=message, timeout=10)

    if resp.status_code != 200:
      raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

    result = resp.json()

    if "error" in result:
      error = result["error"]
      error_code = error.get("code", "unknown")
      error_msg = error.get("message", "Unknown error")

      # Check if it's an authentication error
      if error_code == -32699 or "Authentication" in error_msg:
        raise AuthenticationError(f"Authentication failed: {error_msg}")

      raise Exception(f"Command failed: {error_msg} (code: {error_code})")

    if "result" not in result:
      raise Exception(f"Unexpected response: {result}")

    return result["result"]

  def run(self, command: str, **params) -> dict[Any, Any]:
    """
    Run a command (with automatic login if needed)

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Command result
    """
    # Auto-login if password is set and not logged in
    if self._password:
      if not self._get_login_state():
        self._login()

    return self._run_command(command, **params)

  def run_pretty(self, command: str, **params) -> str:
    """
    Run a command and return pretty-printed JSON

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Pretty-printed JSON string
    """
    result = self.run(command, **params)
    return json.dumps(result, indent=2, ensure_ascii=False)

  def logout(self) -> None:
    """Clear authentication token"""
    self._token_manager.clear_token()
    if "_TclRequestVerificationToken" in self.session.headers:
      del self.session.headers["_TclRequestVerificationToken"]

  # Convenience methods for common commands
  def get_system_status(self) -> dict[Any, Any]:
    """Get system status"""
    return self.run("GetSystemStatus")

  def get_sim_status(self) -> dict[Any, Any]:
    """Get SIM card status"""
    return self.run("GetSimStatus")

  def get_network_info(self) -> dict[Any, Any]:
    """Get network information (requires login)"""
    return self.run("GetNetworkInfo")

  def get_system_info(self) -> dict[Any, Any]:
    """Get system information"""
    return self.run("GetSystemInfo")

  def get_connection_state(self) -> dict[Any, Any]:
    """Get connection state (requires login)"""
    return self.run("GetConnectionState")

  def get_wlan_settings(self) -> dict[Any, Any]:
    """Get WiFi settings (requires login)"""
    return self.run("GetWlanSettings")

  def get_lan_settings(self) -> dict[Any, Any]:
    """Get LAN settings (requires login)"""
    return self.run("GetLanSettings")

  def get_sms_storage_state(self) -> dict[Any, Any]:
    """Get SMS storage state (public command, no login required)"""
    return self.run("GetSMSStorageState")

  # Device Management (requires login)
  def get_connected_device_list(self) -> dict[Any, Any]:
    """Get list of connected devices (requires login)"""
    return self.run("GetConnectedDeviceList")

  def get_block_device_list(self) -> dict[Any, Any]:
    """Get list of blocked devices (requires login)"""
    return self.run("GetBlockDeviceList")

  def block_device(self, device_name: str, mac_address: str) -> dict[Any, Any]:
    """
    Block a connected device (requires login)

    Args:
        device_name: Name of the device to block
        mac_address: MAC address of the device to block
    """
    return self.run("SetConnectedDeviceBlock", DeviceName=device_name, MacAddress=mac_address)

  def unblock_device(self, device_name: str, mac_address: str) -> dict[Any, Any]:
    """
    Unblock a device (requires login)

    Args:
        device_name: Name of the device to unblock
        mac_address: MAC address of the device to unblock
    """
    return self.run("SetDeviceUnlock", DeviceName=device_name, MacAddress=mac_address)

  # WiFi Settings (write - requires login)
  def set_wlan_settings(self, **kwargs) -> dict[Any, Any]:
    """
    Set WiFi settings (requires login)

    Args:
        **kwargs: WiFi settings (ApStatus, Ssid, SecurityMode, WpaKey, etc.)

    Example:
        api.set_wlan_settings(ApStatus=1, Ssid="MyNetwork", SecurityMode=3, WpaKey="password123")
    """
    return self.run("SetWlanSettings", **kwargs)

  # Connection Management (requires login)
  def connect(self) -> dict[Any, Any]:
    """Connect to network (requires login)"""
    return self.run("Connect")

  def disconnect(self) -> dict[Any, Any]:
    """Disconnect from network (requires login)"""
    return self.run("DisConnect")

  # Network Settings (requires login)
  def get_network_settings(self) -> dict[Any, Any]:
    """Get network settings (requires login)"""
    return self.run("GetNetworkSettings")

  def set_network_settings(self, network_mode: int, net_selection_mode: int = 0) -> dict[Any, Any]:
    """
    Set network settings (requires login)

    Args:
        network_mode: Network mode (0=Auto, 1=2G, 2=3G, 3=4G, 255=Auto)
        net_selection_mode: Network selection mode (0=Auto, 1=Manual)
    """
    return self.run(
      "SetNetworkSettings",
      NetworkMode=network_mode,
      NetselectionMode=net_selection_mode,
    )

  # USSD Management (requires login)
  def send_ussd(self, ussd_content: str, ussd_type: int = 1) -> dict[Any, Any]:
    """
    Send USSD code (requires login)

    Args:
        ussd_content: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)
    """
    return self.run("SendUSSD", UssdContent=ussd_content, UssdType=ussd_type)

  def get_ussd_send_result(self) -> dict[Any, Any]:
    """Get USSD send result (requires login)"""
    return self.run("GetUSSDSendResult")

  def set_ussd_end(self) -> dict[Any, Any]:
    """End USSD session (requires login)"""
    return self.run("SetUSSDEnd")

  def send_ussd_code(self, code: str, ussd_type: int = 1, wait_seconds: int = 5) -> dict[Any, Any]:
    """
    Send USSD code and wait for result (requires login)

    Args:
        code: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)
        wait_seconds: Seconds to wait before getting result (default: 5)

    Returns:
        Dict with UssdType, SendState, UssdContent
    """
    import time

    self.send_ussd(code, ussd_type)
    time.sleep(wait_seconds)
    return self.get_ussd_send_result()

  # Poll methods for easy status retrieval
  def poll_basic_status(self) -> dict[str, Any]:
    """
    Poll basic status (does NOT require login)
    Returns: imei, iccid, device, connection_status, network_type, network_name, strength
    """
    system_info = self.get_system_info()
    system_status = self.get_system_status()

    from .constants import get_connection_status, get_network_type

    return {
      "imei": system_info.get("IMEI", ""),
      "iccid": system_info.get("ICCID", ""),
      "device": system_info.get("DeviceName", ""),
      "connection_status": get_connection_status(system_status.get("ConnectionStatus", 0)),
      "network_type": get_network_type(system_status.get("NetworkType", 0)),
      "network_name": system_status.get("NetworkName"),
      "strength": system_status.get("SignalStrength", 0),
    }

  def poll_extended_status(self) -> dict[str, Any]:
    """
    Poll extended status (REQUIRES login)
    Returns: All basic status plus bytes_in, bytes_out, rates, IP addresses, RSSI, RSRP, etc.
    """
    system_info = self.get_system_info()
    network_info = self.get_network_info()
    connection_state = self.get_connection_state()

    from .constants import get_connection_status, get_network_type

    return {
      "imei": system_info.get("IMEI", ""),
      "iccid": system_info.get("ICCID", ""),
      "device": system_info.get("DeviceName", ""),
      "connection_status": get_connection_status(connection_state.get("ConnectionStatus", 0)),
      "bytes_in": connection_state.get("DlBytes", 0),
      "bytes_out": connection_state.get("UlBytes", 0),
      "bytes_in_rate": connection_state.get("DlRate", 0),
      "bytes_out_rate": connection_state.get("UlRate", 0),
      "ipv4_addr": connection_state.get("IPv4Adrress"),
      "ipv6_addr": connection_state.get("IPv6Adrress"),
      "network_name": network_info.get("NetworkName"),
      "network_type": get_network_type(network_info.get("NetworkType", 0)),
      "strength": network_info.get("SignalStrength", 0),
      "rssi": int(network_info.get("RSSI", -999)) if network_info.get("RSSI") else None,
      "rsrp": int(network_info.get("RSRP", -999)) if network_info.get("RSRP") else None,
      "sinr": int(network_info.get("SINR", -999)) if network_info.get("SINR") else None,
      "rsrq": int(network_info.get("RSRQ", -999)) if network_info.get("RSRQ") else None,
    }

  def poll(self) -> dict[str, Any]:
    """
    Poll extended status (REQUIRES login)
    Alias for poll_extended_status() to match TypeScript API

    @deprecated Use poll_extended_status() for clarity
    """
    return self.poll_extended_status()
