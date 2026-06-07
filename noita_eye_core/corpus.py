"""Single source of truth for the 9-message Noita eye corpus.

EyeStat (``noita_eye_data.json``), EyeSieve (``eyesieve_corpus.py``) and the
workbench (an embedded ``DATA`` blob) each carry their own copy of the same 9
ciphertexts.  Copies drift.  This module loads one JSON
(``noita_eye_core/corpus.json``, a byte-copy of the EyeStat data) and exposes a
small typed accessor that every other core module imports.

``cross_check_eyestat`` verifies this copy is identical to the EyeStat archive's
JSON so the "single source" claim is enforced by a test, not just asserted.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
DEFAULT_PATH = HERE / "corpus.json"


@dataclass(frozen=True)
class Corpus:
    deck_size: int                       # alphabet size N (83)
    labels: Tuple[str, ...]
    ciphertexts: Tuple[Tuple[int, ...], ...]
    lengths: Tuple[int, ...]
    sigma0_targets: Optional[Tuple[int, ...]]

    @property
    def N(self) -> int:
        return self.deck_size

    @property
    def num_messages(self) -> int:
        return len(self.ciphertexts)

    @property
    def max_length(self) -> int:
        return max(self.lengths)

    def column(self, t: int) -> List[Tuple[int, int]]:
        """All ``(message_index, symbol)`` present at absolute position ``t``."""
        return [(i, ct[t]) for i, ct in enumerate(self.ciphertexts)
                if t < len(ct)]

    def messages_with_length_at_least(self, t: int) -> List[int]:
        return [i for i, ln in enumerate(self.lengths) if ln > t]


def load(path: Path | str = DEFAULT_PATH) -> Corpus:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    cts = tuple(tuple(int(x) for x in ct) for ct in raw["ciphertexts"])
    lengths = tuple(int(x) for x in raw["message_lengths"])
    labels = tuple(str(x) for x in raw["message_labels"])
    sigma0 = None
    if "sigma0_ct_targets" in raw:
        sigma0 = tuple(int(x) for x in raw["sigma0_ct_targets"])

    c = Corpus(
        deck_size=int(raw["deck_size"]),
        labels=labels,
        ciphertexts=cts,
        lengths=lengths,
        sigma0_targets=sigma0,
    )
    _validate(c)
    return c


def _validate(c: Corpus) -> None:
    if len(c.ciphertexts) != len(c.lengths):
        raise ValueError("ciphertext / length count mismatch")
    if len(c.labels) != len(c.ciphertexts):
        raise ValueError("label / ciphertext count mismatch")
    for i, ct in enumerate(c.ciphertexts):
        if len(ct) != c.lengths[i]:
            raise ValueError(f"message {i}: length {len(ct)} != "
                             f"declared {c.lengths[i]}")
        for v in ct:
            if not (0 <= v < c.deck_size):
                raise ValueError(f"message {i}: symbol {v} out of "
                                 f"[0,{c.deck_size})")


def universal_positions(c: Corpus) -> List[Tuple[int, int]]:
    """Positions where every message shares the same ciphertext symbol.

    Returns ``(position, symbol)`` pairs.  For this corpus this surfaces the
    ``(1, 66), (2, 5)`` header anomaly -- a built-in crib, since a shared
    keystream + identical ciphertext implies identical plaintext there.
    """
    out: List[Tuple[int, int]] = []
    L = min(c.lengths)
    for t in range(L):
        col = {ct[t] for ct in c.ciphertexts}
        if len(col) == 1:
            out.append((t, next(iter(col))))
    return out


def cross_check_eyestat(eyestat_json: Path | str) -> bool:
    """True iff our corpus.json matches the EyeStat archive's data file
    field-for-field (ciphertexts, lengths, deck size)."""
    a = load()
    with Path(eyestat_json).open("r", encoding="utf-8") as f:
        raw = json.load(f)
    b_cts = tuple(tuple(int(x) for x in ct) for ct in raw["ciphertexts"])
    b_lengths = tuple(int(x) for x in raw["message_lengths"])
    return (a.ciphertexts == b_cts
            and a.lengths == b_lengths
            and a.deck_size == int(raw["deck_size"]))


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    c = load()
    out.append(("corpus loads + validates", c.num_messages == 9
                and c.deck_size == 83))
    out.append(("lengths match data",
                c.lengths == (99, 103, 118, 102, 137, 124, 119, 120, 114)))

    uni = dict(universal_positions(c))
    out.append(("universal header (1,66) & (2,5)",
                uni.get(1) == 66 and uni.get(2) == 5))

    # column accessor: position 0 has all 9 messages; position 136 only msg 4.
    out.append(("column(0) has all 9", len(c.column(0)) == 9))
    out.append(("column(136) only longest message",
                [i for i, _ in c.column(136)] == [4]))

    # Cross-check against the EyeStat archive if reachable.
    eyestat_json = HERE.parent / "eyestat" / "noita_eye_data.json"
    if eyestat_json.exists():
        out.append(("corpus.json == EyeStat data (single source)",
                    cross_check_eyestat(eyestat_json)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} corpus checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
