# Noita Eye Glyphs — Cipher Fingerprint

A reproducible, calibrated characterization of the eye-message cipher: what it
**is**, what it is **provably not**, and where the remaining unknowns sit. Every
claim here is backed by a self-tested module in `noita_eye_core/` and is
reproducible with the commands in the last section. Statistical claims are
calibrated against explicit null models (shuffle / Monte-Carlo / analytic), with
z-scores and p-values, and multiple-testing aware where relevant.

> Scope note: this is **Effort A** — a verifiable fingerprint for the community
> to test, exploit, or extend. It does **not** claim a decryption. It is meant to
> stop wasted effort (e.g. blind seed-scanning) and point at the productive
> remaining attacks.

## Corpus (the data)

- **9 messages**, ciphertext alphabet **N = 83** (symbols 0–82), **1036** total
  symbols. Lengths: 99, 103, 118, 102, 137, 124, 119, 120, 114.
- Messages, in order: East 1, West 1, East 2, West 2, East 3, West 3, East 4,
  West 4, East 5. (There is **no West 5** — 9 messages, not 10.)
- The 0–82 values are the game's data-mined eye numbering read as **base-5
  trigrams** (per the community's analysis), not an arbitrary transcription.
- Our `corpus.json` is **byte-identical** to WarFairy's published BASE10
  conversion, to the community trigram xlsx, AND — decisively — to the **hard-coded
  constants decompiled from `noita.exe`** (`SpawnSecretEyes`/`FUN_005b2d10`): all
  **9/9 messages decode to the corpus** via the guide's base-7 unpack
  (`provenance`, `binary_provenance`). Three independent sources agree; the corpus
  is traced to its origin in the game binary.
- **Provenance settled:** the messages are **hard-coded** 64-bit constants that the
  engine only base-7-unpacks and draws — there is **no decryption, key, or
  keystream in the engine, and exactly 9 messages (no West 5)**. The cipher (if any)
  was applied **offline by the author**, which is *why every in-game seed scan was
  null* — there is no in-game seed to find.

## Verified exclusions (what it is NOT)

Each is a calibrated test, not an impression.

| Cipher family | Verdict | Basis (module) |
|---|---|---|
| Monoalphabetic substitution | **excluded** | flat unigram, IoC≈1.07 (`classify`, `stats`) |
| Simple transposition | **excluded** | alphabet/length structure (`classify`) |
| Short-period Vigenère | **excluded** | no Kasiski/Friedman period (`classify`) |
| Fractionation / coordinate (Bifid/Trifid/Polybius) | **excluded** | base-5 digit-structure null (`classify`, `trigram`) |
| AES-128-CTR (salakieli file cipher) | **excluded** | alphabet 83 ≠ 256; depth ⊥ unique-IV; decrypts to noise (`salakieli_aes`) |
| Keyless transform stacks | **excluded** | no stack restores structure (`cipher_fingerprint`) |
| Periodic / repeating-key | **excluded** | 0 offset collisions k=3..7; no period (`repeats`) |
| Block / ECB reuse | **excluded** | 0 offset collisions (`repeats`) |
| Positional transposition / cut / shuffle | **excluded** | 0 offset collisions — no symbol ever moves columns (`repeats`) |
| Independent-column substitution (general GAK, unrelated decks) | **excluded** | abundant isomorphs require *interrelated* alphabets (`isomorph`) |
| Unrelated-alphabet running-key / OTP | **excluded** | same — isomorphs forbid unrelated alphabets (`isomorph`) |
| Header `(66,5)` = the number 34 | **excluded** | not reachable under any principled encoding (`numbertest`) |

## Validated positive findings (what it IS)

- **Pure aperiodic, position-locked stream**: a per-position bijection
  `c[t] = F_t(p[t])` that never moves a symbol between columns. (`repeats`)
- **Interrelated alphabets** (the `F_t` are related, not independent): the corpus
  carries **true isomorphs** — same repeated-letter *pattern*, different *values*
  — at **z > 100** vs a shuffle null (e.g. 51 true isomorphs at L=12 vs ~0).
  This points at **sliding / progressive / autokey** ciphers. (`isomorph`)
- **Shared within groups, per-group in the body**: cross-group ciphertext
  agreement occurs only in the opening (positions 1–6); the body keystream is
  per-group. (`repeats`, `depthmap`, `keystream_scope`)
- **Header `(66,5)` is literal** (positions 1–2, universal across all nine;
  p≈3e-12 under independent keystreams). Not part of the body keystream.
  (`header_test`)
- **Position 0** is per-message and distinct across all nine; not a clean numeric
  index; candidate "indicator" that sets initial state (untested). (`numbertest`)
- **Near-duplicate pairs**: E1≈W1 and E4≈E5 share verbatim passages (an opening
  block + a second block) then diverge. Provable body-persistent shared keystream
  exists for **only these two pairs** (z=20.4, 9.4). (`depthmap`, `pairdiff`)
- **No symbol repeats adjacently** (`AA` absent) and **distance-4 repeats are
  elevated** (26 vs ~12 by chance) — both classic auto-key / progressive signatures.
- **True exploitable depth is ~136 positions** (2-deep, from the two near-dup
  pairs). There is no free 3+ depth in the body. (`depthmap`)

## Cipher hypothesis lattice (current status)

| Hypothesis | Status | Decisive test |
|---|---|---|
| Monoalphabetic / transposition / periodic / block / AES / keyless-stack | **excluded** | see table above |
| Independent-column substitution (general GAK) | **excluded** | isomorphs forbid it |
| **Interrelated alphabets** (sliding/autokey/clock family) | **confirmed** | abundant isomorphs, z>100 vs shuffle null (`isomorph`) |
| **Progressive-alphabet** (offset = position) | **OPEN (correction)** | earlier "refuted" was a *contamination artifact*: on contamination-filtered CLEAN isomorphs pure-progressive has 0 contradictions (raw mr=3 had 121); two solvers agree. Consistent but under-determined — not confirmed either (`headerbase`) |
| **Ciphertext-autokey / clock** (specific interrelation) | **open** | free-δ chaining is *permissive* — consistent even on two-alphabet and random nulls, so it does NOT identify autokey; needs indirect-symmetry recovery (`isomorph`) |
| Affine vs additive sub-type | **open** | crib-activated `a_t`-solve (needs an anchor) |
| Trifid / fractionation on the 3 base-5 eye-marks | **disfavored** | per-eye-mark streams near-uniform; only assoc (d0,d1) is a 0..82-compaction artifact; inverse digit-transpose at every period 2..24 lowers IoC (no anomaly) — structure is glyph-level, not digit-level (`trifid`) |
| Small-seed PRNG keystream (any combiner) | **disfavored** | additive + GAK seed scans to 100M null; if autokey, no seed exists |
| Key from a salakieli-style passphrase | **open** | needs the in-game key-derivation |

**Leading model:** a polyalphabetic cipher over **interrelated alphabets** with an
**aperiodic, position-locked key schedule**, in the **sliding / progressive /
autokey / clock** family. We have **not** pinned the specific member. Two live
candidates remain:
- **Pure progressive** (single global sliding alphabet, offset = position). The
  literal universal `(66,5)` header *forces* this within the per-message-
  progressive family: a literal header makes every per-message base equal, which
  collapses per-message-progressive to pure progressive (`headerbase`, proven on
  plants). And — correcting an earlier over-claim — progressive is **not** refuted:
  the contradictions that suggested refutation came from **contaminated** isomorphs;
  the clean set is consistent with it.
- **Ciphertext-autokey / clock**, which also reads the universal header naturally
  (p[2] constant, p[1] varying with the per-message position-0 symbol).

Deciding between them needs more clean repeated structure or a mapping anchor; the
free-δ chaining test is **permissive** (consistent on two-alphabet and random
controls), so it does not identify the member. The key is **not a small PRNG
seed** (every additive/GAK seed scan to 100M is null).

**Pure-progressive decryption attempt (`pureprog` / `pure_progressive`).** Under
pure progressive the whole corpus decrypts up to a single monoalphabetic relabel
once the alphabet `x=C⁻¹` is recovered, and IoC (relabel-invariant) tests whether
the result is language. The machinery is validated (selftest 6/6: recovers a
planted alphabet up to rotation, decrypts to plaintext+constant, IoC separates
language from uniform). On the **real corpus** it is **under-determined**: the
clean isomorphs are essentially one repeated passage, so `x` is pinned for too few
symbols (37 linked → 22 distinct) and the decrypted-stream IoC is **0.014
(z ≈ 2.2, far below language ~0.06)** — and that faint bump is the known 4× repeat,
not readable text. **Wall: too few independent clean repeated structures to
recover a usable alphabet.** This is the re-runnable gate — more clean isomorphs or
an external glyph→letter anchor would move the IoC if the model holds.

**Contamination-resistant extraction (`chain_extract` / `iso_extract`).** Skeleton
matching returns partial/misaligned pairs (same pattern, different plaintext at
singletons) that defeated earlier chaining. Anchoring a per-message-progressive
alphabet on the cleanest threshold (shuffle-null ≈ 0) and classifying the broader
set against it isolates the genuinely fully-aligned isomorphs — validated on a
66 %-contaminated plant at **precision 0.996 / recall 1.000** (all-seeds robust)
with full alphabet recovery up to rotation. Contamination filtering is
**model-robust**: per-message-progressive and free-δ flag the *identical*
clean/contaminated split on the real corpus. The result is a tight family of
**6 long maximal aligned runs** (len 15) across messages 1/2 — the strongest
structural foothold to date. But the alphabet is only **linked, not ordered**,
and where an order is produced it is **permissive** (the same machinery orders a
comparable alphabet from autokey data), so it is a candidate to test, not model
evidence.

**Live attack vector — refrain known-position crib (`refrain` / `refrain_attack`).**
The 4× repeated refrain spans a **25-glyph** region — its maximal shared-plaintext
extent is West1@32–56 / @62–86, East2@37–61 / @72–96 (the earlier "15" was a
conservative sub-run). It is the same plaintext at four *known* positions, so under
pure-progressive a guessed plaintext value at a known position pins the cipher
alphabet **absolutely** (`x[c]=p+pos`, no rotation freedom). A correct 25-symbol
guess pins **59 of 83 symbols → ~78 % of the corpus decryptable**, and lights
corpus-wide IoC up; a wrong guess self-contradicts. The region's own ciphertext
collisions force ordering-independent constraints (`p[13]=p[10]-3, p[15]=p[8]-7,
p[16]=p[12]-4, p[18]=p[9]-9, p[19]=p[2]-17 (mod 83)`). A shorter candidate (e.g.
13 letters) is slid to every offset in the region. Validated on plants. The body
is **per-message-progressive** (each message its own base; pure-progressive is
contradicted across the 4 instances).

**Crib-seeded English n-gram solver (`ngram_solve`).** IoC hill-climbing is a
*proven dead end* — on a plant it reaches near-true IoC on a WRONG alphabet
(IoC is order-blind/degenerate). The productive replacement: a correct crib + an
ordering hypothesis pins ~59/83 of the alphabet, then hill-climb the residual
symbols + per-message bases by **English character-trigram** likelihood, scored
against a shuffled-decryption null. Validated on a per-message-progressive English
plant (selftest 6/6: corpus reads back as English at z≥4; wrong cribs score low).
On the **real corpus** every community candidate (`trueknowledge`,
`seekeroftruth`, …) rejects under the natural ordering — re-confirming the
**ordering is the remaining barrier**. The solver is ready the instant a correct
(refrain, ordering) pair is supplied.

**Ordering-search solver (`order_solve`).** Removes the need to *know* the
ordering: it pins the alphabet structure ordering-free from the crib's
letter-pattern + ciphertext (GF over symbol/base/plaintext variables; a
contradiction = the crib pattern is incompatible, reported with the slot), then
hill-climbs the ordering `O` + per-message bases by English character-trigram
likelihood with a dictionary word-coverage gate. **Validated** (selftest 7/7): on
a per-message-progressive English plant it **recovers readable English** from a
*sufficient* crib (z≫8, real words). **Key finding:** the crib must be long enough
to pin DISTINCT plaintext values — roughly the **full ~25-glyph region**; a
13-letter crib *under-determines* the alphabet (distinct letters collapse onto the
same value), giving diagnostics but no full read-out. Every run also yields
diagnostics on wrong cribs (contradiction slot, score gradient, partial words,
symbols pinned).

**Refrain extent corrected to 22 glyphs** (W1@32–53 / @62–83, E2@37–58 / @72–93):
an all-distinct crib stays per-message-progressive-consistent through L=22 and
contradicts at L=23. Validated: the all-distinct-extent method recovers planted
refrain lengths to ±1, and the refrain's 22-glyph consistency is **special** (random
4-position sets stay consistent only ~7 glyphs), so the 22-glyph same-plaintext
refrain is **real**.

**Paranoia audit — a retraction.** An earlier claim that "English thematic phrases
all contradict ⇒ the refrain is not English (probably Finnish)" was an **OVER-REACH
and is RETRACTED.** Audit: on a plant that genuinely *is* English (per-message-
progressive, English refrain), random *wrong* English 22-char phrases pass
`pin_structure` at **0/300 — identical to the real corpus (0/300)** — while the true
refrain passes. So a phrase failing the structural test is just normal *wrong-guess*
rejection and carries **no information about the language**. **The plaintext language
remains unknown (English fully viable).** Corollary (the real lesson): **blind
phrase-guessing is near-hopeless** — only a phrase matching the refrain's *exact*
repeat-pattern passes (~0/300 for random phrases, any language). Productive paths:
generate candidates that match the ciphertext's required repeat-template, or find a
different lever; do **not** run a large blind phrase sweep (English or Finnish).

**Anchored refrain composer (`refrain_compose`).** Turns the dof=2 template into a
*generative* attack and pins down what the "ABB" block can be. **Structural facts
(verified):** the entire 22-glyph refrain admits an adjacent **doubled letter ONLY
at (4,5) [forced] and optionally (6,7) or (7,8)** — every other adjacent pair is
forced-different, so any candidate plaintext with a double letter anywhere else is
**dead**. The forced double at (4,5) is the skeleton's `BB`. **Candidate space for
the double:** all bigrams `aa`–`yy` are structurally allowed there (only `zz`
excluded), and **161** standalone 3-letter `XYY` words plus **~25,000** words
(via internal doubles and word *endings* like `-ee/-ll/-ss/-ff/-oo`) can place a
double at (4,5) — so the double-letter slot **alone is not discriminating**. The
narrowing levers are: (1) the no-other-doubles rule; (2) the long-range forced-same
ties (pos 3=13, distance 10; pos 10=16, distance 6); (3) **stacking** multiple
expected words at mutually-compatible offsets (`compatible_placements`); (4) a
dictionary **word-coverage (wcov)** gate over a trigram fill (`compose`). **Honest
result (re-confirmed):** expanding the word/fragment list *widens* the candidate set;
a character-trigram model still ranks English-*flavoured gibberish* at the top, so
the composer outputs a ranked SHORTLIST to feed `order_solve`, not a decryption.
Reading still needs the glyph→char ordering. Example (anchors `god@0`,`see@3`,
`eye@5`) co-place as `godseeye…`; the wcov fill surfaces `godsee­you…` ("god/gods
see you", resonant with the in-game "we are watching you"). `refrain_compose.selftest`
23/23. CLI: `python3 eyecrack/refrain_compose.py --doubles | --offsets W… | --compat
W… | --anchor W`.

**Refrain repeat-template (`template` / `refrain_template`).** Extracts, ordering-
free, the structure the 22-glyph refrain forces on its plaintext (GF over
plaintext-position/base/symbol variables; forced relations found by classify).
Result on the real refrain: **free plaintext degrees of freedom = 2 of 22** — the
relative plaintext is pinned to a 2-parameter family. **Forced-SAME letter groups:
(3,13), (4,5), (10,16)**; free position: 7; 207 forced-DIFFERENT pairs. Skeleton
`???ABB?.??C??A??C?????`. So a valid refrain must share a letter within each group,
differ across all forced-different pairs, and is otherwise nearly determined —
reading it still needs the alphabet ordering, but a correct ordering nearly
determines the refrain. **Caution (audited):** the tiny dof assumes per-message-
progressive; it could partly reflect over-constraint from coincidental
cross-instance matches if the model is imperfect — verify before over-trusting.
Validated: `template.selftest` 7/7 (recovers engineered collisions as
forced-different; forced-same arises only from genuine structure).

**Model verification — paranoia audit (`model_audit`).** Before trusting the dof=2
template we tested whether per-message-progressive is genuinely the refrain's
structure. **SOLID:** the 4 instances are the same plaintext (isomorph significance
z≈117; per-message-progressive consistency to L=22 vs random-window extent ~7).
**NOT cleanly confirmed:** the *specific* model — pure-progressive reaches L=21
(≈22), random 4-windows reach L=22 at empirical p≈0.002–0.006, and those that do
have as much over-determination as the refrain. So the consistency tests are passed
by a flexible model and do not single per-message-progressive out over other
interrelated-alphabet members. **Verdict:** the same-plaintext refrain is
established; the dof=2 repeat-template is a **model-dependent hypothesis** to test,
not a fact. (Report: `report/model_audit_report.md`; `model_audit.selftest` 5/5
validates the method discriminates models on plants.)

**Cipher candidate scoreboard — methodology audit (`eyescoreboard`).** A
paranoia-audited ranking harness that challenges its own ground-truth assumptions
on every run (`run_methodology_audit()`):
- **Plant discrimination** uses model-appropriate OWN plants (pure-progressive gets
  its own plant, not the per-msg plant).
- **Real-corpus discriminator:** GF contradiction rate on broad isomorph pairs
  (base_len=13, repeats≥3) — per-msg **10.9%**, pure **15.0%**, free-δ **0%**.
  Clean/flagged extract counts are **identical** across GF models (18/44) and must
  NOT be scored as a model discriminator.
- **SUPPORTED** tightened: requires plant gates, refrain extent strictly beating
  pure (L=22 vs L=21, gap=1), AND lower real-corpus contradiction rate.
- Cross-checked against `chain_models.discrimination_audit()`; shuffle-null extract
  control; triplet-combine probe.

**Ranking (real corpus, latest run):**
| rank | model | verdict | real contra | refrain |
|---:|---|---|---:|---:|
| 1 | per-msg-progressive | **SUPPORTED** | 10.92% | 22 |
| 2 | pure-progressive | SUGGESTIVE | 15.01% | 21 |
| 3–4 | free-δ / autokey-1 | PERMISSIVE | 0% | — |
| — | mono, OTP, AES, transposition, PRNG, CT-autokey, general-K | EXCLUDED | — | — |

**Premise (model-independent):** YES — isomorph z≈112, per-triplet keystream scope,
exploitable depth 136, E1/W1 re-sync=5.

**Meta-trigram / triplet-combine hypothesis (user question).** If the ciphertext
symbol at each position were a *composite* of the three messages in its triplet
(e.g. a meta-trigram built from E1+W1+E2), aligned combine streams would show
structure vs shuffle null. Probed two ways on all three triplets (body positions
≥25): (1) **sum mod 83** of the three ciphertext values; (2) **base-5 digit-sum**
of the three eye-mark trigrams. Result: IoC matches null (z≈0.5–2, none significant).
Each symbol is already a base-5 trigram of **individual** eye-marks (provenance
9/9); there is **no evidence** the 0–82 stream is a second-level trigram formed by
combining the three messages in a triplet. The triplet structure is in **shared
openings / keystream scope**, not in per-position symbol arithmetic.

Report: `report/eyescoreboard.md`; `eyescoreboard.selftest` 12/12.

Open stages: (1) **identify the specific interrelation** and **order the cipher
alphabet** via indirect-symmetry-of-position chaining (the genuinely hard step —
free-δ consistency alone is insufficient, and isomorph linkage alone does not
order the alphabet); (2) a **mapping anchor** for the plaintext side — the flat
unigram denies frequency analysis, so the anchor must come from a crib, a
confirmed acrostic, or external glyph→letter data.

## Model-independent shared structure (`shared_structure`)

Depending only on "same glyph = same glyph" (isomorph skeletons, no cipher model),
the corpus has a strong, calibrated **triplet** structure:
- **Triplet 1 (E1/W1/E2)** shares a **~22-glyph opening**; **Triplet 3 (E4/W4/E5)**
  shares **~18** — both far above the random-aligned null (~5–7). The messages
  genuinely come in triplets with shared openings (confirms the original triplet
  theory, model-free, z≫null).
- **Triplet 2 (W2/E3/W3)** does **not** share a long opening (~null); W2/W3 share
  ~13 but **E3 is weakly linked to everything** — structurally distinct (longest
  message). **No universal opening** beyond the (66,5) header (9-way ≈ chance).
- The refrain repeats **within** messages too (e.g. a 20-glyph passage at E1@39 and
  E1@67), and there is a cross-triplet passage (W2/E4/W4, 15 glyphs). These are
  model-free same-plaintext anchors that constrain plaintext content regardless of
  cipher. (Report: `report/shared_structure_report.md`; selftest 5/5.)

## Cipher-construction lattice (what fits the validated structure)

Enumerating constructions that satisfy EVERY validated fact (`cipher_lattice`,
report `cipher_lattice_report.md`):

- **New exclusion — ciphertext-autokey.** E1≈W1 are a shared-key near-duplicate pair
  (44% identical, in blocks) with **5 re-sync events** (identical→differ→identical).
  A content-dependent (ciphertext-autokey) keystream would propagate the difference
  forever and never re-sync, so it is **excluded** (`resync`, selftest 6/6). Honest
  limit: *plaintext*-autokey lag-1 re-syncs one position late and is NOT excluded by
  this alone (distinguishing it from a position keystream needs the plaintext).
- **Surviving family:** `c[m][t] = C[(p[m][t] + base_m + K[t]) mod 83]` — a
  position-indexed keystream `K` over a single interrelated (mixed) alphabet `C`,
  plus a per-message/per-group base. Sub-variants that all fit: **A** progressive
  (`K[t]=t`, linear) + per-msg base; **B** general aperiodic `K[t]` + per-msg base;
  **C** per-group mixed alphabet `C_m=S_m∘C`. **D** plaintext-autokey lag-1 is a
  residual alternative not excluded by re-sync.
- **Per-message variation is required** (E2 is isomorphic-not-identical to E1), and
  **keys cluster** (E1=W1 share a base; E2 differs). The community "GAK/XGAK/
  stacked-with-cut" theories all reduce to this single family (a 0–82 'cut' = the
  per-message base; stacked substitution = a per-group alphabet).
- **Open within the family:** K linear vs general; position-keystream vs lag-1
  plaintext-autokey; the base grouping. All moot for *reading* without the
  glyph→character ordering.

## Why years of brute-force failed (the actionable takeaway)

Seed-scanning a PRNG assumes a small-integer seed and a simple combiner. The
evidence says the key schedule is **interrelated/autokey** (no seed) and the
corpus is **too small** (9 short messages, N=83, flat unigram) to confirm a
decryption statistically. The productive attacks are **isomorph-based alphabet
recovery** and **crib-dragging under the interrelated-alphabet model** — not
seed search.

## Reproduce everything

```bash
# math gate — every claim's module selftest (478/478)
python3 noita_eye_core/selftest.py

# structure (run from eyewitness/)
python3 eyewitness/repeat_census.py        # stream vs block/periodic/transposition
python3 eyewitness/isomorph_chain.py       # interrelated alphabets + progressive test
python3 eyewitness/header_base.py          # header => pure-progressive + progressive contamination correction
python3 eyewitness/pure_progressive.py     # pure-progressive recovery + decryption attempt (IoC test)
python3 eyewitness/trifid_scan.py          # digit-level / fractionation (Trifid) analysis of eye-marks
python3 eyewitness/binary_provenance.py    # decompiled SpawnSecretEyes -> corpus (9/9); needs data/lua/noita.c
python3 eyewitness/keyspace_ledger.py        # block structure -> key/keyspace ledger
python3 eyewitness/eyescoreboard.py        # cipher candidate ranking (methodology-audited)
python3 eyecrack/refrain_attack.py --constraints   # known-position crib attack on the 4x refrain
python3 eyecrack/refrain_sweep.py --wordlist eyestat/noita_wordlist.txt  # template-guided sweep
python3 eyecrack/refrain_compose.py --doubles   # where doubles are allowed; anchored composer
python3 eyecrack/refrain_compose.py --compat god see eye  # stacked anchor placements
python3 eyewitness/passage_template.py --html   # discover/extend/template pipeline
python3 eyewitness/passage_template.py --audit    # paranoia invariants (77 checks)
python3 eyecrack/ngram_solve.py "trueknowledge"    # crib-seeded English n-gram solver
python3 eyecrack/order_solve.py "trueknowledgeofthegods"  # ordering-search solver (recovers O from a crib)
python3 eyecrack/ordering_exhaust.py --phrase "..."  # residual ordering exhaust (Phase 2)
python3 eyewitness/iso_extract.py          # contamination-resistant maximal-aligned isomorphs
python3 eyewitness/depth_map.py            # provable shared-keystream / true depth
python3 eyewitness/header_test.py          # (66,5) literal vs keystreamed
python3 eyewitness/number_test.py --target 34   # header-as-number
python3 eyewitness/salakieli_aes.py        # AES-128-CTR falsification

# full dashboard (self-contained HTML)
python3 report/build.py                    # writes report.html
```

*This document is generated from validated findings; see `report.html` for the
interactive dashboard with inline charts and per-hypothesis reproduction.*
