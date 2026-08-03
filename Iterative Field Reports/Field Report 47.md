# Field Report 47 — The Fork Closes

**Series note.** Forty-seventh report of the EYESPIRAL series. FR46's audit showed the
model reproduces end-to-end but explicitly did not certify its premises. This cycle
attacks the largest of those premises and finds that one of its two branches has been
refuted for fifteen cycles without anyone checking. Instrument `eyerepair2.py`, selftest
6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR25 established that the corpus admits a determining,
injective reading only if one well-supported isomorph instance is discarded, and that
**two** repairs worked equally well: drop E1@68 (repair A) or drop E4@51 (repair B). FR27
favoured A on embeddedness — E1@68 is the only instance in either class with no parent
passage — but that is soft evidence, and the model has been carried as "conditional on
repair A" ever since. **The FR32/33 passage settles it, and it did not exist when the fork
was opened.** Rebuilt with the passage included, repair A gives **384 relations with zero
injectivity violations** while repair B gives **393 relations with four** — B forces
q[4] = q[60], q[10] = q[75], q[19] = q[35] and q[37] = q[66], every one of which a
permutation forbids. Without the passage both are clean (223 and 203 relations), which is
exactly the situation FR25 saw. A third reading — dropping *both* instances — is valid but
weaker at 259 relations, and agrees with repair A on all 259 comparable pairs, so it is a
strict weakening rather than a rival. **Repair A is the unique maximum among the readings
that survive**, and FR25's fork, carried as the outstanding debt for twenty-two cycles, is
closed.

---

## 1. F1 — the three readings

| reading | pool | relations | violations | glyphs | exposure |
|---|---|---|---|---|---|
| **A** — drop E3@101, E1@68 | 67 | **384** | **0** | 56 | 74.1% |
| **B** — drop E3@101, E4@51 | 74 | 393 | **4** | 55 | 73.2% |
| **AB** — drop all three | 64 | 259 | 0 | 55 | 73.2% |

Repair B determines *more* relations than A — and four of them are false.

## 2. F2–F3 — what B asserts, and what exposes it

Repair B forces **q[4] = q[60], q[10] = q[75], q[19] = q[35], q[37] = q[66]**. C is a
mixed alphabet, so q is injective and none of these can hold.

| configuration | repair A | repair B |
|---|---|---|
| without the FR32/33 passage | 223 rel / 0 viol | 203 rel / 0 viol |
| **with the passage (14 cells)** | **384 rel / 0 viol** | **393 rel / 4 viol** |

FR25 evaluated the repairs before the passage was discovered, and at that point both were
clean — which is why the fork stayed open. The passage is consistent with A and
inconsistent with B. The evidence that settles the question arrived six cycles after the
question was asked.

## 3. F4 — the logical shape, stated carefully

Passage + B is contradictory, so **either the passage is wrong or B is**. The passage does
not depend on the repair choice for its support: FR32 priced it at 3.6 × 10⁻⁶ across all
E4/W4 window pairs by agreement with the message pair's independently established w, and
FR35 found **fourteen consecutive cells** agreeing on that value — chance 83⁻¹³ — against a
shuffle null of zero. So B is wrong.

This is a **conditional refutation** and is recorded as one. If the passage were ever
withdrawn, B would revive alongside it.

## 4. F5 — the third reading is not a rival

Dropping both instances gives 259 relations with no violations, and compared with repair
A: **259 pairs agree, 0 disagree.** It is a strict weakening — the same content, less of
it — rather than a competing model. Anyone preferring maximum caution can adopt it and
lose 125 relations and 0.9 points of exposure, without changing a single claim.

## 5. What this changes in the doctrine

The model has been carried since FR25 with the caveat "conditional on repair A, which FR27
favoured but did not prove." That phrasing understated one thing and overstated another.

- It **understated** the evidence: three independent lines now converge on E1@68 — FR2's
  structural anomaly (the motif's only parentless occurrence), FR27's embeddedness
  asymmetry, and now the passage's incompatibility with the alternative.
- It **overstated** the openness: there is no longer a *choice* between two repairs. B is
  eliminated, AB is a weakening of A, and A is the unique maximum.

The remaining conditionality is real but different in kind: repair A asserts that a
three-pair skeleton match at E1@68 is spurious, roughly a one-in-six-hundred claim. That
assertion is unproven. What is no longer open is which instance to discard if one must be
discarded.

## 6. Where the model stands

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure, drift unpinned with H4 the only surviving hypothesis. Plaintext: large
effective inventory, no detected structure. Openings: stamped headers, a reading adopted
for consistency and shown by FR45 to be untestable independently.

## 7. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift, and there
is now only one model for them to be applied to — which was not true before this cycle.
(2) **The success criterion** (FR40, FR46 §A4) is unchanged as the most consequential open
item. (3) The passage now carries weight beyond its own claim: it discriminates the
repairs, so any future doubt about it reopens FR25's fork as well as FR33's widening.

## 8. Reproduction

`eyerepair2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — repair A reproducing at 384/0, repair B violating injectivity with the four
specific equalities, both repairs clean *without* the passage (reproducing FR25's
situation), the both-dropped reading valid but weaker, its agreement with A on every
comparable pair, and the baseline guard. The full run reproduces F1–F6. Failures carry
prefix `XD-MBYG04K-URS3LF`.
