# Cipher Family Field Guide 3 — Second-Order Efforts, and the Limits of the De-Drift Channel

*Field Guide 1 fingerprinted the **mechanism** (aperiodic progressive / double-mixed
clock, scattered embedding). Field Guide 2 turned the de-drift channel on the
**plaintext content** and found it high-entropy at unigram order — near-uniform
over ~79 effective symbols, rejecting raw natural language at ~20σ. This guide
covers the attempt to push one order further — to decide **what kind** of
high-entropy source it is by recovering enough of `C` to read the bigram
structure — and reports what that attempt found. Most of what follows is a
**negative result with positive controls**, plus two retractions, plus a
reframing of the bottleneck. Negative results are first-class here: they are the
difference between "we don't know" and "we know why we don't know yet." Every
number is reproduced by the scripts in §8.*

Repo placement: `cipher_data/`. Companions: `cipher_family_field_guide_1.md`,
`cipher_family_field_guide_2.md`, `dedrift_probe.py`, `recover_c.py`.

---

## 1. The question this cycle set out to answer

Field Guide 2's unigram result is consistent with two very different plaintexts,
and they demand opposite strategies:

- **Reading A — the payload is a secondary cipher.** Compressed or encrypted
  data before the linear cipher was applied. Near-uniform at *every* order. If
  true, **no natural-language crib can ever match**, recovering `C` exposes a
  second high-entropy layer, and the entire Kalevala/word-list program (jointcrib,
  eyesieve, refrain_sweep) is aimed at a plaintext that does not exist in that
  form.
- **Reading B — the payload is a large, flat token/symbol inventory.** A
  syllabary, a game-specific glyph set, an index stream: high-entropy at unigram
  order but *retaining* bigram structure, and readable given the token map.

The discriminator is **bigram structure**. A compressed stream is flat at bigram
order (`bigram-IoC ≈ unigram-IoC²`); a token inventory or any real text is
structured (`bigram-IoC ≫ unigram-IoC²`). Measuring it requires bigram coverage
of the de-drifted stream, which requires more of `C` than the 16 verified pins
provide — they yield only ~55 adjacent pin-verified pairs. So the cycle's work
split into two efforts: **recover more of `C`**, or **squeeze a verdict out of
the 55 pairs directly**. Both failed, each for an instructive reason.

## 2. Language is not known (correction carried from the conversation)

Prior notes drifted toward treating "Finnish" as the assumed plaintext language.
It is not assumed. The live candidates are **Finnish, English, and Karelian**
(the last a standing instinct, worth testing given the repo's Livvi-Karelian
corpus). This does not soften Field Guide 2's result: Finnish, English, and
Karelian all sit at natural-language IoC ≈ 0.05–0.07, so the unigram measurement
(0.0126) rejects **all three equally** as raw text. The language question only
re-enters if the payload turns out readable at all — precisely what §3–5 could
not establish.

## 3. Effort 1 — embedding-invariant `C`-recovery, and why it can't climb

`order_anneal` recovers `C` by maximizing a **language** score, which presumes an
embedding `E` (letter↔code). With `E` scattered/unknown that objective is
mis-specified, which is a clean candidate reason the anneal stalls at the
shuffled floor. The proposed fix was an **embedding-invariant** objective: climb
`C` to maximize the **bigram IoC of the de-drifted stream** — the rate of
repeated adjacent code-pairs. Equal codes ⟺ equal letters under any bijection
`E`, so bigram IoC is invariant to the embedding: it detects *whether* the
plaintext has bigram structure without needing to know the alphabet. Fix the 16
pins, anneal the other 67 symbol positions, and use a position-shuffled objective
as an overfit floor.

**It does not work, and the reason is fundamental, not a matter of tuning.** On a
*readable* plant (real English text, encrypted with the same model), the true `C`
gives bigram IoC **0.0106** versus **0.0002** for a random `C` — a **56× signal
that unquestionably exists**. Yet the annealer, seeded with 16 true pins, reaches
only **0.0006**. Seeded with progressively more truth it crawls: 30 pins →
0.0011, 45 pins → 0.0022, **60 of 83 true pins → 0.0053**, still half of the true
0.0106.

The lesson is a general cryptanalytic truth worth stating plainly: **IoC is a
measurement statistic, not a search objective.** A bigram collision requires
several symbols to be simultaneously correct *and* a matching occurrence
elsewhere, so a single symbol-swap produces essentially zero gradient until the
permutation is already near the solution. The landscape is a narrow spike in a
flat plain. This is exactly why the field uses **bigram log-likelihood against
known language n-grams** (which gives per-symbol gradient) — and that objective is
`E`-dependent, i.e. it is `order_anneal` / `eyesieve`, which have swept ~454K
embedding hypotheses without a readable hit. So embedding-invariant recovery is
off the table (no gradient), and embedding-dependent recovery is the thing already
exhausted. `recover_c.py` implements the invariant climb with its overfit control
and a planted selftest; its honest verdict on this corpus is *inconclusive by
floor* — which, given the plant behavior, is a statement about the objective's
weakness, not evidence about the payload.

## 4. Effort 2 — direct bigram measurement on the 55 verified pairs

If we cannot climb, measure directly. De-drift the ~55 adjacent pin-verified
pairs (correct pins, no search) and compute the bigram IoC. Result: **0.0195**,
with 29 colliding bigram pairs, and — checked explicitly — **none of them part of
an extended repeat** (matching runs all shorter than 4, so not a repeated-passage
artifact like the refrain). Against simulation nulls at the same coverage, 0.0195
sat *above* every model, including 27-letter English (null ≈ 0.0015) and
uniform-83 (null ≈ 0.0002). Taken at face value this looked like **strong,
isolated bigram structure** — the Reading-B signature, even stronger than
language.

It is not real. See §5.

## 5. Retraction — the 0.0195 bigram IoC is a sampling-lattice artifact

The tell was a mathematical impossibility. A repeated bigram requires the first
symbols to match too, so **bigram IoC can never exceed unigram IoC on the same
sample** — yet 0.0195 exceeded Field Guide 2's global unigram 0.0126. Something
was non-representative. Two controls settled it:

- **The 55-pair subset is not representative.** The unigram IoC of just those 55
  first-symbols is **0.0364**, nearly triple the global 0.0126. Positions that
  happen to have a pinned neighbor are a geometrically special subset, not a fair
  draw of the plaintext.
- **The random-pin control is decisive.** Reassigning the same 16 symbols to
  **random** positions yields bigram IoC **0.0196** (mean over 500 shuffles; 95th
  pct 0.0202) — *identical* to the "true-pin" 0.0195. The elevated value is
  independent of whether the pins are correct, so it carries **zero information
  about the plaintext**.

The mechanism: at 16-pin sparsity, adjacent-pinned pairs are rare and
geometrically constrained. A bigram collision needs `q[c[t]]−q[c[t′]] = t−t′` at
two consecutive positions; when only a handful of positions qualify, the drift
arithmetic forces such coincidences among the few recurring symbols *regardless of
what `q` is*. Shuffling `q` preserves the position geometry, so the collision rate
is unchanged. **The 0.0195 measures the sampling lattice, not the language.**

**RETRACTED:** the bigram IoC of 0.0195 and any inference of "bigram structure /
Reading B" drawn from it. **CONCLUSION:** the de-drift bigram channel is
**uninformative below roughly 40 pins** — not underpowered-but-leaning, but
dominated by an artifact that swamps any real signal. Always run the
random-relabel control on any statistic derived from a sparse pinned stream; the
unigram result survives it (the pins there are cross-validated and the statistic
is first-order), the bigram result did not.

## 6. What survives, and the convergent case for Reading A

**SOLID (unchanged):** the de-drifted plaintext is high-entropy at unigram order
— IoC 0.0126, 90% CI [0.0097, 0.0156], effective alphabet ≈ 79 — rejecting
Finnish, English, Karelian, and every alphabet ≤ 53 at high significance. This
rests on cross-validated pins (within-message 9/9 and 5/5; cross-message offset
exactly 0 across independent symbol pairs) and a first-order statistic, and it
passes the artifact controls that the bigram result failed.

**UNRESOLVED:** Reading A vs Reading B. The one test that separates them is
unreachable at current coverage.

**But the weight of evidence leans A.** Three independent lines point the same
way, none conclusive alone: (a) the de-drifted output is near-uniform at unigram
order, from verified pins; (b) no embedding among ~454K swept by `eyesieve` makes
it read as language; (c) no `C` is recoverable by structural climb this session,
and the embedding-dependent climb that could recover it is (b). Each is consistent
with the payload being a **secondary cipher (compressed or encrypted)**. This is
**not proof** — a large, flat token inventory whose bigram structure is simply
invisible at 16-pin coverage remains logically alive — but nothing currently
supports B, and three things support A. Treat "secondary cipher" as the leading
hypothesis, not a finding.

## 7. The reframed bottleneck

The recurring answer to "what would break this open" has been *an external anchor
or a correct crib*, wanted to **read** the plaintext. This cycle adds a sharper,
earlier reason to want the same thing: **more pins are needed to even decide
whether reading is possible.** Bigram coverage scales as ~pins², and the sampling
artifact of §5 dissolves once adjacent-pinned pairs stop being rare — empirically,
past roughly 40 pins on a single component. So the pin count is not only the
gate to decryption; it is the gate to the A-vs-B question that determines whether
decryption is even the right goal. An external glyph→char anchor, or a correct
crib on one component (`jointcrib`), remains the lever — now doing double duty.

Concretely: below ~40 pins, do **not** invest in de-drift bigram/entropy probes
(they measure the lattice). Above ~40, the second-order channel opens and the
A-vs-B verdict becomes a direct measurement. Everything between here and there is
pin acquisition.

## 8. Corrections to prior guides

- **Field Guide 2, §6 ("extend the de-drift channel to bigram/entropy").** Mark
  **blocked pending pin coverage (≳40)**. As written it is not a ready next step;
  at 16 pins it returns a sampling artifact (§5). The *intent* is sound; the
  *coverage* is not yet there.
- **Any reference to "bigram structure / effective alphabet ~53 with token
  structure."** Superseded. The ~53 figure was the earlier refrain-inflated
  unigram (already corrected to ~79 in Field Guide 2); the bigram-structure claim
  is retracted here.
- **Field Guide 2's headline unigram result is unaffected** and remains the
  strongest direct statement about the plaintext.

## 9. Methodological notes (for the next person, including future me)

- **A measurement statistic is not a search objective.** IoC/collision measures
  read cleanly but climb terribly (flat gradient). If you must recover a
  permutation, use an objective with per-element gradient (n-gram log-likelihood)
  — which here means committing to an embedding hypothesis.
- **Any statistic from a sparse derived stream needs a relabel/randomization
  control.** The random-pin control (shuffle the assignment, keep the geometry)
  cleanly separates real structure from sampling lattice. It cost one function and
  overturned a headline.
- **Keep a mathematical sanity invariant in view.** "Bigram IoC ≤ unigram IoC on
  the same sample" caught the artifact before the controls confirmed it.
- **Positive controls make negatives informative.** The readable plant proves the
  channel *would* fire if structure were there and reachable; the real corpus not
  firing is then meaningful (bounded by the coverage caveat), not merely silent.

## 10. Reproduce

```bash
python3 dedrift_probe.py --selftest      # first-order channel (SOLID result); plant-validated
python3 dedrift_probe.py                 # unigram IoC 0.0126, effective alphabet ~79
python3 recover_c.py --selftest          # embedding-invariant climb + overfit control (Effort 1)
python3 recover_c.py                      # real corpus: climb floors -> objective too weak, not a payload verdict
```

The §4–5 direct-bigram measurement and its random-pin control are short inline
scripts (in the session log): de-drift the verified adjacent pairs, compute bigram
IoC, then recompute under 500 random 16-symbol assignments and confirm the value
is unchanged. Reference language IoCs (Finnish 0.073, English 0.066, Karelian via
`corpora/corpus-olo`) are computed by `dedrift_probe.candidate_models`.

## 11. Standing conclusion

The de-drift channel gave a strong first-order result (high-entropy plaintext,
language rejected) and a clean **null** at second order: bigram structure is
**not measurable at 16-pin coverage**, and both routes to more coverage —
embedding-invariant climb, embedding-dependent sweep — are respectively
un-climbable and already-exhausted. The leading hypothesis is that the payload is
a **secondary cipher** (three convergent lines), with a large flat token
inventory as the surviving alternative. The bottleneck is unchanged in identity
and sharper in stakes: **pins** — an external anchor or a correct crib — now gate
not just reading the plaintext but knowing whether the plaintext is readable at
all. Below ~40 pins, second-order probes measure the instrument, not the text.
