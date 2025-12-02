"""
Test to ensure sync/async API parity

This test ensures that all sync methods have corresponding async methods
with matching signatures (excluding the async/await keywords).
"""

import inspect
from typing import Any

from alcatel_modem_api import AlcatelClient


def get_public_methods(obj: Any, exclude: set[str] | None = None) -> set[str]:
  """Get all public methods from an object"""
  exclude = exclude or set()
  methods = set()
  for name in dir(obj):
    if name.startswith("_") or name in exclude:
      continue
    attr = getattr(obj, name)
    if callable(attr) and not inspect.isclass(attr):
      methods.add(name)
  return methods


def test_client_sync_async_parity() -> None:
  """Test that AlcatelClient has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")

  # Get all public methods
  sync_methods = get_public_methods(client, exclude={"close", "aclose", "__enter__", "__exit__", "__aenter__", "__aexit__"})

  # Check that run has run_async
  assert "run" in sync_methods, "run() method should exist"
  assert "run_async" in sync_methods, "run_async() method should exist"

  # Verify signatures match (excluding async/await)
  run_sig = inspect.signature(client.run)
  run_async_sig = inspect.signature(client.run_async)

  # Parameters should match (excluding 'self')
  run_params = list(run_sig.parameters.keys())[1:]  # Skip 'self'
  run_async_params = list(run_async_sig.parameters.keys())[1:]  # Skip 'self'

  assert run_params == run_async_params, f"run() and run_async() should have matching parameters. Sync: {run_params}, Async: {run_async_params}"


def test_system_endpoint_parity() -> None:
  """Test that SystemEndpoint has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")
  endpoint = client.system

  sync_methods = get_public_methods(endpoint)
  async_methods = {name for name in sync_methods if name.endswith("_async")}

  # Check that all async methods have sync counterparts
  for async_method in async_methods:
    base_method = async_method.replace("_async", "")
    assert base_method in sync_methods, f"{async_method} should have sync counterpart {base_method}"

  # Check key methods exist
  assert "get_status" in sync_methods, "get_status() should exist"
  assert "get_status_async" in async_methods, "get_status_async() should exist"


def test_network_endpoint_parity() -> None:
  """Test that NetworkEndpoint has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")
  endpoint = client.network

  sync_methods = get_public_methods(endpoint)
  async_methods = {name for name in sync_methods if name.endswith("_async")}

  # Check that all async methods have sync counterparts
  for async_method in async_methods:
    base_method = async_method.replace("_async", "")
    assert base_method in sync_methods, f"{async_method} should have sync counterpart {base_method}"

  # Check key methods exist
  assert "get_info" in sync_methods, "get_info() should exist"
  assert "get_info_async" in async_methods, "get_info_async() should exist"


def test_sms_endpoint_parity() -> None:
  """Test that SMSEndpoint has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")
  endpoint = client.sms

  sync_methods = get_public_methods(endpoint)
  async_methods = {name for name in sync_methods if name.endswith("_async")}

  # Check that all async methods have sync counterparts
  for async_method in async_methods:
    base_method = async_method.replace("_async", "")
    assert base_method in sync_methods, f"{async_method} should have sync counterpart {base_method}"

  # Check key methods exist
  assert "send" in sync_methods, "send() should exist"
  assert "send_async" in async_methods, "send_async() should exist"
  assert "list" in sync_methods, "list() should exist"
  assert "list_async" in async_methods, "list_async() should exist"


def test_wlan_endpoint_parity() -> None:
  """Test that WLANEndpoint has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")
  endpoint = client.wlan

  sync_methods = get_public_methods(endpoint)
  async_methods = {name for name in sync_methods if name.endswith("_async")}

  # Check that all async methods have sync counterparts
  for async_method in async_methods:
    base_method = async_method.replace("_async", "")
    assert base_method in sync_methods, f"{async_method} should have sync counterpart {base_method}"

  # Check key methods exist
  assert "get_settings" in sync_methods, "get_settings() should exist"
  assert "get_settings_async" in async_methods, "get_settings_async() should exist"


def test_device_endpoint_parity() -> None:
  """Test that DeviceEndpoint has matching sync/async methods"""
  client = AlcatelClient("http://192.168.1.1")
  endpoint = client.device

  sync_methods = get_public_methods(endpoint)
  async_methods = {name for name in sync_methods if name.endswith("_async")}

  # Check that all async methods have sync counterparts
  for async_method in async_methods:
    base_method = async_method.replace("_async", "")
    assert base_method in sync_methods, f"{async_method} should have sync counterpart {base_method}"

  # Check key methods exist
  assert "get_connected_list" in sync_methods, "get_connected_list() should exist"
  assert "get_connected_list_async" in async_methods, "get_connected_list_async() should exist"
