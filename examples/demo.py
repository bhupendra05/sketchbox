"""See the space ↔ accuracy trade-off in action."""
import random
import sys
import time

from sketchbox import BloomFilter, CountMinSketch, HyperLogLog


def demo_bloom():
    print("🌸 Bloom filter — membership in bits")
    n = 100_000
    bf = BloomFilter(capacity=n, error_rate=0.01)
    for i in range(n):
        bf.add(f"email-{i}@example.com")

    random.seed(0)
    fp = sum(1 for i in range(n) if f"absent-{i}@example.com" in bf) / n
    real_set = {f"email-{i}@example.com" for i in range(n)}
    sample = list(real_set)[:1000]
    set_bytes = sys.getsizeof(real_set) + sum(sys.getsizeof(s) for s in sample) // 1000 * n

    print(f"   added {n:,} items")
    print(f"   Bloom: {bf.bits_used // 8 / 1024:,.0f} KB   vs   set: {set_bytes / 1_048_576:,.1f} MB")
    print(f"   false-positive rate: {fp:.3%} (target 1.0%)\n")


def demo_countmin():
    print("📊 Count-Min Sketch — frequency of a stream")
    cms = CountMinSketch(epsilon=0.001, delta=1e-5)
    truth = {}
    random.seed(1)
    # a few heavy hitters + lots of noise
    for _ in range(200_000):
        if random.random() < 0.3:
            k = random.choice(["the", "and", "of"])
        else:
            k = f"w{random.randint(0, 5000)}"
        cms.add(k)
        truth[k] = truth.get(k, 0) + 1

    print(f"   table: {cms.depth} x {cms.width} counters, N={cms.total:,}")
    for k in ["the", "and", "of"]:
        print(f"   '{k}': est={cms.estimate(k):,}  true={truth[k]:,}  (≤ +{cms.error_bound:,.0f} error)")
    print()


def demo_hll():
    print("🔢 HyperLogLog — distinct count of 1,000,000 events")
    hll = HyperLogLog(precision=14)
    distinct = 200_000
    start = time.perf_counter()
    for i in range(1_000_000):
        hll.add(f"id-{i % distinct}")
    dur = time.perf_counter() - start

    est = hll.count()
    print(f"   true distinct: {distinct:,}")
    print(f"   HLL estimate:  {est:,}   error: {abs(est - distinct) / distinct:.2%}")
    print(f"   memory: {hll.m / 1024:.0f} KB (vs {distinct * 40 / 1_048_576:.1f} MB for a real set)")
    print(f"   processed 1,000,000 events in {dur:.2f}s\n")


if __name__ == "__main__":
    demo_bloom()
    demo_countmin()
    demo_hll()
