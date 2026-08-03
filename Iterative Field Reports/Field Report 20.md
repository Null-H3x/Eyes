# Field Report 20 — What A-vs-B Actually Costs

**Series note.** Twentieth report of the iterative series. FR19 concluded that the
A-vs-B fork is the binding constraint on the whole programme — it decides whether the
endgame route terminates in readable text or in a permutation nobody can fix. This
cycle builds the discriminator, measures its power, and converts the doctrine's "~40
pins" estimate into a measured requirement. Instrument `eyefork2.py`, selftest 5/5
green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only. This cycle does **not** resolve A-vs-B — it cannot, and §3 says exactly why.
It prepares the test and prices it.

**One-paragraph verdict.** The doctrine's guardrail against bigram probes below ~40
pins turns out to be mechanical rather than cautious, and the mechanism is worth
stating: under the progressive reading, two positions carrying the same plaintext
bigram produce matching ciphertext bigrams only if drift·(t′−t) = 0 — so **the drift
destroys plaintext bigram structure in the raw ciphertext**, and de-drifting, which
needs pins, is unavoidable. The selftest demonstrates it directly: 110 planted
plaintext bigram repeats, **zero** surviving into the ciphertext. The discriminator is
therefore the index of coincidence of adjacent *de-drifted* differences, which has the
useful property of being **shift-invariant** — the per-triplet drift left free by
FR16's coherent model shifts every difference within a triplet by a constant and leaves
the statistic untouched. Measuring its power against the corpus's actual supply of
usable pairs gives the requirement: a pair counts only if **both** positions carry a
determined glyph, so usable pairs grow as the square of coverage. The **current eight
pin-grade glyphs yield 12 usable pairs** — no power whatever. Forty frequency-greedy
pins give ~360; the full reachable set of 51 gives **464**, which is roughly 4σ
separation at moderate structure. And that closes a loop: FR17 showed eight
well-chosen external anchors determine all 51 reachable glyphs, so **the same eight
acquisitions that expose 67.7% of the corpus also supply enough pairs to resolve
A-vs-B.** One acquisition target serves both halves of the programme.

---

## 1. Why the fork is genuinely gated

This is worth deriving rather than asserting, because it explains why twenty cycles of
work have not touched it. Under c[t] = C[(p[t] + off_m + drift·t) mod 83], take two
positions t and t′ carrying the same plaintext bigram: p[t] = p[t′] and
p[t+1] = p[t′+1]. Their ciphertext bigrams match only if drift·(t′−t) ≡ 0 — that is,
only if the positions coincide. Repeated plaintext bigrams, the very thing that reveals
language structure, are systematically erased from the raw ciphertext by the drift.

The selftest checks this on planted data: 110 plaintext bigram repeats, **0** surviving
as ciphertext bigram repeats. No analysis of the raw ciphertext can recover what the
drift removed; the only route is de-drifting, and de-drifting requires knowing q at
both positions of a pair.

## 2. The discriminator

Once positions are de-drifted, the adjacent differences p[t+1] − p[t] become
observable. Branch A (a further layer — flat, high-entropy tokens) makes them uniform;
branch B (a token stream retaining structure) concentrates them. The statistic is their
index of coincidence, against the uniform baseline 1/83 = 0.01205.

| model B structure strength | A | B |
|---|---|---|
| 0.40 | 0.01208 (×1.00) | 0.01267 (×1.05) |
| 0.55 | 0.01188 (×0.99) | 0.01292 (×1.07) |
| 0.65 | 0.01220 (×1.01) | 0.01349 (×1.12) |
| 0.80 | 0.01229 (×1.02) | 0.01451 (×1.20) |

Two properties make it the right choice here. It is **shift-invariant**, so the free
per-triplet drift of FR16's coherent model — which shifts every difference within a
triplet by one constant — leaves it unchanged; the statistic can be computed per triplet
and pooled without knowing any drift. And it is a direct analogue of the unigram IoC the
doctrine already uses for the plaintext-alphabet measurement, so the two sit on the same
footing.

## 3. Power, and the corpus's supply

Separation between the two models, in standard deviations of the A-distribution:

| usable pairs | B = 0.40 | B = 0.55 | B = 0.65 | B = 0.80 |
|---|---|---|---|---|
| 100 | 0.3σ | 1.0σ | 0.7σ | 1.2σ |
| 200 | 0.5σ | 2.2σ | 2.1σ | 4.1σ |
| 400 | 1.1σ | 2.8σ | **4.6σ** | 5.7σ |
| 800 | 2.5σ | 7.3σ | 8.0σ | 13.5σ |

Against that, what the corpus can actually supply. A pair is usable only if *both*
positions carry a determined glyph, so the count grows as the square of coverage:

| pinned glyphs | random | frequency-greedy | coverage |
|---|---|---|---|
| 8 | 9 | 39 | 17.2% |
| 16 | 42 | 104 | 30.8% |
| 25 | 110 | 198 | 43.1% |
| 30 | 153 | 251 | 49.0% |
| 40 | 281 | 360 | 59.2% |
| **51 (all reachable)** | **464** | **464** | **67.7%** |

Total adjacent pairs in the corpus: 1027. **The current eight pin-grade glyphs supply
12.** The doctrine's guardrail is vindicated numerically — at 12 pairs the test has no
power at any structure strength, and any bigram or entropy probe run now would be
reading noise.

Note also that frequency-greedy selection roughly doubles the yield of random selection
at small pin counts (39 versus 9 at k = 8). That is a *different* ordering from FR17's
leverage-greedy anchor list, which maximises how many glyphs get determined. Two
objectives, two orderings — worth keeping distinct if pins ever arrive one at a time.

## 4. The loop that closes

Putting the last four reports together gives a single quantified route:

- **FR17:** eight well-chosen external anchors determine all 51 reachable glyphs.
- **FR19:** those 51 expose 701 of 1036 positions — 67.7% — with unknowns mostly
  isolated single gaps.
- **FR20:** those same 51 supply 464 usable adjacent pairs, around 4σ of A-vs-B
  separation at moderate structure.

So the acquisition target is not two separate programmes. The eight anchors that would
make two-thirds of the corpus legible are the same eight that would resolve the fork
gating whether legibility means anything. That is the most useful thing this cycle
produces: a single, small, well-specified acquisition goal that unlocks both halves.

## 5. The caveat, which is not small

Power depends on how much structure branch B actually has, and that is exactly what is
unknown. At structure strength 0.65 the full reachable set gives 4.6σ; at 0.40 it gives
about 1.1σ, which is no answer at all. **If the true token stream is flatter than the
simulation assumes, A-vs-B stays open even after a complete solve of the reachable
set.** The honest statement is conditional: the corpus can supply enough pairs to
resolve the fork *if* branch B carries moderate structure, and cannot if it carries
little. That asymmetry is itself informative — a null result from this test at full pin
strength would not prove branch A, only that structure is below the detection floor.

## 6. Horizon

(1) **The discriminator is built and gated; it should be run the moment the pin count
rises**, and nothing is gained by running it earlier. (2) **A second statistic with
different failure modes would be worth having** — the difference-IoC is one projection
of bigram structure, and a token stream could carry structure it happens to miss;
conditional-entropy or repeat-distance statistics fail differently. (3) The 15
candidate glyphs (FR18) and #2⁻'s instance-level audit (FR15) remain the standing
structural items. (4) External anchors remain the only lever on everything above.

## 7. Reproduction

`eyefork2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — the IoC baseline, model A/B separation on plaintext, shift
invariance, the drift-destroys-bigrams mechanism on planted data, and the baseline
guard. The full run reproduces S1's discriminator table, S2's power curve across
structure strengths, S3's supply table and S4's synthesis. Failures carry prefix
`XD-MBYG04K-URS3LF`.
