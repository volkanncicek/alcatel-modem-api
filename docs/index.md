# Alcatel Modem API

Modern Python library and CLI tool for interacting with Alcatel LTE modems.

## Features

- 🚀 **Modern API**: Clean, namespace-based API design
- ⚡ **Async Support**: Full async/await support
- 🔒 **Secure**: Optional keyring integration for token storage
- 📝 **Type Safe**: Pydantic models with validation
- 🎨 **Beautiful CLI**: Rich terminal output with Typer
- 🔄 **Auto-retry**: Built-in retry logic with exponential backoff

## Quick Example

```python
from alcatel_modem_api import AlcatelClient

# Create client
client = AlcatelClient("http://192.168.1.1", password="admin")

# Get system status
status = client.system.get_status()
print(f"Signal: {status.signal_strength}%")

# Send SMS
client.sms.send("+1234567890", "Hello from Python!")

# Get network info
network = client.network.get_info()
print(f"Network: {network.network_type}")
```

## Installation

```bash
uv pip install alcatel-modem-api
```

Or with security features (keyring support):

```bash
uv pip install alcatel-modem-api[security]
```

## Documentation

- [Installation Guide](installation.md)
- [Quick Start](quickstart.md)
- [API Reference](api/client.md)
- [CLI Usage](cli.md)
- [Examples](examples.md)

## Supported Models

- MW40V1, MW40V, MW41
- HH72, HH40V
- HH70VB, HH70 (4GEE Home Router / BT variant)
- IK40V
- MW45V
- HUB71

## License

MIT License - see [LICENSE](https://github.com/volkanncicek/alcatel-modem-api/blob/main/LICENSE) file.

