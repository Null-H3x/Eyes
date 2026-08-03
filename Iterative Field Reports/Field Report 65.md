# Field Report 65 — THE FOUNDATION AUDITED FROM RAW DATA: FOUR PREMISES EXACT, ONE OVERSTATED

*Instrument: `eyeprem` (corpus-only, no atlas, no skeleton). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — what is left that can be computed at all

Every item on FR64's horizon requires external input: anchors, glyph pictures, the
binary, Ben's hardware. The honest question opening this cycle was whether anything
remains computable.

One thing does, and it is overdue. **FR46 rebuilt the model end-to-end — but from
corpus *plus atlas plus repairs*.** The atlas and the keystream-scope premise were
*inputs* to that audit, not outputs. In sixty-four cycles nobody has audited the
premises **from the raw corpus up**. These are the claims that, if wrong, invalidate
everything downstream:

| premise | doctrine figure | source |
|---|---|---|
| per-triplet keystream scope | within z=14.65, cross z=−0.47 | scoreboard, keyspace ledger |
| near-duplicate structure | T1 44.4%, T2 7.8%, T3 27.2% | keyspace ledger |
| literal shared runs | 0 of 27 cross-triplet pairs carry a run ≥2 | FR14, called by FR29 "the strongest corroboration available in this project" |
| E1/W1 re-sync events | 5 (excludes ciphertext-autokey) | keyspace ledger |
| literal header positions | [1, 2] | keyspace ledger |

All five are computable from `corpus.json` alone, with no inherited artifact.

---

## 1. SELF-CORRECTION — I pre-wrote a conclusion and the data refuted it in the first row

Scanning for the body definition that reproduces the 44.4% figure, I wrote the
interpretation *into the print statement* before seeing output:

> `-> no start position reproduces 44.4%; the doctrine figure is computed on a
> different base...`

The very first row returned **lo=0 → 44.4%**. The conclusion was false and had been
committed in advance.

This is FR31's error repeated verbatim — there, I drafted "the skeleton cannot
bootstrap itself" from a feasibility probe and the positive control contradicted it
outright. Same shape, thirty-four cycles later: **a narrative written before the
measurement, which would have been published had the number not been sitting
directly under it.** Logged because it is the second occurrence and the guard is
evidently not automatic.

---

## 2. Results — four of five reproduce exactly

**PREMISE 2 — near-duplicate structure: EXACT on all three triplets.**

| triplet | near-dup pair | measured | doctrine |
|---|---|---:|---:|
| T1 | East 1 / West 1 | **44.4%** | 44.4% |
| T2 | West 2 / West 3 | **7.8%** | 7.8% |
| T3 | East 4 / East 5 | **27.2%** | 27.2% |

The odd messages fall out correctly too — E2, E3, W4 — and in every triplet the
near-duplicate pair is the clear maximum.

**A reproducibility trap worth flagging.** The keyspace ledger labels this column
*"body agree"*, but the figures are computed over the **full message including the
shared header**. Excluding the header (pos ≥ 24) gives 28.0% / 2.6% / 12.2%. Anyone
recomputing "body agreement" as the label instructs will conclude the doctrine is
wrong by a wide margin. The numbers are right; the column name is not.

**PREMISE 3 — literal shared runs: EXACT.** Cross-triplet pairs carrying an aligned
run of length ≥2: **0 of 27**, precisely as FR14 claimed. Within-triplet, E1/W1
carries a run of **13** and E4/E5 carries one of 3. The strongest single piece of
evidence in the project verifies from raw data.

**PREMISE 4 — re-sync events: EXACT.** E1/W1 contains **6 maximal identical blocks**,
hence **5 re-sync events**, matching the ledger. The exclusion of ciphertext-autokey
rests on a correctly counted quantity.

**PREMISE 5 — literal header: EXACT.** Positions 1 and 2 carry a single value across
all nine messages (**66** and **5**); position 0 carries nine distinct values (the
per-message indicator); positions 3–5 carry two each. The `[1,2]` claim is exactly
right.

---

## 3. The one premise that is overstated

**PREMISE 1 — keystream scope.** The qualitative claim is robust; the cross-triplet
figure is not.

```
within-triplet body : obs 50, unigram-null μ 10.2  →  z = +12.47   [doctrine +14.65]
cross-triplet  body : obs 36, unigram-null μ 29.2  →  z =  +1.26   [doctrine −0.47]
```

Within-triplet reproduces closely. **Cross-triplet does not sit at baseline — it sits
mildly positive.** The doctrine's phrasing — *"cross z=−0.5, at the uniform
baseline"* — asserts something slightly stronger than the data supports.

Traced: the residual is carried by a **single pair, East 2 / East 4** (4 aligned
agreements against 1.1 expected). Across 27 cross-triplet pairs, one at that level
is entirely unremarkable after multiplicity, and it is **not** promoted to a finding
here.

**What survives intact** is the conclusion the premise exists to support. The
within/cross separation is an order of magnitude in z (+12.47 vs +1.26), so
per-triplet keystream scope stands. What should be corrected is the *claim of
exact baseline* — the honest statement is "cross-triplet is close to baseline, with
a small unexplained residual traceable to one pair," not "at the uniform baseline."

Note also that the choice of null matters here: against uniform 1/83 the cross
figure reads z=+1.67, against a unigram-preserving null z=+1.26. The corpus IoC
exceeds 1/83, so the unigram null is the correct one — the same lesson FR42 and
FR57 established for other statistics.

---

## 4. What this cycle establishes

After sixty-five cycles, **the model-independent foundation verifies from raw data
with no inherited artifact.** Four of five premises reproduce to the digit; the
fifth reproduces qualitatively with an overstated sub-claim that does not threaten
its conclusion.

This is worth having precisely because so much rests on it. FR46 certified that the
published model follows from corpus + atlas + repairs. This certifies that the
*premises feeding that audit* follow from the corpus alone. The two together close
the reproduction chain from raw glyphs to the 384 relations.

---

## 5. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned. Consistent alphabet set exactly 22,550 (FR63), first anchor spent on gauge
(FR64).

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Near-duplicate figures (44.4 / 7.8 / 27.2) | published | **REPRODUCED EXACTLY** from raw corpus |
| "body agree" column label | reads as header-excluded | **MISNOMER** — computed over the full message; header-excluded gives 28.0/2.6/12.2 |
| FR14 literal runs (0 of 27) | strongest corroboration in the project | **REPRODUCED EXACTLY** |
| E1/W1 re-sync = 5 | published | **REPRODUCED EXACTLY** (6 identical blocks) |
| Literal header [1,2] | published | **REPRODUCED EXACTLY** (values 66, 5) |
| Cross-triplet z = −0.47 "at baseline" | published | **OVERSTATED** — measures +1.26 under a unigram null; conclusion unaffected |
| Foundation | audited from atlas down (FR46) | **also audited from raw corpus up** |

---

## 7. Horizon

The internal programme is, as far as I can determine, complete. Every remaining item
requires evidence from outside the ciphertext:

1. **Five real anchors, one per component** (FR64) — uniquely determines all 46 held
   glyphs and 61.3% of the corpus. The first is overhead; placement dominates count.
2. **Count the MSB states on the glyph pictures** (FR59 §4) — cheapest open question,
   symmetric outcome, needs only the glyph inventory.
3. **Settle the radix** (`GHIDRA.md` base-7 vs corpus base-5) — load-bearing for
   FR58/FR59, a fact in an invariant binary.
4. **Port the skeleton filter into EyeStat** (FR61/FR62) — ~17–47 GPU-hours for a
   conclusive Park-Miller sweep.
5. **The success criterion** (FR57) — decidable since FR57, still undecided, and it
   governs whether items 1–4 are worth doing at all.

I would treat item 5 as prior to the rest rather than parallel with it.
