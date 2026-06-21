"""Infer ciphertext deck size (alphabet N) from symbol statistics.

When importing without a known N, try parsing at each standard alphabet size
(especially N=83 for eye ciphers) before ranking candidates.  Parsing at a 256
ceiling mis-splits glued decimals (``10665`` → ``[106, 65]`` instead of
``[10, 66, 5]``), which inflates min_N to nonsense values like 235.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dashboard.cipher_validate import GLYPHS  # noqa: E402

PARSE_CEILING = 256
STANDARD_DECKS = (26, 32, 52, 64, 72, 83, 95, 128, 256)
NOITA_N = 83


@dataclass
class DeckCandidate:
    N: int
    score: float
    coverage: float
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "N": self.N,
            "score": round(self.score, 3),
            "coverage": round(self.coverage, 4),
            "reasons": self.reasons,
        }


def _pooled(messages: Sequence[Sequence[int]]) -> List[int]:
    return [v for m in messages for v in m]


def _score_candidate(
    N: int,
    *,
    min_n: int,
    max_v: int,
    usage: int,
    pooled: Sequence[int],
    messages: Sequence[Sequence[int]],
) -> DeckCandidate:
    if N < min_n:
        return DeckCandidate(N, -999.0, 0.0, ["invalid: below min_N"])

    coverage = usage / N
    reasons: List[str] = []
    score = 0.0

    # Prefer smallest valid N unless evidence supports a standard alphabet.
    score += max(0.0, 40.0 - (N - min_n) * 1.5)
    reasons.append(f"min_N={min_n}, headroom={N - min_n}")

    if 0.15 <= coverage <= 0.95:
        score += 20.0
        reasons.append(f"coverage {coverage:.1%} plausible")
    elif coverage < 0.15:
        score += 5.0
        reasons.append(f"sparse coverage {coverage:.1%} (unused symbols)")
    else:
        score += 10.0
        reasons.append(f"dense coverage {coverage:.1%}")

    if N in STANDARD_DECKS:
        score += 12.0
        reasons.append(f"standard alphabet N={N}")

    if N == NOITA_N:
        if max_v <= NOITA_N - 1:
            score += 18.0
            reasons.append("all symbols fit Noita 83-rune deck")
        from dashboard.eye_puzzle import has_noita_header
        if has_noita_header(messages):
            score += 35.0
            reasons.append("Noita universal header (66,5) detected")
        if usage >= 40:
            score += 8.0
            reasons.append("rich symbol usage for N=83")

    # Penalise non-standard alphabets far larger than observed symbol diversity.
    if N > usage * 3 and N not in STANDARD_DECKS:
        score -= 15.0
        reasons.append("alphabet much larger than symbol diversity")

    if min_n > NOITA_N and usage < 20 and N >= min_n and N not in STANDARD_DECKS:
        score -= 30.0
        reasons.append("large min_N with sparse usage (likely parse artefact)")

    # Slight preference for tight fit when not a standard size.
    if N == min_n and N not in STANDARD_DECKS and min_n <= NOITA_N * 2:
        score += 8.0
        reasons.append("tight minimum fit")
        if coverage >= 0.999:
            score += 6.0
            reasons.append("exact minimum alphabet")

    # High symbols used relative to N — good for eye ciphers.
    if usage >= min(50, N - 5):
        score += 5.0
        reasons.append("broad symbol usage")

    return DeckCandidate(N, score, coverage, reasons)


def _has_noita_header(messages: Sequence[Sequence[int]]) -> bool:
    from dashboard.eye_puzzle import has_noita_header
    return has_noita_header(messages)


def infer_deck_size(
    messages: Sequence[Sequence[int]],
    *,
    top_k: int = 8,
) -> dict:
    """Rank candidate deck sizes; return best inference + evidence."""
    if not messages:
        raise ValueError("no messages to analyse")
    pooled = _pooled(messages)
    if not pooled:
        raise ValueError("no ciphertext symbols found")

    max_v = max(pooled)
    min_n = max_v + 1
    if min_n > PARSE_CEILING:
        raise ValueError(
            f"max symbol {max_v} requires N>{PARSE_CEILING}; "
            "values may be plaintext indices, not ciphertext")
    usage = len(set(pooled))

    candidates: set[int] = {min_n}
    for s in STANDARD_DECKS:
        if min_n <= s <= PARSE_CEILING:
            candidates.add(s)
    for n in range(min_n, min(min_n + 24, PARSE_CEILING + 1)):
        candidates.add(n)

    ranked: List[DeckCandidate] = []
    for N in sorted(candidates):
        ranked.append(_score_candidate(
            N, min_n=min_n, max_v=max_v, usage=usage,
            pooled=pooled, messages=messages))

    ranked.sort(key=lambda c: (-c.score, c.N))
    best = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    margin = best.score - (second.score if second else 0.0)
    if margin >= 25:
        confidence = "high"
    elif margin >= 12:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "inferred_N": best.N,
        "confidence": confidence,
        "score_margin": round(margin, 3),
        "min_N": min_n,
        "max_symbol": max_v,
        "symbol_usage": usage,
        "num_messages": len(messages),
        "total_glyphs": len(pooled),
        "has_noita_header": _has_noita_header(messages),
        "best": best.to_dict(),
        "candidates": [c.to_dict() for c in ranked[:top_k]],
        "notes": [
            f"Minimum valid N is {min_n} (max symbol {max_v}).",
            f"{usage} distinct symbols observed across {len(pooled)} glyphs.",
            f"Best candidate N={best.N} ({confidence} confidence).",
        ],
    }


def _parse_attempts(content: str, *, fmt: str = "auto"):
    """Yield (N, ParseImportResult) for each strict parse that succeeds."""
    from dashboard.import_parse import parse_import_content

    tried: set[int] = set()
    # Eye ciphers: try standard alphabets first (83 before 256).
    for N in STANDARD_DECKS:
        if N in tried:
            continue
        tried.add(N)
        try:
            parsed = parse_import_content(content, fmt=fmt, deck_size=N, strict=True)
        except ValueError:
            continue
        yield N, parsed

    # Separated-token upper bound for non-standard sizes.
    max_tok = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        body = line.split(":", 1)[1].strip() if ":" in line and not re.fullmatch(
            r"[\d\s,;|.+-]+", line.split(":", 1)[0].strip()) else line
        for p in re.split(r"[\s,;|]+", body):
            if not p:
                continue
            if p.isdigit() or (p.startswith("-") and p[1:].isdigit()):
                max_tok = max(max_tok, abs(int(p)))
    if max_tok >= 0:
        mn = max_tok + 1
        for N in range(mn, min(mn + 32, PARSE_CEILING + 1)):
            if N in tried:
                continue
            tried.add(N)
            try:
                parsed = parse_import_content(content, fmt=fmt, deck_size=N, strict=True)
            except ValueError:
                continue
            yield N, parsed


def _rank_parse_attempt(N: int, parsed, inf: dict) -> float:
    """Score a (parse deck size, inferred statistics) pair."""
    pooled = _pooled(parsed.messages)
    max_v = max(pooled) if pooled else 0
    score = inf["best"]["score"]
    if inf["inferred_N"] == N:
        score += 35.0
    elif abs(inf["inferred_N"] - N) <= 3:
        score += 12.0
    score += len(pooled) * 0.05
    if N == NOITA_N and inf.get("has_noita_header"):
        score += 15.0
    # Prefer eye-cipher-scale parses over false fits on tiny alphabets (e.g. N=26
    # splitting glued decimals into many single-digit tokens).
    if N == NOITA_N and max_v >= 40:
        score += 22.0
    if N in STANDARD_DECKS:
        score += max_v * 0.12
    return score


def infer_from_text(
    content: str,
    *,
    fmt: str = "auto",
) -> dict:
    """Parse import text at candidate deck sizes, then infer the best N."""
    from dashboard.import_parse import parse_import_content

    best_inf: Optional[dict] = None
    best_parsed = None
    best_score = -1e9
    best_parse_n = None

    for N, parsed in _parse_attempts(content, fmt=fmt):
        inf = infer_deck_size(parsed.messages)
        score = _rank_parse_attempt(N, parsed, inf)
        if score > best_score:
            best_score = score
            best_inf = inf
            best_parsed = parsed
            best_parse_n = N

    if best_inf is None or best_parsed is None:
        parsed = parse_import_content(content, fmt=fmt, deck_size=None, strict=True)
        best_inf = infer_deck_size(parsed.messages)
        best_parsed = parsed
        best_parse_n = parsed.deck_size

    assert best_inf is not None and best_parsed is not None
    best_inf["labels"] = best_parsed.labels
    best_inf["parse_deck_size"] = best_parse_n
    best_inf["parse"] = {
        "detected_format": best_parsed.detected_format,
        "per_message": best_parsed.per_message,
        "num_messages": len(best_parsed.messages),
        "deck_size": best_parse_n,
    }
    return best_inf


def infer_active_dataset() -> dict:
    from dashboard.dataset_store import get_active

    ds = get_active()
    inf = infer_deck_size(ds.ciphertexts)
    inf["dataset_id"] = ds.id
    inf["dataset_name"] = ds.name
    inf["current_deck_size"] = ds.deck_size
    inf["matches_current"] = ds.deck_size == inf["inferred_N"]
    return inf


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []

    # Noita-like: values 0-82, header pattern
    noita_like = [
        [0, 66, 5, 10, 20, 30],
        [1, 66, 5, 11, 21, 31],
    ]
    r = infer_deck_size(noita_like)
    out.append(("noita-like infers 83", r["inferred_N"] == 83))
    out.append(("noita header boosts confidence", r["has_noita_header"]))

    # Minimal custom alphabet
    custom = [[0, 1, 2, 3], [3, 2, 1, 0]]
    r2 = infer_deck_size(custom)
    out.append(("small corpus min_N=4", r2["inferred_N"] == 4))

    # Unknown import path — glued Noita header token
    r3 = infer_from_text("10665")
    out.append(("glued 10665 infers 83", r3["inferred_N"] == 83))

    r4 = infer_from_text("10 20 30\n40 50 60")
    out.append(("separated decimals infer standard N",
                r4["inferred_N"] in STANDARD_DECKS))

    try:
        infer_deck_size([[]])
        out.append(("empty message rejected", False))
    except ValueError:
        out.append(("empty message rejected", True))

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Infer ciphertext deck size N")
    ap.add_argument("--active", action="store_true",
                    help="analyse active workbench dataset")
    ap.add_argument("--content", default="",
                    help="paste import text instead of active dataset")
    ap.add_argument("--format", default="auto")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    if args.content.strip():
        result = infer_from_text(args.content, fmt=args.format)
    elif args.active:
        result = infer_active_dataset()
    else:
        ap.print_help()
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Inferred N: {result['inferred_N']} "
              f"({result.get('confidence', '?')} confidence)")
        print(f"  min_N={result['min_N']}  max_symbol={result['max_symbol']}  "
              f"usage={result['symbol_usage']}")
        if result.get("matches_current") is False:
            print(f"  WARNING: active dataset has N={result['current_deck_size']}")
        print("\nTop candidates:")
        for c in result.get("candidates", [])[:5]:
            print(f"  N={c['N']:3d}  score={c['score']:6.2f}  "
                  f"cov={c['coverage']:.1%}  {c['reasons'][0]}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise SystemExit(main())
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} deck_infer checks passed")
    raise SystemExit(0 if n == len(results) else 1)
