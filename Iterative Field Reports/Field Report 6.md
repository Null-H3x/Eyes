# Field Report 6 — The Atlas Contradiction

**Series note.** Sixth report of the iterative series (Field *Reports*; Field Guide 6
remains reserved per doctrine). This cycle set out to grow the certified pin
component by feeding the community-certified isomorph atlas — including the short
classes the strict scan's base_len=13 never sees — through the repo's own consensus
machinery (`eyereach.py`, selftest 8/8 green, cross-validation rail armed). The rail
fired. What it caught reorganizes how the atlas may be used as evidence, localizes
the doctrine's known 16-pin bootstrap wall to a named conflict graph, and revises
FR2's motif discovery in a direction that makes it stronger.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified; all
constraint content conditional on the static additive family per FG5, with the
constant-difference (progressive) reading now explicitly under test rather than
assumed.

**One-paragraph verdict.** Read under full-span constant-difference (the
per-message-progressive model), the certified atlas is **globally inconsistent**:
only 27 of 65 instance pairs survive a joint consensus, two different pair pools
yield two internally-consistent, mutually-contradictory certification islands, and
the pre-registered cross-validation rail aborted the run — by design. Dissection
under isolation shows the wholesale drops were greedy-subset artifacts: **eleven of
thirteen classes are individually self-consistent, including #2⁻ with its
cross-triplet pairs** (vindicating FR3's bridges). The genuine breaks are two: the
short motif classes **#M and #M⁻ are internally inconsistent**, and self-consistent
long classes **conflict pairwise** (#1 vs #F, on physically overlapping spans). The
#M break localizes to a four-cycle among the near-dup pair's own two motif
occurrences — where same-passage is beyond doubt — and reduces to a five-line,
hand-checkable arithmetic contradiction (constants 28/30/2 forcing 60 ≡ 2 mod 83)
that **requires the pattern's dot positions**: skeleton-letter-only constraints
close every cycle cleanly. Conclusion: the motif is a **fixed skeleton with
variable interior** — pattern letters repeat, filler tokens vary per occurrence —
and the sound way to feed the atlas into the pin system is **pattern-position rows
only**. The FR5 battery stays UNCHECKABLE (the tier that would have linked its
glyphs is exactly the over-asserting one); the FR5 skeleton stands on the audited
strict island with its subset-relativity now stated; FR3's drift equality is
untouched (it was pattern-pair-based all along).

---

## 1. Corrections and negatives first

**Four plant iterations, all instructive, all logged.** (i) The reach plant's
passages were initially all-distinct — invisible to the calibrated anchor, whose
job is rejecting trivial all-distinct windows; real classes carry pattern letters,
and so must plants. (ii) My collision arithmetic for the determination engine was
fumbled twice in-line; deriving u-equalities on paper first is now the rule.
(iii) The deeper modeling error: I expected class constraints alone to determine
symbols, but per-pair constants absorb everything until **cross-context
collisions** (the same symbol at different offsets across instances) cancel them —
the real refrain has these everywhere; clean synthetic classes have none.
(iv) Conclusion drawn and acted on: the selftest's job is my additions (atlas-pair
construction, value guards, cross-validation, battery plumbing), not re-proving the
repo's consensus mechanics — the final gate runs on the repo's own audited plant,
asserting path-equivalence with direct feeding.

**The greedy-subset trap, caught by my own rail and then by isolation.** The
initial tier table showed all 9 cross-triplet pairs dropped and #1 keeping 1 of 6 —
readings I nearly published. Per-class isolation reversed both: the consensus keeps
a seed-order-dependent consistent island when the pool is globally inconsistent,
and pair-level drop counts against that island are not facts about the pairs.
**Consistencies from a satisfiable system are weak evidence (the q-variables
absorb); conflicts are the hard facts.** This epistemological inversion governs
everything below.

**FR2 revision, in the strengthening direction.** FR2 called the XYZ-motif "a
repeated word or particle." The four-cycle contradiction shows its occurrences are
not full-span repeats: the three dot positions carry occurrence-variable content.
The revised reading — fixed skeleton, variable interior — is *more* word-like
(a stem with inflection), and FR2's crib-shape constraint survives at the pattern
letters, where it always lived.

## 2. What was run

Tiers, pre-committed: S (strict scan, per-message rows — the audited 22/19/16
baseline, reproduced exactly); A (all 65 atlas instance pairs, values re-verified
against the corpus per run); A+S; P (pure-progressive rows). Rail: symbols
determined by both S and A must agree on every pairwise difference or the run
hard-fails. It hard-failed: 11 shared symbols, 51 disagreements. Tier A kept 27/65
pairs; A+S's pin-grade collapsed from 16 to 11 under 45 value-collisions. These
numbers are symptoms of joint over-assertion, not properties of the classes — the
dissection below is the result.

## 3. The conflict graph

**Isolation.** Eleven of thirteen classes are self-consistent under their own
full-span constant-difference systems — including every cross-triplet pair of #2⁻
and the whole #1/#C0/#C1 nest. The two exceptions are the motif family: #M keeps
10/15 of its own pairs, #M⁻ keeps 11/21.

**Pairwise unions.** The class-by-class compatibility matrix is dense with
conflicts among *individually consistent* classes — the flagship edge being
**#1 × #F**, whose instance spans physically overlap in W1 (cells 34–49), so the
two constant-difference systems constrain shared symbols and disagree. Low-conflict
classes (#3, #3+, #2+, #C0, #C1) are those with the fewest instances. The maximal
mutually-consistent coalitions are small; the strict tier's island is one of them,
not the only one.

**Drop-one localization of #M.** Removing any one of {E1@40, E1@68, W1@40, W1@70}
restores full consistency; removing either E2 instance does not. The conflict is a
four-cycle among the near-dup pair's own two motif sightings — the one place in the
corpus where same-passage is certain (E1@40 and W1@40 are *literally identical*,
nine for nine, inside the shared refrain; E1@68 vs W1@70 is the same occurrence
seen across the near-dups' 2-position indel offset). #M⁻ shows no single culprit:
its inconsistency is multi-way across seven instances, as expected once interiors
vary.

## 4. The minimal exhibit

Windows (L = 9, pattern `A.B.CB.AC`, dots at offsets 1, 3, 6):

```
E1@40: 47 44 48 42 19 48 13 47 19      W1@40: identical, all nine cells
E1@68: 71 11 74 56  4 74 19 71  4     W1@70: 68 46 17 36 13 17 21 68 13
```

Constant-difference rows (bases equal by FG4; constants shown): the within-E1 pair
forces x[·@68] − x[·@40] = 28 at every offset; the within-W1 pair forces 30; the
cross pair (E1@68, W1@70) forces 2. Offset 4 and offset 6 of the W1 pair chain
through the shared symbols: x[13] − x[19] = 30 and x[21] − x[13] = 30, so
x[21] − x[19] = 60. The cross pair's offset 6 says x[21] − x[19] = 2.
**60 ≢ 2 (mod 83).** No q-assignment satisfies the four windows' full-span rows.
Restrict the rows to pattern-letter offsets {0, 2, 4, 5, 7, 8} and every triangle
closes exactly (30 = 28 + 2, three times over). The dot rows are the broken
ingredient; the offending chain even shows the mechanism — the value 19 plays
pattern-letter C in three windows and *dot filler* in the fourth.

## 5. Consequences

**For the atlas as evidence.** Full-span constant-difference rows over-assert what
skeleton certification certifies. The sound atlas feed is **pattern-position rows
only** — plus full-span rows exclusively for pairs whose spans are verified literal
(the Δ=0 near-dup alignments). This is the constructive repair, and it is the next
instrument change: the reach campaign retried on sound rows.

**For the pin system.** The strict tier's island (22/19/16, the FR5 skeleton)
survives — its classes are long, low-dot, and self-consistent — but its status is
now explicitly *one consistent island among possible islands*, held up by being the
audited, lowest-spurious-risk configuration. The 16-pin bootstrap wall of doctrine
(the union-find contradiction) now has a mechanism, a graph, and named edges.

**For the models.** Nothing here falsifies the additive family. What breaks is the
conjunction ⟨full-span same-passage ∧ single constant-difference gauge⟩ across
classes. The within-class dot variation accounts for the motif family; the
cross-class edges among long classes (#1 × #F on overlapping cells) remain the
sharpest open objects — under strict per-message-progressive with same-passage
long classes those edges should not exist, so each such edge indicts one of its
premises. Cataloguing which premise fails per edge is precisely the conflict-graph
program the doctrine anticipated, now with its first data.

**Unaffected.** FR3's drift-equality deduction (pattern-pair increments only).
FR4's one-gauge deduction (literal header and literal opening spans — Δ=0
territory). The FR5 battery verdicts (still UNCHECKABLE; the apparent tier-A
"reach" to glyph 47 rode on the over-asserting rows and is withdrawn, not
converted to a verdict).

## 6. Horizon

(1) **Sound reach retry:** pattern-position row mode for the atlas feed; re-run the
tiers, the cross-validation, and the FR5 battery under it — the registered
hypotheses remain frozen and waiting. (2) **Edge autopsy:** for each conflict edge
between self-consistent long classes, extract the minimal broken cycle (as §4) and
classify the failing premise; the #1 × #F overlapping-span edge first. (3) **Dot
recovery:** under the progressive gauge the dot-position values are per-occurrence
recoverable relative to the skeleton — a small table of the motif's interior
variation, feeding the word/inflection reading. (4) Standing items unchanged.

## 7. Reproduction

`eyereach.py` (repo checkout; `EYEFORWARD_DIR` / `EYE_CORPUS` / `EYE_ATLAS`
overrides): `--selftest` for the 8-check gate (audited-plant path-equivalence,
guards, monotone reach, cross-validation, battery labels); full run reproduces the
baseline guard, tier table, and the cross-validation abort. The dissection
(isolation, union matrix, drop-one, exhibit) is in the session transcript and
re-derivable from the printed windows in §4 with pencil arithmetic — the
contradiction is three subtractions and one comparison.
