"""
Tests for typed data models
"""

from alcatel_modem_api.models import ConnectionState, ExtendedStatus, NetworkInfo, SMSMessage, SystemStatus


def test_system_status_from_dict():
  """Test SystemStatus creation from dict"""
  data = {
    "ConnectionStatus": 2,
    "SignalStrength": 75,
    "NetworkName": "Test Network",
    "NetworkType": 8,
    "IMEI": "123456789012345",
    "ICCID": "987654321098765",
    "DeviceName": "Test Device",
  }

  status = SystemStatus.from_dict(data)
  assert status.connection_status == 2
  assert status.signal_strength == 75
  assert status.network_name == "Test Network"
  assert status.network_type == 8
  assert status.imei == "123456789012345"
  assert status.iccid == "987654321098765"
  assert status.device == "Test Device"


def test_network_info_from_dict():
  """Test NetworkInfo creation from dict"""
  data = {
    "NetworkName": "Test Network",
    "NetworkType": 8,
    "SignalStrength": 75,
    "RSSI": -70,
    "RSRP": -100,
    "SINR": 20,
    "RSRQ": -10,
  }

  info = NetworkInfo.from_dict(data)
  assert info.network_name == "Test Network"
  assert info.network_type == 8
  assert info.signal_strength == 75
  assert info.rssi == -70
  assert info.rsrp == -100
  assert info.sinr == 20
  assert info.rsrq == -10


def test_connection_state_from_dict():
  """Test ConnectionState creation from dict"""
  data = {
    "ConnectionStatus": 2,
    "DlBytes": 1000000,
    "UlBytes": 500000,
    "DlRate": 1000,
    "UlRate": 500,
    "IPv4Adrress": "192.168.1.1",
    "IPv6Adrress": "2001:db8::1",
  }

  state = ConnectionState.from_dict(data)
  assert state.connection_status == 2
  assert state.bytes_in == 1000000
  assert state.bytes_out == 500000
  assert state.bytes_in_rate == 1000
  assert state.bytes_out_rate == 500
  assert state.ipv4_addr == "192.168.1.1"
  assert state.ipv6_addr == "2001:db8::1"


def test_extended_status_from_dict():
  """Test ExtendedStatus creation from dict"""
  data = {
    "imei": "123456789012345",
    "iccid": "987654321098765",
    "device": "Test Device",
    "connection_status": 2,
    "bytes_in": 1000000,
    "bytes_out": 500000,
    "bytes_in_rate": 1000,
    "bytes_out_rate": 500,
    "ipv4_addr": "192.168.1.1",
    "ipv6_addr": "2001:db8::1",
    "network_name": "Test Network",
    "network_type": 8,
    "strength": 75,
    "rssi": -70,
    "rsrp": -100,
    "sinr": 20,
    "rsrq": -10,
  }

  status = ExtendedStatus.from_dict(data)
  assert status.imei == "123456789012345"
  assert status.connection_status == 2
  assert status.bytes_in == 1000000
  assert status.network_name == "Test Network"


def test_sms_message_from_dict():
  """Test SMSMessage creation from dict"""
  data = {
    "SMSId": 1,
    "PhoneNumber": "+1234567890",
    "SMSContent": "Test message",
    "SMSTime": "2024-01-01 12:00:00",
    "Status": 2,
    "Read": True,
  }

  sms = SMSMessage.from_dict(data)
  assert sms.sms_id == 1
  assert sms.phone_number == "+1234567890"
  assert sms.content == "Test message"
  assert sms.timestamp == "2024-01-01 12:00:00"
  assert sms.status == 2
  assert sms.read is True


def test_sms_message_alternative_keys():
  """Test SMSMessage with alternative key names"""
  data = {
    "Id": 1,
    "Phone": "+1234567890",
    "Content": "Test message",
    "Time": "2024-01-01 12:00:00",
    "IsRead": False,
  }

  sms = SMSMessage.from_dict(data)
  assert sms.sms_id == 1
  assert sms.phone_number == "+1234567890"
  assert sms.content == "Test message"
  assert sms.read is False
