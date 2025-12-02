"""
Network endpoint namespace
Handles network information, settings, and connection management
"""

from typing import Any

from ..client import AlcatelClient
from ..models import ConnectionState, NetworkInfo


class NetworkEndpoint:
  """Network operations namespace"""

  def __init__(self, client: AlcatelClient):
    """
    Initialize Network endpoint

    Args:
        client: AlcatelClient instance
    """
    self._client = client

  def get_info(self) -> NetworkInfo:
    """
    Get network information (requires login)

    Returns:
        NetworkInfo model with network details
    """
    result = self._client.run("GetNetworkInfo")
    return NetworkInfo.from_dict(result)

  async def get_info_async(self) -> NetworkInfo:
    """
    Get network information (async, requires login)

    Returns:
        NetworkInfo model with network details
    """
    result = await self._client.run_async("GetNetworkInfo")
    return NetworkInfo.from_dict(result)

  def get_settings(self) -> dict[str, Any]:
    """
    Get network settings (requires login)

    Returns:
        Network settings dictionary
    """
    return self._client.run("GetNetworkSettings")

  async def get_settings_async(self) -> dict[str, Any]:
    """
    Get network settings (async, requires login)

    Returns:
        Network settings dictionary
    """
    return await self._client.run_async("GetNetworkSettings")

  def set_settings(self, network_mode: int, net_selection_mode: int = 0) -> dict[str, Any]:
    """
    Set network settings (requires login)

    Args:
        network_mode: Network mode (0=Auto, 1=2G, 2=3G, 3=4G, 255=Auto)
        net_selection_mode: Network selection mode (0=Auto, 1=Manual)

    Returns:
        Settings result
    """
    return self._client.run(
      "SetNetworkSettings",
      NetworkMode=network_mode,
      NetselectionMode=net_selection_mode,
    )

  async def set_settings_async(self, network_mode: int, net_selection_mode: int = 0) -> dict[str, Any]:
    """
    Set network settings (async, requires login)

    Args:
        network_mode: Network mode (0=Auto, 1=2G, 2=3G, 3=4G, 255=Auto)
        net_selection_mode: Network selection mode (0=Auto, 1=Manual)

    Returns:
        Settings result
    """
    return await self._client.run_async(
      "SetNetworkSettings",
      NetworkMode=network_mode,
      NetselectionMode=net_selection_mode,
    )

  def get_connection_state(self) -> ConnectionState:
    """
    Get connection state (requires login)

    Returns:
        ConnectionState model with connection details
    """
    result = self._client.run("GetConnectionState")
    return ConnectionState.from_dict(result)

  async def get_connection_state_async(self) -> ConnectionState:
    """
    Get connection state (async, requires login)

    Returns:
        ConnectionState model with connection details
    """
    result = await self._client.run_async("GetConnectionState")
    return ConnectionState.from_dict(result)

  def connect(self) -> dict[str, Any]:
    """
    Connect to network (requires login)

    Returns:
        Connection result
    """
    return self._client.run("Connect")

  async def connect_async(self) -> dict[str, Any]:
    """
    Connect to network (async, requires login)

    Returns:
        Connection result
    """
    return await self._client.run_async("Connect")

  def disconnect(self) -> dict[str, Any]:
    """
    Disconnect from network (requires login)

    Returns:
        Disconnection result
    """
    return self._client.run("DisConnect")

  async def disconnect_async(self) -> dict[str, Any]:
    """
    Disconnect from network (async, requires login)

    Returns:
        Disconnection result
    """
    return await self._client.run_async("DisConnect")

  def get_register_state(self) -> dict[str, Any]:
    """
    Get network register state (requires login)

    Returns:
        Register state dictionary
    """
    return self._client.run("GetNetworkRegisterState")

  async def get_register_state_async(self) -> dict[str, Any]:
    """
    Get network register state (async, requires login)

    Returns:
        Register state dictionary
    """
    return await self._client.run_async("GetNetworkRegisterState")

  def get_profile_list(self) -> dict[str, Any]:
    """
    Get profile list (requires login)

    Returns:
        Profile list dictionary
    """
    return self._client.run("GetProfileList")

  async def get_profile_list_async(self) -> dict[str, Any]:
    """
    Get profile list (async, requires login)

    Returns:
        Profile list dictionary
    """
    return await self._client.run_async("GetProfileList")

  def get_current_profile(self) -> dict[str, Any]:
    """
    Get current profile (requires login)

    Returns:
        Current profile dictionary
    """
    return self._client.run("getCurrentProfile")

  async def get_current_profile_async(self) -> dict[str, Any]:
    """
    Get current profile (async, requires login)

    Returns:
        Current profile dictionary
    """
    return await self._client.run_async("getCurrentProfile")

  def get_wan_settings(self) -> dict[str, Any]:
    """
    Get WAN settings (requires login)

    Returns:
        WAN settings dictionary
    """
    return self._client.run("GetWanSettings")

  async def get_wan_settings_async(self) -> dict[str, Any]:
    """
    Get WAN settings (async, requires login)

    Returns:
        WAN settings dictionary
    """
    return await self._client.run_async("GetWanSettings")

  def get_wan_is_conn_inter(self) -> dict[str, Any]:
    """
    Get WAN connection interface (requires login)

    Returns:
        WAN connection interface dictionary
    """
    return self._client.run("GetWanIsConnInter")

  async def get_wan_is_conn_inter_async(self) -> dict[str, Any]:
    """
    Get WAN connection interface (async, requires login)

    Returns:
        WAN connection interface dictionary
    """
    return await self._client.run_async("GetWanIsConnInter")

  def get_wan_current_mac_addr(self) -> dict[str, Any]:
    """
    Get WAN current MAC address (requires login)

    Returns:
        MAC address dictionary
    """
    return self._client.run("GetWanCurrentMacAddr")

  async def get_wan_current_mac_addr_async(self) -> dict[str, Any]:
    """
    Get WAN current MAC address (async, requires login)

    Returns:
        MAC address dictionary
    """
    return await self._client.run_async("GetWanCurrentMacAddr")
