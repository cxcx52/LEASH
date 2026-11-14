# Engineering experiments and acceptance contract

The first executable repaired component is a **portable CPU reference for the
bare native binary source reduction**. It computes a small source commitment,
constructs and checks the complete target witness, sends that witness in full,
and roundtrips a reference wire encoding. It does not execute the recursive
ordinary core. The 161040-byte mathematical compact-prover ledger is not a
measurement of this reference program.

The experiment structure separates three stages. Implementation and execution
status are separate: a runnable component has not necessarily been executed on
a particular host. A successful honest test is a correctness observation, not
an empirical soundness or security-level estimate.

## 1. Stages and current state

| Stage | Available component | Required acceptance evidence | Current limitation |
| --- | --- | --- | --- |
| Upstream honest in-memory baseline | Pinned C source audit/preparation adapter and log checks | Supported CPU, recorded checkout/patch/build identity, actual successful prove/reduce/verify stages and return code | Optional; upstream code is not the repaired profile, has hardware requirements, and supplies no complete serialized-proof measurement |
| Repaired native source reference | `native_reference.py` and `native_frontend_smoke.py` | All bare target checks, separate decoded-source oracle checks, exact reference wire roundtrip, dimensions and norm conditions | Sends the entire witness; no recursive-core invocation, fingerprint-source implementation, or security instantiation |
| Full repaired core and compact serialization | Mathematical proofs, exact parameter certificates, and planning manifest | Implement and run every ordinary layer, check every target/norm edge, serialize/decode and reverify the complete transcript | Not implemented; no end-to-end compact source-to-core benchmark exists |

The upstream [adapter](../experiments/adapters/upstream_labrador/README.md) pins
commit `8b6626b26afd4c0162ddd089759d21d3d51bfbdf`. Its Chihuahua, Dachshund, and
Greyhound tests retain their original relation types. In particular, the
Dachshund test uses a linear relation, not the native binary frontend. It keeps
the original challenge/norm choices and OS randomness. It cannot be labeled a
repaired-core implementation by changing a plot legend. Its AVX512-family
prerequisites must be checked before execution; the portable reference does not
depend on those instructions. GPU optimization is deferred.

## 2. Portable native reference

Run directly from a source checkout with standard Python:

```sh
python examples/native_frontend_smoke.py --log-size 6 --seed 1 --rows 160
python examples/native_frontend_smoke.py --log-size 8 --seed 2 --rows 160
python examples/native_frontend_smoke.py --log-size 10 --seed 3 --rows 160
python -m unittest discover -s tests -p test_native_reference.py -v
```

The example locates the checkout's `src` directory, so it does not require a
package installation. It restricts `log-size` to 6 through 10 and rows to 16 or
160. The default modulus is `q=4294967197`, ring degree 64, and toy source rank
2. These are CPU correctness/local-work experiments, not a claim of hardness
at rank 2. The sparse generator sets `n=k=2^log_size`, counts the constant wire
in `n`, and creates an honest assignment. Each A/B row has three selected
columns; C uses the constant column to match that assignment. This is a
controlled synthetic workload, not a representative R1CS benchmark suite.

Python `random.Random` streams make the fixture deterministic. They are labeled
benchmark-only randomness. The matrix, instance, and challenges are reproducible
for the specified seed and implementation. Repeating the same seed measures
process/runtime variation; it does not create independent protocol randomness.
Different seed configurations vary the fixture. Neither usage estimates a
cryptographic error probability.

The executed chronology is:

1. Generate the public sparse binary instance and honest assignment.
2. Generate the small public source matrix and compute the source commitment.
3. Generate the specified number of binary challenge rows after the commitment.
4. Combine each `delta` in `F_2` before lifting, and compute the integer replies.
5. Construct eight aligned blocks: `a,b,c,w` and their conjugates, with explicit
   zero padding. The honest squared bound is `2(n+3k)` and the actual extracted
   squared cap is `(16/3)*2(n+3k)`. The source lifting inequalities are checked.
6. Check source commitment, conjugation coordinates, all four `Jbar` bitness
   equations, the product equation, coefficient-level constant/public pins,
   exact padding zeros, full norm, expected challenge/reply count, integer
   interval/parity, and scalar equations modulo `q`.
7. Separately check decoded bits, integer-lift equality, and the decoded source
   R1CS as correctness oracles for the reference.
8. Encode the prover messages, decode against the fixed public context, and
   recheck the decoded result.

The report exposes `target_check_status` and `source_oracle_check_status`
separately. The direct decoded-source check is stronger than the reduction's
bare target verifier and is used as a diagnostic oracle. Its cost is included
in `verification_with_source_oracle`, which must not be presented as a succinct
verifier timing. A fixed public `Parameters.aggregation_rows` rejects jointly
truncated challenge/reply lists.

`NATIVE_FRONTEND_REFERENCE_PASS` is emitted only after all checks and the
roundtrip succeed. Unit tests also reject locally constructed malformed
mathematical fixtures and wire encodings. They are checker tests, not a
third-party protocol experiment.

## 3. What the byte and time fields mean

The reference prover wire is a deliberately simple, version-local encoding:
source commitment first, signed source scalar replies second, complete target
witness last. Residue coefficients use canonical unsigned little-endian 32-bit
words, and replies use signed little-endian 32-bit words. Dimensions, source
matrix, and saved verifier challenges come from the fixed public context. The
decoder rejects a length mismatch and noncanonical residues. It then passes the
decoded message to the complete reference checker; decoding alone is not
verification. This is an in-memory codec, not a network protocol or stable
production wire format.

| Field | Evidence and scope |
| --- | --- |
| `full_witness_transport_bytes` | Length of actual bytes constructed for all eight padded witness blocks |
| `source_commitment_transport_bytes` | Actual source commitment encoding length |
| `source_scalar_transport_bytes` | Actual signed 32-bit reply encoding length |
| `bare_source_prover_transport_bytes` | Sum of the above actual fields; excludes verifier challenges, setup, statement and framing |
| `diagnostic_JSON_bytes` | Actual UTF-8 diagnostic transcript JSON length, including challenge arrays; not a proof size |
| `compact_proof_bytes` | Null: no recursive core/compact codec is executed |
| `phase_seconds` | Local wall timings for setup, commitment, challenge generation, replies, target construction, checking, encoding and decoded rechecking |
| `local_total_wall_seconds` | Complete local reference operation through its transport checks; Python startup is outside it |
| Harness `wall_seconds` | Complete child process wall time, including startup and reporting |
| `process_peak_rss_kib` | Linux `getrusage(RUSAGE_SELF)` peak for the entire Python process, including setup/checking/encoding; null on other platforms |

Do not add overlapping complete-process and local timings. Report count,
median, range, and dispersion only over runs that satisfy their acceptance
contract; retain failed/time-out runs separately. Parent-process RSS, Python
object estimates, and a whole-process peak are not phase-specific working-set
measurements. No energy, GPU memory, or wattage measurement is currently made.

The generic recorder's stdout/stderr byte counts are **log bytes**. Upstream
`KB` values are formula-based estimates on a KiB scale, as explained in the
adapter. The archived 157.265625 KiB compact encoding bound and roughly 67.54 GiB
verifier traffic bound are mathematical ledgers. These four categories must
remain separate from the actual full-witness reference transport measurements.

## 4. Manifest and provenance contract

Executable configurations in `experiments/configs/native-n<size>-seed<seed>.json`
follow the [generic recorder](../experiments/harness/README.md) schema:

```text
argv, cwd, timeout, repetitions, label, source_revision, evidence_scope,
expectations, metadata
```

Commands are argument arrays, with no shell interpolation. `cwd` is relative to
the configuration file. `python` must resolve to the intended interpreter, for
example by activating its virtual environment; otherwise set `argv[0]` to that
interpreter's absolute path in a local configuration. The checked-in
`source_revision` is explicitly a working-tree declaration. Before remote or
published runs, record the actual commit, dirty state, archive/file hashes,
interpreter, OS/kernel, CPU flags, process/thread settings, and build identity
where applicable. A caller-supplied revision string is not an authenticated
source identity.

The optional `environment_inventory` field can reference an existing probe
record. The recorder preserves its path/hash. It records command completion,
exit status, stdout/stderr paths and hashes, wall time, and available external
memory measurements. No experiment is accepted solely because its process
returned zero: the configurations require the reference's explicit success,
target/oracle status, and roundtrip markers. This is evidence from controlled
local code and logs, not authentication of arbitrary external logs.

Each protocol manifest must include:

* Full `q,d`, source dimensions including the constant wire, public pins/H rows,
  all per-layer `r,n`, commitment ranks and column counts.
* Honest norm, actual extracted source norm, actual target-opening cap, base and
  decomposition counts at each edge. Exact squares/rationals avoid rounded
  inequality checks.
* Scalar/ring aggregation laws, field polynomial/basis, row counts, residual
  lengths, challenge chronology and updated statistical errors.
* Final challenge support, sampling law, cardinality certificate, energy and
  operator cap; projection law, row count, acceptance threshold and slack.
* Restart policy, exact statistical budget and its certificate; separately,
  source/core MSIS roles, norms, complete sampler runtimes and outstanding
  computational advantage obligations.
* Timing boundaries, transport conventions, measured versus estimated fields,
  implementation state, and explicit Fiat--Shamir scope.

`repaired-full.manifest.template.json` records the archived seven-layer candidate
in this form. It has `executable:false` and no command: it is **not a recorder
configuration**. Passing it to the runner must fail schema validation. Its
status is a mathematical candidate, and no security label is assigned.

## 5. Smoke, scale and controlled comparisons

The first reference batch is bounded at `n=k` in `{64,256,1024}`, seeds
`{1,2,3}`, and three new-process repetitions per seed: 27 processes. All use
160 source rows. Smaller 16-row CLI runs are useful for development smoke.
Each configuration has a 120-second timeout; the CLI independently caps size.
Remote authentication/capability probes are prerequisites, not successful
benchmark records. No GPU optimization or large dense projection allocation is
part of this batch.

For example, from the repository root:

```sh
python -m experiments.harness experiments/configs/native-n64-seed1.json --output-dir work/native-n64-seed1 --dry-run
python -m experiments.harness experiments/configs/native-n64-seed1.json --output-dir work/native-n64-seed1
```

The comparison planning file is
`comparison.manifest.template.json`. Its parameter A uses 16 source rows and B
uses 160. Their fixed-opening source error bounds differ. Neither is a concrete
security instantiation, so the experiment may report local work/byte differences
but must not call them equal-security speedups. Matching `q,d` alone is
insufficient for equal security, and the sparse toy workload is not the archived
`2^25` source profile.

| Experiment | Current acceptance scope | Required controls |
| --- | --- | --- |
| Smoke | Positive target/oracle/roundtrip checks on small instances | Dimensions, fixed row count, source matrix role and interpreter recorded |
| Scale 64/256/1024 | Local phase/whole-process timing, memory and actual bare transport | Same generator, density, ranks, degree and row law; seed and repetitions recorded |
| Rows 16 versus 160 | Local aggregation work and reply bytes | Same instance seed and all other parameters; different theorem errors displayed |
| Source independent rows versus fingerprint | Planned | Implement the field-point frontend while retaining integer parity, source binding and updated error |
| Core independent versus power aggregation | Planned | Implement core, retain all six replies, update laws/errors/complete sampler runtimes |
| Cube versus bounded-energy folding | Planned | Reaccount cardinality, folding cap, packed path, collision norms and assumptions; do not infer equal security |

An end-to-end claim for the full repaired system requires actual source output to
feed the implemented ordinary core, every recursive relation/norm edge to match,
complete final verification, and decode/reverify of the serialized compact
transcript. It must retain all public pins, both core outer commitments, early
checks, and the specified restart policy. Source-reference success and a
standalone folding-kernel benchmark do not jointly establish that milestone.

The present conclusion supported by the reference is narrower and useful:
the specified native arithmetic, chronology, packing, full target checks and
full-witness reference codec can be exercised on small honest fixtures, with
reproducible local timings and actual byte counts. Full compact-system
performance and concrete computational security remain separate work.
