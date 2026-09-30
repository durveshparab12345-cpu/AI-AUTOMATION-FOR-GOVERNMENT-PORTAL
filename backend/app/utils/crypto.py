"""
Cryptographic utilities for encryption and hashing.

This module provides functions for encrypting sensitive data (credentials, PII)
and hashing passwords securely.
"""

import hashlib
import hmac
import base64
import secrets
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.password import PBKDF2
from datetime import datetime, timedelta


def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2.

    Args:
        password: Password to hash
        salt: Optional salt; generated if not provided

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)  # 64-char hex string (32 bytes)
    
    # Use PBKDF2 with 100,000 iterations (NIST recommended minimum)
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode() if isinstance(salt, str) else salt,
        iterations=100000,
        backend=default_backend()
    )
    
    derived_key = kdf.derive(password.encode())
    hashed = base64.b64encode(derived_key).decode('utf-8')
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str = None) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Password to verify
        hashed_password: Previously hashed password
        salt: Salt used in hashing

    Returns:
        True if password matches, False otherwise
    """
    if salt is None:
        return False
    
    try:
        new_hash, _ = hash_password(password, salt)
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(new_hash, hashed_password)
    except Exception:
        return False


def encrypt_string(plaintext: str, key: str = None) -> str:
    """
    Encrypt a string using AES-256-GCM.

    Args:
        plaintext: String to encrypt
        key: Encryption key (32 bytes for AES-256); uses ENV if not provided

    Returns:
        Base64-encoded ciphertext with IV and tag
    """
    if key is None:
        key = os.environ.get('ENCRYPTION_KEY', secrets.token_hex(32))
    
    # Ensure key is 32 bytes
    if isinstance(key, str):
        key_bytes = base64.b64decode(key) if len(key) == 44 else key.encode()
    else:
        key_bytes = key
    
    if len(key_bytes) != 32:
        raise ValueError("Encryption key must be 32 bytes for AES-256")
    
    # Generate random IV (12 bytes for GCM)
    iv = secrets.token_bytes(12)
    
    # Encrypt
    cipher = AESGCM(key_bytes)
    ciphertext = cipher.encrypt(iv, plaintext.encode(), None)
    
    # Combine IV + ciphertext and encode
    combined = iv + ciphertext
    return base64.b64encode(combined).decode('utf-8')


def decrypt_string(ciphertext: str, key: str = None) -> str:
    """
    Decrypt a string encrypted with AES-256-GCM.

    Args:
        ciphertext: Base64-encoded ciphertext with IV and tag
        key: Encryption key (must match encryption key)

    Returns:
        Decrypted plaintext

    Raises:
        ValueError: If decryption fails or authentication fails
    """
    if key is None:
        key = os.environ.get('ENCRYPTION_KEY', None)
        if key is None:
            raise ValueError("No encryption key provided")
    
    # Ensure key is 32 bytes
    if isinstance(key, str):
        key_bytes = base64.b64decode(key) if len(key) == 44 else key.encode()
    else:
        key_bytes = key
    
    if len(key_bytes) != 32:
        raise ValueError("Encryption key must be 32 bytes for AES-256")
    
    try:
        # Decode and extract
        combined = base64.b64decode(ciphertext)
        iv = combined[:12]
        encrypted_data = combined[12:]
        
        # Decrypt
        cipher = AESGCM(key_bytes)
        plaintext = cipher.decrypt(iv, encrypted_data, None)
        
        return plaintext.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def generate_hmac(data: str, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature.

    Args:
        data: Data to sign
        secret: Secret key

    Returns:
        Base64-encoded HMAC signature
    """
    if isinstance(data, str):
        data = data.encode()
    if isinstance(secret, str):
        secret = secret.encode()
    
    signature = hmac.new(secret, data, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')


def verify_hmac(data: str, signature: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature.

    Args:
        data: Data that was signed
        signature: HMAC signature to verify
        secret: Secret key (must match signing key)

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        expected_sig = generate_hmac(data, secret)
        return hmac.compare_digest(expected_sig, signature)
    except Exception:
        return False


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """
    Hash data using specified algorithm.

    Args:
        data: Data to hash
        algorithm: Hash algorithm (sha256, sha512, etc.)

    Returns:
        Hex-encoded hash
    """
    if isinstance(data, str):
        data = data.encode()
    
    if algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def generate_random_token(length: int = 32) -> str:
    """
    Generate a random token for temporary use.

    Args:
        length: Length of token in bytes

    Returns:
        Base64-encoded random token
    """
    random_bytes = secrets.token_bytes(length)
    return base64.b64encode(random_bytes).decode('utf-8')


def obfuscate_pii(value: str, start_chars: int = 2, end_chars: int = 2) -> str:
    """
    Obfuscate personally identifiable information.

    Shows only first and last few characters, masks the rest.

    Args:
        value: PII value to obfuscate
        start_chars: Number of characters to show at start
        end_chars: Number of characters to show at end

    Returns:
        Obfuscated string

    Example:
        obfuscate_pii("9876543210") -> "98****3210"
    """
    if len(value) <= start_chars + end_chars:
        return value

    mask_length = len(value) - start_chars - end_chars
    masked = "*" * mask_length

    return value[:start_chars] + masked + value[-end_chars:]


class EncryptionKeyManager:
    """
    Manager for encryption keys.

    Handles key rotation, secure key storage, and key derivation.
    """

    def __init__(self, master_key: str):
        """
        Initialize key manager.

        Args:
            master_key: Master encryption key
        """
        self.master_key = master_key
        self.key_versions: dict = {}
        self.current_version = 1
        self.created_at = datetime.utcnow()

    def derive_key(self, key_id: str, context: str) -> str:
        """
        Derive a key from master key using context.

        Args:
            key_id: Identifier for this key
            context: Context for key derivation

        Returns:
            Derived key
        """
        if isinstance(self.master_key, str):
            master_key_bytes = base64.b64decode(self.master_key) if len(self.master_key) == 44 else self.master_key.encode()
        else:
            master_key_bytes = self.master_key
        
        # Use HKDF to derive key
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=key_id.encode(),
            info=context.encode(),
            backend=default_backend()
        )
        
        derived = hkdf.derive(master_key_bytes)
        return base64.b64encode(derived).decode('utf-8')

    def rotate_key(self, new_master_key: str) -> None:
        """
        Rotate the master key.

        Args:
            new_master_key: New master key
        """
        # Store old key version for decryption of old data
        self.key_versions[self.current_version] = {
            'key': self.master_key,
            'created_at': self.created_at,
            'rotated_at': datetime.utcnow()
        }
        
        # Update to new key
        self.master_key = new_master_key
        self.current_version += 1
        self.created_at = datetime.utcnow()

    def get_current_key_version(self) -> int:
        """
        Get current key version number.

        Returns:
            Current key version
        """
        return self.current_version
