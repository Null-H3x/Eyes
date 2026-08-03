# Field Report 8 — No Grade Below the Pins

**Series note.** Eighth report of the iterative series. This cycle tested a
hypothesis I entered in good faith and then refuted: that a *certified-difference*
grade sits below FR7's absolute pins, cheaply linking the FR5 battery glyphs.
Instrument `eyecluster.py`, selftest 5/5 green, built entirely on the repo's
trusted gauge-invariance primitive after three unsound oracles were caught and
discarded.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
results conditional on the static additive family under the FR7 sound-rows reading.

**One-paragraph verdict.** There is **no relational grade below the absolute pins**.
A difference x[b] − x[a] is certified only if it is invariant under every gauge
freedom — the global rotation *and* each free per-message base — and on the corpus
**all 41 non-pin symbols provably move under a gauge shift**, so the
certified-difference set equals the 10-symbol absolute-pin domain exactly. The pins
already are the complete sound relational inventory; nothing is hiding beneath them.
The three tempting shortcuts (Gaussian reduction, `classify`, reference-only gauge
shifts) all *appear* to find a larger grade and are all unsound — they pivot through
base-lead rows or leave per-message bases fixed, fabricating cross-message
certifications (the naive oracle falsely reports 49 of 51 symbols linked; 7/44
truth-exact on the audit plant). That failure mode is now a permanent negative gate.
The cycle's real yield is the **letter-collision census**: the map of the only sound
growth lever FR7 named. It shows glyph 47 — H1's target — occurring at letter cells
in **seven** atlas classes yet staying gauge-free because every occurrence is the
same handful of refrain tokens, never anchored to the pin component; and it hands
over, per battery glyph, the exact class where a new cross-context anchor would pin
it. Four of the thirteen hypothesis glyphs (1, 27, 76, 77, 80, 33) have **no** letter
collision at all and are unreachable by this route.

---

## 1. Corrections and negatives first

**The hypothesis was wrong, and three oracles were unsound before I found the
sound one.** This is the cycle's substance, so I record the full arc. (i) Gaussian
reduction of the difference row against the GF pivots pivots through base-lead rows,
silently substituting the gauge-0 base values — 7/44 truth-exact on the plant, a
fabrication. (ii) The repo's `classify` shares the same reduction and the same leak.
(iii) A gauge oracle that shifts only the reference symbol leaves every per-message
base pinned at 0, so within-message differences look spuriously constant — 9/191
truth-exact, worse. Only the full gauge test — perturb the reference *and* prove
non-pin symbols move — is sound, and it is exactly the principle `certified_domain`
already uses. The lesson, now a standing gate: **any difference oracle that consults
`solve()` or `classify()` output at face value inherits the base-gauge leak; sound
difference facts come only from gauge-invariance.**

**No pin growth this cycle.** The instrument certifies nothing new about the corpus's
values; it proves a limit and maps a route. That is the honest deliverable.

**What is unaffected.** Every prior structural result (FR3 drift equality, FR4
one-gauge, FR6 epistemology, FR7 sound tier and the surviving q[49]−q[13]≡2) rests on
the same gauge-invariant footing this cycle validates, and none is touched.

## 2. The collapse, stated cleanly

Under the per-message-progressive model the solver carries one free base variable per
message plus the global rotation. A cross-message difference is a linear form over
symbol *and* base variables; it is a fact about the plaintext only if the base
variables cancel — which requires the two symbols to sit at matched base signatures
*and* be constant-linked, i.e. already in one gauge-invariant component. The
gauge-invariance test decides this directly: pin the reference to two values; a
symbol whose offset to the reference changes is gauge-free. **Corpus result: 41/41
non-pin symbols move; the 10 pins are mutually invariant.** Therefore the
certified-difference graph is the single 10-clique on the pins and 41 isolated
vertices — no intermediate structure exists. The selftest proves both halves on the
audit plant (pins invariant, every non-pin moves) and exhibits the naive oracle's
falsehood in the same breath.

## 3. The letter-collision census — the growth map

FR7 named cross-context letter-cell collisions as the determination engine. The
census enumerates them: **37 distinct symbols occur at letter cells in two or more
atlas classes.** Yet the sound domain is only 10, because a collision pins a symbol
*only if it chains to the gauge-anchored component* — and the refrain's most repeated
symbols form a closed island of their own. Glyph 47 is the emblem: it plays #M's
A-letter, #F's C-letter, #1/#C1's B-letter, and roles in #3/#3+/#M⁻ — **seven
classes, six distinct cells** — but every one of those cells is inside the E1/W1/E2
near-dup refrain, so 47 links richly to *other refrain symbols* and never to a pin.
The census therefore doubles as a diagnosis of the bootstrap wall: the corpus's
repetition is concentrated where it cannot anchor.

Per battery glyph, the reachability verdict:

| glyph | role | letter-collides in | status |
|---|---|---|---|
| 47 (H1) | refrain A/B/C | #1 #F #M #C1 #M⁻ #3 #3+ | free; needs a pin inside one of these classes |
| 66 (H3) | #2-family | #2 #2+ #2⁻ | free; #2⁻ is cross-triplet (T2↔T3) |
| 5 (H3) | #2-family/#C0 | #2 #2+ #C0 | free |
| 36, 34, 50, 63 (H2) | various | 1–3 classes each | free; partial indicator reach |
| 1 (H1), 27, 76, 77, 80, 33 (H2) | — | none | **unreachable by letter collision** |

The actionable reading: **H1 is reachable, H3 is reachable, H2 is not** (six of nine
indicators never letter-collide). To pin glyph 47, the campaign needs a certified
anchor *inside* one of its seven classes — the sound-rows tier already keeps all
their pairs, so the missing ingredient is a symbol in one of those classes that is
independently gauge-anchored. #F is the best candidate: it already contains pinned
glyph 19 (role B), so the question is sharply posed — does the sound system certify
47's offset to 19, and if not, what single additional constraint would? (It does not,
by §2; 47 and 19 are constant-linked *within #F's gauge* but #F's gauge floats
relative to the reference. The anchor must come from outside #F.)

## 4. Consequences for doctrine

The 16-pin wall's mechanism, already named in FR6/FR7, gains its final piece:
**growth is gauge-anchoring-limited, not evidence-limited.** The corpus has 37
cross-context letter symbols and 65 self-consistent atlas pairs, yet only 10 pins,
because the constraint graph — though rich — has its dense component (the refrain)
detached from the global gauge. Any successful reach must connect the refrain island
to the reference component; more atlas pairs within the island will not do it. This
reframes P1 and the pin campaign: the target is a *bridging* constraint (a symbol
shared between the refrain classes and a pinned class at a letter cell), and the
census lists every candidate symbol and cell.

## 5. Horizon

(1) **Bridge-symbol search:** enumerate symbols that appear at a letter cell in both
a refrain class (#1/#F/#M/#C1) and a pinned-containing class elsewhere — the minimal
anchor that would grow the domain and, via §3, flip H1. (2) **External-anchor
readiness:** the R6 pipeline (six external pins → convergence) is the doctrine's
other route past the wall; the census says which six glyphs would most enlarge the
domain if supplied externally (the seven-class hub 47 first). (3) **The stem-reading
stress rail** stands. (4) The battery stays frozen and now has a per-glyph reach
map instead of a flat UNCHECKABLE. Standing items unchanged.

## 6. Reproduction

`eyecluster.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest`
for the 5-check gate (sound-oracle exactness, the collapse both halves, the
documented naive-oracle failure, census smoke); full run reproduces the baseline
guard, the 41/41 gauge-motion collapse, the naive-oracle mirage count, and the full
letter-collision census with per-glyph reach. All failures carry prefix
`XD-MBYG04K-URS3LF`. The collapse is checkable by hand from any two gauge solves; the
census is a direct read of the atlas letter cells against the corpus.
