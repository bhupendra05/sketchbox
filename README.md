# sketchbox 🎲

**Three probabilistic data structures, built from scratch — massive data, tiny memory.**

When you can't afford to store everything, you trade a little accuracy for enormous savings
in space. These are the structures behind real databases, caches, and analytics systems —
implemented cleanly, with their math, and **validated against their theoretical error bounds
in the tests.**

Zero dependencies. Pure Python.

## What's inside

### 🌸 Bloom filter — "have I seen this before?"
Membership test with **no false negatives** and a tunable false-positive rate. Stores nothing
but bits.

```python
from sketchbox import BloomFilter

seen = BloomFilter(capacity=1_000_000, error_rate=0.01)
seen.add("user@example.com")
"user@example.com" in seen   # True
"nope@example.com" in seen   # almost always False
```
Sizing is derived from the math: `m = -n·ln(p)/(ln2)²` bits, `k = (m/n)·ln2` hashes.

### 📊 Count-Min Sketch — "how many times have I seen this?"
Frequency estimation for a stream in sub-linear space. **Never underestimates**; overestimates
are bounded by `ε·N` with probability `1−δ`.

```python
from sketchbox import CountMinSketch

cms = CountMinSketch(epsilon=0.001, delta=1e-5)
for word in stream:
    cms.add(word)
cms.estimate("the")   # ~ true count of "the"
```

### 🔢 HyperLogLog — "how many *distinct* things have I seen?"
Count unique items in **~16 KB** regardless of cardinality — millions of uniques, kilobytes of
memory, ~1% error. The algorithm behind `COUNT(DISTINCT)` at scale.

```python
from sketchbox import HyperLogLog

hll = HyperLogLog(precision=14)   # 2^14 registers ≈ 16 KB
for visitor in billions_of_events:
    hll.add(visitor)
len(hll)   # estimated unique visitors, ~0.8% standard error
```

## Why this is interview-worthy

- Each structure is an explicit **space ↔ accuracy** trade-off — and the README/tests show the
  exact bound, not just "it's approximate."
- HyperLogLog uses **leading-zero rank + harmonic mean + small-range (linear counting)
  correction** — the parts people gloss over.
- Hashes are derived by seeding a single fast hash (BLAKE2b) — no need for `k` independent hash
  functions; double hashing and per-row seeds do the job.

## Install & verify

```bash
pip install sketchbox
python -m pytest          # asserts the error bounds actually hold
python examples/demo.py   # Bloom vs set memory, CMS heavy hitters, HLL on 1M items
```

## License

MIT
