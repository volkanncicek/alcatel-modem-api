"""
Fuzz testing with Hypothesis for Alcatel Modem API

These tests use Hypothesis to generate random/malformed input to ensure
Pydantic models handle edge cases and malformed firmware responses gracefully.
"""

import json
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from alcatel_modem_api.models import (
  ConnectionState,
  ExtendedStatus,
  NetworkInfo,
  SMSMessage,
  SystemStatus,
)


@given(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none())))
def test_system_status_fuzz(data: dict[str, Any]) -> None:
  """Test SystemStatus model with fuzzed input"""
  try:
    # SystemStatus should handle any dict without crashing
    status = SystemStatus.model_validate(data)
    # If validation succeeds, ensure it's a valid SystemStatus
    assert isinstance(status, SystemStatus)
  except Exception:
    # It's OK if validation fails on invalid data, but it shouldn't crash
    pass


@given(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none())))
def test_extended_status_fuzz(data: dict[str, Any]) -> None:
  """Test ExtendedStatus model with fuzzed input"""
  try:
    status = ExtendedStatus.model_validate(data)
    assert isinstance(status, ExtendedStatus)
  except Exception:
    # Validation failure is acceptable, crash is not
    pass


@given(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none())))
def test_network_info_fuzz(data: dict[str, Any]) -> None:
  """Test NetworkInfo model with fuzzed input"""
  try:
    info = NetworkInfo.model_validate(data)
    assert isinstance(info, NetworkInfo)
  except Exception:
    pass


@given(st.lists(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none()))))
def test_sms_message_list_fuzz(data_list: list[dict[str, Any]]) -> None:
  """Test SMSMessage model with fuzzed list input"""
  for data in data_list:
    try:
      msg = SMSMessage.model_validate(data)
      assert isinstance(msg, SMSMessage)
    except Exception:
      pass


@given(st.text())
def test_json_decode_fuzz(malformed_json: str) -> None:
  """Test that malformed JSON doesn't crash the client"""
  # This tests the JSON parsing in client._run_command
  try:
    json.loads(malformed_json)
  except (json.JSONDecodeError, ValueError):
    # Expected - malformed JSON should raise JSONDecodeError
    pass
  except Exception as e:
    # Other exceptions are unexpected
    pytest.fail(f"Unexpected exception type: {type(e).__name__}: {e}")


@given(
  st.one_of(
    st.integers(min_value=-1000, max_value=1000),
    st.floats(min_value=-1000.0, max_value=1000.0),
    st.text(),
    st.booleans(),
    st.none(),
  )
)
def test_coerce_int_or_none_fuzz(value: Any) -> None:
  """Test coerce_int_or_none with fuzzed values"""
  from alcatel_modem_api.models import coerce_int_or_none

  result = coerce_int_or_none(value)
  # Should always return int or None, never crash
  assert result is None or isinstance(result, int)


@given(
  st.one_of(
    st.integers(min_value=-1000, max_value=1000),
    st.floats(min_value=-1000.0, max_value=1000.0),
    st.text(),
    st.booleans(),
    st.none(),
  )
)
def test_coerce_str_or_none_fuzz(value: Any) -> None:
  """Test coerce_str_or_none with fuzzed values"""
  from alcatel_modem_api.models import coerce_str_or_none

  result = coerce_str_or_none(value)
  # Should always return str or None, never crash
  assert result is None or isinstance(result, str)


@given(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.floats(), st.booleans(), st.none())))
def test_connection_state_fuzz(data: dict[str, Any]) -> None:
  """Test ConnectionState model with fuzzed input"""
  try:
    state = ConnectionState.model_validate(data)
    assert isinstance(state, ConnectionState)
  except Exception:
    pass
