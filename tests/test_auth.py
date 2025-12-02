"""
Tests for authentication module
"""

import os
import tempfile
from pathlib import Path

from alcatel_modem_api import AuthenticationError, FileTokenStorage, MemoryTokenStorage
from alcatel_modem_api.utils.encryption import encrypt_admin, encrypt_token


def test_encrypt_admin():
  """Test admin credential encryption"""
  result = encrypt_admin("admin")
  assert isinstance(result, str)
  assert len(result) > 0
  # Should produce different output for different inputs
  assert encrypt_admin("admin") == encrypt_admin("admin")  # Deterministic
  assert encrypt_admin("admin") != encrypt_admin("password")


def test_encrypt_token(valid_aes_key, valid_aes_iv):
  """Test token encryption"""
  token = "test_token"

  encrypted = encrypt_token(token, valid_aes_key, valid_aes_iv)
  assert isinstance(encrypted, str)
  assert len(encrypted) > 0
  # Should be base64 encoded
  assert all(c.isalnum() or c in "+/=" for c in encrypted)


def test_memory_token_storage():
  """Test in-memory token storage"""
  storage = MemoryTokenStorage()

  assert storage.get_token() == ""
  storage.save_token("test_token")
  assert storage.get_token() == "test_token"
  storage.clear_token()
  assert storage.get_token() == ""


def test_file_token_storage():
  """Test file-based token storage"""
  with tempfile.TemporaryDirectory() as tmpdir:
    session_file = os.path.join(tmpdir, "test_session")

    storage = FileTokenStorage(session_file)
    assert storage.get_token() == ""

    storage.save_token("test_token")
    assert storage.get_token() == "test_token"

    # Create new storage instance to test persistence
    storage2 = FileTokenStorage(session_file)
    assert storage2.get_token() == "test_token"

    storage.clear_token()
    assert storage.get_token() == ""
    assert not os.path.exists(session_file)


def test_file_token_storage_default_path():
  """Test file token storage uses default path"""
  storage = FileTokenStorage()
  expected_path = str(Path.home() / ".alcatel_modem_session")
  assert storage.session_file == expected_path


def test_file_token_storage_custom_path():
  """Test file token storage with custom path"""
  with tempfile.TemporaryDirectory() as tmpdir:
    custom_path = os.path.join(tmpdir, "custom_session")
    storage = FileTokenStorage(custom_path)
    assert storage.session_file == custom_path


def test_token_storage_protocol():
  """Test that storage implementations have required methods"""
  memory_storage = MemoryTokenStorage()
  # Check that it has required methods
  assert hasattr(memory_storage, "save_token")
  assert hasattr(memory_storage, "get_token")
  assert hasattr(memory_storage, "clear_token")

  with tempfile.TemporaryDirectory() as tmpdir:
    file_storage = FileTokenStorage(os.path.join(tmpdir, "test"))
    # Check that it has required methods
    assert hasattr(file_storage, "save_token")
    assert hasattr(file_storage, "get_token")
    assert hasattr(file_storage, "clear_token")


def test_authentication_error():
  """Test AuthenticationError exception"""
  error = AuthenticationError("Test error")
  assert str(error) == "Test error"
  assert isinstance(error, Exception)
