# Optional upstream honest-test preparation

This standard-library Python adapter prepares the Apache-2.0 upstream
`lattice-dogs/labrador` commit
`8b6626b26afd4c0162ddd089759d21d3d51bfbdf`. It does not download, install,
compile, or execute upstream code. A clean local checkout is required.
Only tracked Git blobs are copied to a **new directory outside both
checkouts**; the upstream license is retained. No upstream source is vendored
in this repository. `source-audit.json` records reviewed source identities.

The three normal witness tests are retained:

| Test | Smoke input at `--log-size 10` | Verification |
|---|---|---|
| Chihuahua | One ternary vector of 1024 ring elements | Two-layer prove/reduce checks and composite verification |
| Dachshund | Two ternary vectors of 1024 ring elements each | `prepare_linear`, two-layer checks and composite verification |
| Greyhound | 1024 ring elements, 65536 polynomial coefficients | Commitment/evaluation reduction and composite verification |

**Dachshund's test is a linear relation, not native binary R1CS**, and none
of these smoke cases represents the paper's `2^25` binary workload. The
original Greyhound test sets `len=1<<19`; with `N=64` this means `2^25`
coefficients, despite the README's `2^26` wording. This adapter records the
actual input dimensions. It retains the original `q=2^32-99`, `N=64`,
`T=14`, `SLACK=2`, parameter search, and OS randomness. It is an upstream
baseline, not an implementation of the repaired mathematical profiles.

Patches affect only the three test drivers: input sizes, explicit checks for
previously ignored integer return values, zero initialization of Greyhound
test cleanup objects, and stage/success markers. Library code and all existing
verification calls remain unchanged. On a newly detected failure the test
returns immediately; process teardown may release objects rather than running
the normal success cleanup. Failed processes are never timing successes.
All nonzero results map to `EXIT_FAILURE`, avoiding exit-code truncation into
an apparent zero. The default small sizes are preparation candidates; no
supported-hardware execution is claimed here.

## Hardware and build prerequisites

The upstream README requires AVX512. Source intrinsics further use VBMI byte
permutation, VBMI2 word compression, VNNI dot products, VAES and AES. The
adapter's conservative Linux x86-64 gate requires the common flags on every
visible CPU:

    avx2 aes avx512f avx512bw avx512dq avx512vl
    avx512vbmi avx512_vbmi2 avx512_vnni vaes

An AVX2-only AMD EPYC 7742 is unsupported. The gate prints
`status=unsupported_capability`, `execution_status=blocked-hardware` and exits
77. Do not build/run on that node or emulate the missing instructions as a
performance result. OS vector-state support, compiler compatibility and
actual execution remain separate checks even when flags are present.

The original Makefile uses GNU make, a C compiler accepting `-std=c2x`, GNU
extensions, x86 intrinsics/assembly, LTO, and libm. It retains
`-O3 -fwrapv -march=native -mtune=native -flto=auto` and its warning flags.
These three targets do not require the separate AES-test OpenSSL or polz-test
GMP link options. Build on the intended execution host. No compiler-version
minimum, portable binary, wattage or energy measurement has been established.

## Prepare and inspect

Use fresh absolute directories; run `plan` to write commands, a unified patch,
and pinned/checkout SHA256 records **without creating a source copy**:

```sh
python experiments/adapters/upstream_labrador/adapter.py plan \
  --source /path/to/clean/labrador \
  --work-dir /scratch/labrador-smoke-source \
  --artifacts /scratch/labrador-smoke-plan
```

Use `prepare` with a new artifact directory to materialize the external work
copy. Both modes execute only read-only Git subprocesses. No shell command is
evaluated from repository text. On a suitable future host, the operator may
explicitly run the generated argument arrays or these equivalent commands:

```sh
python /path/to/repair/experiments/adapters/upstream_labrador/adapter.py capabilities
# Continue only if that command exits 0, and record its JSON output.
cd /scratch/labrador-smoke-source
make -j1 test_chihuahua test_dachshund test_greyhound
./test_chihuahua
./test_dachshund
./test_greyhound
```

Capture each process's stdout, stderr, and actual return code separately.
`check-result --target dachshund --returncode 0 --stdout OUT --stderr ERR`
parses those records; the supplied return code must come from the process.
Success requires exit 0, both ordered verification-stage markers, the final
success marker, and no reported error. Missing output, signals and failed
verification are failures. This is log validation, not authentication of an
untrusted log or proof verification by the Python adapter.

The upstream `print_proof_pp`/`print_witness_pp` functions compute size formulas
and divide by 8192 before printing `KB`. Parsed values are therefore labeled
**estimated KiB**. `pack.h` exposes in-memory proof containers; these tests
do not produce a serialized complete proof. `actual_serialized_proof_bytes`
and `energy_joules` remain null. Upstream `clock()` labels are process CPU
seconds, while complete process wall time/RSS require external measurement.
Do not add overlapping timings or present these estimates as serialized bytes.

Seven small fixture tests cover pin/clean rejection, patch anchors, isolation,
CPU gating and result handling. They do not compile or execute upstream C.
