"""Tests that validate each structure against its theoretical guarantee."""
import random

from sketchbox import BloomFilter, CountMinSketch, HyperLogLog


# ── Bloom filter ──────────────────────────────────────────────────────────────
def test_bloom_no_false_negatives():
    bf = BloomFilter(capacity=5000, error_rate=0.01)
    items = [f"item-{i}" for i in range(5000)]
    for it in items:
        bf.add(it)
    assert all(it in bf for it in items)   # guarantee: never a false negative
    assert len(bf) == 5000


def test_bloom_false_positive_rate_near_target():
    random.seed(42)
    bf = BloomFilter(capacity=5000, error_rate=0.01)
    for i in range(5000):
        bf.add(f"present-{i}")
    false_positives = sum(1 for i in range(5000) if f"absent-{i}" in bf)
    rate = false_positives / 5000
    assert rate < 0.03   # target ~1%, allow slack


def test_bloom_sizing_is_sane():
    bf = BloomFilter(1000, 0.01)
    assert bf.size > 0 and bf.num_hashes > 0


# ── Count-Min Sketch ──────────────────────────────────────────────────────────
def _stream(seed, distinct, n):
    random.seed(seed)
    truth = {}
    cms = CountMinSketch(epsilon=0.01, delta=1e-5)
    for _ in range(n):
        k = f"k{random.randint(0, distinct)}"
        cms.add(k)
        truth[k] = truth.get(k, 0) + 1
    return cms, truth


def test_countmin_never_underestimates():
    cms, truth = _stream(1, 80, 2000)
    for key, true_count in truth.items():
        assert cms.estimate(key) >= true_count   # guarantee: never under


def test_countmin_within_error_bound():
    cms, truth = _stream(2, 80, 2000)
    bound = cms.error_bound
    for key, true_count in truth.items():
        assert cms.estimate(key) - true_count <= bound + 1


# ── HyperLogLog ───────────────────────────────────────────────────────────────
def test_hll_large_cardinality_within_error():
    hll = HyperLogLog(precision=14)
    n = 50_000
    for i in range(n):
        hll.add(f"user-{i}")
    assert abs(hll.count() - n) / n < 0.03   # ~0.8% expected, allow 3%


def test_hll_small_cardinality_accurate():
    hll = HyperLogLog(precision=14)
    for i in range(100):
        hll.add(f"x{i}")
    assert abs(hll.count() - 100) < 20        # linear-counting regime


def test_hll_duplicates_dont_inflate():
    hll = HyperLogLog(precision=12)
    for _ in range(1000):
        hll.add("same")
    assert hll.count() <= 2                    # one distinct item
