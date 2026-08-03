# Field Report 148 — WEST 3 IS THE DARK MESSAGE, AND IT SITS ON A 148-POSITION ISLAND

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Correction to FR147

FR147's horizon said *"West 2 is still dark — the one message absent from the
435-position reading."* **Wrong.** The reading covers:

```
East 1, East 2, East 3, East 4, East 5, West 1, West 2, West 4
absent: WEST 3
```

West 2 is present. I read the message list carelessly and named the wrong
message in a shipped horizon item.

---

## 1. Why West 3 will not link

It is not a coverage problem: **95 of West 3's 124 positions (77%) hold a
determined glyph.** The blocks simply do not connect to the main group.

```
linking edges touching West 3 : 8
West 3 alignments in the pool + extension : 2
     West 2@18 x West 3@23  L=14
     East 3@24 x West 3@23  L=14
```

**Two alignments, both at the same West 3 offset (@23), both length 14.** Every
linking edge West 3 has comes from a single 14-glyph window.

Its blocks scatter across five groups:

```
West 3 block-groups : 2 (18 pos), 4 (2), 5 (56), 12 (148), 22 (5)
main group          : 435 positions
```

> **West 3's largest fragment is a 148-position island** — bigger than repair
> A's entire reading was — sitting adjacent to the main group with no edge
> joining them.

---

## 2. The nine non-atlas West 3 classes do not help

All nine leave the model at 794 relations / 61 glyphs / 8 equalities: they are
**redundant**, so they add no relations and therefore no new cross-block edges.
Being consistent is not the same as being informative, which is the FR38
distinction seen from the linking side rather than the relation side.

---

## 3. What this means for acquisition

The six-anchor programme (FR147) determines the **glyph alphabet**, and that is
unaffected — West 3's glyphs are 77% determined already.

What West 3 lacks is a **block offset**, which is a different unknown. Its
148-position island needs exactly one relation tying it to the main group:
either a genuine shared passage nobody has found, or one external anchor
landing inside it.

**That makes West 3 a seventh anchor with an unusually large yield** — one pin
inside the 148-position island would fold it into the reading, taking coverage
from 435 to roughly 583 positions (42% → 56%).

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| The dark message | "West 2" (FR147) | **WEST 3** — West 2 is in the reading |
| Why it is dark | assumed coverage | **linking** — 77% of its glyphs are determined |
| West 3's evidence | unexamined | **2 alignments, both at offset 23, both L=14** |
| West 3 non-atlas classes | candidate bridges | **all 9 redundant** — consistent but uninformative |
| West 3 fragment | — | **148-position island**, adjacent and unjoined |
| Acquisition | 6 anchors → 79.1% exposure | **+1 anchor inside West 3's island → reading 435 → ~583** |

---

## 5. Model status

Extended skeleton unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1%
exposure, 435-position reading across 8 of 9 messages, 0 conflicts, drift-stable.
Acquisition 6 anchors, or 7 to include West 3. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon

1. **Search specifically for a West 3 bridge.** Its two alignments both sit at
   offset 23; a passage elsewhere in the message would be a different kind of
   evidence. The class enumeration used `k ≥ 2`; West 3 may have weaker but
   genuine structure below that threshold, and a targeted search can afford a
   lower bar than a corpus-wide one.
2. **Rebuild the shipped artifacts** on the extended skeleton — still pending,
   and now with a corrected message list.
3. **The 48 contradictory non-atlas classes remain unexamined.**
