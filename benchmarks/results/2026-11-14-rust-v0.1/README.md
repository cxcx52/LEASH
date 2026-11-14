# Rust frontend-to-backend measurements

Nine end-to-end runs generated, encoded, decoded and verified proofs for binary
R1CS instances with `A = B = C = I` and the all-one assignment. All nine proofs
verified. Each input size used three fresh public setups in a single sequential
process.

| Variables = constraints | Runs | Actual proof bytes, min–max | Prove median (ms) | Verify median (ms) | Encode median (ms) | Decode median (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 3 | 83,923–84,099 | 400.807 | 160.807 | 0.713 | 3.152 |
| 256 | 3 | 84,603–84,731 | 477.447 | 226.623 | 0.643 | 2.815 |
| 1,024 | 3 | 84,787–84,899 | 864.888 | 486.945 | 0.685 | 2.927 |

The sizes count the complete `LEASHR01` proof: its header, source commitment
and scalar replies, ordinary-core messages, and terminal opening. Public
parameters and the circuit are separate verifier inputs. Polynomial
coefficients use the canonical centered, minimum-width bit encoding. The
failed messages from a restarted attempt are not transmitted.

## Profile and environment

- Source revision: `508a5b3ae73825c819e55825bfe6c40f72f9fcbd`, clean before and after the run.
- Default profile: degree 64, modulus 4,294,967,197, source rank 6, 160 source rows, inner rank 24, outer rank 9, 1,024 JL rows and six scalar aggregation challenges.
- One ordinary recursive reduction, full base-16 residue decomposition, cube challenges and deterministic norm budgets.
- Intel Core i9-13980HX, 24 physical cores and 32 logical CPUs; the protocol implementation is single-threaded and uses no GPU.
- Windows 11 build 26300, Rust 1.98.0 and Cargo 1.98.0; release build with the committed lockfile.
- Recorded start: `2026-11-14T15:24:43.237474+00:00`.

The 1,024-variable run with repetition index 0 used one complete-session
restart and took 1,274.292 ms to prove. Its timing includes both attempts.
The other eight runs succeeded on their first attempt. Setup and proof
nonces use OS randomness, so reruns need not have identical proof bytes or
restart counts.

These are small synthetic fixtures. They measure the implemented Rust path;
they do not measure the original paper's large instance, the optimized
seven-layer parameter ledger, an upstream C implementation or a certified
security level. Verification includes reconstructing the public relations
and checking all terminal constraints. Three runs per size give an initial
measurement, not a confidence interval. Peak memory was not measured.

## Records and replay

- [Raw measurements](stdout.jsonl): all nine runs, including setup, codec and restart data.
- [Summary](summary.json): aggregate sizes and medians.
- [Metadata](metadata.json): source, lockfile and log hashes, command and environment.
- [Cargo output](stderr.log): original build and execution log, preserved byte for byte.

To reproduce the measured source in a separate checkout:

```sh
git worktree add --detach ../leash-benchmark 508a5b3ae73825c819e55825bfe6c40f72f9fcbd
cd ../leash-benchmark
python experiments/run_rust_benchmarks.py --out work/replay-rust --rounds 1
```

The output directory must be new. The recorder requires a clean source tree,
checks the lockfile after execution and rejects a missing or failed proof.
Use Rust 1.98.0 to match this measurement's compiler. Later compatibility
commits adjust iterator style and documentation; this report retains the
exact revision actually measured.
