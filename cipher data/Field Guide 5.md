# Cipher Family Field Guide 5 — Consolidating the Family Space, and the Instrument to Attack It

*Field Guide 4 closed by naming the three events that would earn a Field Guide 5:
cross-triplet bridge pins, an off-the-shelf solver's readable hit, or an external
anchor — each of which would move a "conditional" to "settled." **This cycle
delivered none of those.** No pin was added, no plaintext was read, no conditional
moved. What it did instead is worth its own record: it hardened the **boundary**
of the surviving family space with two gauge-level arguments, reduced the sprawling
model zoo to **two families / five generators** with a per-family inventory of
exactly what each leaves unknown, mapped the **geometry of the crib-search surface**
(and found consistency a surprisingly weak filter), and built a working
**instrument** — the Eye Crib Tester — that embodies the whole taxonomy and is
validated to eliminate placements soundly. The net epistemic effect is not a new
fact about the plaintext but a sharper, honest map of **why the standing bottleneck
(recovering C) is unavoidable** — every path that tries to route around it hits the
same wall, and now we can say why in the language of the search space, not just as a
coverage excuse.*

Repo placement: `cipher_data/`. Companions: Field Guides 1–4;
`report/cipher_lattice_report.md`, `report/keyspace_ledger.md`,
`eyewitness/keyspace_ledger.py`, and the instrument `eye_crib_solver.html` with its
audit harnesses. Everything asserted here about family math is executable in the
instrument.

---

## 1. The family space, restated — two families, five generators

Everything survives inside one skeleton, unchanged since the lattice report:

```
c_m[t] = C[( σ·p_m[t] + off_m[t] ) mod N]      N = 83
```

Two — and only two — live **families**, distinguished by how the offset `off` is
generated:

1. **Linear / static** — `off` is driven by *position* (a fixed slide, or a fixed
   keystream that is the same for every message). The offset at `t` does not depend
   on the plaintext.
2. **Nonlinear / dynamic** — `off` is driven by *prior plaintext* (plaintext-autokey).
   The offset at `t` is a running function of `p[<t]`.

Five concrete **generators** realize these two families, and they are exactly what
the instrument implements:

- **Progressive** (linear) — `off = base_m + drift·t`. The simplest survivor.
- **Gromark** (linear) — `off = base_m + K[t]`, `K` an order-2 linear recurrence
  `K[t] = (K[t−1]+K[t−2]) mod N` seeded by a two-number primer. This is the
  **searchable realization** of "general aperiodic keystream": aperiodic (period up
  to N²−1, so it passes the no-period filter) yet keyed by only two numbers.
- **PT-autokey Σ** (dynamic) — `off = β_m + Σp` (running plaintext sum; Alberti).
- **PT-autokey lag-k** (dynamic) — `off = β_m + p_{t−k}` (Vigenère plaintext-autokey).
- **XGAK** (dynamic/hybrid) — `off = β_m + drift·(t−s₀) + Σp` (position clock +
  autokey). The reconciler for the static-vs-dynamic fork: it is the one generator
  that carries both a position term and a plaintext-state term.

**The community's model zoo collapses into these.** "GAK," "XGAK," "stacked cipher
with a 0–82 cut," "seeded hybrid" — the lattice report already showed each reduces
to the surviving skeleton (a substitution ∘ position-keystream folds into a
per-message mixed alphabet; two stacked keystreams collapse to one; a 0–82 cut *is*
the per-message base). This cycle re-derived that collapse from scratch and pinned it
to the five generators above, so there is now a one-to-one map from "a theory someone
proposes" to "a generator in the tool you can test in one click."

**Trifid / fractionation is formally retired.** The lattice already excluded
fractionation on the repo's digit-level tests (the structure is glyph-level, not
digit-level; the eye-mark streams are structureless with no period). This cycle
closed an *earlier working session's* misframing — a "period-4 Trifid front-runner"
that had been floated on the strength of the d=4 anomaly — by confirming the d=4
signal is the generic autokey/progressive distance-4 coincidence (Field Guide 1),
not a fractionation period, and removing the Trifid engine from the instrument
entirely. The d=4 anomaly is evidence *for* the dynamic family, not for fractionation.

## 2. A stronger exclusion — ciphertext-autokey dies gauge-invariantly

The repo excludes **ciphertext-autokey** (a running key fed by prior *ciphertext*)
from the E1/W1 **re-sync structure**: 5 clean re-syncs — runs where two messages go
identical → differ → identical — where a propagating difference should not heal.
This cycle sharpens that exclusion from "ciphertext-autokey is out" to a statement
about an entire **gauge orbit at once**.

Consider the orbit of per-position encryption maps reachable by the free settings:
additive (Vigenère), Beaufort, variant-Beaufort, all four Quagmires, and affine
(`a·p+b`, `a` invertible) — each composed with any mixed plaintext alphabet `C` and
any mixed key alphabet `E`. Two facts hold for **every** member of this orbit:

- **(a)** the per-position map `c = φ(p ; state)` is a **bijection in `p`** (all of
  the above are);
- **(b)** a *ciphertext-autokey* state, by definition, is a running function of the
  emitted **ciphertext**.

Under (a)+(b), two messages sharing a ciphertext prefix hold **identical key state**
through the shared run; at the first differing position the states are still equal,
so by bijectivity the plaintexts differ there; from the next position on, the
ciphertext-fed states are driven by *now-different* ciphertext and diverge. A later
re-sync then requires the two divergent ciphertext histories to drive the state back
into equality — a coincidence — and **five** clean re-syncs compound that coincidence
to negligibility. Crucially, nowhere in this argument does the identity of `φ`, `C`,
or `E` appear. So the single structural observation (5 re-syncs) excludes the
ciphertext-fed variant of the **whole orbit simultaneously** — Vigenère-autokey,
Beaufort-autokey, every Quagmire-autokey, affine-autokey — with no need to scan them
one at a time.

The practical payoff is a **dimensionality cut**. `σ ∈ {+1,−1}`, the Beaufort/variant
flip, and the Quagmire alphabet choices are not *families* to search; they are
**gauge settings absorbed into the two unknown bijections `C` and `E`**. Under
plaintext-autokey (or a position keystream), re-syncs are *free* — identical
plaintext at aligned positions re-synchronizes the state automatically — which is
exactly why the two surviving families survive and the ciphertext-fed orbit does not.

## 3. The accumulator is additive — excluding multiplicative and group-theoretic autokey

A second gauge-level argument constrains **how the offset accumulates across
positions**, and it rules out a class the community could otherwise still propose.

The isomorphs recur at a **constant difference** `q_i − q_j` (a repeat pattern
reappears value-shifted by a fixed additive constant), not a constant *ratio* and not
a constant *group element*. Two occurrences of an isomorph therefore require the
accumulated key between them to differ by an additive constant in `(Z/83, +)`. Now
ask what accumulator structures reproduce that:

- A **multiplicative accumulator** would make two occurrences differ by a constant
  **ratio** in `(Z/83)*` — a different, non-additive signature.
- A **non-abelian group autokey** over `S₈₃` or `A₈₃` (compose a permutation per
  step, keyed by plaintext) would make two occurrences differ by a fixed **group
  element** under *non-commuting* composition — again not a constant additive shift,
  and order-dependent.

Only an **additive** accumulator over `(Z/83, +)` produces the observed constant-
difference isomorphs. So the offset progression lives in the cyclic group — the
same lever the repo used to exclude the Chaocipher class, extended here to exclude
the affine-accumulator and the group-theoretic autokey variants. Two clarifications
keep this honest: this constrains the **accumulator** (the across-position progression
of `off`), *not* the per-position plaintext multiplier `σ`; whether `σ` is a general
affine multiplier `a` rather than `±1` remains **open** (`FINGERPRINT`, "affine vs
additive sub-type"), because it is a crib-activated solve that needs an anchor. The
accumulator being additive and the per-position multiplier being possibly-affine are
independent questions, and only the first is settled here.

## 4. What each surviving family leaves unknown — the variable inventory

Consolidating `keyspace_ledger`, `cipher_lattice_report`, and Field Guide 4 into one
map of "what a crib or a search must actually pin." **Three unknowns are shared by
every family:**

- **`C` — the mixed alphabet** (glyph→value bijection). The standing blocker; a crib
  reveals `C⁻¹` only for the glyphs it physically covers.
- **`σ` — the plaintext multiplier** (`±1` assumed; affine `a` open, §3).
- **the global gauge constant** — `C` and the bases are jointly fixed only up to one
  additive relabel, so even a complete solve leaves a uniform rotation (the instrument's
  `injOffset`).

**Per-family extras:**

| family | extra unknowns beyond C / σ / gauge | keyspace note |
|---|---|---|
| **Progressive** | `drift` (one scalar) + `base_m` | bases **equal within a triplet** (Field Guide 4, Δ=0) → **3 constants**, possibly 1 under a literal header; cross-triplet relation untestable. ~83⁶ |
| **Gromark** | the 2-number **primer** (g₀,g₁) that seeds `K` + `base_m` | searchable realization of general aperiodic `K` |
| **General aperiodic K** | the **whole keystream vector** `K[t]` (one value per position) + `base_m` | ~83³⁰⁰ — **unsearchable** as such; Gromark is its tractable proxy |
| **Family-C (per-msg alphabet)** | a **per-message permutation** `S_m` stacked on `C` | most parameters of any survivor; where the community's stacked theories land |
| **PT-autokey (Σ / lag / XGAK)** | a per-message **seed β_m** + **the recurrence rule itself** (Σ vs lag-k vs Alberti-rotation) | no free `K` vector — the keystream self-generates from plaintext |

**Cross-cutting choices still undetermined** (these sit *above* any single family's
variables): linear vs general `K`; **static vs dynamic** (the Field Guide 4 fork —
still open, depth test inconclusive); affine vs additive `σ`; the base grouping across
triplets. All of them are **moot for reading until `C` falls**.

## 5. The geometry of the crib-search surface — consistency is a weak filter

The instrument added a **joint multi-crib placement search**: enumerate every position
each phrase can sit, and keep the combinations where all phrases are simultaneously
consistent (their merged glyph→value pins never conflict) under a chosen alphabet.
Running it produced a result about the *attack surface itself* that is worth recording:

- **Consistency prunes only about half.** A pair of 7-letter cribs under the default
  alphabet left **≈372,000 of ≈717,000** placements jointly consistent (~52%).
  Consistency is *necessary* but so abundant it barely localizes anything.
- **No alphabet-blind metric localizes the true placement.** Under the correct
  alphabet the true placement is merely *one* consistent placement among many, with no
  local signature — coverage, glyph-pin count, and shared-glyph agreement all fail to
  single it out. This was verified by **plant-and-recover**: a beam search that prunes
  intermediate partials by coverage **drops the planted true triple**. The only honest
  search keeps *every* consistent partial (correctness-preserving, with a loud abort
  cap), because any heuristic prune is lossy.
- **Therefore the only real discriminator is cascade-into-readable-text**, which
  requires `C`. This is the search-space restatement of the standing bottleneck: you
  cannot filter your way to the answer with consistency, because consistency is
  cheap; you have to *read*, and reading needs the alphabet.

This is the same conclusion Field Guides 2–4 reached from entropy and coverage, now
arrived at independently from the combinatorics of crib placement — which is the kind
of convergence that makes a bottleneck trustworthy rather than an excuse.

## 6. The decryption-gating taxonomy — why so little lights up

A clean account of *which unknown blocks each dark cell*, for `c = C[(σ·p + off) mod N]`:

- **(a) `C⁻¹` unknown at the cell's glyph** — the dominant reason. A crib reveals
  `C⁻¹` only for the glyphs it covers, and decryption propagates *only* to other
  occurrences of those glyphs. This is a **per-glyph**, not per-cell, gate: cover a
  glyph anywhere and every one of its instances lights up. The alphabet has up to 83
  symbols; a length-`L` crib pins ≤ `L` of them (fewer after internal repeats), so
  coverage tops out at a fraction and the rest is permanently dark until `C` is
  recovered.
- **(b) `base_m` unsolved** — only under a per-message-base view. A message a crib
  never touches has no solved base (union-find gated), so it stays entirely dark even
  where its glyphs are pinned elsewhere.
- **(c) autokey chain broken upstream** — under any PT-autokey view, the offset at `t`
  needs `p` at `t−1` (or the running sum), so decryption runs forward from a contiguous
  anchor and dies at the first unpinned glyph.

`σ` and the gauge are **global-correctness knobs, not per-cell gates**: a wrong `σ` or
offset yields a fully-populated but wrong/uniformly-rotated plaintext, not blanks. So
"green cells but no plaintext" is always (a), (b), or (c) — never a global setting.

## 7. The instrument — the Eye Crib Tester

The practical output of the cycle is a standalone browser tool that operationalizes
everything above. It is not a solver for `C`; it is a **consistency-and-cascade
instrument** — it eliminates placements that contradict and shows the cascade of those
that don't, matched exactly to the family space.

- **Five family engines** with the exact offset math of §1, selectable as tabs, each
  showing its own equation with **color-coded known (green) / unknown (amber)
  variables** — the variable you set lights up as you input it, and `C` stays amber as
  the standing unknown.
- **A self-certifying key solver.** Gaussian elimination over `Z/N` with unit-pivot
  selection, hardened this cycle to verify its own solution against every equation
  before returning: **sound for any modulus** (never a wrong answer), **complete for
  the ±1 / totally-unimodular systems the families produce** (difference equations
  `q[g] − base = known`), conservative on non-unit rings.
- **Union-find gauge gating** so a crib in one message never leaks a decryption into an
  unlinked one.
- **The joint multi-crib placement search** of §5 — full for two phrases,
  correctness-preserving-with-cap for three or more.
- **The corpus with a live overlay** that follows the active family, so a crib decrypts
  on sight.

**Validation.** Solver + engine paranoia audit **30/30** — soundness proven over 8,000
random systems (prime and composite moduli) cross-checked against brute force plus
3,000 planted engine cribs across all five engines, with zero wrong decryptions and
zero false-positives; union-find isolation and contradiction detection sound in both
directions. Search logic **9/9** (plant-and-recover in same-message, cross-message, and
three-phrase configurations). UI **24/24**. Every family-math claim in this guide is
executable, and its consistency verdicts are audited.

**What it is not:** it does not recover `C`. It is the instrument that will consume a
`C`-hypothesis and show its full-corpus cascade instantly — which is precisely the
lever the next real result needs.

## 8. Reassessed assumption ledger (delta from Field Guide 4)

| Assumption | Status in FG4 | Status now |
|---|---|---|
| Ciphertext-autokey | EXCLUDED (5 re-syncs) | **EXCLUDED gauge-invariantly** across the whole additive/Beaufort/Quagmire/affine × C × E orbit at once (§2) |
| Offset accumulator | additive, assumed | **additive, forced** by constant-difference isomorphs; multiplicative & group-autokey excluded (§3) |
| Family space | A/B/C/D lattice + community zoo | **two families / five generators**, one-to-one with the tool; Trifid retired (§1) |
| Per-family unknowns | scattered (ledger/lattice/FG4) | **single inventory** (§4) |
| Crib-search filter | — (new) | **consistency is weak** (~52% survive); no alphabet-blind discriminator; heuristic pruning is lossy (§5) |
| Static vs dynamic | OPEN (depth test inconclusive) | **OPEN, unchanged** — this cycle added no separating evidence |
| Recovering `C` | standing bottleneck | **standing bottleneck**, now with a search-geometry proof that no consistency filtering substitutes for it (§5, §6) |

## 9. Standing conclusion

Honest accounting: **no conditional moved to settled.** The static-vs-dynamic fork is
exactly where Field Guide 4 left it, no plaintext was read, and the cross-triplet
bridge is untouched. What the cycle bought is a **tighter boundary** and a **built
instrument** — and, as a byproduct, the clearest statement yet of *why the bottleneck
is the bottleneck*. Three independent routes that look like they might route around
recovering `C` — adding more cribs, joint multi-phrase search, filtering by
consistency — all terminate at the same wall, because consistency on this corpus is
**abundant** (§5) and only cascade-into-readable-text discriminates (§5, §6), and
cascade needs `C`. So the highest-leverage action is unchanged from Field Guide 4 and
now doubly justified: **recover the glyph→character ordering** — via the
strong-objective off-the-shelf solvers Field Guide 4 flagged (`stblake/polyalphabetic`,
AZDecrypt, both spanning the static and dynamic families this cycle formalized),
era-and-language-specific n-gram models, or the cross-triplet W2/E4/W4 bridge that
would enlarge the depth stack those solvers feed on. The difference is that the
instrument is now **ready to consume any `C`-hypothesis and show its cascade in one
click** — the last mile between "a solver returns an ordering" and "we can see whether
it reads" is now built.

## 10. Reproduce / instrument

```bash
# The instrument (family engines, solver, joint crib search, live overlay):
#   eye_crib_solver.html   — open in any browser; the in-page self-check runs on load.
# Audit harnesses (Node), reproducing the validation numbers in §7:
#   solver + engine paranoia audit ....... 30/30  (soundness vs brute force; plant-recover)
#   joint crib search logic .............. 9/9    (mergeCheck; plant-and-find; 3-phrase)
#   restructured UI smoke ................ 24/24  (layout, per-family knobs, overlay, decrypt)
# Family-space arguments (§1–§3) are deductive over repo-measured facts:
#   report/cipher_lattice_report.md      — surviving lattice, re-sync exclusion
#   report/keyspace_ledger.md            — surviving construction, keyspaces
#   eyewitness/keyspace_ledger.py        — reproduces the ledger from live measurements
```

## 11. Sources

- Repo: `report/cipher_lattice_report.md`, `report/keyspace_ledger.md`,
  `eyewitness/keyspace_ledger.py`, `FINGERPRINT.md`, Field Guides 1–4.
- Community model context (chaining failure, ~83 internal states, Pyry's
  autokey-Alberti isomorph demonstration, the d=4 observation): Noita Wiki, *Eye
  Messages*, https://noita.wiki.gg/wiki/Eye_Messages
- Off-the-shelf solvers that span both surviving families (carried from Field Guide 4):
  `stblake/polyalphabetic` (Vigenère/Porta/Beaufort/Autokey/Quagmire I–IV);
  AZDecrypt (crib-anchored search, non-contributing-symbol detector).

*Sequential record. **Field Guide 6 is when `C` partially falls** — a strong-objective
solver hit, an era-model climb, or a cross-triplet-enlarged stack — and the instrument
finally cascades a hypothesis into readable text. That is the event that moves the
standing bottleneck; this cycle built the machine that will recognize it.*
