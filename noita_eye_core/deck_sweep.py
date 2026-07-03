"""Score 26- / 52-letter deck orderings embedded in the N=83 eye alphabet.

Tests candidate plaintext-alphabet layouts under:
  - wiki header crib (``deck[66]='.'``, ``deck[5]=' '`` in symbol mode)
  - numbered-list pos-0 digit mapping
  - refrain template + optional anchor phrases
  - ``refrain.attack`` pin / IoC (when phrases map)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import alphabet_cut as ac
import refrain as rf
import template as tp


DEFAULT_ANCHORS: Tuple[str, ...] = ("god", "see", "eye", "godseeye")
DEFAULT_POS0 = (27, 33, 34, 36, 50, 63, 76, 77, 80)


@dataclass
class DeckScore:
    name: str
    variant: str
    deck: str
    letters_26: str
    wiki_symbol_ok: bool
    header_digits_ok: bool
    header_digits: str
    template_ok: bool
    anchors: Dict[str, bool] = field(default_factory=dict)
    refrain_ok: Dict[str, bool] = field(default_factory=dict)
    refrain_pinned: Dict[str, int] = field(default_factory=dict)
    total_score: float = 0.0
    notes: List[str] = field(default_factory=list)


def _score_phrase(
    messages,
    deck: str,
    phrase: str,
    instances,
    L: int,
    N: int,
) -> Tuple[bool, bool, int]:
    """Return (maps, template_ok, symbols_pinned)."""
    pv = ac.letter_values(phrase.lower(), deck, N)
    if pv is None:
        pv = ac.letter_values(phrase.upper(), deck, N)
    if pv is None:
        return False, False, 0
    tmpl_ok = tp.fits(messages, instances, L, phrase.lower(), N)
    atk = rf.attack(messages, pv, N, instances=instances)
    return True, tmpl_ok, atk.symbols_pinned if atk.consistent else 0


def score_deck(
    name: str,
    deck: str,
    messages,
    *,
    variant: str = "26",
    letters_26: str = "",
    instances=None,
    L: int = rf.DEFAULT_LEN,
    N: int = 83,
    anchors: Sequence[str] = DEFAULT_ANCHORS,
    pos0_symbols: Sequence[int] = DEFAULT_POS0,
    wiki_mode: str = "symbol",
) -> DeckScore:
    if instances is None:
        instances = rf.DEFAULT_INSTANCES

    wiki_symbol_ok = (
        wiki_mode == "off"
        or (len(deck) > 66 and deck[66] == "."
            and (variant == "52" or deck[5] == " "))
    )
    hdr_ok, hdr_digits = ac.header_pos0_digits(deck, pos0_symbols)

    tmpl = tp.extract(messages, instances, L, N)
    template_ok = tmpl.consistent

    ds = DeckScore(
        name=name,
        variant=variant,
        deck=deck,
        letters_26=letters_26 or deck[:26],
        wiki_symbol_ok=wiki_symbol_ok,
        header_digits_ok=hdr_ok,
        header_digits=hdr_digits,
        template_ok=template_ok,
    )

    score = 0.0
    if wiki_symbol_ok:
        score += 2.0
    if hdr_ok:
        score += 3.0
    if template_ok:
        score += 1.0

    for phrase in anchors:
        maps, t_ok, pinned = _score_phrase(messages, deck, phrase, instances, L, N)
        ds.anchors[phrase] = maps
        ds.refrain_ok[phrase] = t_ok
        ds.refrain_pinned[phrase] = pinned
        if maps:
            score += 0.5
        if t_ok:
            score += 1.5
        if pinned >= 40:
            score += 0.5

    ds.total_score = score
    if not wiki_symbol_ok:
        ds.notes.append("wiki symbol crib mismatch at deck[5]/deck[66]")
    if not hdr_ok:
        ds.notes.append(f"pos0 digits not 1-9 (got {hdr_digits!r})")
    return ds


def sweep_variants(
    messages,
    *,
    upper26: str,
    name: str = "custom",
    anchors: Sequence[str] = DEFAULT_ANCHORS,
    wiki_mode: str = "symbol",
    lower_modes: Sequence[str] = ("mirror",),
) -> List[DeckScore]:
    """Score both 26- and 52-letter embeddings for one uppercase ordering."""
    out: List[DeckScore] = []
    u = upper26.upper()
    d26 = ac.build_deck_83(u, variant="26", wiki_crib=True, wiki_mode=wiki_mode)
    out.append(
        score_deck(
            f"{name}/26",
            d26,
            messages,
            variant="26",
            letters_26=u,
            anchors=anchors,
            wiki_mode=wiki_mode,
        )
    )
    for lm in lower_modes:
        g52 = ac.expand_to_52(u, lower_mode=lm)
        d52 = ac.build_deck_83(g52, variant="52", wiki_crib=True, wiki_mode=wiki_mode)
        out.append(
            score_deck(
                f"{name}/52-{lm}",
                d52,
                messages,
                variant="52",
                letters_26=u,
                anchors=anchors,
                wiki_mode=wiki_mode,
            )
        )
    return out


def sweep_presets(
    messages,
    *,
    anchors: Sequence[str] = DEFAULT_ANCHORS,
    wiki_mode: str = "symbol",
) -> List[DeckScore]:
    """Score GOD, standard A–Z, and raw-cut (no GOD promote) variants."""
    rows: List[DeckScore] = []
    god = ac.god_alphabet_26()
    rows.extend(sweep_variants(messages, upper26=god, name="god", anchors=anchors, wiki_mode=wiki_mode))
    rows.extend(
        sweep_variants(
            messages,
            upper26=ac.STANDARD_26,
            name="az",
            anchors=anchors,
            wiki_mode=wiki_mode,
        )
    )
    raw = ac.apply_range_cuts(ac.STANDARD_26, ac.GOD_CUT_SPECS)
    rows.extend(
        sweep_variants(messages, upper26=raw, name="god-raw", anchors=anchors, wiki_mode=wiki_mode)
    )
    return rows


def selftest() -> List[Tuple[str, bool]]:
    import corpus as corpus_mod

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    out: List[Tuple[str, bool]] = []

    rows = sweep_presets(M, anchors=("god",))
    out.append(("sweep_presets returns rows", len(rows) >= 3))
    out.append(("all decks length 83", all(len(r.deck) == 83 for r in rows)))
    out.append(("god/26 wiki crib", any(r.name == "god/26" and r.wiki_symbol_ok for r in rows)))

    cut_rows = sweep_variants(M, upper26=ac.god_alphabet_26(), name="t", anchors=("god",))
    out.append(("sweep_variants has 26 and 52", len(cut_rows) >= 2))

    sc = score_deck("x", ac.build_deck_83(ac.STANDARD_26, variant="26"), M, variant="26")
    out.append(("score_deck has total_score", sc.total_score >= 0))

    return out


if __name__ == "__main__":
    import sys

    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} deck_sweep checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
