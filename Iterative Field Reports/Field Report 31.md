# Field Report 31 — A Route That Is Real and Still Cannot Bootstrap

**Series note.** Thirty-first report of the EYESPIRAL series. FR30 named widening the
components as the single lever improving both the endgame exposure and the drift-free
channel's power, and FR18 required any new route to be "different in kind" from isomorph
pattern-matching. This cycle builds one, runs it, and reports what it does and does not
reach. Instrument `eyeseek.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR30's second horizon item dies on inspection: applying the
v-channel to the T3 opening would restate FR29's contradiction rather than test it, since
the three T3 messages carry identical glyphs at identical positions, making v identical
across them **by construction** — requiring equal plaintext then forces the equal offsets
FR29 already proved impossible. That is the seventh horizon item retired this way. The
first item yields a genuinely new constraint form. FR30 established q[s] = base_C +
drift·Δ_s inside a component, so for a candidate same-passage pair at shift Δ, every cell
whose two glyphs lie in one known component predicts **w = Δ_{c₂} − Δ_{c₁} − Δ** to be
constant — drift-free, and applicable to window pairs the isomorph scan rejects outright.
It works: on a planted corpus it finds the passage at the correct alignment; on shuffled
corpora it finds nothing; on the corpus it hits **14 distinct alignments against 0 on
three shuffles.** But **13 of those 14 lie on alignments already in the constraint pool**,
and the single new one — East 4 @ 28 × West 4 @ 29, shift +1 — carries only five
informative cells. That is precisely what the method's selection effect predicts, and the
result is a quantified statement of the bootstrap limit: **the skeleton can confirm its
own territory but cannot extend past it**, because the components were built from the
pool and the scan can only see passages composed largely of glyphs the pool already
linked.

---

## 1. Corrections first

**I wrote a verdict before seeing the numbers, and it was wrong.** Mid-cycle I drafted
the conclusion "a test that cannot recognise the pairs we know are same-passage cannot
discover new ones — the skeleton cannot bootstrap itself," reasoning from a feasibility
probe that showed a mean of only ~1 usable cell per *random* window pair. The positive
control contradicted it outright: certified pairs average **7.6 informative cells**, with
59 of 67 carrying five or more, against a random-pair mean of 1.4. The test discriminates
strongly. The conclusion I reached later is superficially similar but rests on an entirely
different mechanism — selection, not weakness — and I would have published a correct
sentence for a wrong reason.

**A confound caught before it produced a result.** The first scan returned 234 hits and
zero on shuffles, which looked spectacular. Most were windows that are **literally
identical** — the E1/W1 near-duplicate runs and the T1 opening — where identical glyphs
give w trivially and carry no information about the alphabet at all. Restricting to cells
whose glyphs *differ*, and deduplicating sliding windows of one underlying alignment,
takes 234 down to 14. The filter is now a regression test in the gate.

## 2. The method

Inside a component, q[s] = base_C + drift·Δ_s with Δ_s known (FR30). For a candidate
same-passage window pair at shift Δ, a cell whose two glyphs both lie in one component
gives

  q[c₂] − q[c₁] = base_diff + drift·Δ  ⟹  **w = (Δ_{c₂} − Δ_{c₁} − Δ) mod 83 = base_diff/drift**

which must be the *same* for every such cell. Three properties make this different in
kind from what FR19 closed: it is **drift-free**, it uses **derived knowledge** rather
than raw repeat patterns, and it can evaluate window pairs that carry no matching
isomorph skeleton at all.

## 3. Results

| check | outcome |
|---|---|
| planted passage on a synthetic corpus | **found at the correct alignment** |
| shuffled synthetic corpus | 0 hits |
| certified pairs, informative cells | mean 7.6, max 15, ≥5 in 59/67 |
| random window pairs | mean 1.4 |
| **corpus scan (L = 13, ≥5 agreeing)** | **14 alignments** |
| three unigram-preserving shuffles | **0, 0, 0** |
| of the 14, on alignments already in the pool | **13** |
| genuinely new | **1** — East 4 @ 28 × West 4 @ 29, shift +1, 5 cells |

**The circularity caveat on the positive control**, stated because it matters: those
certified pairs *built* the components, so their cell-richness is partly self-fulfilling.
The honest measure of the method is what it finds outside the pool, and that is the
thirteen-versus-one line.

## 4. What this establishes

**The bootstrap limit, quantified.** The scan re-finds known territory reliably — it
recovers the #M family, the strict W1/E2 alignments, the #3 and #2 regions in T3 — and
finds essentially nothing beyond. The reason is structural rather than a defect of the
test: the components consist of glyphs the pool's pairs linked, so a passage made of
*other* glyphs contributes no usable cells and is invisible. **The skeleton confirms its
own reach and cannot extend past it.**

That closes the last route to widening the components without external input. FR19 closed
three (openings, opening↔body isomorphs, constant dots); FR18's fifteen candidate glyphs
were the remaining hope; this cycle shows the one constraint form that is genuinely
different in kind is subject to the same reach limit.

**One lead, watch-grade.** East 4 @ 28 × West 4 @ 29 at shift +1 is not explained by any
pool alignment. With five informative cells its chance price is roughly 83⁻⁴ per
alignment against ~10⁵ alignments scanned, so it is not obviously noise — but five cells
is thin, it sits in the T3 near-duplicate region where alignment artefacts are plausible,
and it was found by a scan I designed after seeing the corpus. Logged for verification,
not claimed.

## 5. Where the programme stands

Every internal route to enlarging the determined set is now closed or quantified:
recalibrating the scan (FR18), the openings, opening↔body isomorphs, constant dot cells
(FR19), and skeleton-guided passage search (here). The determined skeleton stands at 223
relations over 47 glyphs in components of 19/7/7/3/3, drift-conditional but pinned by any
single external pair-difference, and **external anchors remain the only lever** — two in
component 1 buying a quarter of the corpus, nine leaving 44 enumerable completions.

## 6. Horizon

(1) **Verify or retire the E4@28 × W4@29 lead** with a pre-registered test at other
window lengths — if it is a genuine passage it should survive lengthening; if it is an
alignment artefact of the T3 near-duplicates it will not. (2) **#2⁻'s instance-level
audit** is the last standing structural item from FR15. (3) The acquisition target is
unchanged and now well-specified: two external anchors inside component 1, which fix the
rotation and the drift together.

## 7. Reproduction

`eyeseek.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — a planted passage found at the correct alignment, shuffled corpora clean,
the identical-glyph filter proven to suppress literally duplicated windows, alignment
deduplication, and the baseline guard. The full run reproduces S1's positive control with
its circularity caveat, S2's scan against shuffles, S3's known-versus-new table and S4's
reading. Failures carry prefix `XD-MBYG04K-URS3LF`.
