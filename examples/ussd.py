#!/usr/bin/env python3
"""
USSD Example - Send USSD codes to Alcatel modem
Based on: https://github.com/raulcr98/link-zone-desktop

Note: USSD interface may be hidden in web UI but accessible via:
http://192.168.1.1/default.html#more/ussdSetting.html
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelClient

# Common USSD codes (customize for your carrier)
USSD_CODES = {
  "balance": "*222#",  # Check balance (example)
  "data": "*133#",  # Check data usage (example)
  # Add more codes for your carrier
}


def main():
  import argparse

  parser = argparse.ArgumentParser(description="Send USSD code to Alcatel Modem")
  parser.add_argument("-u", "--url", default="http://192.168.1.1", help="Modem URL")
  parser.add_argument("-p", "--password", help="Admin password (required for sending USSD)")
  parser.add_argument("-c", "--code", help="USSD code (e.g., *222#)")
  parser.add_argument("-l", "--list", action="store_true", help="List available USSD codes")
  parser.add_argument("--wait", type=int, default=5, help="Wait seconds before getting result (default: 5)")

  args = parser.parse_args()

  if args.list:
    print("Available USSD codes:")
    for name, code in USSD_CODES.items():
      print(f"  {name}: {code}")
    return

  if not args.code:
    print("Error: USSD code required. Use -c <code> or --list to see examples")
    sys.exit(1)

  if not args.password:
    print("Error: Password required for sending USSD. Use -p <password>")
    sys.exit(1)

  # Initialize API
  api = AlcatelClient(args.url, args.password)

  print(f"Sending USSD code: {args.code}")
  print(f"Waiting {args.wait} seconds for response...")

  try:
    result = api.system.send_ussd_code(args.code, wait_seconds=args.wait)

    send_state = result.get("SendState", 0)
    ussd_content = result.get("UssdContent", "")

    if send_state == 2:  # Success
      print("\n✅ Response received:")
      print(ussd_content)
    elif send_state == 3:  # Error
      print("\n❌ Error occurred")
      print("Tip: Try changing Network Mode (3G or Auto) in settings")
    else:
      print(f"\n⚠️  Unknown state: {send_state}")
      if ussd_content:
        print(f"Content: {ussd_content}")

  except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()
