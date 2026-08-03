# Field Report 45 — A Test That Does Not Exist

**Series note.** Forty-fifth report of the EYESPIRAL series. FR44 asked for independent
evidence on the stamped-header reading — a test that does not route through the constraint
system that motivated it. This cycle tries, fails, and reports the failure along with two
artifacts it caught in its own analysis. Instrument `eyestamp.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The test FR44 requested **does not exist in the form asked**.
Two candidates were tried. The **cross-triplet identity** — East 3 and East 4 carrying
identical glyphs at positions 1–9 despite being in different triplets — looks like evidence
for literal stamped material, but fails on inspection: under the encrypted reading
identical glyphs require K_T2 − K_T3 to be constant across the span, and under progressive
keystreams with FR3's drift equality **it is constant**, so both readings predict the
identity. The **glyph-repeat rate** is informative but not decisive: under the encrypted
reading a repeated glyph needs p[t] − p[t′] = −drift·(t − t′), a 1-in-83 coincidence, so
repeats sit at chance whatever the plaintext; a header written over a *small* symbol set
would repeat far more. Measured per block, the openings sit at chance (pooled z = +0.72)
and match the body (z = −1.60). That **excludes a small-alphabet stamped header** but
cannot separate encrypted material from a header stamped over the full 83-glyph set, since
both are effectively uniform. Along the way this cycle caught **two artifacts in its own
analysis**, both from pooling: pooling all nine openings counts T1's block three times and
T3's three times, inflating the IoC to a spurious z = +12; pooling the five *distinct*
blocks still double-counts their shared prefix, giving a confounded z = +4.57 that measures
the known depth tree. Only the per-block comparison is sound.

---

## 1. S1 — the candidate that failed on inspection

East 3 and East 4 share positions 1–9 identically across different triplets, which at first
looks like a literal stamp. Under the encrypted reading, c_m[t] = C[(p[t] + base_m +
K_g[t])], so identical glyphs across the span require

  base_E3 + K_T2[t] = base_E4 + K_T3[t] for t = 1…9

that is, K_T2 − K_T3 constant. Under progressive keystreams with FR3's cross-triplet drift
equality, that difference **is** constant. Both readings predict the observation, so it
carries no discriminating information. Retired before measurement.

## 2. S2 — the repeat-rate test

| block | len | pairs | repeats | expected | z |
|---|---|---|---|---|---|
| East 1 (T1 opening) | 24 | 276 | 4 | 3.33 | +0.37 |
| West 2 | 20 | 190 | 1 | 2.29 | −0.86 |
| East 3 | 20 | 190 | 6 | 2.29 | +2.47 |
| West 3 | 20 | 190 | 2 | 2.29 | −0.19 |
| East 4 (T3 opening) | 20 | 190 | 2 | 2.29 | −0.19 |
| **pooled openings** | | 1036 | 15 | 12.48 | **+0.72** |
| **body, 20-windows** | | 6840 | 68 | 82.41 | **−1.60** |

East 3's +2.47 is one of five blocks examined and is not remarkable after that
multiplicity. Openings and body sit at comparable rates, both near chance.

## 3. S3 — what is excluded

| stamped alphabet size | expected repeats in 24 glyphs |
|---|---|
| 26 | 10.6 |
| 40 | 6.9 |
| 60 | 4.6 |
| 83 | 3.3 |
| **observed (T1 opening)** | **4** |

A header written over a small symbol set — a title in a 26-letter alphabet, say — is
**excluded**. A header stamped over the full glyph set is not distinguishable from
ciphertext by this measure, because both are effectively uniform over 83 symbols.

## 4. S4 — two artifacts, both mine, both from pooling

| pooling | IoC | what it actually measures |
|---|---|---|
| all nine openings | 0.02825 | T1's block counted 3×, T3's 3× |
| the five distinct blocks | 0.02240 | still double-counts the shared prefix 66, 5, 49, 75, 54 |
| body | 0.01240 | — |

The first gave a spurious z = +12 against the body; the second a confounded z = +4.57. Both
are measuring the depth tree — the nested shared prefixes documented in FR44 — rather than
any distributional difference between opening and body material. I had the first figure
drafted before noticing that the nine openings are not nine independent samples.

The general form of the error is worth naming, since it is the third pooling mistake in
five cycles (FR39's near-duplicate contamination, FR42's geometry-destroying null, and
now this): **when blocks are related by construction, pooling them counts the relationship
as data.**

## 5. S5 — the verdict, and what it means for the doctrine

FR44's requested test does not exist in the form asked. Every measure tried here returns
the same answer for encrypted material and for a header stamped over the full glyph set,
because both are uniform over 83 symbols and the openings are short.

So the stamped-header reading remains **adopted for consistency rather than independently
supported**, and that is its correct standing. It should be carried as such: introduced in
FR29 to remove a contradiction, used in FR33 to force T1 and in FR44 to retire H1, and
resting throughout on the constraint system rather than on evidence outside it. If it is
ever abandoned, H1 revives and FR33's widening needs revisiting.

## 6. Where the model stands

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure. Drift unpinned, with H4 the only surviving hypothesis (conditional on the
untestable consecutive-label premise). Plaintext: large effective inventory, no detected
structure. Openings: stamped headers over the full glyph set, in a nested prefix tree —
with the stamped reading itself unsupported outside the constraint system.

## 7. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift, and would
settle H4 immediately. (2) **The success criterion** (FR40 §4) is untouched and remains the
most consequential open item — it governs whether acquisition is worth pursuing at all.
(3) Any future test of the openings must contend with the fact that short blocks over a
large alphabet carry very little statistical signal; a decisive test would need a
mechanism, not a statistic.

## 8. Reproduction

`eyestamp.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — the pooling artifact demonstrated on constructed data, the repeat counter
verified exact, a 26-symbol block shown to register as elevated while an 83-symbol block
does not, the five distinct opening blocks confirmed, and the baseline guard. The full run
reproduces S1–S5. Failures carry prefix `XD-MBYG04K-URS3LF`.
