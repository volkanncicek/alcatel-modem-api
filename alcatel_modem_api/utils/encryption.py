"""
Encryption utilities for Alcatel modems
Handles Alcatel's custom encryption algorithms
"""

from base64 import b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Encryption key for admin credentials (Alcatel's custom algorithm)
ENCRYPT_ADMIN_KEY = "e5dl12XYVggihggafXWf0f2YSf2Xngd1"


def encrypt_admin(value: str) -> str:
  """
  Encrypt admin credentials using Alcatel's custom algorithm

  Args:
      value: String to encrypt (username or password)

  Returns:
      Encrypted string
  """
  encoded = bytearray()
  for index, char in enumerate(value):
    value_code = ord(char)
    key_code = ord(ENCRYPT_ADMIN_KEY[index % len(ENCRYPT_ADMIN_KEY)])
    encoded.append((240 & key_code) | ((15 & value_code) ^ (15 & key_code)))
    encoded.append((240 & key_code) | ((value_code >> 4) ^ (15 & key_code)))

  return encoded.decode()


def encrypt_token(token: str, param0: str, param1: str) -> str:
  """
  Encrypt authentication token using AES/CBC/PKCS7Padding

  Args:
      token: Token from login response
      param0: Key parameter from login response
      param1: IV parameter from login response

  Returns:
      Base64 encoded encrypted token
  """
  # First, encode token using custom algorithm
  encoded_token = encrypt_admin(token).encode()

  # Then, cipher using AES/CBC/PKCS7Padding
  key = param0.encode()
  iv = param1.encode()

  cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
  encryptor = cipher.encryptor()

  # Do padding
  padder = padding.PKCS7(128).padder()
  padded_data = padder.update(encoded_token) + padder.finalize()

  # Encrypt padded data
  ciphertext = encryptor.update(padded_data) + encryptor.finalize()

  # Base64 encode
  encoded = b64encode(ciphertext).decode()

  return encoded
