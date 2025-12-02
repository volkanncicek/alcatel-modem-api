"""
Exception classes for Alcatel Modem API
"""

from typing import Union


class AlcatelError(Exception):
  """Base exception for all Alcatel Modem API errors"""

  pass


class AlcatelConnectionError(AlcatelError):
  """Raised when connection to modem fails"""

  pass


class AlcatelAPIError(AlcatelError):
  """Raised when API returns an error"""

  def __init__(self, message: str, error_code: Union[int, str, None] = None):
    """
    Initialize API error

    Args:
        message: Error message
        error_code: Optional error code from modem
    """
    super().__init__(message)
    self.error_code = error_code


class AlcatelTimeoutError(AlcatelError):
  """Raised when request times out"""

  pass


class AuthenticationError(AlcatelError):
  """Raised when authentication fails"""

  pass


class UnsupportedModemError(AlcatelError):
  """Raised when the modem is not an Alcatel modem or doesn't support the Alcatel API"""

  pass


class AlcatelSystemBusyError(AlcatelAPIError):
  """Raised when modem system is busy"""

  pass


class AlcatelSimMissingError(AlcatelAPIError):
  """Raised when SIM card is missing or not detected"""

  pass


class AlcatelFeatureNotSupportedError(AlcatelAPIError):
  """Raised when a feature is not supported on this modem model/firmware"""

  pass
