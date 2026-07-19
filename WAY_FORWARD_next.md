# Noita Eye Puzzle — Way Forward (next cycle)

*Written after: (1) a full read of Field Guides 1–5, (2) the mechanical
constraint diagram (`eye_group_ciphers_venn_diagram`), and (3) a working session
that closed the audio side-channel, empirically re-confirmed the Chaocipher
exclusion, and quantified the depth tree. It answers one question, in the spirit
of the earlier guides: **given only what is actually proven, what is the
highest-leverage next move, and why?***

The discipline of this document is that **nothing soft is treated as settled.**
Where a claim is deductive it says so; where it is a measurement it says so; where
it is a lean it says lean. Two things I personally over-stated earlier in the
session are corrected here in the open (§2, §3).

---

## 0. Executive summary

We know the **mechanism class** and we know a great deal about **what it is not**.
We do **not** know four things, and they are the whole game: the **cipher mode**
(static vs dynamic — Field Guide 4 fork, still open), the **plaintext type/language**
(measured high-entropy, natural language rejected — Field Guides 2/3), the
**alphabet size** (83 is a reading-dependent count, not a fact), and the
**alphabet ordering** `C` (the standing bottleneck across all five guides).

The mechanical diagram is the firm ground: it is the *deductive* boundary. Inside
it, the surviving space is small (§1). The bottleneck is unchanged and now proven
unavoidable — **recover `C`** — but this cycle adds a sharper strategic point the
guides circle without centering: **the A-vs-B question (secondary cipher vs. flat
token inventory) must gate the choice of `C`-solver**, because it decides whether
"reads as language" is even a valid success signal. Chasing `C` with a
language-n-gram objective while the plaintext may be high-entropy is the current
plan's one internal contradiction (§4, §5).

The single bounded-payoff action that serves every branch is the **cross-triplet
W2/E4/W4 bridge** (Field Guides 4/5): a few pins that enlarge the depth stack,
push toward the ~40-pin threshold where the A-vs-B verdict becomes measurable
(Field Guide 3 §7), and feed whatever solver we choose. That is #1.

---

## 1. The firm ground — the mechanical skeleton and its boundary

All survivors live in one skeleton (Field Guide 5 §1; `cipher_lattice_report`):

```
c_m[t] = C[( σ · p_m[t] + off_m[t] ) mod N]        N = 83
```

- `C` — the mixed alphabet (glyph→value bijection). **Unknown. The wall.**
- `σ` — plaintext multiplier. `±1` assumed; affine `a` open (Field Guide 5 §3).
- `off` — the offset; how it is generated splits the two surviving families.

**Two families, five generators (Field Guide 5 §1):**

- *Linear / static* — `off` driven by **position**: Progressive (`base_m+drift·t`),
  Gromark (`base_m+K[t]`, Fibonacci-style, 2-number primer), or a general aperiodic
  `K[t]`.
- *Nonlinear / dynamic* — `off` driven by **prior plaintext** (plaintext-autokey):
  running-sum Σ (Alberti), lag-`k` (Vigenère-autokey), or XGAK (position clock +
  autokey).

**What the diagram encodes — the deductive exclusions (map to the guides):**

| Diagram region (grey = excluded) | Why it dies | Guide |
|---|---|---|
| **CTAK** (ciphertext-autokey) | 5 clean re-syncs (identical→differ→identical); a ciphertext-fed state can't heal a propagated difference — and this kills the *entire* additive/Beaufort/Quagmire/affine × `C` × `E` gauge orbit at once, not one cipher at a time | FG5 §2 |
| **Comm. / Non-comm. GCTAK**, **Dihedral** (group-theoretic autokey) | isomorphs recur at a **constant additive difference** in `(Z/83,+)`, not a constant ratio (→ excludes multiplicative accumulators) and not a constant group element (→ excludes non-abelian `S₈₃/A₈₃` autokey). This is the same lever that excludes the Chaocipher class | FG5 §3 |
| Fractionation / Trifid | glyph-level, not digit-level; eye-mark streams structureless, no period. The `d=4` anomaly is generic autokey/progressive distance-4 coincidence, **not** a fractionation period | FG5 §1 |
| Periodic, dynamic-alphabet, homophonic, consecutive-block embedding | the FG1 identification battery; zero adjacent doubles → the embedding is **double-mixed**, not a consecutive block | FG1 §3, §4b |

**Surviving region (black):** GAK (= plaintext-autokey, the dynamic family) plus the
non-autokey **linear/static** family, both sitting inside "isomorphic ciphers"
because the corpus genuinely *has* constant-difference isomorphs. The diagram's own
open question — where "Group Cipher" sits — resolves as: any group construction that
would place us outside the additive accumulator is already excluded by §3; what
remains is additive.

This boundary is the one part of the problem that is **not** in doubt.

---

## 2. What this session added (and one thing it removed)

- **The audio external-anchor avenue is closed — thoroughly.** Spectrogram-image
  stego was ruled out with a validated structure-ranker whose top hits across all
  2,164 assets were mundane sounds; sample-domain LSB/phase/echo are destroyed by
  the shipped Vorbis codec; FSB5 names, metadata chunks, container/appended bytes,
  and Vorbis comments were scanned and contain only FMOD boilerplate and composer
  session titles. **Consequence for the plan:** one whole class of "external anchor"
  the guides repeatedly wished for is now eliminated. The anchor, if it exists, is
  not in the audio.

- **Chaocipher was built and falsified independently.** An exhibit-validated
  Chaocipher engine plus `deck_lab --compare` confirmed empirically what FG5 §3
  proves deductively: a content-driven permutation produces `lag4≈0.9×` and
  destroys isomorphs, the **opposite** of the corpus (`lag4≈2.16×`, strong
  isomorphs). This is not new knowledge — it is an independent second signature on
  a standing exclusion, and a correction to my own earlier "it's probably a
  Chaocipher" framing.

- **The depth tree is quantified.** Position 0 is a **per-message indicator**
  (all 9 differ); positions 1–2 are **identical across all 9** (values 66, 5); from
  position 3 the corpus **branches** — `{E1,W1,E2}` share one continuation,
  `{W2,E3,W3,E4,W4,E5}` another, then sub-branch. This is the "shared section after
  a varying first character" made concrete, it is consistent with **both** surviving
  families (shared plaintext re-synchronizes a plaintext-autokey state *and* aligns a
  position keystream), and it is exactly the depth stack the guides' recommended
  solvers feed on (FG5 §9).

- **Correction removed from the board: the plaintext is not Finnish.** After the
  audio work surfaced kantele samples and Kalevala track titles, I leaned toward a
  Finnish/Kalevala readout. Field Guides 2/3 refute this at the plaintext level:
  the de-drifted unigram distribution is high-entropy (IoC 0.0126, effective
  alphabet ≈ 79), **rejecting Finnish, English, and Karelian at high significance.**
  Finnish is the authors' cultural frame, not the message content. Any plan that
  scores `C`-candidates by natural-language fitness is therefore suspect until the
  A-vs-B question is resolved (§4).

---

## 3. The unknowns, by confidence

- **`C` — glyph→value ordering.** *Unknown; the bottleneck.* A crib reveals `C⁻¹`
  only for the glyphs it physically covers (FG5 §6).
- **Static vs dynamic** (position keystream vs plaintext-autokey). *Open.* The FG4
  depth test was inconclusive; this cycle's tree is consistent with both and adds
  no separating evidence (FG5 §8 ledger). The Chaocipher exclusion narrows
  "dynamic" to *additive plaintext-autokey* — it does **not** decide dynamic vs
  static.
- **Plaintext type — A vs B.** *Leans A (secondary cipher: compressed/encrypted),
  not proven* (FG3 §6). B (a large flat token inventory that is language in a weird
  encoding) remains logically alive below the ~40-pin second-order threshold.
- **Language.** *Unknown, and natural language is rejected at unigram order* (FG2/3).
- **Alphabet size.** 83 is the count under the current reading; it is not an
  independent fact — it is entangled with the reading of the glyph stream (Reading A
  vs B, FG3 §6).
- **`σ` additive vs affine.** *Open* (FG5 §3); a crib-activated solve.
- **Base grouping across triplets.** Bases are **equal within a triplet** (FG4 §3,
  Δ=0); the cross-triplet relation is untested (the W2/E4/W4 bridge, §5).

Everything except `C` is **moot for reading until `C` falls** (FG5 §4) — but the
A-vs-B question is *not* moot, because it changes how we would even recognize a
correct `C` (§4).

---

## 4. The bottleneck, and the strategic fork the plan must add

**Why every route terminates at `C` (FG5 §5, §6, §9).** Consistency is an
*abundant* property of this corpus — ~52% of multi-crib placements survive a
consistency check — so consistency filtering does not converge; adding cribs,
joint multi-phrase search, and consistency pruning all hit the same wall. The only
thing that discriminates a correct ordering is **cascade into a recognizable
plaintext**, and cascade needs `C`. This is proven, not asserted.

**The fork the guides identify but do not center: recognizable *as what*?** The
plan's recommended engines (AZDecrypt, `stblake/polyalphabetic`) are
strong-objective solvers that recognize correct `C` by **natural-language n-gram
score**. But FG2/FG3 measured the plaintext as **high-entropy / non-language**.
These two positions are in tension across cycles (FG2's own IMMEDIATE says
"suspend natural-language crib scoring… test for a second cipher layer before
investing further in ordering `C`"; FG4/FG5 nonetheless list language solvers as
the highest-leverage untried action). The tension is real and it is the pivot:

- **If A (secondary cipher):** a correct `C` yields *more high-entropy text*, and a
  language-objective solver will **not** recognize it. We would need a
  non-language success signal — the recovered layer's own structure, a known-
  plaintext crib on the *inner* cipher, or a compression/format signature.
- **If B (flat inventory / disguised language):** language-ish objectives may work,
  and the AZDecrypt route is well-motivated.

So the A-vs-B verdict is **upstream of the solver choice**, not a side question.
Committing GPU time to a language solver before resolving it risks searching with
the wrong objective — the same category of error as building a Chaocipher solver
for a non-Chaocipher cipher.

---

## 5. The prioritized way forward (reasoning, not tooling)

**Priority 1 — Acquire the cross-triplet W2/E4/W4 bridge pins.** *Bounded payoff,
serves every branch.* It is the one action that simultaneously: (a) enlarges the
depth stack any solver feeds on (FG5 §9); (b) moves the corpus toward the ~40-pin
single-component threshold where the A-vs-B verdict becomes a **direct
measurement** rather than a lean (FG3 §7); and (c) tests the global-key hypothesis
that would align the whole corpus into one stack (FG4 §8). The quantified tree (§2)
is the map of where these messages already agree, which is where bridge cribs are
most constrained. This is the highest-leverage concrete target and it is
independent of the A-vs-B verdict, so it can start now.

**Priority 2 — Resolve A vs B, and let it gate the solver.** Below ~40 pins,
**do not** run de-drift bigram/entropy probes — they measure the sampling lattice,
not the plaintext (FG3 §5, §7). Above it, the second-order channel opens and A-vs-B
is measurable. Concretely: push Priority 1 until a single component clears ~40
pins, then measure. If A, switch the `C`-search objective from language n-grams to
a **structure/known-crib** objective and treat the inner layer as a separate
problem. If B, the AZDecrypt/`stblake` route is validated and becomes Priority 3's
method.

**Priority 3 — Recover `C`, with the objective chosen by Priority 2.** The
instrument (Eye Crib Tester) already consumes any `C`-hypothesis and shows its
full-corpus cascade in one click (FG5 §7) — the last mile is built. What it needs
is a *source* of `C`-hypotheses stronger than consistency:
  - the strong-objective solvers (AZDecrypt, `stblake/polyalphabetic`) run over the
    enlarged depth stack — **but only under the objective A-vs-B licenses**;
  - overlapping cribs under a discriminator **stronger than consistency** (the
    order-gate's alphabet-interrelation test is the independent one the framework
    already flags) — since consistency alone is ~52% permissive (FG5 §5);
  - the depth/isomorph structure as a hard constraint on `C` (constant-difference
    isomorphs pin relations among values independent of language).

**Priority 4 — Break the static-vs-dynamic fork.** Still open and still blocked on
separating evidence. The tree (§2) is the natural place to look for a test:
under a position keystream, agreement between two messages at position `t` depends
*only* on shared plaintext at `t`; under plaintext-autokey it also depends on the
shared history reaching `t`. A carefully constructed agreement-after-divergence
statistic on the branch points might separate them where the earlier depth test
could not — this is a measurement to design, not a tool to build yet.

**Priority 5 — Non-audio external anchors.** With audio closed (§2), the remaining
external-anchor candidates are the web/ARG breadcrumbs and dev statements, most of
which prior effort has already worked. Treat this as low-probability background;
the internal route (Priorities 1–3) is where the odds are.

---

## 6. Guardrails — what not to do (from the guides + this session)

- **Do not** search gauge settings as if they were families: `σ=±1`, the
  Beaufort/variant flip, and the Quagmire alphabet choices are absorbed into the
  two unknown bijections `C` and `E` (FG5 §2). They are not a search axis.
- **Do not** re-open Chaocipher, group/dihedral autokey, or fractionation — all
  excluded deductively (FG5 §1–3), now with an independent empirical confirmation
  for the Chaocipher class (§2).
- **Do not** score `C`-candidates by natural-language fitness until A-vs-B is
  resolved (§4); the plaintext is measured non-language at unigram order (FG2/3).
- **Do not** run de-drift bigram/entropy probes below ~40 pins (FG3 §7).
- **Do not** treat consistency as convergence — it is abundant, not discriminating
  (FG5 §5).
- **Do not** treat `N=83`, the reading, or "position-indexed" as settled — the
  first two are reading-entangled and the static/dynamic fork is open.

---

## 7. Assumption ledger — delta from the Field Guides after this session

| Item | Prior status | Status now |
|---|---|---|
| Audio external anchor | wished-for, unexamined in the guides | **eliminated** — spectrogram/sample-domain/container all cleared this session |
| Chaocipher / group-autokey | excluded deductively (FG5 §3) | **excluded + independently confirmed** empirically (deck_lab, exhibit-validated engine) |
| Plaintext language | high-entropy, non-language (FG2/3) | **unchanged, and the Finnish-context lean is explicitly retired** as a plaintext claim |
| A-vs-B | leans A, side question | **elevated to the strategic pivot** that gates the `C`-solver objective |
| Depth stack | depth + isomorph "assets" (FG1) | **quantified** into a concrete shared-prefix tree feeding Priority 1 |
| Static vs dynamic | OPEN (FG4/FG5) | **OPEN, unchanged** — narrowed only to *additive* dynamic; a branch-point test proposed (Priority 4) |
| Recover `C` | standing bottleneck | **standing bottleneck**, now with the objective-choice fork made explicit |

**Bottom line.** The firm ground is the additive skeleton and its exclusions; the
wall is `C`; the new sharpening is that **A-vs-B must be resolved before we choose
how to attack `C`**, and the one action that advances everything at once is the
**cross-triplet bridge**. No tool should be built until we decide, on the evidence,
which objective the `C`-search runs under.
