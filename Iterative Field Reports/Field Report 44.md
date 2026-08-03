# Field Report 44 — H1 Belongs to a Reading We Discarded

**Series note.** Forty-fourth report of the EYESPIRAL series. FR43 put two structural
hypotheses into conflict and nominated two ways forward. One dissolves on inspection; the
other retires a hypothesis the project has carried since cycle five. Instrument
`eyeh1.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR43's item 1 — attack the consecutive-label assumption — is
**not testable as posed**, and this cycle demonstrates why rather than attempting it. The
indicator is ind_m = C[(label_m + base_m + K_g[0]) mod 83] with base_m free per message
and K_g[0] free per triplet, so a consecutive label assignment and an arbitrary one are
*equally* solvable for the bases; the label structure leaves no trace in the ciphertext.
Item 2 is decisive. **H1's two glyphs sit at the terminal position of an opening block** —
glyph 47 closing T3's 1–20 and glyph 1 closing T1's 1–24, each present in all three
members of its triplet. FR29 concluded the T3 opening must be read as **literal stamped
material** or the system contradicts at every drift, and FR33's widening forced the same
reading onto T1. Under that reading those positions carry no plaintext token, so H1's
claim about their q-values **has no referent**. A second and independent argument points
the same way: if the openings are literal and a shared boundary marker closes both, that
marker would be the *same glyph* — it is not, 1 against 47. A single token encrypting to
two different glyphs is possible only under the *encrypted* reading, which FR29 and FR33
rejected. **H1 is retired**, on coherence rather than on measurement, and FR43's conflict
resolves by removing one side rather than by testing the other.

---

## 1. H1 — where the glyphs live

| glyph | slot | triplet | present in | position in opening |
|---|---|---|---|---|
| 47 | 20 | T3 (E4, W4, E5) | 3/3 | **terminal** of 1–20 |
| 1 | 24 | T1 (E1, W1, E2) | 3/3 | **terminal** of 1–24 |

FR5's reading was structurally reasonable: the last slot of each opening frame looks like
a boundary marker, and the same marker closing both frames would give
q[1] − q[47] = 4. The observation about *where* the glyphs sit was correct. What has
changed is the model around them.

## 2. H2–H3 — why it no longer coheres

FR29 established that admitting the T3 opening as encrypted shared plaintext contradicts
the constraint system at every non-degenerate drift, and that reading it as stamped
literal material leaves a fully consistent model. FR33's passage widening then forced the
same reading onto T1. Both of H1's sites are inside those blocks.

Under a stamped reading there is no plaintext token at those positions, so a relation
between their plaintext tokens is not false — it is **undefined**.

The second argument is independent of that chain and arrives at the same place. If the
openings are literal glyphs and both frames close with the same boundary marker, the
terminal glyphs would be identical. They are **1 and 47**. A single token producing two
different glyphs requires an encryption step with differing offsets — precisely the
encrypted-openings reading the model rejected.

So H1 is not a hypothesis awaiting evidence within the current model; it is a hypothesis
belonging to the branch the model discarded.

## 3. H4 — the prefix tree, and why the stamped reading is natural

| window 1…k | distinct sequences across the nine messages |
|---|---|
| 1–2 | **1** |
| 1–3 | 2 |
| 1–5 | 2 |
| 1–6 | 4 |
| 1–9 | 4 |
| 1–10 | 5 |
| 1–20 | 5 |

The openings form a nested tree: a universal two-glyph head (66, 5) shared by all nine
messages, then successive branchings. Notably East 3 and East 4 share positions 1–9
*across different triplets*. That is the shape of a structured header rather than of nine
independent texts, and it matches what the depth-tree work recorded by a different route.

## 4. H5 — FR43's item 1 dissolves

Fixing consecutive labels 0…8 and solving for the bases succeeds; fixing arbitrary labels
and solving succeeds equally. Both reproduce the observed indicator glyphs exactly. The
label structure is therefore **unobservable from the ciphertext**, and cannot be attacked
from inside the corpus. This is the eighth horizon item in the series to die on inspection
rather than on measurement.

## 5. Where this leaves the drift

- **H1: retired**, conditional on the stamped-header reading. If that reading is ever
  abandoned, H1 revives — and this should be recorded rather than forgotten, since the
  stamped reading is itself a hypothesis adopted to remove a contradiction.
- **H4: survives** as the only drift hypothesis, still resting on an untestable premise,
  still implying drift ∈ {1…8, 75…82} if the labels are consecutive.
- **FR43's conflict is resolved** by removing one side. That is a weaker resolution than
  testing either would have been, and it is the one the evidence supports.

## 6. What the model now carries

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure. Drift unpinned, with one conditional hypothesis rather than two
conflicting ones. Plaintext: large effective inventory, no detected structure
(FR36/FR39/FR40; FR41 withdrawn in FR42). Openings: stamped headers in a nested tree.

## 7. Horizon

(1) **The stamped-header reading now carries more weight than it was adopted with.** It
was introduced in FR29 to remove a contradiction and has since been used to force T1
(FR33) and to retire H1 (here). It deserves a direct test if one can be devised —
something that distinguishes stamped literal glyphs from ciphertext of shared plaintext
without routing through the constraint system. (2) Two external anchors in component 1
remain the only route to the drift, and would settle H4 immediately. (3) The success
criterion (FR40 §4) is untouched and remains the most consequential open item.

## 8. Reproduction

`eyeh1.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — H1's glyphs verified at the stated slots in all three triplet members and
inside the opening blocks, consecutive and arbitrary labels both shown solvable, the
prefix tree verified non-decreasing with a universal two-glyph head, and the baseline
guard. The full run reproduces H1–H6. Failures carry prefix `XD-MBYG04K-URS3LF`.
