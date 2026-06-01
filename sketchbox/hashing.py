"""Deterministic 64-bit hashing, seedable to produce independent hash functions.

Instead of implementing many hash functions, we seed one fast, well-distributed hash
(BLAKE2b) via its ``person`` parameter. This gives as many independent-looking hashes as
we need.
"""
from __future__ import annotations

import hashlib


def _to_bytes(item) -> bytes:
    if isinstance(item, bytes):
        return item
    if isinstance(item, str):
        return item.encode("utf-8")
    return repr(item).encode("utf-8")


def hash64(item, seed: int = 0) -> int:
    """Return a 64-bit hash of ``item`` for the given ``seed`` (0..2^63)."""
    person = (seed & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
    digest = hashlib.blake2b(_to_bytes(item), digest_size=8, person=person).digest()
    return int.from_bytes(digest, "little")
