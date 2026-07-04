# Noita Eye Puzzle — State of the Solve

A single, citable summary of where the investigation stands: what is **proven**,
what is a **working hypothesis**, what is **excluded/retracted**, what is
**open**, and what would **break it open**. Every SOLID claim is backed by a
self-tested module and is reproducible; every hypothesis is flagged as such.
Companion math: `FINGERPRINT.md`, `cribscan/CRIBSCAN_MATH.md`, and the per-topic
reports in `report/`.

---

## TL;DR

The cipher **family** is pinned to a linear class and the corpus is **provably
hard-but-not-hopeless**, but it is **not decrypted**. The one bottleneck is an
**external glyph → character (value-ordering) anchor** — or, equivalently, a
**correct crib** — because the ciphertext alone links the alphabet without
ordering it. New this cycle: a **second, cross-validating crib target** in
Triplet 3 that, together with the refrain, reaches **87–90 % of the alphabet**
with **35 symbols of mutual constraint** — sharpening the correct-crib route from
one lever to two.

---

## The corpus (data) — SOLID

- **9 messages**, alphabet **N = 83** (symbols 0–82), **1036** glyphs. Order:
  East 1, West 1, East 2, West 2, East 3, West 3, East 4, West 4, East 5. **No
  West 5.**
- Each glyph is a **base-5 trigram** (3 eye-marks), verified three ways
  including the **hard-coded constants decompiled from `noita.exe`**
  (`SpawnSecretEyes`): all **9/9 decode to the corpus byte-for-byte**.
- **Provenance settled:** the messages are hard-coded constants the engine only
  unpacks and draws — no key or keystream in the binary. The cipher was applied
  **offline by the author**, which is *why every in-game PRNG-seed scan was
  null* (moot, not merely unswept).

## What it is NOT — SOLID exclusions

| Family | Verdict | Basis |
|---|---|---|
| Monoalphabetic substitution | excluded | flat unigram, IoC≈uniform |
| Transposition / periodic / block | excluded | structure tests |
| AES-128-CTR (salakieli file cipher) | excluded | N=83≠256; decrypts to noise |
| Independent-column / unrelated-alphabet OTP (general GAK) | excluded | isomorphs require *interrelated* alphabets |
| Trifid / fractionation on the 3 eye-marks | excluded | per-mark streams ~uniform; no period; digit-transpose sweep clean |
| Ciphertext-autokey (any lag) | excluded | difference would propagate; E1/W1 show **5 clean re-sync events** (`resync`) |
| Periodic Vigenère / Alberti / plaintext-autokey lag-1 | excluded | constraint-count on clean anchors (`model_power`: periodic ~6400, autokey ~7500, Alberti ~7400 contradictions vs 0 for the linear class) |
| Small-seed PRNG keystream (any combiner) | moot | offline-authored; every additive/GAK seed scan (34B+ in EyeStat) null |
| Structured alphabet construction (affine/power/pre-shift power/closed trigram-digit/deck/keyword-columnar × 4 frames × orientations) | excluded | ~9M scored hypotheses, zero survivors, extremes at chance (`alphabet_sweep`) |

## What it IS — SOLID (model-independent or strongly validated)

- **Interrelated alphabets.** True isomorphs at **z ≈ 117** vs a shuffle null —
  only possible with interrelated per-position alphabets.
- **Linear-class cipher.** On clean anchors the progressive-consistency test
  gives **0 contradictions** and excludes periodic/autokey/Alberti; it confirms
  the **class** `{pmp, pure, beaufort}`, not `pmp` uniquely (`model_power`).
- **Triplet structure (model-free, `shared_structure`).**
  - **Triplet 1 (E1/W1/E2)** shares a ~22-glyph opening; **Triplet 3
    (E4/W4/E5)** shares ~18 — both far above the random-aligned null (~5–7).
  - **Triplet 2 (W2/E3/W3)** shares no long opening; **E3 is structurally
    distinct** (longest message). A cross-triplet passage exists (`W2/E4/W4`).
  - `EyeWitness` adjudicates **TRIPLETS (Theory 2)** over pairs-plus-E5 by 76
    logL, surviving header-stripping; E5 sits *inside* a clique.
- **Header.** Positions 1–2 are a **literal universal (66,5) marker**
  (p≈3e-12), not body keystream; it does not encode 34.
- **Per-triplet keystreams.** Only within-triplet pairs are in depth (cross
  z≈−0.5); each triplet carries its own keystream (`keystream_scope`).
- **Contamination-resistant anchors.** The clean, fully-aligned same-plaintext
  isomorphs are recoverable at precision/recall ≈ 1.0 on planted ground truth
  (`chain_extract`); the filter is **model-robust** (pmp and free-δ flag the
  identical clean/contaminated split).
- **Two sharp crib targets (this cycle).** The refrain (T1) region and the
  **Triplet-3 dof-1 passage** (`E4@50/W4@52/E5@51`, `L=30`) are each a genuine
  same-plaintext set; jointly they reach **72/83 symbols (87 %)**, 75/83 with the
  T1 opening, with **35 symbols overlapping** for cross-validation. Verified;
  see `cribscan/CRIBSCAN_MATH.md` §3 and `passread.py`.

## Working HYPOTHESES (model-dependent — flagged, not proven)

- **The specific class member.** `pmp` (per-message-progressive) is the leading
  reading and is *consistent*, but pure-progressive and Beaufort fit as well; the
  literal header would collapse pmp→pure within the family. Treat drift and sign
  as unknowns to sweep, not as fixed.
- **The refrain dof=2 template** (forced-same `(3,13),(4,5),(10,16)`) and the
  **Triplet-3 dof=2/relative-plaintext classes** `{1,11},{2,9},{4,12}` are
  model-dependent structural cribs — use them to GENERATE and TEST candidates,
  never as confirmation by themselves.
- **EyeScoreboard ranking.** Premise YES (isomorph z≈112); Rank 1 pmp SUPPORTED,
  Rank 2 pure SUGGESTIVE; free-δ/autokey-1 PERMISSIVE; whole families excluded.

## EXCLUDED / RETRACTED approaches (so we don't repeat them)

- **IoC hill-climbing** to recover the alphabet — proven degenerate (near-true
  IoC on a *wrong* alphabet; IoC is order-blind).
- **"Plaintext is Finnish (not English)"** — RETRACTED; wrong phrases fail the
  structural filter even on a genuine-English plant, so phrase failure says
  nothing about language. Language remains unknown.
- **Blind phrase-guessing / bigger crib word lists** — near-hopeless and
  *counter*-productive; more candidates widen the space. Narrowing comes from
  **stacking** compatible anchors + a coverage gate, not a bigger list.
- **Pattern-mode crib testing on one target** — ~98 % permissive under a sliding
  cipher (ciphertext reflects `p+t`, not `p`). *Superseded this cycle:* joint
  placement across two overlapping targets adds 35 hard equality checks and is
  not permissive (`CRIBSCAN_MATH.md` §3b).
- **"The Triplet-3 passage yields 48 sound ordered pins"** — RETRACTED (mine).
  It links 48 symbols but does not order them past the wall; the "48 pins" was a
  solver-extraction bug, caught by running the export on a known-distinct plant
  (it returned 1). Certified sound-pin counts come from `iso_relax`, not
  hand-rolled solvers. `passread.py` reports linkage, not ordering.

## The OPEN problem & what would break it

**The glyph value → character ordering is the bottleneck** — the one thing not
derivable from ciphertext alone, needed to *read* any recovered structure. The
alphabet **links but does not order**: `iso_relax` exports 16 sound pins,
`support_min` needs ~22 to converge (100 % by 40), and the anneal's overfit
control shows the current floor ≈ a shuffled-corpus floor. All downstream
readers (`support_min`, `order_anneal`, `ordering_bridge`, `passread`) are
validated on plants and ready the moment the alphabet crosses linked→ordered.

**What would break it open (priority order):**
1. An **external glyph→letter anchor** (font/value map, acrostic, community
   Rosetta) — model-independent, unlocks reading directly.
2. A **correct crib on either sharp target.** A correct guess *orders* the
   symbols it covers. The refrain (59 symbols) and the Triplet-3 passage (48)
   overlap in 35, so a **jointly-consistent pair of guesses** orders ~72 symbols
   — past `support_min`'s floor — and the 35-symbol overlap rejects wrong pairs.
   This is the sharpened correct-crib route; drive `passread.place_crib` +
   refrain crib under an overlap gate from a salakieli / noita-lexicon list.
3. **New independent repeated structure** — more same-plaintext anchors. Run
   `iso_relax` against the Triplet-3 and cross-triplet (`W2/E4/W4`) structures
   for a *certified* pin count and, if it lifts the floor, feed `support_min`.

## The audit chain (reproducibility)

```bash
python3 noita_eye_core/selftest.py        # aggregate math gate
python3 eyewitness/binary_provenance.py   # decompiled noita.exe -> corpus 9/9
python3 eyewitness/shared_structure.py    # model-free triplet / repeated-passage map
python3 eyewitness/eyescoreboard.py       # cipher-candidate ranking (methodology-audited)
python3 eyeforward/model_power.py         # what the consistency test proves (class, not pmp)
python3 eyeforward/iso_relax.py           # anchor densification + sound-pin export
python3 eyeforward/support_min.py         # language-free q recovery (needs ~22 pins)
python3 eyeforward/ordering_bridge.py     # same-day verdict for any ordering hypothesis
python3 cribscan/passread.py --selftest   # Triplet-3 passage reader + crib (plant-validated)
python3 cribscan/passread.py --passage t3-dof1 --L 30   # real-corpus structure + coverage
```

Every link is either **SOLID-with-evidence** or **honestly flagged as
hypothesis**; the chain records its negatives and retractions (model not
uniquely confirmed; Finnish retracted; the 48-pins solver bug) so it stays
trustworthy. Detailed reports live in `report/` and `cribscan/`.

---

*Consolidated state of the investigation. Granular fingerprint: `FINGERPRINT.md`.
Passage-attack math: `cribscan/CRIBSCAN_MATH.md`. Interactive dashboard:
`report.html`.*
