# Cipher Family Field Guide 2 — The Plaintext Is High-Entropy

*Field Guide 1 fingerprinted the cipher **mechanism** (aperiodic progressive /
double-mixed clock) and established that the plaintext embedding is scattered.
This companion turns the same lens on the **plaintext content itself**, through a
channel that bypasses the alphabet-ordering wall, and reaches a conclusion that
redirects the whole search: the plaintext fed to the cipher is **not natural
language** — it is high-entropy, near-uniform over a large symbol set. Every
number here is reproduced by `cipher_data/dedrift_probe.py` and gated by its
planted selftest.*

Repo placement: `cipher_data/`. Companions: `cipher_family_field_guide_1.md`,
`STATE_OF_THE_SOLVE.md`, `FINGERPRINT.md`.

---

## 1. The de-drift channel (why we can read plaintext statistics without breaking C)

The surviving model is the linear class `c_m[t] = C[(σ·p_m[t] + base_m + drift·t)
mod N]`, N = 83. The drift carries **no key entropy** — it is a fixed linear
function — so define

```
d[t] := q[c_m[t]] − drift·t  =  σ·p_m[t] + base_m           (q = C⁻¹)
```

and the position term cancels. `d` is a **monoalphabetic image of the plaintext**,
per message; `base_m` is only an additive shift. We do not have full `q`, but we
have 16 gauge-invariant pins from `iso_relax` on the refrain component, and a pin
is a *value* valid corpus-wide because `C` is global. So at every position
carrying a pinned symbol we read `d[t]` — the plaintext value up to `(σ, base_m,
one global rotation)`.

Crucially, **all three nuisances are additive/negation transforms**, and
collision statistics — IoC `= Σᵢpᵢ²` and the triple-collision rate `Σᵢpᵢ³` — are
invariant to every one of them. So this channel measures the plaintext's
frequency *shape* directly, with no need to order the alphabet. This is the one
lever in the whole investigation that sidesteps the linked-not-ordered wall: we
cannot yet *read* the plaintext, but we can *characterize* it.

## 2. The pins are correct (three independent checks)

A near-uniform result would be meaningless if the pins were self-consistent but
wrong, so the pins were validated before the measurement was trusted:

- **Within-message.** The two West-1 refrain instances (`@32`, `@62`) are the
  same plaintext; they de-drift to identical values at **9/9** aligned pinned
  positions. East-2 (`@37`, `@72`): **5/5**.
- **Cross-message (the decisive one).** West-1 and East-2 carry the same refrain
  under *different* messages, so a degenerate assignment cannot fake agreement.
  At every aligned position pinned in both, the de-drift offset is a single
  constant — in fact **exactly 0** — across four *independent* symbol pairs
  `(44,13),(48,64),(19,49),(49,31)`. Pins correct, and as a bonus `base_W1 =
  base_E2`: bases are shared within a triplet.
- **Model.** The drift is genuinely aperiodic (Field Guide 1 §4: no periodic
  comb; d=4 spikes but its multiples are flat), and the drift gauge `+1` is the
  one that makes the refrain self-consistent.

## 3. The measurement

De-drift over all pinned positions, **excluding duplicate refrain instances** so
the 4×-repeated refrain does not oversample its own letters (see §4 — this
correction matters):

```
samples: 220 positions across 9 messages
observed IoC (within-message, base-invariant, unbiased) = 0.0126
  jackknife 90% CI [0.0097, 0.0156]
effective alphabet size 1/IoC ≈ 79   (CI [64, 104])

model                    IoC(model)   MC-null 90% band   obs consistent?
uniform-83                   0.0120    [0.0089, 0.0156]   YES
finnish-bigram (top120)      0.0118    [0.0082, 0.0156]   YES
base64 (uniform-64)          0.0156    [0.0119, 0.0197]   YES
uniform-53                   0.0189    [0.0148, 0.0230]   no
finnish-syllable             0.0197    [0.0130, 0.0278]   no
uniform-29                   0.0345    [0.0293, 0.0404]   no
finnish-flattened^0.5        0.0564    [0.0486, 0.0649]   no
hex (uniform-16)             0.0625    [0.0549, 0.0701]   no
natural-english              0.0658    [0.0552, 0.0771]   no
natural-finnish              0.0730    [0.0627, 0.0842]   REJECTED (~20σ)
```

**The plaintext fed to the cipher is high-entropy: near-uniform over a large
symbol set (~64–83 effective).** Consistent with a full-alphabet uniform stream,
a base64-like encoding, or a large token/bigram inventory. Decisively
inconsistent with natural Finnish (the community's working assumption), natural
English, a doubles-collapsed/flattened language, or *any* alphabet of ≤53
symbols.

The MC bands account for the n = 220 sampling spread; the jackknife CI is
collision-valid (a naive bootstrap-with-replacement is **not** — it manufactures
spurious collisions, and an earlier version of this analysis was misled by one).
Caveat: the probe slightly **under**estimates IoC for peaked sources (selftest
recovered 0.066 for a true-0.073 Finnish plant), so the true plaintext IoC may be
modestly above 0.0126 — but nowhere near natural language. At n = 220,
uniform-64 through uniform-83 are not distinguishable; more pins sharpen this
(coverage grows ~quadratically).

## 4. A correction to my earlier claim

An earlier pass reported de-drift IoC ≈ 0.0187 and "effective alphabet ~53." That
number was inflated by the **refrain repeat**: the pins come from the refrain, the
refrain is one plaintext repeated 4×, and counting all instances oversamples its
letters and manufactures collisions. Counting the refrain's plaintext **once**
drops the IoC to 0.0126 — i.e. the plaintext is *even more* uniform than first
stated, and sits right on top of uniform-83. The qualitative conclusion
(high-entropy, not natural language) held; the magnitude was corrected toward the
extreme. The selftest now enforces this de-biasing on planted data.

## 5. What this means for the search

The measurement is SOLID; the interpretation splits into two live readings, and
**both redirect away from the current natural-Finnish-letter approach**:

- **Reading A — the plaintext is compressed or encrypted before the cipher.**
  Natural language, even preprocessed or tokenized, rarely reaches near-uniform-83
  without compression. If the "eye messages" wrap a compressed or
  doubly-enciphered payload, then **no natural-language crib can ever match**, and
  the Kalevala/word-list crib program (including `jointcrib`, `eyesieve`,
  `refrain_sweep`) is aimed at a plaintext that does not exist in that form. This
  is the parsimonious reading and it is falsifiable (§6).
- **Reading B — the plaintext is a large, flat symbol/token inventory** (a
  syllabary, a game-specific glyph set, an index stream). High-entropy but
  *readable* given the right token map — yet still invisible to letter-frequency
  and Finnish-word cribs, so the current scorers remain miscalibrated.

Either way, three concrete consequences the repo should adopt:

1. **The language-model scorers are calibrated to the wrong distribution.** A
   correct decrypt would score like a near-uniform stream, not like Finnish, so
   the readability gates cannot distinguish a true decrypt from noise — a clean
   mechanical explanation for why `eyesieve`'s 454K-hypothesis union sweep
   surfaced only "letter-soup" and never coherent text. **Recalibrate every gate
   against a high-entropy null**, not against raw language.
2. **Stop scoring cribs by natural-language fitness.** Under Reading A there is no
   language to fit; under Reading B the unit is a token, not a letter. The crib
   machinery should score **structural consistency** (the joint-overlap gate,
   which is language-free) and defer any language judgment until the plaintext
   type is settled.
3. **The bottleneck may not be C at all.** If the payload is compressed/encrypted,
   recovering `C` yields a *second* high-entropy layer, not readable text —
   `STATE_OF_THE_SOLVE`'s "recover the anchor and read" endgame would need a
   second stage. This must be tested before more effort goes into ordering `C`.

## 6. How to falsify each reading (next probes)

- **Compression signature.** Extend the de-drift channel from unigram IoC to the
  **de-drifted bigram/entropy** on the ~220 positions (and more as pins grow). A
  compressed stream is near-uniform at *all* orders; a token inventory (Reading B)
  retains bigram structure. This distinguishes A from B with tooling already in
  hand.
- **Alphabet-size estimate.** Sharpen `1/IoC` with more pins; a value pinned near
  83 argues full-alphabet uniform (compression/encryption), near ~50–64 argues a
  syllabary/base64. `relax_structures.py` (cross-triplet, Triplet-3) plus any new
  anchor adds pins.
- **Known-compressor test.** Encode a Kalevala passage with candidate transforms
  (deflate, a Finnish syllabary, base64-of-bytes), run each through the *identical*
  de-drift pipeline in a plant, and match the resulting IoC/entropy fingerprint to
  the observed 0.0126 — the same model-comparison the probe already does for
  unigram IoC, extended to the transforms. Whichever transform reproduces the
  observed high-order statistics names the preprocessing.

## 7. Standing conclusion

SOLID (this cycle, triple-validated pins): the plaintext fed to the linear cipher
is **high-entropy, near-uniform over ~64–83 symbols**, IoC 0.0126 (CI
[0.0097, 0.0156]); natural language and all small alphabets are rejected at high
significance. This is the strongest direct statement about the plaintext obtained
so far, and it is orthogonal to — and stronger than — the earlier preprocessing
lean, because it comes from a verified channel rather than a thin repeat probe.
OPEN: whether the high entropy is compression/encryption (Reading A) or a large
flat token inventory (Reading B) — §6 falsifies this. IMMEDIATE: recalibrate all
readability/scoring gates to a high-entropy null; suspend natural-language crib
scoring pending the plaintext-type resolution; test for a second cipher layer
before investing further in ordering `C`.

## 8. Reproduce

```bash
python3 dedrift_probe.py --selftest      # plants Finnish/uniform-53/base64, proves the
                                         # probe recovers planted IoC and tells types apart
python3 dedrift_probe.py                 # real corpus: pins via iso_relax, de-drift,
                                         # IoC + effective-alphabet + model comparison
```

Real-corpus run needs `iso_relax` and `noita_eye_core` on the path (place beside
`eyeforward/`); the selftest is self-contained (it injects true pins from its
plants). The refrain-duplicate exclusion set is `EXCLUDE_DUP` at the top of the
probe; reference language texts are read from `../corpora/`.
