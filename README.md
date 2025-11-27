# Alcatel Modem API

Generic Python library and CLI tool for Alcatel LTE modems. Supports multiple Alcatel models (see [Supported Models](#supported-models) below) that use the `/jrd/webapi` endpoint.

## Purpose

This library allows you to interact with Alcatel LTE modems through their web API available at `http://modem_ip/jrd/webapi`. You can retrieve modem information, manage SMS messages, configure network settings, and monitor connection status programmatically without needing to use the web interface.

## Features

- ✅ **Generic Support**: Works with multiple Alcatel modem models
- ✅ **Authentication**: Automatic login and token management
- ✅ **SMS Management**: Send and receive SMS messages
- ✅ **System Info**: Get modem status, network info, and settings
- ✅ **CLI Tool**: Easy-to-use command-line interface
- ✅ **Python Library**: Use as a library in your Python projects

## Compatibility

### Supported Models

This library has been tested with the following Alcatel modem models, but it might also work with other Alcatel LTE modems that use the `/jrd/webapi` endpoint:

- Alcatel MW40V1 (tested)
- Alcatel MW40V / MW40 (tested)
- Alcatel MW41 (tested)
- Alcatel HH72 / HUB72 (tested)
- Alcatel HH40V / Linkhub HH40v (tested) - [Technical Documentation & OpenWrt Support](https://github.com/froonix/HH40V/wiki)
- Alcatel IK40V (tested)
- Alcatel HH70VB / 4GEE Home Router (EE branded, tested) - [Technical Documentation](https://github.com/jamesmacwhite/hh70-ee/wiki)
- Alcatel HH70 (BT branded variant, compatible)
- Alcatel MW45V (partial support - different encryption)
- Other Alcatel modems with `/jrd/webapi` endpoint

**Note:** HUB71 uses a different authentication method and may not be fully compatible.

## Installation

```bash
# Install dependencies
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Project Structure

```
alcatel_modem_api/
├── alcatel_modem_api/   # Main package
│   ├── __init__.py      # Package exports
│   ├── api.py           # Main API class (AlcatelModemAPI)
│   ├── auth.py          # Authentication and token management
│   ├── cli.py           # Command-line interface
│   ├── constants.py     # Constants (network types, statuses, verbs)
│   └── sms.py           # SMS operations (SMSManager)
├── examples/            # Example scripts
│   ├── README.md        # Examples documentation
│   ├── poll.py          # Poll usage examples
│   ├── signal.py        # Signal strength monitoring
│   ├── sms.py           # SMS utilities
│   ├── connection.py    # Connection management
│   ├── prometheus_exporter.py # Prometheus metrics exporter
│   ├── munin_exporter.py      # Munin metrics exporter
│   ├── ussd.py          # USSD code examples
├── pyproject.toml       # Python project configuration
├── README.md            # This file
├── requirements.txt     # Dependencies
└── ruff.toml            # Ruff linter configuration
```

## Usage

### Command Line Interface

#### Basic Commands (No Login Required)

```bash
# Get system status
python -m alcatel_modem_api.cli -c GetSystemStatus --pretty
```

**Output example:**
```json
{
  "chg_state": 2,
  "bat_cap": 80,
  "bat_level": 4,
  "NetworkType": 8,
  "NetworkName": "Operator",
  "Roaming": 1,
  "Domestic_Roaming": 1,
  "SignalStrength": 5,
  "ConnectionStatus": 2,
  "Conprofileerror": 0,
  "ClearCode": 0,
  "mPdpRejectCount": 0,
  "SmsState": 2,
  "WlanState": 1,
  "curr_num": 1,
  "TotalConnNum": 1
}
```

```bash
# Get SIM status
python -m alcatel_modem_api.cli -c GetSimStatus --pretty

# Get system info
python -m alcatel_modem_api.cli -c GetSystemInfo --pretty
```

#### Protected Commands (Login Required)

Commands that require login will automatically use a saved authentication token if available. The token is stored in `~/.alcatel_modem_session` after the first successful login.

**If you have a valid token:**
```bash
# Token will be used automatically, no password needed
python -m alcatel_modem_api.cli -c GetLanSettings --pretty
```

**If token is missing or expired:**
```bash
# Command will fail with authentication error
python -m alcatel_modem_api.cli -c GetLanSettings --pretty
```

**Error output:**
```
The modem replied with an error message
  Error code: -32699
  Error message: Authentication Failure
```

**To login and save a new token:**
```bash
# Pass the admin password to login and save token
python -m alcatel_modem_api.cli -c GetLanSettings -p admin --pretty
```

After successful login, the token is saved and subsequent commands will work without the password (until the token expires).

**Output example:**
```json
{
  "DNSMode": 0,
  "DNSAddress1": "",
  "DNSAddress2": "",
  "IPv4IPAddress": "192.168.1.1",
  "host_name": "router.home",
  "SubnetMask": "255.255.255.0",
  "DHCPServerStatus": 1,
  "StartIPAddress": "192.168.1.100",
  "EndIPAddress": "192.168.1.200",
  "DHCPLeaseTime": 12,
  "MacAddress": "aa:bb:cc:dd:ee:ff\n"
}
```

**More examples:**
```bash
# Get network info
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin -c GetNetworkInfo --pretty

# Get WiFi settings
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin -c GetWlanSettings --pretty
```

#### SMS Operations

```bash
# Send SMS
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin sms send -n +1234567890 -m "Hello from Python!"

# Get SMS send status
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin -c GetSendSMSResult --pretty
```

#### List Available Commands

```bash
python -m alcatel_modem_api.cli --list
```

### Python Library

```python
from alcatel_modem_api import AlcatelModemAPI, SMSManager

# Initialize API
api = AlcatelModemAPI(url="http://192.168.1.1", password="admin")

# Get system status
status = api.get_system_status()
print(f"Network: {status['NetworkName']}")
print(f"Signal: {status['SignalStrength']}/5")

# Get network info (requires login)
network = api.get_network_info()
print(network)

# Send SMS
sms = SMSManager(api)
sms.send_sms("+1234567890", "Hello from Python!")

# Get SMS list
sms_list = sms.get_sms_list()
print(sms_list)
```

## API Reference

### AlcatelModemAPI

Main API class for interacting with Alcatel modems.

#### Methods

- `run(command, **params)`: Execute any API command
- `run_pretty(command, **params)`: Execute command and return pretty JSON
- `get_system_status()`: Get system status
- `get_sim_status()`: Get SIM card status
- `get_network_info()`: Get network information (requires login)
- `get_system_info()`: Get system information
- `get_connection_state()`: Get connection state (requires login)
- `get_wlan_settings()`: Get WiFi settings (requires login)
- `get_lan_settings()`: Get LAN settings (requires login)
- `logout()`: Clear authentication token

### SMSManager

Manages SMS operations.

#### Methods

- `send_sms(phone_number, message, timeout=30)`: Send SMS message
- `get_send_status()`: Get SMS send status
- `get_sms_list(contact_number=None)`: Get SMS list
- `get_single_sms(sms_id)`: Get single SMS by ID
- `get_sms_storage_state()`: Get SMS storage state
- `get_sms_settings()`: Get SMS settings

## Available Commands

### Commands that don't require login

- `GetCurrentLanguage`
- `GetSimStatus`
- `GetLoginState`
- `GetSystemStatus`
- `GetSystemInfo`
- `GetQuickSetup`
- `GetSMSStorageState`

### Commands that require login (add `-p password` to command line arguments)

- `GetDeviceNewVersion`
- `GetNetworkInfo`
- `GetWanSettings`
- `GetWanIsConnInter`
- `GetSMSStorageState`
- `GetCallLogCountInfo`
- `GetActiveData`
- `GetConnectionSettings`
- `GetUsageSettings`
- `GetUsageRecord`
- `GetNetworkSettings`
- `GetNetworkRegisterState`
- `GetProfileList`
- `GetConnectionState`
- `GetLanSettings`
- `GetALGSettings`
- `getDMZInfo`
- `GetUpnpSettings`
- `getPortFwding`
- `getSmsInitState`
- `GetSMSListByContactNum`
- `GetSMSContentList`
- `GetSingleSMS`
- `SendSMS`
- `GetSendSMSResult`
- `DeleteSMS`
- `SaveSMS`
- `getSMSAutoRedirectSetting`
- `GetSMSSettings`
- `GetSMSContactList`
- `GetDdnsSettings`
- `GetDynamicRouting`
- `getIPFilterList`
- `GetMacFilterSettings`
- `GetParentalSettings`
- `GetConnectedDeviceList`
- `GetAutoValidatePinState`
- `GetStaticRouting`
- `getUrlFilterSettings`
- `GetVPNPassthrough`
- `getFirewallSwitch`
- `GetDLNASettings`
- `GetFtpSettings`
- `GetSambaSettings`
- `GetDeviceDefaultRight`
- `GetBlockDeviceList`
- `SetConnectedDeviceBlock`
- `SetDeviceUnlock`
- `GetLanStatistics`
- `GetWlanSettings`
- `GetWlanState`
- `GetWlanStatistics`
- `SetWlanSettings`
- `GetWlanSupportMode`
- `GetWmmSwitch`
- `getCurrentProfile`
- `GetLanPortInfo`
- `GetPasswordChangeFlag`
- `GetUSBLocalUpdateList`
- `GetSystemSettings`
- `GetDeviceUpgradeState`
- `GetCurrentTime`
- `GetClientConfiguration`
- `GetUSSDSendResult`
- `SendUSSD`
- `GetUSSDSendResult`
- `SetUSSDEnd`
- `GetWanCurrentMacAddr`
- `GetCallLogList`
- `GetQosSettings`
- `GetVoicemail`
- `Connect`
- `Disconnect`
- `SetNetworkSettings`
- `GetCurrentData`
- `GetExtendTimes`
- `GetLogcfg`
- `GetPingTraceroute`
- `GetPortTriggering`
- `GetSIPAccountSettings`
- `GetSIPServerSettings`
- `GetTransferProtocol`
- `GetWPSConnectionState`
- `GetWPSSettings`

**Note:** Use `--list` or `--list-all` to see all available commands dynamically.

## Configuration

### Default Settings

- **URL**: `http://192.168.1.1`
- **Session File**: `~/.alcatel_modem_session` (stores authentication token)

### Custom URL

If your modem is at a different IP address:

```bash
python -m alcatel_modem_api.cli -u http://192.168.0.1 -c GetSystemStatus
```

## Authentication

Alcatel modems use different authentication methods depending on the model. This library automatically handles authentication for you, but understanding the differences can help with troubleshooting.

### Model-Specific Authentication

#### MW40V1 / MW40V / MW41
- **Login Method**: Unencrypted (plain text)
- **Token**: Plain token (no encryption needed)
- **Example**: 
  ```python
  api = AlcatelModemAPI("http://192.168.1.1", "admin")
  # Login with plain username/password
  ```

#### HH70VB / HH70 (4GEE Home Router / BT variant)
- **Login Method**: Uses `_TclRequestVerificationKey` header (no login required for public commands)
- **Token**: For restricted commands, requires login with encrypted credentials
- **Note**: EE branded variant, compatible with BT branded HH70
- **Example**:
  ```python
  api = AlcatelModemAPI("http://192.168.1.1", "admin")
  # API automatically handles authentication
  ```

#### HH72 / HH40V
- **Login Method**: Encrypted username/password
- **Token**: Encrypted token
- **Encryption Key**: `"e5dl12XYVggihggafXWf0f2YSf2Xngd1"` (found by reverse engineering Android app)
- **Example**:
  ```python
  # Automatically handled by AlcatelModemAPI
  api = AlcatelModemAPI("http://192.168.1.1", "admin")
  # API will try unencrypted first, then encrypted
  ```

#### MW45V
- **Login Method**: Different encryption for username vs password
- **Status**: May require model-specific handling
- **Note**: Encryption differs between username and password fields

#### HUB71
- **Login Method**: Different method to generate `_TclRequestVerificationToken`
- **Status**: Not compatible with standard encryption methods
- **Note**: May require separate implementation

### Authentication Flow

1. **Get Login State**: Check if already logged in
2. **Login**: 
   - Try unencrypted login (MW40V1 style)
   - If fails, try encrypted login (HH72 style)
3. **Token Management**: 
   - Save token to `~/.alcatel_modem_session`
   - Use token in `_TclRequestVerificationToken` header

### Headers

#### Public Commands (No Login)
```python
headers = {
    "_TclRequestVerificationKey": "<key from browser>",
    "Referer": "http://192.168.1.1/index.html"
}
```

#### Restricted Commands (Login Required)
```python
headers = {
    "_TclRequestVerificationToken": "<encrypted token>",
    "Referer": "http://192.168.1.1/index.html"
}
```

### Finding Your Request Key

1. Connect to your modem's WiFi
2. Open browser and go to admin page (usually `192.168.1.1`)
3. Open Developer Tools → Network tab
4. Look for requests to `/jrd/webapi`
5. Copy the value of `_TclRequestVerificationKey` header

### Authentication References

- [GitHub Gist - say_lte.py](https://gist.github.com/lukpueh/a595f74d8edfb512d4f5be7056dfdb1e)
- [Alcatel HH72 Script](https://github.com/spolette/Alcatel_HH72)
- Encryption key found by reverse engineering [Alcatel SmartLink Android app](https://play.google.com/store/apps/details?id=com.alcatel.smartlinkv3)

## Examples

### Check Modem Status

```bash
python -m alcatel_modem_api.cli -c GetSystemStatus --pretty
```

### Send SMS Notification

```bash
# Using CLI
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin sms send -n +1234567890 -m "System backup completed!"

# Using helper script
python examples/sms.py -u http://192.168.1.1 -p admin --send --phone +1234567890 --message "System backup completed!"
```

### Python Script Example

```python
from alcatel_modem_api import AlcatelModemAPI, SMSManager

api = AlcatelModemAPI("http://192.168.1.1", "admin")
sms = SMSManager(api)

# Check connection
status = api.get_system_status()
if status["ConnectionStatus"] == 2:
    print("✅ Connected to network")
    
# Send notification
try:
    sms.send_sms("+1234567890", "Modem is online and connected!")
    print("✅ Notification sent")
except Exception as e:
    print(f"❌ Failed to send: {e}")
```

## Use Cases

### Home Automation Integration

If your mobile ISP contract provides unlimited SMS messages, you can use the modem's SMS functionality to create a notification service for your home automation system. This is especially useful for:

- **System Alerts**: Get notified when backups complete, servers go down, or critical events occur
- **Security Monitoring**: Receive SMS alerts when motion sensors trigger or doors are opened
- **Smart Home Status**: Get daily summaries of energy usage, temperature, or other metrics

**Example: Node-RED Integration**

```python
from alcatel_modem_api import AlcatelModemAPI, SMSManager

api = AlcatelModemAPI("http://192.168.1.1", "admin")
sms = SMSManager(api)

def send_alert(message):
    """Send SMS alert via modem"""
    try:
        sms.send_sms("+1234567890", message)
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

# Use in Node-RED or other automation systems
if __name__ == "__main__":
    send_alert("Home automation system started successfully!")
```

**Example: Shell Script Integration**

```bash
#!/bin/bash
# backup_notification.sh

# Run backup
backup_result=$(./backup_script.sh)

# Send SMS notification
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin \
    sms send -n +1234567890 -m "Backup completed: $backup_result"
```

### Signal Strength Optimization

Use the signal monitor script to find the best position for your modem. This is particularly useful when:

- Setting up a new modem location
- Moving to a new apartment or office
- Troubleshooting poor signal quality

```bash
# Monitor signal strength and get voice announcements when it changes
python examples/signal.py -u http://192.168.1.1 --interval 2

# Walk around your space and place the modem where you get the highest signal
```

See `examples/signal.py` for more options.

### SMS-Based Query System

Query your mobile operator via SMS:

```bash
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin sms send -n 1234 -m "KALAN"
python examples/sms.py -p admin --wait --sender 1234 --timeout 30
```

See `examples/sms.py` for more options.

### Monitoring and Metrics

Export metrics for Prometheus or Munin:

```bash
python examples/prometheus_exporter.py -u http://192.168.1.1 -p admin --port 8080
python examples/munin_exporter.py -u http://192.168.1.1 -p admin -m GetSystemStatus
```

See `examples/prometheus_exporter.py` and `examples/munin_exporter.py` for details.

### Network Management

Manage network connection and settings:

```bash
python examples/connection.py -u http://192.168.1.1 -p admin status
python examples/connection.py -u http://192.168.1.1 -p admin network set 4g
```

See `examples/connection.py` for all options.

### USSD Code Execution

Send USSD codes to query your operator:

```bash
python examples/ussd.py -u http://192.168.1.1 -p admin -c "*222#"
```

See `examples/ussd.py` for more options.

**For detailed examples and usage scenarios, see [`examples/README.md`](examples/README.md).**

## Quick Start Examples

Get started quickly with these practical examples:

```bash
# Check modem status (no password needed)
python examples/poll.py --basic --pretty

# Monitor signal strength
python examples/signal.py -u http://192.168.1.1 -p admin --extended

# Send SMS
python -m alcatel_modem_api.cli -u http://192.168.1.1 -p admin sms send -n 1234 -m "KALAN"

# Check connection status
python examples/connection.py -u http://192.168.1.1 -p admin status

# Send USSD code
python examples/ussd.py -u http://192.168.1.1 -p admin -c "*222#"

# Start Prometheus exporter
python examples/prometheus_exporter.py -u http://192.168.1.1 -p admin --port 8080
```

**Available example scripts:**
- `poll.py` - Poll modem status
- `signal.py` - Signal strength monitoring
- `sms.py` - SMS utilities
- `connection.py` - Network management
- `prometheus_exporter.py` - Prometheus metrics
- `munin_exporter.py` - Munin metrics
- `ussd.py` - USSD codes

For detailed usage and all options, see [`examples/README.md`](examples/README.md).

## Troubleshooting

### Authentication Error

If you get an authentication error, make sure:
1. You provided the correct password with `-p` flag
2. The modem admin password is correct
3. You're using the correct URL

### Connection Error

If you can't connect:
1. Check if the modem is accessible at the URL
2. Verify you're on the same network
3. Try accessing the web interface in a browser first

### SMS Not Sending

If SMS fails to send:
1. Check SIM card status: `GetSimStatus`
2. Verify SMS settings: `GetSMSSettings`
3. Check SMS storage: `GetSMSStorageState`
4. Ensure you have SMS credits/plan

## Advanced Topics

### Root Access for MW40/MW41

For advanced users who need root access to the modem firmware, there are tools available for Alcatel LinkZone MW40/MW41 modems:

**LinkZoneRoot** - Root access tool for MW40/MW41 (MDM9207):
- Repository: [jtanx/LinkZoneRoot](https://github.com/jtanx/LinkZoneRoot)
- Release: [v1.0.0](https://github.com/jtanx/LinkZoneRoot/releases/tag/v1.0.0)
- [Root Access Guide](https://gist.github.com/unixfox/ed9f861c11a8d356f3862541cc24d647) - Step-by-step instructions for getting root access
- [Reverse Engineering Article](https://alex.studer.dev/2021/01/04/mw41-1) - Detailed technical analysis of how root access works (by Alex Studer)
- Usage: Connect device via USB, run the tool as administrator, select the modem drive, then use `adb shell` for root access

**Note:** Root access is for advanced users only. Use at your own risk. Modifying the firmware may void your warranty and could brick your device.

### OpenWrt Support for HH40V

The Alcatel HH40V router is supported by OpenWrt 23.05:

- [OpenWrt Device Page](https://openwrt.org/toh/alcatel/hh40v) - Official OpenWrt support page
- [HH40V Wiki](https://github.com/froonix/HH40V/wiki) - Comprehensive technical documentation including hardware details, network configuration, and OpenWrt installation guides
- **Security Note:** There are [serious security issues](https://github.com/froonix/HH40V/wiki/OpenWrt-(23.05.0)#lte-modem-security) with the built-in LTE modem, especially with IPv6 enabled SIM cards. Use with caution!

**Note:** OpenWrt installation is for advanced users only. Use at your own risk. Modifying the firmware may void your warranty and could brick your device.

### SSH Access for HH70VB (4GEE Home Router)

For the Alcatel HH70VB / 4GEE Home Router, SSH access was disabled in newer firmware updates. However, there is a method to re-enable SSH access by exploiting the backup and restore feature:

**Exploiting Backup/Restore Feature:**
- [Medium Article](https://medium.com/@jamesmacwhite/exploiting-the-backup-and-restore-feature-on-the-4gee-home-router-4b0c0c0c0c0) - Detailed guide on exploiting the backup/restore feature to re-enable SSH (by James White)
- The method involves crafting a modified `configure.bin` file with SSH enabled in the dropbear configuration
- **Default SSH credentials:** `root:oelinux123` and `admin:admin` (change these immediately after gaining access!)

**Security Note:** This exploit requires LAN access and web interface authentication. Once SSH is enabled, it's strongly recommended to:
1. Change default passwords
2. Enable public key authentication
3. Disable password authentication for better security

**Note:** This is for educational and research purposes only. Use at your own risk.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! This library was created by combining and improving features from multiple open-source projects.

## Acknowledgments

This project is built upon and inspired by the following open-source projects:

- **[Alcatel_HH72](https://github.com/spolette/Alcatel_HH72)** - Original API implementation for Alcatel HH72 modems by [spolette](https://github.com/spolette)
- **[IK40V_SMS](https://github.com/rmappleby/IK40V_SMS)** - SMS sending functionality for Alcatel IK40V modems by [Richard Appleby](https://github.com/rmappleby)
- **[juit-lib-tcl-router](https://github.com/juitnow/juit-lib-tcl-router)** - TypeScript client for Alcatel/TCL routers by [Juit](https://github.com/juitnow)
- **[HH70-EE Wiki](https://github.com/jamesmacwhite/hh70-ee/wiki)** - Technical documentation for EE HH70VB router by [James White](https://github.com/jamesmacwhite)
- **[HH40V Wiki](https://github.com/froonix/HH40V/wiki)** - Technical documentation and OpenWrt support for Alcatel HH40V router by [froonix](https://github.com/froonix)
- **[say_lte.py](https://gist.github.com/lukpueh/a595f74d8edfb512d4f5be7056dfdb1e)** - Original signal strength monitoring script for Alcatel Linkhub HH40v by [Lukas Puehringer](https://gist.github.com/lukpueh)

We've integrated their features into a unified, generic library that supports multiple Alcatel modem models. Thank you to the original authors for their contributions!

