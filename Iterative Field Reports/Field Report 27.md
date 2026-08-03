# Field Report 27 — Packing, and Which Repair the Corpus Prefers

**Series note.** Twenty-seventh report of the EYESPIRAL series. FR26 produced the first
relational skeleton that determines and survives the rails, and left two questions: which
of FR25's two repairs is right, and what more can be squeezed from the skeleton. This
cycle answers the first and prices the second. Instrument `eyepack.py`, selftest 7/7
green, with the packing estimator validated against exact enumeration before any corpus
number is quoted.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR22 nominated "injectivity beyond pairwise" and I expected it
to dissolve; in FR26's component setting it does not. Each component carries a free
additive base, so injectivity across components is a **packing constraint** — 47
determined glyphs must occupy 47 distinct slots out of 83. It prunes the placement space
by a factor of **147,000**, from 2.25 × 10¹⁵ to about 1.5 × 10¹⁰, which is real and not
remotely enumerable. It does **not** discriminate the drift: every one of the 82
non-degenerate drifts admits a packing, so eyedrift's degeneracy certificate is
undisturbed and external anchors remain required. What packing does buy is a steep tail —
with nine of the ten components fixed only **44 completions** remain, which is enumerable
by hand, so the tenth anchor is replaceable. The cycle's decisive result is elsewhere and
settles FR26's open question: **embeddedness**. Five of the six #M instances sit inside a
larger certified passage (#1, #F, #C0, #C1), and all three #3 instances sit inside #3+ or
#S. **East 1 @ 68 is the only instance in either candidate class with no parent passage** —
corroborated by nothing except its own skeleton match. Repair A discards exactly that
instance; repair B discards one that sits inside #3+ at the same start position. On
independent structural evidence, **repair A is favoured**.

---

## 1. The packing constraint

FR26's skeleton splits 47 determined glyphs into components of 19, 7, 7, 3, 3 and four of
2. Within a component every pairwise difference is fixed; the component's absolute
position is a free additive base. Injectivity then requires the value sets
(base_c + offsets_c) to be pairwise disjoint.

Pairwise, the constraint is substantial without being fatal: component 1 against
component 2 forbids 62 of 83 relative placements, leaving **21**. No pair is impossible,
so this produces no new contradiction.

Jointly:

| quantity | value |
|---|---|
| unconstrained placements (rotation gauge fixed) | 83⁸ = 2.25 × 10¹⁵ |
| satisfying cross-component injectivity | ≈ 1.53 × 10¹⁰ |
| pruning factor | **≈ 147,000×** |
| surviving fraction | 0.0007% |

Real, and useless alone. A 10¹⁰ search space is not a solve.

**And it does not discriminate the drift.** Sweeping all 82 non-degenerate drifts, every
one admits a packing. That was the cycle's most attractive hypothesis — injectivity
breaking the drift degeneracy without any external anchor — and it fails cleanly.

## 2. What packing does buy: the residual curve

| anchors | components fixed | remaining placements | glyphs known | corpus exposed |
|---|---|---|---|---|
| 2 | 1 | 1.54 × 10¹⁰ | 19 | 25.0% |
| 3 | 2 | 4.95 × 10⁹ | 26 | 34.9% |
| 4 | 3 | 1.56 × 10⁹ | 33 | 45.0% |
| 5 | 4 | 6.38 × 10⁷ | 36 | 48.9% |
| 6 | 5 | 2.63 × 10⁶ | 39 | 55.0% |
| 7 | 6 | 7.18 × 10⁴ | 41 | 57.1% |
| 8 | 7 | 1.88 × 10³ | 43 | 59.5% |
| **9** | 8 | **44** | 45 | 61.8% |
| 10 | 9 | 1 | 47 | 64.6% |

The tail is the useful part. At nine anchors only **44 completions** survive — enumerable
by hand, and separable by any weak additional signal. At eight, 1,880 remain, which is
enumerable by machine. So FR26's ten-anchor figure is better read as **nine anchors plus
a trivial enumeration**, and the marginal value of anchors seven through nine is much
higher than a linear reading suggests.

## 3. The discriminator: embeddedness

FR25 left two repairs, each discarding one instance with a three-pair skeleton, and asked
for independent evidence. The atlas supplies it directly — whether an instance sits inside
a larger certified passage.

**Class #M (L = 9):**

| instance | parent passages |
|---|---|
| East 1 @ 40 | inside #F@30 |
| **East 1 @ 68** | **STANDALONE** |
| West 1 @ 40 | inside #1@34, #F@30, #C1@34 |
| West 1 @ 70 | inside #1@64, #C1@64 |
| East 2 @ 45 | inside #1@39, #F@35, #C0@39 |
| East 2 @ 80 | inside #1@74, #C0@74 |

**Class #3 (L = 12):**

| instance | parent passages |
|---|---|
| East 4 @ 51 | inside #3+@51 |
| West 4 @ 53 | inside #S@36 |
| East 5 @ 52 | inside #S@35, #3+@52 |

Every instance in either class is corroborated by an independently certified larger
passage containing it — **except East 1 @ 68**. Its three-pair skeleton match is the only
evidence for it. E4@51, by contrast, sits inside #3+ at the *same start position*, so
#3 there is literally a sub-window of a longer certified class.

That is the asymmetry FR26 asked for, and it points one way. It also quantifies FR2's
nineteen-cycle-old observation that E1@68 is the motif's solo occurrence "with no parent
passage" — at the time a descriptive remark, now a discriminating one.

**Five independent lines now converge on E1@68:** FR2's structural anomaly; FR6's
four-cycle contradiction running through it; FR21's injectivity localisation; FR25's
presence in every minimal core; and this cycle's embeddedness asymmetry.

## 4. What is established, and what is still owed

**Established.** Cross-component injectivity is a genuine constraint (147,000× pruning)
that does not discriminate the drift. The residual curve makes anchors seven through nine
disproportionately valuable and the tenth unnecessary. Repair A is favoured over repair B
on structural evidence independent of the constraint machinery.

**Still owed.** Repair A remains a *hypothesis*: it asserts that a three-pair skeleton
match — roughly a one-in-six-hundred coincidence — is spurious. Embeddedness makes that
assertion much more comfortable, because a genuine repeated passage would be expected to
recur inside its usual host, but it does not prove it. And the T3 opening contradiction,
FR26's last survivor, is untouched by this cycle.

## 5. Horizon

(1) **The T3 opening** is now the only standing contradiction and the natural next target;
FR26 showed no single class or instance removal clears it, so it wants minimal cores under
the repaired pool. (2) **Feed the 223 relations plus the packing constraint to the crib
machinery** — together they are a far stronger filter than either alone, and the crib
tester can cascade a candidate in one pass. (3) **Anchor strategy is now specific**: the
first two anchors must land in component 1 (fixing rotation and drift together), and
anchors beyond the seventh are worth more than the curve's early entries suggest.
(4) Standing: #2⁻'s instance-level audit, the 15 candidate glyphs.

## 6. Reproduction

`eyepack.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the exact packing counter against brute force, impossible and possible
instances detected at reduced moduli, the randomized estimator agreeing with exact
enumeration to 0.2%, embeddedness detection in both directions, and the baseline guard.
The full run reproduces P1's packing counts, P2's drift sweep, P3's residual curve and
P4's embeddedness tables. Failures carry prefix `XD-MBYG04K-URS3LF`.
