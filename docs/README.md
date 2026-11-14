# Mathematical results

The audit follows the proof chain from probability bounds and source relations to extraction, composition and concrete parameters. The repair develops explicit hypotheses and exact certificates for each step.

| Topic | Guide | Detailed evidence |
| --- | --- | --- |
| Audit findings | [Main proof-chain assessment](../research/notes/critical_path_assessment.md) | [Claim ledger](status.md) |
| Modular projection and completeness | [Modular JL](modular-jl.md) · [Security-parameter family](jl-security-family.md) | [Full proof](../research/proofs/modular-jl.md) |
| Source arithmetic | [Affine R1CS](affine-r1cs.md) | [Native binary interface](../research/proofs/native_binary_source_interface.md) |
| Challenges | [Cube family](challenges.md) · [Filtered family](certified-filtered-challenges.md) | [Exact Fourier predicate](certified-fourier.md) |
| Folding | [Conditional moments](filtered-folding-moments.md) · [Bounded energy](bounded-energy-challenges.md) | [Parameter ledgers](../parameters/README.md) |
| Extraction | [Finite extraction](finite-extraction.md) · [Unknown acceptance gap](unknown-gap-extraction.md) | [Refined computational losses](refined-computational-loss.md) |
| Composition | [Protocol algebra](protocol-conditional.md) · [Complete restarts](bounded-restarts.md) | [Layer composition](../research/proofs/composition_repair.md) |
| Parameters and measurements | [Statistical family](statistical-family.md) | [Recorded benchmarks](../benchmarks/README.md) |

The [Rust library](rust-library.md) implements the binary frontend and ordinary
recursive prover/verifier, including proof transport and a CLI. Its
[protocol guide](rust-protocol.md) connects each executed check to the equations.
The Python package retains the exact certificates and earlier native reference.
The noninteractive compiler is experimental; a security proof for that compiler
and complete concrete computational-security analysis remain open.

The [research archive](../research/README.md) retains the longer derivations, internal reviews, earlier parameter paths and pinned model outputs. The [14 November handoff](../CLOSEOUT.md) records the completed research scope.
