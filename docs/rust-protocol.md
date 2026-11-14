# Rust ordinary reduction: equations and implementation scope

The Rust library implements the ordinary outer-commitment reduction and
recursively constructs its target relation. It provides a binary R1CS frontend
and a separate entry point for an existing quadratic relation. The implementation
uses a seed-expanded setup and an experimental SHAKE transcript compiler. The
interactive extraction theorems in this repository do **not** establish the
security of that compiler, a production security level, or zero knowledge.

This document describes [ordinary.rs](../crates/leash/src/ordinary.rs). The
pipeline and serialization are separate modules. The executable profile is a
simple full-residue decomposition profile; it is not the optimized bounded-energy
parameter path in the research archive.

## Ring, input relations, and supported profile

The ring is `R = Z_q[X]/(X^64+1)`, with `q = 4294967197`. Serialized polynomials
contain exactly 64 canonical residues. Integer norms use their centered
representatives. A witness has `r` blocks of `n` ring elements, written `s_i`.

Every constraint is represented with the convention

```text
C + sum_(i,j) a_ij <s_i,s_j> + sum_(i,l) phi_i,l s_i,l = 0.
```

The inner product here is bilinear ring multiplication and addition, without
conjugation. It is distinct from the Euclidean norm of integer coefficients.
Each stored quadratic term is counted once, including off-diagonal terms. An
input can store both orientations; aggregation adds their coefficients to the
same upper-triangular entry. A full constraint checks the entire polynomial. A
scalar constraint checks only its constant coefficient. Both kinds include the
public constant `C`. The input relation also checks the closed norm cap
`sum_i ||s_i||^2 <= beta^2`.

The supported implementation ranges are:

- inner and outer commitment ranks from 1 through 64;
- exactly 1024 projection rows;
- scalar aggregation count `K` from 6 through 8;
- radix 16, with eight digits for every centered residue of `t`, `g`, and `h`;
- two radix components for `z`, and fixed target block count eight.

These ranges are implementation limits, not certified security parameters.
Before sampling, the backend checks

```text
23 * 250^2 * beta^2 <= 5 * q^2.
```

The check is the modular-JL parameter premise used by the repaired profile.
It does not by itself certify the complete protocol.

## Messages and challenge order

The public context includes the round index, configuration, setup seed, and full
input relation. The order is

```text
u1 -> Pi -> p -> (psi, omega) -> b'' -> (alpha, beta) -> u2 -> c.
```

There is no challenge derived before the prover message that should precede it.
For an interactive reading, challenges at these positions are independent
verifier randomness. In this executable compiler, domain-separated SHAKE streams
derive them from the accumulated transcript. Public matrix rows use separate
domains for the inner matrix, `u1`, and `u2`, including the round index. Row
expansion has a stable column prefix.

The prover computes

```text
t_i = A s_i,
g_ij = <s_i,s_j>                  for i <= j,
u1 = B1 * (digits(t) || digits(g)).
```

Each projection entry has distribution `Pr[-1]=Pr[1]=1/4`, `Pr[0]=1/2` in the
independent-randomness interpretation. Let `w` be the concatenated centered
coefficient vector. The prover sends `p = center_q(Pi w)`. Verification checks its
length, canonical centered encoding, and

```text
sum_j p_j^2 <= 552 * beta^2.
```

For scalar aggregation `k`, the implementation forms the nonconstant part of
the weighted input scalar constraints, then adds the projection linear form
weighted by `omega_k`. A projection coefficient vector is conjugated when it is
converted to a ring coefficient, so its ring constant term is exactly the
integer coefficient dot product modulo `q`.

The prover sends the full polynomial value `b''_k` of this combined nonconstant
part. The verifier checks

```text
ct(b''_k) = -sum_j psi_k,j * ct(C_j) + sum_a omega_k,a * p_a mod q.
```

The minus sign on the public scalar constants is necessary. The subsequent
ring equation uses this nonconstant part minus `b''_k`; it does not add the
scalar constants again. The verifier aggregates these equations and the input
full equations with ring challenges, producing

```text
F(s) = C_F + sum_(i<=j) a_ij <s_i,s_j> + sum_i <phi_i,s_i> = 0.
```

The prover then computes

```text
h_ij = (<phi_i,s_j> + <phi_j,s_i>) / 2     for i <= j,
u2 = B2 * digits(h).
```

Division by two uses the inverse of two modulo the odd modulus. After `u2`,
the final challenges have independently sampled coefficients in
`{-2,-1,0,1,2}` in the interactive interpretation, and
`z = sum_i c_i s_i`. This profile uses the entire cube, including zero; it does
not implement the archive's optional operator-norm or energy filters.

## Decomposition, packing, and all target equations

For each centered coefficient of `t`, `g`, or `h`, the first seven radix digits
lie in `[-8,7]`, and the last digit lies in `[-8,8]`. All eight digits are
retained. Thus the stored digits reconstruct every centered residue exactly
as an integer before reduction modulo `q`.

Write `z = z0 + 16*z1` coefficientwise, with `z0` in `[-8,7]`. No separate
per-digit range constraints are imposed on an extracted target witness; the
target global norm controls it, as in the repaired extraction analysis.

Let

```text
G = r*(r+1)/2,
M = 8*r*kappa + 16*G,
v = digits(t) || digits(g) || digits(h),
z_stride = ceil(n/2),
v_stride = ceil(M/4),
n' = max(z_stride, v_stride).
```

The `t` order is block, digit, inner-matrix row. The `g` and `h` order is
lexicographic upper-triangular pair, then digit. Each off-diagonal pair is
stored once. The two aligned chunks of `z0` occupy target blocks 0 and 1; the
same chunks of `z1` occupy blocks 2 and 3. Four chunks of `v` occupy blocks
4 through 7. Extending the common target block length to `n'` only adds trailing
zero slots; it never changes the chunk stride of `z0` or `z1`.

Using `w_ij = 1` for `i=j` and `2` for `i<j`, the verifier builds the following
full ring equations from public messages and derived challenges:

```text
A z - sum_i c_i t_i = 0,                         kappa equations

<z,z> - sum_(i<=j) w_ij*c_i*c_j*g_ij = 0,

sum_i c_i <phi_i,z>
    - sum_(i<=j) w_ij*c_i*c_j*h_ij = 0,

C_F + sum_(i<=j) a_ij*g_ij + sum_i h_ii = 0,

B1*(digits(t)||digits(g)) - u1 = 0,             outer_rank equations
B2*digits(h) - u2 = 0.                          outer_rank equations
```

Every occurrence of `t`, `g`, and `h` is expanded into its radix digits; every
occurrence of `z` is expanded into `z0+16*z1`. In particular, a quadratic `z`
chunk contributes coefficients `1`, `32`, and `256` on `z0*z0`, `z0*z1`, and
`z1*z1`. The coefficient `a_ij` in the fourth equation already includes the
input's stored orientation multiplicities. It receives no extra factor two.

**Every unassigned target ring slot is explicitly constrained to zero.** This
includes unused `z` chunks and unused `v` slots. Whole-block quadratic terms
otherwise include coordinates that were not assigned by the honest packing.
There is one full linear zero constraint per such ring slot. Consequently the
number of full equations is

```text
kappa + 2*outer_rank + 3 + (8*n' - 2*n - M).
```

The target has no scalar equations. The prover checks the generated target
against its generated witness. The verifier reconstructs that same target
using only the input relation, public messages, setup, and transcript state.

## Deterministic honest norm cap

For every cube challenge, its multiplication operator norm is at most its
coefficient `l1` norm, at most 128. Thus, for every challenge outcome,

```text
||center_q(z)||^2 <= r * 128^2 * beta^2.
```

The low coefficients contribute at most `64*n*64` to the squared norm. From
`z1=(center_q(z)-z0)/16` and `(a+b)^2 <= 2a^2+2b^2`, the high components
contribute at most `128*r*beta^2 + n*64/2`. The `M` residue-digit polynomials
contribute at most `M*64*64`. The target's closed squared cap is therefore

```text
beta_next^2 = n*64*64 + 128*r*beta^2 + ceil(n*64/2) + M*64*64.
```

This cap covers every valid input witness and every final challenge. It uses
no Gaussian digit estimate or average Gram-matrix assumption. The projection
norm check can still cause an honest abort. The pipeline retries the complete
session with a changed attempt value, rebuilding every preceding message; it
does not retry an internal projection while retaining a previous commitment.
Exhausting the configured attempt limit returns an error.

## Recursion, parameter checks, and security boundaries

The exact honest target cap becomes the next round's input parameter. In the
conditional interactive extraction analysis, the next extractor may return a
witness with squared norm up to `(23/5)*beta_next^2`. The parent layer's
binding-radius calculation therefore uses

```text
B_i^2 = ceil((23/5)*beta_next^2)    if another reduction follows,
B_i^2 = beta_next^2                at the final explicit opening.
```

The corresponding conservative integer upper bounds used by the pipeline are

```text
outer collision: 2*ceil_sqrt(B_i^2),
inner weak collision: 8*128*17*ceil_sqrt(B_i^2),
inner strong collision:
    2*17*ceil_sqrt(B_i^2)
    + 4*128*ceil_sqrt(ceil((23/5)*beta_i^2)).
```

The pipeline rejects a profile if any displayed collision radius reaches `q`.
This only excludes the immediately trivial integer kernel vector `q*e_j`; it
does not prove MSIS hardness. Ranks remain uncertified choices. Fixed `q` and
the conservative growing caps limit the supported number of rounds; the
planner can reject even a recursion depth allowed by the configuration parser.

The final verifier checks the terminal witness against its exact target
relation and exact closed cap. Intermediate witnesses are not sent. Proof
bytes contain the source message when applicable, ordinary messages, and this
terminal opening; no general succinctness ratio follows from that format.

For the interactive protocol, statistical errors depend on the modular-JL
theorem, scalar and ring aggregation, the challenge set, extraction loss, and
the number of complete attempts. Computational errors depend on the complete
binding reductions, their runtimes, and actual per-edge radii. See the
[conditional protocol](protocol-conditional.md),
[composition/extraction theorem](unknown-gap-extraction.md), and
[refined computational loss](refined-computational-loss.md).

The code's transcript and seed expansion are additional assumptions and proof
obligations: domain separation alone does not turn the interactive analysis
into ROM/QROM security. Neither the checked arithmetic premises, a successful
test suite, nor a returned `accepted` report establishes knowledge soundness
for this compiler. The implementation also transmits witness-dependent
projections and a terminal opening and makes no zero-knowledge claim.

## API and validation evidence

`prove_round` returns a `RoundMessage` and a `Reduction` containing the target
relation and its witness. `verify_round` returns only the reconstructed public
target. Both receive the caller's transcript state so consecutive rounds share
the same chronological context. `target_shape_and_bound` returns `(8,n',cap)`
without materializing matrices or the triangular pair list. It validates
checked dimensions, the profile, the JL premise, and structural working limits.
These limits are not a byte-accurate peak-memory forecast.

The module tests cover full and scalar constraints with nonzero constants,
off-diagonal input orientation, odd-length aligned splitting, explicit padding
pins, radix boundary values, modified public messages, early rejection of
unsupported dimensions, and a nonzero witness passed through two consecutive
ordinary reductions. In each successful round an independent verifier
transcript reconstructs exactly the prover's target. These are tests of the
implementation's algebra and behavior, not a cryptographic proof.

```text
cargo test -p leash --lib ordinary::tests --release
cargo clippy -p leash --all-targets -- -D warnings
```
