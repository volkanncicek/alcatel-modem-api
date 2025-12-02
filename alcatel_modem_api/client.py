"""
Core HTTP client for Alcatel Modem API
Handles HTTP requests, authentication, retry logic, and token management
"""

import json
import os
import platform
import stat
from pathlib import Path
from typing import Any, Literal, Protocol, Union

import httpx

from .auth import AuthStrategy, EncryptedAuthStrategy, detect_auth_strategy
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
from .utils.diagnostics import detect_modem_brand
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
    connection_limits: Union[httpx.Limits, None] = None,
    encrypt_admin_key: Union[str, None] = None,
    client: Union[httpx.Client, None] = None,
    async_client: Union[httpx.AsyncClient, None] = None,
  ):
    """
    Initialize Alcatel Modem API client

    Args:
        url: Base URL of the modem (default: http://192.168.1.1)
        password: Admin password (optional, required for protected commands)
        session_file: Path to session token file (optional)
        timeout: Request timeout in seconds (default: 10)
        token_storage: Custom token storage implementation (optional)
        connection_limits: Custom httpx.Limits for connection pooling (optional)
        encrypt_admin_key: Custom encryption key for admin credentials (optional)
        client: Custom httpx.Client instance (optional, allows control of proxies, certs, etc.)
        async_client: Custom httpx.AsyncClient instance (optional, allows control of proxies, certs, etc.)
    """
    self._url = url.rstrip("/")
    self._password = password
    self._timeout = timeout

    # Store encryption key override if provided
    self._encrypt_admin_key = encrypt_admin_key

    # Authentication strategy (will be detected on first login)
    self._auth_strategy: Union[AuthStrategy, None] = None

    # Token storage: use custom implementation if provided, otherwise default to file-based storage
    if token_storage is not None:
      self._token_manager = token_storage
    else:
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

    # Use provided clients or create new ones
    if client is not None:
      # Use provided client, but update headers
      self._client = client
      # Merge default headers with existing client headers
      self._client.headers.update(self._default_headers)
      self._client_owned = False  # Don't close client we didn't create
    else:
      # Create httpx client with retry logic and connection pool limits
      # Limits prevent resource exhaustion when creating many client instances
      self._limits = connection_limits or httpx.Limits(max_keepalive_connections=5, max_connections=10)
      retry_transport = httpx.HTTPTransport(retries=3)
      self._client = httpx.Client(
        timeout=timeout,
        transport=retry_transport,
        headers=self._default_headers.copy(),
        limits=self._limits,
      )
      self._client_owned = True  # We own this client, should close it

    # Async client will be created on first use or use provided one
    self._async_client: Union[httpx.AsyncClient, None] = None
    if async_client is not None:
      self._async_client = async_client
      # Merge default headers with existing client headers
      self._async_client.headers.update(self._default_headers)
      self._async_client_owned = False  # Don't close client we didn't create
    else:
      self._async_client = None
      self._async_client_owned = True  # We own async client when we create it

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
      except Exception:  # nosec B110
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
      except Exception:  # nosec B110
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
      # Detect or use cached auth strategy
      if self._auth_strategy is None:
        self._auth_strategy = detect_auth_strategy(self)

      # Type narrowing: mypy now knows _auth_strategy is not None
      assert self._auth_strategy is not None

      # Try encrypted strategy first (most common for newer models)
      # If it fails, fall back to legacy strategy
      try:
        result = self._auth_strategy.login(self, "admin", self._password, self._encrypt_admin_key)
      except Exception:
        # Fallback to legacy strategy if encrypted fails
        from .auth.strategies import LegacyAuthStrategy

        legacy_strategy = LegacyAuthStrategy()
        try:
          result = legacy_strategy.login(self, "admin", self._password, self._encrypt_admin_key)
          self._auth_strategy = legacy_strategy  # Cache successful strategy
        except Exception:
          # If legacy also fails, try encrypted one more time with default key
          encrypted_strategy = EncryptedAuthStrategy()
          result = encrypted_strategy.login(self, "admin", self._password, self._encrypt_admin_key)
          self._auth_strategy = encrypted_strategy  # Cache successful strategy

      # Process token according to strategy
      encrypted_token = self._auth_strategy.process_token(result)

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
      # Detect or use cached auth strategy
      if self._auth_strategy is None:
        self._auth_strategy = detect_auth_strategy(self)

      # Type narrowing: mypy now knows _auth_strategy is not None
      assert self._auth_strategy is not None

      # Try encrypted strategy first (most common for newer models)
      # If it fails, fall back to legacy strategy
      try:
        result = await self._auth_strategy.login_async(self, "admin", self._password, self._encrypt_admin_key)
      except Exception:
        # Fallback to legacy strategy if encrypted fails
        from .auth.strategies import LegacyAuthStrategy

        legacy_strategy = LegacyAuthStrategy()
        try:
          result = await legacy_strategy.login_async(self, "admin", self._password, self._encrypt_admin_key)
          self._auth_strategy = legacy_strategy  # Cache successful strategy
        except Exception:
          # If legacy also fails, try encrypted one more time with default key
          encrypted_strategy = EncryptedAuthStrategy()
          result = await encrypted_strategy.login_async(self, "admin", self._password, self._encrypt_admin_key)
          self._auth_strategy = encrypted_strategy  # Cache successful strategy

      # Process token according to strategy
      encrypted_token = self._auth_strategy.process_token(result)

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

  async def _run_command_async(self, command: str, **params: Any) -> dict[str, Any]:
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
    # Create async client if not exists and not provided
    if self._async_client is None:
      # Limits prevent resource exhaustion when creating many client instances
      # Use the same limits as sync client (if we created sync client)
      limits = getattr(self, "_limits", httpx.Limits(max_keepalive_connections=5, max_connections=10))
      retry_transport = httpx.AsyncHTTPTransport(retries=3)
      self._async_client = httpx.AsyncClient(
        timeout=self._timeout,
        transport=retry_transport,
        headers=self._default_headers.copy(),
        limits=limits,
      )
      self._async_client_owned = True

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

  def run(self, command: str, **params: Any) -> dict[str, Any]:
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
    """Close HTTP clients (only if we own them)"""
    if getattr(self, "_client_owned", True):
      self._client.close()
    # Note: async client should be closed with await aclose()

  async def aclose(self) -> None:
    """Close async HTTP client (only if we own it)"""
    if self._async_client and getattr(self, "_async_client_owned", True):
      await self._async_client.aclose()

  def __enter__(self) -> "AlcatelClient":
    """Context manager entry (sync)"""
    return self

  def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
    """Context manager exit (sync)"""
    self.close()
    return False  # Explicitly propagate exceptions

  async def __aenter__(self) -> "AlcatelClient":
    """Context manager entry (async)"""
    return self

  async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
    """Context manager exit (async)"""
    await self.aclose()
