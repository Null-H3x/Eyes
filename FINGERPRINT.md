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
13 letters) is slid to every offset in the region. Validated on plants (selftest
7/7). **Crux:** the corpus-IoC payoff needs the plaintext-alphabet *ordering*
roughly right; under the plain A–Z ordering candidate refrains reject, implying
the ordering is non-alphabetical (a scrambled/keyword alphabet). Needs a correct
refrain phrase **and** ordering as the human input.

Open stages: (1) **identify the specific interrelation** and **order the cipher
alphabet** via indirect-symmetry-of-position chaining (the genuinely hard step —
free-δ consistency alone is insufficient, and isomorph linkage alone does not
order the alphabet); (2) a **mapping anchor** for the plaintext side — the flat
unigram denies frequency analysis, so the anchor must come from a crib, a
confirmed acrostic, or external glyph→letter data.

## Why years of brute-force failed (the actionable takeaway)

Seed-scanning a PRNG assumes a small-integer seed and a simple combiner. The
evidence says the key schedule is **interrelated/autokey** (no seed) and the
corpus is **too small** (9 short messages, N=83, flat unigram) to confirm a
decryption statistically. The productive attacks are **isomorph-based alphabet
recovery** and **crib-dragging under the interrelated-alphabet model** — not
seed search.

## Reproduce everything

```bash
# math gate — every claim's module selftest (245/245)
python3 noita_eye_core/selftest.py

# structure (run from eyewitness/)
python3 eyewitness/repeat_census.py        # stream vs block/periodic/transposition
python3 eyewitness/isomorph_chain.py       # interrelated alphabets + progressive test
python3 eyewitness/header_base.py          # header => pure-progressive + progressive contamination correction
python3 eyewitness/pure_progressive.py     # pure-progressive recovery + decryption attempt (IoC test)
python3 eyewitness/trifid_scan.py          # digit-level / fractionation (Trifid) analysis of eye-marks
python3 eyewitness/binary_provenance.py    # decompiled SpawnSecretEyes -> corpus (9/9); needs data/lua/noita.c
python3 eyecrack/refrain_attack.py --constraints   # known-position crib attack on the 4x refrain
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
