#!/usr/bin/env python3
"""
Modern command-line interface for Alcatel Modem API
Built with Typer and Rich for beautiful terminal output
"""

import asyncio
import json
import sys
from typing import Annotated, Any, Optional

import typer
from rich.align import Align
from rich.console import Console
from rich.json import JSON
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from typer import Option

from . import AlcatelClient, AuthenticationError, UnsupportedModemError
from .config import get_config_password, get_config_url, load_config, save_config
from .constants import PUBLIC_VERBS, RESTRICTED_VERBS, get_network_type
from .utils.diagnostics_models import DiagnosticReport
from .utils.display import print_model_as_table, print_sms_list_as_table

app = typer.Typer(
  name="alcatel",
  help="Alcatel Modem API CLI - Modern client for Alcatel LTE modems",
  add_completion=False,
)
console = Console()

# Global options
url_option = Option(None, "-u", "--url", help="Modem URL (defaults to config or http://192.168.1.1)")
password_option = Option(None, "-p", "--password", help="Admin password (required for protected commands)")
pretty_option = Option(False, "--pretty", help="Pretty print JSON output")
debug_option = Option(False, "--debug", help="Show full traceback for errors")


def get_client(url: Optional[str] = None, password: Optional[str] = None) -> AlcatelClient:
  """Create and return AlcatelClient instance"""
  # Use config values if not provided
  if url is None:
    url = get_config_url() or "http://192.168.1.1"
  if password is None:
    password = get_config_password()
  return AlcatelClient(url=url, password=password)


def handle_error(e: Exception, debug: bool = False) -> None:
  """Handle errors with appropriate messages"""
  if debug:
    console.print_exception()
    return

  if isinstance(e, UnsupportedModemError):
    console.print("[red]❌ Unsupported Modem:[/red]")
    console.print(f"   {e}")
    console.print()
    console.print("[yellow]💡 Tip:[/yellow] This library only works with Alcatel modems.")
    console.print("   Supported models: MW40V1, HH72, HH40V, HH70VB, IK40V, etc.")
  elif isinstance(e, AuthenticationError):
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    console.print("   Tip: Use -p <password> to provide admin password")
  else:
    console.print(f"[red]❌ Error:[/red] {e}")
    console.print("   Tip: Use --debug to see full traceback")


# SMS subcommands
sms_app = typer.Typer(help="SMS operations")
app.add_typer(sms_app, name="sms")


@sms_app.command("send")
def sms_send(  # type: ignore[no-untyped-def]
  number: Annotated[str, typer.Option("-n", "--number", help="Phone number")],
  message: Annotated[str, typer.Option("-m", "--message", help="SMS message text")],
  url: str = url_option,
  password: Optional[str] = password_option,
):
  """Send SMS message"""
  if not password:
    console.print("[red]❌ Error:[/red] Password required for SMS operations")
    console.print("   Use: -p <password>")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    client.sms.send(number, message)
    console.print(f"[green]✅ SMS sent successfully to {number}[/green]")
  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    console.print(f"[red]❌ Error sending SMS:[/red] {e}")
    raise typer.Exit(1)


@sms_app.command("list")
def sms_list(  # type: ignore[no-untyped-def]
  contact: Annotated[Optional[str], typer.Option("-c", "--contact", help="Filter by contact number")] = None,
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """List SMS messages"""
  if not password:
    console.print("[red]❌ Error:[/red] Password required for SMS operations")
    console.print("   Use: -p <password>")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    messages = client.sms.list(contact_number=contact)

    if pretty:
      print_sms_list_as_table(messages)
    else:
      console.print(JSON(json.dumps([msg.model_dump() if hasattr(msg, "model_dump") else msg for msg in messages], default=str)))

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


# System subcommands
system_app = typer.Typer(help="System operations")
app.add_typer(system_app, name="system")


@system_app.command("status")
def system_status(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Get system status (no login required)"""
  try:
    client = get_client(url, password)
    status = client.system.get_status()

    if pretty:
      print_model_as_table(status, title="System Status")
    else:
      console.print(JSON(json.dumps(status.model_dump(), default=str)))

  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


@system_app.command("poll-basic")
def poll_basic(  # type: ignore[no-untyped-def]
  url: str = url_option,
  pretty: bool = pretty_option,
):
  """Poll basic status (no login required)"""
  try:
    client = get_client(url)
    status = client.system.poll_basic_status()

    if pretty:
      console.print(JSON(json.dumps(status, indent=2, ensure_ascii=False)))
    else:
      console.print(status)

  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


@system_app.command("poll-extended")
def poll_extended(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Poll extended status (requires login)"""
  if not password:
    console.print("[red]❌ Extended status requires password. Use -p <password>[/red]")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    status = client.system.poll_extended_status()

    if pretty:
      console.print(JSON(json.dumps(status.model_dump(), default=str, indent=2)))
    else:
      console.print(status.model_dump())

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


@system_app.command("monitor")
def system_monitor(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
  interval: float = typer.Option(1.0, help="Update interval in seconds"),
):
  """Live dashboard for signal and traffic monitoring"""
  if not password:
    console.print("[red]❌ Monitor requires password. Use -p <password>[/red]")
    raise typer.Exit(1)

  async def monitor_async() -> None:
    """Async monitor loop to prevent UI freezing"""
    try:
      client = get_client(url, password)

      def generate_layout(status: Any) -> Layout:
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body", ratio=1))
        layout["body"].split_row(Layout(name="signal"), Layout(name="traffic"))

        # Header
        net_type = get_network_type(status.network_type)
        header_text = Text(f"Connected to {status.network_name or 'Unknown'} ({net_type})", style="bold white")
        layout["header"].update(Panel(Align.center(header_text), style="blue"))

        # Signal Panel
        signal_color = "green" if status.strength >= 4 else "yellow" if status.strength >= 2 else "red"
        signal_text = Text()
        signal_text.append(f"Strength : {'█' * status.strength}{'░' * (5 - status.strength)}\n", style=signal_color)
        signal_text.append(f"RSSI     : {status.rssi or 'N/A'} dBm\n")
        signal_text.append(f"RSRP     : {status.rsrp or 'N/A'} dBm\n")
        signal_text.append(f"SINR     : {status.sinr or 'N/A'} dB\n")
        layout["signal"].update(Panel(signal_text, title="Signal Quality", border_style=signal_color))

        # Traffic Panel
        traffic_text = Text()
        traffic_text.append(f"Download : {status.bytes_in_rate / 1024 / 1024:.2f} MB/s\n", style="green")
        traffic_text.append(f"Upload   : {status.bytes_out_rate / 1024 / 1024:.2f} MB/s\n", style="blue")
        traffic_text.append(f"Total DL : {status.bytes_in / 1024 / 1024 / 1024:.2f} GB\n")
        traffic_text.append(f"Total UL : {status.bytes_out / 1024 / 1024 / 1024:.2f} GB")
        layout["traffic"].update(Panel(traffic_text, title="Traffic", border_style="white"))

        return layout

      with Live(console=console, screen=True, refresh_per_second=4) as live:
        while True:
          # Use async method to prevent blocking
          status = await client.system.poll_extended_status_async()
          live.update(generate_layout(status))
          await asyncio.sleep(interval)

    except AuthenticationError as e:
      console.print(f"[red]❌ Authentication error:[/red] {e}")
      raise typer.Exit(1)
    except KeyboardInterrupt:
      console.print("Stopped.")
      raise typer.Exit(0)
    except Exception as e:
      handle_error(e, debug=False)
      raise typer.Exit(1)

  # Run async monitor
  try:
    asyncio.run(monitor_async())
  except KeyboardInterrupt:
    console.print("Stopped.")
    raise typer.Exit(0)


# Network subcommands
network_app = typer.Typer(help="Network operations")
app.add_typer(network_app, name="network")


@network_app.command("info")
def network_info(  # type: ignore[no-untyped-def]
  url: Optional[str] = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
  debug: bool = debug_option,
):
  """Get network information (requires login)"""
  if not password:
    password = get_config_password()
  if not password:
    console.print("[red]❌ Error:[/red] Password required")
    console.print("   Use: -p <password> or configure with: alcatel configure -p <password>")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    info = client.network.get_info()

    if pretty:
      console.print(JSON(json.dumps(info.model_dump(), default=str, indent=2)))
    else:
      console.print(info.model_dump())

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=debug)
    raise typer.Exit(1)


@network_app.command("connect")
def network_connect(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Connect to network (requires login)"""
  if not password:
    console.print("[red]❌ Error:[/red] Password required")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    result = client.network.connect()
    console.print("[green]✅ Connection initiated[/green]")
    if pretty:
      console.print(JSON(json.dumps(result, indent=2)))

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


@network_app.command("disconnect")
def network_disconnect(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Disconnect from network (requires login)"""
  if not password:
    console.print("[red]❌ Error:[/red] Password required")
    raise typer.Exit(1)

  try:
    client = get_client(url, password)
    result = client.network.disconnect()
    console.print("[green]✅ Disconnection initiated[/green]")
    if pretty:
      console.print(JSON(json.dumps(result, indent=2)))

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=False)
    raise typer.Exit(1)


# Generic command execution
@app.command("run")
def run_command(  # type: ignore[no-untyped-def]
  command: Annotated[str, typer.Argument(help="Command to execute")],
  url: Optional[str] = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
  debug: bool = debug_option,
):
  """Execute a raw API command"""
  try:
    client = get_client(url, password)
    result = client.run(command)

    if pretty:
      console.print(JSON(json.dumps(result, indent=2, ensure_ascii=False)))
    else:
      console.print(result)

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    console.print("   Tip: Use -p <password> to provide admin password")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e, debug=debug)
    raise typer.Exit(1)


# Configuration command
@app.command("configure")
def configure(  # type: ignore[no-untyped-def]
  url: Annotated[Optional[str], typer.Option("-u", "--url", help="Modem URL")] = None,
  password: Annotated[Optional[str], typer.Option("-p", "--password", help="Admin password (optional)")] = None,
  save_password_unsafe: Annotated[bool, typer.Option("--save-password-unsafe", help="Save password to config file (not recommended)")] = False,
):
  """Configure default URL and password"""
  try:
    if url is None and password is None:
      # Show current config
      config = load_config()
      if config:
        console.print("[cyan]Current configuration:[/cyan]")
        console.print(f"  URL: {config.get('url', 'Not set')}")
        if "password" in config:
          console.print("  Password: [yellow]Set (hidden)[/yellow]")
        else:
          console.print("  Password: [yellow]Not set[/yellow]")
      else:
        console.print("[yellow]No configuration found.[/yellow]")
        console.print("  Use: alcatel configure -u <url> [--save-password-unsafe -p <password>]")
      return

    if url is None:
      url = get_config_url() or "http://192.168.1.1"

    # Only save password if explicitly requested with --save-password-unsafe flag
    password_to_save = password if save_password_unsafe else None

    save_config(url, password_to_save)
    console.print("[green]✅ Configuration saved[/green]")
    console.print(f"  URL: {url}")
    if password_to_save:
      console.print("[yellow]⚠️  Password saved to config file (not recommended for production)[/yellow]")
      console.print("  Consider using environment variables or passing password via CLI instead")
    elif password:
      console.print("[yellow]Password provided but not saved (use --save-password-unsafe to save)[/yellow]")
      console.print("  Password will be used for this session only")
    else:
      console.print("  Password: [yellow]Not saved (use --save-password-unsafe -p <password> to save)[/yellow]")

  except ImportError as e:
    console.print(f"[red]❌ Error:[/red] {e}")
    console.print("   Install tomli-w: uv pip install tomli-w")
    raise typer.Exit(1)
  except Exception as e:
    console.print(f"[red]❌ Error:[/red] {e}")
    raise typer.Exit(1)


# Doctor command for diagnostics
@app.command("doctor")
def doctor(  # type: ignore[no-untyped-def]
  url: str = url_option,
  password: Optional[str] = password_option,
):
  """Run diagnostics and generate support report"""
  console.print("[bold cyan]🔍 Alcatel Modem API Diagnostics[/bold cyan]")
  console.print("=" * 60)
  console.print()

  # Initialize diagnostic report with Pydantic model for automatic masking
  diagnostics = DiagnosticReport(
    library_version="1.0.0",  # TODO: Get from __version__
    python_version=sys.version.split()[0],
    connection={},
    modem_info={},
    api_endpoints={},
    errors=[],
  )

  # Use config values if not provided
  if url is None:
    url = get_config_url() or "http://192.168.1.1"
  if password is None:
    password = get_config_password()

  diagnostics.connection["url"] = url
  diagnostics.connection["password_provided"] = password is not None

  try:
    console.print("[cyan]Testing connection...[/cyan]")
    client = get_client(url, password)

    # Test basic connection
    try:
      system_info = client.system.get_info()
      status = client.system.get_status()
      diagnostics.connection["status"] = "✅ Connected"
      diagnostics.modem_info["model"] = system_info.get("DeviceName", status.device or "Unknown")
      diagnostics.modem_info["firmware"] = system_info.get("SoftwareVersion", "Unknown")
      diagnostics.modem_info["hardware"] = system_info.get("HardwareVersion", "Unknown")
      console.print("  [green]✅ Connected to modem[/green]")
      console.print(f"  Model: {diagnostics.modem_info['model']}")
      console.print(f"  Firmware: {diagnostics.modem_info['firmware']}")
      diagnostics.api_endpoints["/jrd/webapi"] = "✅ Accessible"
    except Exception as e:
      diagnostics.connection["status"] = f"❌ Failed: {str(e)}"
      diagnostics.errors.append(f"Connection test failed: {str(e)}")
      diagnostics.api_endpoints["/jrd/webapi"] = f"❌ Failed: {str(e)}"
      console.print(f"  [red]❌ Connection failed: {e}[/red]")

    # Test authentication if password provided
    if password:
      console.print()
      console.print("[cyan]Testing authentication...[/cyan]")
      try:
        login_state = client._get_login_state()
        if login_state:
          diagnostics.api_endpoints["authentication"] = "✅ Authenticated"
          console.print("  [green]✅ Authentication successful[/green]")
        else:
          try:
            client._login()
            diagnostics.api_endpoints["authentication"] = "✅ Login successful"
            console.print("  [green]✅ Login successful[/green]")
          except Exception as e:
            diagnostics.api_endpoints["authentication"] = f"❌ Failed: {str(e)}"
            diagnostics.errors.append(f"Authentication failed: {str(e)}")
            console.print(f"  [red]❌ Authentication failed: {e}[/red]")
      except Exception as e:
        diagnostics.api_endpoints["authentication"] = f"❌ Error: {str(e)}"
        diagnostics.errors.append(f"Authentication test error: {str(e)}")
        console.print(f"  [yellow]⚠️  Authentication test error: {e}[/yellow]")

    # Test keyring availability
    console.print()
    console.print("[cyan]Checking security features...[/cyan]")
    try:
      from .utils.keyring_storage import KEYRING_AVAILABLE

      if KEYRING_AVAILABLE:
        diagnostics.security = {"keyring": "✅ Available"}
        console.print("  [green]✅ System keyring available[/green]")
      else:
        diagnostics.security = {"keyring": "⚠️  Not available (using file storage)"}
        console.print("  [yellow]⚠️  System keyring not available (using file storage)[/yellow]")
    except Exception:
      diagnostics.security = {"keyring": "❌ Not available"}
      console.print("  [yellow]⚠️  System keyring not available[/yellow]")

  except Exception as e:
    diagnostics.errors.append(f"Diagnostics failed: {str(e)}")
    console.print(f"  [red]❌ Diagnostics error: {e}[/red]")

  # Generate report using Pydantic model's safe serialization
  console.print()
  console.print("[bold cyan]📋 Diagnostic Report[/bold cyan]")
  console.print("=" * 60)

  # Use Pydantic model's safe dump which automatically masks sensitive fields
  import json

  report_dict = diagnostics.model_dump_safe()
  report_json = json.dumps(report_dict, indent=2, ensure_ascii=False)

  console.print()
  console.print("[yellow]Copy the following for GitHub issues:[/yellow]")
  console.print()
  console.print("```json")
  console.print(report_json)
  console.print("```")
  console.print()

  if diagnostics.errors:
    console.print("[red]⚠️  Issues detected. Please include this report when opening an issue.[/red]")
  else:
    console.print("[green]✅ All checks passed![/green]")


# List commands
@app.command("list")
def list_commands(  # type: ignore[no-untyped-def]
  all_commands: Annotated[bool, typer.Option("--all", help="Show all commands")] = False,
):
  """List available commands"""
  if all_commands:
    console.print("[bold]ALL AVAILABLE COMMANDS[/bold]")
    console.print("=" * 60)
    console.print(f"\n[cyan]Public Commands ({len(PUBLIC_VERBS)}):[/cyan]")
    for verb in PUBLIC_VERBS:
      console.print(f"  {verb}")
    console.print(f"\n[yellow]Restricted Commands ({len(RESTRICTED_VERBS)}):[/yellow]")
    for verb in RESTRICTED_VERBS:
      console.print(f"  {verb}")
    console.print(f"\n[green]Total: {len(PUBLIC_VERBS) + len(RESTRICTED_VERBS)} commands[/green]")
  else:
    console.print("[cyan]Commands that don't require login:[/cyan]")
    for verb in PUBLIC_VERBS:
      console.print(f"  {verb}")
    console.print()
    console.print("[yellow]Commands that require login (use -p password):[/yellow]")
    for verb in RESTRICTED_VERBS[:20]:
      console.print(f"  {verb}")
    console.print(f"  ... and {len(RESTRICTED_VERBS) - 20} more")
    console.print()
    console.print("[green]Special commands:[/green]")
    console.print("  system poll-basic - Get basic status (no login)")
    console.print("  system poll-extended - Get extended status (requires login)")
    console.print()
    console.print("Use '--all' to see all available commands")


def cli() -> None:
  """CLI entry point for setuptools"""
  app()


if __name__ == "__main__":
  app()
