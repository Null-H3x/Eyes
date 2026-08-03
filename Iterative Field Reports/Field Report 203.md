# Field Report 203 — THE 6,806-CANDIDATE ENUMERATION IS BUILT AND RUN: FOUR OF SIX STRUCTURAL PREDICATES ARE PROVABLY BLIND, THE TWO THAT SEE FIND NOTHING THAT SURVIVES A GEOMETRY-PRESERVING NULL, AND THE SCALE-INVARIANCE THEOREM NOW HAS A CONSTRUCTIVE EDGE

*July 2026. Cycle: EYESPIRAL-C, attack line 1 of the 30-day program.
Instrument: `eyeenum.py`, gates green after two affine-invariance exclusions.
Scope: crosses FR101's inner-layer line by the principal's ruling. The result
is a clean null with a structural theorem attached — the honest outcome, and
the one that shapes lines 2–4.*

---

## 0. The headline, stated plainly

Enumeration is no longer the obstacle. After the FR201 fragment merges, the
**entire space of complete plaintext assignments for the 771-position giant
fragment is 82 × 83 = 6,806** — a coffee break, not a brute force. The engine
runs it. The binding constraint was always the oracle, and this cycle
establishes *why* the oracle is hard in a way compute can never fix:

**Of six pre-registered structural predicates, four are provably invariant
under the drift orbit, and the two that discriminate return no signal that
survives a geometry-preserving null.**

## 1. The constructive edge on scale-invariance

FR36 said scale-invariant tests cannot see the drift. This cycle makes it
operational: moving through the (d, Q0) orbit **is** applying the affine map
`p → d·p_base + Q0` to plaintext values. So a predicate can discriminate the
drift **if and only if it is not invariant under `p → a·p + b (mod 83)`.**
Checked directly across the orbit:

| predicate | distinct values over 6,806 orbit | admissible? |
|---|---|---|
| distinct-count (entropy) | 1 | **NO** — bijection preserves the value multiset |
| max-count (concentration) | 1 | **NO** — same reason |
| AP-runs (arithmetic progressions) | 1 | **NO** — an AP maps to an AP under any affine map |
| base-5 coset structure | 1 | **NO** — `p//25` partitions are permuted, not changed |
| self-offset (`p == t`) | 8 | **YES** — compares `p` to the fixed external index `t` |
| checksum (`Σp mod 83`) | 21 | **YES** — the additive constant `Q0` shifts sums |
| number-stream match (P5) | — | **YES** — matches a fixed external digit sequence |

The gates *caught two of my own predicates mid-build* (P6, then P7) and
forced their exclusion. This is the rule with teeth: **any internal-only
structural test that is not sensitive to a fixed external reference is dead
on arrival**, and now we can prove it of a candidate before running it.
The admissible class is exactly: predicates anchored to something outside
the affine group — the position index `t`, a sum's absolute value, or an
external constant.

## 2. The two admissible internal predicates: null

**Self-offset (`p == t` at header positions).** Best over the whole orbit:
**11 of 96 giant header cells** match, at (d, Q0) = (13, 20), raw orbit-p =
0.000. That raw figure is the multiple-comparisons tail of scanning 6,806
candidates for a maximum — exactly the FR41 failure mode. Priced against a
geometry-preserving null (40 random injective skeletons over the same giant
glyphs, orbit size preserved, only the plaintext-index alignment
randomized): null best-P2 runs 8–11, mean 9.1, **max 11**. Real skeleton
11. **p = 0.05. Scan artifact, not signal.** Fifth catch of this exact
shape in the program; the doctrine held.

**Checksum (`Σp` per message).** 656 of 6,806 orbit points hit an exact
zero-sum on at least one message — *below* the ~738 expected by chance. No
concentration, orbit-p 0.096 for the minimum. Null.

## 3. P5 — the number-stream battery: null on the registered constants

Six Petri-adjacent base-83 digit streams (Park-Miller `a` = 16807, Mersenne
2³¹−1, the seed constant 0xe4bc7e0, π, e, φ), matched against the giant
plaintext sequence at every phase across the orbit. Best match rate did not
exceed chance for any constant at any (d, Q0). Gate G2 confirms the detector
works — a fully embedded π-stream is recovered at 771/771 with the right
phase — so the null is a property of the corpus, not the instrument. The
registered list is not exhaustive; it is the pre-registered set with a real
prior, and it is clean.

## 4. What this rules on, honestly

- **The inner layer has no affine-detectable self-referential structure of
  the registered kinds.** Self-indexing, per-message checksums, arithmetic
  headers, base-5 coset confinement, and six named number streams are all
  refuted at the giant-fragment level (74.4% of the corpus). This converts
  FR173's "flat and non-linguistic" from a distribution statement into a
  battery of falsified explicit hypotheses — it prunes FR182's surviving
  accounts of the flatness rather than merely restating it.
- **It does NOT rule out** a payload structure that is (a) affine-covariant
  and therefore invisible to any internal test — permanently, by the theorem
  — or (b) referenced to an external key we have not registered, or (c)
  present only in the 20 dark glyphs / two small fragments. These are the
  only places inner-layer structure can now hide, and (a) is unreachable
  from inside on principle.
- **The enumeration itself remains sound and cheap.** The moment any *one*
  external anchor arrives (a single header plaintext, a d-ladder meaning),
  the orbit collapses from 6,806 to a handful and every admissible predicate
  becomes a decisive check rather than a scan.

## 5. Bearing on the 30-day program

Line 1 (this) is the highest-leverage line and it has resolved to a
principled null with a theorem. The consequence for the queue:

- **Line 2 (residual-stress) rises in priority.** If the model is wrong
  anywhere it matters, it shows in the *measured* anomalies — the 121
  contradicting scan candidates, FR184's +1.2σ, FR102's 29th dimension,
  FR195's p = 0.027 base structure — not in a-priori inner-layer space,
  which line 1 has now largely closed. This is the next build.
- **Line 3 (mode tournament) is unchanged in scope** — insurance and the
  community-facing GAK closure — and slightly cheaper to justify now that
  the affine-invariance edge gives a crisp criterion for which mode
  differences could ever be corpus-visible.
- **Line 1 is not redundant to later lines; it retires a hypothesis class
  they would otherwise have to carry.** Its instrument stays live: it is the
  scoring engine that fires the instant an external anchor lands.

## 6. Artifacts and horizon

`eyeenum.py` (engine + admissible battery + affine-invariance guard),
`giant_skeleton.json` (the 6,806-orbit parameterization), `enum_scores.json`
(the fast-predicate orbit scores). The affine-invariance classifier should
be lifted into a standing check — every future structural predicate passes
through it before it is allowed to consume corpus contact.

Next: **build line 2, the residual-stress program**, against the four
measured anomalies above. It is the line most likely to find a real crack if
one exists, precisely because it attacks what we have already observed rather
than what we can imagine.
