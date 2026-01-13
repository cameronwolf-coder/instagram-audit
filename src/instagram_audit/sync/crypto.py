"""Encryption utilities for cloud sync.

Uses AES-256-GCM with PBKDF2 key derivation.
Compatible with Web Crypto API for browser-side decryption.
"""
import base64
import hashlib
import json
import os
from typing import Any

# Use cryptography library for encryption
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# Constants matching Web Crypto API defaults
PBKDF2_ITERATIONS = 100000
SALT_LENGTH = 16
IV_LENGTH = 12  # 96 bits for GCM
KEY_LENGTH = 32  # 256 bits


def derive_key_hash(passphrase: str) -> str:
    """Derive a hash from passphrase for use as KV lookup key.

    This is NOT the encryption key - just an identifier.
    Uses SHA-256 for consistent output across Python and browser.
    """
    return hashlib.sha256(passphrase.encode('utf-8')).hexdigest()


def _derive_encryption_key(passphrase: str, salt: bytes) -> bytes:
    """Derive encryption key from passphrase using PBKDF2."""
    if not CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package required. Install with: pip install cryptography"
        )

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode('utf-8'))


def encrypt_payload(data: dict[str, Any], passphrase: str) -> dict[str, str]:
    """Encrypt a JSON payload with the given passphrase.

    Returns a dict with:
    - encrypted_data: base64-encoded ciphertext
    - salt: base64-encoded salt used for key derivation
    - iv: base64-encoded initialization vector

    The format is compatible with Web Crypto API for browser decryption.
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package required. Install with: pip install cryptography"
        )

    # Generate random salt and IV
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(IV_LENGTH)

    # Derive encryption key
    key = _derive_encryption_key(passphrase, salt)

    # Encrypt with AES-GCM
    aesgcm = AESGCM(key)
    plaintext = json.dumps(data).encode('utf-8')
    ciphertext = aesgcm.encrypt(iv, plaintext, None)

    return {
        "encrypted_data": base64.b64encode(ciphertext).decode('ascii'),
        "salt": base64.b64encode(salt).decode('ascii'),
        "iv": base64.b64encode(iv).decode('ascii'),
    }


def decrypt_payload(encrypted: dict[str, str], passphrase: str) -> dict[str, Any]:
    """Decrypt a payload encrypted with encrypt_payload.

    Args:
        encrypted: Dict with encrypted_data, salt, iv (all base64)
        passphrase: The passphrase used for encryption

    Returns:
        The decrypted JSON data as a dict
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package required. Install with: pip install cryptography"
        )

    # Decode base64
    ciphertext = base64.b64decode(encrypted["encrypted_data"])
    salt = base64.b64decode(encrypted["salt"])
    iv = base64.b64decode(encrypted["iv"])

    # Derive encryption key
    key = _derive_encryption_key(passphrase, salt)

    # Decrypt with AES-GCM
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)

    return json.loads(plaintext.decode('utf-8'))
