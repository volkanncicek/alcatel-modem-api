"""
Pytest configuration and shared fixtures
"""

import os
import tempfile

import pytest
import requests_mock


@pytest.fixture
def temp_session_file():
  """Create a temporary session file for testing"""
  with tempfile.TemporaryDirectory() as tmpdir:
    session_file = os.path.join(tmpdir, "test_session")
    yield session_file


@pytest.fixture
def mock_api(temp_session_file):
  """Create a mocked AlcatelModemAPI instance with temporary session file"""
  from alcatel_modem_api import AlcatelModemAPI

  with requests_mock.Mocker() as m:
    api = AlcatelModemAPI(session_file=temp_session_file)
    yield api, m


@pytest.fixture
def mock_api_with_password(temp_session_file):
  """Create a mocked AlcatelModemAPI instance with password and temporary session file"""
  from alcatel_modem_api import AlcatelModemAPI

  with requests_mock.Mocker() as m:
    api = AlcatelModemAPI(password="secret", session_file=temp_session_file)
    yield api, m


@pytest.fixture
def valid_aes_key():
  """Valid AES key (16 bytes) for encryption tests"""
  return "1234567890123456"


@pytest.fixture
def valid_aes_iv():
  """Valid AES IV (16 bytes) for encryption tests"""
  return "1234567890123456"
