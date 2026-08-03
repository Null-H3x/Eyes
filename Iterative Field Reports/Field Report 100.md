# Field Report 100 — THE PLACEMENT RNG IS OUR RNG, AND THE COORDINATE GRAMMAR DIES ON MECHANICS

*Sources: Lymm's Binoculars (eye-placement algorithm), a community chunk-coordinate*
*ledger. Verified against `eyerunner.py`. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Why this cycle exists

FR99 closed the generator sweep. The exploration that followed asked the only
remaining structural question the corpus itself can pose: **what could the
plaintext BE**, and is any candidate structure checkable on a partial
decryption? That analysis reduced the space to three readings, of which only
one — plaintext as *structured data with a local grammar* — admits a sectional
attack. The best-supported member of that family was a **coordinate list**,
motivated by the artifact being embedded in a game world with a coordinate
system.

Two external artifacts then arrived: a ledger of static in-world chunk
coordinates, and the community's eye-placement script. Together they settle the
coordinate hypothesis, corroborate the sweep's generator choice from outside the
project, and formally subsume a seeding idiom the sweep never explicitly tested.

---

## 1. The placement RNG is bit-identical to the swept generator

Lymm's script places the nine eye messages via `lcm_poro`:

```python
hi = r // 127773;  lo = r - hi*127773
t = 16807*lo - 2836*hi;  if t <= 0: t += 2147483647
```

**Verified: 300 consecutive states across six seeds, zero mismatches against
`eyerunner.py`'s LGM.** This is the same Park-Miller/Schrage generator with the
same Schrage constants that FR92 recovered from the author's `random.cpp` and
FR99 exhausted.

The integer mapping is likewise the project's:

```python
x = int(lcm_output * 4.656612875e-10 * world_chunk_length)
```

— the **floor** map with **his** scale constant, not a modulo reduction and not
`1/(2³¹−1)`. FR96 established that constant's exactness matters (the two
divisors diverge on ~1 draw in 5e17) and the sweep carried it verbatim; here is
independent in-the-wild confirmation that the floor-scaling idiom is the
author's authentic practice for this RNG.

**Value:** the sweep's generator and mapping choices were inferred from his
source and his habits (FR92, FR94). They are now corroborated by a second,
independent artifact that nobody built for this purpose. That does not make the
sweep's null stronger — a null is a null — but it removes a live worry that the
sweep was exhausting the *wrong family*.

---

## 2. A seeding idiom the sweep never tested — and why it changes nothing

The placement code seeds the LGM through a transform the cipher sweep did not
use:

```python
r = float(seed ^ 0xe4bc7e0)
if r > 2147483647.0: r *= 0.5
r = lcm_poro(r)
```

An XOR against a magic constant, then a conditional halving. The sweep fed raw
integers. The obvious worry: if `C` were seeded the same way, the sweep tested
the wrong effective seeds.

**It did not, and the reason is a property of exhaustive sweeps worth stating
as doctrine.** XOR with a constant is a bijection on seed space; the conditional
halve maps `(2³¹, 2³²)` back into `(2³⁰, 2³¹)`. So the transform's entire image
lies within `[0, 2³¹)` — **verified over 200,000 random game-seeds, zero
outside**. FR99 swept LGM seeds `[1, 2³¹)` exhaustively. Every LGM seed this
transform can produce was therefore already tested.

> **A full-range sweep is invariant under any seeding transform whose image
> lands inside the swept range.** The transform changes *which* game-seed maps
> to a given LGM seed; it does not change the *set* of LGM seeds. This is the
> concrete payoff of FR99's decision to exhaust rather than window: a windowed
> sweep would have had to be redone, and this one does not.

FR99's closure holds without qualification.

---

## 3. The coordinate grammar is dead on mechanics, not statistics

The decisive fact from the placement script: **eye positions are a function of
the world seed.** The nine messages appear at different chunk coordinates in
every world; only their *content* is fixed. Three consequences, in order of
importance:

**(a) Eye coordinates cannot be external anchors.** The anchor route (R6) needs
glyph→token pins from outside the cipher. A coordinate that varies by seed
carries *seed entropy*, not glyph identity. There is no "where the eyes are" to
look up. This closes the most attractive reading of the chunk-coordinate data.

**(b) The plaintext cannot be coordinates of anything.** The ciphertext is
identical across all seeds, so the payload is static. A static payload cannot
encode seed-derived positions. Coordinates of *fixed* objects (orbs, tablets,
bosses) remain conceivable in principle, but fail on their own merits —

**(c) The coordinate-list grammar fails its statistical tests independently.**
Measured against the ledger of 49 static object coordinates: those coordinates
cluster near the origin (49% within [−10, 10]), as any real map does, while the
plaintext is flat over 60+ symbols (FR39); the coordinate range (−51..73, width
124) does not fit the eye value range (0..82); and 1,036 glyphs is ~518
coordinate pairs against 49 known locations.

**Self-correction logged.** A test for coordinate-like *difference* structure
(small deltas between consecutive plaintext entries) returned 71% at drift 3
against a 36% random expectation, and I nearly reported it. It is a
**skeleton-geometry artifact of the FR41/FR42 class**: the consecutive
difference is `drift × K` where `K = (ΔΔ − Δt)` is fixed by the known deltas
and independent of plaintext, so "small at small drift" is arithmetic, not
cryptanalysis. The tell is that drift 80 (≡ −3) mirrors drift 3 exactly. Sixth
catch of this shape (FR39, FR42, FR45, FR48, FR97, FR100). The guard remains
what it has always been: ask what the statistic would return if the hypothesis
were false, and check the answer differs.

---

## 4. What the inner-layer analysis established (the cycle's positive content)

Beyond the closures, the exploration produced two structural results worth
carrying:

**The undetermined glyphs never form runs longer than 3.** Measured across all
nine messages: the longest consecutive all-undetermined span in the corpus is
**3 positions** (2 in East 4 and West 4). Undetermined glyphs are *isolated*,
interleaved with determined ones. Consequence: there is no "blank the middle and
brute-force a 15-character span" window anywhere in this corpus. The correct
picture of a partial attack is a **sparse fill** — any window is ~74%
determined plaintext with 1–3 holes.

**The backbone is over-determined ~10×, and that is the real lever.** Correcting
an error I made mid-analysis: the base freedom is not ~8 but **35**, one per
(message, component) pair — 9 messages × ~4 components each. With 635 determined
positions against 1 drift + 35 bases + 27 undetermined tokens ≈ 63 unknowns,
the system is over-determined 10:1. A sufficiently restrictive grammar checked
against the *determined* backbone would pin (drift, bases) globally; the holes
would then fall out under local checks. **This inverts the intuitive attack:**
the lever is the 74% already known, not the 26% unknown.

**The first restrictive grammar tested came back negative.** For every one of
the 82 drifts, the minimum alphabet width into which the determined plaintext
can be squeezed is **75 of 83** — flat against random. No drift collapses it.
A low-entropy inner payload (ASCII text, a small symbol set, a byte encoding of
letters-and-spaces) would have shown a collapse at the true drift. This is a
drift-free, independent confirmation of FR36/FR39 by an unrelated mechanism.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Generator/mapping choice | inferred from his source + habits (FR92, FR94) | **externally corroborated** — placement RNG is bit-identical, floor-map confirmed in the wild |
| Petri seeding transforms | sweep used raw integers | **formally subsumed**: any transform whose image lies in the swept range is irrelevant to an exhaustive sweep |
| Eye coordinates as anchors | untested candidate | **closed** — positions are seed-derived, carry no glyph identity |
| Plaintext as coordinate list | surviving Reading-C grammar | **closed** on mechanics (static payload, seed-varying positions) *and* statistics (clustering, range, count) |
| Undetermined-glyph geometry | "isolated, rarer" (FR54) | quantified: **longest all-undetermined run is 3** corpus-wide; no brute-able blank span exists |
| Base freedom | loosely "~8" | **35** (per message×component); backbone still over-determined 10:1 |
| Low-entropy inner payload | untested | **excluded** — minimum alphabet width 75/83 at every drift |

---

## 6. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean; exposure 74.1%;
alphabet [56, 83], floor 56 (FR97); drift unpinned. **Cumulative: 27.16 billion
candidates, zero survivors (FR99).** No sweep was run this cycle and none is
owed.

---

## 7. Horizon

1. **The surviving inner-layer grammars are index-streams and delimited
   records.** Both need a parameter — a table to index into, or a separator
   token — that the corpus cannot supply. Neither is attackable today.
2. **The glyph images remain the sole blocking resource**, and this cycle
   sharpens *why*: every surviving grammar's missing parameter is something the
   image assets would provide. Coordinates were the one candidate that seemed
   obtainable without them, and it is now closed.
3. **The success criterion** (FR82 §7). Unchanged and still dominant.
