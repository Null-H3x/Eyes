# Field Report 174 — THE ASSETS VERIFIED FIRST-HAND: FIVE PUPIL POSITIONS, NO HIDDEN CHANNEL

*Source: WUOTE noita-builds-data, build 2326595580679356504. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Why re-verify

FR101 closed base-5 on the sprite assets and that finding underpins everything —
the modulus, the trigram reading, the 83-value alphabet. It had never been
checked against the assets directly in this series; it was inherited.

The build data is now reachable via `raw.githubusercontent.com`.

---

## 1. The sprite count

```
eye_01.png  HTTP 200  270 bytes      eye_06.png  404
eye_02.png  HTTP 200  273 bytes      eye_07.png  404
eye_03.png  HTTP 200  272 bytes      eye_08.png  404
eye_04.png  HTTP 200  265 bytes      eye_09.png  404
eye_05.png  HTTP 200  269 bytes
```

**Exactly five sprites, 9 × 5 pixels each.** FR101 confirmed on both counts,
first-hand.

---

## 2. The symbol set, read straight off the pixels

Each sprite has **two** luminance-211 pixels. One is always an edge pixel,
(0,2) or (8,2) — a specular glint. The other is the pupil:

```
eye_01  pupil (4,2) = CENTRE   glint (8,2)
eye_02  pupil (4,3) = DOWN     glint (8,2)
eye_03  pupil (4,1) = UP       glint (0,2)
eye_04  pupil (3,2) = LEFT     glint (0,2)
eye_05  pupil (5,2) = RIGHT    glint (8,2)
```

> **Five pupil positions: centre, up, down, left, right.** That is the base-5
> symbol set, visible in the raw pixel data.

The glint side is fully determined by which way the pupil looks, so it carries
no independent information.

---

## 3. No hidden channel

```
pixels identical across all five : 4 of 45
pixels that vary                 : 41
distinct whole-sprite states     : 5 of 5
```

Forty-one pixels vary, but they take **exactly five joint states**. No sprite
duplicates another and no sixth state hides in the variation.

**FR101's closure of the hidden-rendering-channel family is confirmed
independently**, and now from the pixels rather than from an argument.

---

## 4. Correction to FR101

FR101 recorded *"one luminance-211 pupil per sprite."* There are **two**
211-pixels — pupil plus glint. The detail was wrong; the **conclusion is
unaffected**, since the glint is positionally determined by the pupil.

Worth logging because FR101 is cited for the base-5 foundation in six shipped
documents, and its supporting detail should be right.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Five sprites | inherited from FR101 | **verified first-hand** — eye_06+ return 404 |
| 9×5 dimensions | inherited | **verified** |
| The five symbols | "five orientations" | **centre, up, down, left, right** — pupil position |
| "one 211 pupil per sprite" | FR101 | **two 211-pixels** — pupil + glint; conclusion unaffected |
| Hidden rendering channel | closed by argument | **closed by pixel inspection** — 41 varying pixels, 5 joint states |

---

## 6. Model status

Unchanged and now founded on first-hand asset verification: 794 relations, 61
glyphs, 79.1% exposure, 435-position reading, 68 maximal readings, two invariant
cores, stamped header forced, plaintext inventory 83 with a uniform
distribution. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

The base-5 foundation is now verified from three independent directions:

1. **the assets** — five sprites, five pupil positions (this report)
2. **the engine** — base-7 storage with 0=padding, 1–5=symbols, 6=newline
   (community decompilation)
3. **the corpus** — 3,108 base-5 digits = 1,036 × 3, per-digit counts matching

Nothing about the foundation remains open. What remains is unchanged: 68
readings × 82 drifts × 83⁴ bases, with no oracle available because the inner
layer's distribution is uniform.
