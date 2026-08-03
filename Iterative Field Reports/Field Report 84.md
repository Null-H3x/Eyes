# Field Report 84 — THE HEADER IS NOT NATURAL-LANGUAGE TEXT, AND IT CORROBORATES THE INVENTORY

*Instrument: `eyehdr` (corpus-only, trie-based). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — a test FR45 said did not exist

A4, the stamped-header reading, is the project's weakest load-bearing assumption:
adopted in FR29 to remove a contradiction, used in FR33 to force T1 and FR44 to retire
H1, and FR45 concluded *"the requested test does not exist in the form asked."*

FR45 tested **repeat rates** within 24-glyph opening blocks and found openings and body
comparable. There is a test it did not try: if the headers are **literal text over a
plaintext alphabet**, they should use **few distinct glyphs**; if encrypted, many. That
is directly countable.

---

## 1. SELF-CORRECTION — I flagged the error and then committed it

The first measure pooled the seven distinct header blocks and returned an effective
alphabet of **42.0** against the body's 80.4 — a factor of two, and apparently the
strongest evidence for A4 ever obtained.

**It is entirely a pooling artifact.** The seven blocks share prefixes: positions 1–2
are universal, positions 3–5 shared within branches. Pooling counts the universal
symbols seven times over. I wrote that caveat into my own output and then computed the
pooled figure anyway.

Fourth occurrence of the pooling error in this project's history (FR39, FR45, FR48,
FR84), and the first where the analyst had the warning in front of him.

**The correct object is the trie.** Each stamped symbol is counted once, at the edge
where it occurs — 100 symbols across the whole header structure.

---

## 2. Result

```
header trie   : 100 stamped symbols, 57 distinct, IoC 0.01374, eff. alphabet 72.8
body          : 820 symbols,         83 distinct, IoC 0.01243, eff. alphabet 80.4
```

Against nulls at n = 100:

| source | expected distinct | expected eff. alphabet |
|---|---:|---:|
| literal over 26 | 25.5 ± 0.7 | 25.9 |
| literal over 29 | 28.1 ± 0.9 | 29.0 |
| literal over 40 | 36.9 ± 1.5 | 40.1 |
| literal over 60 | 48.9 ± 2.3 | 60.2 |
| encrypted, 83 | 58.3 ± 2.9 | 82.8 |
| **observed** | **57** | **72.8** |

**vs the encrypted null: z = −0.46 on distinct count, +1.09 on coincidences.**
Indistinguishable.

**FR45's verdict stands** — this test does not discriminate encrypted from stamped
either. But it now has a bound where FR45 had none.

---

## 3. What IS excluded

A literal header over any natural alphabet is **decisively excluded**:

- 26 symbols would give 25.5 distinct; observed 57
- 29 symbols would give 28.1 distinct; observed 57
- 40 symbols would give 36.9 distinct; observed 57
- 60 symbols would give 48.9 distinct; observed 57, **z = +3.5**

> **The header is not literal natural-language text.** If it is literal at all, it is
> literal over a symbol set of **at least 60**, and most consistently around 73–83.

---

## 4. THE CORROBORATION — and why it matters

This is the part worth keeping. **If A4 holds and the header is literal, then its
inventory is a model-free estimate of the plaintext alphabet size.**

Every previous inventory estimate — FR39's 88.7, FR57's 84.6, FR80's 82.1, FR82's 82.5
— came through the v-channel, which depends on the skeleton, the drift, the component
bases, and (as FR79 showed) the sign convention. The header estimate depends on **none
of that**. It is a direct count of stamped symbols.

```
body, via v-channel (model-dependent)  : 82.5   CI [73.0, 93.7]
header, direct count (model-free)      : 72.8
```

Both large, and consistent within the noise at n = 100. **Two estimates with no shared
failure modes agree that the plaintext alphabet is far larger than any natural
language.**

That is the strongest corroboration the inventory figure has received, and it arrives
from the one part of the corpus that bypasses the entire cipher model. Given that
FR81 and FR82 make the inventory the most consequential number in the project, an
independent check on it was worth more than a resolution of A4 would have been.

**The conditionality cuts both ways**, and honestly: if A4 is false and the headers are
encrypted, this is just a second measurement of encrypted material and says nothing
about the plaintext. The corroboration is exactly as strong as A4 is.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7] via v-channel, **72.8 via header trie (model-free,
conditional on A4)**; determinacy threshold 81.2, unresolvable by 51×.

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| A4 testability | "no test exists" (FR45) | **test exists, does not discriminate**, but yields a bound |
| Header as literal natural language | untested | **EXCLUDED** — 26/29/40 give 25–37 distinct, observed 57 |
| Header symbol set | unknown | **≥ 60**, most consistent with 73–83 |
| Inventory corroboration | v-channel only, four estimates sharing failure modes | **model-free header estimate 72.8**, no shared failure modes |
| Pooling error | three prior occurrences | **fourth**, first with the warning already written down |

---

## 7. Horizon

1. **The header ordinal test** (FR83 horizon 1), still unrun. §2 gives the symbol
   inventory but not whether branch values encode an index.
2. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff.
3. **The success criterion** (FR82 §7): *"is it worth acquiring external evidence to
   find out?"* — now with one more reason to think the inventory figure is right, and
   therefore that the corpus sits at or above its determinacy threshold.
