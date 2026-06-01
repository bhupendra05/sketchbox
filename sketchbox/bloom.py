"""Bloom filter — probabilistic set membership with no false negatives."""
from __future__ import annotations

import math

from .hashing import hash64


class BloomFilter:
    """A space-efficient set. ``x in bf`` is never wrongly False, but may rarely be wrongly
    True (rate ≈ ``error_rate`` once ``capacity`` items are inserted).

    Sizing follows the standard optima:
        m = ceil(-n·ln(p) / (ln2)^2)   bits
        k = round((m/n)·ln2)           hash functions
    The k indexes come from double hashing: g_i(x) = h1(x) + i·h2(x) (mod m).
    """

    def __init__(self, capacity: int, error_rate: float = 0.01):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if not 0.0 < error_rate < 1.0:
            raise ValueError("error_rate must be in (0, 1)")
        self.capacity = int(capacity)
        self.error_rate = float(error_rate)
        self.size = self._optimal_m(self.capacity, self.error_rate)
        self.num_hashes = self._optimal_k(self.size, self.capacity)
        self._bits = bytearray((self.size + 7) // 8)
        self._count = 0

    @staticmethod
    def _optimal_m(n: int, p: float) -> int:
        return max(1, int(math.ceil(-n * math.log(p) / (math.log(2) ** 2))))

    @staticmethod
    def _optimal_k(m: int, n: int) -> int:
        return max(1, int(round((m / n) * math.log(2))))

    def _indexes(self, item):
        h1 = hash64(item, 0)
        h2 = hash64(item, 1) or 1  # avoid a zero step
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    def add(self, item) -> None:
        for idx in self._indexes(item):
            self._bits[idx >> 3] |= 1 << (idx & 7)
        self._count += 1

    def __contains__(self, item) -> bool:
        return all((self._bits[idx >> 3] >> (idx & 7)) & 1 for idx in self._indexes(item))

    def __len__(self) -> int:
        return self._count

    @property
    def bits_used(self) -> int:
        return self.size

    @property
    def expected_fp_rate(self) -> float:
        """Current theoretical false-positive rate given how many items were added."""
        return (1 - math.exp(-self.num_hashes * self._count / self.size)) ** self.num_hashes
