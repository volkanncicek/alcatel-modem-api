"""
Diagnostics utilities for modem detection and troubleshooting
"""

from typing import Union

import httpx

# Mapping of brand names to their detection keywords
# Each brand maps to a list of keywords that can appear in headers or body
BRAND_KEYWORDS = {
  "Keenetic": ["keenetic", "keeneticos"],
  "Huawei": ["huawei", "hilink"],
  "Netgear": ["netgear"],
  "TP-Link": ["tp-link", "tplink"],
  "D-Link": ["d-link", "dlink"],
  "ASUS": ["asus"],
  "Zyxel": ["zyxel"],
}


def detect_modem_brand(response: httpx.Response) -> Union[str, None]:
  """
  Detect modem brand from HTTP response headers and body

  This function analyzes HTTP response headers and body content to identify
  the modem manufacturer. This is useful for detecting unsupported modems
  and providing helpful error messages.

  Args:
      response: HTTP response object

  Returns:
      Detected brand name or None if unknown

  Examples:
      >>> import httpx
      >>> response = httpx.get("http://192.168.1.1")
      >>> brand = detect_modem_brand(response)
      >>> print(brand)  # "Huawei", "Keenetic", etc. or None
  """
  # Check all headers (case-insensitive)
  all_headers = {k.lower(): v.lower() for k, v in response.headers.items()}

  # Check Server header
  server = all_headers.get("server", "")
  for brand, keywords in BRAND_KEYWORDS.items():
    if any(keyword in server for keyword in keywords):
      return brand

  # Check X-Powered-By or other custom headers
  powered_by = all_headers.get("x-powered-by", "")
  for brand, keywords in BRAND_KEYWORDS.items():
    if any(keyword in powered_by for keyword in keywords):
      return brand

  # Check response body for brand indicators (more characters for better detection)
  try:
    body_text = response.text[:1000].lower()
    for brand, keywords in BRAND_KEYWORDS.items():
      if any(keyword in body_text for keyword in keywords):
        return brand
  except Exception:
    pass

  return None
