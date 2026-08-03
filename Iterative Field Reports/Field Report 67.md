# Field Report 67 — THE CEILING IS UNIFORM: FR54's SAMPLING EXPLANATION TESTED AND UPHELD

*Instrument: `eyeceil` (corpus-only). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — an explanation carried unexamined for thirteen cycles

FR54 established that the 27 undetermined glyphs are systematically rarer (mean
9.93 vs 13.71, z = +4.32) and concluded the 74.1% ceiling is *"largely a **sampling**
limit, not structural"* — rare glyphs co-occur less often inside certified isomorph
windows, so they enter components less often.

That explanation is entirely about glyph **frequency**. It never asked about glyph
**position**, and there is a specific reason to. FR45 established that the message
openings are **stamped literal headers** rather than encrypted body. If undetermined
glyphs concentrate there, the ceiling has a structural component FR54 missed, and —
more usefully — the *encrypted body* would be better covered than the 74.1% headline
implies.

Thirteen cycles have quoted the ceiling. None tested this.

---

## 1. Result — the ceiling is uniform

```
opening (pos 0-23)   216 positions,  155 determined = 71.8%
body    (pos 24+)    820 positions,  613 determined = 74.8%
whole corpus        1036 positions,  768 determined = 74.1%   [FR54 headline]
```

Three percentage points apart. Undetermined-glyph enrichment in the openings:
**z = +0.80**. Nothing there.

**My hypothesis is refuted, and the refutation is worth more than the hypothesis
would have been.** The ceiling is not concentrated anywhere — not in the headers,
not in the body. It is a genuinely global sampling limit, exactly as FR54 said.

The practical consequence is a negative one and should be stated plainly: **there is
no better-covered region of the corpus to attack.** Any strategy hoping to exploit a
locally denser patch of determined glyphs has nothing to work with.

---

## 2. A weak signal, pre-registered and not promoted

Controlling for frequency — comparing determined and undetermined glyphs *within*
narrow frequency bands — the undetermined ones do sit slightly more in the openings.
Pre-registered threshold: real positional component iff P < 0.01, noting that one
band was chosen.

```
band 8-14 : observed gap +0.0918
            null over 20,000 random 18/30 splits: μ −0.0001, sd 0.0531
            z = +1.73,  one-sided P = 0.0442      → FAILS the threshold
```

Robustness across bands:

| frequency band | glyphs | undetermined | gap | P |
|---|---:|---:|---:|---:|
| 5–9 | 22 | 12 | +0.045 | 0.245 |
| 8–14 | 48 | 18 | +0.092 | 0.045 |
| 10–17 | 47 | 15 | +0.123 | 0.021 |
| 12–20 | 35 | 7 | +0.165 | 0.028 |

All four positive, three of four below P = 0.05, **none below the pre-registered
0.01**. And the bands overlap heavily — 8–14, 10–17 and 12–20 share most of their
glyphs — so this is **not** four independent confirmations; it is closer to one
measurement viewed four ways.

**Classified watch-grade and not promoted.** The threshold was registered before the
bands were run and it is honoured as written. FR55 §3 and FR49 both record what
happens when a threshold is adjusted after seeing the number.

**FR54's sampling explanation stands.**

---

## 3. What this cycle is worth

It is confirmatory, and I will not dress that up. Its value is that a load-bearing
explanation — quoted in every acquisition discussion since FR54 — had never been
tested against the one alternative that FR45 makes plausible. It now has been, and
it survives.

The by-product matters more than the main result: **uniform coverage means the
ceiling cannot be attacked by targeting a region.** Combined with FR63's enumeration
and FR64's anchor arithmetic, the acquisition specification is unchanged and there
is no shortcut hiding in the positional structure.

---

## 4. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%, now known to be **uniformly distributed** across
openings and body; repair A the unique maximal reading; drift unpinned; consistent
alphabet set exactly 22,550 (FR63); first anchor spent on gauge (FR64); deliverable
exhibited (FR66).

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| FR54's "sampling limit" reading of the ceiling | asserted from frequency alone | **TESTED against a positional alternative and UPHELD** |
| Coverage distribution | unmeasured | **UNIFORM** — 71.8% openings, 74.8% body |
| Frequency-matched positional gap | — | **watch-grade**, P = 0.021–0.245 across overlapping bands, fails pre-registered 0.01 |
| "Attack a better-covered region" | never proposed, never excluded | **excluded** — no such region exists |

---

## 6. Horizon — and a recommendation

Unchanged, and I want to be straight about the state of it. Items 2–4 below have
been on the horizon for several cycles without moving, because none of them can be
advanced from inside the ciphertext:

1. **Decide the success criterion** by inspecting FR66 §1 — 635 values, 462 of them
   unique, sitting on the alphabet-83 line. Not a task; a judgement.
2. **Five real anchors, one per component** (FR64) — 22,550 → 1.
3. **MSB state count** on the glyph pictures (FR59) — cheapest external test.
4. **The radix** (`GHIDRA.md`) and **the EyeStat filter port** (FR61/FR62).

**My recommendation, offered as a view.** This cycle tested a real question and
returned a clean negative, which is legitimate work. But it is the second
consecutive cycle whose main output is confirmation of an existing claim, and the
questions I can still pose from inside the corpus are getting smaller each time.
The marginal value of cycle 68 is, on present evidence, lower than the marginal
value of item 1 — which requires no cycle at all.
