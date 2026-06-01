"""HyperLogLog — estimate the number of distinct items in tiny, fixed memory."""
from __future__ import annotations

import math

from .hashing import hash64


class HyperLogLog:
    """Count distinct elements using ``2^precision`` one-byte registers.

    For each item we hash to 64 bits: the top ``precision`` bits choose a register, and we
    store the **rank** (position of the leftmost 1-bit) of the remaining bits. Many distinct
    items ⇒ some register eventually sees a high rank. The cardinality is recovered from the
    harmonic mean of ``2^register`` across all registers, with a small-range correction
    (linear counting) when few registers are filled.

    Standard error ≈ ``1.04 / sqrt(2^precision)`` — e.g. precision 14 ⇒ ~0.81% in ~16 KB.
    """

    def __init__(self, precision: int = 14):
        if not 4 <= precision <= 16:
            raise ValueError("precision must be in [4, 16]")
        self.p = precision
        self.m = 1 << precision
        self._registers = bytearray(self.m)
        self._alpha = self._alpha_m(self.m)
        self._rank_bits = 64 - precision

    @staticmethod
    def _alpha_m(m: int) -> float:
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1.0 + 1.079 / m)

    def add(self, item) -> None:
        x = hash64(item)
        idx = x >> self._rank_bits                      # top p bits -> register
        w = x & ((1 << self._rank_bits) - 1)            # remaining bits
        rank = (self._rank_bits - w.bit_length() + 1) if w else (self._rank_bits + 1)
        if rank > self._registers[idx]:
            self._registers[idx] = rank

    def count(self) -> int:
        m = self.m
        harmonic = sum(2.0 ** (-r) for r in self._registers)
        estimate = self._alpha * m * m / harmonic
        if estimate <= 2.5 * m:                         # small-range correction
            zeros = self._registers.count(0)
            if zeros:
                estimate = m * math.log(m / zeros)      # linear counting
        return int(estimate)

    def __len__(self) -> int:
        return self.count()

    @property
    def standard_error(self) -> float:
        return 1.04 / math.sqrt(self.m)
