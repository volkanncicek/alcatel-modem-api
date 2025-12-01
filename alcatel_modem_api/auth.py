"""
Authentication module for Alcatel modems
Handles encryption and token management
"""

import os
import platform
import stat
from base64 import b64encode
from pathlib import Path
from typing import Protocol

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Encryption key for admin credentials (Alcatel's custom algorithm)
ENCRYPT_ADMIN_KEY = "e5dl12XYVggihggafXWf0f2YSf2Xngd1"


class AuthenticationError(Exception):
  """Raised when authentication fails"""

  pass


def encrypt_admin(value: str) -> str:
  """
  Encrypt admin credentials using Alcatel's custom algorithm

  Args:
      value: String to encrypt (username or password)

  Returns:
      Encrypted string
  """
  encoded = bytearray()
  for index, char in enumerate(value):
    value_code = ord(char)
    key_code = ord(ENCRYPT_ADMIN_KEY[index % len(ENCRYPT_ADMIN_KEY)])
    encoded.append((240 & key_code) | ((15 & value_code) ^ (15 & key_code)))
    encoded.append((240 & key_code) | ((value_code >> 4) ^ (15 & key_code)))

  return encoded.decode()


def encrypt_token(token: str, param0: str, param1: str) -> str:
  """
  Encrypt authentication token using AES/CBC/PKCS7Padding

  Args:
      token: Token from login response
      param0: Key parameter from login response
      param1: IV parameter from login response

  Returns:
      Base64 encoded encrypted token
  """
  # First, encode token using custom algorithm
  encoded_token = encrypt_admin(token).encode()

  # Then, cipher using AES/CBC/PKCS7Padding
  key = param0.encode()
  iv = param1.encode()

  cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
  encryptor = cipher.encryptor()

  # Do padding
  padder = padding.PKCS7(128).padder()
  padded_data = padder.update(encoded_token) + padder.finalize()

  # Encrypt padded data
  ciphertext = encryptor.update(padded_data) + encryptor.finalize()

  # Base64 encode
  encoded = b64encode(ciphertext).decode()

  return encoded


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

  def __init__(self, session_file: str | None = None):
    """
    Initialize file-based token storage

    Args:
        session_file: Path to session file (default: ~/.alcatel_modem_session)
    """
    if session_file is None:
      home = Path.home()
      session_file = str(home / ".alcatel_modem_session")

    self.session_file = session_file
    self._token = None
    self._restore_token()

  def save_token(self, token: str) -> None:
    """Save token to file"""
    self._token = token
    try:
      with open(self.session_file, "w") as f:
        f.write(token)
      # Set file permissions to 600 (read/write for owner only)
      # On Windows, os.chmod has limited functionality but is safe to call
      # It will only affect the read-only flag, which is acceptable for this use case
      try:
        if platform.system() != "Windows":
          os.chmod(self.session_file, stat.S_IRUSR | stat.S_IWUSR)
        else:
          # On Windows, we can at least remove write permissions from others
          # by setting the file to read-only for others (though this is limited)
          # For stricter security on Windows, users should use MemoryTokenStorage
          # or implement custom storage with pywin32
          os.chmod(self.session_file, stat.S_IREAD | stat.S_IWRITE)
      except (OSError, AttributeError):
        # Silently fail if chmod doesn't work (e.g., on some filesystems)
        pass
    except Exception:
      # Silently fail if we can't save token
      pass

  def _restore_token(self) -> None:
    """Restore token from file"""
    try:
      if os.path.exists(self.session_file):
        with open(self.session_file) as f:
          self._token = f.read().strip()
    except Exception:
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
    except Exception:
      pass


class MemoryTokenStorage:
  """In-memory token storage implementation (useful for web apps, testing)"""

  def __init__(self):
    """Initialize in-memory token storage"""
    self._token: str | None = None

  def save_token(self, token: str) -> None:
    """Save token to memory"""
    self._token = token

  def get_token(self) -> str:
    """Get current token from memory"""
    return self._token if self._token else ""

  def clear_token(self) -> None:
    """Clear stored token"""
    self._token = None
