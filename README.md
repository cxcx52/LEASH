# Rigorous repairs for LaBRADOR

Mathematical repair notes and exact, executable certificates for the 34-page version of [LaBRADOR: Compact Proofs for R1CS from Module-SIS](https://eprint.iacr.org/2022/1341), by Ward Beullens and Gregor Seiler.

This repository develops explicit replacements for several numerical and algebraic steps. It is a research contribution, not a production proof system or a claim that the original construction is irreparable. Classical tools are credited; no priority claim is made for the probability inequalities used here.

## What is established

- **Uniform modular JL bound.** For a fixed centered integer vector with norm at least b, b<=q/250, a 1024-row ternary projection satisfies `Pr(||Pi w mod q||^2 <= 120 b^2) < 2^-164`. The proof covers all dimensions and all positive integer moduli, with closed-event boundaries.
- **Honest projection completeness.** The threshold `552 beta^2` accepts a fixed honest vector of norm at most beta with probability at least `25/33`. The resulting norm slack is `sqrt(23/5)`.
- **Security-parameter family.** For every integer `lambda>=128`, explicit integer parameters give a uniform projection error below `2^(-lambda-32)`, with the same norm slack. The all-parameter proof includes the growing wrap union bound; it does not rely on enumerating parameter examples.
- **Exact challenge family.** Coefficients in `{-2,-1,0,1,2}` give exactly `5^64` challenges, with deterministic operator norm at most 128. Appropriate prime moduli ensure invertible differences. There is no rejection-sampling cardinality estimate in this choice.
- **Affine-R1CS repair.** The proposed reduction specifies a constant wire, public-input constraints, centered lifts, both commitment equations, corrected aggregation indices and residual equations, and the sufficient lifting condition `sqrt(Md/2)*beta + beta^2/2 < q/2`.

## What is not established

The changed projection and challenge parameters do **not** certify the original 58 KB result. This package does not implement a cryptographic prover or verifier, rerun a Module-SIS hardness estimator, prove Fiat-Shamir or QROM security, or claim zero knowledge. The full main-protocol extraction and composition obligations are tracked separately; a conditional statistical budget is not a complete security level.

The source audit identifies the PDF by SHA-256 `87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581`. Third-party PDFs are not redistributed.

## Reproduce

Python 3.10 or later; the package has no runtime dependencies.

```sh
python -m venv .venv
# Activate the virtual environment for your operating system.
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/certify.py
```

The tests check exact rational constants, finite distributions, boundary counterexamples, all small NAF encodings, all degree-4 challenge differences, affine public-input pinning, and integer lifting. They support the proofs; finite tests do not prove universally quantified theorems by themselves.

## Read the mathematics

- [Uniform modular JL theorem](docs/modular-jl.md)
- [JL family for every security parameter](docs/jl-security-family.md)
- [Affine-R1CS reduction](docs/affine-r1cs.md)
- [Challenge family and parameter obligations](docs/challenges.md)
- [Conditional main-protocol algebra](docs/protocol-conditional.md)
- [Finite computational extraction theorem](docs/finite-extraction.md)
- [Claim and verification ledger](docs/status.md)

## Contribute

Please distinguish a theorem, a numerical certificate, an experiment, and an unresolved conjecture. A correction should identify the exact claim, its hypotheses, and a proof or reproducible counterexample. Performance claims require a complete parameter and error ledger. Do not report a statistical upper bound as an attack success rate.

Original code and notes in this repository are provided under the MIT license. The original LaBRADOR paper and other cited works retain their respective licenses and authorship.
