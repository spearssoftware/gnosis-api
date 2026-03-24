"""Shared utilities for API key operations."""

import hashlib

from gnosis_api.config import settings


def hash_key(key: str) -> str:
    return hashlib.sha256(f"{settings.api_key_salt}:{key}".encode()).hexdigest()
