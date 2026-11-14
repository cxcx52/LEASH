# Benchmarks

The Rust frontend and recursive backend can be measured end to end with
`cargo run --release -p leash --example measure -- 1`. The example records
actual serialized proof bytes and separate prove/verify/codec timings on
all-one identity R1CS instances. Its [profile and scope](../docs/rust-library.md)
differ from the earlier Python source-reference batch below.

The first CPU batch records 27 native-source runs, nine challenge-predicate runs and two verification jobs. All 38 processes completed. The [result report](results/2026-11-14-first-cpu/README.md) includes per-run hashes, environment details and raw logs.

| Input size n = k | Runs | Encoded full-witness transport | Whole-flow median |
| ---: | ---: | ---: | ---: |
| 64 | 9 | 5,248 bytes | 78.13 ms |
| 256 | 9 | 9,344 bytes | 273.25 ms |
| 1,024 | 9 | 33,920 bytes | 1,079.03 ms |

Whole-flow time includes generation, commitments, checking, encoding and decoding. The transport carries the full witness. The compact encoding estimates have their own [parameter ledger](../parameters/README.md).

The challenge benchmark compares certified Fourier intervals with the exact SPD predicate on identical inputs. Across nine paired runs, the median warm-time ratio was 180.58; all 96 candidate positions agreed, with zero fallback calls. Cold initialization is recorded separately.

## Run the components

From the repository root, with Python 3.10 or later:

```sh
python -m pip install -e .
python examples/native_frontend_smoke.py --log-size 6 --rows 16 --seed 1
python benchmarks/challenge_membership.py --degree 8 --energy 12 --threshold 10 --samples 8
```

For the recorded degree-64 workload:

```sh
python benchmarks/challenge_membership.py --degree 64 --energy 104 --threshold 30 --samples 32 --seed 20261114
```

The [experiment runner](../experiments/README.md) records complete subprocess runs, configurations, exit status and hashes. The [replay instructions](results/2026-11-14-first-cpu/README.md#reproduce-the-evidence-aggregation) reconstruct the saved batch from its original source revision.
