"""
Tests for AlcatelClient
"""

import os

import httpx
import pytest
import respx

from alcatel_modem_api import (
  AlcatelAPIError,
  AlcatelClient,
  AlcatelConnectionError,
  AlcatelTimeoutError,
  AuthenticationError,
  FileTokenStorage,
)


def test_optimistic_login_flow(mock_api_with_password, valid_aes_key, valid_aes_iv):
  """Test optimistic authentication: try command first, login on auth error"""
  client, m = mock_api_with_password

  # Track call count to handle recursion in _get_login_state()
  call_count = {"count": 0}
  login_attempted = {"done": False}

  def response_handler(request):
    call_count["count"] += 1
    import json

    # Access request body - use read() for httpx Request objects
    try:
      content = request.read() if hasattr(request, "read") else (request.content if hasattr(request, "content") else b"")
      data = json.loads(content) if content else {}
    except (AttributeError, json.JSONDecodeError):
      data = {}
    method = data.get("method", "")

    # First few GetLoginState calls fail (from _get_login_state recursion)
    if method == "GetLoginState" and not login_attempted["done"]:
      return httpx.Response(200, json={"error": {"code": -32699, "message": "Auth Failure"}})

    # Login attempts
    if method == "Login":
      params = data.get("params", {})
      # Unencrypted login fails
      if "admin" in str(params.get("UserName", "")):
        return httpx.Response(200, json={"error": {"code": -32699, "message": "Auth Failure"}})
      # Encrypted login succeeds
      login_attempted["done"] = True
      return httpx.Response(200, json={"result": {"token": "new_token", "param0": valid_aes_key, "param1": valid_aes_iv}})

    # After login, GetLoginState succeeds
    if method == "GetLoginState":
      return httpx.Response(200, json={"result": {"State": 1}})

    # GetSystemStatus succeeds
    if method == "GetSystemStatus":
      return httpx.Response(200, json={"result": {"NetworkName": "TestNet"}})

    # Default: auth error
    return httpx.Response(200, json={"error": {"code": -32699, "message": "Auth Failure"}})

  m.post("http://192.168.1.1/jrd/webapi").mock(side_effect=response_handler)

  result = client.run("GetSystemStatus")
  assert result["NetworkName"] == "TestNet"
  # Should have at least 4 calls: GetLoginState (fails), Login (unencrypted fails), Login (encrypted succeeds), GetLoginState (succeeds), GetSystemStatus (succeeds)
  assert len(respx.calls) >= 4


def test_json_rpc_id_format(mock_api):
  """Test that JSON-RPC request IDs are in correct format"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"result": {"status": "ok"}}))

  # Make a request
  client.run("GetSystemStatus")

  # Check that request ID exists and is a string
  import json

  call = respx.calls.last
  request_body = call.request.content
  request_json = json.loads(request_body)
  assert "id" in request_json
  assert isinstance(request_json["id"], str)


def test_token_storage_persistence(temp_session_file):
  """Test that token storage persists across API instances"""
  # Create first API instance and save token
  client1 = AlcatelClient(session_file=temp_session_file)
  client1._token_manager.save_token("test_token_123")

  # Create second API instance and verify token is restored
  client2 = AlcatelClient(session_file=temp_session_file)
  assert client2._token_manager.get_token() == "test_token_123"


def test_token_passed_per_request(temp_session_file, mock_api):
  """Test that token is passed per-request, not via session headers"""
  # Write token to file
  with open(temp_session_file, "w") as f:
    f.write("test_token")

  client, m = mock_api
  # Recreate client with the session file that has token
  client = AlcatelClient(session_file=temp_session_file)

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"result": {"status": "ok"}}))

  client.run("GetSystemStatus")

  # Check that token was passed in request headers
  call = respx.calls.last
  assert call.request.headers.get("_TclRequestVerificationToken") == "test_token"


def test_authentication_error_without_password(mock_api):
  """Test that AuthenticationError is raised when no password is available"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"error": {"code": -32699, "message": "Auth Failure"}}))

  with pytest.raises(AuthenticationError):
    client.run("GetSystemStatus")


def test_connection_error(mock_api):
  """Test connection error handling"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(side_effect=httpx.ConnectError("Connection failed"))

  with pytest.raises(AlcatelConnectionError):
    client.run("GetSystemStatus")


def test_timeout_error(mock_api):
  """Test timeout error handling"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(side_effect=httpx.TimeoutException("Request timed out"))

  with pytest.raises(AlcatelTimeoutError):
    client.run("GetSystemStatus")


def test_invalid_json_response(mock_api):
  """Test handling of invalid JSON responses"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, text="<html>Error</html>"))

  with pytest.raises(AlcatelAPIError):
    client.run("GetSystemStatus")


def test_api_error_response(mock_api):
  """Test handling of API error responses"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"error": {"code": 123, "message": "Command failed"}}))

  with pytest.raises(AlcatelAPIError) as exc_info:
    client.run("GetSystemStatus")

  assert "Command failed" in str(exc_info.value)


def test_custom_token_manager(temp_session_file):
  """Test that custom session file path can be used"""
  client = AlcatelClient(session_file=temp_session_file)

  # Type check: _token_manager should be FileTokenStorage when session_file is provided
  assert isinstance(client._token_manager, FileTokenStorage)
  assert client._token_manager.session_file == temp_session_file


def test_logout(temp_session_file):
  """Test logout functionality"""
  # Write token to file
  with open(temp_session_file, "w") as f:
    f.write("test_token")
  client = AlcatelClient(session_file=temp_session_file)

  assert client._token_manager.get_token() == "test_token"
  client.logout()
  assert client._token_manager.get_token() == ""
  assert not os.path.exists(temp_session_file)
