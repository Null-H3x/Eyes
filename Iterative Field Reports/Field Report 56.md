# Field Report 56 — FOUR EXPLANATIONS, FOUR EXCLUSIONS, AND A RETRACTION OF MY OWN

*Instrument: `eyeperiod` (7/7 selftests, two threshold failures caught before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. THE RETRACTION — FR55's horizon item 2 dies on inspection

FR55 nominated the adjacency prohibition as *"the single highest-value question this
cycle raises"* on the grounds that it "names a specific difference rather than a
distinctness property," so FR53's scale-invariance proof might not cover it. **That
is wrong, and the algebra takes three lines.**

On the skeleton, `p[t+1] − p[t] = drift·(Δ(g₂) − Δ(g₁) − 1)`. The prohibition is
`p[t+1] − p[t] ≠ −drift`. Since drift is invertible mod 83:

```
drift·(Δ(g₂) − Δ(g₁) − 1) ≠ −drift
⟺  Δ(g₂) − Δ(g₁) − 1 ≠ −1
⟺  Δ(g₂) ≠ Δ(g₁)   ⟺   g₁ ≠ g₂
```

The forbidden value is **itself a multiple of the drift**, so it scales out with
everything else. The constraint reduces to "adjacent glyphs differ" — tautologically
true of the observation that produced it, and carrying **zero drift information**.

This is FR53's proof holding in a case built specifically to escape it, which is
worth more than the original statement: a constraint can *name a value* and still be
scale-invariant, provided the value it names is itself drift-proportional. **The
general rule is stronger than FR36/FR53 stated it** — it is not only tests invariant
under scaling that fail, but any constraint whose target coordinate is derived from
the drift. Every quantity in this system is (FR30), so the class of escaping
constraints may be empty.

Tenth horizon item retired on inspection rather than measurement, and the first one
of mine killed one cycle after writing it. The lesson is that the *reason* an item
looks promising deserves the same scrutiny as the item.

That leaves FR55 item 1 — the unexplained short-range profile — as the cycle's
target.

---

## 1. Gate discipline — two failures before corpus contact

The instrument failed its own gate twice, both times on thresholds:

1. **S1** compared coset-4 IoC against the *whole-message* IoC. But a 4-offset
   keystream elevates the whole-message IoC too (0.0141 vs uniform 0.0120), so the
   comparison was self-defeating — a period-4 plant read as only 1.7× its own
   inflated baseline. Correct reference is the uniform 1/83.
2. **S2** required period 8 to clear alongside period 4. Period-8 cosets are half
   the size and correspondingly noisier (0.0227 vs 0.0239); requiring both was
   over-strict for a test aimed at period 4.

Both were caught before the corpus was touched, which is the entire purpose of the
gate. Logged because FR49 established that a gate which cannot fail is worthless,
and the converse deserves recording: this one failed twice and was worth having.

---

## 2. Postulated explanations, and what each predicts

After FR55, the lag-4 excess (26 vs ~11.8, z = +4.23, corrected P = 0.0035, present
in 9/9 messages) is established as real and is **not** plaintext repetition. Four
structural explanations remain, each with a distinct signature:

| # | Explanation | Prediction |
|---|---|---|
| P1 | **Period-4 keystream.** If `K[t+4]=K[t]`, then `c[t]=c[t+4] ⟺ p[t]=p[t+4]` and the excess IS plaintext coincidence — the "aligned fraction" reading | within-coset IoC at p=4 elevated to the plaintext IoC |
| P2 | **Self-isomorph at offset 4.** A passage repeating 4 positions later inside a message | lag-4 hits cluster in *runs* of consecutive t |
| P3 | **Privileged plaintext difference.** An excess at a single value δ₀ surfaces at exactly one lag, so δ₀ = 4·drift | excess at *every* distance, at Δ-difference `4−d` |
| P4 | **Encoding/authorial glyph-spacing.** The excess is a property of the glyph stream, not the plaintext | no plaintext-side translation succeeds |

P1 carries stakes far beyond lag-4: **the entire 384-relation skeleton rests on
`K[t] = drift·t`**, and no cycle in the series has tested for a periodic component.
P3 is the sharpest, because the drift cancels — `p[t]−p[t+d] = δ₀ ⟺ Δ(g₁)−Δ(g₂) =
4−d` — making it testable out-of-sample at every distance except the one that
motivated it.

---

## 3. Results — all three testable explanations excluded

**P1 — PERIOD-4 KEYSTREAM: REJECTED.** Coset IoC across periods 2–12 is flat.

```
 p :   2      3      4      5      6      7      8      9     10     11     12
IoC: .01223 .01166 .01245 .01127 .01292 .01434 .01226 .01262 .01179 .01128 .01064
 xN:  1.02   0.97   1.03   0.94   1.07   1.19   1.02   1.05   0.98   0.94   0.88
```

Coset-4 z = **+0.95** against a +3.0 threshold; ratio to the non-multiple periods 3
and 5 is **1.07×** against a 1.5× threshold. The gate (S7) established this test
detects the effect at **z = +13.1** if the lag-4 excess were plaintext coincidence
under period-4. It is not remotely there. (p=7 sits at z=+2.38; with eleven periods
examined that is the expected maximum of eleven draws and is **not** a finding.)

**The corollary is the more valuable half.** The progressive premise underwriting
FR26–FR54 has been *assumed* for thirty cycles and never directly tested. It now
survives a well-powered test it could have failed. That is not proof the keystream
is progressive, but it removes the most plausible alternative that would have
invalidated the skeleton wholesale.

**P2 — SELF-ISOMORPH AT OFFSET 4: REJECTED.** All 26 lag-4 coincidences are
**isolated singletons** — run-length histogram `{1: 26}`, maximum run 1, zero runs of
length ≥2, where the null mean is 1.12 and 0.13 respectively. The detector fires at
max-run 11 on a planted 10-long offset-4 repeat (S4) and sits at 1 on a clean corpus
(S5). Controls at neighbouring lags 3, 5 and 6 are identical. There is no repeated
passage at internal offset 4.

**P3 — PRIVILEGED PLAINTEXT DIFFERENCE: REJECTED, out-of-sample.** Pooling distances
1–20 with d=4 **excluded**, and testing for Δ-difference `4−d`: 2,481 usable
same-component pairs, **23 observed against a null mean of 28.50** (sd 5.33),
**z = −1.03**. The instrument detects a planted privileged difference at z = +6.7 and
sits at z = −0.67 on a clean control. The excess does not generalise off d=4 at any
distance.

---

## 4. What this leaves

Every structural explanation available inside the established model is now excluded:

| Explanation | Status | Power of the test |
|---|---|---|
| plaintext repetition | excluded (FR55) | k=26 p≈0.021, k=29 p≈0.034 |
| period-4 keystream | **excluded (P1)** | z=+13.1 at the relevant effect size |
| offset-4 self-isomorph | **excluded (P2)** | max-run 11 on plant |
| privileged plaintext difference | **excluded (P3)** | z=+6.7 on plant |

The excess is real, corpus-wide, body-located, glyph-generic (20 distinct glyphs,
max 3 for any one), non-chaining, unphased, isolated, and survives unigram-preserving
nulls, adjacency-constrained nulls, geometry-preserving nulls and multiplicity
correction. **It now has no surviving mechanism.**

This is a stronger statement than "unexplained." Under the model, `c[t]=c[t+4]`
translates to the plaintext statement `p[t]−p[t+4] = drift·4`, and **every attempt to
express the excess as a plaintext-side property has failed** — as repetition (FR55),
as periodicity (P1), as passage structure (P2), and as a difference preference (P3).
The one combination that survives is exactly "the same ciphertext glyph, four apart,"
which is a statement about the **glyph stream** rather than about anything the cipher
is carrying.

**P4 is therefore the surviving reading, and it is offered rather than claimed.** The
corpus already carries one hard glyph-spacing constraint — the adjacency prohibition,
0 over 1,027 pairs, P ≈ 4.1×10⁻⁶ — which FG1 §4b read as an *encoding* property
("double-mixed embedding"), not a plaintext one. The short-range profile

```
d :   1     2     3     4     5     6
n :   0     5     9    26    11    12
z : HARD -2.09 -0.84 +4.23 -0.21 +0.05
```

may be one authorial hand rather than two phenomena. **What does not work is the
obvious conservation argument**: suppression at d≤2 removes ~19 repeats which must
reappear somewhere, and the d=4 excess is ~14 — an attractive match. But
redistribution across 28 lags is uniform (FR55 measured it: constraining the null
moved d=4 from z=+4.21 to +4.23), so the argument requires the displaced repeats to
pile *specifically* at 4, which is the thing being explained. Circular, and recorded
as such so it is not reached for again.

---

## 5. Model status — unchanged, one premise strengthened

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift unpinned
with H4 the only surviving hypothesis. Nothing here touches the skeleton.

The one change is to a premise rather than a figure: **the progressive keystream
reading is no longer merely assumed.** P1 is the first direct test of it in the
series.

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Adjacency prohibition as drift lever | FR55 horizon item 2, "highest-value" | **RETRACTED** — scale-invariant; reduces to "adjacent glyphs differ" |
| FR53 scale-invariance proof | applies to tests invariant under scaling | **STRENGTHENED** — also applies to constraints naming a drift-proportional value; the escaping class may be empty |
| Progressive keystream premise | assumed since FR26, untested | **TESTED and survives** — no periodic component at p=2..12 |
| Lag-4 excess, mechanism | "generic distance-4 coincidence" (FG5), insufficient (FR55) | **NO SURVIVING MECHANISM** — four explanations excluded with powered tests |
| Lag-4 excess, reading | plaintext-side assumed throughout | **glyph-stream-side (P4)** is the only survivor; offered, not claimed |

---

## 7. Horizon

1. **P4 is testable, but not from inside the corpus.** If the d=1 prohibition and the
   d=4 excess are encoding-side, they are properties of how Petri generated the glyph
   sequence, and the evidence lives in the game assets — the Ghidra route
   (`GHIDRA.md`, installers v1.1.1, present in the repo and never run to completion):
   base-7 decoder → draw call → sprite/UV lookup. This is the first time the series
   has had a *specific prediction* to take to the assets rather than a general hope
   of an anchor: a generator that forbids adjacent repeats should be visible in code.

2. **Do not re-open the lag-4 excess from inside the corpus.** Four powered
   exclusions and six characterisations is close to what 1,036 glyphs can support.
   Further internal work on it will produce watch-grade noise.

3. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering); and
   the success criterion, still the most consequential open item and still the only
   thing this series can neither compute nor close.

4. **Repo hygiene, unchanged from FR55 §8** — no Field Reports or FR-cycle
   instruments are tracked; `WAY_FORWARD_next.md` §5 still lists the W2/E4/W4 bridge
   as Priority 1, closed by FR34/FR35.
