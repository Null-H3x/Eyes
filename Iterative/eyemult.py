#!/usr/bin/env python3
"""
eyemult -- test the community's MULTIPLICATIVE cipher candidate against the
corpus's isomorph structure.

THE CANDIDATE (Dykoine, "Cipher model definition and Brute force guidelines"):

    c[i] = ( k[i] * p[i] + phi ) % 83        with k[i] = r^(i+1) % 83
                                             r a primitive root of 83

Status in that document: *"Require more efficient reverse IoC. Can't brute force
it without a significant way to simplify it, requiring millenia of computation."*

*** IT DOES NOT NEED BRUTE FORCE, AND IT DOES NOT NEED THE IoC. ***

The isomorph alignments collapse it algebraically. If two positions a and b
carry the same plaintext token p, then

    c[a] - phi = r^(a+1) * p          c[b] - phi = r^(b+1) * p
 => (c[a] - phi) = r^(a-b) * (c[b] - phi)

So for ANY candidate (r, phi), every co-plaintext cell in a shared passage must
satisfy that one equation. A passage of L cells gives L constraints on two
unknowns. The whole space is 40 primitive roots x 83 phi = 3320 candidates,
which is instant.

WHY THIS IS DECISIVE. The community's own document establishes that the corpus
contains long isomorphs. Any cipher family must reproduce them. This tests the
multiplicative family against exactly that evidence, with no language
assumption and no IoC.

PRE-REGISTERED:
  G1  a PLANTED multiplicative corpus must be recovered (r, phi) exactly,
      or the test cannot detect a true positive and the run VOIDS.
  G2  a shuffled control must NOT be recovered.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import os, sys, json, random
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
XD="XD-MBYG04K-URS3LF"; N=83

def primitive_roots(p=N):
    out=[]
    for r in range(2,p):
        seen=set(); x=1
        for _ in range(p-1):
            x=(x*r)%p; seen.add(x)
        if len(seen)==p-1: out.append(r)
    return out

def load():
    cj=json.load(open(os.path.join(HERE,"corpus.json")))
    at=json.load(open(os.path.join(HERE,"atlas.json")))["classes"]
    return cj["ciphertexts"], cj["message_labels"], at

def pat(w):
    from collections import defaultdict
    pos=defaultdict(list)
    for i,v in enumerate(w): pos[v].append(i)
    reps=sorted((min(p),p) for v,p in pos.items() if len(p)>1)
    out=['.']*len(w)
    for k,(_,p) in enumerate(reps):
        for q in p: out[q]=chr(ord('A')+k)
    return "".join(out)

def cells(atlas, labels):
    """co-plaintext cell pairs (m1,t1,m2,t2) from the atlas's lettered cells"""
    Lx={l:i for i,l in enumerate(labels)}
    out=[]
    for c in atlas:
        ins=[(Lx[i["message"]],i["start"]) for i in c["instances"]]
        p=c["pattern"]; L=c["length"]
        for x in range(len(ins)):
            for y in range(x+1,len(ins)):
                (m1,s1),(m2,s2)=ins[x],ins[y]
                for k in range(L):
                    if p[k]=='.': continue
                    out.append((m1,s1+k,m2,s2+k))
    return out

def score(cts, pairs, r, phi):
    """fraction of co-plaintext cells satisfying (c[a]-phi) = r^(a-b) (c[b]-phi)"""
    ok=0; tot=0
    for m1,t1,m2,t2 in pairs:
        A=(cts[m1][t1]-phi)%N; B=(cts[m2][t2]-phi)%N
        tot+=1
        if B==0:
            if A==0: ok+=1
            continue
        if A==0: continue
        e=(t1-t2)%(N-1)
        if A==(B*pow(r,e,N))%N: ok+=1
    return ok,tot

def sweep(cts, pairs, roots):
    best=[]
    for r in roots:
        for phi in range(N):
            ok,tot=score(cts,pairs,r,phi)
            best.append((ok/tot if tot else 0, ok, tot, r, phi))
    best.sort(reverse=True)
    return best

def selftest():
    ok=[]
    def ck(n,c,d=""):
        ok.append(c); print(f"  {n:38s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise SystemExit(f"{XD} selftest FAILED: {n}")
    cts, labels, atlas = load()
    roots=primitive_roots()
    ck("t1_primitive_roots", len(roots)==40 and roots[0]==2,
       f"{len(roots)} roots, first {roots[:5]}")
    pairs=cells(atlas,labels)
    ck("t2_cells", len(pairs)>200, f"{len(pairs)} co-plaintext cell pairs")
    # G1: plant a multiplicative corpus with known (r, phi) and recover it
    rng=random.Random(7)
    R,PHI=roots[3],37
    lengths=[len(c) for c in cts]
    P=[[rng.randrange(N) for _ in range(L)] for L in lengths]
    # force the atlas's co-plaintext cells to actually share plaintext
    for m1,t1,m2,t2 in pairs:
        if t1<len(P[m1]) and t2<len(P[m2]): P[m2][t2]=P[m1][t1]
    synth=[[ (pow(R,t+1,N)*P[m][t] + PHI)%N for t in range(L)]
           for m,L in enumerate(lengths)]
    b=sweep(synth,pairs,roots)
    ck("t3_G1_planted_recovered", b[0][3]==R and b[0][4]==PHI and b[0][0]==1.0,
       f"recovered r={b[0][3]} phi={b[0][4]} at {100*b[0][0]:.0f}%")
    # G2: shuffled control must not be recovered
    flat=[v for m in synth for v in m]; rng.shuffle(flat)
    it=iter(flat); shuf=[[next(it) for _ in range(L)] for L in lengths]
    b2=sweep(shuf,pairs,roots)
    ck("t4_G2_control_not_recovered", b2[0][0]<0.5,
       f"best control score {100*b2[0][0]:.1f}%")
    print(f"selftest {sum(ok)}/{len(ok)} green")
    return cts, labels, atlas, roots, pairs

def run(cts, labels, atlas, roots, pairs):
    print("="*70)
    print("EYEMULT -- the multiplicative candidate against the real corpus")
    print("="*70)
    print(f"\n  c[i] = (r^(i+1) * p[i] + phi) % 83")
    print(f"  search space: {len(roots)} primitive roots x {N} phi = "
          f"{len(roots)*N} candidates")
    print(f"  evidence    : {len(pairs)} co-plaintext cell pairs from the atlas\n")
    b=sweep(cts,pairs,roots)
    print(f"  {'rank':>4s} {'r':>3s} {'phi':>4s} {'cells satisfied':>16s} {'%':>7s}")
    print("  "+"-"*40)
    for i,(f,ok2,tot,r,phi) in enumerate(b[:10],1):
        print(f"  {i:4d} {r:3d} {phi:4d} {str(ok2)+'/'+str(tot):>16s} {100*f:6.1f}%")
    import statistics
    scores=[x[0] for x in b]
    print(f"\n  best {100*b[0][0]:.1f}%   mean {100*statistics.mean(scores):.1f}%"
          f"   chance ~{100/N:.1f}%")
    print()
    if b[0][0] > 0.9:
        print("  *** A MULTIPLICATIVE SOLUTION FITS. ***")
    else:
        print("  *** REFUTED. No (r, phi) reproduces the isomorph evidence.")
        print(f"      The best of {len(b)} candidates explains {100*b[0][0]:.1f}% of")
        print(f"      co-plaintext cells, against ~{100/N:.1f}% expected by chance.")
        print()
        print("  This required no brute force over keys and no Index of")
        print("  Coincidence: the isomorph alignments collapse the family to")
        print("  one equation per cell.")

if __name__=="__main__":
    env=selftest()
    if "--selftest" not in sys.argv: run(*env)
