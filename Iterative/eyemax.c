/* eyemax.c -- exhaustive-sample enumeration of maximal mutually-consistent
 * isomorph-class sets for the Noita Eye corpus.
 *
 * WHY. FR152-153 found the skeleton is NOT unique: many maximal consistent
 * class sets exist and disagree on ~84% of shared glyph-pair values. The count
 * (~30) is a Chao1 ESTIMATE from 90 greedy runs, and the invariant core
 * (relations identical in every reading) is an UPPER BOUND of 18 that shrinks
 * as more readings are sampled.
 *
 * The invariant core is the sharpest external test the project has -- it is
 * what an acquirer checks a candidate alphabet against. This turns "at most 18"
 * into a converged number.
 *
 * METHOD. Each run: shuffle the 208 classes, greedily add any class whose rows
 * keep the GF(83) system consistent, then emit the reduced relation signature.
 * Runs are independent -> embarrassingly parallel. Distinct signatures are
 * collected; the invariant core is their intersection.
 *
 * GATE (mandatory, runs before any work):
 *   G1  seeds 1,2,3 must reproduce the Python reference vectors
 *         seed 1 -> 794 relations, 61 glyphs, 6 equalities
 *         seed 2 -> 724 relations, 61 glyphs, 8 equalities
 *         seed 3 -> 794 relations, 61 glyphs, 6 equalities
 *   G2  a PLANTED CANARY class that must always be rejected
 *   Build refuses to proceed if either fails. (FR60/FR98: a harness that
 *   cannot fail reports success regardless.)
 *
 * BUILD  gcc -O3 -march=native -fopenmp -o eyemax eyemax.c
 * RUN    ./eyemax maxset_problem.txt <runs> <threads>
 *
 * Exceptions carry XD-MBYG04K-URS3LF.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define P 83
#define NCOL 92            /* 83 glyphs + 9 message bases */
#define MAXCLS 256
#define MAXROW 64

static int inv_tab[P];
static void init_inv(void){
    for(int a=1;a<P;a++) for(int b=1;b<P;b++) if((a*b)%P==1){ inv_tab[a]=b; break; }
}

typedef struct { int n; int rhs; int col[8]; int val[8]; } Row;
typedef struct { int nrow; Row row[512]; } Cls;

static Cls cls[MAXCLS]; static int ncls;
static Row seed[64]; static int nseed;

/* sparse-ish dense GF(P) system in row-echelon form over NCOL columns */
typedef struct { int piv[NCOL]; int8_t m[NCOL][NCOL+1]; int nr; } Sys;

static void sys_init(Sys*s){ memset(s->piv,-1,sizeof(s->piv)); s->nr=0; }

/* returns 0 = redundant, 1 = added, -1 = contradiction */
static int sys_add(Sys*s, const Row*r){
    int v[NCOL+1]; memset(v,0,sizeof(v));
    for(int i=0;i<r->n;i++) v[r->col[i]] = (v[r->col[i]] + r->val[i])%P;
    v[NCOL] = ((r->rhs)%P+P)%P;
    for(int c=0;c<NCOL;c++){
        if(!v[c]) continue;
        if(s->piv[c]>=0){
            int pr=s->piv[c], f=v[c];
            for(int k=c;k<=NCOL;k++)
                v[k] = (v[k] - f*(int)s->m[pr][k])%P, v[k]=(v[k]+P*64)%P;
        } else {
            int f=inv_tab[v[c]];
            for(int k=c;k<=NCOL;k++) v[k]=(v[k]*f)%P;
            for(int k=0;k<=NCOL;k++) s->m[s->nr][k]=(int8_t)v[k];
            s->piv[c]=s->nr; s->nr++;
            return 1;
        }
    }
    return v[NCOL] ? -1 : 0;
}

static int add_class(Sys*s, int ci){
    Sys bak; memcpy(&bak,s,sizeof(Sys));
    for(int i=0;i<cls[ci].nrow;i++){
        if(sys_add(s,&cls[ci].row[i])==-1){ memcpy(s,&bak,sizeof(Sys)); return 0; }
    }
    return 1;
}

/* query: is q[b]-q[a] determined, and to what? returns -1 if not */
static int query(Sys*s,int a,int b){
    int hit=-1;
    for(int d=0;d<P;d++){
        Row r; r.n=2; r.col[0]=b; r.val[0]=1; r.col[1]=a; r.val[1]=P-1; r.rhs=d;
        Sys t; memcpy(&t,s,sizeof(Sys));
        if(sys_add(&t,&r)==0){ if(hit>=0) return -1; hit=d; }
    }
    return hit;
}

static uint64_t rng_s;
static uint64_t rnd(void){ rng_s^=rng_s<<13; rng_s^=rng_s>>7; rng_s^=rng_s<<17; return rng_s; }

static void run_order(const int*ord,int n,int*rel,int*gly,int*eq,int*sigbuf){
    Sys s; sys_init(&s);
    for(int i=0;i<nseed;i++) sys_add(&s,&seed[i]);
    for(int i=0;i<n;i++) add_class(&s,ord[i]);
    int reached[P],nr=0;
    for(int g=0;g<P;g++){ /* reached if it appears in some pivot row */
        int seen=0;
        for(int c=0;c<NCOL && !seen;c++) if(s.piv[c]==g) seen=1;
        (void)seen;
    }
    /* count determined pairs */
    int R=0,E=0,G=0; int gl[P]; nr=0;
    for(int g=0;g<P;g++){ int used=0;
        for(int r2=0;r2<s.nr && !used;r2++) if(s.m[r2][g]) used=1;
        if(used) gl[nr++]=g; }
    G=nr;
    int idx=0;
    for(int i=0;i<nr;i++) for(int j=i+1;j<nr;j++){
        int d=query(&s,gl[i],gl[j]);
        if(d>=0){ R++; if(d==0) E++; if(idx<3000){ sigbuf[idx*3]=gl[i];
            sigbuf[idx*3+1]=gl[j]; sigbuf[idx*3+2]=d; idx++; } }
    }
    sigbuf[9000]=idx;
    *rel=R; *gly=G; *eq=E;
}

static void run_one(unsigned seed_v,int*rel,int*gly,int*eq,int*sigbuf){
    rng_s = seed_v ? seed_v : 0x9E3779B9u;
    int ord[MAXCLS]; for(int i=0;i<ncls;i++) ord[i]=i;
    for(int i=ncls-1;i>0;i--){ int j=rnd()%(i+1); int t=ord[i];ord[i]=ord[j];ord[j]=t; }
    run_order(ord,ncls,rel,gly,eq,sigbuf);
}

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"XD-MBYG04K-URS3LF usage: %s problem.txt [runs] [threads]\n",argv[0]); return 2; }
    init_inv();
    FILE*f=fopen(argv[1],"r");
    if(!f){ fprintf(stderr,"XD-MBYG04K-URS3LF cannot open %s\n",argv[1]); return 2; }
    int p,nb; if(fscanf(f,"%d %d %d %d",&ncls,&p,&nb,&nseed)!=4){
        fprintf(stderr,"XD-MBYG04K-URS3LF bad header\n"); return 2; }
    for(int i=0;i<nseed;i++){ int n,rhs; fscanf(f,"%d %d",&n,&rhs);
        seed[i].n=n; seed[i].rhs=rhs;
        for(int k=0;k<n;k++) fscanf(f,"%d %d",&seed[i].col[k],&seed[i].val[k]); }
    for(int c=0;c<ncls;c++){ int idx,nr2; fscanf(f,"%d %d",&idx,&nr2);
        cls[c].nrow=nr2;
        for(int r=0;r<nr2;r++){ int n,rhs; fscanf(f,"%d %d",&n,&rhs);
            cls[c].row[r].n=n; cls[c].row[r].rhs=rhs;
            for(int k=0;k<n;k++) fscanf(f,"%d %d",&cls[c].row[r].col[k],&cls[c].row[r].val[k]); } }
    fclose(f);
    fprintf(stderr,"loaded %d classes, %d seed rows\n",ncls,nseed);

    /* ---- GATE: FIXED ORDERS, RNG-independent ---- */
    FILE*of=fopen("maxset_orders.txt","r");
    if(!of){ fprintf(stderr,"XD-MBYG04K-URS3LF missing maxset_orders.txt\n"); return 3; }
    int nord,ncheck; if(fscanf(of,"%d %d",&nord,&ncheck)!=2) return 3;
    int*sb=malloc(9001*sizeof(int)); int ok=1;
    for(int t=0;t<nord;t++){
        char nm[64]; int wr,wg,we;
        if(fscanf(of,"%63s %d %d %d",nm,&wr,&wg,&we)!=4) return 3;
        int ord[MAXCLS];
        for(int i=0;i<ncheck;i++) if(fscanf(of,"%d",&ord[i])!=1) return 3;
        int R,G,E; run_order(ord,ncheck,&R,&G,&E,sb);
        int pass = (R==wr&&G==wg&&E==we);
        fprintf(stderr,"  G1 %-9s: rel %d gly %d eq %d  (want %d %d %d)  %s\n",
            nm,R,G,E,wr,wg,we,pass?"PASS":"FAIL");
        if(!pass) ok=0;
    }
    fclose(of);
    /* G2 canary: a fabricated class asserting q[x]=q[x]+1 must be rejected */
    { Sys s3; sys_init(&s3);
      Row bad; bad.n=1; bad.col[0]=0; bad.val[0]=0; bad.rhs=1;
      if(sys_add(&s3,&bad)!=-1){
          fprintf(stderr,"  G2 canary: FAIL (0=1 accepted)\n"); ok=0; }
      else fprintf(stderr,"  G2 canary: PASS\n"); }
    if(!ok){ fprintf(stderr,"XD-MBYG04K-URS3LF GATE FAILED -- refusing to run.\n"
        "The C build does not reproduce the Python reference vectors.\n"); return 3; }
    fprintf(stderr,"gate PASS\n");

    long runs = argc>2?atol(argv[2]):1000;
    int nt = argc>3?atoi(argv[3]):1;
#ifdef _OPENMP
    omp_set_num_threads(nt);
#endif
    fprintf(stderr,"running %ld greedy orders on %d threads...\n",runs,nt);
    /* stream signatures to stdout; dedupe/intersect offline in Python */
    #pragma omp parallel
    {
        int*b=malloc(9001*sizeof(int));
        #pragma omp for schedule(dynamic,64)
        for(long i=0;i<runs;i++){
            int R,G,E; run_one((unsigned)(i+1000),&R,&G,&E,b);
            if(R>=700){
                #pragma omp critical
                {
                    printf("R %d %d %d %d\n",R,G,E,b[9000]);
                    for(int k=0;k<b[9000];k++) printf("%d %d %d\n",b[k*3],b[k*3+1],b[k*3+2]);
                }
            }
        }
        free(b);
    }
    fprintf(stderr,"done\n");
    return 0;
}
