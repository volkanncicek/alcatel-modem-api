"""
System endpoint namespace
Handles system status, SIM status, polling methods, and USSD operations
"""

import asyncio
import time
from typing import Any

from ..client import AlcatelClient
from ..constants import get_connection_status, get_network_type
from ..models import ExtendedStatus, SystemStatus


class SystemEndpoint:
  """System operations namespace"""

  def __init__(self, client: AlcatelClient):
    """
    Initialize System endpoint

    Args:
        client: AlcatelClient instance
    """
    self._client = client

  def get_status(self) -> SystemStatus:
    """
    Get system status (no login required)

    Returns:
        SystemStatus model with system information
    """
    result = self._client.run("GetSystemStatus")
    return SystemStatus.from_dict(result)

  async def get_status_async(self) -> SystemStatus:
    """
    Get system status (async, no login required)

    Returns:
        SystemStatus model with system information
    """
    result = await self._client.run_async("GetSystemStatus")
    return SystemStatus.from_dict(result)

  def get_info(self) -> dict[str, Any]:
    """
    Get system information (no login required)

    Returns:
        System information dictionary
    """
    return self._client.run("GetSystemInfo")

  async def get_info_async(self) -> dict[str, Any]:
    """
    Get system information (async, no login required)

    Returns:
        System information dictionary
    """
    return await self._client.run_async("GetSystemInfo")

  def get_sim_status(self) -> dict[str, Any]:
    """
    Get SIM card status (no login required)

    Returns:
        SIM status dictionary
    """
    return self._client.run("GetSimStatus")

  async def get_sim_status_async(self) -> dict[str, Any]:
    """
    Get SIM card status (async, no login required)

    Returns:
        SIM status dictionary
    """
    return await self._client.run_async("GetSimStatus")

  def get_login_state(self) -> dict[str, Any]:
    """
    Get login state (no login required)

    Returns:
        Login state dictionary
    """
    return self._client.run("GetLoginState")

  async def get_login_state_async(self) -> dict[str, Any]:
    """
    Get login state (async, no login required)

    Returns:
        Login state dictionary
    """
    return await self._client.run_async("GetLoginState")

  def poll_basic_status(self) -> dict[str, Any]:
    """
    Poll basic status (does NOT require login)
    Returns: imei, iccid, device, connection_status, network_type, network_name, strength

    Returns:
        Dictionary with basic status information
    """
    system_info = self.get_info()
    system_status = self.get_status()

    return {
      "imei": system_info.get("IMEI", ""),
      "iccid": system_info.get("ICCID", ""),
      "device": system_info.get("DeviceName", ""),
      "connection_status": get_connection_status(system_status.connection_status),
      "network_type": get_network_type(system_status.network_type),
      "network_name": system_status.network_name,
      "strength": system_status.signal_strength,
    }

  async def poll_basic_status_async(self) -> dict[str, Any]:
    """
    Poll basic status (async, does NOT require login)

    Returns:
        Dictionary with basic status information
    """
    system_info = await self.get_info_async()
    system_status = await self.get_status_async()

    return {
      "imei": system_info.get("IMEI", ""),
      "iccid": system_info.get("ICCID", ""),
      "device": system_info.get("DeviceName", ""),
      "connection_status": get_connection_status(system_status.connection_status),
      "network_type": get_network_type(system_status.network_type),
      "network_name": system_status.network_name,
      "strength": system_status.signal_strength,
    }

  def poll_extended_status(self) -> ExtendedStatus:
    """
    Poll extended status (REQUIRES login)
    Returns: All basic status plus bytes_in, bytes_out, rates, IP addresses, RSSI, RSRP, etc.

    Returns:
        ExtendedStatus model with extended information
    """
    # Import here to avoid circular import
    from ..endpoints.network import NetworkEndpoint

    system_info = self.get_info()
    network_endpoint = NetworkEndpoint(self._client)
    network_info = network_endpoint.get_info()
    connection_state = network_endpoint.get_connection_state()

    return ExtendedStatus(
      imei=system_info.get("IMEI", ""),
      iccid=system_info.get("ICCID", ""),
      device=system_info.get("DeviceName", ""),
      connection_status=connection_state.connection_status,
      bytes_in=connection_state.bytes_in,
      bytes_out=connection_state.bytes_out,
      bytes_in_rate=connection_state.bytes_in_rate,
      bytes_out_rate=connection_state.bytes_out_rate,
      ipv4_addr=connection_state.ipv4_addr,
      ipv6_addr=connection_state.ipv6_addr,
      network_name=network_info.network_name,
      network_type=network_info.network_type,
      strength=network_info.signal_strength,
      rssi=network_info.rssi,
      rsrp=network_info.rsrp,
      sinr=network_info.sinr,
      rsrq=network_info.rsrq,
    )

  async def poll_extended_status_async(self) -> ExtendedStatus:
    """
    Poll extended status (async, REQUIRES login)

    Returns:
        ExtendedStatus model with extended information
    """
    # Import here to avoid circular import
    from ..endpoints.network import NetworkEndpoint

    system_info = await self.get_info_async()
    network_endpoint = NetworkEndpoint(self._client)
    network_info = await network_endpoint.get_info_async()
    connection_state = await network_endpoint.get_connection_state_async()

    return ExtendedStatus(
      imei=system_info.get("IMEI", ""),
      iccid=system_info.get("ICCID", ""),
      device=system_info.get("DeviceName", ""),
      connection_status=connection_state.connection_status,
      bytes_in=connection_state.bytes_in,
      bytes_out=connection_state.bytes_out,
      bytes_in_rate=connection_state.bytes_in_rate,
      bytes_out_rate=connection_state.bytes_out_rate,
      ipv4_addr=connection_state.ipv4_addr,
      ipv6_addr=connection_state.ipv6_addr,
      network_name=network_info.network_name,
      network_type=network_info.network_type,
      strength=network_info.signal_strength,
      rssi=network_info.rssi,
      rsrp=network_info.rsrp,
      sinr=network_info.sinr,
      rsrq=network_info.rsrq,
    )

  def send_ussd(self, ussd_content: str, ussd_type: int = 1) -> dict[str, Any]:
    """
    Send USSD code (requires login)

    Args:
        ussd_content: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)

    Returns:
        USSD send result
    """
    return self._client.run("SendUSSD", UssdContent=ussd_content, UssdType=ussd_type)

  async def send_ussd_async(self, ussd_content: str, ussd_type: int = 1) -> dict[str, Any]:
    """
    Send USSD code (async, requires login)

    Args:
        ussd_content: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)

    Returns:
        USSD send result
    """
    return await self._client.run_async("SendUSSD", UssdContent=ussd_content, UssdType=ussd_type)

  def get_ussd_result(self) -> dict[str, Any]:
    """
    Get USSD send result (requires login)

    Returns:
        USSD result dictionary
    """
    return self._client.run("GetUSSDSendResult")

  async def get_ussd_result_async(self) -> dict[str, Any]:
    """
    Get USSD send result (async, requires login)

    Returns:
        USSD result dictionary
    """
    return await self._client.run_async("GetUSSDSendResult")

  def end_ussd(self) -> dict[str, Any]:
    """
    End USSD session (requires login)

    Returns:
        End USSD result
    """
    return self._client.run("SetUSSDEnd")

  async def end_ussd_async(self) -> dict[str, Any]:
    """
    End USSD session (async, requires login)

    Returns:
        End USSD result
    """
    return await self._client.run_async("SetUSSDEnd")

  def send_ussd_code(self, code: str, ussd_type: int = 1, wait_seconds: int = 5) -> dict[str, Any]:
    """
    Send USSD code and wait for result (requires login)

    Args:
        code: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)
        wait_seconds: Seconds to wait before getting result (default: 5)

    Returns:
        Dict with UssdType, SendState, UssdContent
    """
    self.send_ussd(code, ussd_type)
    time.sleep(wait_seconds)
    return self.get_ussd_result()

  async def send_ussd_code_async(self, code: str, ussd_type: int = 1, wait_seconds: int = 5) -> dict[str, Any]:
    """
    Send USSD code and wait for result (async, requires login)

    Args:
        code: USSD code (e.g., "*222#")
        ussd_type: USSD type (1=Request, 2=Response)
        wait_seconds: Seconds to wait before getting result (default: 5)

    Returns:
        Dict with UssdType, SendState, UssdContent
    """
    await self.send_ussd_async(code, ussd_type)
    await asyncio.sleep(wait_seconds)
    return await self.get_ussd_result_async()
