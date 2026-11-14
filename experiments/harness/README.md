# Local experiment recorder

This standard-library runner records explicitly configured local commands. It
does not implement a protocol, verifier, lattice solver, network client, or SSH
deployment. A successful process or matching output marker is an observation;
the caller remains responsible for independent correctness checks and for
describing the experiment's evidence scope.

Run from the repository root, with Python 3.10 or newer:

```sh
python3 -m experiments.harness experiments/harness/examples/smoke.json --output-dir experiments/results/smoke --dry-run
python3 -m experiments.harness experiments/harness/examples/smoke.json --output-dir experiments/results/smoke
```

The example's executable is `python3`; change its first `argv` item to the actual
interpreter on systems using another name. No shell, shell quoting, variable
expansion, wildcard expansion, or implicit working-directory changes are used.
`cwd` and optional `environment_inventory` resolve relative to the config file;
`--output-dir` resolves relative to the invoking process. Dry run validates the
configuration and resolves paths, but starts no process, probes no resource
tool, and writes no file or directory.

## Configuration

The machine-readable description is [config.schema.json](config.schema.json).
Required fields are `argv`, `cwd`, `timeout`, `repetitions`, `label`,
`source_revision`, and `evidence_scope`. Runtime validation additionally rejects
NULs, nonfinite timeouts, nonexistent directories, and empty executables.
Optional `metadata` holds JSON descriptions such as protocol manifests or
measurement contracts; it has no execution semantics.

`environment_inventory` may name an existing public experiment-inventory file.
Each record includes that file's path, byte length, and SHA-256 at run start.
The runner does not collect environment variables, credentials, or machine
inventory itself. Child processes inherit the calling environment normally;
there is no environment override in this schema. Configuration arguments,
metadata, and command output are recorded verbatim, so experiment configs and
commands should contain public experiment inputs, not credentials.

`expectations` supports `exit_codes` and literal UTF-8 substring lists:
`stdout_contains`, `stderr_contains`, `stdout_not_contains`, and
`stderr_not_contains`. The command's own success marker must represent a check
the caller understands; a printed marker alone is not independent verification.
All configured checks must hold and execution must finish without a timeout
for expectation status `passed`. With no checks, status is `not_configured`,
even if the command exits zero. The recorder never emits a security verdict or
a generic `verified=true` field.

## Records and units

Every repetition allocates a new directory using an atomic exclusive mkdir and
a random UUID. Existing run directories and records are never reused or
overwritten. Each contains:

- `config.json`: normalized caller configuration;
- `stdout.log` and `stderr.log`: exact binary output;
- `record.json`: UTC timestamps, end-to-end `wall_seconds`, execution status,
  exit code, timeout flag, cleanup details, literal-check results, and each
  output log's byte count and SHA-256;
- `gnu-time.log` when GNU time instrumentation was available.

Execution status is `completed`, `timed_out`, `launch_error`, or `interrupted`.
`completed` describes process completion and includes nonzero exits. A launcher
such as GNU time that starts successfully but cannot execute its child produces
its normal nonzero exit; this is still `completed`, with diagnostic stderr.
The caller-provided revision is labelled `source_revision_verified=false`.

Wall time includes process launch, waiting, instrumentation overhead, and any
cleanup. It is not an algorithm-only latency. Linux exit observation polls at
up to 10 ms intervals. For short kernels, the command should report its own
well-defined repeated-operation timings in addition to this invocation total.

On Linux, a detected GNU time executable supplies `max_rss_kib`, with
`max_rss_bytes = 1024 * max_rss_kib`. GNU time's RSS statistic is not an aggregate
simultaneous memory peak across a parallel process tree. Unsupported platforms,
missing GNU time, or interrupted instrumentation produce `null` values and an
explicit reason. Resource logs also receive byte counts and SHA-256 hashes.

## Timeout and process ownership

Each POSIX run starts a new session and process group. On Linux, timeout sends
SIGTERM and then SIGKILL after a 0.2-second grace period to that run's group only.
The leader is kept unreaped until cleanup finishes, so its PID cannot be reused
for an unrelated group during cleanup. Live members left in the owned group
after normal leader exit are also cleaned up and recorded, keeping recorded
logs stable. No name-based or machine-wide process killing is performed.

Commands must keep their descendants in the inherited process group; deliberate
session detachment is outside this runner's cleanup guarantee. On non-POSIX
platforms timeout terminates the direct process only, and the record identifies
that limitation. The Linux test includes a live grandchild and an unrelated
process to check both group cleanup and isolation.

The CLI returns zero for an operationally completed run set whose commands exit
zero and whose configured checks do not fail; this is not a verification or
security signal. It returns one for other recorded failures, 130 for interruption,
and argparse's nonzero exit for invalid input. A configured expected nonzero
exit can pass its observation check while the CLI still reports a nonzero
operational outcome. All per-run records remain authoritative.

Run the focused checks with:

```sh
python3 -m unittest discover -s tests -p test_experiment_harness.py -v
```
