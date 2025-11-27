#!/usr/bin/env python3
"""
Command-line interface for Alcatel Modem API
"""

import argparse
import sys

from . import AlcatelModemAPI, AuthenticationError, SMSManager


def print_available_commands():
  """Print list of available commands"""
  from .constants import PUBLIC_VERBS, RESTRICTED_VERBS

  print("Commands that don't require login:")
  for verb in PUBLIC_VERBS:
    print(f"  {verb}")
  print()
  print("Commands that require login (use -p password):")
  for verb in RESTRICTED_VERBS[:20]:  # İlk 20'yi göster
    print(f"  {verb}")
  print(f"  ... and {len(RESTRICTED_VERBS) - 20} more")
  print()
  print("Special commands:")
  print("  poll_basic - Get basic status (no login)")
  print("  poll_extended - Get extended status (requires login)")
  print()
  print("Use '--list-all' to see all available commands")


def main():
  parser = argparse.ArgumentParser(
    description="Alcatel Modem API CLI - Generic client for Alcatel LTE modems",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )

  parser.add_argument(
    "-u",
    "--url",
    default="http://192.168.1.1",
    help="Modem URL (default: http://192.168.1.1)",
  )

  parser.add_argument("-p", "--password", help="Admin password (required for protected commands)")

  parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")

  parser.add_argument("-l", "--list", action="store_true", help="List available commands")

  parser.add_argument("--list-all", action="store_true", help="List all available commands")

  # Create subparsers for commands
  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  # SMS subparser
  sms_parser = subparsers.add_parser("sms", help="SMS operations")
  sms_subparsers = sms_parser.add_subparsers(dest="sms_action", help="SMS actions")

  # SMS send command
  sms_send = sms_subparsers.add_parser("send", help="Send SMS message")
  sms_send.add_argument("-n", "--number", required=True, help="Phone number to send SMS to")
  sms_send.add_argument("-m", "--message", required=True, help="SMS message text")

  # Regular command parser (for backward compatibility)
  parser.add_argument("-c", "--command", help="Command to execute (legacy format)")

  args = parser.parse_args()

  # Handle list commands
  if args.list:
    print_available_commands()
    return

  if args.list_all:
    from .constants import PUBLIC_VERBS, RESTRICTED_VERBS

    print("=" * 60)
    print("ALL AVAILABLE COMMANDS")
    print("=" * 60)
    print(f"\nPublic Commands ({len(PUBLIC_VERBS)}):")
    for verb in PUBLIC_VERBS:
      print(f"  {verb}")
    print(f"\nRestricted Commands ({len(RESTRICTED_VERBS)}):")
    for verb in RESTRICTED_VERBS:
      print(f"  {verb}")
    print(f"\nTotal: {len(PUBLIC_VERBS) + len(RESTRICTED_VERBS)} commands")
    return

  # Handle SMS subcommand
  if args.command == "sms":
    if not hasattr(args, "sms_action") or not args.sms_action:
      sms_parser.print_help()
      return

    if not args.password:
      print("❌ Error: Password required for SMS operations")
      print("   Use: -p <password>")
      sys.exit(1)

    api = AlcatelModemAPI(args.url, args.password)
    sms = SMSManager(api)

    if args.sms_action == "send":
      # number and message are required by argparse, so they should exist
      try:
        sms.send_sms(args.number, args.message)
        print(f"✅ SMS sent successfully to {args.number}")
      except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)
      except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        sys.exit(1)
    return

  # Handle legacy SMS format (backward compatibility)
  if args.command and args.command.startswith("sms:"):
    parts = args.command.split(":", 2)
    if len(parts) == 3 and parts[1] == "send":
      if not args.password:
        print("❌ Error: Password required for SMS operations")
        print("   Use: -p <password>")
        sys.exit(1)
      print("❌ Error: Legacy SMS format is deprecated. Use: sms send -n <number> -m <message>")
      sys.exit(1)

  # Handle special poll commands
  if args.command in ["poll_basic_status", "pollBasic", "poll_basic"]:
    api = AlcatelModemAPI(args.url)
    status = api.poll_basic_status()
    if args.pretty:
      import json

      print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
      print(status)
    return

  if args.command in [
    "poll_extended_status",
    "pollExtended",
    "poll_extended",
    "poll",
  ]:
    if not args.password:
      print("❌ Extended status requires password. Use -p <password>")
      sys.exit(1)
    api = AlcatelModemAPI(args.url, args.password)
    status = api.poll_extended_status()
    if args.pretty:
      import json

      print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
      print(status)
    return

  # Handle regular command
  if not args.command:
    parser.print_help()
    return

  api = AlcatelModemAPI(args.url, args.password)

  try:
    if args.pretty:
      result = api.run_pretty(args.command)
      print(result)
    else:
      result = api.run(args.command)
      print(result)
  except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
    print("   Tip: Use -p <password> to provide admin password")
    sys.exit(1)
  except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


def cli():
  """CLI entry point for setuptools"""
  main()


if __name__ == "__main__":
  main()
