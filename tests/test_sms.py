"""
Tests for SMS module
"""

import json

import httpx
import pytest
import respx

from alcatel_modem_api import AlcatelAPIError


def test_get_sms_list_empty(mock_api):
  """Test getting SMS list when empty"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"result": []}))

  result = client.sms.list()
  assert isinstance(result, list)
  assert len(result) == 0


def test_get_sms_list_with_messages(mock_api):
  """Test getting SMS list with messages"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(
    return_value=httpx.Response(
      200,
      json={
        "result": [
          {"SMSId": 1, "PhoneNumber": "+1234567890", "SMSContent": "Test message"},
        ],
      },
    ),
  )

  result = client.sms.list()
  assert isinstance(result, list)
  assert len(result) == 1
  # SMSMessage is now a Pydantic model
  assert result[0].sms_id == 1


def test_get_sms_list_dict_with_list(mock_api):
  """Test getting SMS list when API returns dict with list inside"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(
    return_value=httpx.Response(200, json={"result": {"SMSList": [{"SMSId": 1, "PhoneNumber": "+1234567890"}]}}),
  )

  result = client.sms.list()
  assert isinstance(result, list)
  assert len(result) == 1


def test_get_sms_list_error_response(mock_api):
  """Test that error responses raise AlcatelAPIError"""
  client, m = mock_api

  # First call returns error in result (edge case)
  m.post("http://192.168.1.1/jrd/webapi").mock(
    return_value=httpx.Response(200, json={"result": {"error": {"message": "SMS retrieval failed"}}}),
  )

  with pytest.raises(AlcatelAPIError):
    client.sms.list()


def test_get_sms_list_dict_without_list(mock_api):
  """Test getting SMS list when API returns dict without list key"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"result": {"Status": "ok"}}))

  result = client.sms.list()
  # Should return empty list, not wrap dict in list
  assert isinstance(result, list)
  assert len(result) == 0


def test_get_sms_list_with_contact_number(mock_api):
  """Test getting SMS list filtered by contact number"""
  client, m = mock_api

  m.post("http://192.168.1.1/jrd/webapi").mock(return_value=httpx.Response(200, json={"result": []}))

  result = client.sms.list(contact_number="+1234567890")
  assert isinstance(result, list)

  # Check that ContactNum parameter was passed
  call = respx.calls.last
  request_body = call.request.content
  request_json = json.loads(request_body)
  assert request_json["params"]["ContactNum"] == "+1234567890"
