"""Count-Min Sketch — frequency estimation for streams in sub-linear space."""
from __future__ import annotations

import math

from .hashing import hash64


class CountMinSketch:
    """Estimate how many times each item appeared in a stream.

    A ``depth × width`` table of counters; each item increments one counter per row (chosen
    by a per-row hash). The estimate is the **minimum** across rows — collisions can only add
    to a counter, so the min never *underestimates*. With

        width = ceil(e / epsilon),  depth = ceil(ln(1 / delta))

    the overestimate is at most ``epsilon · N`` with probability ``1 − delta``.
    """

    def __init__(self, epsilon: float = 0.001, delta: float = 1e-5):
        if not 0.0 < epsilon < 1.0:
            raise ValueError("epsilon must be in (0, 1)")
        if not 0.0 < delta < 1.0:
            raise ValueError("delta must be in (0, 1)")
        self.epsilon = float(epsilon)
        self.delta = float(delta)
        self.width = max(1, int(math.ceil(math.e / epsilon)))
        self.depth = max(1, int(math.ceil(math.log(1.0 / delta))))
        self._table = [[0] * self.width for _ in range(self.depth)]
        self._total = 0

    def add(self, item, count: int = 1) -> None:
        for row in range(self.depth):
            self._table[row][hash64(item, row) % self.width] += count
        self._total += count

    def estimate(self, item) -> int:
        return min(self._table[row][hash64(item, row) % self.width] for row in range(self.depth))

    def __getitem__(self, item) -> int:
        return self.estimate(item)

    @property
    def total(self) -> int:
        return self._total

    @property
    def error_bound(self) -> float:
        return self.epsilon * self._total
