# Field Report 30 — One Parameter, and a Channel That Does Not Need It

**Series note.** Thirtieth report of the EYESPIRAL series. FR29's horizon asked whether
any nonzero relation is invariant under a subgroup of drifts. The question has a
*deductive* answer and needed no search — and answering it opens a measurement channel
the series has not had. Instrument `eyefree.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Every row of the constraint system has right-hand side
drift·Δᵢ, so any determined relation — being a linear combination of rows — has the form
**D = drift · Δ_eff (mod 83)**. Verified for all 223 relations at eight drifts. Two
consequences follow immediately: a relation is drift-invariant **iff** Δ_eff = 0, in
which case it is identically zero (exactly FR29's base[W1] − base[E1] = 0); and for
Δ_eff ≠ 0 the map drift ↦ drift·Δ_eff is injective on 1…82, so the value is constant on
**no** subset of size greater than one, let alone a subgroup. FR29's horizon item is
answered without a search: there is nothing to find, and the skeleton is a
**one-parameter family** — fixing the drift fixes all 223 relations at once. The
constructive half is what that makes available. Inside a component q[s] = base_C +
drift·Δ_s with Δ_s known, so at any position carrying a component glyph, **p[t] = A +
drift·v[t]** where **v[t] = (Δ_{c[t]} − t) mod 83** is computable with no knowledge of
the drift, the bases, or the alphabet. Plaintext coincidences are therefore exactly
v-coincidences — a plaintext measurement that is drift-free, and non-circular because it
is taken only outside certified spans. It returns 1947 usable pairs and 14 coincidences
against an empirical null of 23.4 ± 4.8: **no structure, and underpowered for the
question that matters.** FG2/FG3's reported effective alphabet of 79 would sit at
z = +0.25 here. Planted controls at 40 and 20 fire at z = +4.5 and +14.9, so the method
responds to structure; the corpus's pair count is the limit.

---

## 1. Corrections first

**A scaling bug in my own plant, caught by the gate.** The channel identity failed its
selftest twice before I found it: I built the synthetic check with Δ defined as
q[s] − q[anchor], which is *drift·Δ*, not Δ. On the corpus the two coincide because Δ is
measured at drift = 1, so the corpus computation was never wrong — but the plant ran at
drift 11 and exposed the difference. Worth recording because it is the mirror of the
usual failure: the plant was wrong and the corpus code right, and only having both
caught it.

**FR29's horizon item dissolves.** It asked for a search over subgroups. The algebra
answers it outright, which is the fifth or sixth time in this series that Challenge I has
retired a horizon item on inspection rather than measurement.

## 2. D1 — the drift-linearity deduction

| drift | relations | matching d · D(1) |
|---|---|---|
| 1, 2, 3, 5, 7, 17, 41, 82 | 223 | **223** |

Every determined value is a fixed multiple of the drift. So:

- **invariant ⟺ Δ_eff = 0 ⟺ identically zero.** FR29's drift-invariant result was not
  luck; it is the only kind of invariance the system permits.
- **no subgroup invariance exists** for a nonzero relation, because d ↦ d·Δ_eff is
  injective.
- **the skeleton is a one-parameter family.** This restates FR26's bijectivity finding
  structurally: one known pair-difference pins the drift because the whole system moves
  together.

## 3. D2 — the drift-free plaintext channel

Inside a component, q[s] = base_C + drift·Δ_s. Hence for a position whose glyph lies in
that component,

  p[t] = q[c[t]] − base_m − K_g[t] = (base_C − base_m − κ_g) + drift·(Δ_{c[t]} − t)

so with **v[t] = (Δ_{c[t]} − t) mod 83**, we have p[t] = A + drift·v[t] within a fixed
(message, component) block. The map v ↦ p is affine and injective, so **p[t] = p[t′] if
and only if v[t] = v[t′]**.

Two properties make this worth having. It needs **no drift, no bases, no alphabet** — the
one-parameter unknown cancels out of a coincidence test. And it is taken only at
positions **outside every certified span**, so it is not circular with the isomorph
evidence that produced the components in the first place.

| quantity | value |
|---|---|
| glyphs with a known Δ | 47 |
| blocks (message × component) | 61 |
| positions excluded as circular | 368 |
| usable pairs | **1947** |
| coincidences | **14** |
| empirical null | 23.4 ± 4.81 |
| z | −1.96 |

## 4. D3–D4 — power, and why the result is a null rather than an answer

| effective plaintext alphabet | expected coincidences | z |
|---|---|---|
| 79 (FG2/FG3's figure) | 24.6 | **+0.25** |
| 70 | 27.8 | +0.91 |
| 60 | 32.5 | +1.88 |
| 50 | 38.9 | +3.23 |
| 40 | 48.7 | +5.25 |

Planted controls on the same block shape: alphabet 83 → z = +0.29, alphabet 40 →
z = +4.52, alphabet 20 → z = +14.85. **The method works.** What it cannot do at 1947
pairs is separate an effective alphabet of 79 from a flat one, and 79 is precisely the
figure the doctrine carries. So this channel does not resolve A-vs-B, and the reason is
sample size rather than method — pairs grow with the square of component coverage, so
widening the components is what would buy resolution.

## 5. D5 — watch-grade, unregistered

The observed count sits *below* the flat expectation (z = −1.96, one-sided P = 0.024).
For i.i.d. plaintext the coincidence rate cannot fall below 1/83 in expectation, so this
is either a fluctuation or positional anti-correlation of some kind. It is logged with no
mechanism and no correction for having looked, and it is not a finding.

## 6. What this adds to the model

- **The drift is the single remaining scalar unknown** in the alphabet skeleton, and its
  role is now characterised exactly rather than empirically.
- **A new measurement channel exists** that is independent of that unknown. It is
  currently underpowered, but it is the first plaintext probe in the series that needs
  neither pins in the classical sense nor a drift hypothesis, and it re-derives on sound
  evidence a quantity the doctrine previously measured over pins now known suspect.
- **The requirement is quantified**: roughly a doubling of determined-glyph coverage
  would take an effective alphabet of 70 from z = +0.9 to about z = +3.

## 7. Horizon

(1) **Widen the components** — this is now the single lever that improves both the
endgame exposure (FR19) and this channel's power, and FR18's fifteen candidate glyphs
remain the only route that does not require external anchors. (2) **Apply the channel to
the T3 opening**: under the stamped-header reading of FR29 those positions are not
plaintext, so their v-statistics should differ from body positions — the T1/T3 asymmetry
gives a built-in control, and this is the direct test FR29 nominated. (3) Standing:
#2⁻'s instance-level audit.

## 8. Reproduction

`eyefree.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the drift-linearity deduction verified across eight drifts, the channel
identity proved on synthetic data with known plaintext (v-differences reproduce plaintext
differences, and v-coincidence is exactly plaintext coincidence), flat and structured
plants at the null and far from it, non-circularity, and the baseline guard. The full run
reproduces D1–D5. Failures carry prefix `XD-MBYG04K-URS3LF`.
