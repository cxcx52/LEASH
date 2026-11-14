![LEASH](assets/labrador.png)

# LEASH

LEASH is a Rust library for binary R1CS proofs and recursive lattice arguments.
It provides a circuit builder, a generic quadratic-relation backend, proof
serialization, and a command-line prover and verifier.

[Usage](docs/usage.md) · [Benchmarks](benchmarks/README.md) · [Affected papers](impact/README.md) · [Related implementations](impact/REPOSITORIES.md)

## Quick start

Requires Rust 1.85 or later. From the repository root:

```sh
cargo run --release --locked -p leash --example library
cargo run --release --locked -p leash -- demo --out demo-output
cargo run --release --locked -p leash -- verify --parameters demo-output/parameters.json --circuit demo-output/circuit.json --proof demo-output/proof.leash --context leash/example/v1
```

The demo creates a circuit, its assignment, public parameters, a proof, and a
verification report. The separate verification command uses only the public
inputs and proof.

## Use as a library

```toml
[dependencies]
leash = { git = "https://github.com/cxcx52/labrador-rigorous-repair", branch = "main" }
```

```rust
use leash::{frontend::CircuitBuilder, prove, setup, verify, Config};

fn main() -> Result<(), String> {
    let mut circuit = CircuitBuilder::new();
    let a = circuit.input(true)?;
    let b = circuit.public_input(false)?;
    let output = circuit.xor(a, b)?;
    circuit.pin_public(output, true)?;
    let (statement, assignment) = circuit.finish()?;

    let parameters = setup(Config::default())?;
    let proof = prove(&parameters, &statement, &assignment)?;
    assert!(verify(&parameters, &statement, &proof)?.accepted);
    Ok(())
}
```

The frontend supports AND, XOR, NOT, equality constraints, and public input and
output pins. Use `prove_relation` and `verify_relation` to supply quadratic ring
relations directly. `Proof::to_bytes` and `Proof::from_bytes` provide canonical
transport. Other languages can invoke the CLI and read its JSON output.

The [usage guide](docs/usage.md) covers context binding, parameter planning,
supported dimensions, and the generic backend's norm semantics.

LEASH is experimental. Its SHAKE Fiat–Shamir compiler has no established security
proof, and the implementation is not zero knowledge.

## Benchmarks

End-to-end measurements on an Intel Core i9-13980HX, using the default profile
and one recursive reduction. Each row summarizes three runs on an all-one
identity R1CS instance of the indicated size.

| Variables = constraints | Proof bytes | Prove median | Verify median |
| ---: | ---: | ---: | ---: |
| 64 | 83,923–84,099 | 401 ms | 161 ms |
| 256 | 84,603–84,731 | 477 ms | 227 ms |
| 1,024 | 84,787–84,899 | 865 ms | 487 ms |

All nine proofs verified after serialization and decoding.
[Configuration, results, and reproduction](benchmarks/README.md).

The [completeness example](docs/completeness.md) checks a small, deterministic
counterexample to the original fixed-profile norm budget, then completes a
LEASH proof and verification for the same binary instance:

```sh
cargo run --release --locked -p leash --example completeness
```

## Development

```sh
cargo test --workspace --all-targets --release --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo fmt --all -- --check
cargo doc --workspace --no-deps --open
```

| Directory | Contents |
| --- | --- |
| `crates/leash` | Library API, recursive prover/verifier, codec, CLI, and examples |
| `crates/leash-frontend` | Binary circuit builder and R1CS frontend |
| `crates/leash-core` | Ring arithmetic, relations, transcripts, and commitments |
| `docs` | Integration guide |
| `benchmarks` | End-to-end results and reproduction commands |
| `impact` | Affected papers and implementation dependencies |

## Affected papers and implementations

| Dependency | Papers |
| --- | --- |
| Exact lower-tail bound | RoKoko (ASIACRYPT), Orthus (CRYPTO) |
| Numerical premise or norm slack | Grand Danois (ePrint), Aggregating Falcon Signatures (CRYPTO), Symphony (ASIACRYPT), Toolkit (CCS), Lemur+ (ePrint) |
| Backend or composition | Greyhound (CRYPTO), Hachi (ePrint), LaZer (CCS), Unmasking TRaccoon (CRYPTO), LaBinius (ePrint) |
| Optional LaBRADOR compression | RoK, Paper, SISsors (ASIACRYPT); LatticeFold (ASIACRYPT); Serval (ePrint) |

The [paper table](impact/README.md) identifies the affected claim, configuration,
and source pages. The [implementation table](impact/REPOSITORIES.md) covers
`lattice-dogs/labrador`, `lazer-crypto/labrador`, `lazer-crypto/lazer`,
`dfaranha/aggregate-falcon`, `georgeorourke/hachi-pcs`, `osdnk/labinius`,
`lattice-arguments/rokoko`, and `dingdangdangwhx/Lemur-plus`, with links to the
relevant source code.

## License

[MIT](LICENSE).
