# Field Report 3 — The Bridge Ledger

**Series note.** Third report of the iterative series. Doctrine remains Field Guides
1–5; FG6 stays reserved. This cycle discharges FR2's pre-registered obligation (the
full-template mask) and opens the roadmap's Priority 1 (the cross-triplet bridge) with
an instrument, `eyebridge.py`, selftest 13/13 green before corpus contact.

**Scope constraint (given).** Isomorphs untouched; instrument read-only; family space =
the FR1 survivor set (static Perfectly Isomorphic: progressive / Gromark / general-K).

**One-paragraph verdict.** The depth tree is now resolved to individual positions, and
it contains more bridge structure than the doctrine has priced. The corpus's opening
region is a nested stack: positions 1–2 universal; **3–5 six-deep across all of
T2+T3**; **6–9 four-deep across {E3, E4, W4, E5}** — E3 shares the opening template
four positions deeper with the *other* triplet than with its own; 10–20 three-deep in
T3; 3–24 three-deep in T1. Under the static family this certifies **K₂ − K₃ constant
on [1..9]** (bases absorbed), merging the T2 and T3 depth stacks on nine positions —
81 new cross-triplet depth pairs. The two cross-triplet isomorph classes already in
the atlas (#2⁻ spanning T2→T3, #M⁻ spanning T2→T1) contribute 21 rigid K-increment
equalities, and under the progressive family they **force drift equality across all
three triplets** — which in turn makes K₂ − K₃ constant *everywhere* and collapses the
whole corpus into a single depth stack. Separately, the pre-registered full-template
mask landed exactly as FR2 predicted: with atlas spans and opening spans both removed,
**every spectral residual collapses at every lag** — the coincidence-spectrum chapter
is closed, and the only surviving global spectral feature of this corpus is the d = 1
suppression. No corpus-wide spectral signal exists.

---

## 1. Corrections and negatives first

**An FR2 horizon item dissolves on inspection.** FR2 §8 proposed occurrence-relative
co-location as "the one place template events still touch K under general-K." Working
the algebra: the increment equalities such an instrument would test — K[aᵢ+j′] −
K[aᵢ+j] equal across occurrences at every pattern pair — are exactly the content of
the skeleton-identity certification the atlas already carries. The proposed test could
only re-derive what the isomorph classes certify by existing. Withdrawn, and the
withdrawal is what pointed this cycle at the *cross-triplet* classes, where the same
algebra is not yet on the books.

**A roadmap line needs a post-FR1 edit.** WAY_FORWARD §2 calls the depth tree
"consistent with both surviving families (shared plaintext re-synchronizes a
plaintext-autokey state *and* aligns a position keystream)." FR1 killed the
plaintext-autokey branch; the tree now reads purely as position-keystream alignment.

**Instrument iterations, logged.** Three plant failures preceded green. (i) The null
plant seeded a fresh RNG *inside* the element comprehension, producing nine constant
messages, two of which collided into a fake 109-long head run — a seeding-discipline
lesson worth writing down. (ii) The full-mask plant was underpowered at one planted
link per message; fixed at three. (iii) Most instructive: after boosting, the "atlas
mask alone kills body-template d=4" check failed at z = 2.0 because the plant's
*shared opening* had grown an accidental d = 4 link — amplified ninefold by exactly
the mechanism this instrument exists to expose. The opening is now rejection-sampled
clean. The plant misbehaved by doing precisely what the corpus does.

**One unregistered observation, disclosed.** Eyeballing the opening value table after
the run: at position 20, five messages carry value 47 — W2 and E3 rejoining the T3
stack value after their divergence points (W3 alone breaks it). Single-position
re-convergences sit outside this cycle's registered statistics (head runs; internal
runs ≥ 3). Naive joint pricing gives p ≈ 0.002, but it was found by looking, so it is
logged watch-grade only and drives a pre-registered census next cycle (§8).

## 2. Problem set

Two obligations. First, FR2's registered prediction: the masked-spectrum residuals
(d = 9 at z = 2.52; the t = 6 trifold) are opening-template leakage, and a mask
covering atlas spans *plus* opening spans collapses everything. Second, the roadmap's
Priority 1: the cross-triplet W2/E4/W4 bridge — "the quantified tree is the map of
where these messages already agree, which is where bridge cribs are most constrained"
— with the cross-triplet base/keystream relation explicitly flagged untested (FG4 §3
boundary). The instrument serves both: position-resolved cartography feeds the opening
mask *and* the bridge ledger.

## 3. Instrument, plants, pre-registration

`eyebridge.py`, stdlib-only, deterministic, read-only. Components: pairwise
literal-agreement cartography (head runs anchored at t = 1; internal runs); the
opening-span mask rule (fixed before the corpus run: per message, [0, e] where e is
the deepest head-run reach with any partner); the full-template masked spectrum
(machinery inherited from `eyecho`); the bridge-ledger enumerator (cross-triplet
isomorph classes → increment-equality constraints) with a checker validated on a
planted general-K corpus, including a deliberately broken plant that must be flagged;
and the depth-pair merge metric. Selftest 13/13.

| rule | threshold |
|---|---|
| internal literal run | length ≥ 3 certifies a bridge event (corpus-wide null E ≈ 0.006) |
| head-run novelty | length ≥ 3 certifies template beyond the universal 2-position header |
| full-mask verdict | z < 2.0 collapsed; z ≥ 3.0 corpus-wide signal flag (FR2 bands inherited) |
| verdict lags | {3, 4, 7, 9, 13, 17}, 2000-iteration permutation nulls; full d = 1..24 sweep at 400 |

## 4. The position-resolved depth tree

Head runs (last agreeing position, all 36 pairs): within T1, all three pairs run
1..24 — **t1open is a three-way identical stack**, not merely pairwise. Within T3,
all three pairs run 1..20, and all three messages diverge simultaneously at 21.
Within T2, all three pairs stop at 1..5. Cross-triplet: **E3 runs 1..9 with each of
E4, W4, E5** — deeper than with its own triplet — while W2 and W3 run 1..5 with every
T3 message, the same depth as within T2.

The stack, by position, with values:

| positions | stack | values |
|---|---|---|
| 0 | 9-way distinct | per-message indicator |
| 1–2 | all 9 | 66, 5 |
| 3–5 | {E1,W1,E2} / {W2,E3,W3,E4,W4,E5} | 48 62 13 / **49 75 54 (six-deep)** |
| 6–9 | T1 continues / W2 alone / W3 alone / **{E3,E4,W4,E5}** | **2 60 29 40 (four-deep)** |
| 10–20 | T1 continues / {E4,W4,E5} | E3 departs at 10; T3 trio 2 55 9 15 59 18 68 3 36 5 47 |
| 21–24 | {E1,W1,E2} only | T3 trio splits three ways at 21 |
| 25+ | near-dup islands | E1/W1 body 22.7×; E4/E5 9.4×; W4/E5 4.7× |

Internal literal runs ≥ 3 (certified events): five, all inside near-dup pairs —
E1/W1 at 29 (L=4) and 37 (**L=13**), E4/E5 at 25, 29, 38 (L=3 each). **No literal
cross-triplet body runs exist.** The corpus's cross-triplet bridge material is the
openings plus two isomorph classes, and nothing else.

**The E3 question, raised and settled by body depth.** The opening cartography alone
would group E3 with T3. Reassignment (E3 keyed with K₃) would even simplify #2⁻ into a
within-stack repeat. But body-only agreement (t > 25) is decisive in the other
direction: E3↔T3 rates sit at baseline (1.8–1.9×, two hits each, Poisson-unremarkable),
identical to its baseline relation with W2/W3. E3's membership in T2 rests where it
always did — the #4 class (W2@18, E3@24, W3@23) — and its opening tie to T3 is a
*template* fact, not a keystream fact. Both facts are now on the books separately,
which is what matters for the ledger below.

## 5. The full-template mask — the registered prediction lands

Mask = atlas spans ∪ opening spans (rule of §3; opening ends: T1 messages 24, T3
messages 20, E3 9, W2/W3 5). Every verdict lag collapsed:

| lag | hits | comps | x | z | verdict |
|---|---|---|---|---|---|
| 3 | 2 | 415 | 0.40 | −1.30 | collapsed |
| 4 | 6 | 391 | 1.27 | +0.72 | collapsed |
| 7 | 2 | 329 | 0.50 | −0.94 | collapsed |
| 9 | 5 | 290 | 1.43 | +0.88 | collapsed |
| 13 | 3 | 225 | 1.11 | +0.26 | collapsed |
| 17 | 1 | 195 | 0.43 | −0.89 | collapsed |

The d = 1..24 sweep flags nothing at |z| ≥ 2 except d = 1 (z = −2.44) — the
zero-adjacent-doubles suppression, which survives every mask because it is a global
property, and which under the progressive gauge is the known hole in the plaintext
adjacent-difference distribution. **Conclusion, per the FR2 registration: the
coincidence spectrum of this corpus contains no corpus-wide signal at any lag. Every
excess ever observed in it — d = 4 included — was repeated-passage structure. The
spectrum chapter is closed.** (FR2's masked d = 9 watch item: confirmed collapsed,
z = 0.88.)

## 6. The bridge ledger

**Literal bridges (openings).** The six-deep stack on 3–5 and the four-deep stack on
6–9 certify, under the static family with the shared-template reading, that
**K₂ − K₃ is constant on [1..9]** (per-message bases absorb the constant; σ cancels
because the template plaintext is common; the conspiracy alternative prices at
~83⁻⁹ ≈ 10⁻¹⁷). On those nine positions T2 and T3 are one depth component:
**81 new cross-triplet depth pairs** on top of the 967 within-triplet pairs. T1
attaches through the universal header only — a 2-position certificate.

**Isomorph bridges.** Two atlas classes span triplets, and their pattern pairs are
rigid cross-K links: #2⁻ (E3@64 ↔ E4@73, W4@76, E5@74; pattern pairs at spacings 4,
4, 13) yields 9 increment equalities K₂[64+j′] − K₂[64+j] = K₃[a+j′] − K₃[a+j];
#M⁻ (E3@101 ↔ six T1 occurrences; spacings 3, 7) yields 12 equalities linking K₂ to
K₁. The enumerator and its checker are plant-validated, broken-plant flagged.

**The drift deduction.** Under the progressive family (K_g[t] = drift_g·t + κ_g),
each increment equality reads drift_gA·(j′−j) = drift_gB·(j′−j) with j′−j invertible
mod 83, so: #2⁻ forces **drift₂ = drift₃** and #M⁻ forces **drift₁ = drift₂**. All
three drifts are equal. Corollary: K₂ − K₃ = κ₂ − κ₃ is then constant *everywhere*,
not just on [1..9], and likewise for T1 — **under the supported per-message-progressive
family, the entire nine-message corpus is a single depth stack** with all 36 pairs in
depth at every shared position (~3,500 depth pairs). The opening certificate and the
21 increment links are, under that family, consistency confirmations; under general-K
they are the certified subset: [1..9] merged plus 21 links, T1 weakly attached.

**P1 status.** The roadmap's untested cross-triplet relation is now measured: the
bridge exists, its literal span is [1..9], its rigid links are enumerated, and the
progressive-family corollary upgrades it to a global stack. What the bridge is *not*,
on current evidence, is a body-literal phenomenon — bridge cribs must be aimed at the
opening stack, where constraint density is highest: positions 3–5 are six-deep
(one crib token constrains six equations), 6–9 four-deep, 10–20 three-deep, 3–24
three-deep on the T1 side. That is the concrete real estate FG5 §9's solvers should
be fed first, and it is where the ~40-pin component threshold (FG3 §7) is cheapest to
approach — with the honest caveat that depth pairs are raw material for pins, not
pins; the conversion runs through the existing iso_relax → support_min pipeline.

## 7. Consequences

The corpus's statistical-anomaly ledger is now short. Closed: d = 4 (FR2, template),
every other spectral lag (this report, template + openings), the autokey branch (FR1),
period-4 K (FR2), position-locked K structure (FR2, power-limited). Open and genuine:
the d = 1 suppression (a plaintext-difference hole under progressive), the near-dup
divergence structure (FR1's Σ-ledger geometry), and the pin wall itself. The
constructive assets gained across the three reports: the XYZ-motif (FR2), the
position-resolved stack table, the K₂−K₃ offset certificate, the drift-equality
deduction, and the merged-component arithmetic — all of which point the same
direction: **the opening stack is the attack surface.**

## 8. Horizon

(1) **Re-convergence census, pre-registered next cycle:** scan all positions for
k-way stack matches among post-divergence messages (the 47@20 trigger, §1); null =
per-position independent 1/83 matching against the local stack value; verdict bands
set on plants before the corpus run. Payoff: every certified re-convergence position
is an extra depth cell in exactly the crib-constrained region. (2) **Feed the merged
stack to the pin pipeline:** run iso_relax → support_min with the [1..9] cross-triplet
cells (and, under the progressive reading, the global gauge) added to the depth
inventory; measure whether the largest pinned component moves toward the ~40
threshold. This is the direct P1 continuation and uses existing repo tooling.
(3) **E3 membership** becomes decidable if the pipeline run under both groupings
(E3∈K₂ vs E3∈K₃) yields asymmetric consistency — a cheap discriminating experiment to
bolt onto (2). (4) The balanced-Σ loophole and lag k ≥ 11 residuals from FR1 remain
the family-space cleanup items, lower priority than the stack work.

## 9. Reproduction

`eyebridge.py`: `python3 eyebridge.py --selftest` (13 planted checks, gate),
`python3 eyebridge.py` (gate, then C1 cartography, C2 internal runs, C3 opening
spans, C4 full-mask spectrum, C5 bridge ledger, C6 merge metric). Expects
`noita_eye_core/corpus.json` and `data/isomorph_atlas.json` (`EYE_CORPUS` /
`EYE_ATLAS` overrides); atlas values re-verified against the corpus before any
statistic prints; failures carry prefix `XD-MBYG04K-URS3LF`. The stack table in §4 is
checkable by eye from the corpus opening values; the drift deduction in §6 is two
lines of modular arithmetic from the atlas instance table.
