# Field Report 66 — THE DELIVERABLE, PRODUCED AT LAST: 462 OF 545 TOKENS OCCUR EXACTLY ONCE

*Instrument: `eyeexhibit` (corpus + skeleton, no anchors). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — my own closing claim from FR65 was false

FR65 ended: *"The internal programme is, as far as I can determine, complete."*

**It was not, and the omission is embarrassing.** Sixty-five cycles have
characterised, excluded, audited, enumerated and priced — and **not one has produced
the deliverable.** FR46 "exhibited" it as Δ tables. FR40, FR42, FR46, FR57 and FR63
argued at length about whether the output would count as a solution. Nobody built
the output and looked at it.

Worse, a large part of it needs **no anchors at all**. Within a component, plaintext
coincidence is `v[t] = v[t′]` — drift-free and base-free since FR30. So the
plaintext **repeat structure** over the held positions has been fully determined
since cycle 30, sitting unexamined for thirty-six cycles while the success criterion
was repeatedly deferred as "the most consequential open item."

The object the criterion should be decided on has been available the whole time.

---

## 1. THE DELIVERABLE, as it stands today with zero external evidence

```
positions covered            635 of 1036   (61.3%)
(message, component) blocks   35
determined repeat classes    545
  occurring exactly once     462
  occurring twice             76
  occurring three times        7
positions in a known repeat  173  (27.2% of covered)
```

**Four hundred and sixty-two of five hundred and forty-five tokens occur exactly
once.** That is the artifact. It is not a preview or an estimate — it is what the
corpus determines, now, unconditionally on drift, bases or anchors.

**What full anchoring would add.** Sampling 400 of the 22,550 candidates and
computing whole-message repeat structure (all components, not just within-block):
positions in a repeat rise from 173 to a mean of **367** (range 332–404, sd 12.4).
So the complete solution roughly doubles the repeat information — and still leaves
the majority of positions as singletons.

---

## 2. THE COMPARISON THAT SETTLES IT

Same block structure, same 635 positions, drawn from different sources:

| source | singletons | pairs | 3+ |
|---|---:|---:|---:|
| **observed (determined)** | **462** | **76** | **7** |
| random, alphabet 83 | 472 | 68 | 9 |
| random, alphabet 60 | 422 | 83 | 15 |
| random, alphabet 30 | 290 | 104 | 41 |
| random, alphabet 26 | 259 | 105 | 49 |
| English-frequency text | 191 | 83 | 73 |

**The corpus sits on the alphabet-83 line.** Not near it — on it: 462/76/7 against
472/68/9. English-frequency text of the same length in the same blocks gives
191/83/73, a completely different object.

This is FR57's result in its strongest and most concrete form. FR57 measured an
effective inventory and reported a confidence interval. This exhibits the actual
repeat profile of the actual reconstructed plaintext and compares it directly with
what language looks like.

---

## 3. The exhibit — East 1, positions 0–47

`T#` = a token determined to repeat within its block · `.` = determined singleton ·
`?` = undetermined glyph

```
.   .   .   .   .   .   ?   ?   ?   ?   .   ?   T2  .   ?   ?
T0  ?   ?   .   ?   ?   .   .   .   ?   ?   .   .   T1  .   .
.   .   ?   ?   .   ?   .   ?   .   T2  .   .   .   .   T3  .
```

62 of East 1's 99 positions are covered. This is what "solved" looks like for this
message: a sequence of mostly-distinct tokens with four recurrences in forty-eight
positions.

---

## 4. What this decides, and what it does not

**DECIDED: branch B is dead as an outcome.** Recovering `C` does not produce
readable text in any encoding, because the token stream has the repeat profile of a
uniform draw over 83 symbols. No amount of alphabet-mapping or context-filling
converts 462 hapax tokens into language. FR39's warning that "context will not fill
those gaps" is now visible rather than inferred.

**NOT DECIDED — and it cannot be, from here: whether an inner layer exists.** A
well-compressed or well-encrypted inner layer produces *exactly this profile*. Branch
A (secondary cipher) is entirely consistent with the exhibit, and so is a stream with
no content at all. **The exhibit cannot distinguish "meaningless" from "encrypted."**
That distinction requires evidence outside the ciphertext, and no statistic computed
from this corpus will supply it.

So the success criterion resolves to a sharper question than it has been carrying:

> Recovering `C` yields §1's artifact — 635 values, 462 of them unique, with the
> repeat profile of uniform noise over 83 symbols. **Is producing that object the
> solution to the Eye Messages?**

Three positions remain defensible, unchanged since FR40 but now anchored to an
artifact rather than an argument: (a) recovering the alphabet and offsets *is* the
solution, and the inner layer is a separate problem; (b) pivot to characterising the
inner layer directly, accepting that it may not exist; (c) stop.

What has changed is that the question can now be answered by **looking** rather than
by reasoning about confidence intervals.

---

## 5. Scope

Covers the 46 held glyphs (components 25/11/7/3), 61.3% of the corpus. The full
56-glyph skeleton reaches 74.1% and would raise all counts proportionally without
changing the profile — the alphabet-83 line does not move with sample size.
Conditional on repair A.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned; consistent alphabet set exactly 22,550 (FR63); first anchor spent on gauge
(FR64); model-independent premises verified from raw corpus (FR65).

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| "Internal programme complete" (FR65) | my closing claim | **RETRACTED** — the deliverable had never been produced |
| The deliverable | described, never built | **BUILT** — 635 positions, 545 classes, 462 singletons |
| Plaintext repeat structure | implicit in FR30 since cycle 30 | **EXHIBITED** — available with zero anchors, unexamined for 36 cycles |
| Branch B (readable text) | excluded by statistic (FR39/FR57) | **excluded by artifact** — repeat profile is the alphabet-83 line |
| Branch A (inner layer) | leans A, unresolved | **UNDECIDABLE from the corpus** — encrypted and empty look identical here |
| Success criterion | "decidable but undecided" (FR57) | **decidable by inspection of §1** |
| What full anchoring adds | unquantified | 173 → ~367 positions in a repeat; majority stay singletons |

---

## 8. Horizon

1. **Decide the success criterion by looking at §1.** It no longer requires new
   evidence, new compute, or another cycle. It requires a judgement about whether
   that object is the thing being sought.
2. If **(a)** — five real anchors, one per component (FR64), buys the full 61.3%
   artifact and 22,550 → 1.
3. If **(b)** — the inner-layer programme needs an external hypothesis about what
   was encoded, since the corpus cannot distinguish encrypted from empty.
4. Items unchanged and still cheap: **MSB state count** on the glyph pictures
   (FR59), **the radix** (`GHIDRA.md`), **the EyeStat filter port** (FR61/FR62).

My own read, offered as a view and not a finding: the internal programme is now
genuinely complete, and item 1 is not a task but a decision.
