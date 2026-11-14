# First recorded CPU reference batch — 14 November 2026

All **38 recorded processes** completed successfully: 27 native-source runs,
9 challenge-membership runs, the 66-test package suite, and the 102-file
research archive check. The measurements below refer to source commit
`fac2517e163517540f09cbf866d4a7cae8e3d40e`.

The [machine-readable summary](summary.json) records descriptive statistics and
per-record hashes. [Raw records](raw-records.tar.gz) include every configuration,
stdout/stderr log, process record, batch record, deployment manifest and the
read-only environment inventory. Source files were checked against the release
manifest before and after execution (184 files); imported logs were rehashed
before aggregation. These checks establish artifact consistency, not external
attestation of the host or a security proof.

## Host and method

Ubuntu 24.04.4, Python 3.12.3, AMD EPYC 7742. The container exposes a CPU quota
equivalent to 40 cores and a 200 GiB memory limit. No NVIDIA device node is
visible. AVX2 is available; AVX512 is absent. CUDA 12.8's compiler exists, but no
GPU experiment was run. The optional upstream C adapter was not executed.

Workloads ran sequentially in fresh Python processes, using one Python thread
and no CPU affinity pinning. Every native configuration used seeds 1, 2 and 3,
with three repetitions each. Repetitions share the same fixture. Times are
single-host descriptive observations, without confidence intervals or a
controlled comparison to upstream C. GNU time was absent; workload RSS comes
from Linux `resource.getrusage(RUSAGE_SELF)` and includes the whole Python
process. The harness correctly leaves its separate GNU-time RSS field null.

## Native binary source reference

The implementation constructs a source commitment, samples binary challenge
rows, constructs integer scalar replies and the padded conjugate witness,
checks the bare target, directly checks the decoded source as a separate
oracle, and encodes/decodes the complete witness. All 11 target checks, all
3 oracle checks, and all 27 byte-roundtrip checks passed.

Parameters are `q=4294967197`, `d=64`, source rank 2, 160 binary rows generated
by the deterministic benchmark PRNG, and squared norm slack `16/3`. The sparse synthetic generator fits C to
the honest assignment. This is a bounded correctness fixture, not a realistic
application circuit or the large rank-6 parameter profile.

| n = k (including constant wire) | Runs | Actual prover transport (bytes) | Source commitment median (ms) | Target + source-oracle check median (ms) | In-process whole-flow median (ms) | Whole-process peak RSS median (MiB) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 9 | 5,248 | 5.91 | 22.39 | 78.13 | 19.69 |
| 256 | 9 | 9,344 | 23.91 | 76.32 | 273.25 | 20.65 |
| 1,024 | 9 | 33,920 | 95.07 | 298.69 | 1,079.03 | 25.85 |

Transport consists of the full witness (4,096 / 8,192 / 32,768 bytes), a
512-byte source commitment and 640-byte scalar replies. These are byte strings
actually produced by the encoder, excluding the public statement, matrix,
verifier challenges and framing. They are **not compact proof sizes**.

The whole-flow time includes instance/matrix/challenge generation, commitment,
replies, witness construction, checking, encoding, decoding and a second check.
The encoding phase also builds diagnostic JSON. It excludes Python process
startup; harness wall-time medians, including startup and observation overhead,
are 183.65 / 445.58 / 1,182.10 ms. Full minima and maxima are in the summary;
the largest whole-flow timing range was 270.46–641.83 ms for n=256. We do not
infer an asymptotic scaling law from these three sizes.

## Exact challenge-membership kernel

We used coefficient alphabet {-2,-1,0,1,2}, degree 64, energy cap 104 and strict
operator-norm threshold 30. Each of three seeds selects 32 raw energy-ball
candidates by exact counting and unranking. Python's deterministic RNG is used
only for public fixtures. Each fixture was repeated three times. Methods see
the same input, with their invocation order alternating across candidates.

The three fixtures accepted 32/32, 31/32 and 32/32 candidates. All 96 candidate
positions agreed between certified Fourier intervals and the exact SPD test;
all repeated runs agreed as well. Every decision used an interval accept/reject
path, with **zero SPD fallbacks in this batch**. Thus these observations do
exercise two distinct decision paths. For other inputs the Fourier method can
fall back to the same SPD routine, so agreement there is not an independent
check. The 95/96 count is descriptive and does not replace a cardinality proof
or a population rejection-probability bound.

| Measurement | Median | Minimum–maximum |
| --- | ---: | ---: |
| Warm certified Fourier, 32 candidates | 20.89 ms | 19.00–23.01 ms |
| Warm exact SPD, same 32 candidates | 3,671.03 ms | 3,504.41–3,936.36 ms |
| Within-process SPD/Fourier elapsed-time ratio | 180.58× | 165.38–187.49× |
| Cold Fourier table initialization + zero query | 350.07 ms | 343.55–501.64 ms |

The ratio is the median of nine paired process-level ratios, not the ratio of
the two displayed medians. Cold initialization excludes Python startup/imports
and is reported separately. Kernel RSS is for the process running both methods;
it cannot compare their individual memory costs.

## Supported conclusion and remaining work

The repaired native-source definitions now have an executable honest-flow
reference with an actual byte roundtrip. The certified challenge filter also
has measured exact-decision agreement and a substantial warm-kernel advantage
over the package's generic SPD implementation on these fixtures. This supports
using the Fourier path as an implementation component.

The recursive ordinary core, the fingerprint source variant, a compact full
transcript serializer and Fiat–Shamir are not implemented here. There is no
measured compact end-to-end prover/verifier time, no GPU speedup, no complete
computational-security certification, and no direct performance comparison
with the original paper. The earlier **161,040-byte ledger remains a modelled
prover-message encoding bound**. Neither that bound nor the original paper's
size claim is validated by these small full-witness runs.

## Reproduce the evidence aggregation

From the repository root (the result-report commit contains the summarizer):

```sh
mkdir -p work/replay-first-cpu
tar -xzf docs/experiment-results/2026-11-14-first-cpu/raw-records.tar.gz -C work/replay-first-cpu
git archive --format=tar fac2517e163517540f09cbf866d4a7cae8e3d40e > work/first-cpu-source.tar
python experiments/summarize_first_batch.py --import-root work/replay-first-cpu --source-archive work/first-cpu-source.tar --output work/replayed-first-cpu-summary.json
```

Raw-record bundle SHA-256:
`4c2c9304556a54b3a403b8007f3884dde3d38f468c65e6ad5d1a8f13924676d6`.
Source archive SHA-256:
`a5e39310210caec8ade4b86829c1a3440f99731e4a74b858e2a3da1e37ed8024`.

To repeat execution, export that source commit, create a new environment
inventory and deployment manifest, then invoke `experiments/run_first_batch.py`
with a fresh output directory. Fresh measurements will have different run IDs,
timestamps and timing values; the deterministic fixture hashes should match
under the recorded Python/source combination.
