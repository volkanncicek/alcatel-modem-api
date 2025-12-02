"""
Authentication strategy implementations for different Alcatel modem models

This module implements the Strategy Pattern to handle different authentication
methods used by various Alcatel modem models. Each model may require a different
authentication flow, and this pattern allows easy extension for new models.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..utils.encryption import encrypt_admin, encrypt_token


class AuthStrategy(ABC):
  """
  Abstract base class for authentication strategies

  Each Alcatel modem model may use a different authentication method.
  This abstract class defines the interface that all authentication strategies must implement.
  """

  @abstractmethod
  def login(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """
    Perform login using the strategy's authentication method (sync)

    Args:
        client: AlcatelClient instance (for making API calls)
        username: Username (typically "admin")
        password: Admin password
        encrypt_key: Optional custom encryption key

    Returns:
        Login response dictionary containing token and optional encryption parameters

    Raises:
        AuthenticationError: If login fails
    """
    pass

  async def login_async(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """
    Perform login using the strategy's authentication method (async)

    Default implementation calls sync login. Override if async-specific behavior is needed.

    Args:
        client: AlcatelClient instance (for making API calls)
        username: Username (typically "admin")
        password: Admin password
        encrypt_key: Optional custom encryption key

    Returns:
        Login response dictionary containing token and optional encryption parameters

    Raises:
        AuthenticationError: If login fails
    """
    # Default: use sync version (most strategies don't need async-specific logic)
    return self.login(client, username, password, encrypt_key)

  @abstractmethod
  def process_token(self, login_result: dict[str, Any]) -> str:
    """
    Process the token from login result according to strategy

    Args:
        login_result: Result dictionary from login() method

    Returns:
        Processed token string ready for use in API requests
    """
    pass


class LegacyAuthStrategy(AuthStrategy):
  """
  Legacy authentication strategy for MW40V1 and similar models

  Uses plain text username/password without encryption.
  Token is used directly without additional encryption.
  """

  def login(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with plain text credentials (sync)"""
    return client._run_command("Login", UserName=username, Password=password)

  async def login_async(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with plain text credentials (async)"""
    return await client._run_command_async("Login", UserName=username, Password=password)

  def process_token(self, login_result: dict[str, Any]) -> str:
    """Use token directly without encryption"""
    return str(login_result["token"])


class TokenAuthStrategy(AuthStrategy):
  """
  Token-based authentication strategy for MW40/MW41 models

  Similar to legacy but may have slight differences in token handling.
  Currently uses the same approach as LegacyAuthStrategy but separated
  for future model-specific handling.
  """

  def login(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with plain text credentials (sync)"""
    return client._run_command("Login", UserName=username, Password=password)

  async def login_async(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with plain text credentials (async)"""
    return await client._run_command_async("Login", UserName=username, Password=password)

  def process_token(self, login_result: dict[str, Any]) -> str:
    """Use token directly without encryption"""
    return str(login_result["token"])


class EncryptedAuthStrategy(AuthStrategy):
  """
  Encrypted authentication strategy for HH72/HH40V and similar models

  Uses encrypted username/password and encrypted token.
  Requires param0 and param1 from login response for token encryption.
  """

  def login(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with encrypted credentials (sync)"""
    # Use custom encryption key if provided, otherwise use default
    if encrypt_key:
      # Create a custom encrypt function with the provided key
      def custom_encrypt_admin(value: str) -> str:
        encoded = bytearray()
        for index, char in enumerate(value):
          value_code = ord(char)
          key_code = ord(encrypt_key[index % len(encrypt_key)])
          encoded.append((240 & key_code) | ((15 & value_code) ^ (15 & key_code)))
          encoded.append((240 & key_code) | ((value_code >> 4) ^ (15 & key_code)))
        return encoded.decode()

      encrypt_func = custom_encrypt_admin
    else:
      encrypt_func = encrypt_admin

    return client._run_command("Login", UserName=encrypt_func(username), Password=encrypt_func(password))

  async def login_async(self, client: Any, username: str, password: str, encrypt_key: Optional[str] = None) -> dict[str, Any]:
    """Login with encrypted credentials (async)"""
    # Use custom encryption key if provided, otherwise use default
    if encrypt_key:
      # Create a custom encrypt function with the provided key
      def custom_encrypt_admin(value: str) -> str:
        encoded = bytearray()
        for index, char in enumerate(value):
          value_code = ord(char)
          key_code = ord(encrypt_key[index % len(encrypt_key)])
          encoded.append((240 & key_code) | ((15 & value_code) ^ (15 & key_code)))
          encoded.append((240 & key_code) | ((value_code >> 4) ^ (15 & key_code)))
        return encoded.decode()

      encrypt_func = custom_encrypt_admin
    else:
      encrypt_func = encrypt_admin

    return await client._run_command_async("Login", UserName=encrypt_func(username), Password=encrypt_func(password))

  def process_token(self, login_result: dict[str, Any]) -> str:
    """Encrypt token using param0 and param1 from login response"""
    token = login_result["token"]
    if "param0" in login_result and "param1" in login_result:
      return encrypt_token(token, login_result["param0"], login_result["param1"])
    # Fallback: use token directly if param0/param1 not present
    return str(token)


def detect_auth_strategy(client: Any, model: Optional[str] = None) -> AuthStrategy:
  """
  Detect and return the appropriate authentication strategy for the modem

  Args:
      client: AlcatelClient instance
      model: Optional model name (if known)

  Returns:
      Appropriate AuthStrategy instance

  Note:
      Currently tries encrypted first, then falls back to legacy.
      Future versions may use model detection to select strategy upfront.
  """
  # If model is known, select strategy directly
  if model:
    model_lower = model.lower()
    if "mw40v1" in model_lower:
      return LegacyAuthStrategy()
    elif "mw40" in model_lower or "mw41" in model_lower:
      return TokenAuthStrategy()
    elif "hh72" in model_lower or "hh40v" in model_lower or "hh70" in model_lower:
      return EncryptedAuthStrategy()

  # Default: try encrypted first, fallback to legacy
  # This matches the current behavior in AlcatelClient
  return EncryptedAuthStrategy()
