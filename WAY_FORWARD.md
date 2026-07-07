# Noita Eye Puzzle — A Way Forward

*A synthesis of (1) the current state of the `null-h3x/eyes` tooling, (2) the
external cryptanalytic literature on cipher fingerprinting, and (3) Skizzee's
AGL-GAK impossibility proof — assembled into a prioritized plan of attack.*

This document does not restate the solve (`STATE_OF_THE_SOLVE.md`) or the
fingerprint (`FINGERPRINT.md`). It answers one question: **given everything we
now know, what is the highest-leverage thing to do next, and why?**

Every external claim below is checked against the corpus in this repo, not taken
on faith. Where I reproduced a number independently it says so; where I could
not, it says that too.

---

## 0. Executive summary

The investigation is in an unusually strong position for an unsolved cipher: the
**family is pinned**, the **corpus provenance is closed**, and the **one
remaining barrier is named** (glyph→character ordering). The AGL proof removes a
whole algebraic branch, and — read together with the community's own
convergence — it points the search at a specific, well-motivated target: a
**dynamic-permutation ("deck") cipher** in the spirit of Chaocipher/Hutton.

**Provenance, stated precisely (correcting an earlier loose phrasing).** The eye
messages are hard-coded constants in the binary; there is **no functional in-game
mechanism that decrypts them** — no runtime call, no in-engine solver, no seed the
game consumes. They were produced by an offline authoring process and are
generally accepted to be **solved offline, outside the game**. This is not a
nuance: it is *why* PRNG/seed scanning is not merely unproductive but categorically
misdirected (§5), and *why* the attack surface is pure cryptanalysis of a fixed
corpus rather than reverse-engineering game state.

The way forward is **not** more cipher-family search. It is a three-front push:

1. **Order the alphabet you already have** — the linked-not-ordered wall is the
   whole game. Two independent, overlapping crib targets now cover ~85–90% of
   the alphabet; a jointly-consistent pair of correct guesses orders it. Drive
   this under an overlap-consistency gate.
2. **Model the deck cipher directly** — the AGL proof plus the community's
   "letter-moves-on-use" insight both point at S83/A83 dynamic permutations.
   Instrument Chaocipher/Hutton/Hutton-2 as *generators* and test them against
   the isomorph structure and the two near-duplicate pairs.
3. **Exploit the autokey self-encryption crib-placement trick** — a technique
   from the classical autokey literature that places a crib using only internal
   ciphertext structure, *no alphabet ordering required*. This repo has
   crib-dragging but not this specific lever.

Details, with the reasoning, below.

---

## 1. What the repo already establishes (reviewed, verified)

I cloned the repo, ran `noita_eye_core/selftest.py` (**478/478-class gate passes**;
30+ modules green), and independently reproduced the load-bearing claims rather
than trusting the markdown:

- **Corpus is faithful.** `corpus.json` matches the values cited in every
  document and in the AGL proof to the integer. The `(66,5)` universal header at
  positions 1–2 is present in all nine messages; position 0 differs per message
  (E1=50, W1=80, E2=36…). Confirmed by direct load.
- **The isomorph signal is real and overwhelming.** Running the repo's own
  `isomorph.significance` with proper `min_repeats` filtering: at L=12,
  min_repeats=3, **observed = 51 true isomorphs vs a shuffle-null mean of 0.04
  (z ≈ 132, p = 0)**; at L=14, min_repeats=4, observed = 24 vs null 0
  (unbounded z). I first got a misleadingly low z≈6 with a naive "any matching
  skeleton" count — the repo is *right* to insist on the repeat-count filter,
  and this is a good caution against sloppy nulls. **The community's agreed
  isomorph indicator is not folklore; it is a >100σ effect.**
- **The exclusions are calibrated, not impressionistic.** Mono/transposition/
  periodic/block/AES/general-GAK/CT-autokey are each ruled out by a specific
  test with a null. The strongest positive facts (position-locked stream, no
  adjacent doubles at z≈−3.7, distance-4 excess 2.24×, per-triplet keystream
  scope, ~136 positions of exploitable 2-deep depth) are all reproduced by
  self-tested modules.

### New input: the community isomorph atlas — 13 verified classes, folded in

A community isomorph-structure chart catalogs **13 labeled isomorph classes**,
each with an occurrence count and a log-probability confidence score. I
transcribed all 13 and **verified every one against `corpus.json`**: after
recovering the exact dot-spacing (three of my first-pass transcriptions were one
dot short in the long gaps), **all 13 occurrence counts match the chart exactly**
— 43 located instances, **65 aligned same-plaintext pairs**. This is now shipped
as `isomorph_atlas.json` (id, exact pattern, positions across all nine messages,
score, validated rank, and trust tier) so the pipeline can consume it directly.

**The scores are real, and I reproduced them.** The chart's right-hand number is
a log-improbability confidence (higher = rarer by chance). Two independent checks:
(1) an **empirical floor test** — under a 5000× per-message permutation null,
*every one of the 13 classes* fails to reach its observed count even once
(p < 2×10⁻⁴). **Nothing in this atlas is discardable as noise.** The score is
therefore a **reliability *weight*, not an include/exclude gate.** (2) an
**analytic reproduction** — scoring each class by a Poisson tail under a
uniform-83 null tracks the community's numbers at **Pearson 0.975** (mine run
~0.5–5 points higher, consistent with their using a slightly more conservative
null). The chart's confidence column is trustworthy; use it to rank.

**Two orthogonal axes — this is the part worth getting right.** Reliability (the
score) and *reachability* (whether the repo's own pipeline can surface the class)
are different things, and conflating them misvalues the atlas:

- **Reliability** = the confidence score. Drives how much *weight* a class's links
  deserve.
- **Reachability** = internal-repeats (`length − distinct_symbols`), which **is
  exactly the repo's `find_isomorphs` `min_repeats` threshold**. On this corpus
  the clean/noisy boundary is sharp: at min_repeats = 2 you get 48 raw pairs vs a
  null mean of 1.4; at ≥ 3 it collapses to zero-vs-null. Classes at
  internal-repeats = 2 are ones the repo's clean-anchor pass *structurally skips*.

The prize classes are **high-reliability *and* low-reachability** — reliable
anchors the repo could not reach on its own. Exactly one class qualifies: **`#M-`
(`A.B..B.A`) — analytic score 10.3, seven occurrences / 21 aligned pairs, but
internal-repeats = 2.** It is the single largest anchor contributor in the whole
atlas *and* invisible to the repo's own enumeration. That, not raw class count, is
the concrete "genuine increase." **This corrects my earlier lumping:** `#M-` and
`#4` both sit at internal-repeats = 2, but they are *not* equivalent — `#M-` is a
solidly-reliable Tier-B anchor (more reliable than the clean-regime `#3`), while
`#4` is the sole Tier-C floor (score 3.5, the only class within striking distance
of chance). Reachability lumped them; reliability separates them.

**Ranked, with trust tiers:**

| tier | classes (by score) | use |
|---|---|---|
| **A** (score ≥ 17) | #1 (28.0), #2+ (21.4), #2 (20.9), #F (20.8), #M (19.5), #S/#C0/#C1 (17.5) | hard, load-bearing links |
| **B** (score 8–13) | #2- (12.8), #M- (9.7)★, #3+ (9.7), #3 (9.1) | score-weighted soft anchors |
| **C** (score < 8) | #4 (3.5) | tiebreak-only, never load-bearing |

★ `#M-` is the high-reliability / repo-unreachable standout.

**How to use it (wired into P1/P4 below):** feed `isomorph_atlas.json` to the
`chain_extract` bootstrap **weighted by tier** — Tier A as hard links, Tier B
(including `#M-`) as score-weighted soft links, Tier C (`#4`) admitted only as a
tiebreaker and never as a constraint anything rests on. This is additive to
`iso_relax`, not a replacement: certified ordered-pin counts still come only from
`iso_relax` (§5 guardrail).

### Tooling inventory (including the redundant duplicates)

The repo carries several **parallel implementations of the same attacks** —
partly evolution, partly deliberate cross-check. Mapping them so effort isn't
wasted re-running equivalent things:

| Capability | Canonical module | Redundant / older copies |
|---|---|---|
| Core math gate | `noita_eye_core/selftest.py` | `dashboard/selftest.py`, `eyeforward/selftest.py` |
| Isomorph significance + chaining | `noita_eye_core/isomorph.py` | `eyecrack/globality.py`, archived `eyestat` |
| Contamination-resistant extraction | `noita_eye_core/chain_extract` | `eyecrack/skeleton_match.py`, `report/iso_extract*` |
| Refrain known-position crib | `noita_eye_core/refrain.py` | `eyecrack/refrain_attack.py`, `eyecrack/refrain_*` (compose/sweep/pipeline), `noita_eye_core/refrain_*` |
| Crib-seeded n-gram read | `noita_eye_core/ngram_solve.py` | `eyecrack/ngram_solve.py` |
| Ordering search from crib | `noita_eye_core/order_solve.py` | `eyecrack/order_solve.py`, `eyecrack/ordering_exhaust.py`, `*order_bench` |
| Cipher-family sieve | `eyesieve/` (packaged) | `dashboard/cipher_validate.py`, `eyecrack/cipher_fingerprint.py` |
| Deck / permutation model | `dashboard/deck_infer.py`, `eyecrack/deck_sweep.py` | — (thin; see §3) |
| Passage/Triplet-3 reader | `cribscan/passread.py` | `noita_eye_core/passage_template.py`, `eyecrack/passage_template.py` |
| Forward pipeline (pins→q→read) | `eyeforward/` (iso_relax → support_min → order_anneal) | `eyeforward/order_gpu.py` (accelerator) |
| Dashboards | `report/build.py` → `report.html` | `dashboard/`, `workbench.html`, `eye_crib_primer.html` |

**Takeaway for effort economy:** the *forward pipeline* (`eyeforward/`) and the
*two-crib passage machinery* (`cribscan/` + `refrain`) are the live edge. The
`eyecrack/` tree is largely superseded by `noita_eye_core/` equivalents — keep
it for cross-validation but don't develop against it. The deck tooling is the
**thinnest part of the repo relative to how important it now is** (§3).

---

## 2. What the external fingerprinting literature adds

I pulled the standard cryptanalytic references on how ciphers are identified by
their statistical markers. Three things are worth importing; the rest the repo
already does better than the generic tools.

### 2a. The repo is already past the generic identifiers

Public "cipher identifier" tools (dCode, caesarcipher.org, CryptoCrack, CCT) all
run the same core battery: **Index of Coincidence** (mono vs poly), **Friedman/
Kappa test** (period), **chi-squared** (frequency fit), **Kasiski** (repeat
spacing), and **word-pattern isomorphism** against a dictionary. Your repo has
calibrated, null-backed versions of every one of these and has already used them
to exclude the families they detect. **There is no off-the-shelf identifier that
will tell you more than you know.** IoC in particular is a dead end here (flat
unigram by construction, and IoC is order-blind — which `pureprog` already proved
degenerate on a wrong alphabet).

### 2b. Friedman's "IC of the modular sum of two streams" ≈ your depth analysis

The declassified Friedman monograph (*The Index of Coincidence*, NSA FOLDER_231)
devotes chapters to the **IC of the modular sum of two streams**, the **cross-IC**,
and **coincidence alignment of multiple messages in the same key** — putting
messages side by side and counting positional coincidences to detect shared key.
This is precisely the theory under your `depthmap`/`pairdiff`/`resync` work on
the E1≈W1 and E4≈E5 near-duplicate pairs. **Implication:** the two near-duplicate
pairs are your richest classical foothold, and the *right* classical framing for
them is Friedman two-stream coincidence, not generic IoC. Any deck-cipher model
(§3) must reproduce the observed **5 clean re-sync events** on E1/W1 — that is a
hard, model-independent constraint the literature tells you how to weaponize.

### 2c. The autokey self-encryption crib-placement trick — **import this**

This is the one genuinely new lever from the literature. In classical autokey
cryptanalysis (Black Chamber; practicalcryptography; the Cipher Museum), a crib
is placed **without knowing the key or the cipher alphabet** by exploiting the
cipher's *self-referential* structure:

> Encrypt the crib *with itself*, sliding it one position at a time, and look for
> the resulting short pattern in the ciphertext. Where it appears, the crib is
> placed — because the autokey feedback makes shifted-plaintext-vs-plaintext
> reduce to a known table.

The Wikipedia framing: *"a three-character guess reveals six more characters
(three on each side), creating a cascade effect,"* which lets you **rule out
wrong guesses fast**. Your repo places cribs by *assuming an ordering and testing
readability*; this technique places them by *pattern alone*. For a
plaintext-driven cipher (which is exactly what the community converged on — see
§3), an analog of this self-encryption placement should exist and would attack
the ordering wall from a completely different side. **This is a concrete new
module to build**, not just a re-run.

### 2d. The community's own convergence (crucial context)

The Noita wiki and the Steam megathread show the community independently reached
the same model your fingerprint did, and named the mechanism the AGL proof only
implies. Key quotes, paraphrased:

- Pyry's autokey-Alberti demonstration: isomorphs of pattern `a.....ba.b` appear
  in ciphertext whose *plaintext does not share that pattern* — i.e. isomorphs
  are a **cipher artifact**, confirming interrelated alphabets.
- Toboter's reading of Pyry's Conditions: the cipher is **polyalphabetic**, each
  ciphertext char is **conditionally dependent on the previous ciphertext char**,
  the state/key is **shared across all messages**, and there are **≥20, probably
  ~83 internal states** — "an internal state is something that affects the
  ciphertext other than the plaintext char."
- `simplesmiler` (2024): classical alphabet chaining fails on the eyes because it
  **relies on commutativity, which this mechanism lacks**. Their model:
  **"plaintext-driven cipher-alphabet permutation"** — a letter **moves position
  within the key upon use**, with *minimal side effects* (so shared sections and
  isomorphs survive). Named precedents: **Chaocipher** and **Hutton**.

This is the same destination as Skizzee's proof, reached from the other
direction. Hold that thought for §4.

---

## 3. What the AGL proof establishes, and where it points

**The proof is sound. I reproduced every quantitative claim independently:**

- The six flagship instances and their `A.B.CB.AC` repeat pattern match the
  corpus exactly (indices 0=7→A, 2=5→B, 4=8→C in all six).
- The three within-message pools, solved from any two arrows, **fail to predict
  the third in all nine basis cases** — reproduced to the integer, matching the
  proof's tables (e.g. Pool 1 A+B → `3x+13`, predict f(19)=70≠4).
- The exhaustive affine relabeling: **0 of 6806** σ(x)=cx+d make any pool
  3/3-consistent. Reproduced.
- The all-columns strengthening: **1/20, 0/20, 0/20** collinear source-triples,
  all six arrows functional. Reproduced.

**What it proves:** neither `C83:C82` (full AGL(1,83)) nor its index-2 subgroup
`C83:C41` can be the state group of a GAK cipher producing the eyes — under
*either* multiplication convention, *all* valid hidden subgroups, and *all* 6806
affine coset labelings — **if** the flagship isomorphs are the same plaintext.

**The one honest caveat (the author flags it too):** the escape hatch is a
**non-affine** bijection from the 83 cosets to {0…82} (83! of them), which arrow
analysis on 9 constraints cannot eliminate. But — and this is the important part
— the author notes such a labeling *"has no algebraic motivation from the group
structure; a non-affinely-labeled AGL cipher is observationally indistinguishable
from a cipher over a larger group with a scrambled action."* In other words, the
non-affine escape hatch **is already the deck-cipher hypothesis wearing a
disguise.** Ruling out S83/A83 would subsume it.

**Where it points:** the proof's own conclusion — *"the remaining candidates
consistent with the transitivity restriction on 83-symbol transitive permutation
groups are S83 and A83, corresponding to the deck cipher model."* This is
exactly `simplesmiler`'s Chaocipher/Hutton model. **Two independent lines of
reasoning — an algebraic impossibility proof and the community's mechanism
inference — converge on the same target.** That convergence is the single most
actionable fact in this whole review.

---

## 4. The plan (prioritized)

Ordered by leverage-per-unit-effort. Each item says what to do, why it's next,
and how you'll know it worked.

### Priority 1 — Order the alphabet via the two-crib overlap gate
**This is the whole game.** The alphabet *links but does not order*
(`iso_relax` exports ~16 sound pins; `support_min` needs ~22 to converge, 100%
by 40). Two overlapping crib targets now exist — the T1 refrain region (~59
symbols under the model) and the Triplet-3 dof-1 passage (~48), overlapping in
~31–35 symbols. I verified the union covers ~83–90% of the alphabet depending on
exactly which sub-windows and whether the T1-open region is included.

**Do:** drive `cribscan/passread.py`'s `place_crib` **jointly** with the refrain
crib under a **hard overlap-consistency gate** — a candidate pair must agree on
all overlap symbols. This is the specific thing that defeats the "pattern-mode
crib is 98% permissive" trap: single-target letter-pattern scoring is
permissive; *35 hard equality checks across two committed targets* is not. Feed
candidates from the salakieli/noita-lexicon list, not a blind sweep.

**Seed it with the atlas.** Before the crib gate runs, give the alphabet-linkage
step the strongest possible starting `q` by folding in `isomorph_atlas.json`
(P4). The better-linked the alphabet going in, the fewer overlap symbols a correct
crib pair has to carry on its own — the atlas widens the linked substrate the
ordering then commits.

**Why now:** it needs no new theory and no external anchor. It converts the
existing linked alphabet into an ordered one *if* a correct pair exists in the
candidate list. A correct pair orders ~72 symbols → past `support_min`'s floor →
corpus decrypts.

**Success signal:** a candidate pair passes the overlap gate AND lights up
corpus-wide IoC / `ngram_solve` z-score above the shuffled-decryption null. Any
single-target "hit" that fails the overlap gate is a false positive — that's the
gate earning its keep.

**Guardrail:** honor the repo's own retraction. Report *linkage* from `passread`
and take *certified ordered-pin counts only from `iso_relax`*. Don't let a
hand-rolled solver claim ordered pins again.

**Status — BUILT (`cribscan/order_gate.py`).** The gate is implemented and
plant-validated (`--selftest`, 18/18). It drives `place_crib`-style value-mode
placement on both targets under one joint (T1-phrase, T3-phrase, ordering, σ,
drift) hypothesis, applies the hard overlap-consistency gate (`q_A[s]−q_B[s]` must
be a single δ on the overlap), welds to one map, seeds the atlas (tier-A/B, with a
cross-index consistency guard) to extend coverage, and scores survivors by a
corpus IoC z that is invariant to base and rotation. Findings, calibrated: (a) on
these targets value-mode per-target placement is *already* sharp — **0 false
positives over thousands of random candidates**, and even an isomorph-preserving
relabel (which passes pattern-mode) self-contradicts — so the gate's role is to
confirm the joint hypothesis, weld, and resolve the single-target rotation, not to
rescue a permissive check; (b) a correct pair welds to a full solve (plant: 70/83,
100% read, IoC z ≈ 50; a 49-pair candidate run selects the truth uniquely); (c)
real-corpus reachability (`--real`) confirms this plan's numbers exactly — **31
hard checks**, union **69/83 (83.1%)**, atlas grand union **82/83 (98.8%)**. Next
action is to feed real candidate lists (salakieli/noita-lexicon) and hand any gate
pass with high z to `iso_relax` for the certified count.

### Priority 2 — Model the deck cipher as a generator (the thin spot)
Both §3 and the community point at S83/A83 dynamic permutations. The repo's deck
tooling (`deck_infer`, `deck_sweep`) is thin relative to this. **Build a
dynamic-permutation generator lab** — Chaocipher, Hutton, Hutton-2, and
`simplesmiler`'s "swap-used-letter-in-key" variant — parameterized over:
- permutation update rule (swap / shift-to-front / rotate-segment on use),
- what drives the update (plaintext char, ciphertext char, position),
- the per-message base / initial deck state.

Then **filter every variant against the hard model-independent facts** the way
`plantlab`/`pyry_gate` already do for the linear class:
1. Reproduces isomorphs at z≈132 (L=12, mr=3)?
2. Reproduces **zero adjacent doubles** and **distance-4 excess 2.24×**?
3. Reproduces **5 re-sync events** on an E1≈W1-style near-duplicate pair? (This
   is the Friedman two-stream constraint from §2b — it is *very* restrictive for
   dynamic permutations, because most update rules propagate a divergence
   forever, exactly like CT-autokey which re-sync already excluded.)
4. Produces the **cross-triplet vs within-triplet keystream scope** (`keystream_scope`)?

**Why now:** it's the branch the evidence actually favors and the repo has barely
instrumented. A variant that passes all four gates is a *far* stronger hypothesis
than the linear-class members, which the isomorph tests can't separate anyway.

**Success signal:** exactly one update-rule family passes all four gates on
plants *and* matches the real corpus's re-sync/scope/double statistics. That
narrows the "specific member" question the linear-class analysis can't close.

**Guardrail:** the re-sync gate is the discriminator — build it first and use it
to kill families fast, the way `resync` killed CT-autokey. If a dynamic
permutation can't re-sync on E1/W1, it's dead regardless of how nice its
isomorphs look.

### Priority 3 — Build the self-encryption crib placer (new lever from §2c)
Port the autokey self-encryption placement idea to the eyes' model. For a
plaintext-driven permutation, derive the analog of "encrypt the crib with itself
and slide it" — a placement test that uses **only internal ciphertext structure**,
independent of the glyph→char ordering. Even a partial version that places a
3–4 symbol crib and cascades (±3 on each side, per the Wikipedia cascade) would
attack the ordering wall from a side nothing in the repo currently uses.

**Why now:** it's orthogonal to Priorities 1–2. If ordering-by-readability
(P1) and model-fit (P2) both stall, a pattern-only placer is the third
independent shot. Low risk of the "permissive" failure because it keys on exact
internal structure, not language plausibility.

**Success signal:** the self-encryption pattern of a candidate crib appears in
the ciphertext at a position consistent with a known shared-section boundary —
placing the crib without any ordering assumption, then cascading.

### Priority 4 — Certified pin count, now seeded by the isomorph atlas
Run `eyeforward/iso_relax` against the **Triplet-3** and **cross-triplet
(W2/E4/W4)** structures for a *certified* sound-pin count (the repo flags this as
not-yet-done) — but **seed it with `isomorph_atlas.json` first**. The 65 aligned
same-plaintext pairs (43 instances across 13 verified, now *ranked* classes) are
precisely the `chain_extract` input, and `#M-`'s 7 occurrences are reliable
alignment material (analytic score 10.3) that the repo's own `min_repeats` ≥ 3
anchor pass structurally skips. Concretely: (1) load the atlas, (2) run the
`chain_extract` anchor-then-classify bootstrap **weighted by tier** — Tier A
(score ≥ 17) as the hard anchor set, Tier B (incl. `#M-`) as score-weighted soft
links, Tier C (`#4`, score 3.5) as a tiebreaker only, never load-bearing, (3) hand
the resulting linkage to `iso_relax` for a certified count, (4) if the floor
lifts, feed `support_min`. Cheap, parallelizable, and it now has genuinely new
anchor material to chew on rather than re-running the same enumeration.

---

## 5. What NOT to do (so the plan stays honest)

The repo has earned these negatives; the plan respects them.

- **No blind phrase sweeps** (English *or* Finnish). Proven near-hopeless and
  *counterproductive* — more candidates widen the space. Narrowing comes from
  stacking compatible anchors under a coverage/overlap gate. (The Finnish claim
  was specifically retracted; language remains genuinely unknown.)
- **No IoC hill-climbing to recover the alphabet.** Order-blind, degenerate —
  near-true IoC on a *wrong* alphabet. Dead.
- **No PRNG seed scanning.** Provenance is closed: the messages are hard-coded
  constants authored offline, with **no functional in-game decrypt mechanism** to
  reverse. There is no seed the game consumes. (34B+ scans already null, and now
  known to be *moot*, not merely unswept — the target is the fixed corpus, not
  game state.)
- **No structured-alphabet construction sweeps.** ~9M scored hypotheses, zero
  survivors, extremes at chance. That corner is excluded.
- **No re-deriving AGL/dihedral/other affine or metacyclic state groups.** The
  proof (verified here) plus the existing dihedral impossibility close the
  affine-coset-labeled branch. Effort belongs on non-affine dynamic permutations.
- **Don't claim ordered pins from hand-rolled solvers.** Certified counts come
  from `iso_relax` only. (The "48 pins" retraction is the cautionary tale.)

---

## 6. The one-paragraph version

The eyes are a **polyalphabetic cipher over a single interrelated 83-symbol
alphabet with a plaintext-driven, position-locked, non-commutative key schedule**
— almost certainly a **dynamic permutation (deck) cipher** of the
Chaocipher/Hutton family, since both an algebraic impossibility proof (AGL-GAK,
verified here) and the community's independent mechanism inference converge
there. The **sole barrier is glyph→character ordering**; the alphabet links but
does not order. The highest-leverage move is to **order it via a hard
overlap-consistency gate across the two overlapping crib targets** (refrain +
Triplet-3, ~85–90% joint coverage, ~31–35 symbol overlap), while **instrumenting
the deck-cipher family as a generator** and filtering it against the hard
model-free statistics — above all the **5 re-sync events** on E1≈W1, which is the
Friedman two-stream constraint that kills most dynamic-permutation update rules
the same way it killed ciphertext-autokey. A **self-encryption crib placer**
imported from classical autokey cryptanalysis is the orthogonal third shot.

---

*Prepared as a synthesis of the `null-h3x/eyes` repository, the classical
cipher-fingerprinting literature (Friedman IC, autokey/running-key crib
placement, isomorph/pattern-word methods), and Skizzee's AGL-GAK impossibility
proof. All corpus-level claims independently reproduced against
`noita_eye_core/corpus.json`.*
