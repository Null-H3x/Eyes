#!/usr/bin/env python3
"""EyeCrack — known-position crib attack on the 4x repeated refrain.

The refrain (West1@38/@68, East2@43/@78, len 15) is the SAME plaintext at 4 KNOWN
positions. Under pure-progressive c[t]=C[(p[t]+t)], a guessed plaintext value at a
known position pins the cipher alphabet ABSOLUTELY (x[c]=p+pos). A correct guess
pins up to ~37 of 83 symbols (=> ~50% corpus decryptable) and lights IoC up across
the whole corpus; a wrong guess contradicts itself.

The refrain's own ciphertext has internal collisions, which force these
ORDERING-INDEPENDENT constraints on any candidate plaintext (mod N=83):
    p[7]=p[4]-3,  p[9]=p[2]-7,  p[10]=p[6]-4,  p[12]=p[3]-9
i.e. a valid 15-symbol guess must satisfy those value relations. Under a natural
A=0,B=1,... ordering these become letter-gap constraints (e.g. letter[7] sits 3
slots before letter[4] in the ordering).

Usage:
    python3 refrain_attack.py "doyoubelievet hi"          # single guess (15 chars)
    python3 refrain_attack.py --wordlist phrases.txt       # rank many by IoC-z
    python3 refrain_attack.py --constraints                # just print the constraints
    python3 refrain_attack.py --alphabet "<83-char order>" "guess"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import refrain as rf          # noqa: E402


def constraints(messages, instances, L):
    seg = messages[instances[0][0]][instances[0][1]:instances[0][1] + L]
    first = {}; out = []
    for i, v in enumerate(seg):
        v = int(v)
        if v in first:
            out.append((first[v], i))
        else:
            first[v] = i
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phrases", nargs="*")
    ap.add_argument("--wordlist")
    ap.add_argument("--alphabet", default=rf.DEFAULT_ALPHABET)
    ap.add_argument("--len", type=int, default=rf.DEFAULT_LEN)
    ap.add_argument("--null", type=int, default=400)
    ap.add_argument("--constraints", action="store_true")
    ap.add_argument("--show", type=int, default=12, help="top survivors to render")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    inst = rf.DEFAULT_INSTANCES
    L = args.len

    print("=" * 70)
    print("EYECRACK — refrain known-position crib attack")
    print("=" * 70)
    cons = constraints(M, inst, L)
    print(f"Target: 4 instances {[ (c.labels[m],p) for m,p in inst]}, length {L}")
    print("Ordering-independent plaintext constraints (mod 83) a valid guess must meet:")
    for i, j in cons:
        print(f"    p[{j}] = p[{i}] - {j - i}")
    print(f"Plaintext-alphabet ordering (hypothesis): '{args.alphabet[:40]}...'")
    if args.constraints:
        return 0

    phrases = list(args.phrases)
    if args.wordlist:
        phrases += [ln.strip() for ln in Path(args.wordlist).read_text().splitlines()
                    if ln.strip()]
    if not phrases:
        print("\nNo phrases given. Provide 15-char guesses or --wordlist.")
        return 0

    rows = []
    for raw in phrases:
        s = raw
        if len(s) < L:
            continue
        for off in range(len(s) - L + 1):
            sub = s[off:off + L]
            pv = rf.phrase_to_values(sub, args.alphabet, N)
            if pv is None:
                continue
            r = rf.attack(M, pv, N, instances=inst, n_null=args.null)
            rows.append((sub, r))

    consistent = [(s, r) for s, r in rows if r.consistent]
    print(f"\n{len(rows)} windows tested; {len(consistent)} pass refrain consistency.")
    consistent.sort(key=lambda sr: sr[1].ioc_z, reverse=True)
    print(f"\n{'phrase':18s} {'pinned':>6} {'cov':>5} {'IoC':>7} {'z':>7}  verdict")
    print("-" * 70)
    for s, r in consistent[:max(args.show, 20)]:
        verdict = ("STRONG — render below" if r.ioc_z >= 6 else
                   "weak" if r.ioc_z >= 3 else "noise")
        print(f"{s:18s} {r.symbols_pinned:>6} {r.coverage:>4.0%} "
              f"{r.ioc:>7.4f} {r.ioc_z:>7.2f}  {verdict}")
    # render the top survivors
    for s, r in consistent[:args.show]:
        if r.ioc_z >= 6:
            print(f"\n--- decryption under guess '{s}' (IoC z={r.ioc_z:.2f}) ---")
            for lab, line in zip(c.labels, rf.render(M, r.pinned, args.alphabet, N)):
                print(f"  {lab}: {line}")
    if not consistent:
        print("  (none consistent — none of these guesses fit the refrain constraints)")
    print("\nREAD: 'z' is the corpus-wide IoC vs a random-refrain null. A correct")
    print("refrain should stand out at z>>6 AND render as language under the right")
    print("ordering. Consistency alone is necessary, not sufficient.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
