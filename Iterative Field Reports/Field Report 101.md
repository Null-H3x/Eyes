# Field Report 101 — THE ASSETS ARE IN HAND AND THEY WITHHELD NOTHING; THE SUCCESS CRITERION IS SETTLED

*Sources: Noita launch build data (`WUOTE/noita-builds-data`), the raw base-5*
*orientation stream (`Null-H3x/Eyes`), the community wiki. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The expected payoff did not materialise

Since FR97 the standing line has been that **the glyph images are the sole
blocking resource** — three open vectors (MSB counting, MDL segmentation,
FR97's encounter-order construction family) all waited on them, and FR99 and
FR100 each closed by pointing at them as the lever.

The assets have now been acquired and analysed. **All three vectors resolve,
and all three resolve negatively.** The images contain exactly what the
community transcription already captured and nothing besides. This cycle
therefore reports an acquisition that *closes* rather than opens — the inverse
of what the last four reports anticipated, and worth stating plainly before
anything else.

---

## 1. The assets

`biome_impl/caves/eye_01.png` … `eye_05.png`, plus a template `eye.png`.
**Byte-identical across builds** (verified on two build IDs), so stable since
launch.

Each sprite is **9 × 5 pixels, greyscale (R = G = B at every pixel)**. The
entire information content is **one pixel**: a unique luminance-211 pupil whose
position within a fixed shell selects the state.

| sprite | pupil offset from centre (2,4) | orientation |
|---|---|---|
| `eye_01` | (0, 0) | CENTER |
| `eye_02` | (+1, 0) | DOWN |
| `eye_03` | (−1, 0) | UP |
| `eye_04` | (0, −1) | LEFT |
| `eye_05` | (0, +1) | RIGHT |

The shell is asymmetric and rotates with the pupil: `eye_02 = rot180(eye_03)`
and `eye_04 = rot180(eye_05)` **exactly**, and the family's pixel-variation map
is perfectly 180°-rotationally symmetric. `eye.png` differs from `eye_01` at a
single pixel (2,3) and reads as the base template.

---

## 2. What the assets close

**V2 — most-significant-feature count: RESOLVED as base 5.** The vector asked
for a state count on the glyph inventory, base 5 predicting four MSB states and
base 7 predicting two. The question is answered more directly than the test
anticipated: **there are exactly five eye sprites in the game data**, so each
eye carries five states and a trigram is base-5 by construction. A base-7
reading would require seven orientations; seven do not exist. No inference from
the 0–82 range is needed.

**The hidden-rendering-channel family: dead.** Every pixel is greyscale, so
there is no colour channel. Only one pixel varies informatively. There is no
tail encoding, no sub-pixel state, no per-instance variation. **The 1,036
trigram values are the complete information content of the artifact** — nothing
was discarded in transcription.

**MDL segmentation: moot.** The glyphs are atomic five-state symbols with no
internal structure to segment differently. Combined with the community's
reading-order search, there is no alternative parse to weigh.

**FR97's encounter-order construction family: loses its asset.** That
hypothesis — `C` built by `VectorAddUnique`-style encounter-order dedup of a
raster-scanned image — requires an **83-element** asset to scan. What exists is
*five* 9 × 5 sprites. The 83 values are a derived combinatorial object (5³
trigrams minus the unused 42), not a stored atlas. **There is no glyph atlas in
the data tree**, so this construction family has nothing to operate on. It was
the last construction hypothesis FR99 could not close; it is now closed for
want of an input rather than by sweep.

---

## 3. The parse is canonical — verified, not assumed

The raw orientation stream was checked against the corpus. Stripping headers
leaves **3,108 orientation digits = 1,036 trigrams × 3**, with per-digit counts
matching the corpus decomposition exactly:

```
raw   : 0:774  1:739  2:699  3:490  4:406   (+86 row terminators)
corpus: 0:774  1:739  2:699  3:490  4:406
```

The chain orientations → trigrams → 0–82 → `corpus.json` is verified end to
end.

**The orientation→digit assignment is forced.** Testing all 120 relabelings
σ of the five digits and recomputing `v' = 25σ(a) + 5σ(b) + σ(c)`, exactly
**two of 120** yield an unbroken value range:

| σ | range | note |
|---|---|---|
| (0,1,2,3,4) | 0–82 | the accepted form |
| (4,3,2,1,0) | 42–124 | the complement, `v → 124 − v` |

The two are related by a bijective relabeling, to which every instrument in this
programme is invariant (standing doctrine). They are therefore not competing
hypotheses: **the corpus labeling is unique up to a change that changes
nothing.**

**Self-correction on novelty.** This is almost certainly a *rediscovery*. The
community's published reading-order search (~86,000 possibilities) plausibly
covers this space, and the wiki records that only one of 36 standard reading
orders produces the unbroken range. The result is logged as **independent
confirmation from a different angle** — digit relabeling with reading order
held fixed — not as a finding. It does settle one thing conclusively: the
`eye_01…05` asset numbering cannot supply an *alternative* digit assignment,
because no alternative exists.

One micro-question remains unresolved and is recorded as such: which
orientation the accepted convention calls digit 0. The wiki's reference image
was not retrievable from the analysis environment. **It has no cryptanalytic
consequence** — the assignment is forced regardless of which orientation
carries which label.

---

## 4. THE SUCCESS CRITERION IS SETTLED

FR82 §7 posed it, FR39 sharpened it, FR40 stated three defensible positions,
and every report since FR42 has carried it as *the most consequential open
item* — the one question the corpus could neither compute nor close. It has now
been answered by the principal:

> **The goal is to solve the eye puzzle by solving for unknown variables and
> pinning the exact cipher mechanism down.**

This is position (a) of FR40's three: **recovering the cipher — its mechanism
and its parameters — IS the solution. The inner layer is a separate problem.**

The consequences are immediate and clarifying:

- **Readability is out of scope.** FR36/FR39/FR40's exclusion of a small or
  structured plaintext inventory, and FR100's closure of the coordinate
  grammar, cease to be discouraging results. They bear on the *inner* layer,
  which the criterion places outside the objective.
- **The token-stream objection dissolves.** "Recovering `C` yields 768 values
  over an inventory exceeding 60, not a reading" has been the standing caveat
  on the entire acquisition programme since FR39. Under this criterion that
  output **is** the deliverable, not a disappointment.
- **The programme has a definite terminus**, and it is reachable: a pinned
  mechanism plus (drift, bases, `C` over the determined backbone).

**The dominant open question of the last sixty reports is closed.** Not by
measurement — by decision, which is the only way a criterion question can be
closed.

---

## 5. What the criterion implies for the horizon

Restating the objective in the model's own terms. The cipher as currently
modelled:

```
q[c[t]]  =  p[t] + base_m + K_g[t]                    (mod 83)
q[s]     =  base_C + drift · Δ_s        within a component
K_g[t]   =  drift · t + κ_g             (progressive, linear in position)
```

**Two sub-goals, with different costs:**

**(A) Solve the unknown variables.** drift (1 of 82), the 35 per-(message,
component) bases, and `C` over the 56-glyph backbone. This is the acquisition
programme and it is entirely external: two anchors in component 1 fix drift and
base together (the second supplies a pair-difference, bijective in the drift),
delivering 25 glyphs and 31.2% of the corpus; then one anchor per remaining
component to 56 glyphs and 74.1%. FR54's priority ordering stands — the first
two anchors are worth more than the next eight combined, and components are not
interchangeable with singletons.

**(B) Pin the exact mechanism.** This is *not* the same task, and it may be
substantially **internal**. The alphabet-side relation `q[s] = base_C +
drift·Δ_s` is derived (FR26, FR30). The keystream-side claim — that `K_g[t]`
advances **linearly** in position with slope equal to the same drift — is the
load-bearing structural statement of the whole model, and this programme has
never audited whether it is *derived* or *assumed*. That audit needs no
anchors.

If the linear advance is proven, the mechanism is pinned up to a single scalar
and sub-goal (B) is complete today, leaving (A) as the entire remaining
programme. If it is assumed, testing it is real internal work directly serving
the stated objective — and it would be the first internally-executable item the
horizon has carried since FR97.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Success criterion (FR82 §7)** | the dominant open question since FR40 | **SETTLED: pin the mechanism and solve the variables; the inner layer is out of scope** |
| Glyph images | the sole blocking resource | **acquired**; contain nothing beyond the transcription |
| V2 MSB base-5 vs base-7 | open, needed images | **resolved: base 5** — five sprites exist, seven do not |
| Hidden rendering channel | untested | **closed** — greyscale throughout, one informative pixel |
| MDL segmentation | open, needed images | **moot** — glyphs are atomic five-state symbols |
| FR97 encounter-order family | live, needed assets | **closed** — no 83-element asset exists in the data tree |
| Orientation→digit assignment | unexamined degree of freedom | **forced**: 2 of 120 relabelings, related by a null relabeling |
| Corpus transcription | trusted | **verified** — 3,108 digits, exact per-digit match |
| Artifact information content | unknown whether complete | **the 1,036 values are complete**; nothing hidden in rendering |
| Keystream linearity | used throughout | **flagged as unaudited** — derived or assumed is now the live question |

---

## 7. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean; exposure 74.1%;
alphabet [56, 83] with floor 56 (FR97); drift unpinned. **Cumulative: 27.16
billion candidates, zero survivors (FR99).** No sweep run this cycle and none
owed.

---

## 8. Horizon

1. **Audit the keystream-linearity claim.** Is `K_g[t] = drift·t + κ_g`
   *derived* from the isomorph constraints, or *assumed* and merely consistent?
   This directly serves the stated objective, needs no external evidence, and
   is the first internally-executable item since FR97. If derived, sub-goal (B)
   is already complete and the programme reduces to acquisition.
2. **The anchor programme, by FR54's ordering.** Two anchors in component 1
   first — they fix drift and base together and deliver 31.2% of the corpus.
   Then one per remaining component. This is sub-goal (A) in full.
3. **The success criterion is closed.** It should not reappear on a horizon
   again. Reports from here measure progress against a fixed target.
