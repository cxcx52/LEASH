# Benchmarks

These runs use binary R1CS instances with `A = B = C = I` and the all-one
assignment. Each size is measured three times with fresh public parameters.
All nine proofs verified after encoding and decoding.

| Variables = constraints | Proof bytes, min–max | Prove median (ms) | Verify median (ms) | Encode median (ms) | Decode median (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 83,923–84,099 | 400.807 | 160.807 | 0.713 | 3.152 |
| 256 | 84,603–84,731 | 477.447 | 226.623 | 0.643 | 2.815 |
| 1,024 | 84,787–84,899 | 864.888 | 486.945 | 0.685 | 2.927 |

Proof sizes include the header, source commitment and replies, recursive
messages, and terminal opening. Public parameters and the circuit are separate
inputs. Proving times include any complete-session retry; verification times
include reconstruction of the public relations and checking the terminal opening.

## Configuration

The default profile uses degree 64, modulus 4,294,967,197, source rank 6, inner
rank 24, outer rank 9, 160 source rows, 1,024 JL rows, and six scalar aggregation
challenges. These measurements use one recursive reduction.

The machine is an Intel Core i9-13980HX running Windows 11. The protocol runs
sequentially on one thread in a release build with Rust 1.98.0. One of the three
1,024-variable runs required a complete-session retry and took 1,274.292 ms to
prove. The remaining runs succeeded on their first attempt.

[Per-run measurements](results.jsonl) · [Summary and measured source revision](summary.json)

## Reproduce

Run from the repository root:

```sh
cargo run --release --locked -p leash --example measure -- 1
```

The example emits one JSON object per run, including setup, proof generation,
encoding, decoding, verification, actual proof size, and retry count. Replace
`1` with `2` to measure two recursive reductions. Setup and proof nonces use OS
randomness, so proof sizes and retry counts can vary between runs.
