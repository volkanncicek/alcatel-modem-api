#!/usr/bin/env python3
"""
SMS Helper - Send SMS and wait for response
Utility functions for SMS operations
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelModemAPI, SMSManager


def wait_for_sms_response(api, sender_number="2222", timeout=60, check_interval=2):
  """
  Wait for SMS from a specific number

  Args:
      api: AlcatelModemAPI instance
      sender_number: Sender phone number (e.g., "2222")
      timeout: Maximum wait time in seconds
      check_interval: Check interval in seconds
  """
  print(f"📱 Waiting for SMS from {sender_number}...")
  print(f"⏱️  Maximum wait time: {timeout} seconds")
  print()

  sms = SMSManager(api)
  start_time = time.time()
  last_count = 0

  while time.time() - start_time < timeout:
    try:
      storage = sms.get_sms_storage_state()
      unread_count = storage.get("UnreadSMSCount", 0)

      if unread_count > last_count:
        print(f"✅ New SMS detected! (Unread: {unread_count})")
        print("   Checking SMS list...")
        # TODO: Get SMS list and find the new SMS
        break

      elapsed = int(time.time() - start_time)
      if elapsed % 10 == 0:  # Show status every 10 seconds
        print(f"⏳ Waiting... ({elapsed}/{timeout} seconds)")

      time.sleep(check_interval)

    except Exception as e:
      print(f"⚠️  Error during check: {e}")
      time.sleep(check_interval)

  if time.time() - start_time >= timeout:
    print("⏱️  Timeout! SMS not received.")
  else:
    print("✅ SMS received!")


def send_and_wait(api, phone_number, message, sender_number=None, timeout=60):
  """
  Send SMS and wait for response

  Args:
      api: AlcatelModemAPI instance
      phone_number: Recipient phone number
      message: Message text
      sender_number: Expected sender number (if None, waits for phone_number)
      timeout: Maximum wait time in seconds
  """
  sms = SMSManager(api)

  print("📤 Sending SMS...")
  print(f"   Recipient: {phone_number}")
  print(f"   Message: {message}")
  print()

  try:
    sms.send_sms(phone_number, message)
    print("✅ SMS sent!")
    print()

    if sender_number:
      wait_for_sms_response(api, sender_number, timeout)
    else:
      wait_for_sms_response(api, phone_number, timeout)

  except Exception as e:
    print(f"❌ Error: {e}")


def main():
  import argparse

  parser = argparse.ArgumentParser(description="SMS Helper Utilities")
  parser.add_argument("-u", "--url", default="http://192.168.1.1", help="Modem URL")
  parser.add_argument("-p", "--password", required=True, help="Admin password")
  parser.add_argument("--send", action="store_true", help="Send SMS")
  parser.add_argument("--wait", action="store_true", help="Wait for SMS")
  parser.add_argument("--phone", help="Phone number")
  parser.add_argument("--message", help="Message text")
  parser.add_argument("--sender", help="Expected sender number")
  parser.add_argument("--timeout", type=int, default=60, help="Wait time in seconds")

  args = parser.parse_args()

  api = AlcatelModemAPI(args.url, args.password)

  if args.send:
    if not args.phone or not args.message:
      print("❌ --phone and --message are required for sending SMS")
      sys.exit(1)

    send_and_wait(api, args.phone, args.message, args.sender, args.timeout)

  elif args.wait:
    sender = args.sender or args.phone or "2222"
    wait_for_sms_response(api, sender, args.timeout)

  else:
    parser.print_help()


if __name__ == "__main__":
  main()
