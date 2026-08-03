# Field Report 22 — Injectivity Picks One Configuration

**Series note.** Twenty-second report of the EYESPIRAL series. FR21 applied
injectivity for the first time and read it as a refutation of the certified pool. This
cycle audits every configuration the series has published, corrects FR21 on two counts,
and finds that the constraint does something more useful than condemn: it selects.
Instrument `eyeinject.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Two corrections to FR21, and one result. **First**, FR21
compared symbols only *inside* the certified domain and found a single collision. The
sound check — asking for every pair of solution symbols whether q[a] − q[b] = 0 is
*forced* — finds **six**: (4,46), (10,71), (17,81), (20,64), (30,50), (36,68).
**Second**, and more consequential, FR21 tested under a single global drift. Sweeping
the two model choices the series has been weighing gives a clean 2×2, and only one cell
satisfies injectivity: **per-triplet drifts *with* the E3@101 bridge removed.** Global
drift fails with the full pool (6 collisions) and still fails with the bridge removed
(5). Per-triplet drifts fail with the full pool (6) and come out **clean** with the
bridge removed. So neither change suffices alone, and their conjunction is exactly
FR16's coherent package — reached here by a completely independent route, from a
non-linear constraint the linear machinery cannot represent, with no appeal to
satisfiability or to the free-drift health measure FR16 used. FR21's headline therefore
needs rewriting: the pool is not false in general; it is false *under a global drift, or
with the weak bridge kept*, and FR21's localisation to class #M and instance E1@68 is a
property of that model rather than a defect of the atlas.

---

## 1. Corrections first

**FR21 under-counted.** It computed the certified domain (ten symbols) and looked for
duplicate values among them, finding (4,46). But injectivity applies to all 83 glyphs,
not just certified ones, and the right question for any pair is whether the equality is
*forced* — `classify(q[b] − q[a] = 0) == redundant` — not whether two entries happen to
match. Asked properly across every solution symbol, the global-drift model forces six
distinct pairs equal.

**FR21 generalised from one model.** Its sweep covered all 82 drift *values* but only
the global-drift *structure*. The per-triplet structure — which FR13–FR17 have used
throughout and which FR16 argued for on independent grounds — behaves differently, and
that difference is the finding.

**An unsound audit caught and discarded mid-cycle.** My first retroactive pass compared
`solve()` values under the per-triplet model and reported **45 collisions among ten
symbols** — every pair. That is the solver setting free variables to zero and collapsing
the representative, not a fact about the corpus. It is the same trap FR8, FR9 and FR17
each recorded, arriving in yet another disguise, and it is now a negative gate in the
selftest: the naive check must report more violations than the sound one on a system
that has none.

## 2. The 2×2

| | full pool | reduced (E3@101 removed) |
|---|---|---|
| **global drift** | 6 collisions | 5 collisions |
| **per-triplet drifts** | 6 collisions | **CLEAN** |

Forced collisions under the global model are present at drift 1, 2, 3, 7, 17, 41 and 82
alike — no drift value escapes them. And the coherent configuration stays clean when the
run-forced merges are added: FR16's package plus E4/E5, and plus E1/W1, both satisfy
injectivity.

## 3. Why this matters

The series has argued for FR16's package twice before, both times from inside the linear
constraint machinery: once from satisfiability (which configurations avoid contradiction)
and once from the free-drift health measure (which avoid buying consistency by
flattening the keystream). Both arguments live in the same formalism, and a shared
formalism can share a blind spot — a concern FR14 raised explicitly when it noted that a
contradiction derived solely inside one framework can always be blamed on the framework.

Injectivity is outside that formalism. It comes from the cipher's own definition — C is
a mixed alphabet, therefore a permutation — and the GF machinery structurally cannot
represent it. That it independently selects the same configuration is the strongest
corroboration the package has received.

It is also a reminder about FR21's framing. What looked like "the certified pool is
false" was really "the certified pool is false *in the model I happened to test it in*."
The constraint was doing discrimination work and I read it as condemnation.

## 4. What is now standing

- **The coherent package** — per-triplet drifts, E3@101 discarded, per-message offsets
  with E4/E5 sharing one, all thirteen classes otherwise intact — is the only
  configuration that satisfies satisfiability, the health measure, *and* injectivity.
- **FR21's localisation is withdrawn as a claim about the atlas.** Class #M and instance
  E1@68 are where the global-drift model's falsehood surfaces; under the per-triplet
  reading with the bridge removed, #M is unproblematic and E1@68 needs no repair. FR2's
  observation that E1@68 is the motif's solo occurrence stands as a structural note, not
  as evidence against it.
- **Injectivity as a standing rail** survives from FR21, with the method corrected:
  test forced equalities, never solver representatives.

## 5. Horizon

(1) **Re-derive the certified inventory under the coherent package**, now that it is the
sole survivor of three independent checks; FR17's anchor leverage map and FR20's pair
counts were both computed against the global-drift pool and should be recomputed.
(2) **Extend injectivity beyond pairwise** — it also forbids any k glyphs from occupying
fewer than k values, which is a stronger constraint than pairwise distinctness and might
prune further. (3) **#2⁻'s instance-level audit** remains the last standing item from
FR15. (4) The 15 candidate glyphs (FR18) still want a non-isomorph constraint form.

## 6. Reproduction

`eyeinject.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — both systems build, the global model does violate injectivity, FR21's pair
is among the violations, the per-triplet coherent model does not violate, the negative
gate proving the naive solve()-value check invents violations (45 versus 0), and the
baseline guard. The full run reproduces C1's forced-collision census with its drift
sweep, C2's 2×2 and C2b, and C3's verdict. Failures carry prefix `XD-MBYG04K-URS3LF`.
