"""Tier-1 solve tools — HTTP API helpers for the ordering workbench panel."""
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
import refrain as rf
import ngram_solve as ng
import rosetta
import base_search
import refrain_pipeline


def default_alphabet() -> str:
    return rf.DEFAULT_ALPHABET


def ordering_preview(
    ordering: Sequence[str],
    *,
    corpus_path: Optional[str] = None,
    messages: Optional[Sequence[Sequence[int]]] = None,
    N: Optional[int] = None,
    labels: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Score a candidate ordering O and return decrypt preview."""
    if messages is None:
        c = corpus_mod.load(corpus_path)
        messages = [list(x) for x in c.ciphertexts]
        N = c.N
        labels = list(c.labels)
    else:
        N = N or (max(max(m) for m in messages) + 1 if messages else 83)
        labels = labels or [str(i) for i in range(len(messages))]

    if len(ordering) < N:
        raise ValueError(f"ordering length {len(ordering)} < N={N}")

    alphabet = rf.DEFAULT_ALPHABET
    model = ng.TrigramModel(alphabet, ng._ENGLISH)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    O = list(ordering[:N])

    from alphabet_brute import _score_identity

    sc = _score_identity(messages, O, model=model, aidx=aidx, N=N, n_null=15, seed=0)
    return {
        "trigram": sc.trigram,
        "z": sc.z,
        "word_coverage": sc.word_coverage,
        "dict_hits": sc.dict_hits,
        "composite": sc.composite,
        "plaintext": {labels[i]: sc.plaintext.get(i, "") for i in sc.plaintext},
        "ordering_preview": "".join(O[:40]) + ("…" if N > 40 else ""),
    }


def rosetta_propagate(
    pins: Dict[int, str],
    *,
    corpus_path: Optional[str] = None,
    crib: Optional[str] = None,
    offset: int = 0,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    rep = rosetta.analyze(
        [list(x) for x in c.ciphertexts],
        pins,
        c.N,
        labels=c.labels,
        crib=crib,
        offset=offset,
    )
    return {
        "pins": rep.pins,
        "bijective_ok": rep.bijective_ok,
        "duplicate_letters": rep.duplicate_letters,
        "coverage": rep.coverage,
        "crib_consistent": rep.crib_consistent,
        "word_coverage": rep.word_coverage,
        "dict_hits": rep.dict_hits,
        "notes": rep.notes,
        "plaintext": rep.plaintext,
        "ordering": rep.ordering,
    }


def run_base_search(
    *,
    mode: str = "auto",
    corpus_path: Optional[str] = None,
    phrase: Optional[str] = None,
    offset: int = 0,
    top: int = 10,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    mode_used, results = base_search.run_search(
        [list(x) for x in c.ciphertexts],
        c.N,
        mode=mode,
        phrase=phrase,
        offset=offset,
        top=top,
    )
    return {
        "mode": mode_used,
        "results": [
            {
                "score": r.score,
                "refrain_consistent": r.refrain_consistent,
                "near_dup_agreement": r.near_dup_agreement,
                "bases": r.bases,
                "notes": r.notes,
            }
            for r in results
        ],
    }


def run_refrain_pipeline_api(
    *,
    corpus_path: Optional[str] = None,
    anchors: Optional[Sequence[str]] = None,
    top: int = 15,
) -> Dict[str, Any]:
    c = corpus_mod.load(corpus_path)
    hits, meta = refrain_pipeline.run_pipeline(
        [list(x) for x in c.ciphertexts],
        c.N,
        labels=c.labels,
        anchors=anchors or (),
        top=top,
    )
    return {
        "meta": meta,
        "hits": [
            {
                "phrase": h.phrase,
                "offset": h.offset,
                "source": h.source,
                "z": h.z,
                "word_coverage": h.word_coverage,
                "symbols_pinned": h.symbols_pinned,
            }
            for h in hits
        ],
    }
