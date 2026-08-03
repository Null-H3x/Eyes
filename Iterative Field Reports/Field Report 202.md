# Field Report 202 — THE ATTACK TOOLKIT: THE HEADERS TURN OUT TO HOLD EVERY KEY, THE HUNTER GOES QUIET, AND THE WHOLE DETERMINABLE SOLUTION REDUCES TO FOUR PLAINTEXT VALUES AT STAMPED POSITIONS

*July 2026. Cycle: EYESPIRAL-C, building against the FR201 attack surface.
Instruments: `eyeheader.py` (gated 25/25) and `eyehunt.py` (gates green after
two control-forced redesigns). One vector claim from the previous synthesis
is retracted below; one structural finding supersedes it by a wide margin.*

---

## 0. Corrections and negatives first

**The 82-fingerprint idea is retracted — killed by FR36 in my own output.**
The proposed drift-filter (per-`d` header equality profiles for matching
qualitative lore) returned **one** partition across all 82 drifts, because
`d·Δcoef ≡ 0 ⟺ Δcoef ≡ 0`: header equality structure is drift-invariant,
like every other internal structure. Qualitative lore can *confirm* the
model; only a **quantitative** relation ("position a is position b plus k")
pins `d`, via `d = k·Δcoef⁻¹`. The shipped kit reflects the honest version:
a d-free structure sheet plus the relation→`d` lookup.

**Arithmetic erratum:** the previous synthesis said 111 header positions;
the true count is **132** (24×3 + 20×3). Of these, 96 sit on determined
giant glyphs, 5 on small-component glyphs (§2), 1 on comp-2's glyph 18, and
the rest on six dark glyphs.

**Two plants failed before one passed, and both failures were design
findings.** A byte-identical copy plant produces exact pairs whose rows
cancel to contradictions — degenerate, correctly rejected. The
system-derived synthetic pair then exposed a structural flaw: weak
(two-pair) templates admit chance co-members into every group, and the
group-as-unit rule rejects even a perfect planted pair inside a
contaminated group. Fix: **pair-level admission** — the atlas pool's own
architecture — priced against the full pair count by geometry-preserving
controls. Third gate-forced redesign of this session's instruments; the
controls are doing exactly what they were built for.

## 1. `eyeheader` — the turnkey, shipped and gated

`header_attack_kit.json` contains the complete header map (132 positions,
identity verified across each triplet), drift-1 `q`-relatives for every
determined header glyph, the base vector, and:

- **Six d-ladders** — repeated glyphs within one header whose two offsets
  make a single glyph's *meaning* pin the drift outright:
  `p[12]−p[1] = −11d` (glyph 66), `−17d` (13), `−14d` (29), `−9d` (62) in
  T1; `−4d` (2), `−17d` (5) in T3.
- **The two-value solver**, gated on 25 planted `(d, Q0)` round-trips,
  exact: any two known header plaintexts on giant glyphs → `(d, Q0)` →
  771 positions plus both headers decoded.
- **The d-free structure sheet**: the 96 giant-determined header positions
  collapse into **49 plaintext classes** — the headers' internal repetition
  structure, on record and externally checkable against any future lore.

## 2. The structural finding: the small components live in the headers

Component membership against the header map:

| component | glyphs | where they sit |
|---|---|---|
| giant (57) | … | 26 distinct header glyphs, 96 positions, all 5 determined indicators |
| comp-1 (4) | 14, 32, 55, 59 | **T1 header offsets 15, 14; T3 header offsets 11, 14** |
| comp-2 (2) | 18, 80 | **T3 header offset 15; West 1's indicator (position 0)** |

Every small-component glyph except the W1 indicator is a stamped-header
glyph at a known offset. Consequence — the ask table collapses:

```
value at any TWO giant header positions          -> d + Q0      -> 771 positions
value at T1:14, T1:15, T3:11, or T3:14 (any one) -> A_comp1     -> + 48
value at T3:15 (or W1's indicator)               -> A_comp2     -> + 29
------------------------------------------------------------------------
FOUR plaintext values, all at stamped-header /   -> 848 positions, C on 63
indicator positions, three inside the headers       glyphs: everything the
themselves                                          corpus can determine
```

And one of the two giant values is substitutable by a *single* repeated
glyph's meaning (the d-ladders). "What do the openings say" is no longer a
flavor question adjacent to the puzzle. **It is the puzzle.** The headers —
44 designer-written, launch-visible, community-discussed positions — contain
the keys to every fragment of the solution.

## 3. `eyehunt` — the compounding scanner, gated green, and the vein goes quiet

Architecture after the redesigns: stratum A = full-skeleton groups at
L 60–137 (beyond FR201's ceiling); stratum B = pair-level, target-anchored
(anchors containing a small-component or dark glyph at a template letter,
partners sharing the full ≥2-pair template), admission at implied_new ≥ 4,
0 contradictions, novel ≥ 1. Gates: geometry-preserving control **0/58**;
the synthetic system-derived plant **generated and admitted (2 pairs)**.

The run: **stratum A, 0 admitted. Stratum B, 58 real pairs: 18 known, 32
redundant, 8 weak, 0 contradictions — 0 admitted.** The FR201 vein is mined
out at this generator family. Honestly unswept: longer stratum-B windows,
≥3-pair templates outside the anchor set, cross-header T1↔T3 alignments,
exact-repeat strata — all with low expected value now that the targeted
stratum has nulled cleanly. Zero contradictions among 58 target-anchored
pairs is itself a small model confirmation.

## 4. Doctrine changes

| item | prior | now |
|---|---|---|
| minimal complete ask | 4 pins: 2 indicators + 2 anchors | **4 plaintext values at stamped positions** (three in-header); 2 giant-header values alone → 74.4% |
| drift from qualitative lore | proposed (previous synthesis) | **retracted** — FR36 holds; quantitative relations only |
| header structure | uncharacterized | 49 p-classes over 96 positions, d-free, shipped |
| internal compounding vector | open, expected to compound | **paid once (FR201), nulled at the targeted family**; residual generators enumerated, low priority |
| verification surface | 1603 relations + cores | + header structure sheet as an external-lore consistency check |

## 5. Artifacts and horizon

Shipped: `eyeheader.py`, `header_attack_kit.json`, `eyehunt.py`.

1. **Publication v2.2 leads with the header ask** — four stamped positions,
   three of them in the openings everyone has stared at since launch, and a
   d-ladder shortcut through any one repeated glyph's meaning.
2. A2-full live-span fuzz and the 121-candidate characterization remain the
   protective queue; Threadripper corroboration of sha `7b4132e8…` optional.
3. The internal game rests unless a new generator family earns a prior. The
   external game now has the sharpest possible shape: not "solve our
   cipher," but *"tell us what five specific stamped positions mean, and the
   machine does the rest."*
