"""Validate known cipher implementations against the eye corpus.

Lets you test whether a hypothesised (plaintext, key, combiner) reproduces the
observed ciphertext at a chosen message offset — the same arithmetic
``cipher_ops`` uses everywhere else, so a match here means your external code
agrees with the workbench's canonical combiners.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Eyesieve glyph display alphabet (value 0-82)
GLYPHS = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "!@#$%&*+-=<>?.,:;~^|/"
)

KNOWN_MODES = {
    "add": {
        "label": "Vigenère / additive (c = p + k mod N)",
        "family": "linear_stream",
        "impl": "noita_eye_core.cipher_ops",
    },
    "sub": {
        "label": "Key-subtracted (c = p - k mod N)",
        "family": "linear_stream",
        "impl": "noita_eye_core.cipher_ops",
    },
    "beaufort": {
        "label": "Beaufort (c = k - p mod N)",
        "family": "linear_stream",
        "impl": "noita_eye_core.cipher_ops",
    },
    "pure_progressive": {
        "label": "Pure progressive (c = p + base + t mod N, no per-msg base)",
        "family": "progressive",
        "impl": "noita_eye_core.pureprog",
    },
    "per_msg_progressive": {
        "label": "Per-message progressive (c = p + base_m + t mod N)",
        "family": "progressive",
        "impl": "noita_eye_core.chain_models",
    },
    "identity": {
        "label": "Identity / no cipher (c = p)",
        "family": "trivial",
        "impl": "builtin",
    },
    "user_ciphertext": {
        "label": "Compare pasted ciphertext to corpus (validate external output)",
        "family": "compare",
        "impl": "builtin",
    },
}


@dataclass
class CipherValidateResult:
    mode: str
    message: str
    message_index: int
    offset: int
    length: int
    corpus_slice: List[int]
    computed: List[int]
    plaintext: List[int]
    key: List[int]
    base: int
    matches: int
    match_rate: float
    verdict: str
    positions: List[dict] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    decrypt_ioc: Optional[float] = None
    round_trip_ok: Optional[bool] = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "message": self.message,
            "message_index": self.message_index,
            "offset": self.offset,
            "length": self.length,
            "corpus_slice": self.corpus_slice,
            "computed": self.computed,
            "plaintext": self.plaintext,
            "key": self.key,
            "base": self.base,
            "matches": self.matches,
            "match_rate": self.match_rate,
            "verdict": self.verdict,
            "positions": self.positions,
            "notes": self.notes,
            "decrypt_ioc": self.decrypt_ioc,
            "round_trip_ok": self.round_trip_ok,
            "corpus_glyphs": "".join(_glyph(v) for v in self.corpus_slice),
            "computed_glyphs": "".join(_glyph(v) for v in self.computed),
        }


def _glyph(v: int) -> str:
    return GLYPHS[v] if 0 <= v < len(GLYPHS) else "?"


def parse_values(text: str, *, N: int = 83, strict: bool = False) -> List[int]:
    """Parse integers, glyphs, or glued ciphertext streams."""
    text = text.strip()
    if not text:
        return []

    def _token_parse() -> List[int]:
        parts = re.split(r"[\s,;]+", text)
        vals: List[int] = []
        for p in parts:
            if not p:
                continue
            if p.isdigit() or (p.startswith("-") and p[1:].isdigit()):
                v = int(p)
                if strict and not (0 <= v < N):
                    raise ValueError(f"value {v} outside [0, {N})")
                vals.append(v % N)
            elif len(p) == 1 and p in GLYPHS:
                vals.append(GLYPHS.index(p))
            else:
                raise ValueError(
                    f"cannot parse value {p!r} (use 0-{N - 1} or glyph)")
        return vals

    if re.search(r"[\s,;]", text):
        return _token_parse()

    if text.isdigit():
        whole = int(text)
        if strict and not (0 <= whole < N):
            raise ValueError(f"value {whole} outside [0, {N})")
        if whole < N and len(text) <= 3:
            return [whole]

    try:
        from dashboard.import_parse import (
            detect_import_format,
            parse_ciphertext_line,
            parse_digit_stream,
            parse_letter_stream,
        )
        fmt = detect_import_format(text)
        if fmt == "digit_stream":
            return parse_digit_stream(text, N=N, strict=strict).values
        if fmt == "letter_stream":
            return parse_letter_stream(text, N=N, strict=strict).values
        return parse_ciphertext_line(text, N=N, strict=strict).values
    except ValueError:
        return _token_parse()


def message_index(label: str, labels: Sequence[str]) -> int:
    norm = label.strip().lower().replace("_", " ")
    aliases = {
        "e1": "east 1", "w1": "west 1", "e2": "east 2", "w2": "west 2",
        "e3": "east 3", "w3": "west 3", "e4": "east 4", "w4": "west 4",
        "e5": "east 5",
    }
    norm = aliases.get(norm.replace(" ", ""), norm)
    for i, lab in enumerate(labels):
        if lab.lower() == norm:
            return i
    raise ValueError(f"unknown message {label!r}; use: {', '.join(labels)}")


def _expand_key(key: Sequence[int], length: int) -> List[int]:
    if not key:
        return [0] * length
    if len(key) >= length:
        return list(key[:length])
    return [key[i % len(key)] for i in range(length)]


def _ioc(seq: Sequence[int]) -> float:
    from collections import Counter
    n = len(seq)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(seq).values()) / (n * (n - 1))


def encrypt_mode(
    plain: Sequence[int],
    *,
    mode: str,
    key: Sequence[int],
    base: int,
    offset: int,
    N: int,
) -> List[int]:
    if mode == "identity":
        return list(plain)
    if mode == "user_ciphertext":
        raise ValueError("user_ciphertext mode uses pasted values as computed")
    if mode == "pure_progressive":
        return [(p + base + offset + i) % N for i, p in enumerate(plain)]
    if mode == "per_msg_progressive":
        return [(p + base + offset + i) % N for i, p in enumerate(plain)]
    import sys
    from pathlib import Path
    core = Path(__file__).resolve().parent.parent / "noita_eye_core"
    if str(core) not in sys.path:
        sys.path.insert(0, str(core))
    import cipher_ops as co
    k = _expand_key(key, len(plain))
    return co.encrypt_stream(plain, k, mode, N)


def decrypt_mode(
    cipher: Sequence[int],
    *,
    mode: str,
    key: Sequence[int],
    base: int,
    offset: int,
    N: int,
) -> List[int]:
    if mode == "identity":
        return list(cipher)
    if mode in ("pure_progressive", "per_msg_progressive"):
        return [(c - base - offset - i) % N for i, c in enumerate(cipher)]
    import sys
    from pathlib import Path
    core = Path(__file__).resolve().parent.parent / "noita_eye_core"
    if str(core) not in sys.path:
        sys.path.insert(0, str(core))
    import cipher_ops as co
    k = _expand_key(key, len(cipher))
    return co.decrypt_stream(cipher, k, mode, N)


def validate_cipher(
    messages: Sequence[Sequence[int]],
    labels: Sequence[str],
    *,
    mode: str,
    message: str,
    offset: int,
    plaintext: Optional[Sequence[int]] = None,
    key: Optional[Sequence[int]] = None,
    base: int = 0,
    user_ciphertext: Optional[Sequence[int]] = None,
    N: int = 83,
) -> CipherValidateResult:
    if mode not in KNOWN_MODES:
        raise ValueError(f"unknown mode {mode!r}; valid: {sorted(KNOWN_MODES)}")

    mi = message_index(message, labels)
    msg = messages[mi]
    notes: List[str] = []

    if mode == "user_ciphertext":
        if not user_ciphertext:
            raise ValueError("user_ciphertext mode requires ciphertext values")
        computed = list(user_ciphertext)
        plain = list(plaintext) if plaintext else []
        k = list(key) if key else []
        length = len(computed)
    else:
        if not plaintext:
            raise ValueError("plaintext values required")
        plain = list(plaintext)
        k = list(key) if key else [0]
        length = len(plain)
        computed = encrypt_mode(
            plain, mode=mode, key=k, base=base, offset=offset, N=N)

    if offset < 0 or offset + length > len(msg):
        raise ValueError(
            f"slice [{offset}:{offset + length}] out of range for "
            f"{labels[mi]} (len {len(msg)})")

    corpus_slice = list(msg[offset:offset + length])
    positions = []
    matches = 0
    for i, (exp, obs) in enumerate(zip(computed, corpus_slice)):
        ok = exp == obs
        if ok:
            matches += 1
        positions.append({
            "i": i,
            "abs": offset + i,
            "plain": plain[i] if i < len(plain) else None,
            "key": (_expand_key(k, length)[i] if k else None),
            "expected": exp,
            "observed": obs,
            "match": ok,
            "exp_glyph": _glyph(exp),
            "obs_glyph": _glyph(obs),
        })

    rate = matches / max(1, length)
    if rate == 1.0:
        verdict = "EXACT_MATCH"
        notes.append("Computed ciphertext matches corpus slice exactly.")
    elif rate >= 0.5:
        verdict = "PARTIAL_MATCH"
        notes.append(f"{matches}/{length} positions match — check offset, base, or mode.")
    else:
        verdict = "NO_MATCH"
        notes.append("Poor match — likely wrong cipher family, key, or plaintext.")

    round_trip_ok = None
    decrypt_ioc = None
    if mode in ("add", "sub", "beaufort"):
        import sys
        from pathlib import Path
        core = Path(__file__).resolve().parent.parent / "noita_eye_core"
        if str(core) not in sys.path:
            sys.path.insert(0, str(core))
        import cipher_ops as co
        kexp = _expand_key(k, length)
        dec = co.decrypt_stream(computed, kexp, mode, N)
        round_trip_ok = dec == plain
        if not round_trip_ok:
            notes.append("Round-trip encrypt/decrypt does not recover plaintext.")
        try:
            decrypt_ioc = _ioc(co.decrypt_stream(corpus_slice, kexp, mode, N))
        except (ValueError, IndexError, TypeError):
            notes.append("decrypt IoC unavailable for corpus slice")

    return CipherValidateResult(
        mode=mode,
        message=labels[mi],
        message_index=mi,
        offset=offset,
        length=length,
        corpus_slice=corpus_slice,
        computed=computed,
        plaintext=plain,
        key=k,
        base=base,
        matches=matches,
        match_rate=rate,
        verdict=verdict,
        positions=positions,
        notes=notes,
        decrypt_ioc=decrypt_ioc,
        round_trip_ok=round_trip_ok,
    )


def sweep_linear_modes(
    messages: Sequence[Sequence[int]],
    labels: Sequence[str],
    *,
    message: str,
    offset: int,
    plaintext: Sequence[int],
    key: Sequence[int],
    base: int = 0,
    N: int = 83,
) -> List[dict]:
    """Try add/sub/beaufort and report best match (quick family picker)."""
    results = []
    for mode in ("add", "sub", "beaufort"):
        r = validate_cipher(
            messages, labels, mode=mode, message=message, offset=offset,
            plaintext=plaintext, key=key, base=base, N=N)
        results.append(r.to_dict())
    results.sort(key=lambda x: x["match_rate"], reverse=True)
    return results


def catalog() -> List[dict]:
    return [
        {"id": k, **{kk: vv for kk, vv in v.items()}}
        for k, v in KNOWN_MODES.items()
    ]


def selftest() -> List[Tuple[str, bool]]:
    import sys
    from pathlib import Path
    core = Path(__file__).resolve().parent.parent / "noita_eye_core"
    sys.path.insert(0, str(core))
    import cipher_ops as co
    import corpus as c

    cor = c.load()
    M = [list(x) for x in cor.ciphertexts]
    out: List[Tuple[str, bool]] = []

    plain = [10, 20, 30, 40, 50]
    key = [7, 3]
    ct = co.encrypt_stream(plain, _expand_key(key, len(plain)), "add", cor.N)
    # Plant into message 0 at offset 10
    msg_copy = list(M[0])
    off = 10
    for i, v in enumerate(ct):
        msg_copy[off + i] = v
    M2 = [msg_copy if i == 0 else list(m) for i, m in enumerate(M)]

    r = validate_cipher(
        M2, cor.labels, mode="add", message="East 1", offset=off,
        plaintext=plain, key=key, N=cor.N)
    out.append(("validate_cipher exact match on planted add", r.verdict == "EXACT_MATCH"))
    out.append(("validate_cipher round_trip on add", r.round_trip_ok is True))

    r2 = validate_cipher(
        M2, cor.labels, mode="sub", message="East 1", offset=off,
        plaintext=plain, key=key, N=cor.N)
    out.append(("wrong mode does not false-positive as exact", r2.verdict != "EXACT_MATCH"))

    vals = parse_values("10 20 30")
    out.append(("parse_values integers", vals == [10, 20, 30]))
    out.append(("parse_values glyphs", parse_values("o % 5") == [50, 66, 5]))

    try:
        parse_values("999", N=83, strict=True)
        out.append(("parse_values strict rejects OOR", False))
    except ValueError:
        out.append(("parse_values strict rejects OOR", True))

    sweep = sweep_linear_modes(
        M2, cor.labels, message="East 1", offset=off, plaintext=plain, key=key, N=cor.N)
    out.append(("sweep_linear_modes ranks add first", sweep[0]["mode"] == "add"))

    out.append(("catalog lists known modes", len(catalog()) >= 6))
    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} cipher_validate checks passed")
    sys.exit(0 if n == len(results) else 1)
