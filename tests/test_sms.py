"""
Tests for SMS module
"""

import pytest

from alcatel_modem_api import AlcatelAPIError
from alcatel_modem_api.sms import SMSManager


def test_get_sms_list_empty(mock_api):
  """Test getting SMS list when empty"""
  api, m = mock_api
  sms = SMSManager(api)

  m.post("http://192.168.1.1/jrd/webapi", json={"result": []})

  result = sms.get_sms_list()
  assert isinstance(result, list)
  assert len(result) == 0


def test_get_sms_list_with_messages(mock_api):
  """Test getting SMS list with messages"""
  api, m = mock_api
  sms = SMSManager(api)

  m.post(
    "http://192.168.1.1/jrd/webapi",
    json={
      "result": [
        {"SMSId": 1, "PhoneNumber": "+1234567890", "SMSContent": "Test message"},
      ],
    },
  )

  result = sms.get_sms_list()
  assert isinstance(result, list)
  assert len(result) == 1
  assert result[0]["SMSId"] == 1


def test_get_sms_list_dict_with_list(mock_api):
  """Test getting SMS list when API returns dict with list inside"""
  api, m = mock_api
  sms = SMSManager(api)

  m.post(
    "http://192.168.1.1/jrd/webapi",
    json={"result": {"SMSList": [{"SMSId": 1, "PhoneNumber": "+1234567890"}]}},
  )

  result = sms.get_sms_list()
  assert isinstance(result, list)
  assert len(result) == 1


def test_get_sms_list_error_response(mock_api):
  """Test that error responses raise AlcatelAPIError"""
  api, m = mock_api
  sms = SMSManager(api)

  # First call returns error in result (edge case)
  m.post(
    "http://192.168.1.1/jrd/webapi",
    json={"result": {"error": {"message": "SMS retrieval failed"}}},
  )

  with pytest.raises(AlcatelAPIError):
    sms.get_sms_list()


def test_get_sms_list_dict_without_list(mock_api):
  """Test getting SMS list when API returns dict without list key"""
  api, m = mock_api
  sms = SMSManager(api)

  m.post("http://192.168.1.1/jrd/webapi", json={"result": {"Status": "ok"}})

  result = sms.get_sms_list()
  # Should return empty list, not wrap dict in list
  assert isinstance(result, list)
  assert len(result) == 0


def test_get_sms_list_with_contact_number(mock_api):
  """Test getting SMS list filtered by contact number"""
  api, m = mock_api
  sms = SMSManager(api)

  m.post("http://192.168.1.1/jrd/webapi", json={"result": []})

  result = sms.get_sms_list(contact_number="+1234567890")
  assert isinstance(result, list)

  # Check that ContactNum parameter was passed
  request = m.request_history[0]
  request_body = request.json()
  assert request_body["params"]["ContactNum"] == "+1234567890"
