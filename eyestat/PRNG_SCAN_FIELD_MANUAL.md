# EyeStat PRNG Scan — Offline Field Manual

This file is written for the case where you're on the Ubuntu box running the
scan and **cannot reach claude.ai** (login/email verification is down). It is
self-contained. Everything you need to launch, monitor, diagnose, and recover
a multi-day run is below — no network required.

---

## The one-liner

```bash
source ~/.venvs/eyestat/bin/activate
cd ~/Desktop/Projects/Eyes-main/eyestat
python3 run.py                    # preflight → dir guard → launch
```

Wrap the real run so an SSH drop can't kill it:

```bash
nohup python3 run.py > prng_run.log 2>&1 &
```

---

## Recommended launch sequence (do in order)

1. **Dry run** — see the exact command, execute nothing:
   ```bash
   python3 run.py --dry-run
   ```
2. **Short real slice** — proves the whole path on real hardware in minutes:
   ```bash
   python3 run.py --seed-end 5000000
   ```
   Confirm `[validate] … PASS` prints and, at the end,
   `prng_run_progressive/results/run_summary.txt` exists and reads sanely.
3. **Full run**:
   ```bash
   nohup python3 run.py > prng_run.log 2>&1 &
   ```

---

## Monitoring a live run

```bash
tail -f prng_run.log                                  # live console
cat prng_run_progressive/results/run_summary.txt      # refreshes per shard
nvidia-smi                                            # GPU temp / utilization
```

---

## If it "only ran a short selection"

Run the built-in diagnostic — it reconstructs what happened from the shard
files on disk, no Claude needed:

```bash
python3 run.py --doctor --log prng_run.log
```

It reports how many seeds were actually covered, the fraction of the
Park-Miller space, and — critically — whether coverage has **gaps**. Then:

- **Gaps present + `[skip]` lines in the log** → the run resumed into a dir
  that already held shards and skipped them. This is the usual cause of a
  short run. Fix:
  ```bash
  python3 run.py --fresh          # wipe and start clean
  # or keep the old data and scan elsewhere:
  python3 run.py --output-dir prng_run_v2
  ```
- **Contiguous but short, run still alive** → it's simply mid-scan. A full
  2^31 run is the 30–90 day job; a few million seeds in the first minutes is
  normal. Let it run.
- **Contiguous but short, process exited** → it stopped early. Check the log:
  ```bash
  grep -iE "error|abort|validate|fail|Traceback|exceeds|CuPy|memory" prng_run.log
  ```

---

## Failure modes and fixes

| Symptom | Cause | Fix |
|---|---|---|
| `cupy … IMPORT FAILED` in preflight | driver/venv broke on reboot | reinstall the CuPy wheel matching your CUDA; confirm `nvidia-smi` works |
| `CROSS-VALIDATION FAILED — aborting` | GPU and CPU disagree on 50 seeds | **do not scan** — a numerical/driver mismatch; this guard just saved you a corrupt run |
| `exceeds Park-Miller's seed space` | `--seed-end > 2^31-1` | `run.py` clamps this automatically; if you called the runner directly, cap at 2147483647 |
| refuses to launch, "already holds shard files" | output dir has prior shards | `--resume` to continue, `--fresh` to wipe |
| run exits in seconds, no error, no `[skip]` | shard loop ended early (check `n_shards`) | run `--doctor`; inspect `--dry-run` command for a bad `--shard-size` |
| all-zero / garbage decode at seed 0 | Park-Miller seed 0 is a fixed point | `run.py` starts at seed 1 by default; never scan from 0 |

---

## Recovering an interrupted run

Shards are written atomically (`.tmp` → final rename), so a kill mid-shard
loses only the in-flight shard, never completed ones. To continue:

```bash
python3 run.py --resume
```

Completed shards are detected and skipped; the scan picks up where it stopped.

---

## What a clean result looks like

A finished run with no survivors is the **expected** outcome and is
scientifically meaningful. `run_summary.txt` will show `survivors : 0`, the
covered fraction, and an explicit HONEST SCOPE block. That block matters: a
null covers **only** the enumerated (mode × prng × seed-range) slice — not
other seeds, other PRNG families, or non-PRNG key sources. Record the covered
fraction so a partial null is never mistaken for an exhaustive one.

---

## Flags quick reference

```
python3 run.py --help                 # full flag list
python3 run.py --mode progressive_beaufort   # the -p sign variant
python3 run.py --dry-run              # print command, run nothing
python3 run.py --doctor               # diagnose from disk
python3 run.py --fresh                # wipe output dir first
python3 run.py --resume               # continue a partial run
python3 run.py -- --threshold 11 --workers 12   # pass through to runner
```
