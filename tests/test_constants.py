"""
Tests for constants module
"""

from alcatel_modem_api.constants import (
  CONNECTION_STATUSES,
  NETWORK_TYPES,
  SMS_SEND_STATUS,
  get_connection_status,
  get_network_type,
  get_sms_send_status,
)


def test_get_network_type_known_values():
  """Test get_network_type with known network type values"""
  assert get_network_type(0) == "No Service"
  assert get_network_type(1) == "2G"
  assert get_network_type(2) == "2G"
  assert get_network_type(3) == "3G"
  assert get_network_type(4) == "3G"
  assert get_network_type(5) == "3G"
  assert get_network_type(6) == "3G+"
  assert get_network_type(7) == "3G+"
  assert get_network_type(8) == "4G"
  assert get_network_type(9) == "4G+"
  assert get_network_type(10) == "3G"
  assert get_network_type(11) == "2G"
  assert get_network_type(16) == "5G"


def test_get_network_type_unknown_value():
  """Test get_network_type with unknown network type value"""
  result = get_network_type(99)
  assert "Unknown" in result
  assert "99" in result


def test_get_connection_status_known_values():
  """Test get_connection_status with known connection status values"""
  assert get_connection_status(0) == "Disconnected"
  assert get_connection_status(1) == "Connecting"
  assert get_connection_status(2) == "Connected"
  assert get_connection_status(3) == "Disconnecting"


def test_get_connection_status_unknown_value():
  """Test get_connection_status with unknown connection status value"""
  result = get_connection_status(99)
  assert "Unknown" in result
  assert "99" in result


def test_get_sms_send_status_known_values():
  """Test get_sms_send_status with known SMS send status values"""
  assert get_sms_send_status(0) == "None"
  assert get_sms_send_status(1) == "Sending"
  assert get_sms_send_status(2) == "Success"
  assert get_sms_send_status(3) == "Fail Sending"
  assert get_sms_send_status(4) == "Memory Full"
  assert get_sms_send_status(5) == "Failed"


def test_get_sms_send_status_unknown_value():
  """Test get_sms_send_status with unknown SMS send status value"""
  result = get_sms_send_status(99)
  assert "Unknown" in result
  assert "99" in result


def test_network_types_dict_completeness():
  """Test that NETWORK_TYPES dict contains expected mappings"""
  assert 0 in NETWORK_TYPES
  assert 8 in NETWORK_TYPES  # 4G
  assert 16 in NETWORK_TYPES  # 5G
  assert NETWORK_TYPES[8] == "4G"
  assert NETWORK_TYPES[16] == "5G"


def test_connection_statuses_dict_completeness():
  """Test that CONNECTION_STATUSES dict contains expected mappings"""
  assert 0 in CONNECTION_STATUSES
  assert 1 in CONNECTION_STATUSES
  assert 2 in CONNECTION_STATUSES
  assert 3 in CONNECTION_STATUSES
  assert CONNECTION_STATUSES[2] == "Connected"


def test_sms_send_status_dict_completeness():
  """Test that SMS_SEND_STATUS dict contains expected mappings"""
  assert 0 in SMS_SEND_STATUS
  assert 2 in SMS_SEND_STATUS  # Success
  assert 5 in SMS_SEND_STATUS  # Failed
  assert SMS_SEND_STATUS[2] == "Success"
  assert SMS_SEND_STATUS[5] == "Failed"

