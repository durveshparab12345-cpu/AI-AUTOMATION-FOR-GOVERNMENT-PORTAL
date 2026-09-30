"""
Security utilities: JWT, password hashing, encryption.

Handles:
- JWT token creation and verification
- Password hashing with bcrypt
- Credential encryption/decryption (AES-256-GCM)
- Token validation and revocation
"""

from __future__ import annotations

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings

# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================


def create_access_token(
    subject: str,
    extra: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The subject of the token (typically user_id or email)
        extra: Additional claims to include in the token
        expires_delta: Custom expiration time (default from settings)

    Returns:
        Signed JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "iss": settings.APP_NAME,
        "aud": settings.APP_NAME,
        **(extra or {}),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token claims or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def decode_token_unsafe(token: str) -> dict[str, Any] | None:
    """
    Decode a token without verifying signature (for inspection only).

    WARNING: Only use for non-security-critical purposes like debugging.
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
        )
        return payload
    except JWTError:
        return None


# ============================================================================
# ENCRYPTION & DECRYPTION (AES-256-GCM)
# ============================================================================

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    import base64

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


def generate_encryption_key() -> bytes:
    """Generate a random 32-byte key for AES-256."""
    return secrets.token_bytes(32)


def encrypt_credential(plaintext: str, key: bytes | None = None) -> str:
    """
    Encrypt a credential using AES-256-GCM.

    Args:
        plaintext: The credential to encrypt
        key: Encryption key (if None, uses settings SECRET_KEY)

    Returns:
        Base64-encoded ciphertext with nonce prepended
    """
    if not ENCRYPTION_AVAILABLE:
        raise RuntimeError("Encryption not available: install cryptography")

    if key is None:
        # Derive key from SECRET_KEY
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()

    nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)

    # Combine nonce + ciphertext and base64 encode
    encrypted = base64.b64encode(nonce + ciphertext).decode()
    return encrypted


def decrypt_credential(encrypted: str, key: bytes | None = None) -> str:
    """
    Decrypt a credential using AES-256-GCM.

    Args:
        encrypted: Base64-encoded ciphertext from encrypt_credential()
        key: Encryption key (if None, uses settings SECRET_KEY)

    Returns:
        Decrypted plaintext

    Raises:
        ValueError: If decryption fails (wrong key or corrupted data)
    """
    if not ENCRYPTION_AVAILABLE:
        raise RuntimeError("Encryption not available: install cryptography")

    if key is None:
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()

    try:
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted)

        # Extract nonce (first 12 bytes) and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)

        return plaintext.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


# ============================================================================
# TOKEN BLACKLIST / REVOCATION (placeholder for Redis integration)
# ============================================================================

# In production, these would use Redis for fast lookup
_token_blacklist: set[str] = set()


def revoke_token(token: str) -> None:
    """Add a token to the revocation blacklist."""
    _token_blacklist.add(token)


def is_token_revoked(token: str) -> bool:
    """Check if a token has been revoked."""
    return token in _token_blacklist


def clear_revoked_tokens() -> None:
    """Clear all revoked tokens (useful for testing)."""
    _token_blacklist.clear()
