"""UUIDv7-like ID generator for Mutsumi tasks.

Produces 26-character Crockford Base32 encoded IDs:
- First 12 chars: millisecond timestamp
- Remaining 14 chars: random entropy
"""

from __future__ import annotations

import os
import time

# Crockford Base32 alphabet (excludes I, L, O, U)
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode_crockford(value: int, length: int) -> str:
    """Encode an integer to Crockford Base32 with fixed length."""
    result: list[str] = []
    for _ in range(length):
        result.append(_ALPHABET[value & 0x1F])
        value >>= 5
    result.reverse()
    return "".join(result)


def generate_task_id() -> str:
    """Generate a UUIDv7-like task ID (26-char Crockford Base32).

    Layout:
      - 12 chars: millisecond timestamp (60-bit capacity)
      - 14 chars: random entropy (70-bit capacity)
    """
    timestamp_ms = int(time.time() * 1000)
    random_bytes = os.urandom(9)  # 72 bits, we use 70
    random_int = int.from_bytes(random_bytes, "big") >> 2  # trim to 70 bits

    ts_part = _encode_crockford(timestamp_ms, 12)
    rand_part = _encode_crockford(random_int, 14)
    return ts_part + rand_part
