#!/usr/bin/env python3
"""
Modern command-line interface for Alcatel Modem API
Built with Typer and Rich for beautiful terminal output
"""

import json
import sys
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table
from typer import Option

from . import AlcatelClient, AuthenticationError, UnsupportedModemError
from .constants import PUBLIC_VERBS, RESTRICTED_VERBS

app = typer.Typer(
  name="alcatel",
  help="Alcatel Modem API CLI - Modern client for Alcatel LTE modems",
  add_completion=False,
)
console = Console()

# Global options
url_option = Option("http://192.168.1.1", "-u", "--url", help="Modem URL")
password_option = Option(None, "-p", "--password", help="Admin password (required for protected commands)")
pretty_option = Option(False, "--pretty", help="Pretty print JSON output")


def get_client(url: str, password: Optional[str] = None) -> AlcatelClient:
  """Create and return AlcatelClient instance"""
  return AlcatelClient(url=url, password=password)


def handle_error(e: Exception) -> None:
  """Handle errors with appropriate messages"""
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


# SMS subcommands
sms_app = typer.Typer(help="SMS operations")
app.add_typer(sms_app, name="sms")


@sms_app.command("send")
def sms_send(
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
def sms_list(
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
      # Create a table for better display
      table = Table(title="SMS Messages", show_header=True, header_style="bold magenta")
      table.add_column("ID", style="cyan")
      table.add_column("Phone Number", style="green")
      table.add_column("Content", style="yellow")
      table.add_column("Timestamp", style="blue")
      table.add_column("Read", style="magenta")

      for msg in messages:
        if isinstance(msg, dict):
          table.add_row(
            str(msg.get("sms_id", "")),
            msg.get("phone_number", ""),
            msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", ""),
            msg.get("timestamp", ""),
            "✓" if msg.get("read") else "✗",
          )
        else:
          # Handle Pydantic models
          table.add_row(
            str(msg.sms_id),
            msg.phone_number,
            msg.content[:50] + "..." if len(msg.content) > 50 else msg.content,
            msg.timestamp or "",
            "✓" if msg.read else "✗",
          )

      console.print(table)
    else:
      console.print(JSON(json.dumps([msg.model_dump() if hasattr(msg, "model_dump") else msg for msg in messages], default=str)))

  except AuthenticationError as e:
    console.print(f"[red]❌ Authentication error:[/red] {e}")
    raise typer.Exit(1)
  except Exception as e:
    handle_error(e)
    raise typer.Exit(1)


# System subcommands
system_app = typer.Typer(help="System operations")
app.add_typer(system_app, name="system")


@system_app.command("status")
def system_status(
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Get system status (no login required)"""
  try:
    client = get_client(url, password)
    status = client.system.get_status()

    if pretty:
      table = Table(title="System Status", show_header=True, header_style="bold magenta")
      table.add_column("Property", style="cyan")
      table.add_column("Value", style="green")

      table.add_row("Connection Status", str(status.connection_status))
      table.add_row("Signal Strength", str(status.signal_strength))
      table.add_row("Network Name", status.network_name or "N/A")
      table.add_row("Network Type", str(status.network_type))
      table.add_row("IMEI", status.imei or "N/A")
      table.add_row("ICCID", status.iccid or "N/A")
      table.add_row("Device", status.device or "N/A")

      console.print(table)
    else:
      console.print(JSON(json.dumps(status.model_dump(), default=str)))

  except Exception as e:
    handle_error(e)
    raise typer.Exit(1)


@system_app.command("poll-basic")
def poll_basic(
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
    handle_error(e)
    raise typer.Exit(1)


@system_app.command("poll-extended")
def poll_extended(
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
    handle_error(e)
    raise typer.Exit(1)


# Network subcommands
network_app = typer.Typer(help="Network operations")
app.add_typer(network_app, name="network")


@network_app.command("info")
def network_info(
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
):
  """Get network information (requires login)"""
  if not password:
    console.print("[red]❌ Error:[/red] Password required")
    console.print("   Use: -p <password>")
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
    handle_error(e)
    raise typer.Exit(1)


@network_app.command("connect")
def network_connect(
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
    handle_error(e)
    raise typer.Exit(1)


@network_app.command("disconnect")
def network_disconnect(
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
    handle_error(e)
    raise typer.Exit(1)


# Generic command execution
@app.command("run")
def run_command(
  command: Annotated[str, typer.Argument(help="Command to execute")],
  url: str = url_option,
  password: Optional[str] = password_option,
  pretty: bool = pretty_option,
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
    handle_error(e)
    raise typer.Exit(1)


# List commands
@app.command("list")
def list_commands(
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


def cli():
  """CLI entry point for setuptools"""
  app()


if __name__ == "__main__":
  app()