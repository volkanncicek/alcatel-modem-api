"""
Core HTTP client for Alcatel Modem API
Handles HTTP requests, authentication, retry logic, and token management
"""

import json
import os
import platform
import stat
from pathlib import Path
from typing import Any, Dict, Protocol, Union

import httpx

from .exceptions import (
  AlcatelAPIError,
  AlcatelConnectionError,
  AlcatelFeatureNotSupportedError,
  AlcatelSimMissingError,
  AlcatelSystemBusyError,
  AlcatelTimeoutError,
  AuthenticationError,
  UnsupportedModemError,
)
from .utils.encryption import encrypt_admin, encrypt_token
from .utils.logging import get_logger

logger = get_logger(__name__)

# Default headers for API requests
DEFAULT_VERIFICATION_KEY = "KSDHSDFOGQ5WERYTUIQWERTYUISDFG1HJZXCVCXBN2GDSMNDHKVKFsVBNf"

# HTTP status code error messages
HTTP_STATUS_MESSAGES = {
  400: "Bad Request - Invalid parameters or malformed request",
  401: "Unauthorized - Authentication required",
  403: "Forbidden - Access denied",
  404: "Not Found - Endpoint or resource not found",
  405: "Method Not Allowed - HTTP method not supported for this endpoint",
  429: "Too Many Requests - Rate limit exceeded",
  500: "Internal Server Error - Modem encountered an error",
  502: "Bad Gateway - Invalid response from modem",
  503: "Service Unavailable - Modem is temporarily unavailable",
  504: "Gateway Timeout - Request timed out",
}


def format_http_error(status_code: int, response_text: str = "") -> str:
  """
  Format HTTP error message with descriptive text

  Args:
      status_code: HTTP status code
      response_text: Response body text (optional)

  Returns:
      Formatted error message
  """
  status_msg = HTTP_STATUS_MESSAGES.get(status_code, f"HTTP {status_code} error")
  error_text = response_text[:200].strip() if response_text else ""

  if error_text:
    return f"{status_msg}: {error_text}"
  else:
    return status_msg


def detect_modem_brand(response: httpx.Response) -> Union[str, None]:
  """
  Detect modem brand from HTTP response headers and body

  Args:
      response: HTTP response object

  Returns:
      Detected brand name or None if unknown
  """
  # Check all headers (case-insensitive)
  all_headers = {k.lower(): v.lower() for k, v in response.headers.items()}

  # Check Server header
  server = all_headers.get("server", "")
  if "keenetic" in server:
    return "Keenetic"
  if "huawei" in server or "hilink" in server:
    return "Huawei"
  if "netgear" in server:
    return "Netgear"
  if "tp-link" in server or "tplink" in server:
    return "TP-Link"
  if "d-link" in server or "dlink" in server:
    return "D-Link"
  if "asus" in server:
    return "ASUS"
  if "zyxel" in server:
    return "Zyxel"

  # Check X-Powered-By or other custom headers
  powered_by = all_headers.get("x-powered-by", "")
  if "keenetic" in powered_by:
    return "Keenetic"

  # Check response body for brand indicators (more characters for better detection)
  try:
    body_text = response.text[:1000].lower()
    if "keenetic" in body_text or "keeneticos" in body_text:
      return "Keenetic"
    if "huawei" in body_text or "hilink" in body_text:
      return "Huawei"
    if "netgear" in body_text:
      return "Netgear"
    if "tp-link" in body_text or "tplink" in body_text:
      return "TP-Link"
    if "d-link" in body_text or "dlink" in body_text:
      return "D-Link"
    if "asus" in body_text:
      return "ASUS"
    if "zyxel" in body_text:
      return "Zyxel"
  except Exception:
    pass

  return None


class TokenStorageProtocol(Protocol):
  """Protocol for token storage implementations"""

  def save_token(self, token: str) -> None:
    """Save token to storage"""
    ...

  def get_token(self) -> str:
    """Get current token from storage"""
    ...

  def clear_token(self) -> None:
    """Clear stored token"""
    ...


class FileTokenStorage:
  """File-based token storage implementation"""

  def __init__(self, session_file: Union[str, None] = None):
    """
    Initialize file-based token storage

    Args:
        session_file: Path to session file (default: ~/.alcatel_modem_session)
    """
    if session_file is None:
      home = Path.home()
      session_file = str(home / ".alcatel_modem_session")

    self.session_file = session_file
    self._token: Union[str, None] = None
    self._restore_token()

  def save_token(self, token: str) -> None:
    """Save token to file"""
    self._token = token
    try:
      with open(self.session_file, "w") as f:
        f.write(token)
      # Set file permissions to 600 (read/write for owner only)
      try:
        if platform.system() != "Windows":
          os.chmod(self.session_file, stat.S_IRUSR | stat.S_IWUSR)
        else:
          os.chmod(self.session_file, stat.S_IREAD | stat.S_IWRITE)
      except (OSError, AttributeError) as e:
        logger.warning(f"Could not secure session file permissions: {e}")
    except Exception as e:
      logger.warning(f"Could not save token to file: {e}")

  def _restore_token(self) -> None:
    """Restore token from file"""
    try:
      if os.path.exists(self.session_file):
        with open(self.session_file) as f:
          self._token = f.read().strip()
    except Exception as e:
      logger.debug(f"Could not restore token from file: {e}")
      self._token = None

  def get_token(self) -> str:
    """Get current token"""
    return self._token if self._token else ""

  def clear_token(self) -> None:
    """Clear stored token"""
    self._token = None
    try:
      if os.path.exists(self.session_file):
        os.remove(self.session_file)
    except Exception as e:
      logger.debug(f"Could not remove token file: {e}")


class MemoryTokenStorage:
  """In-memory token storage implementation (useful for web apps, testing)"""

  def __init__(self) -> None:
    """Initialize in-memory token storage"""
    self._token: Union[str, None] = None

  def save_token(self, token: str) -> None:
    """Save token to memory"""
    self._token = token

  def get_token(self) -> str:
    """Get current token from memory"""
    return self._token if self._token else ""

  def clear_token(self) -> None:
    """Clear stored token"""
    self._token = None


class AlcatelClient:
  """
  Core HTTP client for Alcatel LTE modems

  Supports both sync and async operations using httpx.
  Handles authentication, retry logic, and token management.
  """

  def __init__(
    self,
    url: str = "http://192.168.1.1",
    password: Union[str, None] = None,
    session_file: Union[str, None] = None,
    timeout: int = 10,
    token_storage: Union[TokenStorageProtocol, None] = None,
  ):
    """
    Initialize Alcatel Modem API client

    Args:
        url: Base URL of the modem (default: http://192.168.1.1)
        password: Admin password (optional, required for protected commands)
        session_file: Path to session token file (optional)
        timeout: Request timeout in seconds (default: 10)
        token_storage: Custom token storage implementation (optional)
    """
    self._url = url.rstrip("/")
    self._password = password
    self._timeout = timeout

    # Token storage - try keyring first, fallback to file
    if token_storage:
      self._token_manager = token_storage
    else:
      # Try to use keyring storage with file fallback
      try:
        from .utils.keyring_storage import KeyringTokenStorage

        self._token_manager = KeyringTokenStorage(session_file, use_keyring=True)
      except (ImportError, Exception):
        # Fallback to file storage if keyring not available or fails
        logger.debug("Keyring not available, using file storage")
        self._token_manager = FileTokenStorage(session_file if session_file else None)

    # Default headers
    self._default_headers = {
      "_TclRequestVerificationKey": DEFAULT_VERIFICATION_KEY,
      "Referer": self._url,
      "Content-Type": "application/json",
      "Accept": "text/plain, */*; q=0.01",
      "X-Requested-With": "XMLHttpRequest",
    }

    # Restore token if available
    token = self._token_manager.get_token()
    if token:
      self._default_headers["_TclRequestVerificationToken"] = token

    # Create httpx clients with retry logic
    retry_transport = httpx.HTTPTransport(retries=3)
    self._client = httpx.Client(
      timeout=timeout,
      transport=retry_transport,
      headers=self._default_headers.copy(),
    )

    # Async client will be created on first use
    self._async_client: Union[httpx.AsyncClient, None] = None

    # Initialize endpoint namespaces
    from .endpoints.device import DeviceEndpoint
    from .endpoints.network import NetworkEndpoint
    from .endpoints.sms import SMSEndpoint
    from .endpoints.system import SystemEndpoint
    from .endpoints.wlan import WLANEndpoint

    self.sms = SMSEndpoint(self)
    self.network = NetworkEndpoint(self)
    self.wlan = WLANEndpoint(self)
    self.device = DeviceEndpoint(self)
    self.system = SystemEndpoint(self)

  def set_password(self, password: str) -> None:
    """Set admin password"""
    self._password = password

  def _raise_unsupported_modem_error(self, resp: httpx.Response, detected_brand: Union[str, None]) -> None:
    """
    Raise UnsupportedModemError with appropriate message

    Args:
        resp: HTTP response object
        detected_brand: Detected modem brand or None

    Raises:
        UnsupportedModemError: Always raises this exception
    """
    if detected_brand:
      raise UnsupportedModemError(
        f"This library only supports Alcatel modems. "
        f"Detected modem brand: {detected_brand}. "
        f"Please use a library designed for {detected_brand} modems, "
        f"or connect to an Alcatel modem that supports the /jrd/webapi endpoint."
      )
    else:
      raise UnsupportedModemError(
        f"This library only supports Alcatel modems with the /jrd/webapi endpoint. "
        f"The endpoint returned HTTP {resp.status_code}, which suggests this is not an Alcatel modem "
        f"or the modem doesn't support the Alcatel API. "
        f"Please verify you're connecting to an Alcatel modem (MW40V1, HH72, HH40V, etc.) "
        f"or use a library designed for your modem brand."
      )

  def _check_unsupported_modem(self, resp: httpx.Response) -> None:
    """
    Check if response indicates an unsupported modem and raise appropriate error (sync)

    Args:
        resp: HTTP response object

    Raises:
        UnsupportedModemError: If modem is detected as non-Alcatel
    """
    if resp.status_code not in (404, 405):
      return  # Only check for 404/405 errors

    # Try to detect brand from current response first
    detected_brand = detect_modem_brand(resp)

    # If not detected and response body is empty, try root page for better detection
    if not detected_brand and not resp.text.strip():
      try:
        root_resp = self._client.get(self._url, timeout=2)
        detected_brand = detect_modem_brand(root_resp)
      except Exception:
        pass  # Ignore errors when checking root page

    self._raise_unsupported_modem_error(resp, detected_brand)

  async def _check_unsupported_modem_async(self, resp: httpx.Response) -> None:
    """
    Check if response indicates an unsupported modem and raise appropriate error (async)

    Args:
        resp: HTTP response object

    Raises:
        UnsupportedModemError: If modem is detected as non-Alcatel
    """
    if resp.status_code not in (404, 405):
      return  # Only check for 404/405 errors

    # Try to detect brand from current response first
    detected_brand = detect_modem_brand(resp)

    # If not detected and response body is empty, try root page for better detection
    if not detected_brand and not resp.text.strip():
      try:
        if self._async_client is not None:
          root_resp = await self._async_client.get(self._url, timeout=2)
          detected_brand = detect_modem_brand(root_resp)
      except Exception:
        pass  # Ignore errors when checking root page

    self._raise_unsupported_modem_error(resp, detected_brand)

  def _get_login_state(self) -> bool:
    """Check if already logged in"""
    try:
      result = self._run_command("GetLoginState")
      if result.get("State") == 1:  # 1 = logged in, 0 = logged out
        token = self._token_manager.get_token()
        if token:
          self._default_headers["_TclRequestVerificationToken"] = token
          self._client.headers["_TclRequestVerificationToken"] = token
          return True
      return False
    except Exception:
      return False

  async def _get_login_state_async(self) -> bool:
    """Check if already logged in (async)"""
    try:
      # Use _run_command_async directly
      result = await self._run_command_async("GetLoginState")
      if result.get("State") == 1:
        token = self._token_manager.get_token()
        if token:
          self._default_headers["_TclRequestVerificationToken"] = token
          if self._async_client:
            self._async_client.headers["_TclRequestVerificationToken"] = token
          return True
      return False
    except Exception:
      return False

  def _login(self) -> None:
    """Login to modem with admin credentials"""
    if not self._password:
      raise AuthenticationError("Password is required for login")

    try:
      # Try unencrypted first (MW40V1 style)
      try:
        result = self._run_command("Login", UserName="admin", Password=self._password)
      except Exception:
        # If that fails, try encrypted (HH72 style)
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
      self._default_headers["_TclRequestVerificationToken"] = encrypted_token
      self._client.headers["_TclRequestVerificationToken"] = encrypted_token
      if self._async_client is not None:
        self._async_client.headers["_TclRequestVerificationToken"] = encrypted_token

    except Exception as e:
      if isinstance(e, AuthenticationError):
        raise
      raise AuthenticationError(f"Login failed: {str(e)}")

  async def _login_async(self) -> None:
    """Login to modem with admin credentials (async)"""
    if not self._password:
      raise AuthenticationError("Password is required for login")

    try:
      try:
        result = await self._run_command_async("Login", UserName="admin", Password=self._password)
      except Exception:
        result = await self._run_command_async("Login", UserName=encrypt_admin("admin"), Password=encrypt_admin(self._password))

      token = result["token"]

      if "param0" in result and "param1" in result:
        encrypted_token = encrypt_token(token, result["param0"], result["param1"])
      else:
        encrypted_token = str(token)

      self._token_manager.save_token(encrypted_token)
      self._default_headers["_TclRequestVerificationToken"] = encrypted_token
      if self._async_client:
        self._async_client.headers["_TclRequestVerificationToken"] = encrypted_token

    except Exception as e:
      if isinstance(e, AuthenticationError):
        raise
      raise AuthenticationError(f"Login failed: {str(e)}")

  def _run_command(self, command: str, **params: Any) -> dict[str, Any]:
    """
    Execute a JSON-RPC command on the modem (sync)

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Command result dictionary

    Raises:
        AlcatelAPIError: If command fails
        AlcatelConnectionError: If connection fails
        AlcatelTimeoutError: If request times out
        AuthenticationError: If authentication fails
    """
    # Handle empty params - use None instead of empty dict
    params_value = params if params else None

    message = {
      "jsonrpc": "2.0",
      "method": command,
      "id": "1",
      "params": params_value,
    }

    api_url = f"{self._url}/jrd/webapi"

    try:
      resp = self._client.post(api_url, json=message)
    except httpx.TimeoutException as e:
      raise AlcatelTimeoutError(f"Request timed out after {self._timeout} seconds: {str(e)}")
    except httpx.ConnectError as e:
      raise AlcatelConnectionError(f"Failed to connect to modem at {self._url}: {str(e)}")
    except httpx.RequestError as e:
      raise AlcatelConnectionError(f"Request failed: {str(e)}")

    if resp.status_code != 200:
      # Check if this might be an unsupported modem (405/404 on /jrd/webapi endpoint)
      self._check_unsupported_modem(resp)

      error_msg = format_http_error(resp.status_code, resp.text)
      raise AlcatelConnectionError(error_msg)

    # Handle JSON decode errors
    try:
      result = resp.json()
    except (ValueError, json.JSONDecodeError):
      raise AlcatelAPIError(f"Invalid response from modem (not JSON). HTTP {resp.status_code}: {resp.text[:200]}")

    if "error" in result:
      error = result["error"]
      error_code = error.get("code", "unknown")
      error_msg = error.get("message", "Unknown error")

      # Check if it's an authentication error
      if error_code == -32699 or "Authentication" in error_msg:
        raise AuthenticationError(f"Authentication failed: {error_msg}")

      # Map common error messages to specific exceptions
      error_msg_lower = error_msg.lower()
      if "system busy" in error_msg_lower or "busy" in error_msg_lower:
        raise AlcatelSystemBusyError(f"Modem system is busy: {error_msg}", error_code=error_code)
      if "sim" in error_msg_lower and ("missing" in error_msg_lower or "not" in error_msg_lower):
        raise AlcatelSimMissingError(f"SIM card issue: {error_msg}", error_code=error_code)
      if "not supported" in error_msg_lower or "unsupported" in error_msg_lower:
        raise AlcatelFeatureNotSupportedError(f"Feature not supported: {error_msg}", error_code=error_code)

      raise AlcatelAPIError(f"Command failed: {error_msg} (code: {error_code})", error_code=error_code)

    if "result" not in result:
      raise AlcatelAPIError(f"Unexpected response: {result}")

    return result["result"]  # type: ignore[no-any-return]

  async def _run_command_async(self, command: str, **params: Any) -> Dict[str, Any]:
    """
    Execute a JSON-RPC command on the modem (async)

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Command result dictionary

    Raises:
        AlcatelAPIError: If command fails
        AlcatelConnectionError: If connection fails
        AlcatelTimeoutError: If request times out
        AuthenticationError: If authentication fails
    """
    # Create async client if not exists
    if self._async_client is None:
      retry_transport = httpx.AsyncHTTPTransport(retries=3)
      self._async_client = httpx.AsyncClient(
        timeout=self._timeout,
        transport=retry_transport,
        headers=self._default_headers.copy(),
      )

    # Handle empty params - use None instead of empty dict
    params_value = params if params else None

    message = {
      "jsonrpc": "2.0",
      "method": command,
      "id": "1",
      "params": params_value,
    }

    api_url = f"{self._url}/jrd/webapi"

    try:
      resp = await self._async_client.post(api_url, json=message)
    except httpx.TimeoutException as e:
      raise AlcatelTimeoutError(f"Request timed out after {self._timeout} seconds: {str(e)}")
    except httpx.ConnectError as e:
      raise AlcatelConnectionError(f"Failed to connect to modem at {self._url}: {str(e)}")
    except httpx.RequestError as e:
      raise AlcatelConnectionError(f"Request failed: {str(e)}")

    if resp.status_code != 200:
      # Check if this might be an unsupported modem (405/404 on /jrd/webapi endpoint)
      await self._check_unsupported_modem_async(resp)

      error_msg = format_http_error(resp.status_code, resp.text)
      raise AlcatelConnectionError(error_msg)

    # Handle JSON decode errors
    try:
      result = resp.json()
    except (ValueError, json.JSONDecodeError):
      raise AlcatelAPIError(f"Invalid response from modem (not JSON). HTTP {resp.status_code}: {resp.text[:200]}")

    if "error" in result:
      error = result["error"]
      error_code = error.get("code", "unknown")
      error_msg = error.get("message", "Unknown error")

      # Check if it's an authentication error
      if error_code == -32699 or "Authentication" in error_msg:
        raise AuthenticationError(f"Authentication failed: {error_msg}")

      # Map common error messages to specific exceptions
      error_msg_lower = error_msg.lower()
      if "system busy" in error_msg_lower or "busy" in error_msg_lower:
        raise AlcatelSystemBusyError(f"Modem system is busy: {error_msg}", error_code=error_code)
      if "sim" in error_msg_lower and ("missing" in error_msg_lower or "not" in error_msg_lower):
        raise AlcatelSimMissingError(f"SIM card issue: {error_msg}", error_code=error_code)
      if "not supported" in error_msg_lower or "unsupported" in error_msg_lower:
        raise AlcatelFeatureNotSupportedError(f"Feature not supported: {error_msg}", error_code=error_code)

      raise AlcatelAPIError(f"Command failed: {error_msg} (code: {error_code})", error_code=error_code)

    if "result" not in result:
      raise AlcatelAPIError(f"Unexpected response: {result}")

    return result["result"]  # type: ignore[no-any-return]

  def run(self, command: str, **params: Any) -> Dict[str, Any]:
    """
    Run a command (with automatic login if needed) - sync

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

  async def run_async(self, command: str, **params: Any) -> dict[str, Any]:
    """
    Run a command (with automatic login if needed) - async

    Args:
        command: Command name
        **params: Command parameters

    Returns:
        Command result
    """
    # Use fully async auth flow to avoid blocking
    if self._password and not await self._get_login_state_async():
      await self._login_async()

    return await self._run_command_async(command, **params)

  def logout(self) -> None:
    """Clear authentication token"""
    self._token_manager.clear_token()
    if "_TclRequestVerificationToken" in self._default_headers:
      del self._default_headers["_TclRequestVerificationToken"]
    if "_TclRequestVerificationToken" in self._client.headers:
      del self._client.headers["_TclRequestVerificationToken"]
    if self._async_client and "_TclRequestVerificationToken" in self._async_client.headers:
      del self._async_client.headers["_TclRequestVerificationToken"]

  def close(self) -> None:
    """Close HTTP clients"""
    self._client.close()
    if self._async_client:
      # Note: async client should be closed with await, but this is for sync cleanup
      pass

  async def aclose(self) -> None:
    """Close async HTTP client"""
    if self._async_client:
      await self._async_client.aclose()

  def __enter__(self) -> "AlcatelClient":
    """Context manager entry (sync)"""
    return self

  def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
    """Context manager exit (sync)"""
    self.close()

  async def __aenter__(self) -> "AlcatelClient":
    """Context manager entry (async)"""
    return self

  async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
    """Context manager exit (async)"""
    await self.aclose()
