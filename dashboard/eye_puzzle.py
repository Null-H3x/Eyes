"""Eye-puzzle-like cipher convert / plant / analyze for arbitrary datasets.

Models supported (no requirement for Noita header 66,5):
  * Linear stream: add, sub, beaufort (cipher_ops)
  * Pure progressive: c[t] = (p[t] + base + t) mod N
  * Per-message progressive: c[t] = (p[t] + base_m + t) mod N
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collections import Counter
from dataclasses import dataclass, field
import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple

from dashboard.cipher_validate import GLYPHS, KNOWN_MODES, encrypt_mode, parse_values
from dashboard.dataset_store import Dataset


@dataclass
class AnalysisResult:
    deck_size: int
    num_messages: int
    total_glyphs: int
    universal_positions: List[dict]
    per_message_ioc: List[float]
    pooled_ioc: float
    symbol_usage: int
    has_noita_header: bool
    eye_puzzle_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "deck_size": self.deck_size,
            "num_messages": self.num_messages,
            "total_glyphs": self.total_glyphs,
            "universal_positions": self.universal_positions,
            "per_message_ioc": self.per_message_ioc,
            "pooled_ioc": self.pooled_ioc,
            "symbol_usage": self.symbol_usage,
            "has_noita_header": self.has_noita_header,
            "eye_puzzle_notes": self.eye_puzzle_notes,
        }


def _ioc(seq: Sequence[int]) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(seq).values()) / (n * (n - 1))


def find_universal_positions(
    messages: Sequence[Sequence[int]],
) -> List[Tuple[int, int]]:
    """Positions where every message shares the same ciphertext symbol."""
    if not messages:
        return []
    L = min(len(m) for m in messages)
    out = []
    for t in range(L):
        col = {m[t] for m in messages}
        if len(col) == 1:
            out.append((t, next(iter(col))))
    return out


def has_noita_header(messages: Sequence[Sequence[int]]) -> bool:
    if len(messages) < 2:
        return False
    L = min(len(m) for m in messages)
    if L < 3:
        return False
    return all(m[1] == 66 and m[2] == 5 for m in messages)


def analyze_dataset(ds: Dataset) -> AnalysisResult:
    messages = ds.ciphertexts
    N = ds.deck_size
    uni = find_universal_positions(messages)
    pooled = [v for m in messages for v in m]
    notes = []
    if not uni:
        notes.append(
            "No universal ciphertext positions across all messages — "
            "expected for custom imports (Noita eyes have CT[1]=66, CT[2]=5).")
    else:
        notes.append(
            f"{len(uni)} universal position(s) found: "
            + ", ".join(f"({p},{s})" for p, s in uni[:8])
            + ("…" if len(uni) > 8 else ""))
    if has_noita_header(messages):
        notes.append("Matches Noita universal header pattern at positions 1 and 2.")
    elif N == 83:
        notes.append(
            "N=83 but no (66,5) header — valid eye-puzzle-like corpus without "
            "Noita marker bytes.")

    return AnalysisResult(
        deck_size=N,
        num_messages=len(messages),
        total_glyphs=len(pooled),
        universal_positions=[
            {"position": p, "symbol": s, "glyph": GLYPHS[s] if 0 <= s < len(GLYPHS) else "?"}
            for p, s in uni
        ],
        per_message_ioc=[_ioc(m) for m in messages],
        pooled_ioc=_ioc(pooled),
        symbol_usage=len({v for m in messages for v in m}),
        has_noita_header=has_noita_header(messages),
        eye_puzzle_notes=notes,
    )


def plant_message(
    plaintext: Sequence[int],
    *,
    mode: str,
    key: Sequence[int],
    base: int = 0,
    offset: int = 0,
    N: int = 83,
) -> List[int]:
    return encrypt_mode(list(plaintext), mode=mode, key=key, base=base,
                        offset=offset, N=N)


def _validate_plant_mode(mode: str) -> None:
    if mode not in KNOWN_MODES or mode in ("user_ciphertext",):
        raise ValueError(
            f"invalid plant mode {mode!r}; use one of: add, sub, beaufort, "
            "pure_progressive, per_msg_progressive, identity")


def _validate_inject_header(inject_header: Optional[Sequence[int]]) -> None:
    if inject_header is None:
        return
    if len(inject_header) % 2 != 0:
        raise ValueError(
            f"inject_header must be an even-length [pos,sym,...] list, "
            f"got {len(inject_header)} values")
    for j in range(0, len(inject_header), 2):
        pos = int(inject_header[j])
        if pos < 0:
            raise ValueError(f"inject_header position {pos} must be >= 0")


def plant_dataset(
    plaintexts: Sequence[Sequence[int]],
    labels: Sequence[str],
    *,
    mode: str,
    keys: Optional[Sequence[Sequence[int]]] = None,
    bases: Optional[Sequence[int]] = None,
    deck_size: int = 83,
    name: str = "Planted eye-puzzle dataset",
    inject_header: Optional[Sequence[int]] = None,
) -> Dataset:
    """Build ciphertext messages from plaintext using an eye-puzzle-like model."""
    if not plaintexts:
        raise ValueError("at least one plaintext message required")
    if deck_size < 2 or deck_size > 256:
        raise ValueError("deck_size must be in [2, 256]")
    _validate_plant_mode(mode)
    _validate_inject_header(inject_header)
    N = deck_size
    keys = keys or [[0] for _ in plaintexts]
    bases = bases or [0] * len(plaintexts)
    if len(keys) < len(plaintexts):
        keys = list(keys) + [keys[-1]] * (len(plaintexts) - len(keys))
    if len(bases) < len(plaintexts):
        bases = list(bases) + [bases[-1]] * (len(plaintexts) - len(bases))

    ciphertexts = []
    for i, plain in enumerate(plaintexts):
        for v in plain:
            if not (0 <= v < N):
                raise ValueError(f"plaintext value {v} outside [0, {N})")
        ct = plant_message(
            plain, mode=mode, key=keys[i], base=bases[i], offset=0, N=N)
        if inject_header:
            for j in range(0, len(inject_header), 2):
                pos, sym = int(inject_header[j]), int(inject_header[j + 1])
                if 0 <= pos < len(ct):
                    ct[pos] = sym % N
                else:
                    raise ValueError(
                        f"inject_header position {pos} out of range "
                        f"for message length {len(ct)}")
        ciphertexts.append(list(ct))

    lbls = list(labels) if labels else [f"Msg {i + 1}" for i in range(len(plaintexts))]
    if len(lbls) < len(plaintexts):
        lbls.extend(f"Msg {i + 1}" for i in range(len(lbls), len(plaintexts)))

    meta = {
        "plant_mode": mode,
        "inject_header": list(inject_header) if inject_header else None,
    }
    return Dataset(
        id=f"plant-{uuid.uuid4().hex[:10]}",
        name=name,
        source="planted",
        deck_size=N,
        labels=lbls,
        ciphertexts=ciphertexts,
        notes=f"Planted with mode={mode} ({len(plaintexts)} messages)",
        metadata=meta,
    )


def convert_plaintext_to_ciphertext(
    plaintext_text: str,
    *,
    mode: str,
    key_text: str = "",
    base: int = 0,
    N: int = 83,
) -> dict:
    """Single-message convert for display / copy-paste."""
    _validate_plant_mode(mode)
    if N < 2 or N > 256:
        raise ValueError("deck_size must be in [2, 256]")
    plain = parse_values(plaintext_text, N=N)
    key = parse_values(key_text, N=N) if key_text.strip() else [0]
    ct = plant_message(plain, mode=mode, key=key, base=base, N=N)
    return {
        "plaintext": plain,
        "ciphertext": ct,
        "glyphs": "".join(GLYPHS[v] if 0 <= v < len(GLYPHS) else "?" for v in ct),
        "decimal": " ".join(str(v) for v in ct),
        "mode": mode,
        "length": len(ct),
    }


def parse_plaintext_messages(text: str, *, N: int = 83) -> Tuple[List[str], List[List[int]]]:
    """One plaintext per non-empty line; optional ``label: values`` prefix."""
    labels = []
    plains = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line and not line.split(":")[0].strip().isdigit():
            lab, rest = line.split(":", 1)
            labels.append(lab.strip())
            plains.append(parse_values(rest, N=N))
        else:
            labels.append(f"Message {len(plains) + 1}")
            plains.append(parse_values(line, N=N))
    return labels, plains


def selftest() -> List[Tuple[str, bool]]:
    from dashboard.dataset_store import load_builtin

    out: List[Tuple[str, bool]] = []
    builtin = load_builtin()
    a = analyze_dataset(builtin)
    out.append(("builtin has noita header flag", a.has_noita_header))
    out.append(("builtin finds universal positions", len(a.universal_positions) >= 2))

    # Plant without header
    plain = [[10, 20, 30, 40], [11, 21, 31, 41]]
    ds = plant_dataset(plain, ["A", "B"], mode="add",
                       keys=[[7], [8]], bases=[0, 3], deck_size=83)
    a2 = analyze_dataset(ds)
    out.append(("planted dataset has no false noita header", not a2.has_noita_header))
    out.append(("plant round-trip length", len(ds.ciphertexts[0]) == 4))

    conv = convert_plaintext_to_ciphertext("10 20 30", mode="add", key_text="5", N=83)
    out.append(("convert returns ciphertext", len(conv["ciphertext"]) == 3))

    labels, msgs = parse_plaintext_messages("A: 1 2 3\n4 5 6", N=83)
    out.append(("parse plaintext messages", len(msgs) == 2 and labels[0] == "A"))

    try:
        plant_dataset([[1, 2, 3]], ["A"], mode="add", inject_header=(1, 2, 3))
        out.append(("odd inject_header rejected", False))
    except ValueError:
        out.append(("odd inject_header rejected", True))

    from dashboard.cipher_validate import validate_cipher
    pds = plant_dataset(plain, ["A", "B"], mode="add", keys=[[7], [8]], bases=[0, 3])
    r = validate_cipher(
        pds.ciphertexts, pds.labels, mode="add", message="A", offset=0,
        plaintext=plain[0], key=[7], N=83)
    out.append(("planted corpus validates exact", r.verdict == "EXACT_MATCH"))

    try:
        plant_dataset([[1, 2, 3]], ["A"], mode="not_a_mode")
        out.append(("invalid plant mode rejected", False))
    except ValueError:
        out.append(("invalid plant mode rejected", True))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} eye_puzzle checks passed")
    sys.exit(0 if n == len(results) else 1)
