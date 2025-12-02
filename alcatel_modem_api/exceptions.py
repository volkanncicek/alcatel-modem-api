"""
Exception classes for Alcatel Modem API
"""


class AlcatelException(Exception):
  """Base exception for all Alcatel Modem API errors"""

  pass


class AlcatelConnectionError(AlcatelException):
  """Raised when connection to modem fails"""

  pass


class AlcatelAPIError(AlcatelException):
  """Raised when API returns an error"""

  pass


class AlcatelTimeoutError(AlcatelException):
  """Raised when request times out"""

  pass


class AuthenticationError(AlcatelException):
  """Raised when authentication fails"""

  pass


class UnsupportedModemError(AlcatelException):
  """Raised when the modem is not an Alcatel modem or doesn't support the Alcatel API"""

  pass
