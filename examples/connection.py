#!/usr/bin/env python3
"""
Connection Manager - Manage modem connection and network settings
Based on: https://github.com/raulcr98/link-zone-desktop
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelClient
from alcatel_modem_api.constants import get_network_type

NETWORK_MODES = {
    "auto": 0,
    "2g": 1,
    "3g": 2,
    "4g": 3,
}

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage Alcatel Modem Connection")
    parser.add_argument("-u", "--url", default="http://192.168.1.1",
                       help="Modem URL")
    parser.add_argument("-p", "--password", required=True,
                       help="Admin password")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Connect command
    subparsers.add_parser("connect", help="Connect to network")

    # Disconnect command
    subparsers.add_parser("disconnect", help="Disconnect from network")

    # Status command
    subparsers.add_parser("status", help="Show connection status")

    # Network settings
    network_parser = subparsers.add_parser("network", help="Network settings")
    network_subparsers = network_parser.add_subparsers(dest="network_command")

    network_subparsers.add_parser("get", help="Get network settings")
    set_network_parser = network_subparsers.add_parser("set", help="Set network mode")
    set_network_parser.add_argument("mode", choices=["auto", "2g", "3g", "4g"],
                                    help="Network mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize API
    api = AlcatelClient(args.url, args.password)

    try:
        if args.command == "connect":
            print("Connecting to network...")
            result = api.network.connect()
            print("✅ Connection initiated")
            print(f"Response: {result}")

        elif args.command == "disconnect":
            print("Disconnecting from network...")
            result = api.network.disconnect()
            print("✅ Disconnection initiated")
            print(f"Response: {result}")

        elif args.command == "status":
            connection_state = api.network.get_connection_state()
            system_status = api.system.get_status()
            network_settings = api.network.get_settings()

            print("\n📊 Connection Status:")
            print(f"  Connection Status: {connection_state.connection_status}")
            print(f"  Network Name: {system_status.network_name}")
            print(f"  Network Type: {get_network_type(system_status.network_type)}")
            print(f"  Signal Strength: {system_status.signal_strength}")
            print(f"  Network Mode: {network_settings.get('NetworkMode', 'Unknown')}")
            print(f"  Network Selection Mode: {network_settings.get('NetselectionMode', 'Unknown')}")

        elif args.command == "network":
            if args.network_command == "get":
                settings = api.network.get_settings()
                print("\n📡 Network Settings:")
                print(f"  Network Mode: {settings.get('NetworkMode', 'Unknown')}")
                print(f"  Network Selection Mode: {settings.get('NetselectionMode', 'Unknown')}")

            elif args.network_command == "set":
                network_mode = NETWORK_MODES[args.mode]
                print(f"Setting network mode to {args.mode.upper()} ({network_mode})...")

                # Check if connected
                connection_state = api.network.get_connection_state()
                is_connected = connection_state.connection_status == 2

                if is_connected:
                    print("⚠️  Modem is connected. Disconnecting first...")
                    api.network.disconnect()
                    import time
                    time.sleep(2)

                result = api.network.set_settings(network_mode)
                print(f"✅ Network mode set to {args.mode.upper()}")

                if is_connected:
                    print("Reconnecting...")
                    time.sleep(2)
                    api.network.connect()
                    print("✅ Reconnected")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

