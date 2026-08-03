# Field Report 17 — Offsets Are Not the Bottleneck

**Series note.** Seventeenth report of the iterative series. FR16's horizon asked
whether certification can finally grow from the first coherent configuration. It
cannot — and the third consecutive flat result of this kind is diagnostic rather than
disappointing. The cycle turns that diagnosis into the first operational target list
for the doctrine's R6 external-anchor programme. Instrument `eyeanchor.py`, selftest
5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Two constraints available since FR14 have never been
imposed: the offset equalities that literal body runs *force* — E1/W1 (a run of length
13, chance ≈ 5 × 10⁻²⁵) and E4/E5 (three runs of length 3). Unlike FR15's removal test
these add information, so the question is well-posed. **The answer is flat:**
certification stays at exactly 10 certified symbols — the same ten glyphs — with one
merge, both, or neither, in FR16's coherent per-triplet-drift model. Together with
FR11's reading comparison and FR16's bridge removal, that is three consecutive
certification-growth tests returning nothing, and all three manipulated **offset**
information. The diagnosis follows FR8: certified differences collapse onto the
absolute-pin domain, so what limits growth is symbol linking under gauge invariance,
and offsets never touch it. External anchors, by contrast, act on symbols. A single
anchor still does not grow the gauge-invariant domain, but it does **determine**
symbols, which is the operationally relevant quantity — and the leverage is extremely
uneven: **one well-placed anchor determines 21 of the 51 reachable glyphs while a badly
placed one determines 1.** A greedy selection reaches **all 51 with just 8 anchors**,
where random placement needs about 30. Placement dominates count, and the ordered
target list is now concrete: **5, 4, 16, 25, 9, 14, 12, 39.**

---

## 1. Corrections first

**I nearly published a test that did not test what its prose claimed.** The
certification comparison was initially run with the repo's fixed global drift, under
which the E4/E5 merge simply contradicts — reproducing FR9/FR16 rather than probing
FR16's coherent configuration, which requires per-triplet drifts. Caught before
publication; the instrument now reports **both** row models side by side, and the flat
conclusion is verified in the one that matters:

| configuration | global drift = 1 | per-triplet drifts (FR16 model) |
|---|---|---|
| reduced pool, no merges | 10 | 10 |
| reduced + E1/W1 merge | 10 | 10 |
| reduced + E4/E5 merge | CONTRADICTION | 10 |
| reduced + both merges | CONTRADICTION | 10 |
| full pool + both merges | CONTRADICTION | 10 |

Same ten glyphs throughout: {4, 12, 13, 19, 23, 37, 44, 46, 49, 72}.

**A measurement I had to discard.** Pinning two glyphs and recounting the certified
domain returned zero every time — an artifact, not a result: `certified_domain` shifts
a reference that the pins have already fixed, so the gauge test degenerates. Replaced
with a direct determination test (is a symbol's value forced?), which is what the R6
question actually needs.

## 2. The diagnosis

Three cycles, three flat results, one common factor:

- FR11 — compare certification under two keystream readings: same 10 symbols.
- FR16 — remove the weak cross-triplet bridge: pin set byte-identical.
- FR17 — impose both run-forced offset equalities: same 10 symbols.

Each manipulated offsets or bases. FR8 proved the certified-difference set equals the
absolute-pin domain exactly, with every non-pin symbol moving under a gauge shift. The
corollary, now confirmed from three independent directions, is that **offset
information is orthogonal to certification.** No rearrangement of which messages share
an offset will ever grow the pin inventory. That closes off a family of experiments the
series has been repeatedly drawn to, and it sharpens where effort belongs.

## 3. The R6 leverage curve

External anchors act on symbols, so they are the one lever FR8 left standing. Measuring
determination — how many of the 51 glyphs the constraint pool touches become forced —
under k randomly placed anchors:

| anchors | determined (mean) | best | worst |
|---|---|---|---|
| 0 | 0.0 | 0 | 0 |
| 1 | 9.8 | 21 | 2 |
| 2 | 16.2 | 24 | 6 |
| 3 | 25.2 | 37 | 11 |
| 5 | 31.2 | 43 | 24 |
| 8 | 36.8 | 48 | 24 |
| 12 | 43.2 | 49 | 31 |
| 16 | 46.2 | **51** | 40 |
| 25 | 48.8 | 51 | 42 |
| 30 | 49.9 | 51 | 47 |

The spread at every k is the story. A single anchor is worth 21 symbols or 2 depending
only on which component it lands in.

## 4. The target list

Per-glyph leverage splits sharply: a large tier of glyphs (81, 74, 71, 68, 64, 62, 57,
50, 48, 47, …) each determine **21** on their own, while 12, 58, 14, 32, 39 and 54
determine 1 or 2. Choosing anchors greedily rather than randomly:

| anchors | set | determined |
|---|---|---|
| 1 | 5 | 21 / 51 |
| 2 | 5, 4 | 30 |
| 3 | 5, 4, 16 | 37 |
| 4 | 5, 4, 16, 25 | 41 |
| 5 | 5, 4, 16, 25, 9 | 44 |
| 6 | +14 | 46 |
| 7 | +12 | 49 |
| **8** | **5, 4, 16, 25, 9, 14, 12, 39** | **51 / 51** |

Eight well-chosen external anchors determine every reachable glyph; random placement
needs roughly thirty for the same result. For a programme whose whole difficulty is
obtaining external pins at all, a factor of four in how many are needed is the
practical payoff of this cycle.

## 5. Caveats, stated plainly

- **"Determined" presumes the pins are correct.** This measures the constraint system's
  propagation power, not the truth of any anchor. A wrong pin propagates wrongness just
  as efficiently.
- **51 of 83 glyphs are reachable at all.** The remaining 32 never appear inside any
  pair span, so determining all 51 is not a full solve — it is full determination of
  the part the current evidence can speak to.
- **The ranking is relative to the current sound tier** and would move if the pool
  changes; it should be recomputed after any pool revision.

## 6. Horizon

(1) **Feed the target list to the external-anchor effort.** The ordered set in §4 is
what to seek first; if only one anchor is ever obtained, the high-leverage tier (21
symbols each) is where to spend it. (2) **Extend reachability.** Thirty-two glyphs lie
outside every pair span; finding any certified structure that touches them is worth
more than further work on the reachable 51. (3) **Audit #2⁻'s core** at instance level
as FR15 did for #M⁻'s bridge — the surviving cross-triplet link deserves the same
scrutiny. (4) Standing: anchor calibration at rep = 4, which has silently shaped every
pool in this series.

## 7. Reproduction

`eyeanchor.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — zero pins determine nothing, one pin determines a nonempty set,
monotonicity under added pins, pinning everything determines everything, and the
baseline guard. The full run reproduces C1's two-model certification table, C2's
leverage curve, C3's per-glyph ranking, C4's greedy set and C5's caveats. Failures carry
prefix `XD-MBYG04K-URS3LF`.
