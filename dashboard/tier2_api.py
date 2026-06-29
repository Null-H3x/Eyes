"""Tier-2 solve tools — HTTP API helpers for Phase 2 crib/ordering workbench."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

_REPO = Path(__file__).resolve().parent.parent
_CORE = _REPO / "noita_eye_core"
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import corpus as corpus_mod
import pos0_base
import triplet_base_search as tbs
import order_bench
import compose_order
import exhaust_bench


def run_pos0_analysis(*, corpus_path: Optional[str] = None) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    rep = pos0_base.analyze(
        [list(x) for x in c.ciphertexts], c.N, labels=c.labels,
    )
    return {
        "model": rep.model,
        "model_score": rep.model_score,
        "rows": [
            {"msg": r.msg, "label": r.label, "pos0_ct": r.pos0_ct,
             "assumed_p0": r.assumed_p0, "implied_base": r.implied_base}
            for r in rep.rows
        ],
        "bases": rep.bases,
        "triplet_notes": rep.triplet_notes,
        "notes": rep.notes,
    }


def run_triplet_base_search(
    *,
    mode: str = "auto",
    corpus_path: Optional[str] = None,
    phrase: Optional[str] = None,
    top: int = 5,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    rep = tbs.search_all(
        [list(x) for x in c.ciphertexts], c.N,
        mode=mode, phrase=phrase, top=top,
    )
    return {
        "merged_bases": rep.merged_bases,
        "notes": rep.notes,
        "triplets": [
            {
                "triplet": tr.triplet,
                "members": tr.members,
                "mode": tr.mode,
                "best_score": tr.best.score if tr.best else None,
                "best_bases": tr.best.bases if tr.best else {},
                "notes": tr.notes,
            }
            for tr in rep.results
        ],
    }


def run_order_bench(
    *,
    phrases: Optional[Sequence[str]] = None,
    corpus_path: Optional[str] = None,
    top: int = 15,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    phrase_list = list(phrases or ["trueknowledgeofthegods"])
    hits = order_bench.run_bench(
        [list(x) for x in c.ciphertexts], phrase_list, c.N, top=top,
    )
    return {
        "hits": [
            {
                "phrase": h.phrase,
                "offset": h.offset,
                "z": h.z,
                "word_coverage": h.word_coverage,
                "symbols_pinned": h.symbols_pinned,
            }
            for h in hits
        ],
    }


def run_compose_order_api(
    *,
    anchors: Optional[Sequence[str]] = None,
    seed_phrases: Optional[Sequence[str]] = None,
    corpus_path: Optional[str] = None,
    top: int = 15,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    hits, meta = compose_order.run_compose_order(
        [list(x) for x in c.ciphertexts], c.N,
        labels=c.labels,
        anchors=anchors or (),
        seed_phrases=seed_phrases or (),
        top=top,
    )
    return {
        "meta": meta,
        "hits": [
            {
                "phrase": h.phrase,
                "offset": h.offset,
                "z": h.z,
                "word_coverage": h.word_coverage,
                "compose_score": h.compose_score,
            }
            for h in hits
        ],
    }


def run_exhaust_bench_api(
    *,
    phrase: str,
    offset: int = 0,
    corpus_path: Optional[str] = None,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    r = exhaust_bench.run_exhaust(
        [list(x) for x in c.ciphertexts], phrase, offset, c.N,
    )
    return {
        "consistent": r.consistent,
        "method": r.method,
        "free_slots": r.free_slots,
        "z": r.z,
        "word_coverage": r.word_coverage,
        "symbols_pinned": r.symbols_pinned,
    }
