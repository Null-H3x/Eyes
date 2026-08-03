/* eyefast.c -- verified OpenMP port of eyerunner.py (FR95/FR96 lineage).
 *
 * XD-MBYG04K-URS3LF prefix on all fatal messages.
 *
 * G3 from the GPU queue, executed: the audited skeleton filter in C, with
 * the ENTIRE paranoia design ported, not just the arithmetic:
 *   - 14-check startup gate, including HARDCODED FR96 reference vectors:
 *     a build of this program that does not reproduce them refuses to run.
 *   - in-stream canaries; one miss aborts the whole run (all threads).
 *   - checkpoint/resume by 1M-seed chunks.
 *   - hits persisted in full with verify_hit output (drift, bases, packing).
 *   - JSON report schema-compatible with eyerunner.py.
 *
 * PORT CORRECTNESS NOTES (the traps, handled):
 *   T1  LGM state: int64. Schrage margin 4,636 inside 2^31-1 (FR96) holds
 *       trivially in 64-bit. Output i * 4.656612875e-10 -- HIS constant
 *       verbatim, never 1/(2^31-1).
 *   T2  fastrand: uint32_t state; unsigned wraparound is defined behaviour.
 *       Signed int overflow (his C source relies on it) is UB in modern C,
 *       so the port uses unsigned arithmetic with identical bit results.
 *       Seeding is (seed ^ 12) & 0xFFFFFFFF per FR94 (B6).
 *   T3  float determinism: compile with -O2 -ffp-contract=off and WITHOUT
 *       -ffast-math. The two FP expressions (i*SCALE; (hl)*r) contain no
 *       fusable multiply-add. Python float == IEEE binary64 == C double on
 *       x86-64/SSE2; truncation int() == (int) cast on positives.
 *   T4  exactness of the fastrand floor map: v/32768.0 is exact (v < 2^15),
 *       times (i+1) <= 83 stays under 23 significand bits -- exact.
 *   T5  seed 0: SKIPPED for LGM generators (his Next() asserts(seed), B1);
 *       TESTED for fastrand generators. eyerunner.py skipped seed 0 for all
 *       generators, silently excluding the fastrand stream with initial
 *       state 12 (seed^12 is a bijection, so no other seed covers it).
 *       Improvement P1, gate-checked.
 *
 * BUILD:   gcc -O2 -fopenmp -ffp-contract=off -o eyefast eyefast.c
 * SABOTAGE BUILD (FR95 test 2 -- filter dies mid-run, canary must catch):
 *          gcc -O2 -fopenmp -ffp-contract=off -DSABOTAGE=60000 -o eyefast_sab eyefast.c
 *
 * USAGE:
 *   ./eyefast --selftest
 *   ./eyefast --parity > decks.txt          (cross-check vs eyerunner.py)
 *   ./eyefast --gen fy_fastrand_floor --start 0 --count 4294967296 \
 *             --out g2a.json --threads 32 [--resume]
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define XD "XD-MBYG04K-URS3LF"
#define N 83
#define CHUNK 1000000LL

static void die(const char *msg) {
    fprintf(stderr, "%s %s\n", XD, msg);
    exit(2);
}

/* ---------------------------------------------------------- skeleton */

/* components as (glyph, delta) pairs -- identical to eyerunner.py C1..C4 */
static const int C1g[]={0,1,5,6,7,9,10,17,20,27,30,34,41,45,47,48,50,57,62,63,64,68,71,79,81};
static const int C1d[]={0,3,7,34,36,58,55,29,39,1,66,61,69,60,35,82,8,33,28,31,81,65,38,57,54};
static const int C2g[]={13,19,23,25,44,46,49,60,66,72,78};
static const int C2d[]={0,53,4,82,1,31,52,81,55,35,25};
static const int C3g[]={16,21,26,40,42,67,73};
static const int C3d[]={0,58,1,57,35,31,2};
static const int C4g[]={4,35,37};
static const int C4d[]={0,55,57};
static const int *COMPG[4]={C1g,C2g,C3g,C4g};
static const int *COMPD[4]={C1d,C2d,C3d,C4d};
static const int COMPN[4]={25,11,7,3};

static int RELa[400], RELb[400], RELd[400];
static int NREL = 0;
static int INV83[N];

static void build_skeleton(void) {
    for (int x = 1; x < N; x++) {            /* modular inverses, N prime */
        long long r = 1, b = x, e = N - 2;
        while (e) { if (e & 1) r = r * b % N; b = b * b % N; e >>= 1; }
        INV83[x] = (int)r;
    }
    NREL = 0;
    for (int c = 0; c < 4; c++)
        for (int i = 0; i < COMPN[c]; i++)
            for (int j = i + 1; j < COMPN[c]; j++) {
                int d = (COMPD[c][j] - COMPD[c][i]) % N;
                if (d < 0) d += N;
                if (d) {
                    RELa[NREL] = COMPG[c][i];
                    RELb[NREL] = COMPG[c][j];
                    RELd[NREL] = d;
                    NREL++;
                }
            }
}

#ifdef SABOTAGE
static long long sk_calls = 0;               /* FR95 test 2 reproduction */
#endif

static int skeleton_ok(const int *p) {
#ifdef SABOTAGE
    #pragma omp atomic
    sk_calls++;
    if (sk_calls > (long long)SABOTAGE) return 0;   /* filter silently dies */
#endif
    int diff = p[RELb[0]] - p[RELa[0]];
    diff %= N; if (diff < 0) diff += N;
    int drift = (int)((long long)diff * INV83[RELd[0]] % N);
    if (drift == 0) return 0;
    for (int k = 0; k < NREL; k++) {
        int dd = p[RELb[k]] - p[RELa[k]];
        dd %= N; if (dd < 0) dd += N;
        if (dd != (int)((long long)drift * RELd[k] % N)) return 0;
    }
    return 1;
}

static int drift_of(const int *p) {
    int diff = p[RELb[0]] - p[RELa[0]];
    diff %= N; if (diff < 0) diff += N;
    return (int)((long long)diff * INV83[RELd[0]] % N);
}

static void invert(const int *p, int *o) {
    for (int i = 0; i < N; i++) o[p[i]] = i;
}

typedef struct { int drift, packing_ok, relations_ok, bases[4]; } Verify;

static Verify verify_hit(const int *p) {
    Verify v; v.drift = drift_of(p); v.relations_ok = skeleton_ok(p);
    v.packing_ok = 0;
    for (int i = 0; i < 4; i++) v.bases[i] = -1;
    if (v.drift == 0) return v;
    int seen[N]; memset(seen, 0, sizeof seen);
    int ok = 1, total = 0;
    for (int c = 0; c < 4; c++) {
        int g0 = COMPG[c][0];
        int base = p[g0] - v.drift * COMPD[c][0] % N;
        base %= N; if (base < 0) base += N;
        v.bases[c] = base;
        for (int i = 0; i < COMPN[c]; i++) {
            int g = COMPG[c][i];
            int want = (base + v.drift * COMPD[c][i]) % N;
            if (p[g] != want) ok = 0;
            if (seen[p[g]]) ok = 0;
            seen[p[g]] = 1; total++;
        }
    }
    v.packing_ok = ok && total == 46;
    return v;
}

/* --------------------------------------------------------- generators */

#define M31 2147483647LL
#define SCALE 4.656612875e-10          /* HIS constant verbatim (FR96) */

typedef struct { long long s; } Lgm;

static void lgm_init(Lgm *r, long long seed) {
    if (seed == 0) die("seed 0 invalid for LGM: his Next() asserts(seed)");
    if (seed <= 0 || seed >= M31)
        die("LGM seed outside [1, 2^31): (long)seed cast diverges");
    r->s = seed;
}
static double lgm_next(Lgm *r) {
    long long i = r->s;
    long long hi = i / 127773LL;
    long long lo = i - hi * 127773LL;
    i = 16807LL * lo - 2836LL * hi;
    if (i <= 0) i += M31;
    r->s = i;
    return (double)i * SCALE;
}
static int lgm_random(Lgm *r, int low, int high) {
    return low + (int)((double)(high - low + 1) * lgm_next(r));
}

static void fy_lgm(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    for (int i = N - 1; i > 0; i--) {
        int j = lgm_random(&r, 0, i);
        if (j > i) die("index > i: SCALE constant wrong, run invalid");  /* B3 */
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void fy_lgm_fwd(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    for (int i = 0; i < N - 1; i++) {
        int j = lgm_random(&r, i, N - 1);
        if (j > N - 1) die("index out of range: run invalid");
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}

static void fy_fastrand_floor(long long seed, int *p) {
    uint32_t g = ((uint32_t)seed) ^ 12u;                /* B6: seed ^ 12 */
    for (int i = 0; i < N; i++) p[i] = i;
    for (int i = N - 1; i > 0; i--) {
        g = 214013u * g + 2531011u;                     /* defined wrap  */
        uint32_t v = (g >> 16) & 0x7FFFu;
        int j = (int)(((double)v / 32768.0) * (double)(i + 1));   /* T4 */
        if (j > i) die("fastrand floor index > i: run invalid");
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void fy_fastrand_mod(long long seed, int *p) {
    uint32_t g = ((uint32_t)seed) ^ 12u;
    for (int i = 0; i < N; i++) p[i] = i;
    for (int i = N - 1; i > 0; i--) {
        g = 214013u * g + 2531011u;
        uint32_t v = (g >> 16) & 0x7FFFu;
        int j = (int)(v % (uint32_t)(i + 1));
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}

/* ---- FR116: DOUBLE back-to-back Fisher-Yates ------------------------------
 * One seed, ONE continuing RNG stream, TWO consecutive passes over the deck.
 * FR99 exhausted SINGLE shuffles; the double idiom -- his documented habit --
 * was only ever swept to 2M seeds. Direction is a free choice per pass, so all
 * four combinations are covered.                                            */

static void lgm_pass_desc(Lgm *r, int *p) {
    for (int i = N - 1; i > 0; i--) {
        int j = lgm_random(r, 0, i);
        if (j > i) die("index > i: SCALE constant wrong, run invalid");
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void lgm_pass_asc(Lgm *r, int *p) {
    for (int i = 0; i < N - 1; i++) {
        int j = lgm_random(r, i, N - 1);
        if (j > N - 1) die("index out of range: run invalid");
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void fy_lgm_dd(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    lgm_pass_desc(&r, p); lgm_pass_desc(&r, p);
}
static void fy_lgm_aa(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    lgm_pass_asc(&r, p); lgm_pass_asc(&r, p);
}
static void fy_lgm_da(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    lgm_pass_desc(&r, p); lgm_pass_asc(&r, p);
}
static void fy_lgm_ad(long long seed, int *p) {
    Lgm r; lgm_init(&r, seed);
    for (int i = 0; i < N; i++) p[i] = i;
    lgm_pass_asc(&r, p); lgm_pass_desc(&r, p);
}

static uint32_t fr_next(uint32_t *g) {
    *g = 214013u * (*g) + 2531011u;
    return ((*g) >> 16) & 0x7FFFu;
}
static void fr_pass_floor(uint32_t *g, int *p) {
    for (int i = N - 1; i > 0; i--) {
        uint32_t v = fr_next(g);
        int j = (int)(((double)v / 32768.0) * (double)(i + 1));
        if (j > i) die("fastrand floor index > i: run invalid");
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void fr_pass_mod(uint32_t *g, int *p) {
    for (int i = N - 1; i > 0; i--) {
        uint32_t v = fr_next(g);
        int j = (int)(v % (uint32_t)(i + 1));
        int t = p[i]; p[i] = p[j]; p[j] = t;
    }
}
static void fy_fr_floor_dd(long long seed, int *p) {
    uint32_t g = ((uint32_t)seed) ^ 12u;
    for (int i = 0; i < N; i++) p[i] = i;
    fr_pass_floor(&g, p); fr_pass_floor(&g, p);
}
static void fy_fr_mod_dd(long long seed, int *p) {
    uint32_t g = ((uint32_t)seed) ^ 12u;
    for (int i = 0; i < N; i++) p[i] = i;
    fr_pass_mod(&g, p); fr_pass_mod(&g, p);
}

typedef void (*GenFn)(long long, int *);
typedef struct { const char *name; GenFn fn; int lgm; } Gen;
#define NGENS 10
static const Gen GENS[NGENS] = {
    {"fy_lgm",            fy_lgm,            1},
    {"fy_lgm_fwd",        fy_lgm_fwd,        1},
    {"fy_fastrand_floor", fy_fastrand_floor, 0},
    {"fy_fastrand_mod",   fy_fastrand_mod,   0},
    /* FR116 double back-to-back variants */
    {"fy_lgm_dd",         fy_lgm_dd,         1},
    {"fy_lgm_aa",         fy_lgm_aa,         1},
    {"fy_lgm_da",         fy_lgm_da,         1},
    {"fy_lgm_ad",         fy_lgm_ad,         1},
    {"fy_fr_floor_dd",    fy_fr_floor_dd,    0},
    {"fy_fr_mod_dd",      fy_fr_mod_dd,      0},
};

/* ------------------------------------------------- xorshift (internal) */
/* For gate shuffles and canary construction only -- never a tested stream */
static uint64_t xs_state = 0x9E3779B97F4A7C15ULL;
static uint64_t xs64(void) {
    uint64_t x = xs_state;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return xs_state = x;
}
static uint32_t xs_below(uint32_t n) { return (uint32_t)(xs64() % n); }

/* ----------------------------------------------------------- canaries */

static int canaries[64][N];
static int n_canaries = 0;

static int make_consistent(int drift, const int *bases, int *out) {
    int q[N]; for (int i = 0; i < N; i++) q[i] = -1;
    int used[N]; memset(used, 0, sizeof used);
    for (int c = 0; c < 4; c++)
        for (int i = 0; i < COMPN[c]; i++) {
            int val = (bases[c] + drift * COMPD[c][i]) % N;
            if (val < 0) val += N;
            if (used[val]) return 0;              /* packing violated */
            used[val] = 1;
            q[COMPG[c][i]] = val;
        }
    int freev[N], nf = 0;
    for (int v = 0; v < N; v++) if (!used[v]) freev[nf++] = v;
    for (int i = nf - 1; i > 0; i--) {            /* shuffle free values */
        int j = (int)xs_below((uint32_t)(i + 1));
        int t = freev[i]; freev[i] = freev[j]; freev[j] = t;
    }
    int k = 0;
    for (int g = 0; g < N; g++) out[g] = (q[g] >= 0) ? q[g] : freev[k++];
    return 1;
}

static void build_canaries(int want) {
    int base_sets[4][4]; int nb = 0; int tmp[N];
    for (long tries = 0; tries < 400000 && nb < 4; tries++) {
        int b[4] = {0, (int)xs_below(N), (int)xs_below(N), (int)xs_below(N)};
        if (make_consistent(1, b, tmp)) memcpy(base_sets[nb++], b, sizeof b);
    }
    if (nb == 0) die("no valid packing found for canaries");
    n_canaries = 0;
    for (int bi = 0; bi < nb && n_canaries < want; bi++)
        for (int drift = 1; drift < N && n_canaries < want; drift++) {
            int sb[4];                          /* FR53: bases scale WITH drift */
            for (int c = 0; c < 4; c++) sb[c] = (int)(( (long long)drift * base_sets[bi][c]) % N);
            if (make_consistent(drift, sb, tmp) && skeleton_ok(tmp))
                memcpy(canaries[n_canaries++], tmp, sizeof tmp);
        }
    if (n_canaries < want) die("could not build requested canaries");
}

/* ------------------------------------------------------- startup gate */

/* FR96 reference vectors, seed 1234 -- Python-independent ground truth.
 * A build that does not reproduce these is not testing the same stream. */
static const int REF_lgm[12]     = {21,20,5,53,3,76,40,47,39,6,23,41};
static const int REF_lgm_fwd[12] = {0,27,35,80,38,20,10,61,26,39,1,3};
static const int REF_fr_floor[12]= {21,14,67,4,32,23,73,58,17,2,19,16};
static const int REF_fr_mod[12]  = {8,64,43,65,16,82,15,71,11,26,14,54};

static int gate_pass = 0, gate_total = 0;
static char gate_json[8192];

static void gk(const char *name, int cond, const char *detail) {
    char line[512];
    snprintf(line, sizeof line, "%s{\"check\":\"%s\",\"pass\":%s,\"detail\":\"%s\"}",
             gate_total ? "," : "", name, cond ? "true" : "false", detail);
    strncat(gate_json, line, sizeof gate_json - strlen(gate_json) - 1);
    gate_total++;
    if (cond) { gate_pass++; printf("  %-28s PASS %s\n", name, detail); }
    else { printf("  %-28s FAIL %s\n", name, detail); die("GATE FAIL"); }
}

static int refcmp(const int *p, const int *ref) {
    for (int i = 0; i < 12; i++) if (p[i] != ref[i]) return 0;
    return 1;
}

static void gate(void) {
    char d[128]; int p[N], q[N];
    gate_json[0] = 0;

    Lgm r; lgm_init(&r, 1); lgm_next(&r);
    snprintf(d, sizeof d, "%lld", r.s);
    gk("park_miller_kat_1", r.s == 16807, d);
    lgm_next(&r);
    snprintf(d, sizeof d, "%lld", r.s);
    gk("park_miller_kat_2", r.s == 282475249, d);
    snprintf(d, sizeof d, "%d", NREL);
    gk("relation_count", NREL == 379, d);

    for (int g = 0; g < NGENS; g++) {
        long long probes[3] = {1, 1234, GENS[g].lgm ? 1500000000LL : 4294967295LL};
        int ok = 1;
        for (int s = 0; s < 3; s++) {
            GENS[g].fn(probes[s], p);
            int seen[N]; memset(seen, 0, sizeof seen);
            for (int i = 0; i < N; i++) { if (p[i]<0||p[i]>=N||seen[p[i]]) ok=0; else seen[p[i]]=1; }
        }
        char nm[64]; snprintf(nm, sizeof nm, "permutation_%s", GENS[g].name);
        gk(nm, ok, "");
    }
    /* P1: fastrand seed 0 is a valid stream (state 12) and must be covered */
    fy_fastrand_floor(0, p);
    { int seen[N]; memset(seen,0,sizeof seen); int ok=1;
      for (int i=0;i<N;i++){ if(seen[p[i]]) ok=0; seen[p[i]]=1; }
      gk("fastrand_seed0_valid", ok, "state 12, previously skipped"); }

    build_canaries(8);
    int allc = 1;
    for (int i = 0; i < 8; i++) if (!skeleton_ok(canaries[i])) allc = 0;
    gk("positive_control", allc, "8 canaries");

    int bad = 0;
    for (int t = 0; t < 20000; t++) {
        for (int i = 0; i < N; i++) p[i] = i;
        for (int i = N - 1; i > 0; i--) {
            int j = (int)xs_below((uint32_t)(i + 1));
            int tt = p[i]; p[i] = p[j]; p[j] = tt;
        }
        if (skeleton_ok(p)) bad++;
    }
    snprintf(d, sizeof d, "%d/20000 false positives", bad);
    gk("negative_control", bad == 0, d);

    snprintf(d, sizeof d, "%d", drift_of(canaries[0]));
    gk("drift_recovery", drift_of(canaries[0]) != 0, d);
    Verify v = verify_hit(canaries[0]);
    snprintf(d, sizeof d, "%d", v.drift);
    gk("verify_hit_on_canary", v.packing_ok && v.relations_ok, d);
    for (int i = 0; i < N; i++) q[i] = i;
    q[0] = 1; q[1] = 0;
    gk("verify_hit_rejects_bad", !verify_hit(q).packing_ok, "");
    int indep = 0; for (int c = 0; c < 4; c++) indep += COMPN[c] - 1; indep -= 1;
    snprintf(d, sizeof d, "%d", indep);
    gk("independent_constraints", indep == 41, d);

    fy_lgm(1234, p);            gk("refvec_fy_lgm",            refcmp(p, REF_lgm),      "FR96");
    fy_lgm_fwd(1234, p);        gk("refvec_fy_lgm_fwd",        refcmp(p, REF_lgm_fwd),  "FR96");
    fy_fastrand_floor(1234, p); gk("refvec_fy_fastrand_floor", refcmp(p, REF_fr_floor), "FR96");
    fy_fastrand_mod(1234, p);   gk("refvec_fy_fastrand_mod",   refcmp(p, REF_fr_mod),   "FR96");
    printf("gate %d/%d green\n", gate_pass, gate_total);
}

/* -------------------------------------------------------------- sweep */

typedef struct { long long seed; int dir; Verify v; int perm[N]; } Hit;
#define MAXHITS 256
static Hit hits[MAXHITS]; static int nhits = 0;

static volatile int aborted = 0;
static long long ck_planted = 0, ck_caught = 0;

static void sweep(const Gen *G, long long start, long long count,
                  const char *out_path, long long n_can, int nthreads,
                  int resume) {
    char ckpath[512]; snprintf(ckpath, sizeof ckpath, "%s.ckpt", out_path);
    long long nchunks = (count + CHUNK - 1) / CHUNK;
    char *done = calloc(nchunks, 1);
    long long resumed_seeds = 0;
    if (resume) {
        FILE *f = fopen(ckpath, "r");
        if (f) { long long c;
            while (fscanf(f, "%lld", &c) == 1)
                if (c >= 0 && c < nchunks && !done[c]) { done[c] = 1; resumed_seeds += CHUNK; }
            fclose(f);
            printf("resumed: %lld chunks (%lld seeds) already complete\n",
                   resumed_seeds / CHUNK, resumed_seeds);
        }
    }
    FILE *ck = fopen(ckpath, resume ? "a" : "w");
    if (!ck) die("cannot open checkpoint file");

    double t0 = (double)time(NULL);
    long long done_seeds = 0;

#ifdef _OPENMP
    omp_set_num_threads(nthreads);
#endif
    #pragma omp parallel for schedule(dynamic, 1)
    for (long long c = 0; c < nchunks; c++) {
        if (done[c] || aborted) continue;
        long long lo = start + c * CHUNK;
        long long hi = lo + CHUNK; if (hi > start + count) hi = start + count;
        int p[N], q[N];
        long long my_planted = 0, my_caught = 0;
        for (long long s = lo; s < hi && !aborted; s++) {
            if (s == 0 && G->lgm) continue;                    /* B1, T5 */
            if (G->lgm && s >= M31) continue;                  /* B2 range */
            if (n_can > 0 && (s % n_can) == 0) {               /* canary */
                my_planted++;
                const int *cn = canaries[(int)(((unsigned long long)s) % (unsigned)n_canaries)];
                if (skeleton_ok(cn)) my_caught++;
                else {
                    fprintf(stderr, "%s CANARY MISSED at seed %lld -- filter is dead, run invalid\n", XD, s);
                    aborted = 1;
                    break;
                }
            }
            G->fn(s, p);
            for (int dir = 0; dir < 2; dir++) {
                const int *cand;
                if (dir == 0) cand = p; else { invert(p, q); cand = q; }
                if (skeleton_ok(cand)) {
                    Verify v = verify_hit(cand);
                    #pragma omp critical
                    if (nhits < MAXHITS) {
                        hits[nhits].seed = s; hits[nhits].dir = dir; hits[nhits].v = v;
                        memcpy(hits[nhits].perm, cand, sizeof(int) * N);
                        nhits++;
                        printf("HIT  gen=%s seed=%lld dir=%s drift=%d packing_ok=%d\n",
                               G->name, s, dir ? "inv" : "fwd", v.drift, v.packing_ok);
                        if (!v.packing_ok)
                            printf("     WARNING: packing FAILED -- treat as a bug, not a find\n");
                    }
                }
            }
        }
        #pragma omp critical
        {
            ck_planted += my_planted; ck_caught += my_caught;
            if (!aborted) {
                done_seeds += (hi - lo);
                fprintf(ck, "%lld\n", c); fflush(ck);
                double el = (double)time(NULL) - t0; if (el < 1) el = 1;
                printf("  chunk %lld/%lld  %.0f seeds/s  hits=%d  canaries %lld/%lld\n",
                       c + 1, nchunks, (double)done_seeds / el, nhits, ck_caught, ck_planted);
                fflush(stdout);
            }
        }
    }
    fclose(ck);
    if (aborted) die("run VOID: canary missed (see above)");
    if (ck_planted == 0 && n_can > 0)
        die("no canaries planted -- cannot certify the filter was live");
    if (ck_caught != ck_planted) die("canary mismatch");

    double el = (double)time(NULL) - t0; if (el < 1) el = 1;
    FILE *o = fopen(out_path, "w");
    if (!o) die("cannot open output");
    fprintf(o, "{\n \"version\": \"eyefast-1.0-c (FR98)\",\n"
               " \"port_of\": \"eyerunner-1.0 (FR95)\",\n"
               " \"generator\": \"%s\",\n \"seed_start\": %lld,\n"
               " \"seed_count\": %lld,\n \"seeds_tested\": %lld,\n"
               " \"directions\": [\"fwd\", \"inv\"],\n \"candidates\": %lld,\n"
               " \"elapsed_s\": %.1f,\n \"rate_seeds_per_s\": %.1f,\n"
               " \"resumed_from\": %lld,\n \"threads\": %d,\n"
               " \"relations_used\": %d,\n \"glyphs_used\": 46,\n"
               " \"filter\": \"skeleton consistency, one shared drift over all relations\",\n"
               " \"independent_constraints\": 41,\n"
               " \"selectivity\": \"83^-41 (~1e-78); FR96 corrected the earlier 83^-378\",\n"
               " \"selectivity_note\": \"necessary-not-sufficient: 46 of 56 glyphs; verify hits downstream\",\n"
               " \"canaries_planted\": %lld,\n \"canaries_caught\": %lld,\n"
               " \"canary_integrity\": %s,\n \"hit_count\": %d,\n \"hits\": [",
            G->name, start, count, resumed_seeds + done_seeds,
            (resumed_seeds + done_seeds) * 2, el,
            (double)done_seeds / el, resumed_seeds, nthreads, NREL,
            ck_planted, ck_caught,
            (ck_caught == ck_planted && ck_planted > 0) ? "true" : "false", nhits);
    for (int h = 0; h < nhits; h++) {
        fprintf(o, "%s\n  {\"generator\": \"%s\", \"seed\": %lld, \"direction\": \"%s\","
                   " \"drift\": %d, \"packing_ok\": %s, \"bases\": [%d,%d,%d,%d],"
                   " \"permutation\": [", h ? "," : "", G->name, hits[h].seed,
                hits[h].dir ? "inv" : "fwd", hits[h].v.drift,
                hits[h].v.packing_ok ? "true" : "false",
                hits[h].v.bases[0], hits[h].v.bases[1], hits[h].v.bases[2], hits[h].v.bases[3]);
        for (int i = 0; i < N; i++) fprintf(o, "%s%d", i ? "," : "", hits[h].perm[i]);
        fprintf(o, "]}");
    }
    fprintf(o, "],\n \"reference_vectors_seed_1234\": {"
               "\"fy_lgm\": [21,20,5,53,3,76,40,47,39,6,23,41],"
               "\"fy_lgm_fwd\": [0,27,35,80,38,20,10,61,26,39,1,3],"
               "\"fy_fastrand_floor\": [21,14,67,4,32,23,73,58,17,2,19,16],"
               "\"fy_fastrand_mod\": [8,64,43,65,16,82,15,71,11,26,14,54]},\n"
               " \"gate\": [%s]\n}\n", gate_json);
    fclose(o);
    printf("DONE  hits=%d  canaries %lld/%lld  %.0f seeds/s  -> %s\n",
           nhits, ck_caught, ck_planted, (double)done_seeds / el, out_path);
}

/* --------------------------------------------------------------- main */

static void parity_dump(void) {
    /* probe seeds across magnitude ranges; Python side re-runs these */
    long long lgm_probes[] = {1,2,3,7,1234,99991,123456789,1500000000,2147483646};
    long long fr_probes[]  = {0,1,2,1234,99991,123456789,2147483646,2147483648LL,
                              3999999999LL,4294967295LL};
    int p[N];
    xs_state = 20260726ULL;
    for (int g = 0; g < NGENS; g++) {
        int nlp = (int)(sizeof lgm_probes / sizeof *lgm_probes);
        int nfp = (int)(sizeof fr_probes / sizeof *fr_probes);
        int np = GENS[g].lgm ? nlp : nfp;
        const long long *probes = GENS[g].lgm ? lgm_probes : fr_probes;
        for (int s = 0; s < np; s++) {
            GENS[g].fn(probes[s], p);
            printf("%s %lld", GENS[g].name, probes[s]);
            for (int i = 0; i < N; i++) printf(" %d", p[i]);
            printf("\n");
        }
        for (int t = 0; t < 50; t++) {          /* 50 random probes each */
            long long s = GENS[g].lgm
                ? (long long)(1 + xs64() % (M31 - 1))
                : (long long)(xs64() & 0xFFFFFFFFULL);
            GENS[g].fn(s, p);
            printf("%s %lld", GENS[g].name, s);
            for (int i = 0; i < N; i++) printf(" %d", p[i]);
            printf("\n");
        }
    }
}

int main(int argc, char **argv) {
    build_skeleton();
    const char *gen = "fy_lgm", *out = "eyefast.json";
    long long start = 1, count = 1000000, n_can = 10000;
    int threads = 1, resume = 0, selftest = 0, parity = 0;
#ifdef _OPENMP
    threads = omp_get_max_threads();
#endif
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--gen") && i+1 < argc) gen = argv[++i];
        else if (!strcmp(argv[i], "--start") && i+1 < argc) start = atoll(argv[++i]);
        else if (!strcmp(argv[i], "--count") && i+1 < argc) count = atoll(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i+1 < argc) out = argv[++i];
        else if (!strcmp(argv[i], "--threads") && i+1 < argc) threads = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--canary-every") && i+1 < argc) n_can = atoll(argv[++i]);
        else if (!strcmp(argv[i], "--resume")) resume = 1;
        else if (!strcmp(argv[i], "--selftest")) selftest = 1;
        else if (!strcmp(argv[i], "--parity")) parity = 1;
        else die("unknown argument");
    }
    if (parity) { parity_dump(); return 0; }
    printf("eyefast-1.0-c (FR98)  port of eyerunner-1.0 (FR95)\n");
    printf("running startup gate...\n");
    gate();
    if (selftest) return 0;
    const Gen *G = NULL;
    for (int i = 0; i < NGENS; i++) if (!strcmp(GENS[i].name, gen)) G = &GENS[i];
    if (!G) die("unknown generator");
    build_canaries(64);
    printf("gate clean; sweeping %lld seeds from %lld with %s on %d threads\n",
           count, start, G->name, threads);
    sweep(G, start, count, out, n_can, threads, resume);
    return 0;
}
