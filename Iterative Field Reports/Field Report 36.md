# Field Report 36 — A Test That Is Not Scale-Invariant

**Series note.** Thirty-sixth report of the EYESPIRAL series. FR35 left only housekeeping
on the internal ledger, so this cycle challenges a standing assumption instead: that the
drift cannot be pinned from inside the corpus. Instrument `eyeclust.py`, selftest 7/7
green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Every determined relation has the form drift·Δ_eff (FR30), so
the drift rescales the whole skeleton at once — and both tests the series has aimed at it,
injectivity (FR21) and cross-component packing (FR27), are **invariant under that
rescaling** and therefore structurally incapable of pinning it. What would not be
invariant is a property of the *plaintext*: FR30's channel gives p = A + drift·v with v
computable without knowing drift, bases or alphabet, so if the plaintext alphabet were a
contiguous range of size k — the natural shape for a token stream numbered 0…k−1 — then
{drift·v} would have to fit inside a window of width k, and window width is emphatically
not scale-invariant. The test finds **nothing**: the corpus's best drift sits at
z = −2.19, which is what the minimum of 82 draws reaches by chance. But the positive
controls make that null informative rather than empty. A planted contiguous alphabet of
26, 40 or 60 recovers the true drift at **rank 1, z between −4.1 and −5.7**, while a
planted full-width alphabet recovers nothing. So the null **excludes a small contiguous
plaintext alphabet at roughly 4σ power** — an independent, drift-free corroboration of
FG2/FG3's effective alphabet near 79, reached without pins and by a completely different
mechanism.

---

## 1. Why this was worth trying

The series has twice aimed a global-consistency test at the drift and twice found it
inert. That is not bad luck; it is structural. FR30's deduction makes every determined
quantity a fixed multiple of the drift, so changing the drift applies one invertible
scalar to the entire skeleton. Injectivity asks whether values are distinct — preserved
under any invertible scaling. Packing asks whether component value-sets can be placed
disjointly — likewise preserved. **Any scale-invariant test is guaranteed to fail here**,
and recognising that narrows the search usefully: the discriminator has to be sensitive to
*magnitude*, not just to distinctness.

Window width is such a property. If the plaintext alphabet is contiguous of size k, then
within each (message, component) block all p values lie in a window of width k, so all
drift·v values do too. Multiply by the wrong drift and a tight cluster smears across the
ring.

## 2. C1 — power, established before the corpus is touched

| planted alphabet k | rank of true drift | best drift found | z of truth |
|---|---|---|---|
| 26 | **1** | 37 ✓ | −5.47 |
| 40 | **1** | 37 ✓ | −5.73 |
| 60 | **1** | 37 ✓ | −4.06 |
| 83 (full width) | 70 | 39 ✗ | +1.06 |

Decisive for a small contiguous alphabet, powerless at full width — exactly as the
construction predicts, and the full-width row is the negative control that stops the test
from being a machine that always finds something.

## 3. C2 — the corpus

| rank | drift | mean window | z |
|---|---|---|---|
| 1 | 14 | 54.15 | −2.19 |
| 2 | 69 | 54.15 | −2.19 |
| 3 | 34 | 54.18 | −2.17 |
| 4 | 49 | 54.18 | −2.17 |

Mean 57.25, sd 1.42. The best drift reaches z = −2.19, which the minimum of 82 draws
attains routinely. **No drift discrimination.**

The results appear in mirror pairs (14/69, 34/49, 24/59) because the statistic is
symmetric under drift → −drift: a window and its reflection have equal width. That is a
property of the test, documented in the gate, not a finding.

H1's predicted drift 31 ranks 71st of 82. Since the test has no power here that is
**neither support nor refutation** — worth stating explicitly, because a poorly-powered
test producing an unfavourable rank is exactly the kind of thing that invites
over-reading.

## 4. C3 — what the null buys

The controls show the test would locate the drift at z ≈ −4 or better for any contiguous
plaintext alphabet up to size 60. It does not. Therefore:

> **A small contiguous plaintext alphabet is excluded.** If the plaintext is a token
> stream whose tokens are contiguously numbered, the inventory is large.

That is an independent corroboration of FG2/FG3's effective alphabet near 79 — reached
drift-free, without pins, on the repaired skeleton, and by a mechanism (clustering) with
no relationship to the coincidence measure that produced the original figure. Two
unrelated routes agreeing is worth more than either alone.

**The caveat is real and bounds the claim.** A small but *scattered* alphabet would not
cluster and is not excluded here. Ruling that out needs a coincidence measure, which FR30
built and found underpowered at current component coverage. So the fork narrows rather
than closes: branch B survives only in a form where the token inventory is either large or
non-contiguously numbered.

## 5. Where the model stands

Unchanged in structure, sharpened in interpretation:

- **384 determined relations over 56 glyphs**, components 25/11/7/3 plus five pairs,
  injectivity clean, 74.1% of corpus positions exposed.
- **The drift remains unpinned**, and this cycle explains *why* previous attempts failed —
  they were scale-invariant by construction. This attempt was not, and still found
  nothing, which is itself the plaintext-alphabet result.
- **A-vs-B narrowed**: small contiguous token inventories are out.

## 6. Horizon

(1) **The scattered-alphabet variant** is the one branch-B form this cycle does not touch;
FR30's coincidence channel is the right instrument and needs roughly a doubling of
component coverage to reach 3σ, which only external anchors can now supply. (2) **#2⁻'s
instance-level audit** remains the last unexecuted internal task. (3) The acquisition
target is unchanged: two external anchors inside component 1 fix rotation and drift
together, after which H1's prediction of drift 31 becomes a genuine test rather than an
unfalsifiable one.

## 7. Reproduction

`eyeclust.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — window width exact on constructed sets, a planted k = 26 alphabet
recovering the drift at rank 1, a planted full-width alphabet recovering nothing, the
drift → −drift symmetry documented, FR35's skeleton reproduced, sufficient blocks, and the
baseline guard. The full run reproduces C1's power table, C2's corpus sweep and C3's
exclusion. Failures carry prefix `XD-MBYG04K-URS3LF`.
