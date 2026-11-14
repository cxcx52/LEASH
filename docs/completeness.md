# Completeness example

```sh
cargo run --release --locked -p leash --example completeness
```

The example checks a 448-variable binary R1CS instance with `A = B = C = I`
and the all-one assignment. It prints two JSON records:

1. An exact check of the original fixed-profile norm budget.
2. A complete LEASH proof, serialization, decoding, and verification run for
   the same source instance.

## Original norm budget

Let `J = 1 + X + ... + X^63`. Pack the witness into four blocks containing
seven copies of `J` and four containing seven copies of its conjugate.
This gives `r = 8`, `n = 7`, and squared norm `3584`.

With degree 64, modulus 4,294,967,197, `tau = 71`, and inner rank `kappa = 24`,
the original rounding rules give:

| Parameter | Value |
| --- | ---: |
| Folding base `b` | 9 |
| Residue digits `t1` | 10 |
| Residue base `b1` | 10 |
| Gram digits `t2` | 2 |
| Gram base `b2` | 10 |

The example explicitly computes all 36 upper-triangular Gram entries by
integer negacyclic multiplication. Their total squared norm is 154,215,936.
For any two-digit modular reconstruction `g = u0 + 10*u1`, centered lifting
and Cauchy–Schwarz give:

```text
||u0||² + ||u1||² >= ||g||² / 101.
```

The Gram digits alone therefore require squared norm at least
`154,215,936 / 101`. The original total budget is `102,115,328 / 81`.
The lower bound exceeds the budget by `2,177,842,688 / 8,181`.
All remaining target contributions are nonnegative. The result holds for
every modular two-digit reconstruction and does not depend on challenge coins.

The parameter rules are in Section 5.4 of
[LaBRADOR](https://eprint.iacr.org/2022/1341); the budget is Equation (5),
and the ordinary verifier's norm check is Figure 3, line 14. The calculation
uses the stated coefficientwise binary packing and its public worst-case norm
bound. The inner rank matches LEASH's default profile.

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
