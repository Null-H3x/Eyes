# Field Report 117 — THE CRIB VERIFIER: TURNING THE MODEL INTO SOMETHING OTHERS CAN USE

*Instruments: `eyecrib.py` (9/9 gate) and `eyemodel.py` (embedded tables). July 2026.*
*Cycle: EYESPIRAL.*

---

## 0. Why a tool rather than another analysis

FR115 closed the last internal attack; FR116 priced the remaining compute and
found the reachable work is under a week with the next tier 3,850× a GPU month.
**The project's constraint changed character**: for 116 cycles it was analysis,
and it is now access to one piece of external evidence.

`ACQUISITION_SPEC.md` is written for someone who *already has* evidence. What
was missing is the reverse — a way for anyone to **test a guess**. Every prior
instrument in this series was built for me; this one is built for other people.

---

## 1. What it does

Feed it a **crib** (what you believe the plaintext says over a run of positions
in one message) or **anchors** (what you believe specific glyph values decrypt
to in the alphabet), and it returns one of four verdicts by checking all 1,394
candidate `(d1, d2)` pairs:

```
1394  NO INFORMATION   the guess is too short or lands badly
  17  PARTIAL          ratio unresolved -- the two-anchor state
   1  SOLVED           the drift is determined
   0  REFUTED          no assignment of the free parameters works
```

A solved result is classified against the repair fork automatically — the ratio
falls in repair A's exclusive set, repair B's, or the four-way overlap — so
**testing a crib also tests the fork** (FR109/FR110), at no extra cost.

**Self-contained.** `eyemodel.py` embeds the coefficient tables `ALPHA`/`BETA`,
the nine components, the corpus and the ratio classification, all generated from
the canonical build (`eyeaudit.py` 11/11: 384 relations, 0 violations, 56
glyphs, 74.1% exposure). Anyone can run it with stdlib Python and no toolchain.

---

## 2. Gate

```
t1_tables                 56 glyphs, components [25,11,7,3,2,2,2,2,2]
t2_corpus                 1036 glyphs
t3_valid                  1394 candidates
t4_true_crib_survives     planted truth survives
t4b_true_crib_resolves    resolves to exactly 1 at L=20
t5_corrupt_refuted        one token corrupted -> 0 survivors
t6_short_uninformative    2-token crib -> 1394 survivors
t7_anchors                3 planted anchors in C1 survive
t7b_undetermined_raises   an undetermined glyph is rejected with a clear error
                                                              9/9 green
```

The two that matter are **t5** and **t6**: the tool must refute a wrong guess
and must *not* claim information it does not have.

---

## 3. Demonstrated end to end

A correct 16-token crib planted at East 4@40 (truth `d1=35, d2=61`):

```
crib East 4@40 length 16: 11 positions usable (5 land on undetermined glyphs)
candidate (d1,d2) surviving : 1 of 1394
>>> SOLVED <<<   d1 = 35   d2 = 61   ratio 55   ->  repair A only
```

The same crib with **one token changed**:

```
candidate (d1,d2) surviving : 0 of 1394
>>> REFUTED <<<
```

A three-token crib:

```
>>> NO INFORMATION <<<   1394 of 1394 survive
```

Bad input fails loudly rather than silently: an undetermined glyph offered as an
anchor, or an unknown message name, each raise with the reason and the valid
options.

---

## 4. What it makes possible

**Anyone can now falsify the model in thirty seconds.** That is the point.
A wrong guess is refuted outright ~80% of the time with a residual false-accept
rate of ~0.24% (FR113), so the tool is a genuine test rather than a
plausibility check.

Three uses the project could not support before:

- **Community hypotheses become testable.** Years of proposed readings on the
  wiki and in the research repos can be checked mechanically instead of argued.
- **A fragment-holder learns what they have.** Someone who knows a piece of the
  plaintext without realising its value can find out immediately.
- **An approach to the author becomes concrete.** The ask is no longer "what
  does it say" but *"fifteen consecutive tokens, or one glyph's alphabet
  value — and here is the tool that will verify your answer."*

---

## 5. The honest caveats, stated in the tool itself

- **The plaintext is almost certainly not letters.** Inventory exceeds ~60
  symbols with no detected language structure (FR36/39/40). Guesses of the form
  "this spells a word" are already excluded by shape. Tokens are integers 0..82.
- **Conditional on repair A.** FR109/FR110 showed repair A is the *conventional*
  reading, not a supported one; repair B is live at five ratios. The tool
  reports which repair a result implies rather than hiding the assumption.
- **Undetermined glyphs contribute nothing.** 27 of 83 carry no relation, so a
  crib landing on them is shorter than it looks — the tool reports usable
  positions separately from length.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Model accessibility | six reports plus a toolchain | **two stdlib files**, `eyecrib.py` + `eyemodel.py` |
| Testing a hypothesis | required me | **anyone, in seconds** |
| Repair-fork test | manual, per FR109 | **automatic** on every solved result |
| Project bottleneck | analysis | **access to evidence** — and the tool is aimed at that |

---

## 7. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean at 17 ratios;
exposure 74.1%; reading space 2^36.4. Cumulative: 27.28 billion candidates,
zero survivors.

---

## 8. Horizon

1. **Run the double-shuffle sweep** when the GPU box is free (FR116, ~25 min).
   Expected null; it closes the last motivated generator gap.
2. **Put `eyecrib.py` in front of people.** The community repos and the wiki are
   the obvious first audience, and the tool is designed so that no trust in this
   series is required — it either refutes your guess or it does not.
3. **The analysis programme is closed.** Every internal route has been
   exhausted with a stated reason. What remains is evidence, and this cycle is
   the last thing I can build that makes evidence easier to obtain rather than
   easier to analyse.
