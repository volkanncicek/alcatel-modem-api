# Examples

This directory contains example scripts demonstrating how to use the Alcatel Modem API library.

## Examples

### `poll.py`
Example usage of polling methods.

```bash
# Basic status (no login required)
python examples/poll.py --basic --pretty

# Extended status (requires login)
python examples/poll.py -p admin --extended --pretty
```

### `signal.py`
Signal strength monitor - Helps position your modem for best signal.

```bash
# Basic monitoring (print only)
python examples/signal.py -u http://192.168.1.1

# With voice announcements (macOS)
python examples/signal.py -u http://192.168.1.1 --voice

# Extended info (RSSI, RSRP, SINR - requires login)
python examples/signal.py -u http://192.168.1.1 -p admin --extended

# Custom interval
python examples/signal.py -u http://192.168.1.1 --interval 2
```

**Usage Scenario:**
1. Connect modem to extension cable
2. Run the script
3. Try different positions
4. Script will tell you the best signal strength

**Platform Support:**
- macOS: `say` command (built-in)
- Windows: SAPI (requires pywin32)
- Linux: `espeak` or `festival` (installation required)

### `ussd.py`
USSD code example - Send USSD codes to the modem.

```bash
# Send USSD code
python examples/ussd.py -u http://192.168.1.1 -p admin -c "*222#"

# List example codes
python examples/ussd.py --list

# Set wait time
python examples/ussd.py -u http://192.168.1.1 -p admin -c "*222#" --wait 10
```

**USSD Send States:**
- `2`: Success - Response received
- `3`: Error - Try changing Network Mode (3G or Auto)

### `connection.py`
Connection and network settings management.

```bash
# Connect
python examples/connection.py -u http://192.168.1.1 -p admin connect

# Disconnect
python examples/connection.py -u http://192.168.1.1 -p admin disconnect

# Show status
python examples/connection.py -u http://192.168.1.1 -p admin status

# Show network settings
python examples/connection.py -u http://192.168.1.1 -p admin network get

# Change network mode (auto, 2g, 3g, 4g)
python examples/connection.py -u http://192.168.1.1 -p admin network set 4g
```

**Network Modes:**
- `auto`: Automatic selection (0)
- `2g`: 2G only (1)
- `3g`: 3G only (2)
- `4g`: 4G only (3)

### `sms.py`
SMS helper utilities - Send SMS and wait for response.

```bash
# Send SMS and wait for response
python examples/sms.py -p admin --send --phone 2222 --message KALAN --sender 2222

# Wait for SMS
python examples/sms.py -p admin --wait --sender 2222 --timeout 60
```

### `prometheus_exporter.py`
Prometheus metrics exporter - Export modem metrics in Prometheus format.

```bash
# Basic usage (metrics that don't require login)
python examples/prometheus_exporter.py -u http://192.168.1.1 --port 8080

# All metrics (including login-required metrics)
python examples/prometheus_exporter.py -u http://192.168.1.1 -p admin --port 8080 --interval 10
```

**Prometheus Configuration:**
```yaml
scrape_configs:
  - job_name: 'alcatel-modem'
    scrape_interval: 10s
    static_configs:
      - targets: ['localhost:8080']
```

### `munin_exporter.py`
Munin exporter - Export modem metrics in Munin format.

```bash
# Show config
python examples/munin_exporter.py -u http://192.168.1.1 -m GetSystemStatus --config

# Show values
python examples/munin_exporter.py -u http://192.168.1.1 -m GetSystemStatus

# Show only specific keys
python examples/munin_exporter.py -u http://192.168.1.1 -m GetSystemStatus --keys bat_cap SignalStrength
```


## Usage

All examples can be run from the project root:

```bash
cd alcatel_modem_api
python examples/poll.py --basic --pretty
```

Or directly from the examples directory:

```bash
cd alcatel_modem_api/examples
python poll.py --basic --pretty
```

**Note:** Make sure the package is installed or the parent directory is in your Python path.

## Tests

For test scripts, see the `tests/` directory.
