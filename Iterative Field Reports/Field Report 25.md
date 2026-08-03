# Field Report 25 — A Repair That Determines

**Series note.** Twenty-fifth report of the EYESPIRAL series. FR24 swept thirty model
configurations and concluded that no cell determines anything without asserting a false
equality. This cycle takes up its horizon item — locate the constraints producing those
equalities — and in doing so finds that FR24's conclusion was scoped to the wrong space.
Instrument `eyerepair.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Every one of the six false equalities has a verified-minimal
core, and **every core contains E3@101** — the #M⁻ bridging window FR15 priced at
coincidence grade. One core needs only **two pairs** and is checkable by hand in four
lines. That localisation then opens the repair FR24 missed: FR24 ranged over the *model*
space (drift partitions, base structures), but the defect lives in the *pool* space.
Under the fixed-drift reading, dropping E3@101 removes one violation of six; sweeping
every remaining atlas instance for a second removal finds exactly two that clear **all**
violations while retaining determination — **E3@101 + E1@68 → 28 forced differences,
zero violations**, and **E3@101 + E4@51 → 36 forced differences, zero violations**.
These are the first configurations in twenty-five cycles that determine alphabet
relations *and* respect injectivity, so FR24's "no such cell exists" is corrected to "no
such cell exists in the model space." The repairs are not free: E3@101 sits in a
two-pair skeleton and is cheap to discard, but E1@68 and E4@51 sit in three-pair
skeletons where a chance match runs about one in six hundred, so discarding either is
expensive on the pattern evidence — the same unresolved tension FR21 flagged.

---

## 1. C1 — where the falsehoods come from

Minimal cores under the free-drift reading, each verified minimal at runtime:

| forced equality | core size | classes involved | contains E3@101 |
|---|---|---|---|
| q[46] = q[4] | 11 | #2⁻, #3, #M, #M⁻, strict | yes |
| q[71] = q[10] | 11 | #2, #2⁻, #3, #M⁻, strict | yes |
| q[81] = q[17] | 9 | #2⁻, #3, #M⁻, #S, strict | yes |
| q[64] = q[20] | 10 | #2, #2⁻, #3, #M⁻, strict | yes |
| q[50] = q[30] | 9 | #2⁻, #3, #M⁻, strict | yes |
| **q[68] = q[36]** | **2** | #M⁻, strict | yes |

E3@101 is in every core. It is the common ingredient of every falsehood the constraint
system asserts — which is a striking convergence with FR15, where an entirely
independent argument (pattern-weight null, p ≈ 0.10) called that same window
coincidence-grade.

**The two-pair exhibit.** The last row is small enough to check by hand:

- Pair A — #M⁻, East 2 @ 80 × East 3 @ 101, shift 21, pattern `A.B..B.A`. Offsets 0 and
  7 both give q[36] − q[41] = X; offsets 2 and 5 both give q[17] − q[57] = X. So
  **q[36] − q[41] = q[17] − q[57]**.
- Pair B — strict, West 1 @ 70 × East 2 @ 80, shift 10. Offset 0 gives q[41] − q[68] = Y;
  offset 2 gives q[57] − q[17] = Y, i.e. **q[17] − q[57] = −Y**.
- Therefore q[36] − q[41] = −Y, and q[41] = q[68] + Y, giving **q[36] = q[68]**.

Two pairs, four lines, one equality that a permutation forbids.

## 2. C2 — the repair FR24's sweep could not see

FR24's thirty cells varied the drift partition and the base structure. The defect is not
in the model; it is in the constraint pool. Under the fixed-drift reading — the one that
determines things at all — the search over second removals gives:

| pool | symbols | forced differences | violations |
|---|---|---|---|
| full | 51 | 276 | 6 |
| drop E3@101 | 50 | 256 | 5 |
| **drop E3@101 + E1@68** | 49 | **28** | **0** |
| **drop E3@101 + E4@51** | 49 | **36** | **0** |

Two repairs, each removing two instances, each yielding a system that determines
alphabet relations and violates nothing. That is the cell FR24 declared empty, and it
exists — just not along the axes FR24 varied. **The correction: "no configuration
determines without asserting a falsehood" holds over the model space, not over the pool
space.**

E1@68 is the same window FR21 localised as the minimal single-instance repair under the
global-drift model, and the same one FR2 flagged nineteen cycles ago as the motif's solo
occurrence with no parent passage. Four independent lines now meet there.

## 3. C3 — what the repairs cost

| instance | class | skeleton pairs | expected chance matches corpus-wide |
|---|---|---|---|
| East 3 @ 101 | #M⁻ | 2 | **0.14** |
| East 1 @ 68 | #M | 3 | 0.0017 |
| East 4 @ 51 | #3 | 3 | 0.0016 |

E3@101 is cheap: a roughly one-in-seven chance match, unremarkable by any standard this
series has used. The second removal is not. Both candidates sit in three-pair skeletons,
where a chance match runs about one in six hundred, and both patterns match nowhere in
the corpus except their own class instances. Discarding either asserts that a
three-constraint skeleton match is coincidence, which the null says it very likely is
not.

So the honest position is a genuine trade rather than a solution: **the corpus admits a
consistent, determining reading only if one structurally well-supported isomorph
instance is wrong.** That is the same tension FR21 identified and could not resolve; what
this cycle adds is that the tension is now minimal (two instances, not a class), specific
(two named alternatives), and *productive* — the repaired pool determines 28 or 36
relations rather than nothing.

## 4. Where this leaves the doctrine

- **The pin inventory can be rebuilt, conditionally.** Under either repair the system
  determines relations among roughly thirty symbols with no injectivity violation. That
  is far short of the 276 the unrepaired global-drift pool claimed, but unlike those it
  is not known-false.
- **FR24's exclusion is narrowed, not overturned.** Within the additive family and a
  *fixed* pool, determination and injectivity remain mutually exclusive. Repairing the
  pool is what breaks the deadlock, and repairing the pool is a hypothesis about the
  atlas rather than about the cipher.
- **E3@101 should be treated as excluded going forward.** Three independent lines — FR15's
  null, FR23's determination census, and this cycle's cores — agree on it, and it is the
  only removal that costs nothing on the pattern evidence.

## 5. Horizon

(1) **Discriminate E1@68 from E4@51.** They are alternative second removals with
different yields (28 versus 36 determinations) and different homes (#M in T1 versus #3 in
T3). Independent evidence — whether either window is anomalous in some way the pattern
weight does not capture — would decide between them, and FR2's observation that E1@68 is
the motif's only parentless occurrence is exactly that kind of evidence, not yet
quantified. (2) **Rebuild the certified inventory under each repair** and recompute
FR17's leverage map, FR19's exposure and FR20's pair supply against it. (3) **Check
whether the repaired systems survive the other rails** — the gauge ladder, the
opening/body test, the run-forced merges. A repair that fixes injectivity but reopens an
old contradiction is not a repair. (4) Standing: #2⁻'s instance-level audit, the 15
candidate glyphs.

## 6. Reproduction

`eyerepair.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the full pool reproducing 276 forced differences with six equalities,
E3@101 removing exactly one, the E3@101 + E1@68 repair clearing all violations while
still determining, the two-pair core verified minimal, and the baseline guard. The full
run reproduces C1's cores and hand exhibit, C2's repair sweep and C3's pricing. Failures
carry prefix `XD-MBYG04K-URS3LF`.
