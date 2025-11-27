"""
Constants for Alcatel Modem API
Network types, connection statuses, etc.
"""

# Network Types mapping
NETWORK_TYPES = {
  0: "No Service",
  1: "2G",
  2: "2G",
  3: "3G",
  4: "3G",
  5: "3G",
  6: "3G+",
  7: "3G+",
  8: "4G",
  9: "4G+",
  10: "3G",
  11: "2G",
  16: "5G",
}

# Connection Statuses mapping
CONNECTION_STATUSES = {
  0: "Disconnected",
  1: "Connecting",
  2: "Connected",
  3: "Disconnecting",
}

# SMS Send Status codes
SMS_SEND_STATUS = {
  0: "None",
  1: "Sending",
  2: "Success",
  3: "Fail Sending",
  4: "Memory Full",
  5: "Failed",
}

# Public verbs (no authentication required)
PUBLIC_VERBS = [
  "GetCurrentLanguage",
  "GetLoginState",
  "GetQuickSetup",
  "GetSMSStorageState",
  "GetSimStatus",
  "GetSystemInfo",
  "GetSystemStatus",
]

# Restricted verbs (authentication required)
RESTRICTED_VERBS = [
  "GetAutoValidatePinState",
  "GetBlockDeviceList",
  "GetClientConfiguration",
  "GetConnectedDeviceList",
  "GetConnectionSettings",
  "GetConnectionState",
  "GetCurrentData",
  "GetCurrentTime",
  "GetDdnsSettings",
  "GetDeviceDefaultRight",
  "GetDeviceUpgradeState",
  "GetExtendTimes",
  "GetLanPortInfo",
  "GetLanSettings",
  "GetLanStatistics",
  "GetLogcfg",
  "GetMacFilterSettings",
  "GetNetworkInfo",
  "GetNetworkSettings",
  "GetParentalSettings",
  "GetPasswordChangeFlag",
  "GetPingTraceroute",
  "GetPortTriggering",
  "GetProfileList",
  "GetSIPAccountSettings",
  "GetSIPServerSettings",
  "GetSMSContactList",
  "GetSMSSettings",
  "GetSystemSettings",
  "GetTransferProtocol",
  "GetUpnpSettings",
  "GetUsageRecord",
  "GetUsageSettings",
  "GetVpnClient",
  "GetVpnClientStatus",
  "GetWPSConnectionState",
  "GetWPSSettings",
  "GetWanCurrentMacAddr",
  "GetWanIsConnInter",
  "GetWanSettings",
  "GetWlanSettings",
  "GetWlanState",
  "GetWlanStatistics",
  "GetWlanSupportMode",
  "GetWmmSwitch",
  # Additional commands from HH72 repo
  "GetCallLogCountInfo",
  "GetCallLogList",
  "GetVoicemail",
  "GetQosSettings",
  "GetUSBLocalUpdateList",
  "GetDLNASettings",
  "GetFtpSettings",
  "GetSambaSettings",
  "GetVPNPassthrough",
  "getFirewallSwitch",
  "getUrlFilterSettings",
  "GetStaticRouting",
  "GetDynamicRouting",
  "getIPFilterList",
  "getCurrentProfile",
  "GetALGSettings",
  "getDMZInfo",
  "getPortFwding",
  "getSMSAutoRedirectSetting",
  "GetNetworkRegisterState",
  "GetActiveData",
  # SMS related
  "SendSMS",
  "GetSendSMSResult",
  "GetSMSListByContactNum",
  "GetSingleSMS",
  "getSmsInitState",
  # Connection Management
  "Connect",
  "DisConnect",
  # Network Settings
  "SetNetworkSettings",
  # USSD
  "SendUSSD",
  "GetUSSDSendResult",
  "SetUSSDEnd",
  # Device Management
  "SetConnectedDeviceBlock",
  "SetDeviceUnlock",
  "GetBlockDeviceList",
  # SMS Management (additional)
  "GetSMSContentList",
  "DeleteSMS",
  "SaveSMS",  # Save draft SMS
  # WiFi Settings (write)
  "SetWlanSettings",
]


def get_network_type(network_type: int) -> str:
  """Get human-readable network type"""
  return NETWORK_TYPES.get(network_type, f"Unknown ({network_type})")


def get_connection_status(status: int) -> str:
  """Get human-readable connection status"""
  return CONNECTION_STATUSES.get(status, f"Unknown ({status})")


def get_sms_send_status(status: int) -> str:
  """Get human-readable SMS send status"""
  return SMS_SEND_STATUS.get(status, f"Unknown ({status})")
