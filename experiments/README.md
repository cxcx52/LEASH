# Recorded implementation experiments

This workspace measures implementation behavior separately from the mathematical
certificates in `research/`. The original research archive remains unchanged.
An experiment passing does not establish a cryptographic security level.

## Code boundaries

| Location | Responsibility | Current scope |
|---|---|---|
| `crates/` | Rust binary frontend, recursive prover/verifier and canonical codec | Callable library, generic relation API and CLI |
| `experiments/run_rust_benchmarks.py` | Clean-revision Rust measurement recorder | Nine full proof/encoding/verification runs; source, lockfile and log hashes |
| `src/labrador_repair/` | Exact arithmetic and reference semantics | Includes a small native binary frontend with a full-witness transport |
| `examples/native_frontend_smoke.py` | Honest source/target/encoding round trip | Bare source reduction, not the recursive succinct core |
| `benchmarks/` | Explicitly scoped kernel measurements | Energy-ball fixtures; exact Fourier versus SPD membership predicates |
| `experiments/harness/` | Local subprocess recording and bounded execution | Config, UTC times, exit status, logs, hashes, optional resource data |
| `experiments/environment_probe.py` | Read-only environment inventory | CPU features, container limits, toolchains, visible CUDA/GPU capabilities |
| `experiments/adapters/` | Optional pinned external implementation adapters | Upstream C preparation; never silently substitutes a different relation |
| `experiments/configs/` | Small reproducible experiment contracts | Each template states its implementation and security scope |

The engineering plan and acceptance matrix are in
[engineering-experiments.md](../docs/engineering-experiments.md).
The recorder interface is documented in [harness/README.md](harness/README.md).

## Run and evidence discipline

For the Rust implementation, commit the source and run:

```sh
python experiments/run_rust_benchmarks.py --out work/rust-results --rounds 1
```

The directory must be new. This recorder uses the OS randomness in the library,
records complete-session retries and validates all nine returned proofs. Its
[first result report](../benchmarks/results/2026-11-14-rust-v0.1/README.md)
includes the precise profile and measurement scope. The remaining instructions
describe the earlier Python and remote experiment harness.

Use a fresh experiment branch and an immutable Git revision for measured runs.
Deploy only the tracked release archive, retain its SHA-256, and hash the deployed
source files against the archive. The recorder labels a supplied revision as a
caller assertion; the deployment manifest supplies the separate provenance check.
Do not copy SSH configurations, credentials, unrelated home-directory files, or
untracked research scratch data into a release.

Every run records its exact argument list, working directory, parameter metadata,
source revision, environment inventory hash, start/end UTC, exit/timeout status,
stdout/stderr bytes and hashes. Inputs use deterministic public benchmark seeds.
This does not make the reference RNG a cryptographic randomness source. Store
raw results outside the source release, never overwrite a previous run, and
export a summary together with the corresponding raw logs.

Record the container's CPU and memory quotas as well as host-visible totals.
The presence of a CUDA toolkit or a host driver report does not establish access
to a GPU device. An unavailable CPU instruction set or GPU is an unsupported
capability, not a successful benchmark and not an authentication failure.

## First experiment families

1. Replay the package's exact tests and archive checker on the remote interpreter.
2. Run native reference fixtures at n=k=64, 256 and 1024, with 160 challenge rows,
   several declared seeds and repeated processes. Record setup, commitment,
   response, checking and encoding times separately. The source rank is a toy
   benchmark choice; it is not the rank-6 large security profile.
3. Compare the exact membership methods on the same degree-64, energy-at-most-104
   candidates with threshold 30. Report cold initialization separately from warm
   predicate time. If the Fourier path falls back to the shared SPD routine,
   agreement on those cases is not an independent implementation check.

The native checking time includes a diagnostic source-relation oracle. Report it
under that name; it is stronger work than the target checks alone. The serialized
reference sends the full witness and has its own round-trip decoder. Its measured
bytes are not the estimated 157.27 KiB compact protocol payload. Setup, statement,
verifier challenges and framing have separate accounting.

The kernel's sampled acceptance count describes only its stored fixtures; it
does not replace the exact probability/count certificates. Its RSS is the peak
of the whole process containing both algorithms, not separate algorithm peaks.
None of these first runs implements the complete compact recursive prover,
Fiat--Shamir, GPU acceleration or a numerical computational-security proof.

## Reproducibility and repository state

Install the package into an isolated environment with `python -m pip install -e .`
when using examples that import it. The scripts use the standard library.
The runner accepts `--dry-run` before any workload is started. Generated results
and local deployment work are ignored by Git. Reviewed compact result summaries
may be committed later with explicit source/run identities; raw benchmark output
must not be confused with new universally quantified proof evidence.
