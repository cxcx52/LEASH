# LEASH

A callable binary R1CS frontend and an ordinary recursive lattice-argument
backend. The crate provides setup, proof generation, canonical byte transport,
verification, a circuit builder and a generic quadratic-relation interface.

```rust
use leash::{frontend::CircuitBuilder, prove, setup, verify, Config};

fn main() -> Result<(), String> {
    let mut builder = CircuitBuilder::new();
    let a = builder.input(true)?;
    let b = builder.public_input(false)?;
    let output = builder.xor(a, b)?;
    builder.pin_public(output, true)?;
    let (statement, assignment) = builder.finish()?;
    let parameters = setup(Config::default())?;
    let proof = prove(&parameters, &statement, &assignment)?;
    assert!(verify(&parameters, &statement, &proof)?.accepted);
    Ok(())
}
```

This is a research implementation. Its seed-expanded CRS and SHAKE Fiat–Shamir
compiler have no certified security level; the protocol is not zero knowledge.
The complete API, parameter semantics, generic backend integration and CLI are
described in [the library guide](../../docs/usage.md).
