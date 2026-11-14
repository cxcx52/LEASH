![LaBRADOR audit and repair](assets/labrador.png)

# LEASH: When LaBRADOR's Guarantees Go Astray

This repository audits the proof chain of [LaBRADOR](https://eprint.iacr.org/2022/1341) and develops a rigorous reconstruction. The findings concern probability bounds, source arithmetic, extraction, challenge sampling and concrete parameter accounting. The repair supplies explicit theorems, exact certificates and a record of the resulting costs.

The Rust workspace provides a callable binary R1CS frontend, an ordinary recursive prover/verifier, proof serialization and a CLI. The Python package preserves the arithmetic certificates, challenge predicates and earlier native source reference. Detailed proofs, parameter ledgers and recorded experiments accompany both.

[Rust library](docs/rust-library.md) · [Mathematics](docs/README.md) · [Parameters](parameters/README.md) · [Benchmarks](benchmarks/README.md) · [Downstream papers and repositories](impact/README.md)

## Use the Rust frontend and backend

Build a binary circuit with AND, XOR and NOT gates, pin its public inputs and outputs, and call `setup`, `prove` and `verify`. `prove_relation` and `verify_relation` accept a generic quadratic ring relation directly. Proofs have a canonical byte encoding and can be verified in a separate process.

```sh
cargo test --workspace --all-targets --release --locked
cargo run --release -p leash --example library
cargo run --release -p leash -- demo --out demo-output
cargo run --release -p leash -- verify --parameters demo-output/parameters.json --circuit demo-output/circuit.json --proof demo-output/proof.leash --context leash/example/v1
```

The implemented path uses deterministic norm bounds, full residue decomposition, explicit padding constraints and complete-session retries. The seed-expanded setup and SHAKE Fiat–Shamir compiler are experimental; this release makes no zero-knowledge or certified security-level claim. The generic relation interface exposes its extraction norm slack. [API, CLI and integration guide](docs/rust-library.md) · [Implemented equations](docs/rust-protocol.md).

## Findings and reconstruction

The audit identifies missing premises in several necessary steps of the original argument. An exact lower-tail example exceeds both the strict `2^-128` and `2^-127` projection budgets. Source lifting requires a stronger integer bound and a complete commitment relation. Extraction and recursion require explicit relaxed norms, challenge counts after filtering and an error budget covering complete attempts.

| Part of the proof chain | Result in this repository |
| --- | --- |
| Random projection | A uniform modular JL theorem, honest completeness and an explicit security-parameter family |
| Source relations | Constant and public-input pins, centered lifts, commitment equations and a native binary interface |
| Short challenges | Certified support size after filtering, an exact Fourier predicate and conditional moment bounds |
| Extraction and composition | An ordinary-core extractor, relation-matched recursion and bounded complete restarts |
| Quantitative refinements | Bounded-energy challenges and a cubic-root computational-loss bound for the specified collision experiments |
| Parameters | Exact norm, padding and communication ledgers, with separately recorded lattice-cost estimates |

The [proof-chain assessment](research/notes/critical_path_assessment.md) connects each finding to its evidence. The [claim ledger](docs/status.md) gives the hypotheses and verification status of the replacement results.

## Recorded measurements

The first CPU batch contains 38 completed processes: 27 native-source runs, nine challenge-predicate runs, the 66-test package suite and the 102-file archive check. Measurements use source revision `fac2517e163517540f09cbf866d4a7cae8e3d40e`.

**Environment.** AMD EPYC 7742, Ubuntu 24.04.4 and Python 3.12.3; container limits of 40 CPU equivalents and 200 GiB. Workloads ran sequentially in fresh, single-threaded Python processes. Each native size used three seeds and three repetitions per seed.

| Native input size n = k | Runs | Full-witness transport (bytes) | Whole-flow median (ms) |
| ---: | ---: | ---: | ---: |
| 64 | 9 | 5,248 | 78.13 |
| 256 | 9 | 9,344 | 273.25 |
| 1,024 | 9 | 33,920 | 1,079.03 |

Whole-flow time includes generation, commitments, target and source checks, encoding and decoding. Transport contains the full witness, source commitment and scalar replies.

The exact challenge-membership benchmark compares Fourier intervals with the generic SPD predicate on identical inputs. The median warm-time ratio across nine paired runs was **180.58×**. All 96 candidate positions agreed; the batch used zero fallback calls. Cold initialization is reported separately.

[Full measurements and replay](benchmarks/results/2026-11-14-first-cpu/README.md) · [Machine-readable summary](benchmarks/results/2026-11-14-first-cpu/summary.json) · [Raw records](benchmarks/results/2026-11-14-first-cpu/raw-records.tar.gz)

## Parameter results

The final recorded path has seven ordinary-core layers, ring degree 64, inner rank 24, outer rank 9 and source rank 6. With the bounded-energy challenge family, its prover-message encoding bound is **155.1484375 KiB** per attempt. Adding the native source, source fingerprint and byte padding gives **161,040 bytes (157.265625 KiB)**.

The source fingerprint uses 187 challenge bits; the two core aggregation challenges total 1,960 bytes across seven layers. Dense independent JL matrices still dominate verifier communication, at about 67.54 GiB in the explicit encoding. The [parameter ledger](parameters/README.md) gives the complete accounting and the exact statistical expression.

These figures describe the reconstructed encoding. The Rust backend follows a different, conservative decomposition profile and reports its actual serialized sizes. It does not implement this optimized ledger. A proved Fiat–Shamir compiler and concrete computational-security bounds at the extraction runtimes remain open. The CPU batch above covers the earlier Python native source and exact predicates.

## Build and reproduce

Use Python 3.10 or later. The package uses the standard library at runtime. Run the following commands from the repository root:

```sh
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/certify.py
python research/scripts/verify_archive.py
```

Run the native source example and a small challenge benchmark:

```sh
python examples/native_frontend_smoke.py --log-size 6 --rows 16 --seed 1
python benchmarks/challenge_membership.py --degree 8 --energy 12 --threshold 10 --samples 8
```

Additional certificate examples cover the security-parameter family, filtered moments, bounded energy and computational loss:

```sh
python examples/statistical_family.py
python examples/filtered_folding.py
python examples/bounded_energy.py
python examples/refined_loss.py
```

The [experiment runner](experiments/README.md) records configurations, logs, exit status and hashes. Sage cost-model reproduction accepts the estimator checkout through `--estimator`; its pinned revision and commands are in the [research guide](research/README.md#pinned-sage-cost-reproduction).

## Repository guide

```text
assets/         Homepage artwork
crates/         Rust arithmetic, circuit frontend, recursive backend and CLI
src/            Python arithmetic and reference implementation
examples/       Executable certificates and native source example
tests/          Exact arithmetic and interface regression tests
docs/           Mathematical guides and claim ledger
parameters/     Parameter overview and links to preserved ledgers
benchmarks/     Predicate benchmark and recorded CPU results
experiments/    Run recorder, configurations and external adapters
impact/         Paper census and implementation dependency evidence
research/       Detailed proofs, reviews, scripts and hashed records
```

| Component | Entry point |
| --- | --- |
| Callable frontend, backend and CLI | [leash](crates/leash) · [Usage guide](docs/rust-library.md) |
| Rust binary circuit and native source | [leash-frontend](crates/leash-frontend) |
| Rust ring arithmetic and relations | [leash-core](crates/leash-core) |
| Modular projection certificates | [bounds.py](src/labrador_repair/bounds.py) |
| Challenge families and exact membership | [challenges.py](src/labrador_repair/challenges.py) · [fourier.py](src/labrador_repair/fourier.py) |
| Energy counting and folding moments | [energy.py](src/labrador_repair/energy.py) · [folding.py](src/labrador_repair/folding.py) |
| Source relations and full-witness codec | [r1cs.py](src/labrador_repair/r1cs.py) · [native_reference.py](src/labrador_repair/native_reference.py) |
| Extraction-loss certificates | [extraction_bounds.py](src/labrador_repair/extraction_bounds.py) |

The [14 November 2026 handoff](CLOSEOUT.md) records the earlier research closeout. The tag `research-closeout-2026-11-14` preserves that snapshot. The paper census, repository presentation and Rust implementation are subsequent additions authorized by the author.

## Papers and implementation dependencies

The version-pinned census identifies **12 downstream papers** with a numerical or substantial composition dependency. It records the affected claim in each paper, including the authors' heuristic qualifications and the scope of optional configurations.

| Dependency | Papers |
| --- | --- |
| Exact lower-tail statement | [RoKoko](https://eprint.iacr.org/2026/575), [Orthus](https://eprint.iacr.org/2026/398) |
| Numerical premise or derived slack | [Grand Danois](https://eprint.iacr.org/2026/1196), [Aggregating Falcon Signatures](https://eprint.iacr.org/2024/311), [Symphony](https://eprint.iacr.org/2025/1905), [Toolkit](https://eprint.iacr.org/2026/1289), [Lemur+](https://eprint.iacr.org/2026/2054) |
| Concrete backend or composition | [Greyhound](https://eprint.iacr.org/2024/1293), [Hachi](https://eprint.iacr.org/2026/156), [LaZer](https://eprint.iacr.org/2024/1846), [Unmasking TRaccoon](https://eprint.iacr.org/2025/849), [LaBinius](https://eprint.iacr.org/2026/2103) |

Three further papers offer an optional LaBRADOR compressor: [RoK, Paper, SISsors](https://eprint.iacr.org/2024/1972), [LatticeFold](https://eprint.iacr.org/2024/257) and [Serval](https://eprint.iacr.org/2025/1903). [TTRP shortness checks](https://eprint.iacr.org/2026/2146) use the older JL parameters as a comparison baseline. [Page-level evidence, version hashes and exclusions](impact/README.md).

The implementation map follows published artifacts, vendored sources and declared dependencies. Each repository has a recorded revision and evidence link in the [repository register](impact/REPOSITORIES.md).

| Repository | Connection |
| --- | --- |
| [lattice-dogs/labrador](https://github.com/lattice-dogs/labrador) | Upstream LaBRADOR and Greyhound implementation |
| [lazer-crypto/labrador](https://github.com/lazer-crypto/labrador) | LaBRADOR backend used by LaZer |
| [lazer-crypto/lazer](https://github.com/lazer-crypto/lazer) | Declared LaBRADOR submodule and succinct-proof branch |
| [dfaranha/aggregate-falcon](https://github.com/dfaranha/aggregate-falcon) | Artifact accompanying the Falcon aggregation paper |
| [georgeorourke/hachi-pcs](https://github.com/georgeorourke/hachi-pcs) | Hachi prototype; the paper's Greyhound tail is an estimated composition |
| [osdnk/labinius](https://github.com/osdnk/labinius) | Vendored LaBRADOR backend for recursive opening |
| [lattice-arguments/rokoko](https://github.com/lattice-arguments/rokoko) | Artifact accompanying RoKoko |
| [dingdangdangwhx/Lemur-plus](https://github.com/dingdangdangwhx/Lemur-plus) | Vendored C backend used by the signature aggregation driver |

Code and original research notes are available under the [MIT license](LICENSE). Cited papers and external repositories retain their own authorship and licenses.
