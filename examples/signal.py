#!/usr/bin/env python3
"""
Signal Strength Monitor - Help position your Alcatel modem for best signal

This script continuously monitors signal strength and alerts you when it changes.
Useful for positioning your modem to get the best signal.

Inspired by: https://gist.github.com/lukpueh/a595f74d8edfb512d4f5be7056dfdb1e
Original author: Lukas Puehringer <luk.puehringer@gmail.com>

Enhanced with:
- Cross-platform support (Windows, Linux, macOS)
- Configurable intervals
- Quiet mode option
- Better error handling
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelClient
from alcatel_modem_api.constants import get_network_type


def say_signal_strength(strength, platform="auto"):
  """
  Announce signal strength (platform-specific)

  Args:
      strength: Signal strength value
      platform: Platform to use ('auto', 'macos', 'windows', 'linux')
  """
  if platform == "auto":
    import platform as plat

    platform = plat.system().lower()

  try:
    if platform == "darwin" or platform == "macos":
      # macOS
      import subprocess

      subprocess.run(["say", str(strength)], check=False)
    elif platform == "windows":
      # Windows - use SAPI
      import win32com.client

      speaker = win32com.client.Dispatch("SAPI.SpVoice")
      speaker.Speak(f"Signal strength {strength}")
    elif platform == "linux":
      # Linux - use espeak or festival
      import subprocess

      try:
        subprocess.run(["espeak", f"Signal strength {strength}"], check=False)
      except FileNotFoundError:
        try:
          subprocess.run(
            ["festival", "--tts"],
            input=f"Signal strength {strength}",
            text=True,
            check=False,
          )
        except FileNotFoundError:
          print("⚠️  Install 'espeak' or 'festival' for voice output on Linux")
  except Exception as e:
    print(f"⚠️  Could not announce signal: {e}")


def main():
  import argparse

  parser = argparse.ArgumentParser(
    description="Monitor Alcatel Modem Signal Strength",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Basic monitoring (print only)
  python examples/signal.py -u http://192.168.1.1

  # With voice announcements (macOS)
  python examples/signal.py -u http://192.168.1.1 --voice

  # With voice announcements (Windows)
  python examples/signal.py -u http://192.168.1.1 --voice --platform windows

  # Extended info (network type, RSSI, etc.)
  python examples/signal.py -u http://192.168.1.1 -p admin --extended

  # Custom interval
  python examples/signal.py -u http://192.168.1.1 --interval 2
        """,
  )
  parser.add_argument(
    "-u",
    "--url",
    default="http://192.168.1.1",
    help="Modem URL (default: http://192.168.1.1)",
  )
  parser.add_argument("-p", "--password", help="Admin password (optional, for extended info)")
  parser.add_argument(
    "-i",
    "--interval",
    type=int,
    default=1,
    help="Check interval in seconds (default: 1)",
  )
  parser.add_argument(
    "--voice",
    action="store_true",
    help="Announce signal strength changes with voice",
  )
  parser.add_argument(
    "--platform",
    choices=["auto", "macos", "windows", "linux"],
    default="auto",
    help="Platform for voice output (default: auto-detect)",
  )
  parser.add_argument(
    "--extended",
    action="store_true",
    help="Show extended network info (requires login)",
  )
  parser.add_argument("--quiet", action="store_true", help="Only show changes, not every check")

  args = parser.parse_args()

  # Initialize API
  api = AlcatelClient(args.url, args.password)

  print("📡 Signal Strength Monitor")
  print(f"   Modem: {args.url}")
  print(f"   Interval: {args.interval}s")
  if args.voice:
    print(f"   Voice: Enabled ({args.platform})")
  if args.extended:
    print("   Extended Info: Enabled")
  print("\nPress Ctrl+C to stop...\n")

  last_strength = None
  last_network_type = None
  last_rssi = None

  try:
    while True:
      try:
        # Get system status (no login required)
        system_status = api.system.get_status()
        strength = system_status.signal_strength
        network_type_code = system_status.network_type
        network_type = get_network_type(network_type_code)
        network_name = system_status.network_name

        # Extended info (requires login)
        rssi = None
        rsrp = None
        sinr = None
        if args.extended and args.password:
          try:
            network_info = api.network.get_info()
            rssi = network_info.rssi
            rsrp = network_info.rsrp
            sinr = network_info.sinr
          except Exception:
            pass

        # Check if anything changed (only if we have previous values)
        # Don't mark as changed on first run (last_strength is None)
        changed = False
        if last_strength is not None:
          changed = strength != last_strength or network_type != last_network_type or (rssi is not None and rssi != last_rssi)

        # Build status line
        status_line = f"Signal: {strength}/5 | Network: {network_type} ({network_name})"
        if rssi is not None:
          status_line += f" | RSSI: {rssi} dBm"
        if rsrp is not None:
          status_line += f" | RSRP: {rsrp} dBm"
        if sinr is not None:
          status_line += f" | SINR: {sinr} dB"

        # Print logic
        if args.quiet:
          # Quiet mode: only print on changes
          if changed:
            print(status_line)
            if args.voice:
              say_signal_strength(strength, args.platform)
        else:
          # Normal mode: print every interval on a new line
          # Add indicator if value changed
          change_indicator = " ⚠️ CHANGED" if changed else ""
          print(f"{status_line}{change_indicator}")

          # Voice announcement on change
          if changed and args.voice:
            say_signal_strength(strength, args.platform)

        # Update last values
        last_strength = strength
        last_network_type = network_type
        last_rssi = rssi

      except KeyboardInterrupt:
        raise
      except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.quiet:
          print("   Retrying...")

      time.sleep(args.interval)

  except KeyboardInterrupt:
    print("\n\n👋 Monitoring stopped")


if __name__ == "__main__":
  main()
