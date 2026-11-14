# Calling the LEASH Rust library

LEASH now includes an executable binary-circuit frontend and an ordinary
recursive lattice-argument backend. A caller can build a circuit, supply its
assignment, generate a proof, send its bytes and verify them in another process.
The generic backend also accepts quadratic ring relations directly.

The implementation is a research library. It uses a public seed to expand the
commitment matrices and SHAKE256 to compile the interactive messages. The
archived theorems analyze interactive protocols; they do not establish the
security of this Fiat–Shamir compiler. The library has no zero-knowledge or
certified security-level claim. These properties are also explicit in its
verification reports.

## Build and run

From the repository root, with Rust 1.85 or later:

```sh
cargo test --workspace --all-targets --release --locked
cargo run --release -p leash --example library
cargo run --release -p leash -- demo --out demo-output
```

The demo writes public parameters, a small AND/XOR/NOT circuit, its synthetic
assignment, a binary proof and a timing report. The output directory must not
already contain those files. The verification command needs no assignment:

```sh
cargo run --release -p leash -- verify \
  --parameters demo-output/parameters.json \
  --circuit demo-output/circuit.json \
  --proof demo-output/proof.leash \
  --context leash/example/v1
```

Run `cargo run --release -p leash -- --help` for separate setup, planning,
proving and verification commands. `prove-relation` and `verify-relation` use
typed JSON for a generic relation and its assignment. The verifier accepts
only the relation, parameters and proof; the assignment is a prover input.
Files are created without overwriting existing output.

Install a local CLI with `cargo install --path crates/leash --locked`.
Other languages can call that executable and consume its JSON result. Exit
status zero means success; a failed check returns status 2.

## Rust API

A project in a neighboring checkout can depend on the package by path:

```toml
[dependencies]
leash = { path = "../labrador-rigorous-repair/crates/leash" }
```

For a Git dependency, use the repository URL and pin the reviewed revision.
The repository remains private, so callers need read access.

```toml
[dependencies]
leash = { git = "https://github.com/cxcx52/labrador-rigorous-repair", branch = "main" }
```

```rust
use leash::{frontend::CircuitBuilder, prove, setup, verify, Config, Proof};

fn main() -> Result<(), String> {
    let mut circuit = CircuitBuilder::new();
    let a = circuit.input(true)?;
    let b = circuit.public_input(false)?;
    let c = circuit.xor(a, b)?;
    circuit.pin_public(c, true)?;
    let (statement, assignment) = circuit.finish()?;

    let parameters = setup(Config::default())?;
    let proof = prove(&parameters, &statement, &assignment)?;
    let bytes = proof.to_bytes()?;
    let received = Proof::from_bytes(&bytes)?;
    let result = verify(&parameters, &statement, &received)?;
    assert!(result.accepted);
    Ok(())
}
```

The executable form is [examples/library.rs](../crates/leash/examples/library.rs).
For application separation, use `prove_with_context` and `verify_with_context`
with the same caller-supplied public context. Parameters, the complete statement,
public values, context, proof kind, nonce and attempt number are bound before
protocol challenges are derived.

## Frontend

`CircuitBuilder` supports private inputs, public inputs, AND, XOR, NOT, equality
constraints and public output pins. Wire zero is the constant one. `finish`
returns a `BinaryR1cs` statement and an `Assignment`; they serialize separately.
Callers may instead construct sparse A/B/C rows directly. Each row contains its
nonzero column indices in strictly increasing order.

The native reduction packs `a,b,c,w` and their conjugates into degree-64
polynomials. It includes the source commitment, coefficientwise conjugation,
four bitness checks using the conjugated all-coefficient-ones polynomial, the
product check, scalar source replies, constant/public pins and all padding
constraints. Dimensions need not be multiples of 64. An empty gate set is
supported and receives explicit zero padding.

`verify_source` is a lower-level compiler: it constructs a relation that still
has to be verified by the backend. Applications normally use `leash::verify`.

## Backend and recursion

The backend implements both outer commitments, the 1024-row modular projection,
scalar and ring aggregation, short folding challenges, amortized openings,
decomposition, and the complete next relation. Each upper-triangular Gram entry
is stored once. The verifier reconstructs intermediate relations from public
messages and checks the terminal opening.

The executable path uses full centered-residue base-16 decomposition with eight
digits for commitments and Gram entries. Its norm budgets are deterministic
upper bounds. Structured all-one witnesses therefore do not depend on the
original Gaussian heuristic. Zero padding is enforced by explicit equations,
including padding introduced by recursive repartitioning.

`plan_binary` and `plan_relation` calculate every layer before proving. They
check the modular-JL size condition, derived shapes, resource limits and the
actual commitment-collision bounds at each recursive edge. A radius reaching
the trivial `q`-multiple kernel vector is rejected. Passing these checks does
not certify Module-SIS hardness at the selected ranks.

The default profile uses source rank 6, inner rank 24, outer rank 9, 160 source
challenge rows, six scalar aggregations and one core round. `Config::development`
uses rank 2 commitments for tests. Both profiles use 1024 JL rows and the full
challenge cube `{-2,-1,0,1,2}^64`, whose operator norm is bounded by 128.
This differs from the filtered, tighter parameter path in the research ledger.
Supported depth is 0–3, subject to the per-layer parameter checks; unsupported
combinations return an error. Depth zero sends the source target opening directly.

Complete honest attempts are bounded by `max_attempts`. A failed JL check restarts
the whole source-and-core execution with a new attempt domain. This is an honest
generator policy; it does not limit a malicious party's random-oracle queries.

See [the executable protocol](rust-protocol.md) for the equations and norm bounds.

## Calling the backend from another proof system

`prove_relation`, `verify_relation` and their context-bearing variants take
`leash::algebra::Relation` and `Witness` directly. A relation specifies blocks,
block length, an honest squared-norm bound, full ring equations and constant-term
equations. A quadratic term multiplies a coefficient by the dot product of two
blocks. A linear term addresses one polynomial in one block. All terms plus
`constant` sum to zero.

For a generic relation with core rounds, the interactive extraction theorem
allows squared input norm up to `23/5` times the honest bound. The parameter plan
and verification report expose the ceiling of this quantity. With no core
rounds, the strict input norm is checked directly. A caller such as Pikkufold
must map its terminal equations and **actual extracted norm** into this interface;
this repository does not yet contain a Pikkufold-specific adapter.

For the binary frontend, the source lifting inequalities already account for
the relaxed cap, so its intended source statement is still the original binary
R1CS with its public pins.

## Transport and resources

Proof transport has a versioned header, prover messages and one terminal opening.
Polynomials use centered zigzag integers and the minimum bit width for each
64-coefficient polynomial. An all-zero polynomial takes one byte. Decoding checks
canonical widths and residues, all counts, truncation and trailing bytes before
verification. Verifier challenges are regenerated, not accepted from a proof file.

The current frontend supports at most 4096 variables and 4096 constraints, with
65536 sparse nonzeros. Its JSON helper accepts at most 4 MiB. Proof transport is
limited to 64 MiB and at most 262144 terminal polynomials. Generic relation limits
are exposed by `leash-core`; they bound structure, not peak memory. These limits
are deliberate properties of this portable release.

The terminal plan's `terminal_opening_u32_bytes` is the size of an uncompressed
32-bit coefficient encoding, not a heap-memory estimate. `VerificationReport.proof_bytes` is the actual complete serialized
proof size. Neither includes public parameters, statement bytes or application
framing. Larger dimensions, NTT/SIMD acceleration, a tighter filtered challenge
profile, zero knowledge and a proved noninteractive compiler are further work.

## Tests and measurements

The tests exercise arithmetic against independent Python known answers, complete
source constraints, ordinary and two-round recursion, context/public-input
binding, malformed messages, and strict wire decoding. The full pipeline accepts
the structured all-one identity-R1CS witness using deterministic norm bounds.

For sequential end-to-end measurements on sizes 64, 256 and 1024:

```sh
cargo run --release -p leash --example measure -- 1
```

To retain the source revision, environment, logs, hashes and summary from a clean
checkout, use:

```sh
python experiments/run_rust_benchmarks.py --out work/rust-measurement --rounds 1
```

Each size uses three fresh setups. The synthetic identity circuits have all-one
assignments. Reported proof sizes are measured bytes; their easy constraints
and the current conservative profile are stated explicitly. These measurements
do not compare against the original C backend or reproduce the old 157 KiB ledger.
