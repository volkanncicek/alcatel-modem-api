"""
Configuration management for Alcatel Modem API CLI
Stores URL and password in a config file
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from platformdirs import user_config_dir

if TYPE_CHECKING:
  import tomli
  import tomli_w
else:
  try:
    import tomli as _tomli
    import tomli_w as _tomli_w

    tomli = _tomli  # type: ignore[assignment]
    tomli_w = _tomli_w  # type: ignore[assignment]
  except ImportError:
    tomli = None  # type: ignore[assignment]
    tomli_w = None  # type: ignore[assignment]

# Use platformdirs for cross-platform config directory (XDG compliant)
CONFIG_DIR = Path(user_config_dir("alcatel-api", "Alcatel Modem API"))
CONFIG_PATH = CONFIG_DIR / "config.toml"


def load_config() -> dict[str, str]:
  """
  Load configuration from file

  Returns:
      Configuration dictionary with url and optionally password
  """
  if not CONFIG_PATH.exists():
    return {}

  if tomli is None:
    return {}

  try:
    with open(CONFIG_PATH, "rb") as f:
      config = tomli.load(f)
      return config.get("alcatel", {})  # type: ignore[no-any-return]
  except Exception:
    return {}


def save_config(url: str, password: Optional[str] = None) -> None:
  """
  Save configuration to file

  Args:
      url: Modem URL
      password: Admin password (optional, not recommended to store in plain text)
  """
  if tomli_w is None:
    raise ImportError("tomli-w is required for saving config. Install with: uv pip install tomli-w")

  # Create config directory if it doesn't exist
  CONFIG_DIR.mkdir(parents=True, exist_ok=True)

  config = {"alcatel": {"url": url}}
  if password:
    config["alcatel"]["password"] = password

  try:
    with open(CONFIG_PATH, "wb") as f:
      tomli_w.dump(config, f)
    # Set restrictive permissions (owner read/write only)
    if os.name != "nt":  # Unix-like systems
      os.chmod(CONFIG_PATH, 0o600)
  except Exception as e:
    raise RuntimeError(f"Failed to save config: {e}")


def get_config_url() -> Optional[str]:
  """Get URL from config file"""
  config = load_config()
  return config.get("url")


def get_config_password() -> Optional[str]:
  """Get password from config file"""
  config = load_config()
  return config.get("password")
