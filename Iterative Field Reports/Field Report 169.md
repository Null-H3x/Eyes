# Field Report 169 — `eyeverify.py`: THE ARTIFACT AN OUTSIDE SOLVER ACTUALLY NEEDS

*Instrument: `eyeverify.py` (4/4 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I — what is still missing

Three verifiers exist and none answers the question an external contributor
actually has:

```
eyecrib.py   repair-A based; REJECTS glyph 36 outright
eyepair.py   tests only the q[36]/q[68] pair
eyemodel.py  rebuilds the model rather than testing a guess
```

What someone outside has is **a candidate alphabet, whole or partial**, and one
question: *is it refuted?*

The two invariant cores answer that **without requiring any choice this project
made** — 13 relations on community-certified evidence, 19 on the extended model.
Nothing packaged that.

---

## 1. What it does

Self-contained: no corpus, no model rebuild, stdlib only. Takes a partial or
complete alphabet and reports:

- how many core relations are **testable** given what was supplied
- which of the 82 drifts survive **both** cores (relations scale with `d`, FR30)
- whether the candidate is **refuted at every drift**
- what the two invariant homophones say about it
- if nothing is testable, **which glyphs to supply** to get a verdict

```
$ python3 eyeverify.py --alphabet "13:0,19:30,72:48,5:10,10:45"

  core        relations testable
  atlas               4 of 13
  extended            1 of 19
  drifts surviving BOTH cores: 1 of 82   [1]
  *** NOT REFUTED. ***

$ python3 eyeverify.py --alphabet "13:0,19:7,72:48,5:10,10:45"

  drifts surviving BOTH cores: 0 of 82
  *** REFUTED at every drift. ***
     q[13]-q[19]: core requires 53, candidate gives 76
     q[19]-q[72]: core requires 65, candidate gives 42
```

**Five glyph values are enough to refute a wrong candidate.**

---

## 2. Why this is the right end-state artifact

Everything else the project ships is **conditional**: on the repair choice, the
class selection, one of 68 readings, an unpinned drift. `eyeverify.py` is
conditional on none of it — a violation of either core kills a candidate
regardless.

It also **fails usefully**: given too few glyphs it names the 41 that would make
a verdict possible, rather than returning nothing.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Candidate-alphabet testing | three partial tools, none sufficient | **`eyeverify.py`**, self-contained, 4/4 gate |
| Minimum to refute a candidate | unstated | **as few as 5 glyph values** |
| `eyecrib.py`'s glyph-36 refusal | a known gap | **superseded** for candidate testing |

---

## 4. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, alphabet [56, 75], 79.1%
exposure, 435-position reading, 6 anchors, 68 maximal readings, two invariant
cores (13 atlas / 19 extended), stamped header forced. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 5. Horizon

**The project is now handed off rather than merely documented.** An outside
contributor needs three files and no context:

```
INVARIANT_CORE.md   what is known that no choice of mine affects
eyeverify.py        test a candidate against it in seconds
ACQUISITION_SPEC.md what evidence would finish it
```

Remaining work is external and unchanged: 6 anchors as pairs within one
component, 15 consecutive crib tokens, or the `q[36]`/`q[68]` pair — which
FR168 established is the better-supported of the two homophone tests.
