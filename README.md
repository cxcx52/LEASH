# Rigorous repairs for LaBRADOR

Mathematical repair notes and exact, executable certificates for the 34-page version of [LaBRADOR: Compact Proofs for R1CS from Module-SIS](https://eprint.iacr.org/2022/1341), by Ward Beullens and Gregor Seiler.

**Research closeout, 14 November 2026.** At the author's request this work is
concluded at the documented audit, conditional repairs, parameter certificates
and bounded implementation experiments. Start with [the final handoff](CLOSEOUT.md)
and [claim ledger](docs/status.md). Full-backend development and cross-project
integration are outside this completed batch; historical plans are not active tasks.

This repository develops explicit replacements for several numerical and algebraic steps. It is a research contribution, not a production proof system or a claim that the original construction is irreparable. Classical tools are credited; no priority claim is made for the probability inequalities used here.

Start with the [assessment of the main proof chain](research/notes/critical_path_assessment.md): the findings affect necessary dependencies of the advertised end-to-end conclusions, including probability bounds, source arithmetic, extraction interfaces, and concrete accounting. The contributions include exact counterexamples, corrected theorems, quantitative refinements, and explicit reconstruction costs, beyond the protocol variants themselves.

## What is established

- **Uniform modular JL bound.** For a fixed centered integer vector with norm at least b, b<=q/250, a 1024-row ternary projection satisfies `Pr(||Pi w mod q||^2 <= 120 b^2) < 2^-164`. The proof covers all dimensions and all positive integer moduli, with closed-event boundaries.
- **Honest projection completeness.** The threshold `552 beta^2` accepts a fixed honest vector of norm at most beta with probability at least `25/33`. The resulting norm slack is `sqrt(23/5)`.
- **Security-parameter family.** For every integer `lambda>=128`, explicit integer parameters give a uniform projection error below `2^(-lambda-32)`, with the same norm slack. The all-parameter proof includes the growing wrap union bound; it does not rely on enumerating parameter examples.
- **Exact challenge family.** Coefficients in `{-2,-1,0,1,2}` give exactly `5^64` challenges, with deterministic operator norm at most 128. Appropriate prime moduli ensure invertible differences. There is no rejection-sampling cardinality estimate in this choice.
- **Certified filtered alternative.** Restricting the same cube to operator norm strictly below 31 retains more than `(9/16)*5^64` challenges, with expected raw candidate count below `16/9`. An exact integer predicate handles the strict boundary. The proof supplies a cardinality lower bound without assuming that conditioned coefficients remain independent.
- **Certified Fourier predicate.** Integer Fourier enclosures with an exact fallback decide precisely the same filtered set. The fast path uses quadratic arithmetic operations; unresolved inputs retain the cubic exact check.
- **Filtered folding moments.** Covariance symmetry, the paired real spectrum of ring multiplication, and centered conditional variance give a rigorous honest-fold bound. At d=64,T=34, the cap `Gamma^2=(21/2)*d*beta^2` has rejection probability at most `1/16` for any fixed ring vectors of total squared norm at most beta squared.
- **Bounded-energy alternative.** At d=64, restricting squared coefficient norm to 104 and operator norm to strictly below 30 leaves a certified challenge set above `2^143`. Exact counting and dependent-coordinate moments permit `Gamma^2=9*d*beta^2` at folding failure at most `1/16`. This trades some challenge entropy for smaller norm bounds.
- **Affine-R1CS repair.** The proposed reduction specifies a constant wire, public-input constraints, centered lifts, both commitment equations, corrected aggregation indices and residual equations, and the sufficient lifting condition `sqrt(Md/2)*beta + beta^2/2 < q/2`.
- **Universal ordinary-core extraction.** One classical expected-polynomial-time extractor needs no acceptance-rate estimate. Its statistical knowledge error is `delta_JL + q^(-m) + q^(-d/2) + (r+2)/|C|`, with explicit computational losses and MSIS assumptions. The output uses the stated relaxed norm relation.
- **Tighter computational loss.** Retaining bad-anchor probability mass improves the earlier fourth-root scaling to a cubic-root bound for the same full collision experiments. The refined term is `sqrt(eta_0)+(2*eta_h+2*r*eta_y+eta_g)^(1/3)+eta_E`, with a tighter exact version. Every advantage still refers to the complete reduction at its actual runtime.
- **Controlled composition.** Ordinary layers compose additively under explicit fresh-randomness, relation-matching and runtime-product conditions. The affine-R1CS-plus-core corollary uses the actual extracted norm in the lifting and binding bounds.
- **Bounded complete-protocol restarts.** A gate-preserving extractor extends to adaptive rejected histories under a fixed statement. With at most Q complete attempts, statistical errors add across attempts; honest failure is at most `(1-a)^Q` when every reached attempt accepts with probability at least a.
- **Full statistical parameter family.** Scaling the ring degree and aggregation count as well as the projection gives a negligible ordinary-core statistical budget. The arithmetic certificate separates this budget from lattice hardness and lifting conditions.
- **Complete native binary interface.** Coefficient-level public pins, explicit conjugation, aligned padding, integer parity and a separate source-binding role connect the native frontend to the core under stated extraction premises.
- **Short source and aggregation challenges.** Classical random-evaluation fingerprints replace the respective independent coefficient families, with explicit field certificates and revised error bounds. The native source challenge uses 187 bits; seven layers of the two core aggregation challenges use 1960 bytes. The dense JL challenge family is unchanged.

## What is not established

The standalone `552 beta^2` completeness theorem and the final `H=640`,
squared-slack `16/3` parameter path are separate instantiations. The statistical
formula shown above for ordinary-core extraction uses independent aggregation
coins; the fingerprint variant uses the revised polynomial-degree terms in its
ledger. The smallest encoding reported below is limited to the recorded paths
and finite search domain, not a global optimum over all protocols or parameters.

The changed projection and challenge parameters do **not** certify the original 58 KB result. This package does not implement a cryptographic prover or verifier, prove Fiat-Shamir or QROM security, or claim zero knowledge. The optional [research archive](research/README.md) supplies exact recursive schedules and pinned heuristic SIS cost outputs, with separate Sage reproduction scripts. These are cost-model evaluations, not lattice-solving experiments or a complete security level.

The current smallest ordinary-core encoding bound is **155.1484375 KiB per complete attempt**, using the bounded-energy family and independently screened outer ranks. The specified native source raises the prover-message bound to 157.17578125 KiB, or **157.265625 KiB (161040 bytes)** with its fingerprint variant and byte padding. Setup and statement, verifier messages, framing, Fiat-Shamir material, and rejected attempts are separate. The complete fingerprint variant still has about 67.54 GiB of explicitly encoded verifier traffic, dominated by independent JL matrices. This is not a succinct-verifier result. The archive preserves the full parameter path, source interface, finite-domain optimization, earlier comparison stages, and original result hashes. Complete computational security at the actual reduction runtimes remains open.

The source audit identifies the PDF by SHA-256 `87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581`. Third-party PDFs are not redistributed.

## Reproduce

The [recorded implementation experiments](experiments/README.md) add a portable
native-frontend reference, full-witness encoding/decoding, exact-predicate
microbenchmarks, and a subprocess recorder. Their scope is separate from a
complete compact recursive prover or a numerical security certification.
The [first recorded CPU batch](docs/experiment-results/2026-11-14-first-cpu/README.md)
includes 38 successful processes, actual full-witness transport sizes, paired
kernel timings, and the raw records needed to reproduce the summary.

Python 3.10 or later; the package has no runtime dependencies.

```sh
python -m venv .venv
# Activate the virtual environment for your operating system.
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/certify.py
python examples/statistical_family.py
python examples/gated_rows.py
python examples/certified_challenges.py
python examples/certified_fourier.py
python examples/bounded_restarts.py
python examples/filtered_folding.py
python examples/bounded_energy.py
python examples/refined_loss.py
```

The tests check exact rational constants, finite distributions, boundary counterexamples, all small NAF encodings, all degree-4 challenge differences, affine public-input pinning, and integer lifting. They support the proofs; finite tests do not prove universally quantified theorems by themselves.

## Read the mathematics

- [Uniform modular JL theorem](docs/modular-jl.md)
- [JL family for every security parameter](docs/jl-security-family.md)
- [Affine-R1CS reduction](docs/affine-r1cs.md)
- [Challenge family and parameter obligations](docs/challenges.md)
- [Certified operator-norm-filtered alternative](docs/certified-filtered-challenges.md)
- [Exact Fourier enclosure and fallback](docs/certified-fourier.md)
- [Filtered folding covariance and fourth moments](docs/filtered-folding-moments.md)
- [Bounded-energy challenges and exact moment certificates](docs/bounded-energy-challenges.md)
- [Conditional main-protocol algebra](docs/protocol-conditional.md)
- [Finite computational extraction theorem](docs/finite-extraction.md)
- [Universal extraction without a known acceptance gap](docs/unknown-gap-extraction.md)
- [Refined computational losses and their limits](docs/refined-computational-loss.md)
- [Bounded complete-protocol restarts](docs/bounded-restarts.md)
- [Statistical parameter family](docs/statistical-family.md)
- [Claim and verification ledger](docs/status.md)
- [Research parameter archive and reproduction guide](research/README.md)

## Contribute

Please distinguish a theorem, a numerical certificate, an experiment, and an unresolved conjecture. A correction should identify the exact claim, its hypotheses, and a proof or reproducible counterexample. Performance claims require a complete parameter and error ledger. Do not report a statistical upper bound as an attack success rate.

Original code and notes in this repository are provided under the MIT license. The original LaBRADOR paper and other cited works retain their respective licenses and authorship.
