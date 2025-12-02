"""
Pytest configuration and shared fixtures
"""

import os
import tempfile

import pytest
import respx

from alcatel_modem_api import AlcatelClient


@pytest.fixture
def temp_session_file():
  """Create a temporary session file for testing"""
  with tempfile.TemporaryDirectory() as tmpdir:
    session_file = os.path.join(tmpdir, "test_session")
    yield session_file


@pytest.fixture
def mock_api(temp_session_file):
  """Create a mocked AlcatelClient instance with temporary session file"""
  with respx.mock:
    client = AlcatelClient(session_file=temp_session_file)
    yield client, respx


@pytest.fixture
def mock_api_with_password(temp_session_file):
  """Create a mocked AlcatelClient instance with password and temporary session file"""
  with respx.mock:
    client = AlcatelClient(password="secret", session_file=temp_session_file)
    yield client, respx


@pytest.fixture
def valid_aes_key():
  """Valid AES key (16 bytes) for encryption tests"""
  return "1234567890123456"


@pytest.fixture
def valid_aes_iv():
  """Valid AES IV (16 bytes) for encryption tests"""
  return "1234567890123456"
