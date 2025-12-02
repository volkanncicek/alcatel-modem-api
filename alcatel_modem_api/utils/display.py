"""
Display utilities for CLI output
Provides reusable functions for formatting Pydantic models as tables
"""

from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

console = Console()


def print_model_as_table(model: BaseModel, title: str = "", show_header: bool = True, header_style: str = "bold magenta") -> None:
  """
  Print a Pydantic model as a formatted table

  Args:
      model: Pydantic model instance to display
      title: Optional table title
      show_header: Whether to show table header
      header_style: Style for table header
  """
  table = Table(title=title, show_header=show_header, header_style=header_style)
  table.add_column("Property", style="cyan")
  table.add_column("Value", style="green")

  for field_name, field_info in model.model_fields.items():
    value = getattr(model, field_name, None)
    if value is None:
      value = "N/A"
    elif isinstance(value, (list, dict)):
      value = str(value)
    table.add_row(field_name.replace("_", " ").title(), str(value))

  console.print(table)


def print_dict_as_table(data: dict[str, Any], title: str = "", show_header: bool = True, header_style: str = "bold magenta") -> None:
  """
  Print a dictionary as a formatted table

  Args:
      data: Dictionary to display
      title: Optional table title
      show_header: Whether to show table header
      header_style: Style for table header
  """
  table = Table(title=title, show_header=show_header, header_style=header_style)
  table.add_column("Property", style="cyan")
  table.add_column("Value", style="green")

  for key, value in data.items():
    if value is None:
      value = "N/A"
    elif isinstance(value, (list, dict)):
      value = str(value)
    table.add_row(key.replace("_", " ").title(), str(value))

  console.print(table)


def print_sms_list_as_table(messages: list[Any], title: str = "SMS Messages") -> None:
  """
  Print a list of SMS messages as a formatted table

  Args:
      messages: List of SMS message objects (dict or Pydantic models)
      title: Optional table title
  """
  table = Table(title=title, show_header=True, header_style="bold magenta")
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
