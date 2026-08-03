# Field Report 60 — THE 34-BILLION-SEED SWEEP COULD NOT HAVE FOUND THE ANSWER

*Instrument: `eyefilter` (4/4 selftests, green before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — a measurement whose premise is now known to be false

`eyeforward` lists "a PRNG under an untested family" as a live hiding place for
`C`, and doctrine records EyeStat's Tier-1 sweep — **~34 billion seeds across 16
PRNG/mode combinations, zero chi²-filter survivors**. The standing correction is
that this sweep was partial, so the corner is not exhausted.

That correction is too weak, and the reason is FR57. The sweep's filter selects
candidates by a **plaintext property**, and FR57 certified what that property
actually is. If the filter selects for something the true plaintext does not have,
then zero survivors is what the sweep returns **whether or not the correct seed was
tested** — and the 34 billion is not partial evidence, it is no evidence.

This is the FR48/FR52 shape: a measurement that includes its own premise among its
evidence. The guard is the same one those cycles named — *ask what the test would
return if the hypothesis were false, and check the answer differs.*

---

## 1. What the filter actually is

Read from source rather than memory (`eyestat_gpu.py` chi2_pre_filter, mirrored in
`shadow_audit.shadow_chi2_pre_filter`, documented in
`eyestat_compute_audit.py` Phase 8):

```
chi2_l   = Σᵢ ( sorted_desc(f_candidate)[i] − sorted_desc(expected_l)[i] )²
min_chi2 = min over l ∈ {fi, krl, en}
PASS  if min_chi2 ≤ threshold
```

It keeps candidates whose **sorted frequency profile resembles a natural language**,
using the Finnish / Karelian / English tables in `eyestat_scoring.py`. Survivors
then proceed to Hungarian symbol→letter assignment against language letter
frequencies and dictionary word counting.

This is a natural-language objective end to end. `WAY_FORWARD_next.md` §6 lists
exactly this as a guardrail — *"do not score `C`-candidates by natural-language
fitness until A-vs-B is resolved"* — and §4 identifies it as "the current plan's one
internal contradiction." **A-vs-B is now resolved, against the readable branch**
(FR36, FR39, FR40, FR42, FR57).

---

## 2. Gate — the instrument works when the premise holds

Four selftests green before corpus contact. **S3 is the control that makes the
finding meaningful:** on a *language* plaintext the filter cleanly discriminates the
correct key from a wrong key, mean chi² gap **+0.0434**. The filter is not broken.
It is well-built for a plaintext this corpus does not have.

Minor observation logged in passing: an English-sampled text is attributed to
Karelian. Sorted profiles are near-identical across languages, so the filter matches
*shape*, not language identity — its `best_lang` output should not be read as a
language determination.

---

## 3. THE DECISIVE RESULT — no power at the certified inventory

FR57 puts the plaintext effective inventory at a point estimate of **84.6**, CI
**[77.3, 93.4]**, with FR39's hard lower bound around 60. Discrimination between
correct and wrong keys, 200 draws each:

| plaintext inventory | correct-key chi² | wrong-key chi² | gap | gap/sd | verdict |
|---|---:|---:|---:|---:|---|
| 83 (flat) | 0.04362 | 0.04348 | **−0.000134** | −0.14 | **NO POWER** |
| 79 (FG2/FG3 estimate) | 0.04300 | 0.04370 | +0.000692 | 0.77 | **NO POWER** |
| 60 (FR39 lower bound) | 0.03865 | 0.04357 | +0.004925 | 4.79 | discriminates |
| *language (control)* | — | — | *+0.0434* | — | *discriminates* |

**At the certified inventory the filter has no power at all.** At 83 the correct key
scores marginally *worse* than wrong keys. The filter only begins to discriminate at
60 — the extreme bottom of FR39's range, and outside FR57's confidence interval
entirely.

And there is no threshold that rescues it:

```
chi² of a correct decryption of a flat plaintext : 0.04289
chi² of a wrong-key decryption                   : 0.04357
chi² of a language plaintext                     : 0.00017
→ a threshold set to admit the correct answer also admits 461/500 wrong keys (92%)
```

The real corpus sits exactly where this predicts: observed ciphertext chi² **0.03917**,
**70× worse** than a language-shaped text and statistically indistinguishable from
the wrong-key distribution. **The corpus itself is in the filter's rejection region.**

---

## 4. What is withdrawn, and what is not

**WITHDRAWN: the evidential value of the 34-billion-seed sweep.** Zero survivors is
not a partial null over seed space. It is the filter's output on *any* input
resembling this corpus, correct seed included. The sweep neither supports nor
weakens the PRNG hypothesis; it is silent. The standing note that the corner is "not
exhaustively swept" understates this — the issue is not coverage but that the
instrument cannot register a hit.

**NOT WITHDRAWN: the scoreboard's `prng-seed` EXCLUDED verdict**, which carries
score −1000 alongside transposition, monoalphabetic and ct-autokey-global. Those sit
on the model-independent premise checks (isomorph abundance, depth scope, re-sync
events), not on the seed sweep. Nor the keyspace ledger's `PRNG-seed × GAK` MOOT,
which rests on the offline-author argument. I audited the filter, not those.

**Consequence for the roadmap.** My own FR58/FR59 horizon advised "extend PRNG
*families*, not seeds." That is insufficient and I am correcting it: **extending
families under this filter would produce another uninformative null.** The filter
must be replaced before any further sweep is worth GPU time.

---

## 5. THE REPLACEMENT — the skeleton is a savage filter and needs no language

The project already owns a discriminator that requires no plaintext assumption. Any
candidate `C` implies values for the 46 determined glyphs, and those must satisfy the
**379 within-component relations**, drift-free, plus injectivity plus FR27's packing.

Its selectivity, measured in FR59: a random alphabet produces **310 contradictions**
and fits **0 / 300** times. Against chi²'s measured discrimination of **zero** at the
certified inventory, that is not an improvement in degree.

| filter | needs a plaintext assumption? | discrimination at inventory ~84 |
|---|---|---|
| chi² pre-filter | yes — language-shaped frequencies | **none** (gap/sd = −0.14) |
| skeleton consistency | **no** | random `C` rejected 300/300 |

Cost is ~379 modular subtractions and a constant-check per candidate — trivially
GPU-parallel, comparable to the chi² kernel it would replace. This is the concrete
engineering change that would make a PRNG sweep meaningful, and it is the same
asymmetry argued in the anchor discussion: **hunt orderings, not correspondences**,
because an ordering is instantly falsifiable and a correspondence is not.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift unpinned
with H4 the only surviving hypothesis.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| 34B-seed sweep | partial null; corner not exhausted | **UNINFORMATIVE** — the filter cannot register a hit on this corpus |
| chi² pre-filter | calibrated and trusted (FR-era diagnostic) | **correctly calibrated, wrong objective**; no power above inventory ~60 |
| "extend PRNG families, not seeds" (FR58/59 horizon) | my recommendation | **CORRECTED** — replace the filter first, or the null repeats |
| EyeStat `best_lang` output | language attribution | **shape match only**; does not identify a language |
| skeleton as a candidate filter | used for pins | **promoted** — the language-free replacement for chi² |
| scoreboard `prng-seed` EXCLUDED | premise-check based | **unchanged** — not audited here, rests on other grounds |

---

## 8. Horizon

1. **Re-point EyeStat at the skeleton filter.** This is the highest-value engineering
   item in the project: it converts an instrument that provably cannot succeed into
   one whose false-positive rate is effectively nil, at similar cost per candidate.
   Until then no PRNG sweep — new families or otherwise — is worth running.

2. **Count the MSB states on the glyph pictures** (FR59 §4). Still the cheapest open
   question, still symmetric, still needs no binary.

3. **Settle the radix** (`GHIDRA.md` base-7 vs corpus base-5). Load-bearing for FR58
   and FR59.

4. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering); and
   the success criterion, which FR57 made decidable and which remains undecided.
