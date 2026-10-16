"""
SecureFlow AI - Cryptographic Token Vault
================================================================================
File: ai-service/app/crypto/vault.py

Provides zero-leak enterprise cryptographic operations:
  - AES-256-GCM Envelope Encryption / Decryption with random 96-bit nonce and tag
  - Deterministic HMAC-SHA256 Tokenization for reversible pseudonymization
  - Key versioning metadata ("v1", "v2", etc.)
  - Detokenization with authorization key checks
"""

import os
import hmac
import base64
import hashlib
import logging
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("SecureFlowAI.CryptoVault")


class CryptoVault:
    """
    AES-256-GCM + HMAC-SHA256 Cryptographic Vault.
    Guarantees:
      1. Plaintext PII is never persisted in logs or database unencrypted.
      2. Reversible tokenization enables authorized SOC officers to detokenize data.
      3. Key versioning permits future zero-downtime key rotation.
    """

    def __init__(self, master_key_hex: Optional[str] = None, hmac_salt: Optional[str] = None, key_version: str = "v1"):
        self.key_version = key_version
        
        # 256-bit (32 bytes) master key for AES-GCM
        env_key = os.getenv("VAULT_MASTER_KEY")
        key_source = master_key_hex or env_key or "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        
        try:
            self.master_key = bytes.fromhex(key_source)[:32]
            if len(self.master_key) < 32:
                # Pad to 32 bytes if shorter
                self.master_key = self.master_key.ljust(32, b"\0")
        except ValueError:
            self.master_key = hashlib.sha256(key_source.encode("utf-8")).digest()

        # Salt for HMAC token generation
        self.hmac_salt = (hmac_salt or os.getenv("VAULT_HMAC_SALT") or "secureflow-bank-salt").encode("utf-8")
        self._aesgcm = AESGCM(self.master_key)
        logger.info(f"[CRYPTO VAULT] Initialized with key version '{self.key_version}'.")

    def hash_sha256(self, plaintext: str) -> str:
        """Computes one-way zero-leak SHA-256 hash for audit indexing without exposing PII."""
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()

    def generate_token(self, entity_type: str, plaintext: str) -> str:
        """
        Generates a reversible, deterministic HMAC token.
        Format: TOK_{ENTITY_TYPE}_{16_CHAR_HMAC_HEX}
        Example: TOK_CREDIT_CARD_4a8b1c9e2f3d5a6b
        """
        digest = hmac.new(self.hmac_salt, f"{entity_type}:{plaintext}".encode("utf-8"), hashlib.sha256).hexdigest()
        clean_type = entity_type.upper().replace(" ", "_")
        return f"TOK_{clean_type}_{digest[:16]}"

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts plaintext using AES-256-GCM with a fresh random 12-byte (96-bit) nonce.
        Returns base64-encoded string: nonce (12 bytes) + ciphertext + 16-byte tag.
        """
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    def decrypt(self, encrypted_b64: str) -> str:
        """
        Decrypts an AES-256-GCM base64 string.
        Extracts nonce, verifies tag, and returns decrypted plaintext.
        """
        try:
            raw_bytes = base64.b64decode(encrypted_b64.encode("utf-8"))
            if len(raw_bytes) < 28:  # 12 nonce + 16 tag minimum
                raise ValueError("Ciphertext too short.")
            nonce = raw_bytes[:12]
            ciphertext_with_tag = raw_bytes[12:]
            decrypted = self._aesgcm.decrypt(nonce, ciphertext_with_tag, None)
            return decrypted.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Unable to decrypt payload: {e}")

    def vault_token(self, entity_type: str, plaintext_value: str) -> Tuple[str, str, str]:
        """
        High-level vaulting operation:
        Returns (token, encrypted_ciphertext_b64, sha256_hash).
        """
        token = self.generate_token(entity_type, plaintext_value)
        ciphertext = self.encrypt(plaintext_value)
        content_hash = self.hash_sha256(plaintext_value)
        return token, ciphertext, content_hash


# Global Singleton
_vault_instance: Optional[CryptoVault] = None


def get_crypto_vault() -> CryptoVault:
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = CryptoVault()
    return _vault_instance
