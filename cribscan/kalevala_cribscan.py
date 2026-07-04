#!/usr/bin/env python3
"""kalevala_cribscan.py — high-propensity phrase inventory + isomorph-signature
crib scan of the merged Kalevala (1849 + 1835) against the Noita Eye messages.

Three tiers, from most to least cipher-model-robust:

  T1  REPEAT-LAG: plaintext sequences of length >= L repeating verbatim at the
      exact lags implied by the eyes' within-message isomorph pairs:
        #M   (9, 28) East1   (9, 30) West1   (9, 35) East2
        #C1  (26, 30) West1
        #C0  (24, 35) East2
        #1   (18, 30) West1  (18, 35) East2
      Valid under ANY cipher where isomorph-pair == same plaintext.

  T2  T1 + direct-mode pattern fit (#M strict at the repeat site, #F at t-10).
      Adds the within-window equality structure — valid only if the key is
      locally flat across the 9-symbol window (substitution-like locally).

  T3  PHRASE PROPENSITY: repeated full lines and word n-grams ranked by count;
      each top formula tested for #M/#M- strict fit at every internal offset.

Orthography: w->v merged for all matching (Wäinämöinen == Väinämöinen);
original spellings preserved for display.
"""
import sys, os, re, unicodedata
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isoscan import (PATTERNS, parse_pattern, canonical_pattern,
                     scan_pattern, filter_strict, MASTER_ALPHABET)

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "corpora", "kalevala_finnish_clean.txt")

# (name, length, lag, message) — from validated pattern positions
SIGNATURES = [
    ("#M",  9, 28, "East1"),
    ("#M",  9, 30, "West1"),
    ("#M",  9, 35, "East2"),
    ("#1", 18, 30, "West1"),
    ("#1", 18, 35, "East2"),
    ("#C1", 26, 30, "West1"),
    ("#C0", 24, 35, "East2"),
]
LAG_RANGE = range(20, 46)          # spectrum context around targets
PAT = {name: pat for name, pat, *_ in PATTERNS}


def load_corpus():
    with open(CORPUS, encoding="utf-8") as f:
        return f.read()


def norm_word(w):
    """lowercase, NFC, w->v, strip non-letters."""
    w = unicodedata.normalize("NFC", w.lower()).replace("w", "v")
    return "".join(c for c in w if c in MASTER_ALPHABET)


def build_stream(text):
    """Letters-only stream (w->v merged) + map stream index -> char offset."""
    text_n = unicodedata.normalize("NFC", text.lower()).replace("w", "v")
    idx = {c: i for i, c in enumerate(MASTER_ALPHABET)}
    stream, srcpos = [], []
    for pos, ch in enumerate(text_n):
        if ch in idx:
            stream.append(idx[ch])
            srcpos.append(pos)
    return np.array(stream, dtype=np.int64), srcpos, text_n


def stream_str(stream, a, b):
    return "".join(MASTER_ALPHABET[i] for i in stream[a:b])


def context(text_n, srcpos, s_start, s_len, pad=45):
    a = max(0, srcpos[s_start] - pad)
    b = min(len(text_n), srcpos[min(s_start + s_len, len(srcpos)) - 1] + pad)
    return re.sub(r"\s+", " ", text_n[a:b]).strip()


# ---------------------------------------------------------------- T3 phrases
def phrase_inventory(text, top_n=30):
    lines = [re.sub(r"\s+", " ", l.strip()) for l in text.split("\n")]
    lines = [l for l in lines if len(l) >= 8]
    keyed = Counter(" ".join(norm_word(w) for w in l.split()) for l in lines)
    line_top = [(k, c) for k, c in keyed.most_common(200) if c >= 4][:top_n]

    words = [norm_word(w) for w in re.findall(r"\S+", text)]
    words = [w for w in words if w]
    grams = Counter()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            grams[" ".join(words[i:i + n])] += 1
    gram_top = [(g, c) for g, c in grams.most_common(400)
                if c >= 15 and len(g.replace(" ", "")) >= 8][:top_n]
    return line_top, gram_top


def phrase_pattern_fits(phrases):
    """Test each phrase (letters only) for #M / #M- strict fit at any offset."""
    out = []
    for ph, cnt in phrases:
        letters = ph.replace(" ", "")
        seq = [MASTER_ALPHABET.index(c) for c in letters if c in MASTER_ALPHABET]
        hits = []
        for pname in ("#M", "#M-"):
            pat = PAT[pname]; L = len(pat)
            for off in range(0, len(seq) - L + 1):
                if canonical_pattern(seq[off:off + L]) == pat:
                    hits.append((pname, off, letters[off:off + L]))
        if hits:
            out.append((ph, cnt, hits))
    return out


# ---------------------------------------------------------- T1 repeat lags
def lag_spectrum(stream, length, lags):
    """count of i with stream[i:i+length] == stream[i+lag:i+lag+length]."""
    n = stream.size
    counts = {}
    for lag in lags:
        V = n - lag - length
        if V <= 0:
            counts[lag] = 0
            continue
        eq = stream[:n - lag] == stream[lag:]
        # run-length: window of `length` consecutive equalities
        c = np.convolve(eq.astype(np.int8), np.ones(length, dtype=np.int8),
                        "valid")
        counts[lag] = int((c[:V] == length).sum())
    return counts


def repeat_hits(stream, length, lag):
    n = stream.size
    eq = stream[:n - lag] == stream[lag:]
    c = np.convolve(eq.astype(np.int8), np.ones(length, dtype=np.int8), "valid")
    starts = np.flatnonzero(c == length)
    # collapse runs (a repeat of length k>L yields k-L+1 starts) — keep run heads
    keep = [s for j, s in enumerate(starts) if j == 0 or s != starts[j - 1] + 1]
    return keep


# ------------------------------------------------------------- T2 composite
def composite_scan(stream, lag):
    """#F strict at t, 9-mer at t+10 repeating verbatim at t+10+lag.
    Returns list of t. Also returns relaxed tier (eq-only #F)."""
    fpat = PAT["#F"]
    starts_eq, classes, L = scan_pattern(stream, fpat)
    strict = set(filter_strict(stream, starts_eq, fpat).tolist())
    n = stream.size
    hits_strict, hits_eq = [], []
    for t in starts_eq:
        a = t + 10
        b = a + lag
        if b + 9 > n:
            continue
        if np.array_equal(stream[a:a + 9], stream[b:b + 9]):
            (hits_strict if t in strict else hits_eq).append(int(t))
    return hits_strict, hits_eq


# --------------------------------------------------------------------- main
def main():
    text = load_corpus()
    stream, srcpos, text_n = build_stream(text)
    print(f"corpus stream: {stream.size} letters (w->v merged)\n")

    # ---- T3: phrase inventory
    line_top, gram_top = phrase_inventory(text)
    print("== T3a: top repeated full lines (count >= 4) ==")
    for ph, c in line_top:
        print(f"  {c:4d}x  {ph}")
    print("\n== T3b: top word 2/3-grams (count >= 15, >= 8 letters) ==")
    for g, c in gram_top:
        print(f"  {c:4d}x  {g}")

    fits = phrase_pattern_fits(line_top + gram_top)
    print("\n== T3c: formulas with internal #M / #M- strict fit ==")
    for ph, cnt, hits in fits:
        hs = "; ".join(f"{p}@{o}:{s}" for p, o, s in hits[:4])
        print(f"  {cnt:4d}x  {ph}   [{hs}]")

    # ---- T1: lag spectrum + target-signature hits
    print("\n== T1: repeat-lag spectrum (length 9), lags 20..45 ==")
    spec = lag_spectrum(stream, 9, LAG_RANGE)
    for lag in LAG_RANGE:
        mark = " <== target" if lag in (28, 30, 35) else ""
        bar = "#" * min(60, spec[lag])
        print(f"  lag {lag:2d}: {spec[lag]:4d} {bar}{mark}")

    print("\n== T1: target-signature hits ==")
    all_nine = {}
    for name, length, lag, msg in SIGNATURES:
        hits = repeat_hits(stream, length, lag)
        print(f"\n-- {name} (len {length}, lag {lag}) [{msg}] : "
              f"{len(hits)} run-head hits")
        counted = Counter(stream_str(stream, s, s + length) for s in hits)
        for s in hits[:12]:
            seg = stream_str(stream, s, s + length)
            pat9 = canonical_pattern(stream[s:s + length].tolist())
            print(f"   @{s:6d}  {seg}  pat={pat9}")
            print(f"           ...{context(text_n, srcpos, s, length + lag)}...")
        if length == 9:
            for s in hits:
                seg = stream_str(stream, s, s + 9)
                all_nine.setdefault(seg, []).append((lag, s))

    # ---- T2: within-window fit on T1 survivors
    print("\n== T2a: T1 9-mer hits that ALSO fit #M strictly (direct) ==")
    m_pat = PAT["#M"]
    n_t2 = 0
    for seg, occ in sorted(all_nine.items(), key=lambda kv: -len(kv[1])):
        seq = [MASTER_ALPHABET.index(c) for c in seg]
        if canonical_pattern(seq) == m_pat:
            lags = sorted(set(l for l, _ in occ))
            print(f"  {seg}  lags={lags}  sites={len(occ)}")
            n_t2 += 1
    if n_t2 == 0:
        print("  (none)")

    print("\n== T2b: composite  #F(strict)@t + 9-mer repeat @t+10, lag L ==")
    for lag in (28, 30, 35):
        hs, he = composite_scan(stream, lag)
        print(f"  lag {lag}: strict={len(hs)}  eq-only={len(he)}")
        for t in (hs + he)[:6]:
            tier = "STRICT" if t in hs else "eq"
            print(f"   [{tier}] @{t}: {stream_str(stream, t, t + 19)} | "
                  f"9mer={stream_str(stream, t + 10, t + 19)}")
            print(f"        ...{context(text_n, srcpos, t, 19 + lag + 9)}...")


if __name__ == "__main__":
    main()
