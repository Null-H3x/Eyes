# Field Report 191 — FR180 UNBLOCKED AND CLOSED: `C` IS NOT A KEYWORD ALPHABET UNDER ANY PLAUSIBLE ORDERING

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The block, removed

FR180 identified the keyword-alphabet test as **the only route that could pin
the drift from internal evidence**, and left it blocked: the test needs the
trigram-to-value table, which the corpus does not carry (values arrive
pre-converted).

The community sources supply it. Both the Noita Wiki and the community
transcription state the mapping directly:

> *"Each trigram can be read as a three-digit base 5 number from 000 to 444."*
> *"Possible values from 000 to 312, or 83 unique results (out of a possible
> 125)."*

**The mapping is plain base-5**: a trigram `(d₁,d₂,d₃)` has value
`25d₁ + 5d₂ + d₃`, and only `000..312` — that is, `0..82` — occur. So glyph
value `v` decomposes as `(v//25, (v//5)%5, v%5)` with no extra data needed.

The transcription also confirms the engine detail independently: *"The '5'
character creates a new line of eyes and is not actually displayed otherwise"* —
matching the base-7 decompilation exactly (0 = padding, 1–5 = eyes, 6 = newline).

---

## 1. And the test runs without a rebuild

Relabelling glyphs only **permutes the `q` table** — it does not change the
model. So all 720 candidate orderings (6 digit-significance orders × 120 digit
relabellings) can be evaluated against a single solve.

**A keyword alphabet's signature**: consecutive indices in the ordered tail share
one `q`-difference, and that difference is the drift.

```
orderings evaluated : 720
best result         : 2 of 6 adjacent pairs share difference 55
expected by chance  : 0.07
```

> **No ordering produces a keyword signature. `C` is not a keyword-derived
> alphabet under any of the 720 plausible orderings.**

---

## 2. What this closes

FR180 framed the outcome in advance:

> *"If no ordering produces a tail, the keyword hypothesis is dead and with it
> the last structural shortcut the family offers. What remains is the
> literature's own fallback: cribs."*

**That is where it lands.** The Quagmire family's one structural constraint on
its mixed alphabet — that it is keyword-built rather than arbitrary — does not
hold here.

Petri combined two classical constructions (FR179) but did **not** use the
classical alphabet-building method with them. `C` is an arbitrary permutation, or
close to one.

**And with it dies the fifth and last drift-pinning route.** FR166 and FR167
retired four to FR30/36/53 and the invariant core; this one survived those and
has now failed on its own terms.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Trigram-to-value table | blocking FR180 | **recovered** — plain base-5, `25d₁+5d₂+d₃` |
| Keyword-alphabet test | blocked | **run over all 720 orderings** |
| `C` keyword-derived | negative in one indexing (FR180) | **negative in ALL plausible indexings** |
| Drift-pinning routes | four dead, one live | **all five dead** |
| Newline symbol | from decompilation | **independently confirmed** by the community transcription |

---

## 4. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, one reading, five fragments,
819 positions (79.1%), Quagmire II with a progressive key, `C` an arbitrary
permutation. Cumulative: 27.16 billion candidates, zero survivors.

---

## 5. Horizon

**Internal structure is now exhausted in a specific, checkable sense**: the
cipher family has been identified, its standard attack chain traced step by
step, and its one structural shortcut tested to destruction across every
plausible parameterisation.

What remains:

1. **Fragment 2's own analysis** — 222 positions across six messages, still
   never examined beyond its IC.
2. **Acquisition**, unchanged: 6 anchors as pairs within a component, 15 crib
   tokens, or the `q[36]`/`q[68]` pair.

The literature's verdict on this family (FR179) and this project's independent
conclusion now agree exactly: **cribs are the only route.**
