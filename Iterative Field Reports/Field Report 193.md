# Field Report 193 — THE FRAGMENTS ARE THE COMPONENTS, AND THAT MAKES THE ACQUISITION SPEC WRONG IN ONE PLACE

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Fragment 2, finally examined

```
frag comp  glyphs positions  msgs  runs>=4  in runs  longest
   1  [1]      37       491     9       20       97        8
   2  [2]      16       222     9        0        0        3
   3  [3]       4        48     9        0        0        2
   4  [5]       2        29     9        0        0        1
   5  [4]       2        29     9        0        0        1
```

**Fragment 2 shares zero glyphs with Fragment 1.** It is component 2 of the
skeleton, and every fragment is exactly one component.

That is structural, not incidental: `A_block = base_component − b_message`, so
blocks in different components have unrelated base values, and **no relation
crosses a component by definition** — components are the maximal connected sets
of the `q`-relation graph.

> **The fragments cannot be joined internally. Ever. Joining them requires one
> anchor per component — which is precisely FR147's 6-anchor programme, arrived
> at from the opposite direction.**

Two independent derivations of the same requirement is worth more than either
alone.

---

## 1. And Fragment 2 is unusable for reading

```
Fragment 2: 222 positions, 9 messages, longest contiguous run = 3
```

Its positions are **scattered singles and pairs** across all nine messages, with
no run of four anywhere. All 97 positions in runs of length ≥4 sit in Fragment 1.

So the 222 positions are real determinations but they do not form readable text
in any stretch. **Fragment 2's value is as an anchor target, not as a reading.**

---

## 2. The acquisition spec has an error

```
longest contiguous determined stretch anywhere : 8   (East 3, 105-112)
the acquisition spec's crib asks for           : 15
```

**No 15-position window is fully determined anywhere in the corpus.**

The spec asks for "15 consecutive plaintext tokens" as an alternative to
anchors. That is still valid as *external* evidence — a crib is supplied, not
verified — but the spec implied the crib could be checked against the reading,
and it cannot. **A 15-token crib would necessarily cover positions the model
does not read**, so it arrives unverifiable.

Corrected framing: **a crib of 8 tokens at East 3 positions 105–112 would be
fully checkable against the existing reading**, which makes it a far better ask
than 15 unverifiable ones — shorter, and self-validating.

---

## 3. The acquisition targets, re-ranked

| target | cost | yield | verifiable? |
|---|---|---|---|
| **one indicator value** (FR192) | 1 symbol | 5 linked plaintext values + pins the drift | yes |
| **8-token crib at East 3 105–112** | 8 symbols | pins component 1 outright | **yes — fully determined** |
| `q[36]`/`q[68]` pair | 2 symbols | tests the whole non-bijective family | yes |
| 6 anchors, one per component | 6 symbols | full solve | yes |
| 15-token crib | 15 symbols | full solve | **no — no such window is read** |

**The 15-token crib is the worst option on the list** and it has been the
headline ask since FR54.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| The 5 fragments | linked groups | **exactly the 5 components** |
| Joining fragments | "no internal route" (FR178) | **structurally impossible** — no relation crosses a component |
| 6-anchor requirement | from FR147's ordering | **independently re-derived** from fragment structure |
| Fragment 2 | 222 positions, unexamined | **16 glyphs, longest run 3** — anchor target, not a reading |
| 15-token crib | headline ask (FR54) | **unverifiable**; no 15-window is determined |
| Best crib | 15 tokens | **8 tokens at East 3 105–112**, fully checkable |

---

## 5. Model status

Unchanged: 794 relations, 61 glyphs, one reading, five fragments = five
components, 819 positions (79.1%). Cumulative: 27.16 billion candidates, zero
survivors.

---

## 6. Horizon

`ACQUISITION_SPEC.md` should be rewritten around the re-ranked targets. The two
that matter:

1. **One indicator value** — smallest possible ask, yields five plaintext
   positions and the drift.
2. **East 3, positions 105–112** — eight consecutive tokens, the longest
   fully-determined window in the corpus, and therefore the only crib that can
   be validated the moment it arrives.
