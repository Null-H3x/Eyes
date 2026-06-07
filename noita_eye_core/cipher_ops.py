"""Canonical modular stream-cipher combiners shared by EyeStat, EyeSieve and
the workbench.

Every tool re-implements the same handful of position-wise combiners over the
83-symbol alphabet (``(c +/- k) mod N``, Beaufort, ...).  Putting the one
correct definition here -- with round-trip KATs -- means a fix or a validation
covers all consumers at once (the convergence goal from the audit).

A *combiner* maps a plaintext symbol ``p`` and a key symbol ``k`` to a
ciphertext symbol ``c`` in ``Z_N``.  Each combiner ships with its inverse
(recover ``p`` from ``c`` and ``k``) and a key-recovery (recover ``k`` from a
known ``(p, c)`` pair) because depth analysis lives or dies on those being
exactly consistent.

Crucially for depth analysis we record, per mode, the *key sign* ``key_sign``:
how the key enters the ciphertext as a function of plaintext.  For any mode that
is linear in the key with a fixed sign (add/sub/beaufort), differencing two
ciphertexts at the same position cancels the key -- which is the whole basis of
the depth attack in :mod:`depth`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

N_DEFAULT = 83


@dataclass(frozen=True)
class Combiner:
    """A position-wise modular combiner and its exact inverses.

    ``key_sign`` is the coefficient of ``k`` in ``c`` as a linear function of
    ``p`` and ``k`` modulo ``N`` (``+1`` for additive, ``-1`` for Beaufort /
    subtractive-key).  When it is a fixed constant (not ``None``), differencing
    two ciphertexts at a shared position cancels the key.

    ``plain_sign`` is the coefficient of ``p`` in ``c``.  It is what relates the
    *ciphertext* difference to the *plaintext* difference:
    ``c_i - c_j == plain_sign * (p_i - p_j) (mod N)``.  ``None`` means
    non-linear in the plaintext.
    """

    name: str
    encrypt: Callable[[int, int, int], int]   # (p, k, N) -> c
    decrypt: Callable[[int, int, int], int]   # (c, k, N) -> p
    recover_key: Callable[[int, int, int], int]  # (p, c, N) -> k
    key_sign: int | None
    plain_sign: int | None


def _add_enc(p: int, k: int, N: int) -> int:
    return (p + k) % N


def _add_dec(c: int, k: int, N: int) -> int:
    return (c - k) % N


def _add_key(p: int, c: int, N: int) -> int:
    return (c - p) % N


def _sub_enc(p: int, k: int, N: int) -> int:
    # c = p - k  (key subtracted)
    return (p - k) % N


def _sub_dec(c: int, k: int, N: int) -> int:
    return (c + k) % N


def _sub_key(p: int, c: int, N: int) -> int:
    return (p - c) % N


def _beaufort(p: int, k: int, N: int) -> int:
    # Beaufort is an involution: c = k - p, and decrypt is the same map.
    return (k - p) % N


def _beaufort_key(p: int, c: int, N: int) -> int:
    return (c + p) % N


MODES: Dict[str, Combiner] = {
    # c = (p + k) mod N      (Vigenere)
    "add": Combiner("add", _add_enc, _add_dec, _add_key,
                    key_sign=+1, plain_sign=+1),
    # c = (p - k) mod N      (key-subtracted variant)
    "sub": Combiner("sub", _sub_enc, _sub_dec, _sub_key,
                    key_sign=-1, plain_sign=+1),
    # c = (k - p) mod N      (Beaufort; self-inverse)
    "beaufort": Combiner("beaufort", _beaufort, _beaufort, _beaufort_key,
                         key_sign=-1, plain_sign=-1),
}

# Modes whose key enters linearly with a fixed sign, so that c_i - c_j cancels
# the key at a shared position.  These are exactly the modes the depth attack
# can exploit.
LINEAR_MODES = tuple(name for name, m in MODES.items() if m.key_sign is not None)


def get_mode(mode: str) -> Combiner:
    if mode not in MODES:
        raise KeyError(f"unknown combiner mode {mode!r}; "
                       f"valid: {sorted(MODES)}")
    return MODES[mode]


def encrypt_stream(plain: Sequence[int], key: Sequence[int],
                   mode: str = "add", N: int = N_DEFAULT) -> List[int]:
    """Encrypt ``plain`` with position-aligned ``key`` (``len(key) >=
    len(plain)``)."""
    c = get_mode(mode)
    if len(key) < len(plain):
        raise ValueError(
            f"key shorter ({len(key)}) than plaintext ({len(plain)})")
    return [c.encrypt(p, key[t], N) for t, p in enumerate(plain)]


def decrypt_stream(cipher: Sequence[int], key: Sequence[int],
                   mode: str = "add", N: int = N_DEFAULT) -> List[int]:
    c = get_mode(mode)
    if len(key) < len(cipher):
        raise ValueError(
            f"key shorter ({len(key)}) than ciphertext ({len(cipher)})")
    return [c.decrypt(x, key[t], N) for t, x in enumerate(cipher)]


def keystream_from_known(plain: Sequence[int], cipher: Sequence[int],
                         mode: str = "add", N: int = N_DEFAULT) -> List[int]:
    """Recover the keystream from an aligned (plaintext, ciphertext) pair.

    This is the exact arithmetic crib-drag uses: a hypothesised plaintext
    fragment pins the keystream over its span.
    """
    c = get_mode(mode)
    if len(plain) != len(cipher):
        raise ValueError("plain and cipher must be the same length")
    return [c.recover_key(p, x, N) for p, x in zip(plain, cipher)]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    """Round-trip + key-recovery KATs for every combiner across the whole
    alphabet, plus the depth-relevant differencing-cancels-key property."""
    import random
    out: List[tuple[str, bool]] = []
    N = N_DEFAULT

    for name, m in MODES.items():
        ok = True
        for p in range(N):
            for k in range(N):
                c = m.encrypt(p, k, N)
                if not (0 <= c < N):
                    ok = False
                if m.decrypt(c, k, N) != p:
                    ok = False
                if m.recover_key(p, c, N) != k:
                    ok = False
        out.append((f"{name}: decrypt/encrypt/recover_key round-trip (all "
                    f"{N}x{N})", ok))

    # Beaufort must be an involution.
    bf = MODES["beaufort"]
    inv_ok = all(bf.encrypt(bf.encrypt(p, k, N), k, N) == p
                 for p in range(N) for k in range(N))
    out.append(("beaufort is an involution", inv_ok))

    # Stream helpers agree with manual application; keystream_from_known
    # inverts encrypt_stream exactly.
    rng = random.Random(12345)
    plain = [rng.randrange(N) for _ in range(200)]
    key = [rng.randrange(N) for _ in range(200)]
    stream_ok = True
    for mode in MODES:
        cipher = encrypt_stream(plain, key, mode, N)
        if decrypt_stream(cipher, key, mode, N) != plain:
            stream_ok = False
        if keystream_from_known(plain, cipher, mode, N) != key:
            stream_ok = False
    out.append(("stream encrypt/decrypt/keystream_from_known round-trip",
                stream_ok))

    # Differencing cancels the key for every linear mode: with a shared key,
    # (c_i - c_j) mod N depends only on the plaintexts.
    diff_ok = True
    p1 = [rng.randrange(N) for _ in range(300)]
    p2 = [rng.randrange(N) for _ in range(300)]
    key2 = [rng.randrange(N) for _ in range(300)]
    for mode in LINEAR_MODES:
        m = MODES[mode]
        c1 = encrypt_stream(p1, key2, mode, N)
        c2 = encrypt_stream(p2, key2, mode, N)
        sign = m.plain_sign
        for t in range(300):
            cd = (c1[t] - c2[t]) % N
            # c_i - c_j == plain_sign * (p_i - p_j); key cancels in all cases.
            expect = (sign * (p1[t] - p2[t])) % N
            if cd != expect:
                diff_ok = False
                break
    out.append(("differencing cancels key for linear modes", diff_ok))

    # --- edge / error paths -------------------------------------------------
    # Smallest meaningful alphabet (N=2) round-trips for every mode.
    small_ok = True
    for mode in MODES:
        m = MODES[mode]
        for p in range(2):
            for k in range(2):
                if m.decrypt(m.encrypt(p, k, 2), k, 2) != p:
                    small_ok = False
    out.append(("round-trip holds at N=2", small_ok))

    # A large prime-ish N also round-trips (no hidden 83 assumption).
    big_ok = all(
        MODES["add"].decrypt(MODES["add"].encrypt(p, k, 257), k, 257) == p
        for p in (0, 1, 100, 256) for k in (0, 5, 256))
    out.append(("no hidden N=83 assumption (N=257)", big_ok))

    # get_mode rejects unknown modes.
    try:
        get_mode("rot13")
        rejected = False
    except KeyError:
        rejected = True
    out.append(("get_mode rejects unknown mode", rejected))

    # encrypt_stream rejects a too-short key (no silent truncation).
    try:
        encrypt_stream([1, 2, 3], [0, 0], "add", N)
        short_rejected = False
    except ValueError:
        short_rejected = True
    out.append(("encrypt_stream rejects short key", short_rejected))

    # keystream_from_known rejects length mismatch.
    try:
        keystream_from_known([1, 2], [1, 2, 3], "add", N)
        mismatch_rejected = False
    except ValueError:
        mismatch_rejected = True
    out.append(("keystream_from_known rejects length mismatch",
                mismatch_rejected))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} cipher_ops checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
