"""
WLAN (WiFi) endpoint namespace
Handles WiFi settings and configuration
"""

from typing import Any

from ..client import AlcatelClient


class WLANEndpoint:
  """WiFi operations namespace"""

  def __init__(self, client: AlcatelClient):
    """
    Initialize WLAN endpoint

    Args:
        client: AlcatelClient instance
    """
    self._client = client

  def get_settings(self) -> dict[str, Any]:
    """
    Get WiFi settings (requires login)

    Returns:
        WiFi settings dictionary
    """
    return self._client.run("GetWlanSettings")

  async def get_settings_async(self) -> dict[str, Any]:
    """
    Get WiFi settings (async, requires login)

    Returns:
        WiFi settings dictionary
    """
    return await self._client.run_async("GetWlanSettings")

  def set_settings(self, **kwargs: Any) -> dict[str, Any]:
    """
    Set WiFi settings (requires login)

    Args:
        **kwargs: WiFi settings (ApStatus, Ssid, SecurityMode, WpaKey, etc.)

    Example:
        client.wlan.set_settings(ApStatus=1, Ssid="MyNetwork", SecurityMode=3, WpaKey="password123")

    Returns:
        Settings result
    """
    return self._client.run("SetWlanSettings", **kwargs)

  async def set_settings_async(self, **kwargs: Any) -> dict[str, Any]:
    """
    Set WiFi settings (async, requires login)

    Args:
        **kwargs: WiFi settings (ApStatus, Ssid, SecurityMode, WpaKey, etc.)

    Returns:
        Settings result
    """
    return await self._client.run_async("SetWlanSettings", **kwargs)

  def get_state(self) -> dict[str, Any]:
    """
    Get WiFi state (requires login)

    Returns:
        WiFi state dictionary
    """
    return self._client.run("GetWlanState")

  async def get_state_async(self) -> dict[str, Any]:
    """
    Get WiFi state (async, requires login)

    Returns:
        WiFi state dictionary
    """
    return await self._client.run_async("GetWlanState")

  def get_statistics(self) -> dict[str, Any]:
    """
    Get WiFi statistics (requires login)

    Returns:
        WiFi statistics dictionary
    """
    return self._client.run("GetWlanStatistics")

  async def get_statistics_async(self) -> dict[str, Any]:
    """
    Get WiFi statistics (async, requires login)

    Returns:
        WiFi statistics dictionary
    """
    return await self._client.run_async("GetWlanStatistics")

  def get_support_mode(self) -> dict[str, Any]:
    """
    Get WiFi support mode (requires login)

    Returns:
        Support mode dictionary
    """
    return self._client.run("GetWlanSupportMode")

  async def get_support_mode_async(self) -> dict[str, Any]:
    """
    Get WiFi support mode (async, requires login)

    Returns:
        Support mode dictionary
    """
    return await self._client.run_async("GetWlanSupportMode")

  def get_wmm_switch(self) -> dict[str, Any]:
    """
    Get WMM switch (requires login)

    Returns:
        WMM switch dictionary
    """
    return self._client.run("GetWmmSwitch")

  async def get_wmm_switch_async(self) -> dict[str, Any]:
    """
    Get WMM switch (async, requires login)

    Returns:
        WMM switch dictionary
    """
    return await self._client.run_async("GetWmmSwitch")

  def get_wps_settings(self) -> dict[str, Any]:
    """
    Get WPS settings (requires login)

    Returns:
        WPS settings dictionary
    """
    return self._client.run("GetWPSSettings")

  async def get_wps_settings_async(self) -> dict[str, Any]:
    """
    Get WPS settings (async, requires login)

    Returns:
        WPS settings dictionary
    """
    return await self._client.run_async("GetWPSSettings")

  def get_wps_connection_state(self) -> dict[str, Any]:
    """
    Get WPS connection state (requires login)

    Returns:
        WPS connection state dictionary
    """
    return self._client.run("GetWPSConnectionState")

  async def get_wps_connection_state_async(self) -> dict[str, Any]:
    """
    Get WPS connection state (async, requires login)

    Returns:
        WPS connection state dictionary
    """
    return await self._client.run_async("GetWPSConnectionState")
