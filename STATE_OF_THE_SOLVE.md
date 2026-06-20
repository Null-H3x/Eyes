# Noita Eye Puzzle — State of the Solve

A single, citable summary of where the investigation stands: what is **proven**,
what is a **working hypothesis**, what is **excluded/retracted**, what is **open**,
and what would **break it open**. Every claim is backed by a self-tested module in
`noita_eye_core/` (aggregate gate: `python3 noita_eye_core/selftest.py`, currently
**478/478**) and is reproducible. Companion docs: `FINGERPRINT.md` (detailed
fingerprint), `report.html` (dashboard), and the per-topic reports in `report/`.

---

## TL;DR

The cipher **family** is pinned down and the corpus is **provably hard-but-not-
hopeless**, but it is **not decrypted**. The single remaining bottleneck is an
**external glyph → character (value-ordering) anchor**: every model-independent
structural lever has been mapped, and reading the plaintext requires knowing which
glyph value is which character — the one thing not derivable from the ciphertext
alone.

---

## The corpus (data) — SOLID

- **9 messages**, alphabet **N = 83** (symbols 0–82), **1036** glyphs. Order: East 1,
  West 1, East 2, West 2, East 3, West 3, East 4, West 4, East 5. **No West 5.**
- Each glyph is a **base-5 trigram** (3 eye-marks). Verified three independent ways:
  community BASE10 (WarFairy), the trigram xlsx, and — decisively — the **hard-coded
  constants decompiled from `noita.exe`** (`SpawnSecretEyes`): all **9/9 messages
  decode to the corpus byte-for-byte** (`provenance`, `binary_provenance`).
- **Provenance settled:** the messages are hard-coded constants the engine only
  unpacks and draws — **no decryption, key, or keystream in the binary**. The cipher
  was applied **offline by the author**, which is *why every in-game PRNG-seed scan
  was null*.

## What it is NOT — SOLID exclusions

Each is a calibrated test, not an impression (modules in parentheses):

| Family | Verdict | Basis |
|---|---|---|
| Monoalphabetic substitution | excluded | flat unigram, IoC≈uniform (`classify`,`stats`) |
| Transposition / periodic / block | excluded | structure tests (`classify`) |
| AES-128-CTR (salakieli file cipher) | excluded | N=83≠256; decrypts to noise (`salakieli_aes`) |
| Independent-column substitution (general GAK) / unrelated-alphabet OTP | excluded | abundant isomorphs require *interrelated* alphabets (`isomorph`) |
| Trifid / fractionation on the 3 eye-marks | disfavored | per-mark streams ~uniform; no period signal (`trifid`) |
| Small-seed PRNG keystream | disfavored→moot | every additive/GAK seed scan to 100M null; provenance shows no in-game seed |

## What it IS — SOLID (model-independent or strongly validated)

- **Interrelated alphabets.** True isomorphs (same repeat-pattern, different values)
  at **z ≈ 117** vs a shuffle null — only possible with interrelated per-position
  alphabets. Rules out the families above (`isomorph`).
- **Triplet structure (model-free).** Depending only on "same glyph = same glyph":
  - **Triplet 1 (E1/W1/E2)** shares a **~22-glyph opening**; **Triplet 3
    (E4/W4/E5)** shares **~18** — both far above a random-aligned null (~5–7).
  - **Triplet 2 (W2/E3/W3)** shares **no** long opening; **E3 is structurally
    distinct** (weakly linked to all; longest message).
  - The opening passage also **repeats within** messages (e.g. E1@39 and E1@67), and
    a cross-triplet passage exists (W2/E4/W4). **No universal opening** beyond the
    `(66,5)` header. (`shared_structure`, report `shared_structure_report.md`.)
  - This rigorously confirms the original "messages come in triplets" theory.
- **Header.** Positions 1,2 are a **literal universal `(66,5)` marker** (cross-message
  agreement p≈3e-12), not body keystream; it does **not** encode the number 34
  (`header_test`, `numbertest`).
- **Contamination-resistant extraction.** The clean, fully-aligned isomorphs
  (same-plaintext anchors) are recoverable at precision ≈1.0 / recall ≈1.0 on
  planted ground truth (`chain_extract`).

## Working HYPOTHESES (model-dependent — flagged, not proven)

- **Per-message-progressive body cipher** `c[m][t]=C[(p[t]+base_m+t)]`. It is the
  leading model and is *consistent* with the data, but the **model-verification audit
  did NOT uniquely confirm it**: pure-progressive fits nearly as well, and a small
  fraction of random windows pass the same consistency tests (`model_audit`,
  `model_audit_report.md`). Treat as a hypothesis.
- **The dof=2 refrain template** (the 22-glyph refrain's relative plaintext pinned to
  a 2-parameter family; forced-same letters at positions (3,13),(4,5),(10,16)). This
  follows from the per-message-progressive model and is therefore **model-dependent**;
  do not treat a template match as confirmation by itself (`template`).
- **Pure-progressive** (single global sliding alphabet) remains a live alternative;
  the literal header would force it within the per-message-progressive family.
- **EyeScoreboard ranking (`eyescoreboard`).** Methodology-audited scoreboard that
  ranks interrelated-alphabet models on plant discrimination, real-corpus GF
  contradiction rate (the metric that actually differs), and refrain extent.
  **Premise (block-difference + triplet depth): YES** (isomorph z≈112). **Rank 1:**
  per-message-progressive **SUPPORTED** (real contra 10.9% vs pure 15.0%; refrain
  L=22 vs L=21). **Rank 2:** pure-progressive **SUGGESTIVE** (within 1 glyph on
  refrain). **free-δ / autokey-1:** PERMISSIVE (0% real contradictions). Whole
  families EXCLUDED (mono, OTP, AES, transposition, PRNG, CT-autokey, general-K).
  **Triplet combine probe (meta-trigram hypothesis):** sum mod 83 and base-5
  digit-sum across triplet members show IoC ≈ shuffle null (z≈0.5–2) — symbols are
  **not** composites of the three messages in a triplet. Report:
  `report/eyescoreboard.md`.

## EXCLUDED / RETRACTED approaches (so we don't repeat them)

- **IoC hill-climbing** to recover the alphabet — **proven degenerate** (reaches
  near-true IoC on a *wrong* alphabet; IoC is order-blind). Do not use.
- **"Plaintext is Finnish (not English)"** — **RETRACTED**. Wrong English phrases
  fail the structural filter at 0/300 *even on a genuinely-English plant*, so phrase
  failure says nothing about language. Language remains unknown.
- **Blind phrase-guessing** — near-hopeless: random phrases pass the structural filter
  at ~0/300 in any language (only the exact repeat-structure passes). Use
  `refrain_sweep` to filter candidates by template instead.
- **Expanding the crib word list to "narrow" the refrain** — does the OPPOSITE.
  The refrain's only mandatory double letter is at positions (4,5) (the `BB`), and
  ~161 `XYY` words plus ~25k words (via word endings / internal doubles) can fill it;
  more candidates *widen* the space. Even a character-trigram model ranks English-
  flavoured gibberish at the top. Narrowing comes from **stacking** compatible
  anchors + a word-coverage gate (`refrain_compose`), not from a bigger word list.

## Refrain double-letter structure (model-dependent, `refrain_compose`)

Within the 22-glyph refrain, an adjacent **doubled letter is possible ONLY at (4,5)
[forced] and optionally (6,7)/(7,8)**; every other adjacent pair is forced-different.
The forced (4,5) double is the skeleton's `BB`. Use the composer to (a) report the
double map (`--doubles`), (b) list template-compatible offsets for expected words and
*fragments* (`--offsets god eye see …`), (c) enumerate **joint placements** that
stack several expected words (`--compat god see eye` → `godseeye…`), and (d)
trigram-fill + wcov-rank a shortlist (`--anchor god --anchor see`). Output is a
candidate SHORTLIST for `order_solve`, not a read — the glyph→char ordering is still
required. (`refrain_compose.selftest` 23/23.)

## The OPEN problem & what would break it

**The plaintext-alphabet ordering (glyph value → character) is the bottleneck.** It is
the one thing not derivable from the ciphertext alone, and it is needed to *read* any
recovered structure. With it:
- the contamination-filtered same-plaintext anchors become readable;
- the ordering-search / crib tools (`order_solve`, `ngram_solve`, `refrain_attack`,
  validated on plants to recover English from a sufficient crib) become live;
- a correct ~22-glyph refrain crib would pin most of the alphabet.

**What would break it open (in priority order):**
1. An **external glyph→letter anchor** (a confirmed font/value mapping, an acrostic,
   or community Rosetta data) — model-independent and unlocks reading.
2. A **correct ~22-glyph refrain phrase** (full region, not 13 letters) — the
   crib/ordering tools then recover the alphabet (validated on plants).
3. New **independent repeated structure** beyond the one refrain — more
   same-plaintext anchors.

## The audit chain (reproducibility)

```bash
python3 noita_eye_core/selftest.py        # aggregate math gate (478/478)
python3 eyewitness/datastream_check.py    # corpus integrity, 3 independent sources
python3 eyewitness/binary_provenance.py   # decompiled noita.exe -> corpus 9/9
python3 eyewitness/shared_structure.py    # model-free triplet/shared-opening map
python3 eyewitness/model_audit.py         # model verification (honest verdict)
python3 eyewitness/eyescoreboard.py       # cipher candidate ranking (methodology-audited)
python3 eyewitness/refrain_template.py    # refrain repeat-template (dof=2; hypothesis)
python3 eyewitness/keyspace_ledger.py     # block structure -> key/keyspace ledger
python3 eyecrack/refrain_sweep.py --show-template   # template-guided refrain sweep
python3 eyecrack/refrain_compose.py --doubles       # refrain double-letter map + anchored composer
python3 eyewitness/passage_template.py --html       # discover · extend · template pipeline
python3 eyewitness/passage_template.py --audit      # paranoia invariants on real corpus
python3 eyes.py                           # menu of all tools + dashboard build
```

Every link is either **SOLID-with-evidence** or **honestly flagged as hypothesis**;
the chain deliberately records negative/inconclusive results (model not uniquely
confirmed; Finnish retracted) so it stays trustworthy. Detailed reports live in
`report/`.

---

*Generated as the consolidated state of the investigation. For the granular
fingerprint see `FINGERPRINT.md`; for the interactive dashboard see `report.html`.*
