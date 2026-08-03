# Field Report 194 — PROGRAMME REVIEW: THE FULL RECORD AUDITED FOR GAPS, STALE DOCTRINE, AND THE NON-GAME LINES THAT REMAIN

*July 2026. Cycle: EYESPIRAL-C, SURVEY + CHALLENGE I product. Reviewed: all 193
Field Reports, 12 doctrine documents, 109 instruments, the 2026-07-21 dossier
audit, and the shipped data artifacts in the Iteration 1–3 archive. Constraint
honored throughout: no line proposed below requires in-game Noita content.*

---

## 0. Verdict in one paragraph

The record is in strong shape analytically — the model is settled, the reading
is linked across all nine messages, the internal drift-pinning routes are
exhausted by proof rather than fatigue, and the retraction discipline caught
its own five-cycle failure. What the review found is not a missed attack but
**four errors in the current record (one in the standing headline ask), a
doctrine layer that has fallen roughly forty cycles behind the reports, one
uniqueness claim certified at 1/4,000th the rigor of the claim it replaced,
six recorded-but-unexecuted audits, and five genuinely untried internal
lines** — three of which are magnitude-sensitive and therefore live where
every scale-invariant test is proven dead.

---

## 1. ERRORS FOUND — corrections first, per convention

### E-A. FR192/FR193's headline ask is wrong by one symbol *(verified by construction this cycle)*

FR192 §7, repeated in FR193's target table:

> *"a single known indicator value yields five plaintext positions **and pins
> the drift**, because the five differences are known and one absolute value
> fixes the scale."*

It does not. The fragment constant is free, so an indicator observation is one
equation in two unknowns:

```
p0[m] = A + d·r[m]  (mod 83)     r = {E1:0, E2:63, E3:54, W3:30, E4:23}

learn ONE absolute value  ->  82 surviving (d, A) pairs      [measured]
learn E1's value alone    ->  82 surviving; d fully free     [r=0 degenerate]
learn TWO values          ->   1 surviving                    [exact]
```

This is the **E9 error class** (FR107: a gauge fixed for one computation reused
where it does not hold) — the fourth catch of that shape. The corrected minimal
ask is **two indicator values** (any two of the five determined ones), or one
indicator value plus any other absolute pin inside fragment 1. Still the
smallest ask the project has ever had; just not one symbol. FR193's ranking
table and any outward-facing ask must be corrected before publication.

### E-B. The Iteration 1–3 archive fails E6's own reproducibility guard *(verified live)*

```
$ python3 eyeaudit.py
ModuleNotFoundError: No module named 'iso_relax'
```

The archive ships 104 Python instruments and every report, but **not** the
seven-module dependency closure (`iso_relax`, `plantlab`, `pyry_gate`,
`support_min`, `isomorph`, `chain_models`, `chain_extract`) and **not**
`corpus.json` / `atlas.json`. This is byte-for-byte the failure mode E6 logged
at FR104, whose standing guard reads: *"any future reconstitution must verify
the audit RUNS, not merely that files are present."* The zip cannot rebuild its
own skeleton; every quantitative line of effort below therefore requires the
`null-h3x/eyes` checkout, not this archive. Fix: ship the closure + data, or a
`requirements` manifest with fetch instructions, and add `eyeaudit.py 11/11` as
a packaging gate.

### E-C. FR192 internal count inconsistency

§1 says *"six of the nine indicators are determined, giving ten testable
pairs"*; §4 lists **five** determined values. C(5,2)=10 matches the pairs, so
either "six" is a typo or one determined indicator was silently dropped from
the value list. One-line erratum either way; matters because the indicator set
is now the acquisition centerpiece.

### E-D. FR191's status line contradicts the non-bijective standing

FR191 model status: *"`C` an arbitrary permutation."* The standing model
carries **8 forced homophones** (`|image(q)| ≤ 75`); `C` is explicitly not a
permutation, a point FR127 proved by exhaustion and FR189/190 spent five cycles
re-learning the vocabulary for. The §2 prose ("or close to one") shows the
intent, but the status line is exactly the loose usage the FR189 standing rule
was written to kill. Erratum-level; worth patching because status lines get
quoted.

### E-E. CORRECTIONS.md died at FR118

The errata ledger — the project's designated institutional memory — has **no
entry after FR118**. Roughly seventy-five cycles of corrections live only in
individual reports: FR126 (cross-block excess withdrawn), FR128 (wrong
objective function), FR131/132 (artifacts built on the wrong quantity), FR141
(alphabet-bound simulation withdrawn), FR163→164 (homophone reversal),
FR152/153/162→**176** (the largest correction in the series), FR185–189→190
(the five-cycle conflation). Anyone applying the ledger's own instruction —
"reports are the lab notebook, corrections are carried forward" — would today
carry none of these forward. Backfill is mechanical: the doctrine-change tables
in each FR are already in ledger format.

---

## 2. THE DOCTRINE LAYER IS ~40 CYCLES STALE

FR176–FR193 changed the state materially: **one reading** (not ~30/68), **five
fragments = the five components**, **819 positions across all nine messages**,
**all 36 base differences forced**, **single drift with a 2-anchor opening**,
**re-ranked acquisition targets**, **15-token crib demoted to worst option**.
Almost none of that has propagated:

| document | vintage | stale claims still carried | superseded by |
|---|---|---|---|
| `CURRENT_STATE.md` | FR156 | "~30 maximal readings"; "choose anchors as pairs to cut the space ~5×"; "West 3 is dark, 148-position island, +1 anchor"; 435-position reading; instrument list lacks `eyeverify.py` | FR176 (unique), FR178 (W3 linked into fragment 1), FR193 (targets re-ranked) |
| `ACQUISITION_SPEC.md` | body FR108-era, banner FR156 | entire body is repair-A: 9 components, 11 anchors, 3-anchor opening, blind clusters, 17 ratios; headline ask "15 consecutive tokens" | FR147 (6 anchors, 2-anchor opening), FR176, FR193 (**explicitly mandates the rewrite**; 15-token crib unverifiable — longest determined window is 8) |
| `HYPOTHESIS_CATALOG.md` | FR120 | tests against the **withdrawn** `CANDIDATE_READINGS.txt` (17 readings); coverage table says E1/W1/E2 have zero coverage | FR132, FR176–178 (one reading, all nine messages covered) |
| `INVARIANT_CORE.md` | FR162/168 | framed as the refuge from a 68-reading ambiguity | FR176 — still valid, now a *conservative floor*; needs the banner |
| `MASTER_RECORD.md` | FR140 | Part 6's "last non-guessing work" list; offset-4 reopening presented as pending | resolved/subsumed by FR144–146 extended-skeleton adoption — but no document *says so* (see §3.4) |
| `REPAIR_RANKING.md` | FR128 | ranks a fork that no longer exists | FR150 (East 3@101 inert), FR146 |
| `GPU_TASK_QUEUE.md` | FR94/95 | queues sweeps that completed | FR99, FR116 ("compute is no longer the binding constraint") |
| `DISCORD_POST.md` | FR140 | 409 relations/57 glyphs; 191 positions; asks for **15 tokens or 11 pins** | FR145+, FR193 — **the community-facing ask on record is the wrong ask** (see L-7) |
| `Agents.md` | community frame | GAK consensus, "affine family not ruled out," "plaintext expected Finnish," six-group question open | FR172/173 (not language), FR179 (family placed), FR175/167/191 (multiplicative, keyed, keyword-C all refuted) — unreconciled (see L-4) |

None of this is cosmetic. Three of these documents are the ones an outside
contributor or a fresh agent instance reads first, and today each would send
them to a superseded model, a dissolved ambiguity, or an unverifiable ask.
**One consolidation cycle (an FR156-style rebuild against FR193's state)
retires the whole table.**

---

## 3. RECORDED-BUT-UNEXECUTED AUDITS

Items the record itself flagged and never ran. Ordered by what they cost.

### 3.1 Uniqueness is certified at 1/4,000th the standard of the claim it replaced — **the priority item**

FR162 settled "exactly 68 readings" for the class-only system with **795,545
greedy orders**, a flat discovery curve, and Chao1 = observed. FR176 then made
the *larger* claim — with the atlas pool mandatory, the reading is **unique** —
on **18 runs, later 150**. The project's own Rule 7 (*a simulation varying a
parameter must be checked where the answer is known*) and the FR162 precedent
both say what to do: re-run `eyemax` in atlas-mandatory mode at the FR162
scale, publish the discovery curve and Chao1.

Both outcomes pay. Saturation at 1 upgrades the headline from "found in 150
runs" to "counted"; any rival appearing means the invariant core quietly
resumes load-bearing duty and the doctrine banners were premature. Instrument
exists (`eyemax.c` + `run_maxset.sh`); this is hours of Threadripper time.

### 3.2 The triplet assignment `g` — assumed for 190 cycles, now provably vestigial: dissolve it formally

`CIPHER_FORMULA.md` Table 1 still carries `g` as **"ASSUMED — hardcoded, never
re-derived"** (also MASTER_RECORD Part 5). But under the standing model the
index does no work: the drift is **single** (forced under repair C, multiply
bridged under the extended skeleton) and `kappa_g` is absorbed into `b_m`
per message. `K_g[t] = d·t + kappa_g` with both facts applied is just
`d·t` plus a per-message constant — the triplet layer asserts nothing.

One-cycle closure: rebuild with `g ∈ {global, per-triplet, per-message}` and
show relations/exposure/reading identical. That converts a 190-cycle "ASSUMED"
flag into a proof of irrelevance, simplifies the published formula by one
symbol family, and is precisely Rule 3 (*rank models by what they must
assert*). The formula the world should see is:

```
c[m][t] = C[ ( p[m][t] + b_m + d·t ) mod 83 ]
```

### 3.3 The reading order — the "only untested inherited input left" (FR165 horizon 3), still untested

Two mitigations since: glyph identity (hence the whole skeleton) is
label-invariant, and FR191's 720-ordering sweep covered the six symmetric
orders × 120 relabelings for the keyword question. What remains inherited is
only Toboter's derivation that exactly six orders yield the unbroken 0–82 set.
Low value, cheap to close: re-run the 0–82 census over all reading orders
once, in-house, and move the item from "inherited" to "reproduced." Worth
doing only because it is the last line in the assumption ledger.

### 3.4 The FR140 reopenings have no closure record

MASTER_RECORD Part 0/Part 6 reopened the **offset-4 exclusion** (+193 relations
on offer) and the **17-ratio re-audit under non-bijectivity**, calling the
latter "the last non-guessing work." The FR141–146 arc then rebuilt the
skeleton on a different basis (extended skeleton; single drift; ratios
dissolved with the fork per FR150), which *subsumes* both — but no document
states their disposition, and MASTER_RECORD still presents them as pending.
One paragraph each in the consolidation cycle: offset-4 → state whether the
extended pool includes it and what it changes; 17 ratios → superseded by the
single-drift standing. Otherwise a future cycle re-opens them cold (the exact
failure the sixth methodology rule was written for).

### 3.5 Two small unaccounted residues

- **FR102's 29th excess dimension.** "28 of the 29 are local wiggle" — the
  29th was never named. Almost certainly the global scale, but say so.
- **FR184's surviving +1.2σ.** Logged, never characterized, never formally
  accepted as residual. One sentence in the ledger either way.

---

## 4. NEW INTERNAL LINES — untried, non-game, and mostly magnitude-sensitive

The scale-invariance results (FR30/36/53) kill every test that depends only on
equality structure. What survives is anything that compares **known relative
vectors against candidate absolute laws** — the move FR192 invented for the
indicators and then applied exactly once. The project now possesses **two**
fully-determined relative vectors it has never swept:

### L-1. The base-vector structure sweep *(highest-value new line)*

FR178 forced **all 36 base differences** — the nine `b_m` are known relative,
up to drift scale. Nobody has asked whether the vector is *structured*. The
FR166 "±29 observation" (assumption 3, verdict *"survives — an observation,
not a test"*) has sat untested for 28 cycles and is prima facie evidence that
it might be: several forced differences cluster at ±29·d.

Sweep, per candidate law `b_m = δ·f(m) + c` and per drift `d`:

```
f(m) candidates, all corpus-internal:
  message index (E1..E5,W1..W4 in each of the plausible orderings)
  message length            {99,103,118,102,137,124,119,120,114}
  indicator glyph value     c0[m] = {50,80,36,76,63,34,27,77,33}
  stamped-header-derived values (headers are literal glyphs — known data)
  East/West split encodings (sign, offset, interleave)
```

Consistency of `δ = Δb/Δf` across all 36 pairs is the test — magnitude-
sensitive, pre-registrable, negative-controllable with shuffled `f`. **Any hit
pins the drift outright** (the sixth internal drift route, after FR191 declared
five dead — this one postdates the tools that killed the others). A clean null
finally retires FR166's assumption 3 properly instead of leaving it parked.

### L-2. The indicator self-reference sweep *(extends FR192 beyond numberings)*

FR192 tested exactly one identity family — message *numberings* — and nulled
it. The indicator relative vector `{E1:0, E2:63, E3:54, W3:30, E4:23}` has
never been tested against the **self-referential** candidates: `p0[m] = g(c0[m])`
(the indicator encrypts its own glyph value), `p0[m] = g(length_m)`,
`p0[m] = g(header_m)`. Same machinery as L-1, ten pair-equations per
hypothesis, consistency pins `d`. This is the natural "message identity"
reading FR192 named and then only partially explored.

### L-3. The joint law: do the two vectors know each other?

With both vectors determined, cross-laws cost one scan each: `p0[m] = b_m + c`
(the indicator *is* the message's own offset — a designer convention with real
precedent in indicator-based classical systems), or `b_m = δ·p0[m]`. Ten
testable pairs, magnitude-sensitive, drift-pinning on a hit.

*L-1/L-2/L-3 are one instrument and one cycle combined (`eyelaw.py`, gated on
planted truths, pre-registered thresholds, shuffled-`f` negative control).
They are the only remaining tests that can pin the drift from inside — because
they are the only remaining quantities with magnitudes.*

### L-4. The rival ledger the community frame demands

`Agents.md` carries the community consensus — GAK-class hidden-state deck,
four surviving groups, `S₈₃` expected — and **no Field Report has ever engaged
it by name**: `AGL`/`Frobenius` appear in zero FRs; `GAK` last appears at FR60.
Meanwhile the project holds discriminators the community frame has never been
scored against:

| corpus fact | progressive model | generic hidden-state GAK / deck |
|---|---|---|
| 7 different-shift alignments predicted from one drift (FR118: 6 free predictions, 83⁻⁶ ≈ 1.2e-11) | predicted | each offset free |
| homophone under-production, 8 vs 11–53 control (FR164) | expected | unexplained |
| flat frequency + isomorph coexistence (FR173/181) | source property | needs it too, asserts more |
| 794 relations, 0 contradictions from 143 classes | consequence | not predicted |

One cycle writes this head-to-head for `AGL(1,83)`, `C₈₃⋊C₄₁`, `A₈₃/S₈₃`, and
the dossier's scoped-generator conjecture, in the FR182 verdict-table format.
Rule 3 does most of the work: every rival must assert strictly more to explain
the same facts. Deliverables: closes Agents.md §7 Q1 from this side, arms the
publication refresh (L-7), and converts "sole tested rival refuted" — which
reads as a weakness — into a scored field.

### L-5. Reconcile the parallel dossier frame

The 2026-07-21 audit of `eye_messages_focused_state_dossier` sits in the
archive with **zero cross-references** to the FR series, describing a rival
research programme (instruction/checksum generator, Q-C opcodes, P17 parsers,
Gate joins) whose corrected state still lists "GAK/A83/S83 possible." Most of
its residue dissolves in one page under the standing model — e.g. its **seven
carry-free successor pairs**: under uniform plaintext the model expects
`1027/83 ≈ 12.4` adjacent `+1` ciphertext pairs by chance; seven observed is
*below* chance and evidence of nothing. Its "equality templates" are the
isomorph classes; its "exceptional first trigram" is FR192's indicator. A
reconciliation appendix prevents the two frames from generating duplicate work
or contradictory public claims.

### L-6. Re-run the blind catalog on the object that now exists

The FR120 pattern/grammar sweep ran against 461 positions and 17 candidate
readings — both superseded. Against **one** reading of **819 positions** the
discrimination arithmetic changes entirely (nothing to discriminate; a k≥2 hit
is now a *finding*, and grammar predicates like windowing/periodicity get
double the support). FR173's uniformity says expect null — run it anyway,
because the catalog is the standing answer to "did you check for X" and it
currently certifies the wrong object. Cheap; instruments exist.

### L-7. The publication refresh — the highest-yield external action, currently mis-aimed

FR170 §7 named "publish for collective attack" the top remaining action.
What is on record (`DISCORD_POST.md`, FR140-era) asks the community for **15
consecutive tokens** — which FR193 proved *unverifiable* (no 15-window is
determined) — or **11 pins** (now 6), against a model two rebuilds old. The v2
post writes itself from the current state, with the corrected asks:

```
1. TWO indicator values                       (per E-A; smallest verifiable ask)
2. 8-token crib at East 3, positions 105–112  (the only fully-checkable window)
3. the q[36]/q[68] and q[22]/q[64] pairs      (invariant homophone tests)
4. 6 anchors: 2 in component 1, 1 per other   (full solve)
```

plus `eyeverify.py` and both invariant cores, so nothing requires trusting a
single choice this project made. Sequence it **after** §1's errata and §3.1's
certification so the numbers ship final.

### L-8. One scope ruling is owed to the record

FR101 settled: mechanism recovery *is* the solution; inner layer out of scope
(E3 in the ledger). FR176 then adopted "GOAL B — order `C` until the plaintext
coheres" as *"the only live route,"* and FR177/178 rank work by it. Both cannot
head the doctrine. If Goal B is in scope, the one concrete executable is the
FR182 survivor — **candidate-number streams** (base-83 digits of
Petri-adjacent constants: 16807, 2³¹−1, `0xe4bc7e0`, release dates, the
Mnemonica sequence) matched against fragment 1's equality structure,
pre-registered, shuffle-controlled. If it is not, strike the Goal B framing
from FR176–178's status lines. Either ruling is fine; carrying both invites
the next FR189.

---

## 5. CLOSED — do not reopen without new evidence of the stated kind

For the next SURVEY phase, the walls, with their proofs:

**Sweeps** — 27.16B, canary-verified, zero survivors (FR99/FR116); any seeding
transform into the swept range is *already swept* (FR100 doctrine — this
covers Mnemonica-as-seed, FR167a). **Structured `C`** — keyword refuted across
all 720 orderings (FR191); affine refuted, 18 distinct multipliers over 19
invariant relations (FR166/167); keyed/magician construction refuted (FR167).
**Keystream rivals** — plaintext autokey collapses 73 glyphs to one value,
`C(73,2)=2628` exactly (FR137); multiplicative `r^i·p+φ` refuted at 3,320
candidates without brute force (FR175); constant-offset mechanism refuted
(FR157); periods 2–90 and polynomial/exponential bends excluded (FR56/91/102).
**Enumeration** — the residual 2¹⁹ is affordable and unscorable; a uniform
payload has nothing to rank (FR170 §2–3). **Dot-cell linking** — 1,110
propagation conflicts; a greedy subset is FR35's error (FR177). **Word/phrase
cribs** — plaintext is not language at any granularity (FR172/173/181).
**Alphabet narrowing** — all 3,403 merges tested; the 22 unconstrained glyphs
are invisible by construction (FR135/141). **The repair fork** — East 3@101 is
inert (FR150). **West 3 special-casing** — dissolved; its exposed positions
read inside fragment 1 (FR178). **The 48 contradictory classes** — chance
isomorphs, z = −0.97 against control (FR165). **Drift from inside, via any
scale-invariant channel** — proven dead five ways (FR30/36/53/166/191); only
the magnitude-bearing lines of §4 are exempt, and they are exempt for a stated
structural reason.

---

## 6. PRIORITY ORDER

| # | item | cost | what it buys |
|---|---|---|---|
| 1 | §3.1 uniqueness certification (`eyemax`, atlas-mandatory, FR162 scale) | hours of compute | the headline claim at the record's own standard — everything downstream quotes it |
| 2 | §1 errata cycle: E-A correction, E-C/E-D patches, E-E ledger backfill | one cycle | a record safe to publish from; the ask arithmetic fixed |
| 3 | §4 L-1/L-2/L-3 — `eyelaw.py`, the three magnitude sweeps | one cycle | the only remaining internal drift routes; retires FR166 assumption 3 either way |
| 4 | §3.2 triplet dissolution + §3.4 closure paragraphs | one short cycle | formula minimality; two zombie reopenings buried properly |
| 5 | §2 doctrine consolidation (CURRENT_STATE / ACQUISITION_SPEC / catalog rebuild) | one cycle | the FR193-mandated rewrite; onboarding stops misdirecting |
| 6 | L-4 rival ledger + L-5 dossier reconciliation | one cycle | the community frame answered in its own vocabulary |
| 7 | L-7 publication refresh (after 1–5) | zero compute | the highest-yield external action, aimed correctly for the first time since FR140 |
| 8 | E-B packaging fix; L-6 catalog re-run; §3.3 reading-order reproduction; L-8 scope ruling | as convenient | hygiene, completeness, and one decision only the principal can make |

Items 1–3 are independent and can run in parallel. Nothing above requires an
anchor, a crib, Petri, or the game.

---

## 7. What this review did not find

No untested cipher family with a real prior. No unexploited forced constraint
(the base differences were the last, and FR178 spent them). No statistical
channel that survives scale-invariance beyond the three in §4. No error in the
load-bearing proofs re-derived here (FR127's exhaustion, FR137's collapse,
FR164's calibration, FR178's linking — the last verified by its own
sign-error's self-diagnosis). The internal game is nearly over, and the record
mostly knows it; the gaps above are the difference between *nearly* and
*audited shut*.
