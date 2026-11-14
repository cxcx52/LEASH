# Native binary R1CS to the ordinary core: explicit interface

Date: 2026-11-14. Independent mathematical review of the local 34-page LaBRADOR
PDF, Section 6, PDF pages 22--24, compared with `r1cs_repair.md`,
`composition_repair.md`, and the current parameter ledgers. This document concerns
the coefficient-packed native binary reduction. It does not use the NAF/affine
reduction over `Z_(2^d+1)`, and does not change a package or parameter bundle.

**Conclusion.** The current first core shape can represent a corrected native
binary source relation without additional witness coordinates, provided the
constant coordinate was already counted in the source dimension. This requires
the block-aligned layout and complete target equations below. The earlier shape
and norm calculation alone did not supply this interface. The source contributes
one MSIS assumption and an explicit square-root collision loss, as well as source
messages and verifier challenges. Neither computational loss nor communication
is part of the reported core-only number.

## 1. Source statement and coefficient packing

Let `d>=2` be a power of two and `q` an odd prime. Write
`R_q=F_q[X]/(X^d+1)`, and use coefficientwise centered integer representatives for
all norms. The current instance uses `d=64` and `q=4294967197`.

The public binary relation consists of matrices `A,B,C in F_2^(k x n)`, a list
of public bit coordinates `P` and their values `x_j`, and optionally
`H in F_2^(h x n)`. A witness `w in F_2^n` must satisfy

```text
w_0=1,  w_j=x_j for j in P,
H w=0,
(A w) circle (B w)=C w.                              (SRC)
```

The constant coordinate is included in `n`. Public values and all matrices are
fixed as part of the statement before the source commitment or challenges. A
new constant coordinate cannot be added without updating `n` and its padding.
Rows of `H` may encode other public affine relations by using the existing
constant column. Ordinary public-coordinate pins are checked exactly in the
target and need not be added to `H`.

For a vector `u` of coefficient length divisible by `d`, `Pack(u)` groups every
`d` consecutive entries into one polynomial in increasing coefficient order.
Let `bar` denote the automorphism `X -> X^(-1)`. Its integer coefficient action
is

```text
bar(u_0,...,u_(d-1))=(u_0,-u_(d-1),...,-u_1).
```

It is a signed permutation, preserves the centered norm, and satisfies
`ct(Pack(u) bar(Pack(v)))=<u,v>` on each group. A native source coordinate is one
coefficient, not one ring element.

Consequently the correct target pin for `w_j=x_j` is the coefficient-selection
linear equation `coeff_j(w)=x_j` over `F_q`. The affine repair's whole-ring pin
`w_0_bold=1` must not be copied here: it would also pin the other `d-1` binary
coordinates packed into that polynomial to zero.

## 2. The all-coefficient-ones term

Let `J=1+X+...+X^(d-1)` and let `Jbar=bar(J)`. For a packed vector `u`,

```text
ct <u,bar(u)-Jbar_vector> = sum_j u_j(u_j-1),           (BIT)
```

where `Jbar_vector` has one copy per packed polynomial, and `u_j` on the right
means integer coefficients. The linear term can equivalently be written as
`ct <bar(J)_vector,u>`.

The printed Figure 4 uses a symbol `1` in this position. The intended coefficient
identity must be made explicit. If that symbol is interpreted as the scalar
ring element `1`, the identity is false: for `u=X`,
`ct(u(bar(u)-1))=1` although its coefficients are binary. This is a local
algebraic distinction, not a claim of a complete protocol attack. The corrected
interface always uses `Jbar`.

## 3. Protocol chronology and complete target

Assume first that `n,k` are divisible by `d`, and put `D=n+3k`.
The source CRS includes an independently uniform matrix

```text
K_src in R_q^(rho_src x (D/d)).
```

There is **one** source commitment. Its columns correspond only to the original
packed `a,b,c,w` coefficients, excluding conjugate copies and layout padding.

1. The honest prover forms `a=Lift(Aw mod 2)`, `b=Lift(Bw mod 2)`, and
   `c=Lift(Cw mod 2)`. It sends
   `t=K_src (Pack(a)||Pack(b)||Pack(c)||Pack(w))`.
2. After `t` and its prover state are fixed, the verifier sends independent
   uniform `alpha_i,beta_i,gamma_i in F_2^k`, and optionally
   `eta_i in F_2^h`, for `i=1,...,ell`.
3. Both sides calculate, **in F_2 before lifting**,

   ```text
   delta_i=Lift(A^T alpha_i+B^T beta_i+C^T gamma_i+H^T eta_i mod 2)
             in {0,1}^n.
   ```

4. The prover sends the integer

   ```text
   g_i=<alpha_i,a>+<beta_i,b>+<gamma_i,c>-<delta_i,w>.
   ```

   The verifier requires `-n <= g_i <= 3k` and `g_i` even, for every row.
   This is an integer/parity check with a specified representative, not parity
   of an arbitrary residue modulo an odd prime.
5. Invoke the ordinary core on the following exact target, with full witness
   `v=(a,b,c,w,bar(a),bar(b),bar(c),bar(w))` in the layout of Section 6.
   An honest target cap is `beta_h^2=2D`; the actual extracted cap is `beta_*`.

The target contains every item in this list:

* The source commitment equation `K_src(a||b||c||w)-t=0` over `R_q`.
* All coefficientwise equations identifying each conjugate block with the signed
  coefficient permutation of its original block.
* Four constant-term equations (BIT), for `a,b,c,w` separately.
* The constant-term product check, for `u=a+b-2c`,
  `ct <u,bar(a)+bar(b)-2bar(c)-Jbar_vector>=0`.
* Each public coefficient pin, including `w_0=1`.
* Each scalar linear equation over `F_q`
  `<alpha_i,a>+<beta_i,b>+<gamma_i,c>-<delta_i,w>-g_i=0`.
* All layout-padding zero equations specified below.
* The full coefficient norm bound `||v||<=beta_*`.

Scalar coefficient equations are supported by the principal relation: any
coefficient-linear functional is `ct <bar(Pack(coefficients)),v>` with its
constant term. Conjugation is not `R_q`-linear, so its equality is expanded into
coefficient-linear equations. All five quadratic checks fit the principal
dot-product form with the aligned layout below.

No `d_i` blocks occur. In particular `ell=160` introduces scalar replies and
target equations, but no witness coordinates. This differs from the affine
repair, whose witness length is `n+(3+ell)k` **ring** elements.

## 4. Deterministic semantic lemmas

Require

```text
beta_*^2 < q,   6k < q,   n+3k < q.                      (LIFT)
```

**Bitness.** Centered lifting commutes with conjugation, since `q` is odd and the
automorphism is a signed permutation. For each original block, every integer
`z` has `z(z-1)>=0` and `z(z-1)<=2z^2`. Therefore

```text
0 <= sum_j u_j(u_j-1) <= 2||u||^2
   = ||u||^2+||bar(u)||^2 <= beta_*^2 < q.
```

The constant-term equation makes this integer a multiple of `q`. It must be
zero, so every original coefficient belongs to `{0,1}`. This uses the zero-
congruence bound `<q`, not a centered-value recovery claim requiring `<q/2`.

**Products.** After bitness is established, each integer
`z=a_j+b_j-2c_j` lies in `{-2,-1,0,1,2}`. Its value `z(z-1)` is nonnegative
and at most 6. The product check and `6k<q` imply every such value is zero.
For three bits this is equivalent to `a_j b_j=c_j`. Padding coefficients vanish
and add zero to this calculation.

**Source scalar replies.** Given binary blocks, the actual integer expression
`G_i` in Step 4 lies in `[-n,3k]`. Both `G_i` and the transmitted `g_i` are in
that interval and are congruent modulo `q`. Its span is `n+3k<q`, so `G_i=g_i`.
The parity check implies

```text
<alpha_i,a-Aw>+<beta_i,b-Bw>+<gamma_i,c-Cw>+<eta_i,Hw>=0 in F_2.
```

The optional `H` terms do not enlarge the integer range: they were combined
inside the binary `delta_i` before lifting. Merely requiring `n+3k<q` would not
justify centered parity in general. The specified interval representative does.
In the concrete profile, the stronger condition `2 max(n,3k)<q` also holds, so
centered lifting is a valid implementation choice there.

One may encode the transmitted scalar as an integer index for the even numbers
in the interval. Alternatively, transmitting `u_i=g_i/2` requires explicitly
using `2u_i` in the target equation and enforcing its corresponding integer
range. No operation involving a modular inverse of 2 silently preserves parity.

## 5. One aggregation error, one source binding role

Fix the original opening `(a,b,c,w)` before the source challenges. All
deterministic target checks imply binary coefficients, correct products, and
public pins. If `w` nevertheless fails (SRC), the residual vector

```text
e=(a-Aw,b-Bw,c-Cw,Hw) in F_2^(3k+h)
```

is nonzero. Each independent source row annihilates this fixed vector with
probability exactly `1/2`. Hence all `ell` rows do so with probability `2^-ell`.
The index choices, matrices, and public pins were fixed before these rows. The
`g_i` values may depend on them: verified integer lifting already forces their
parities to the corresponding residual parities. This is one stage of linear
aggregation, so there is no second `2^-ell` union term. At `ell=160` its
statistical error is `2^-160`, not the affine repair's two-stage error.

Computational binding supplies the fixed-opening premise as follows. At the
saved prefix after `t`, run two independent complete suffixes, including fresh
source rows and independent fresh core-extractor kernels. Discard any output
that fails the complete target. If both return different original openings,
their difference is a nonzero `K_src` kernel vector. By the bitness lemma all
its coefficients are in `{-1,0,1}`, so

```text
||difference||_infinity <= 1,
||difference||_2^2 <= D.                                  (SRC-MSIS)
```

This is stronger than the generic `2 beta_*` Euclidean bound. Its column count
is `D/d`, not `2D/d`; conjugate copies are not committed. Denote this **complete,
unconditional** experiment's success probability by `eta_src`. It includes
initialization, the source prefix, both source suffixes, and both core kernels.
The relevant MSIS advantage has that matrix distribution, norm, and total
expected runtime. The source CRS and the core CRSs must be independently
uniform, or admit the claimed efficient joint embedding.

At each saved source prefix, let `p_v` be the accepted probability mass of a
verified target with original opening `v`; set `a=sum p_v` and fix a maximizing
opening using a deterministic tie rule. The accepted nonmodal mass is
`e=a-max p_v`. The two-suffix collision probability is
`c=a^2-sum p_v^2>=e^2`. Averaging gives nonmodal accepted mass at most
`sqrt(eta_src)`. The modal opening is fixed before the realized source rows,
even though its definition uses the distribution of future suffixes. It need
not be computed by an algorithm.

On modal accepted branches, the preceding fixed-opening argument bounds invalid
source output by `2^-ell`. Thus a bare source extractor that reads one verified
target witness, takes its `w` coefficients, and verifies (SRC) succeeds with
probability at least

```text
epsilon_virtual - 2^-ell - sqrt(eta_src).                  (SOURCE)
```

There is no information-theoretic uniqueness claim and no free source MSIS
assumption. The sqrt loss remains explicit.

## 6. Exact current layout and dimensions

For the current profile,

```text
n=k=2^25=33554432,  d=64,  ell=160,
D=n+3k=134217728,
one original block: 524288 ring elements,
source matrix: rho_src x 2097152 ring entries,
un-padded complete witness: 4194304 ring elements,
beta_h^2=2D=268435456=2^28,
beta_*^2=(16/3) 2^28=4294967296/3 < 4294967197.
```

Also `6k=201326592<q`, `n+3k=134217728<q`, and
`2 max(n,3k)=201326592<q`.

Use **eight separately aligned blocks**, one each for `a,b,c,w` and their
conjugates. Pad each block from 524288 to `14*37450=524300` ring elements, then
split it into 14 vectors of length 37450. Thus

```text
r=8*14=112,
n_core=37450,
r*n_core=4194400 ring elements,
padding=8*12=96 ring elements=6144 coefficients.
```

Each padding ring is required to be zero. Zero-padding all 96 rings only at the
end of an otherwise concatenated witness would not provide this particular
aligned quadratic representation. With the stated layout, for example,

```text
<a,bar(a)> = sum_(j=1)^14 <a_chunk_j,bar(a)_chunk_j>.
```

All five source quadratic tests become sums of permitted same-position dot
products. Linear rows, including commitments and scalar checks, use the
corresponding public coordinate selection/permutation maps. No new witness
coordinates beyond the existing 4194400 slots are needed.

One simple explicit target constraint ledger is:

```text
full-ring equations: rho_src source commitment rows + 96 padding-zero rows;
constant-term equations:
    D conjugation-coordinate rows
  + 4 bitness rows + 1 product row
  + ell scalar aggregation rows
  + 1 constant-wire pin + |P| other public-coordinate pins.
```

Here conjugation rows concern only real source coefficients; the 96 ring-zero
rows cover every padded coefficient. Replacing the 96 ring-zero equations by
6144 scalar equations is an alternative with the same semantics. Omitting them
or using a different implicit layout requires a new explicit argument. General
`H` contributes `ell*h` challenge bits and coefficient-formation work, but no
additional target rows beyond the existing `ell` scalar rows.

These large public equation counts matter to statement generation, verifier
work, and memory. The ordinary core's aggregation error can be independent of
the number of equations without its verifier computation becoming independent
of that number. Neither the shape nor this interface makes dense source matrix
products or the dense first JL projection succinct.

## 7. Composition and complete error accounting

Assume the ordinary core has the reviewed all-statements extractor for precisely
the target above, returns norm at most `beta_*`, and satisfies the fresh-kernel,
state-uniform expected runtime and polynomial product conditions of
`composition_repair.md`. Let its error be `kappa_core+nu_core`, where both terms
include every ordinary layer and each computational advantage has its actual
nested reduction cost and norm.

Replace the source reduction's final target witness with a fresh independent
core-extractor invocation. Any source early rejection forces failure. On the
ordinary source-prefix distribution, this virtual bare prover accepts with
probability at least `epsilon_total-kappa_core-nu_core`. The modal proof above
allows randomized final output: its new kernel coins are included in each
suffix mass and are resampled independently for each fork. It gives

```text
Pr[valid binary source witness]
 >= epsilon_total-kappa_core-2^-ell-nu_core-sqrt(eta_src).   (COMPOSED)
```

Expected extraction cost is one source-prefix execution plus one core-extractor
bound and source decoding/verification. The source collision experiment costs
one saved source prefix and two independent complete suffixes, each including
a fresh core extractor. Those costs, including matrix and challenge processing,
belong in `eta_src`. The reviewed expected-time to strict-PPT truncation argument
is still required if the assumed MSIS theorem only quantifies over strict PPT.

For bounded complete ordinary protocol restarts, the real acceptance gate must
include this source stage and all core stages. The first-real-acceptance coupling
then gives the sum over restart initializers of

```text
kappa_core,j + 2^-ell + nu_core,j + sqrt(eta_src,j).
```

In particular, for seven core layers and `Q` attempts, a uniform statistical
budget is

```text
Q [sum_(i=1)^7 (delta_JL,i+q^(-m_i)+q^(-d/2)+(r_i+2)/N_i) + 2^-160].
```

The previously used `2^-160` source summand is therefore the correct statistical
summand for this native interface, but the additional source collision term
must remain in the computational budget. This statement does not replace the
required independently initialized runtime/advantage bounds by a per-CRS bound.

Honest source checks pass deterministically, and its witness norm is at most
`2D`. Hence the source stage preserves the core's honest per-attempt acceptance
lower bound. The existing conditional restart completeness theorem applies to
the complete source-plus-core attempt when all of its premises are met.

## 8. Communication and scope of the current number

Source prover messages in one complete attempt are:

```text
source commitment: rho_src*d*ceil(log2 q) = 2048*rho_src bits;
source scalars: ell*ceil(log2(number of even integers in [-n,3k])).
```

For the current dimensions the number of permitted even integers is
`2^26+1`, so a canonical fixed-width scalar index needs 27 bits. The source
scalars use `160*27=4320` bits = 540 bytes. Encoding each as a 32-bit residue
instead uses 640 bytes and requires the explicit centered/interval check.

Thus the additional prover payload is `256*rho_src+540` bytes for the even-index
encoding, or `256*rho_src+640` bytes for residue encoding. The source rank must
be separately selected and assessed; it is not inherited from a core matrix
with different columns or norm. A 155.148... KiB **core-only** ledger is not the
complete source-plus-core prover payload until this addition and the exact
encoding convention are specified. Bounded restarts also require a separate
distinction between the accepted attempt's transcript and all communication
spent on earlier rejected attempts.

The uncompressed source verifier challenge is `ell*(3k+h)` independent bits.
For `h=0` the current value is 16106127360 bits = 1.875 GiB. This is separate
from prover proof-size ledgers and from the core verifier challenges. Replacing
these independent coins by seeds or a random oracle requires a separate model
and theorem. No such replacement is established here.

Established here: a specified non-vacuous native binary source relation, complete
target equations, exact chronology, coefficient/parity lifting, aligned current
shape, source MSIS role and loss, and a conditional source-plus-core theorem.
Remaining external obligations: choose and assess the source rank at its actual
MSIS norm and full reduction runtime; generate the exact target coefficients and
new setup for this interface; include all source messages in the intended size
ledger; retain the core's own unresolved concrete advantage bounds. This proof
does not establish Fiat--Shamir security, zero knowledge, a concrete numerical
security level, or a performance advantage.

## 9. Offline checks

`python scripts/native_binary_source_checks.py` writes the exact results to
`work/native_binary_source_checks.json`. It verifies 650 integer conjugation and
bitness identities, 254 short integer-vector implications, 32768 small `F_2`
aggregation-row cases including optional `H`, and 256 small aligned layouts.
It also checks all current integer dimension, norm, range, collision-radius and
message-width calculations. These are local arithmetic checks, not executions
of a cryptographic prover or extractor. The general guarantees come from the
lemmas above.

Archived original result files are in [../notes/parameter-results](../notes/parameter-results); the `work/` paths above describe ignored rerun outputs. Historical review hashes identify the original reviewed bytes.
