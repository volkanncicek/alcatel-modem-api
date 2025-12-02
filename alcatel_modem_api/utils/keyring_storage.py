"""
Keyring-based token storage with file fallback
Uses system keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)
Falls back to file storage if keyring is not available
"""

import logging
from pathlib import Path
from typing import Protocol, Union

# Keyring is now a core dependency
import keyring

logger = logging.getLogger(__name__)

KEYRING_AVAILABLE = True


class TokenStorageProtocol(Protocol):
  """Protocol for token storage implementations"""

  def save_token(self, token: str) -> None:
    """Save token"""
    ...

  def get_token(self) -> str:
    """Get stored token"""
    ...

  def clear_token(self) -> None:
    """Clear stored token"""
    ...


class KeyringTokenStorage:
  """
  Token storage using system keyring with file fallback

  Uses keyring service name: "alcatel-modem-api"
  Uses keyring username: "session-token"
  """

  def __init__(self, session_file: Union[str, None] = None, use_keyring: bool = True):
    """
    Initialize keyring-based token storage

    Args:
        session_file: Path to fallback session file (default: ~/.alcatel_modem_session)
        use_keyring: Whether to attempt using keyring (default: True)
    """
    if session_file is None:
      home = Path.home()
      session_file = str(home / ".alcatel_modem_session")

    self.session_file = session_file
    self.use_keyring = use_keyring
    self.service_name = "alcatel-modem-api"
    self.username = "session-token"

    if self.use_keyring:
      logger.debug("Using system keyring for token storage")
    else:
      logger.debug("Keyring disabled, using file storage")

  def save_token(self, token: str) -> None:
    """Save token to keyring (with file fallback)"""
    if self.use_keyring:
      try:
        keyring.set_password(self.service_name, self.username, token)
        logger.debug("Token saved to system keyring")
        return
      except Exception as e:
        logger.warning(f"Failed to save token to keyring, falling back to file: {e}")
        # Fall through to file storage

    # Fallback to file storage
    try:
      with open(self.session_file, "w") as f:
        f.write(token)
      logger.debug(f"Token saved to file: {self.session_file}")
    except Exception as e:
      logger.warning(f"Could not save token to file: {e}")

  def get_token(self) -> str:
    """Get token from keyring (with file fallback)"""
    if self.use_keyring:
      try:
        token = keyring.get_password(self.service_name, self.username)
        if token:
          logger.debug("Token retrieved from system keyring")
          return token
      except Exception as e:
        logger.debug(f"Failed to get token from keyring, trying file: {e}")

    # Fallback to file storage
    try:
      if Path(self.session_file).exists():
        with open(self.session_file) as f:
          token = f.read().strip()
          if token:
            logger.debug(f"Token retrieved from file: {self.session_file}")
            return token
    except Exception as e:
      logger.debug(f"Could not restore token from file: {e}")

    return ""

  def clear_token(self) -> None:
    """Clear token from both keyring and file"""
    if self.use_keyring:
      try:
        keyring.delete_password(self.service_name, self.username)
        logger.debug("Token cleared from system keyring")
      except Exception as e:
        logger.debug(f"Could not clear token from keyring (may not exist): {e}")

    # Also clear file
    try:
      if Path(self.session_file).exists():
        Path(self.session_file).unlink()
        logger.debug(f"Token file removed: {self.session_file}")
    except Exception as e:
      logger.debug(f"Could not remove token file: {e}")
