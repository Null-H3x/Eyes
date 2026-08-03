# Field Report 151 — ISOMORPH DOES NOT IMPLY SHARED PASSAGE: 23% OF STRONG CLASSES CANNOT BE CO-PLAINTEXT

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I on the nominated test

FR150 proposed testing whether T1's stamped-header region extends past position
24, which would explain all thirty body contradictions at once. **Extending a
boundary until contradictions vanish is fitting, not testing.** The honest
version checks the *shape* first: a header is a **prefix**, so header-explicable
contradictions must be contiguous from position 0.

```
East 1   positions 32-86   runs [(32,86)]
West 1   positions 32-79   runs [(32,49), (60,79)]
East 2   positions 37-89   runs [(37,54), (65,89)]
East 3   positions 93-108  runs [(93,108)]
```

**The header explanation is dead, twice over.** East 3's contradictions sit at
93–108, nowhere near an opening and in a triplet whose opening the doctrine
never called literal. And East 1 would need 55 of its 99 positions declared
stamped — that is not a header, that is most of the message.

---

## 1. The contradiction is irreducible

Taking the strongest body contradiction (L=18, six instances, surprise 3.59)
and applying FR25's minimal-core method:

```
removing one POOL pair at a time  : NONE clears it
removing one ADDED class at a time: NONE clears it
```

No single element is responsible. The conflict is distributed.

---

## 2. What that exposes

The model treats a certified isomorph class as **co-plaintext**: same equality
pattern implies same underlying text. **That implication has never been
examined.** It is the premise the entire skeleton rests on.

The corpus's 208 strong classes divide:

```
 13  atlas          -> assumed co-plaintext
 19  informative    -> consistent, adopted FR146
128  redundant      -> consistent, add nothing
 48  CONTRADICTORY  -> cannot be co-plaintext

consistent : 160/208 = 77%
NOT        :  48/208 = 23%
```

> **If "isomorph implies shared passage" were true, all 208 would be consistent.
> Twenty-three percent are not. The implication is false: a strong isomorph can
> arise without the two windows sharing plaintext.**

At k=3 the expected chance instance count is 0.002 corpus-wide, and several of
the contradicting classes carry six instances. They are not coincidences. They
are real repeated *structures* that are not repeated *text*.

---

## 3. What this does and does not do to the model

**It does not make the skeleton wrong.** 794 relations over 160
mutually-consistent classes, with 100% out-of-sample mutual prediction against a
2.8% control (FR146), remains strong evidence that those 160 cohere.

**It does weaken how that evidence should be read.** The classes fed to the
model are those that happen to be consistent with it — partly a **consistency
filter**, not purely an evidential selection. FR146's prediction test was run
only on classes already known to cohere, so it demonstrates mutual coherence
rather than validating the co-plaintext premise itself.

**The honest statement:** the model is a maximal mutually-consistent set of
isomorph classes, and it is a very good one. It is not "the classes that are
shared passages," because the corpus contains strong isomorphs that demonstrably
are not.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Stamped-header extension | proposed explanation (FR150) | **REFUTED** — East 3 at 93–108; East 1 would need 55/99 positions |
| The 30 body contradictions | unexplained | **irreducible** — no single removal clears them |
| **Isomorph implies co-plaintext** | **unexamined premise** | **FALSE** — 23% of strong classes cannot be co-plaintext |
| Class selection | evidential | **partly a consistency filter** |
| FR146's mutual prediction | validates the classes | **validates mutual coherence**, not the premise |

---

## 5. Model status

Content unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 0 conflicts, 6 anchors. **Its standing is now more
precisely described: a maximal mutually-consistent set of 160 isomorph classes,
not a set of verified shared passages.** Cumulative: 27.16 billion candidates,
zero survivors.

---

## 6. Horizon

1. **Is there a rival maximal-consistent set?** The 48 excluded classes may
   themselves cohere around a *different* skeleton. If a second maximal set
   exists with comparable size, the model has a rival it has never seen. If not,
   the current one is the unique maximum and that is a much stronger statement
   than it can currently make.
2. **That test is the natural completion of this line** and needs no external
   evidence.
3. **Artifact rebuild stays deferred** until item 1 resolves.
