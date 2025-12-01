"""
Tests for AlcatelModemAPI
"""

import os

import pytest
import requests

from alcatel_modem_api import (
  AlcatelAPIError,
  AlcatelConnectionError,
  AlcatelModemAPI,
  AlcatelTimeoutError,
  AuthenticationError,
)


def test_optimistic_login_flow(mock_api_with_password, valid_aes_key, valid_aes_iv):
  """Test optimistic authentication: try command first, login on auth error"""
  api, m = mock_api_with_password

  # 1. Initial call fails with Auth error
  # 2. Login succeeds
  # 3. Retry succeeds
  m.post(
    "http://192.168.1.1/jrd/webapi",
    [
      {"json": {"error": {"code": -32699, "message": "Auth Failure"}}, "status_code": 200},
      {"json": {"result": {"token": "new_token", "param0": valid_aes_key, "param1": valid_aes_iv}}},  # Login response
      {"json": {"result": {"NetworkName": "TestNet"}}},  # Retry success
    ],
  )

  result = api.run("GetSystemStatus")
  assert result["NetworkName"] == "TestNet"
  assert m.call_count == 3


def test_json_rpc_id_format(mock_api):
  """Test that JSON-RPC request IDs are in correct format"""
  api, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi", json={"result": {"status": "ok"}})

  # Make a request
  api.run("GetSystemStatus")

  # Check that request ID exists and is a string
  request = m.request_history[0]
  request_body = request.json()
  assert "id" in request_body
  assert isinstance(request_body["id"], str)


def test_token_storage_persistence(temp_session_file):
  """Test that token storage persists across API instances"""
  # Create first API instance and save token
  api1 = AlcatelModemAPI(session_file=temp_session_file)
  api1._token_manager.save_token("test_token_123")

  # Create second API instance and verify token is restored
  api2 = AlcatelModemAPI(session_file=temp_session_file)
  assert api2._token_manager.get_token() == "test_token_123"


def test_token_passed_per_request(temp_session_file, mock_api):
  """Test that token is passed per-request, not via session headers"""
  # Write token to file
  with open(temp_session_file, "w") as f:
    f.write("test_token")

  api, m = mock_api
  # Recreate API with the session file that has token
  api = AlcatelModemAPI(session_file=temp_session_file)

  m.post("http://192.168.1.1/jrd/webapi", json={"result": {"status": "ok"}})

  api.run("GetSystemStatus")

  # Check that token was passed in request headers
  request = m.request_history[0]
  assert request.headers.get("_TclRequestVerificationToken") == "test_token"


def test_authentication_error_without_password(mock_api):
  """Test that AuthenticationError is raised when no password is available"""
  api, m = mock_api

  m.post(
    "http://192.168.1.1/jrd/webapi",
    json={"error": {"code": -32699, "message": "Auth Failure"}},
  )

  with pytest.raises(AuthenticationError):
    api.run("GetSystemStatus")


def test_connection_error(mock_api):
  """Test connection error handling"""
  api, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi", exc=requests.exceptions.ConnectionError("Connection failed"))

  with pytest.raises(AlcatelConnectionError):
    api.run("GetSystemStatus")


def test_timeout_error(mock_api):
  """Test timeout error handling"""
  api, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi", exc=requests.exceptions.Timeout("Request timed out"))

  with pytest.raises(AlcatelTimeoutError):
    api.run("GetSystemStatus")


def test_invalid_json_response(mock_api):
  """Test handling of invalid JSON responses"""
  api, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi", text="<html>Error</html>", status_code=200)

  with pytest.raises(AlcatelAPIError):
    api.run("GetSystemStatus")


def test_api_error_response(mock_api):
  """Test handling of API error responses"""
  api, m = mock_api

  m.post(
    "http://192.168.1.1/jrd/webapi",
    json={"error": {"code": 123, "message": "Command failed"}},
  )

  with pytest.raises(AlcatelAPIError) as exc_info:
    api.run("GetSystemStatus")

  assert "Command failed" in str(exc_info.value)


def test_custom_token_manager(temp_session_file):
  """Test that custom session file path can be used"""
  api = AlcatelModemAPI(session_file=temp_session_file)

  assert api._token_manager.session_file == temp_session_file


def test_logout(temp_session_file):
  """Test logout functionality"""
  # Write token to file
  with open(temp_session_file, "w") as f:
    f.write("test_token")
  api = AlcatelModemAPI(session_file=temp_session_file)

  assert api._token_manager.get_token() == "test_token"
  api.logout()
  assert api._token_manager.get_token() == ""
  assert not os.path.exists(temp_session_file)
