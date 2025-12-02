# Alcatel Modem API

[![PyPI version](https://img.shields.io/pypi/v/alcatel-modem-api.svg)](https://pypi.org/project/alcatel-modem-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/alcatel-modem-api.svg)](https://pypi.org/project/alcatel-modem-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/volkanncicek/alcatel-modem-api/actions/workflows/main.yml/badge.svg)](https://github.com/volkanncicek/alcatel-modem-api/actions)

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
# Install from source (development)
uv pip install -e .

# Or using pip
pip install -e .

# Or install from PyPI (when published)
pip install alcatel-modem-api
```

## Project Structure

```
alcatel_modem_api/
├── alcatel_modem_api/   # Main package
│   ├── __init__.py      # Package exports
│   ├── client.py         # Core HTTP client (AlcatelClient)
│   ├── cli.py           # Command-line interface (Typer)
│   ├── constants.py     # Constants (network types, statuses, verbs)
│   ├── exceptions.py   # Custom exceptions
│   ├── models.py        # Pydantic data models
│   ├── endpoints/       # Namespace endpoints
│   │   ├── sms.py       # SMS operations
│   │   ├── network.py   # Network operations
│   │   ├── wlan.py      # WiFi operations
│   │   ├── device.py    # Device management
│   │   └── system.py    # System operations
│   └── utils/           # Utility functions
│       └── encryption.py # Encryption utilities
├── examples/            # Example scripts
│   ├── README.md        # Examples documentation
│   ├── poll.py          # Poll usage examples
│   ├── signal.py        # Signal strength monitoring
│   ├── sms.py           # SMS utilities
│   ├── connection.py    # Connection management
│   ├── prometheus_exporter.py # Prometheus metrics exporter
│   ├── munin_exporter.py      # Munin metrics exporter
│   └── ussd.py          # USSD code examples
├── pyproject.toml       # Python project configuration
├── README.md            # This file
├── requirements.txt     # Dependencies
└── ruff.toml            # Ruff linter configuration
```

## Usage

### Command Line Interface

The CLI uses modern Typer-based commands with beautiful Rich output.

**Note:** After installation, use the `alcatel` command. If not installed as a package, you can also use:
```bash
python -m alcatel_modem_api.cli system status --pretty
```

#### Basic Commands (No Login Required)

```bash
# Get system status
alcatel system status --pretty

# Or using run command
alcatel run GetSystemStatus --pretty
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
alcatel run GetSimStatus --pretty

# Get system info
alcatel run GetSystemInfo --pretty

# Poll basic status
alcatel system poll-basic --pretty
```

#### Protected Commands (Login Required)

Commands that require login will automatically use a saved authentication token if available. The token is stored in `~/.alcatel_modem_session` after the first successful login.

**If you have a valid token:**
```bash
# Token will be used automatically, no password needed
alcatel run GetLanSettings --pretty
```

**If token is missing or expired:**
```bash
# Command will fail with authentication error
alcatel run GetLanSettings --pretty
```

**Error output:**
```
❌ Authentication error: Authentication failed: Authentication Failure
   Tip: Use -p <password> to provide admin password
```

**To login and save a new token:**
```bash
# Pass the admin password to login and save token
alcatel run GetLanSettings -p admin --pretty
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
alcatel network info -u http://192.168.1.1 -p admin --pretty

# Get WiFi settings
alcatel wlan settings -u http://192.168.1.1 -p admin --pretty

# Poll extended status
alcatel system poll-extended -u http://192.168.1.1 -p admin --pretty
```

#### SMS Operations

```bash
# Send SMS
alcatel sms send -n +1234567890 -m "Hello from Python!" -u http://192.168.1.1 -p admin

# List SMS messages
alcatel sms list -u http://192.168.1.1 -p admin --pretty

# List SMS from specific contact
alcatel sms list -c +1234567890 -u http://192.168.1.1 -p admin --pretty
```

#### Network Operations

```bash
# Connect to network
alcatel network connect -u http://192.168.1.1 -p admin

# Disconnect from network
alcatel network disconnect -u http://192.168.1.1 -p admin

# Get network info
alcatel network info -u http://192.168.1.1 -p admin --pretty
```

#### List Available Commands

```bash
# List public commands (no login required)
alcatel list

# List all commands
alcatel list --all
```

### Python Library

```python
from alcatel_modem_api import AlcatelClient

# Initialize client
client = AlcatelClient(url="http://192.168.1.1", password="admin")

# Get system status (returns Pydantic model)
status = client.system.get_status()
print(f"Network: {status.network_name}")
print(f"Signal: {status.signal_strength}/5")

# Get network info (requires login, returns Pydantic model)
network = client.network.get_info()
print(f"RSSI: {network.rssi} dBm")
print(f"RSRP: {network.rsrp} dBm")
print(f"Signal Quality: {network.signal_quality_percent}%")

# Send SMS
client.sms.send("+1234567890", "Hello from Python!")

# Get SMS list (returns list of SMSMessage models)
sms_list = client.sms.list()
for msg in sms_list:
    print(f"{msg.phone_number}: {msg.content}")

# Context manager support (automatic cleanup)
with AlcatelClient(url="http://192.168.1.1", password="admin") as client:
    status = client.system.get_status()
    print(status.network_name)

# Async support with context manager
import asyncio

async def main():
    async with AlcatelClient(url="http://192.168.1.1", password="admin") as client:
        status = await client.system.get_status_async()
        print(status.network_name)

asyncio.run(main())
```

## API Reference

### AlcatelClient

Main API class for interacting with Alcatel modems.

#### Core Methods

- `run(command, **params)`: Execute any API command (sync)
- `run_async(command, **params)`: Execute any API command (async)
- `logout()`: Clear authentication token
- `set_password(password)`: Set admin password for automatic login
- `close()`: Close HTTP clients (sync)
- `aclose()`: Close HTTP clients (async)
- Context manager support: Use `with AlcatelClient(...)` or `async with AlcatelClient(...)` for automatic cleanup

#### Namespace Endpoints

The API is organized into namespaces for better organization:

**System Endpoint** (`client.system`):
- `get_status()`: Get system status (returns `SystemStatus` model)
- `get_info()`: Get system information
- `get_sim_status()`: Get SIM card status
- `poll_basic_status()`: Poll basic status (no login required)
- `poll_extended_status()`: Poll extended status (requires login, returns `ExtendedStatus` model)
- `send_ussd_code(code, wait_seconds=5)`: Send USSD code

**Network Endpoint** (`client.network`):
- `get_info()`: Get network information (returns `NetworkInfo` model)
  - `NetworkInfo.signal_quality_percent`: Calculated signal quality percentage (0-100) based on RSRP/RSSI
- `get_settings()`: Get network settings
- `set_settings(network_mode, net_selection_mode=0)`: Set network settings
- `connect()`: Connect to network
- `disconnect()`: Disconnect from network
- `get_connection_state()`: Get connection state (returns `ConnectionState` model)

**SMS Endpoint** (`client.sms`):
- `send(phone_number, message, timeout=30)`: Send SMS message
- `list(contact_number=None)`: Get SMS list (returns list of `SMSMessage` models)
- `get(sms_id)`: Get single SMS by ID
- `get_storage_state()`: Get SMS storage state
- `get_settings()`: Get SMS settings
- `delete(sms_id)`: Delete SMS by ID

**WLAN Endpoint** (`client.wlan`):
- `get_settings()`: Get WiFi settings
- `set_settings(...)`: Set WiFi settings
- `get_state()`: Get WiFi state
- `get_statistics()`: Get WiFi statistics

**Device Endpoint** (`client.device`):
- `get_connected_list()`: Get connected devices
- `get_block_list()`: Get blocked devices
- `block(mac_address)`: Block device
- `unblock(mac_address)`: Unblock device

All endpoints have both sync and async versions (e.g., `get_status()` and `get_status_async()`).

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
- **Config File**: `~/.config/alcatel-api/config.toml` (stores default URL and password)

### Configuration Management

You can save your default URL and password to avoid typing them every time:

```bash
# Configure default URL and password
alcatel configure -u http://192.168.1.1 -p admin

# View current configuration
alcatel configure

# After configuration, you can use commands without -u and -p
alcatel system status
alcatel network info
```

**Note:** Storing passwords in plain text is not recommended for production use. Consider using environment variables or passing the password via CLI flags instead.

### Custom URL

If your modem is at a different IP address:

```bash
# Using CLI flag (overrides config)
alcatel system status -u http://192.168.0.1

# Or configure it once
alcatel configure -u http://192.168.0.1
alcatel system status
```

## Authentication

Alcatel modems use different authentication methods depending on the model. This library automatically handles authentication for you, but understanding the differences can help with troubleshooting.

### Model-Specific Authentication

#### MW40V1 / MW40V / MW41
- **Login Method**: Unencrypted (plain text)
- **Token**: Plain token (no encryption needed)
- **Example**: 
  ```python
  client = AlcatelClient("http://192.168.1.1", "admin")
  # Login with plain username/password
  ```

#### HH70VB / HH70 (4GEE Home Router / BT variant)
- **Login Method**: Uses `_TclRequestVerificationKey` header (no login required for public commands)
- **Token**: For restricted commands, requires login with encrypted credentials
- **Note**: EE branded variant, compatible with BT branded HH70
- **Example**:
  ```python
  client = AlcatelClient("http://192.168.1.1", "admin")
  # API automatically handles authentication
  ```

#### HH72 / HH40V
- **Login Method**: Encrypted username/password
- **Token**: Encrypted token
- **Encryption Key**: `"e5dl12XYVggihggafXWf0f2YSf2Xngd1"` (found by reverse engineering Android app)
- **Example**:
  ```python
  # Automatically handled by AlcatelClient
  client = AlcatelClient("http://192.168.1.1", "admin")
  # Client will try unencrypted first, then encrypted
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
alcatel system status --pretty
```

### Send SMS Notification

```bash
# Using CLI
alcatel sms send -n +1234567890 -m "System backup completed!" -u http://192.168.1.1 -p admin

# Using helper script
python examples/sms.py -u http://192.168.1.1 -p admin --send --phone +1234567890 --message "System backup completed!"
```

### Python Script Example

```python
from alcatel_modem_api import AlcatelClient

client = AlcatelClient("http://192.168.1.1", "admin")

# Check connection
status = client.system.get_status()
if status.connection_status == 2:
    print("✅ Connected to network")
    
# Send notification
try:
    client.sms.send("+1234567890", "Modem is online and connected!")
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
from alcatel_modem_api import AlcatelClient

client = AlcatelClient("http://192.168.1.1", "admin")

def send_alert(message):
    """Send SMS alert via modem"""
    try:
        client.sms.send("+1234567890", message)
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
alcatel sms send -n +1234567890 -m "Backup completed: $backup_result" \
    -u http://192.168.1.1 -p admin
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
alcatel sms send -n 1234 -m "KALAN" -u http://192.168.1.1 -p admin
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
alcatel system status --pretty

# Or using poll script
python examples/poll.py --basic --pretty

# Monitor signal strength
python examples/signal.py -u http://192.168.1.1 -p admin --extended

# Send SMS
alcatel sms send -n 1234 -m "KALAN" -u http://192.168.1.1 -p admin

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

### Debug Mode

If you encounter errors, use the `--debug` flag to see full traceback:

```bash
alcatel system status --debug
alcatel network info -p admin --debug
```

This will show the complete Python traceback, which is helpful for debugging issues.

### Authentication Error

If you get an authentication error, make sure:
1. You provided the correct password with `-p` flag or configured it with `alcatel configure`
2. The modem admin password is correct
3. You're using the correct URL

### Connection Error

If you can't connect:
1. Check if the modem is accessible at the URL
2. Verify you're on the same network
3. Try accessing the web interface in a browser first
4. Use `--debug` flag to see detailed error information

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

