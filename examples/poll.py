#!/usr/bin/env python3
"""
Poll example - Basic and Extended status polling
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelClient


def main():
  import argparse

  parser = argparse.ArgumentParser(description="Poll modem status")
  parser.add_argument("-u", "--url", default="http://192.168.1.1", help="Modem URL")
  parser.add_argument("-p", "--password", help="Admin password (for extended status)")
  parser.add_argument("--basic", action="store_true", help="Poll basic status (no login)")
  parser.add_argument("--extended", action="store_true", help="Poll extended status (requires login)")
  parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")

  args = parser.parse_args()

  api = AlcatelClient(args.url, args.password)

  if args.extended:
    if not args.password:
      print("❌ Extended status requires password. Use -p <password>")
      sys.exit(1)

    print("📊 Polling extended status...")
    status = api.system.poll_extended_status()

    if args.pretty:
      print(json.dumps(status.model_dump(), indent=2, ensure_ascii=False))
    else:
      print(status.model_dump())

  elif args.basic:
    print("📊 Polling basic status...")
    status = api.system.poll_basic_status()

    if args.pretty:
      print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
      print(status)

  else:
    # Default: show both
    print("📊 Polling basic status (no login required)...")
    basic = api.system.poll_basic_status()
    print(json.dumps(basic, indent=2, ensure_ascii=False))
    print()

    if args.password:
      print("📊 Polling extended status (login required)...")
      extended = api.system.poll_extended_status()
      print(json.dumps(extended.model_dump(), indent=2, ensure_ascii=False))
    else:
      print("💡 Use -p <password> to get extended status")


if __name__ == "__main__":
  main()
