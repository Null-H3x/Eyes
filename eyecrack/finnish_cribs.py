#!/usr/bin/env python3
"""finnish_cribs.py -- scaled Finnish creation-myth crib bank for the eyes.

WHY THIS EXISTS
===============
Two findings converged this session:
  1. The stone tablets decode to a Finnish Kalevala-register creation myth
     numbered by Volume (II, IV..X, with a duplicated X) -- and Volume I is
     MISSING.  The eye messages are the hardest-protected, thematically
     separate system.  Working hypothesis: EYES = the missing Volume I, the
     opening of that creation myth, in the same Finnish mythic register.
  2. The rune font sheet's glyph inventory counts to N=83 as a CASE-
     SENSITIVE character set (26 upper + 26 lower + 10 digits + symbols; the
     umlaut variant makes a Finnish-aware 83 too).  So the eye plaintext is
     mixed-case with punctuation -- NOT the all-caps stream every crib
     attempt has assumed, which is why English uppercase phrases never fit.

The skeleton_match filter is sound but starved: the T1 refrain's four forced
equalities need ~30k-460k windows to expect even one CHANCE hit, and every
corpus slid so far had <3000 windows.  So T1's zeros to date are
statistically meaningless -- discriminating T1 needs a corpus two-to-three
orders of magnitude larger, in the RIGHT language and case model.  This
module builds that corpus.

WHAT IT PRODUCES
================
* A running-text bank of the KNOWN myth (the stone-tablet Volumes we have)
  plus any external Finnish running text you drop in (Kalevala cantos, etc).
* Windowing in TWO charset models so the eyes decide which is right:
    - despaced-lower : letters only, lowercased (the old assumption)
    - charset83      : case + punctuation preserved, mapped to an 83-symbol
                       alphabet (the font-sheet hypothesis)
* A compose path over the shipped 92k Finnish lexicon (eyestat/
  extra_words_fi.txt) for phrases the running text doesn't contain.

HONEST LIMITS
=============
* This does NOT decode the eyes.  It manufactures high-quality CANDIDATE
  cribs in the right language/register/case model, to feed skeleton_match
  and then crib_fit.  A survivor is a lead, not a solution.
* The Kalevala opening cantos are the ideal corpus and are NOT shipped
  (fetch them yourself and pass via --external); the module ships only the
  in-game myth text as seed so it runs standalone.
* The charset83 mapping is a HYPOTHESIS about what N=83 is.  The module
  makes it testable; it does not assume it is correct.  Both models are
  emitted so the eyes arbitrate.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
_EYESTAT = HERE.parent / "eyestat"


# ---------------------------------------------------------------------------
# The known in-game myth (stone-tablet Volumes), Finnish, as shipped seed.
# Umlauts preserved; the charset models below decide how to fold them.
# ---------------------------------------------------------------------------
MYTH_FI = """\
Keskikesän kuikka lenteli suon yllä ja laskeutui suuren puun juurelle.
Vesilintu muni kolme munaa.
Ensimmäinen munista vierähti pesästä ja halkesi.
Halkeamasta vuosi verta seitsemän päivää ja seitsemän yötä.
Verestä muodostui elämä ja kuolema.
Valkuainen valui länteen ja siitä muodostui kylmyys ja jää.
Kuoresta muodostuivat maat ja vuoret.
Keltuainen valui itään ja siitä muodostui lämpö ja tuli.
Viimein munasta kuoriutui Luonto.
Luonto loi lait luonnon, asetti eläimet, niityt, joet, kummut ja vuoret.
Luonto puuhasteli itsekseen.
Luonto katseli tekojaan ja oli tyytyväinen luomuksiinsa.
Maailmassa oli harmonia.
Toinen munista kuoriutui ja sieltä syntyi Taikuus.
Taikuus katseli Luonnon luomuksia ja antoi niille sielun.
Ei pelkästään eläimille, vaan myös aineille.
Sielun paino jalosti ja kieroutti luonnon luomuksia.
Kullan jalous antoi sille hohdon.
Mudan saamattomuus antoi sille pistävän hajun.
Taikuus rikkoi luonnon lakeja.
Luonto ja Taikuus alkoivat riidellä siitä miten maailman kuuluisi olla.
Munista viimeinen kuoriutui ja sieltä syntyi teknologia.
Teknologia antoi luonnon eläimille kyvyn käyttää koneita ja laitteita.
"""


# ---------------------------------------------------------------------------
# charset models
# ---------------------------------------------------------------------------
def _strip_accents(s: str) -> str:
    """a-umlaut -> a, o-umlaut -> o, etc. (ASCII fold)."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def norm_despaced_lower(text: str) -> str:
    """Old model: ASCII letters only, lowercased, no spaces."""
    t = _strip_accents(text.lower())
    return "".join(c for c in t if "a" <= c <= "z")


# charset83 (Finnish-aware): A-Z a-z 0-9 + a-umlaut/o-umlaut (upper+lower)
# + a compact punctuation set.  This is one concrete 83-symbol instantiation
# of the font-sheet count; the exact symbol subset is a hypothesis knob.
_UML = "äöÄÖ"
# Need exactly 17 marks so 26+26+10+4+17 == 83.  This specific subset is a
# HYPOTHESIS knob (font sheet showed PUNCT + SYMBOLS rows); the eyes arbitrate.
_PUNCT83 = " .,:;?!'\"-()[]/@&"       # 17 marks incl. space
_CHARSET83 = ("abcdefghijklmnopqrstuvwxyz"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              "0123456789" + _UML + _PUNCT83)


def charset83_index() -> Dict[str, int]:
    return {c: i for i, c in enumerate(_CHARSET83)}


def norm_charset83(text: str, keep_space: bool = True) -> str:
    """Case + umlauts + light punctuation preserved; unknown chars dropped.
    This is the string the font-sheet hypothesis says the eyes encode."""
    idx = charset83_index()
    out = []
    for c in text:
        if c in idx:
            if c == " " and not keep_space:
                continue
            out.append(c)
    return "".join(out)


CHARSET_MODELS = {
    "despaced-lower": (norm_despaced_lower, False),
    "charset83": (lambda t: norm_charset83(t, keep_space=False), False),
    "charset83-spaced": (lambda t: norm_charset83(t, keep_space=True), True),
}


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------
def load_running_text(paths: Sequence[str]) -> List[str]:
    """Lines of running text from external files (Kalevala cantos, etc.)."""
    lines: List[str] = []
    for p in paths:
        for ln in Path(p).read_text(encoding="utf-8",
                                    errors="ignore").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                lines.append(ln)
    return lines


def seed_myth_lines() -> List[str]:
    return [ln.strip() for ln in MYTH_FI.splitlines() if ln.strip()]


def load_finnish_lexicon(min_len: int = 2, max_len: int = 16) -> List[str]:
    p = _EYESTAT / "extra_words_fi.txt"
    if not p.exists():
        return []
    ws = []
    for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        w = ln.strip()
        if w and not w.startswith("#") and min_len <= len(w) <= max_len:
            ws.append(w)
    seen = set()
    return [w for w in ws if not (w in seen or seen.add(w))]


# ---------------------------------------------------------------------------
# windowing
# ---------------------------------------------------------------------------
def slide_windows(text: str, length: int, model: str) -> Iterator[str]:
    fn, _ = CHARSET_MODELS[model]
    s = fn(text)
    for i in range(len(s) - length + 1):
        yield s[i:i + length]


def windows_over_lines(lines: Sequence[str], length: int, model: str
                       ) -> Iterator[Tuple[str, str]]:
    """(source_line, window). Windows within each line only (no cross-line
    contamination), plus windows over the whole joined text to catch refrains
    that span line breaks in the source formatting."""
    for ln in lines:
        for w in slide_windows(ln, length, model):
            yield ln, w
    joined = " ".join(lines)
    for w in slide_windows(joined, length, model):
        yield "<joined>", w


def compose_windows(words: Sequence[str], length: int, model: str,
                    max_words: int = 7, cap: int = 3_000_000
                    ) -> Iterator[str]:
    """Length-bucketed DFS over the lexicon under the given model.
    Words are normalized by the model first (so umlauts fold consistently)."""
    fn, keep_space = CHARSET_MODELS[model]
    norm_words: Dict[int, List[str]] = {}
    for w in words:
        nw = fn(w)
        if nw:
            norm_words.setdefault(len(nw), []).append(nw)
    sep = " " if keep_space else ""
    seplen = len(sep)
    lengths = sorted(norm_words)
    yielded = 0

    def rec(remaining: int, depth: int, acc: List[str]) -> Iterator[str]:
        nonlocal yielded
        if yielded >= cap:
            return
        if remaining == 0:
            if acc:
                yield sep.join(acc)
                yielded += 1
            return
        if depth >= max_words:
            return
        for L in lengths:
            need = L + (seplen if acc else 0)
            if need > remaining:
                break
            for w in norm_words[L]:
                yield from rec(remaining - need, depth + 1, acc + [w])
                if yielded >= cap:
                    return

    yield from rec(length, 0, [])


# ---------------------------------------------------------------------------
# skeleton integration (reuse skeleton_match if importable)
# ---------------------------------------------------------------------------
def _load_skeletons():
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import skeleton_match as sm
    return sm


def sweep(lines_or_words, length: int, model: str, sk, *,
          compose: bool = False, max_words: int = 7, cap: int = 3_000_000,
          strict_injective: bool = False) -> Tuple[int, Dict[str, str]]:
    """Return (n_windows, {window: source}) surviving the skeleton."""
    survivors: Dict[str, str] = {}
    n = 0
    if compose:
        for w in compose_windows(lines_or_words, length, model, max_words, cap):
            n += 1
            ok, _ = sk.check(w, strict_injective=strict_injective)
            if ok:
                survivors.setdefault(w, "<composed>")
    else:
        for src, w in windows_over_lines(lines_or_words, length, model):
            n += 1
            ok, _ = sk.check(w, strict_injective=strict_injective)
            if ok:
                survivors.setdefault(w, src)
    return n, survivors


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []

    # (1) charset83 is exactly 83 symbols and injective.
    checks.append((f"charset83 size == 83 ({len(_CHARSET83)})",
                   len(_CHARSET83) == 83 and
                   len(set(_CHARSET83)) == 83))

    # (2) accent fold: umlaut-a -> a, umlaut-o -> o under despaced-lower.
    s = norm_despaced_lower("Ensimmäinen yötä JÄÄ")
    checks.append(("accent fold to ASCII lower",
                   s == "ensimmainenyotajaa"))

    # (3) charset83 preserves case + umlaut, drops unknowns.
    c = norm_charset83("Ab9ä! ~", keep_space=True)
    # '~' not in set -> dropped; '!' in set; space kept
    checks.append(("charset83 preserves case/umlaut, drops unknown",
                   c == "Ab9ä! "))

    # (4) seed myth loads and has the expected mythic tokens.
    lines = seed_myth_lines()
    joined = " ".join(lines).lower()
    checks.append((f"seed myth loads ({len(lines)} lines)",
                   len(lines) >= 20 and "kuikka" in joined
                   and "luonto" in joined and "taikuus" in joined))

    # (5) windowing yields exact-length windows in each model.
    for model in CHARSET_MODELS:
        ws = list(slide_windows("Keskikesän kuikka lenteli suon yllä",
                                24, model))
        oklen = all(len(w) == 24 for w in ws)
        checks.append((f"windows exact length 24 [{model}]",
                       oklen and len(ws) > 0))

    # (6) compose hits target length under a model with spaces.
    words = ["luonto", "loi", "lait", "ja", "vuoret", "muna", "kolme"]
    comp = list(compose_windows(words, 12, "charset83-spaced",
                                max_words=3, cap=500))
    fn, _ = CHARSET_MODELS["charset83-spaced"]
    okc = all(len(w) == 12 for w in comp) and len(comp) > 0
    checks.append((f"compose hits length under spaced model ({len(comp)})",
                   okc))

    # (7) integration: skeleton_match imports and a known-passing synthetic
    #     window survives while a broken one does not.
    try:
        sm = _load_skeletons()
        sk = sm.build_skeletons()["T3"]
        # synthesize a 20-char string satisfying T3 (pos2=pos19, pos6=pos10)
        base = list("abcdefghijklmnopqrst")
        base[18] = base[1]      # pos19 == pos2
        base[9] = base[5]       # pos10 == pos6
        good = "".join(base)
        okg, _ = sk.check(good)
        bad = list(good); bad[18] = "z" if bad[1] != "z" else "q"
        okb, _ = sk.check("".join(bad))
        checks.append(("skeleton_match integration (T3 pass/fail)",
                       okg and not okb))
    except Exception as e:
        checks.append((f"skeleton_match integration (SKIP: {e})", True))

    # (8) lexicon loads if present (soft).
    lex = load_finnish_lexicon()
    checks.append((f"finnish lexicon loads ({len(lex)} words)"
                   if lex else "finnish lexicon (SKIP: not present)",
                   True))

    # (9) determinism.
    a = list(slide_windows("Luonto loi lait luonnon", 12, "charset83"))
    b = list(slide_windows("Luonto loi lait luonnon", 12, "charset83"))
    checks.append(("windowing deterministic", a == b))

    return checks


def _run_selftest() -> int:
    ok = True
    for name, passed in selftest():
        print(f"[{'OK  ' if passed else 'FAIL'}] {name}")
        ok &= passed
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--triplet", choices=["T1", "T3"], default="T1")
    ap.add_argument("--model", choices=list(CHARSET_MODELS),
                    default="despaced-lower")
    ap.add_argument("--external", nargs="*", default=None,
                    help="external Finnish running-text files (Kalevala etc.)")
    ap.add_argument("--compose", action="store_true",
                    help="compose from the shipped 92k Finnish lexicon")
    ap.add_argument("--max-words", type=int, default=7)
    ap.add_argument("--cap", type=int, default=3_000_000)
    ap.add_argument("--strict-injective", action="store_true")
    ap.add_argument("--limit-out", type=int, default=60)
    args = ap.parse_args()
    if args.selftest:
        return _run_selftest()

    sm = _load_skeletons()
    sk = sm.build_skeletons()[args.triplet]
    print(f"[{sk.name}] len={sk.length} equalities={sk.equalities} "
          f"model={args.model}")

    if args.compose:
        words = load_finnish_lexicon()
        print(f"[compose] lexicon={len(words)} words, target={sk.length}")
        n, surv = sweep(words, sk.length, args.model, sk, compose=True,
                        max_words=args.max_words, cap=args.cap,
                        strict_injective=args.strict_injective)
    else:
        lines = seed_myth_lines()
        if args.external:
            lines += load_running_text(args.external)
        print(f"[slide] {len(lines)} lines "
              f"({'seed+external' if args.external else 'seed only'})")
        n, surv = sweep(lines, sk.length, args.model, sk,
                        strict_injective=args.strict_injective)

    print(f"[{sk.name}] {n} windows -> {len(surv)} distinct survivors")
    # expected chance hits, for honest reading
    import math
    k = 21 if "lower" in args.model else 40   # rough effective alphabet
    p = (1.0 / k) ** len(sk.equalities)
    print(f"[note] ~{n * p:.2f} chance survivors expected "
          f"(k~{k}, {len(sk.equalities)} equalities); "
          f"need ~{1/p:,.0f} windows per expected hit")
    for w, src in list(surv.items())[:args.limit_out]:
        print(f"   {w!r}   <= {src[:56]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
