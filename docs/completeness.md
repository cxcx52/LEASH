# Completeness example

```sh
cargo run --release --locked -p leash --example completeness
```

The example checks a 192-variable binary R1CS instance with `A = B = C = I`
and the all-one assignment. It prints two JSON records:

1. An exact check of the original fixed-profile norm budget.
2. A complete LEASH proof, serialization, decoding, and verification run for
   the same source instance.

## Original norm budget

Let `J = 1 + X + ... + X^63`. Pack the witness into four blocks containing
three copies of `J` and four containing three copies of its conjugate.
This gives `r = 8`, `n = 3`, and squared norm `1536`.

With degree 64, modulus 4,294,967,197, `tau = 71`, and test rank `kappa = 1`,
the original rounding rules give:

| Parameter | Value |
| --- | ---: |
| Folding base `b` | 9 |
| Residue digits `t1` | 10 |
| Residue base `b1` | 10 |
| Gram digits `t2` | 2 |
| Gram base `b2` | 8 |

The example explicitly computes all 36 upper-triangular Gram entries by
integer negacyclic multiplication. Their total squared norm is 28,325,376.
For any two-digit modular reconstruction `g = u0 + 8*u1`, centered lifting
and Cauchy–Schwarz give:

```text
||u0||² + ||u1||² >= ||g||² / 65.
```

The Gram digits alone therefore require squared norm at least
`28,325,376 / 65`. The original total budget is `7,072,256 / 27`.
The lower bound exceeds the budget by `305,088,512 / 1,755`.
All remaining target contributions are nonnegative. The result holds for
every modular two-digit reconstruction and does not depend on challenge coins.

The parameter rules are in Section 5.4 of
[LaBRADOR](https://eprint.iacr.org/2022/1341); the budget is Equation (5),
and the ordinary verifier's norm check is Figure 3, line 14. The calculation
uses the stated coefficientwise binary packing and its public worst-case norm
bound. Rank one is a small test configuration, with no assigned security level.

This check covers the fixed ordinary-round norm budget. It does not execute
the original source compiler, complete recursive verifier, adaptive parameter
enlargement, or upstream C implementation.

## LEASH round trip

The second record uses LEASH's default profile and full verifier. It generates
a proof for the same binary instance, encodes it, decodes and re-encodes it,
checks canonical byte equality, and verifies the proof. Its output includes
the configuration, proof size, retry count, and verification report.

The two records use different parameter profiles. Their purpose is to show
the fixed-budget failure and the current library's handling of that source
instance; they are not a performance comparison.
