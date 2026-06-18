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
  conversion (verified). Caveat: not yet an independent re-read of raw glyphs.

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
| **Ciphertext-autokey / clock** (constant offset per pair) | **confirmed (structure)** | free-δ isomorph chaining: consistent + over-determined (redundant 278–895), 60–68/83 symbols linked, at every threshold (`isomorph`) |
| **Progressive-alphabet** (offset = position) | **refuted** | progressive (fixed-δ) chaining contradicts where free-δ is consistent (`isomorph`) |
| Affine vs additive sub-type | **open** | crib-activated `a_t`-solve (needs an anchor) |
| Small-seed PRNG keystream (any combiner) | **disfavored** | additive + GAK seed scans to 100M null; if autokey, no seed exists |
| Key from a salakieli-style passphrase | **open** | needs the in-game key-derivation |

**Leading model:** a polyalphabetic cipher over **interrelated alphabets** with an
**aperiodic, position-locked, per-group key schedule** whose alphabets are related
by a **constant offset per isomorph pair** — the signature of **ciphertext-autokey
(offset 1) or a clock cipher**, **not** a positional progressive (which the free-δ
vs fixed-δ chaining test refutes). The key is **not a small PRNG seed** (every
additive/GAK seed scan to 100M is null; under autokey there is no seed).

Two stages remain: (1) **order the cipher alphabet** via indirect-symmetry-of-
position chaining (free-δ proves the constant-offset interrelation and links most
of the 83 symbols, but does not by itself *order* them — the unknown per-pair
offsets couple symbols without ordering); (2) a **mapping anchor** for the
plaintext side — the flat unigram denies frequency analysis, so the anchor must
come from a crib, a confirmed acrostic, or external glyph→letter data.

## Why years of brute-force failed (the actionable takeaway)

Seed-scanning a PRNG assumes a small-integer seed and a simple combiner. The
evidence says the key schedule is **interrelated/autokey** (no seed) and the
corpus is **too small** (9 short messages, N=83, flat unigram) to confirm a
decryption statistically. The productive attacks are **isomorph-based alphabet
recovery** and **crib-dragging under the interrelated-alphabet model** — not
seed search.

## Reproduce everything

```bash
# math gate — every claim's module selftest (216/216)
python3 noita_eye_core/selftest.py

# structure (run from eyewitness/)
python3 eyewitness/repeat_census.py        # stream vs block/periodic/transposition
python3 eyewitness/isomorph_chain.py       # interrelated alphabets + progressive test
python3 eyewitness/depth_map.py            # provable shared-keystream / true depth
python3 eyewitness/header_test.py          # (66,5) literal vs keystreamed
python3 eyewitness/number_test.py --target 34   # header-as-number
python3 eyewitness/salakieli_aes.py        # AES-128-CTR falsification

# full dashboard (self-contained HTML)
python3 report/build.py                    # writes report.html
```

*This document is generated from validated findings; see `report.html` for the
interactive dashboard with inline charts and per-hypothesis reproduction.*
