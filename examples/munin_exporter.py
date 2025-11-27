#!/usr/bin/env python3
"""
Munin exporter for Alcatel Modem API
Exports modem metrics in Munin format for monitoring

Based on: https://github.com/.../alcatel-mw40-munin-plugin
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelModemAPI


def get_alcatel_data(api, method):
    """Get data from Alcatel API (similar to PHP version)"""
    try:
        result = api.run(method)
        return result
    except Exception as e:
        print(f"# ERROR: {e}", file=sys.stderr)
        return {}

def show_config(data, plugin_name, plugin_id, keys=None):
    """Show Munin config"""
    print(f"graph_title {plugin_name}")
    print(f"graph_vlabel {plugin_id}")
    print("graph_category network")

    if keys:
        filtered = {k: v for k, v in data.items() if k in keys}
    else:
        filtered = data

    for name, value in filtered.items():
        if isinstance(value, (int, float)):
            print(f"{plugin_id}_{name}.label {name}")
            print(f"{plugin_id}_{name}.type GAUGE")
        else:
            print(f"{plugin_id}_{name}.label {name}")
            print(f"{plugin_id}_{name}.type INFO")

def show_values(data, plugin_id, keys=None, convert_to_int=False):
    """Show Munin values"""
    if keys:
        filtered = {k: v for k, v in data.items() if k in keys}
    else:
        filtered = data

    for name, value in filtered.items():
        if convert_to_int:
            value = int(value) if value else 0

        if isinstance(value, (int, float)):
            print(f"{plugin_id}_{name}.value {value}")
        else:
            print(f"{plugin_id}_{name}.info {value}")

def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Munin exporter for Alcatel Modem")
    parser.add_argument("-u", "--url", default=os.getenv("MODEM_URL", "http://192.168.1.1"),
                       help="Modem URL")
    parser.add_argument("-p", "--password", default=os.getenv("MODEM_PASSWORD"),
                       help="Admin password")
    parser.add_argument("-m", "--method", required=True,
                       help="API method (GetSystemStatus, GetNetworkInfo, etc.)")
    parser.add_argument("--keys", nargs="+",
                       help="Only export these keys")
    parser.add_argument("--config", action="store_true",
                       help="Show Munin config")
    parser.add_argument("--plugin-name",
                       help="Plugin name (default: auto-generated)")
    parser.add_argument("--plugin-id",
                       help="Plugin ID (default: auto-generated)")

    args = parser.parse_args()

    # Generate plugin name and ID
    if not args.plugin_name:
        args.plugin_name = f"Alcatel Modem {args.method}"
    if not args.plugin_id:
        args.plugin_id = args.plugin_name.replace(" ", "")

    # Initialize API
    api = AlcatelModemAPI(args.url, args.password)

    # Get data
    data = get_alcatel_data(api, args.method)

    if not data:
        print(f"# ERROR: No data received from {args.method}", file=sys.stderr)
        sys.exit(1)

    # Show config or values
    if args.config:
        show_config(data, args.plugin_name, args.plugin_id, args.keys)
    else:
        show_values(data, args.plugin_id, args.keys)

if __name__ == "__main__":
    main()

