# Eye Corpus — Field Map (mechanism-invariant record layout)

**Tier 1** = fact (identical ciphertext). **Tier 2** = field layout: an equality run forces a
CONSTANT plaintext difference over the run under *every* surviving family, certifying a coherent
field. Within a triplet the relation is EQUAL (FG4 Δbase=0); across triplets it is CONSTANT-SHIFT
(magnitude = the untested cross-triplet base delta). **Tier 3** (values, shift magnitudes) needs C
and is withheld. *Label caveat:* equal/shift inherits the base-cluster model; the layout and the
constant-Δp constraint are invariant regardless.

Corpus N=83; lengths [99, 103, 118, 102, 137, 124, 119, 120, 114]. Triplets T1={East 1, West 1, East 2}, T2={West 2, East 3, West 3}, T3={East 4, West 4, East 5}.

## Structural highlights

- **pos 0**: all 9 messages distinct → per-message indicator (sets base_m).
- **pos 1–2: identical ciphertext across ALL 9 messages.** A fixed record marker. Invariant
  consequence (holds for every surviving family): each message's pos-1–2 plaintext is a fixed
  function of that message's base/indicator — i.e. a **base-canceling header** producing a
  constant ciphertext. This is a strong structured-record signal *and* a recognition anchor.
  It forces a fork: either all bases are equal at the body (contradicting per-message bases),
  or the header plaintext varies to cancel a varying base (a header↔indicator link). Worth
  resolving — it is the master alignment point across all three triplets.
- **Near-duplicate pairs**: {East 1, West 1} share 44 identical positions; {East 4, East 5} share 31. These are the tightest depth pairs.
- **Record skeleton**: [pos 0 indicator] · [pos 1–2 universal header] · [pos 3+ triplet-branching body].

## Record grammar (fields, left to right)

- **pos 1–2** (len 2): [{East 1, West 1, East 2, West 2, East 3, West 3, East 4, West 4, East 5}: EQUAL {East 1,West 1,East 2} {West 2,East 3,West 3} {East 4,West 4,East 5}; SHIFT across (certified)]
- **pos 3–5** (len 3): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (certified)] [{West 2, East 3, West 3, East 4, West 4, East 5}: EQUAL {West 2,East 3,West 3} {East 4,West 4,East 5}; SHIFT across (certified)]
- **pos 6–9** (len 4): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (certified)] [{East 3, East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5}; SHIFT across (certified)]
- **pos 10** (len 1): [{East 1, West 1, East 2, West 2}: EQUAL {East 1,West 1,East 2}; SHIFT across (p=2e-06)] [{East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5} (p=1e-04)]
- **pos 11–12** (len 2): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (certified)] [{East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5} (certified)]
- **pos 13** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)] [{West 2, West 3}: EQUAL {West 2,West 3} (p=1e-02)] [{East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5} (p=1e-04)]
- **pos 14** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)] [{East 3, West 3}: EQUAL {East 3,West 3} (p=1e-02)] [{East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5} (p=1e-04)]
- **pos 15–19** (len 5): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (certified)] [{East 4, West 4, East 5}: EQUAL {East 4,West 4,East 5} (certified)]
- **pos 20** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)] [{West 2, East 3, East 4, West 4, East 5}: EQUAL {West 2,East 3} {East 4,West 4,East 5}; SHIFT across (certified)]
- **pos 21** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)]
- **pos 22** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)] [{West 2, West 4, East 5}: EQUAL {West 4,East 5}; SHIFT across (p=1e-04)]
- **pos 23** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)]
- **pos 24** (len 1): [{East 1, West 1, East 2, East 4, West 4}: EQUAL {East 1,West 1,East 2} {East 4,West 4}; SHIFT across (certified)]
- **pos 25** (len 1): [{West 3, East 4, East 5}: EQUAL {East 4,East 5}; SHIFT across (p=1e-04)]
- **pos 26–27** (len 2): [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-04)]
- **pos 29** (len 1): [{East 1, West 1, West 3}: EQUAL {East 1,West 1}; SHIFT across (p=1e-04)] [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-02)]
- **pos 30** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-02)]
- **pos 31** (len 1): [{East 1, West 1, West 4}: EQUAL {East 1,West 1}; SHIFT across (p=1e-04)] [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-02)]
- **pos 32** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)]
- **pos 33** (len 1): [{West 2, West 3}: EQUAL {West 2,West 3} (p=1e-02)]
- **pos 35** (len 1): [{West 1, East 4, East 5}: EQUAL {East 4,East 5}; SHIFT across (p=1e-04)]
- **pos 37** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)]
- **pos 38** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{East 3, East 4, East 5}: EQUAL {East 4,East 5}; SHIFT across (p=1e-04)]
- **pos 39–40** (len 2): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-04)] [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-04)]
- **pos 41** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{East 2, East 4}: SHIFT across (p=1e-02)]
- **pos 42** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{East 2, West 3}: SHIFT across (p=1e-02)] [{East 4, East 5}: EQUAL {East 4,East 5} (p=1e-02)]
- **pos 43–45** (len 3): [{East 1, West 1}: EQUAL {East 1,West 1} (p=2e-06)]
- **pos 46** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)]
- **pos 47–48** (len 2): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-04)]
- **pos 49** (len 1): [{East 1, West 1, East 2}: EQUAL {East 1,West 1,East 2} (p=1e-04)]
- **pos 52** (len 1): [{East 3, East 4}: SHIFT across (p=1e-02)]
- **pos 55** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{West 4, East 5}: EQUAL {West 4,East 5} (p=1e-02)]
- **pos 56** (len 1): [{West 1, East 4}: SHIFT across (p=1e-02)]
- **pos 58** (len 1): [{West 4, East 5}: EQUAL {West 4,East 5} (p=1e-02)]
- **pos 59** (len 1): [{East 1, West 2}: SHIFT across (p=1e-02)]
- **pos 61** (len 1): [{East 3, West 4}: SHIFT across (p=1e-02)]
- **pos 63** (len 1): [{East 3, West 3}: EQUAL {East 3,West 3} (p=1e-02)] [{East 4, West 4}: EQUAL {East 4,West 4} (p=1e-02)]
- **pos 64** (len 1): [{West 4, East 5}: EQUAL {West 4,East 5} (p=1e-02)]
- **pos 66** (len 1): [{East 2, East 5}: SHIFT across (p=1e-02)]
- **pos 68** (len 1): [{West 2, West 3}: EQUAL {West 2,West 3} (p=1e-02)]
- **pos 70** (len 1): [{East 2, West 3}: SHIFT across (p=1e-02)]
- **pos 71** (len 1): [{East 1, East 4}: SHIFT across (p=1e-02)]
- **pos 72** (len 1): [{West 4, East 5}: EQUAL {West 4,East 5} (p=1e-02)]
- **pos 73** (len 1): [{West 2, East 5}: SHIFT across (p=1e-02)]
- **pos 74** (len 1): [{East 1, West 4}: SHIFT across (p=1e-02)]
- **pos 81** (len 1): [{East 1, East 2}: EQUAL {East 1,East 2} (p=1e-02)]
- **pos 82** (len 1): [{West 1, East 2}: EQUAL {West 1,East 2} (p=1e-02)]
- **pos 84** (len 1): [{West 1, East 5}: SHIFT across (p=1e-02)] [{West 3, East 4}: SHIFT across (p=1e-02)]
- **pos 86** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)] [{East 2, East 3}: SHIFT across (p=1e-02)]
- **pos 88** (len 1): [{West 3, West 4}: SHIFT across (p=1e-02)]
- **pos 94** (len 1): [{East 2, East 4}: SHIFT across (p=1e-02)]
- **pos 97** (len 1): [{East 1, West 1}: EQUAL {East 1,West 1} (p=1e-02)]
- **pos 101** (len 1): [{West 3, East 5}: SHIFT across (p=1e-02)]
- **pos 107** (len 1): [{West 3, East 4}: SHIFT across (p=1e-02)]
- **pos 110** (len 1): [{East 2, East 4}: SHIFT across (p=1e-02)] [{East 3, East 5}: SHIFT across (p=1e-02)]
- **pos 111** (len 1): [{West 4, East 5}: EQUAL {West 4,East 5} (p=1e-02)]

## Bridge targets — cross-triplet constant-shift runs (align the corpus)

Measuring the shift on any of these pins a cross-triplet base delta (Priority 1). The pos 1–2
marker is the strongest (spans all three triplets) but its identical-ciphertext form needs the
base fork resolved to read as a shift.

- pos 1–2 (len 2): {East 1, West 1, East 2, West 2, East 3, West 3, East 4, West 4, East 5} — shift UNKNOWN
- pos 3–5 (len 3): {West 2, East 3, West 3, East 4, West 4, East 5} — shift UNKNOWN
- pos 6–9 (len 4): {East 3, East 4, West 4, East 5} — shift UNKNOWN

## Phylogeny (pairwise identical-position count)

- East 1 ↔ West 1: 44
- East 4 ↔ East 5: 31
- East 1 ↔ East 2: 27
- West 1 ↔ East 2: 27
- West 4 ↔ East 5: 26
- East 4 ↔ West 4: 22
- East 3 ↔ East 4: 12
- East 3 ↔ East 5: 12
- East 3 ↔ West 4: 11
- West 2 ↔ West 3: 8

## Downstream uses

1. **Recognition template** — a correct C must reproduce this layout on decrypt (language-free).
2. **C-constraints** — each equality run is a constant-Δp relation any (C, mode) must satisfy.
3. **Bridge** — the cross-triplet runs are where one measured shift merges the depth stack.