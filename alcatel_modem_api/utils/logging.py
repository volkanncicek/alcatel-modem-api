"""
Logging utilities with secret sanitization
Prevents sensitive data (tokens, passwords) from appearing in logs
"""

import logging
import re


class RedactingFilter(logging.Filter):
  """
  Logging filter that redacts sensitive information from log records

  Redacts:
  - Authentication tokens (_TclRequestVerificationToken)
  - Passwords in JSON payloads
  - Passwords in headers
  """

  # Patterns to match sensitive data
  SENSITIVE_PATTERNS = [
    # Token in headers or JSON
    (r'("_TclRequestVerificationToken":\s*")[^"]+"', r'\1********"'),
    (r'("token":\s*")[^"]+"', r'\1********"'),
    # Password in JSON or params
    (r'("Password":\s*")[^"]+"', r'\1********"'),
    (r'("password":\s*")[^"]+"', r'\1********"'),
    # Password in URL params (less common but possible)
    (r'(password=)[^&\s"]+', r"\1********"),
    # Token in URL params
    (r'(token=)[^&\s"]+', r"\1********"),
  ]

  def filter(self, record: logging.LogRecord) -> bool:
    """Filter log record and redact sensitive information"""
    if hasattr(record, "msg") and record.msg:
      record.msg = self._redact(str(record.msg))

    if hasattr(record, "args") and record.args:
      # Redact sensitive data in format arguments
      record.args = tuple(self._redact(str(arg)) if isinstance(arg, str) else arg for arg in record.args)

    return True

  def _redact(self, text: str) -> str:
    """Redact sensitive patterns from text"""
    # Performance optimization: check if sensitive keywords exist before regex
    text_lower = text.lower()
    if not any(keyword in text_lower for keyword in ("token", "password")):
      return text  # No sensitive data, skip regex processing

    result = text
    for pattern, replacement in self.SENSITIVE_PATTERNS:
      result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def setup_logging(level: int = logging.WARNING) -> None:
  """
  Set up logging with redaction filter

  Args:
      level: Logging level (default: WARNING)
  """
  # Get root logger
  root_logger = logging.getLogger()
  root_logger.setLevel(level)

  # Remove existing handlers to avoid duplicates
  root_logger.handlers.clear()

  # Create console handler
  handler = logging.StreamHandler()
  handler.setLevel(level)

  # Add redacting filter
  handler.addFilter(RedactingFilter())

  # Set formatter
  formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )
  handler.setFormatter(formatter)

  root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
  """
  Get a logger with redaction filter applied

  Args:
      name: Logger name (typically __name__)

  Returns:
      Logger instance
  """
  logger = logging.getLogger(name)

  # Ensure redacting filter is applied to handlers
  for handler in logger.handlers:
    if not any(isinstance(f, RedactingFilter) for f in handler.filters):
      handler.addFilter(RedactingFilter())

  return logger
