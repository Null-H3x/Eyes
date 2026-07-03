"""plantlab — shared ground-truth plant generators for the eyeforward modules.

Every paranoia audit in this package is only as honest as its plants. This
module is the single source of planted corpora, so every selftest exercises
the SAME generators and a bug here is caught by the KATs below rather than
silently validating five modules against five slightly-different worlds.

Model families implemented (N prime, default 83):

  pmp          per-message-progressive   c[t] = C[(p[t] + base_m + t) mod N]
  pure         pure-progressive          c[t] = C[(p[t] + base  + t) mod N]
  autokey1     ciphertext chain          c[t] = (E(p[t]) + c[t-1]) mod N
  chain_nz     chain, E has no zero      same, E(p) != 0  =>  doubles impossible
  alberti      Pyry's autokey Alberti    c[t] = C[(p[t] + k_t) mod N],
                                         k_{t+1} = (k_t + g(p[t])) mod N

Plaintext coding: characters are mapped into Z_N by a random INJECTION rho
(the author's value-coding is unknown, so plants must not assume 0..26).

Honest limits: plants use the embedded English sample below; anything trained
on the same text will look better on plants than on truly held-out language.
Selftests that measure *recovery* say so explicitly.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

N_DEFAULT = 83
ALPHABET = " abcdefghijklmnopqrstuvwxyz"

# Original filler text (written for this project; deliberately plain English
# with natural repetition so shared-section and isomorph plants are realistic).
SAMPLE_TEXT = (
    "the work begins before the sun rises and the work continues after the "
    "sun has set the miners walk the long tunnel and count the lamps on the "
    "wall every lamp marks a turn and every turn leads deeper into the rock "
    "the old maps show a river under the mountain and the new maps show the "
    "same river in a different place the foreman keeps a ledger of every "
    "load and every load is weighed twice once at the face and once at the "
    "gate nobody remembers who dug the first shaft but everybody knows the "
    "song about it the song says the mountain gives and the mountain takes "
    "and the wise miner leaves before the third bell in the winter the "
    "water rises and the lower galleries close in the summer the dust "
    "settles on the rails and the carts run quiet the apprentice learns the "
    "names of the seams before the names of the tools and the master checks "
    "the props twice before any charge is set the record of the deep survey "
    "was copied three times and each copy went to a different town so that "
    "no single fire could take the knowledge away"
)


@dataclass
class Plant:
    """A planted corpus with full ground truth attached."""
    model: str
    N: int
    cts: List[List[int]]                 # ciphertexts
    pts: List[str]                       # plaintext chunks (characters)
    pvals: List[List[int]]               # plaintext values in Z_N (rho applied)
    rho: Dict[str, int]                  # char -> value injection
    C: Optional[List[int]] = None        # mixed alphabet (value -> symbol), if any
    q: Optional[List[int]] = None        # C^{-1} (symbol -> position), if any
    bases: Optional[List[int]] = None    # per-message bases / start keys
    E: Optional[Dict[int, int]] = None   # chain substitution, if any
    meta: dict = field(default_factory=dict)

    @property
    def used_chars(self) -> List[str]:
        return sorted(set("".join(self.pts)))


def _chunks(text: str, n_msgs: int, msg_len: int, rng: random.Random) -> List[str]:
    """n_msgs chunks of msg_len chars, starting at word boundaries where
    possible; wraps around the sample if it runs out."""
    body = (text + " ") * (1 + (n_msgs * msg_len) // max(1, len(text)))
    out, pos = [], 0
    for _ in range(n_msgs):
        # nudge start to a word boundary for realism
        while pos < len(body) and body[pos] == " ":
            pos += 1
        out.append(body[pos:pos + msg_len])
        pos += msg_len + rng.randrange(0, 4)
    return out


def _rho(chars: Sequence[str], N: int, rng: random.Random,
         forbid: Optional[set] = None) -> Dict[str, int]:
    pool = [v for v in range(N) if not forbid or v not in forbid]
    vals = rng.sample(pool, len(chars))
    return {ch: v for ch, v in zip(sorted(set(chars)), vals)}


def gen(model: str, *, n_msgs: int = 9, msg_len: int = 115, N: int = N_DEFAULT,
        seed: int = 0, text: str = SAMPLE_TEXT,
        shared_prefix: int = 0, groups=None, group_share: int = 0,
        lengths=None) -> Plant:
    """Generate a plant.

    shared_prefix > 0 : first k chars identical across ALL messages.
    groups+group_share: model the real corpus's TRIPLET structure -- each group
                        (list of message indices) shares its own opening of
                        group_share chars. This is the dominant source of the
                        real corpus's isomorphs, so matching it is what lets a
                        plant reach the observed ~18-pair density.
    lengths           : per-message lengths (defaults to msg_len for all); pass
                        the real corpus lengths to match sparsity exactly.
    """
    rng = random.Random(seed)
    if lengths is None:
        lengths = [msg_len] * n_msgs
    pts = _chunks(text, n_msgs, max(lengths), rng)
    pts = [p[:lengths[i]] for i, p in enumerate(pts)]
    if shared_prefix:
        pref = pts[0][:shared_prefix]
        pts = [pref + p[shared_prefix:] for p in pts]
    if groups and group_share:
        for grp in groups:
            lead = pts[grp[0]][:group_share]
            for gi in grp:
                pts[gi] = lead + pts[gi][group_share:]
    chars = sorted(set("".join(pts)))

    if model in ("pmp", "pure"):
        rho = _rho(chars, N, rng)
        pvals = [[rho[ch] for ch in p] for p in pts]
        C = list(range(N)); rng.shuffle(C)
        q = [0] * N
        for pos, sym in enumerate(C):
            q[sym] = pos
        if model == "pmp":
            bases = [rng.randrange(N) for _ in range(n_msgs)]
        else:
            b = rng.randrange(N); bases = [b] * n_msgs
        cts = [[C[(pv + bases[m] + t) % N] for t, pv in enumerate(pvals[m])]
               for m in range(n_msgs)]
        return Plant(model, N, cts, pts, pvals, rho, C=C, q=q, bases=bases)

    if model in ("autokey1", "chain_nz"):
        rho = _rho(chars, N, rng)
        pvals = [[rho[ch] for ch in p] for p in pts]
        # E: value -> step; chain_nz forbids step 0 so doubles are impossible
        dom = sorted({v for pv in pvals for v in pv})
        steps = [s for s in range(N) if not (model == "chain_nz" and s == 0)]
        img = rng.sample(steps, len(dom))
        E = {v: s for v, s in zip(dom, img)}
        bases = [rng.randrange(N) for _ in range(n_msgs)]      # IVs
        cts = []
        for m, pv in enumerate(pvals):
            c, prev = [], bases[m]
            for v in pv:
                prev = (E[v] + prev) % N
                c.append(prev)
            cts.append(c)
        return Plant(model, N, cts, pts, pvals, rho, bases=bases, E=E)

    if model == "alberti":
        rho = _rho(chars, N, rng)
        pvals = [[rho[ch] for ch in p] for p in pts]
        C = list(range(N)); rng.shuffle(C)
        q = [0] * N
        for pos, sym in enumerate(C):
            q[sym] = pos
        dom = sorted({v for pv in pvals for v in pv})
        g = {v: rng.randrange(1, N) for v in dom}   # rotation from prev plaintext
        bases = [rng.randrange(N) for _ in range(n_msgs)]
        cts = []
        for m, pv in enumerate(pvals):
            k, c = bases[m], []
            for v in pv:
                c.append(C[(v + k) % N])
                k = (k + g[v]) % N
            cts.append(c)
        return Plant(model, N, cts, pts, pvals, rho, C=C, q=q, bases=bases,
                     meta={"g": g})

    if model == "periodic":
        # Vigenere-style PERIODIC key, NO +t ramp:
        #   c[t] = C[(p[t] + key[t mod L]) mod N]
        # This PRESERVES isomorphs (a repeated word at period-aligned offsets
        # gives the same skeleton) yet is NOT per-msg-progressive -- the offset
        # is periodic in t, not linear. It is the critical hard negative: if
        # progressive-chain consistency also passes here, "consistency confirms
        # pmp" is false. Key length coprime-ish to typical spacings.
        rho = _rho(chars, N, rng)
        pvals = [[rho[ch] for ch in p] for p in pts]
        C = list(range(N)); rng.shuffle(C)
        q = [0] * N
        for pos, sym in enumerate(C):
            q[sym] = pos
        keylen = 7
        key = [rng.randrange(N) for _ in range(keylen)]
        # per-message PHASE so shared openings give DIFFERENT ciphertext (a true
        # isomorph, not an exact repeat) -- required to respect C7 (first
        # symbols differ) and to make the discrimination test non-degenerate.
        phase = [rng.randrange(keylen) for _ in range(n_msgs)]
        cts = [[C[(pv + key[(t + phase[m]) % keylen]) % N]
                for t, pv in enumerate(pvals[m])] for m in range(n_msgs)]
        return Plant(model, N, cts, pts, pvals, rho, C=C, q=q,
                     bases=list(phase),
                     meta={"key": key, "keylen": keylen, "phase": phase})

    if model == "beaufort":
        # Beaufort-style PROGRESSIVE (subtractive): c[t] = C[(base_m - p[t] + t)].
        # Isomorph-preserving and progressive, but the plaintext enters with a
        # SIGN FLIP. Tests whether progressive-chain (which assumes +p) is
        # fooled by, or correctly contradicts, a reflected plaintext map.
        rho = _rho(chars, N, rng)
        pvals = [[rho[ch] for ch in p] for p in pts]
        C = list(range(N)); rng.shuffle(C)
        q = [0] * N
        for pos, sym in enumerate(C):
            q[sym] = pos
        bases = [rng.randrange(N) for _ in range(n_msgs)]
        cts = [[C[(bases[m] - pv + t) % N] for t, pv in enumerate(pvals[m])]
               for m in range(n_msgs)]
        return Plant(model, N, cts, pts, pvals, rho, C=C, q=q, bases=bases)

    raise ValueError(f"unknown model {model!r}")


def shuffle_null(cts: Sequence[Sequence[int]], seed: int = 0) -> List[List[int]]:
    """Per-message shuffle: preserves symbol frequencies, destroys position."""
    rng = random.Random(seed)
    out = []
    for ct in cts:
        c = list(ct); rng.shuffle(c); out.append(c)
    return out


def uniform_null(n_msgs: int, msg_len: int, N: int = N_DEFAULT,
                 seed: int = 0) -> List[List[int]]:
    rng = random.Random(seed)
    return [[rng.randrange(N) for _ in range(msg_len)] for _ in range(n_msgs)]


# ---------------------------------------------------------------------------
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []

    # KAT: pmp plant decrypts back to its own plaintext values via q
    p = gen("pmp", seed=1)
    ok = True
    for m, ct in enumerate(p.cts):
        for t, c in enumerate(ct):
            if (p.q[c] - p.bases[m] - t) % p.N != p.pvals[m][t]:
                ok = False
    checks.append(("pmp round-trip via q", ok))

    # pure: all bases equal
    pp = gen("pure", seed=2)
    checks.append(("pure single base", len(set(pp.bases)) == 1))

    # chain_nz: zero adjacent doubles by construction; autokey1 usually not
    cz = gen("chain_nz", seed=3)
    dz = sum(ct[t] == ct[t + 1] for ct in cz.cts for t in range(len(ct) - 1))
    checks.append(("chain_nz forbids doubles", dz == 0))
    a1 = gen("autokey1", seed=3)
    checks.append(("autokey1 round-trip",
                   all((a1.cts[m][t] - (a1.bases[m] if t == 0 else a1.cts[m][t-1]))
                       % a1.N == a1.E[a1.pvals[m][t]]
                       for m in range(9) for t in range(len(a1.cts[m])))))

    # alberti round-trip
    al = gen("alberti", seed=4)
    ok = True
    for m, ct in enumerate(al.cts):
        k = al.bases[m]
        for t, c in enumerate(ct):
            if al.q[c] != (al.pvals[m][t] + k) % al.N:
                ok = False
            k = (k + al.meta["g"][al.pvals[m][t]]) % al.N
    checks.append(("alberti round-trip", ok))

    # periodic round-trip: c[t] = C[(p + key[t mod L])]
    pe = gen("periodic", seed=6)
    kl = pe.meta["keylen"]; key = pe.meta["key"]; ph = pe.meta["phase"]
    checks.append(("periodic round-trip via q",
                   all((pe.q[pe.cts[m][t]] - key[(t + ph[m]) % kl]) % pe.N
                       == pe.pvals[m][t]
                       for m in range(9) for t in range(len(pe.cts[m])))))
    # beaufort round-trip: c[t] = C[(base_m - p + t)]
    bf = gen("beaufort", seed=6)
    checks.append(("beaufort round-trip via q",
                   all((bf.bases[m] - bf.q[bf.cts[m][t]] + t) % bf.N
                       == bf.pvals[m][t]
                       for m in range(9) for t in range(len(bf.cts[m])))))

    # shared_prefix actually shares plaintext
    sp = gen("pmp", seed=5, shared_prefix=20)
    checks.append(("shared_prefix", all(x[:20] == sp.pts[0][:20] for x in sp.pts)))

    # rho is injective; determinism
    checks.append(("rho injective", len(set(p.rho.values())) == len(p.rho)))
    checks.append(("deterministic", gen("pmp", seed=1).cts == p.cts))

    # shuffle null preserves frequencies
    sh = shuffle_null(p.cts, seed=9)
    checks.append(("shuffle preserves freqs",
                   all(sorted(a) == sorted(b) for a, b in zip(sh, p.cts))))
    return checks


if __name__ == "__main__":
    for name, ok in selftest():
        print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
