"""
Device endpoint namespace
Handles device management, connected devices, blocking, and LAN settings
"""

from typing import Any

from ..client import AlcatelClient


class DeviceEndpoint:
  """Device management operations namespace"""

  def __init__(self, client: AlcatelClient):
    """
    Initialize Device endpoint

    Args:
        client: AlcatelClient instance
    """
    self._client = client

  def get_connected_list(self) -> dict[str, Any]:
    """
    Get list of connected devices (requires login)

    Returns:
        Connected devices dictionary
    """
    return self._client.run("GetConnectedDeviceList")

  async def get_connected_list_async(self) -> dict[str, Any]:
    """
    Get list of connected devices (async, requires login)

    Returns:
        Connected devices dictionary
    """
    return await self._client.run_async("GetConnectedDeviceList")

  def get_block_list(self) -> dict[str, Any]:
    """
    Get list of blocked devices (requires login)

    Returns:
        Blocked devices dictionary
    """
    return self._client.run("GetBlockDeviceList")

  async def get_block_list_async(self) -> dict[str, Any]:
    """
    Get list of blocked devices (async, requires login)

    Returns:
        Blocked devices dictionary
    """
    return await self._client.run_async("GetBlockDeviceList")

  def block(self, device_name: str, mac_address: str) -> dict[str, Any]:
    """
    Block a connected device (requires login)

    Args:
        device_name: Name of the device to block
        mac_address: MAC address of the device to block

    Returns:
        Block result
    """
    return self._client.run("SetConnectedDeviceBlock", DeviceName=device_name, MacAddress=mac_address)

  async def block_async(self, device_name: str, mac_address: str) -> dict[str, Any]:
    """
    Block a connected device (async, requires login)

    Args:
        device_name: Name of the device to block
        mac_address: MAC address of the device to block

    Returns:
        Block result
    """
    return await self._client.run_async("SetConnectedDeviceBlock", DeviceName=device_name, MacAddress=mac_address)

  def unblock(self, device_name: str, mac_address: str) -> dict[str, Any]:
    """
    Unblock a device (requires login)

    Args:
        device_name: Name of the device to unblock
        mac_address: MAC address of the device to unblock

    Returns:
        Unblock result
    """
    return self._client.run("SetDeviceUnlock", DeviceName=device_name, MacAddress=mac_address)

  async def unblock_async(self, device_name: str, mac_address: str) -> dict[str, Any]:
    """
    Unblock a device (async, requires login)

    Args:
        device_name: Name of the device to unblock
        mac_address: MAC address of the device to unblock

    Returns:
        Unblock result
    """
    return await self._client.run_async("SetDeviceUnlock", DeviceName=device_name, MacAddress=mac_address)

  def get_lan_settings(self) -> dict[str, Any]:
    """
    Get LAN settings (requires login)

    Returns:
        LAN settings dictionary
    """
    return self._client.run("GetLanSettings")

  async def get_lan_settings_async(self) -> dict[str, Any]:
    """
    Get LAN settings (async, requires login)

    Returns:
        LAN settings dictionary
    """
    return await self._client.run_async("GetLanSettings")

  def get_lan_statistics(self) -> dict[str, Any]:
    """
    Get LAN statistics (requires login)

    Returns:
        LAN statistics dictionary
    """
    return self._client.run("GetLanStatistics")

  async def get_lan_statistics_async(self) -> dict[str, Any]:
    """
    Get LAN statistics (async, requires login)

    Returns:
        LAN statistics dictionary
    """
    return await self._client.run_async("GetLanStatistics")

  def get_lan_port_info(self) -> dict[str, Any]:
    """
    Get LAN port information (requires login)

    Returns:
        LAN port info dictionary
    """
    return self._client.run("GetLanPortInfo")

  async def get_lan_port_info_async(self) -> dict[str, Any]:
    """
    Get LAN port information (async, requires login)

    Returns:
        LAN port info dictionary
    """
    return await self._client.run_async("GetLanPortInfo")

  def get_device_default_right(self) -> dict[str, Any]:
    """
    Get device default rights (requires login)

    Returns:
        Device default rights dictionary
    """
    return self._client.run("GetDeviceDefaultRight")

  async def get_device_default_right_async(self) -> dict[str, Any]:
    """
    Get device default rights (async, requires login)

    Returns:
        Device default rights dictionary
    """
    return await self._client.run_async("GetDeviceDefaultRight")
