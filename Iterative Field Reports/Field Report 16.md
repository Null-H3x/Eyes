# Field Report 16 — Neither Branch Alone; Both Together

**Series note.** Sixteenth report of the iterative series. FR15 proposed that the
#M⁻ bridging window East 3 @ 101 is a coincidence-grade match and that discarding it
resolves the body-internal contradiction. This cycle adopts that provisionally,
measures what it actually buys, corrects the conditions under which FR15's claim
holds, and lands on the first configuration in seven cycles that is consistent without
flattening the keystream. Instrument `eyecohere.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Two corrections and one constructive result. First,
**FR15's claim is conditional on the drift scope**: under a *single global* drift,
removing the bridge changes nothing whatsoever — the gauge ladder, the base-equality
matrix, the opening contradiction, the body-internal contradiction and the certified
pin set all come out bit-identical. FR15's live verdict lives entirely in the
*per-triplet* drift reading. That is not a flaw in the result but it must be stated,
and the two readings are not independent: a single global drift is licensed only by
FR3's cross-triplet drift-equality deduction, which itself rests on the two bridge
windows — one of which FR15 priced at p ≈ 0.10. Discarding the weak bridge and letting
drifts vary per triplet are one package. Second, **that package is not sufficient on
its own**: the reduced pool plus the literal openings is still degenerate, so branch
(ii) alone does not rescue the opening contradiction, exactly as FR14 showed branch (i)
alone does not rescue the body-internal one. Third, and constructively: **together they
do.** With the openings excluded and E3@101 dropped, the pool carries the E4/E5 offset
equality that the literal body runs force, and comes out **LIVE with all three triplet
drifts still free** — the first configuration since FR9 that buys consistency without
surrendering determination. And it costs nothing certified: the pin inventory is
identical before and after.

---

## 1. Corrections first

**FR15 needs a scope qualifier.** I reported that dropping E3@101 turns the
body-internal system from degenerate to live. It does — under per-triplet drifts. Under
a single global drift the bridge is completely inert:

| test | full pool | reduced pool |
|---|---|---|
| 1 gauge (pure) | 0/82 drifts | 0/82 |
| 3 gauges (per-triplet offsets) | 0/82 | 0/82 |
| 9 gauges (per-message offsets) | 82/82 | 82/82 |
| pool + openings | 0/82 | 0/82 |
| pool + body-run merge | 0/82 | 0/82 |
| certified / pin-grade | 10 / 8 | **10 / 8, same pins** |

Every FR9–FR14 result is reproduced unchanged. What makes the removal bite is the
decoupling of T1's drift from T2/T3, which only matters if drifts are allowed to differ
per triplet — and that permission is exactly what discarding the #M⁻ bridge grants,
since FR3 derived drift(T1) = drift(T2) from that window. Mechanism and licence are the
same act, which is coherent, but it means the claim must always be stated as a package.

**A test I designed and had to discard.** FR15's horizon nominated re-running the pin
pipeline with E3@101 excluded to see whether certification grows. That is ill-posed:
removing constraints can only shrink or preserve a certified domain, so both hypotheses
predict the same direction. It joins FR14's opening-agreement item as a horizon
proposal that dissolved on inspection. The measured outcome — the pin set is
byte-identical with and without the bridge — confirms the test carries no information.

**The T3 gap does not require a keystream break.** FR14 flagged the two-position gap
between T3's proven-arithmetic ranges [35, 66) and [68, 98) as having two independent
reasons to be interesting. Testing whether the shift-+1 spans on either side can share
a single slope: they can. A continuous keystream carries both, so the gap needs no
cipher event — it reads as a local plaintext difference inside a near-duplicate pair
whose alignment (offset +1, an indel relative to the Δ=0 runs at 25/29/38) is unchanged
across it. The test is one-sided — separate slopes also fit, since they have more
freedom — so this removes the *motivation* for siting a reset at 66–68 without
excluding one.

## 2. The package, measured

Per-triplet drifts throughout; free drifts are the health measure.

| configuration | verdict | free drifts |
|---|---|---|
| full pool | LIVE | 3/3 |
| full pool + openings | DEGENERATE | 0/3 |
| full pool + body-run merge | DEGENERATE | 0/3 |
| full pool + openings + merge | DEGENERATE | 0/3 |
| reduced pool | LIVE | 3/3 |
| **reduced + openings** | **DEGENERATE** | 0/3 |
| **reduced + body-run merge** | **LIVE** | **3/3** |
| reduced + openings + merge | DEGENERATE | 0/3 |

The row that matters most is the sixth: **branch (ii) alone does not fix the opening
contradiction.** FR14 established the mirror fact for branch (i). Each of the two
smallest available fixes is insufficient by itself, and each is insufficient against
the half of the evidence the other addresses.

## 3. The coherent configuration

The seventh row is the constructive result. Take the atlas and strict pool, drop the
six pairs touching E3@101, exclude the literal openings from the constraint pool, and
add the offset equality that E4/E5's three literal body runs force. That system is
**LIVE with all three triplet drifts free** — meaning per-triplet progressive
keystreams survive intact, rather than being flattened into the piecewise-monoalphabetic
corner every previous escape landed in.

Stated as a model, the minimal coherent reading of this corpus is now:

- **the openings are not shared plaintext** under the body's cipher parameters —
  a structural prelude imposing no constraint (branch i);
- **E3@101 is a chance pattern match**, not a genuine #M⁻ instance (branch ii), so
  T1's drift is untied from T2/T3 while #2⁻'s genuine bridge keeps
  drift(T2) = drift(T3);
- **per-message offsets**, with E4 and E5 sharing one, as the literal body runs
  require;
- **all thirteen atlas classes real**, minus that single instance;
- **per-triplet progressive keystreams**, all three drifts live.

What it costs the doctrine: FR3's drift(T1) = drift(T2) link and its depth-stack
reading of the openings as plaintext; FR4's one-gauge deduction (already refuted
independently in FR9); and the opening stack as crib real estate. What it costs in
certified material: **nothing** — the pin inventory is unchanged at 10 certified, 8
pin-grade, same eight glyphs.

## 4. Where the trilemma stands

The three branches were never mutually exclusive, and the evidence now says the
resolution is a conjunction rather than a choice:

- **(i) + (ii) jointly sufficient** — the configuration above.
- **(iii′) still live but less motivated**: a single T3 reset remains admissible at
  102–103, while the 66–68 siting has lost its independent rationale (§1) and FR13
  showed such resets flatten most segment slopes.

Nothing here proves (i) or (ii); both remain the cheapest hypotheses that fit, and
E3@101's support is weak rather than absent (p ≈ 0.10, not p ≈ 0.001). But for the
first time the series has a complete, internally consistent reading of the corpus that
honours every piece of hard evidence — the atlas classes, the literal body runs, the
gauge theorem — without a degenerate keystream.

## 5. Horizon

(1) **Test the coherent configuration predictively.** Under it, the openings carry no
cipher constraint and E3@101 is noise; feed the reduced pool to the pin pipeline with
per-triplet drifts and see whether any new sound-grade relation appears once the
contradiction is gone — the first time in the series that certification has been
attempted from a non-degenerate configuration. (2) **Audit #2⁻'s core** at instance
level as FR15 did for #M⁻'s bridge, to check the surviving cross-triplet link is as
solid as its pattern weight suggests. (3) **Re-price FR3 and FR4** in the doctrine
under the reduced bridge set. (4) Standing: FR8's bridge-symbol search, anchor
calibration at rep = 4.

## 6. Reproduction

`eyecohere.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — bridge-removal arithmetic, the baseline, FR14 and FR15 reproduced,
and the drift-scope correction asserted directly. The full run reproduces C1's
global-drift comparison table, C2's eight-configuration package matrix, C3's reading and
C4's certification comparison. Failures carry prefix `XD-MBYG04K-URS3LF`.
