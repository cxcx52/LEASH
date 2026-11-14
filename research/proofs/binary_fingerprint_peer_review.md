# Independent review of the native binary fingerprint substitution

Date: 2026-11-14. Review completed: no blocking mathematical error found in
[binary_fingerprint_frontend.md](binary_fingerprint_frontend.md), subject to the
explicit native-interface and ordinary-core premises retained in that document.
This review concerns an interactive, single-source aggregation substitution. It
does not certify concrete cryptographic security, Fiat--Shamir, zero knowledge,
or total verifier efficiency.

Reviewed source SHA-256 values, before this review was written:

| File | SHA-256 |
|---|---|
| `binary_fingerprint_frontend.md` | `193a44a568a53377c62ed3bd64566b2f351eb5d786fa552193d5060d2a262fec` |
| `native_binary_source_interface.md` | `0a1142898fa9d24e6272eb32de7f3a9155aca306c741419511499587ab2f2196` |
| `../scripts/binary_fingerprint_checks.py` | `5fbd321feaed8c2ac70351a66cbb2693aea95ff63e9f9e7887d0bb0c7eab622e` |

Hashes record reviewed bytes, not a claim that future explanatory edits preserve
them. The independent checker is
[binary_fingerprint_peer_checks.py](../scripts/binary_fingerprint_peer_checks.py).
Its run output is `../work/binary_fingerprint_peer_checks.json`.

## 1. What is fixed, and when

The reviewed baseline is the coefficient-packed native binary interface, not
the older affine/parity interface with additional `d_i` witness blocks. There is
one source commitment to the original `(a,b,c,w)` blocks. The public relation,
matrix dimensions, constant-wire index, public coefficient pins, field basis,
and irreducible field polynomial are fixed before the source challenge. The
complete core target still contains the source commitment, signed conjugation
equalities, four bitness equations using `Jbar`, the product equation, public
coefficient pins, all padding-zero equations, and the norm cap.

For an original opening `v=(a,b,c,w)`, define

```text
e(v)=(a-Aw,b-Bw,c-Cw) in F_2^(3k).
```

If these deterministic equations hold and `w` is an invalid source witness,
then `e(v)` is nonzero: otherwise the established binary `a,b,c` equal the
three matrix products and the exact product check gives the source relation.
Public pins remain exact target equations; they are not omitted from the
relation or counted as part of this `3k` residual. An optional additional
`Hw=0` constraint must either remain exact with a justified encoding or add
its residual coordinates and update the fingerprint parameters. The reviewed
variant explicitly takes `h=0`.

The literal commitment need not have a unique opening. In the computational
proof, the analytical modal original opening is chosen at the saved prefix
following the commitment and before the realized field challenge. Its definition
may integrate over the distribution of all future field and core coins. This
does not make it a function of the realized challenge. No efficiently computable
mode or per-CRS uniqueness premise has been introduced.

## 2. Coordinate-row equivalence and integer lifting

Use different symbols for the basis variable `U` and the formal fingerprint
variable `Y`. For a public irreducible `f(U)` of degree `m`, put
`F=F_2[U]/(f)` and sample a uniform `t in F`. Define

```text
t^j=sum_i R_(i,j)(t) U^i,
P_e(Y)=sum_(j=0)^(L-1) e_j Y^j,   L=3k.
```

Linearity over `F_2` gives

```text
P_e(t)=sum_i (sum_j R_(i,j)(t)e_j) U^i.
```

The displayed basis is linearly independent, so all `m` coordinate parities
vanish exactly when `P_e(t)=0`. Independence between different rows of `R` is
unnecessary. They are usually strongly correlated.

Splitting row `i` into `alpha_i,beta_i,gamma_i`, compute

```text
delta_i=Lift(A^T alpha_i+B^T beta_i+C^T gamma_i mod 2).
G_i=<alpha_i,a>+<beta_i,b>+<gamma_i,c>-<delta_i,w>.
```

For binary original coefficients, `G_i` is an integer in `[-n,3k]`, and its
parity is precisely coordinate `i` of `P_e(t)`. The target proves `G_i=g_i mod q`;
both integers lie in this interval and its span `n+3k` is less than `q`.
Consequently `G_i=g_i` as integers. Checking the specified `g_i` to be even
therefore checks the intended parity. This argument survives the change from
160 independent rows to 187 correlated rows without any new witness coordinate.

Combining the contributions to `delta_i` in `F_2` before lifting is essential
to the stated interval. Reducing the formal polynomial `P_e(Y)` modulo `f(Y)`
before evaluation would be a different operation and is not part of the proof.
No homomorphism from the odd-characteristic core field to `F` is required.

## 3. Root bound, field certificate, and edge cases

An injective coefficient embedding sends every nonzero binary residual to a
nonzero polynomial over `F` of degree `D<=L-1`. Its number of distinct roots
in any field is at most `D`. Thus

```text
Pr_t[P_e(t)=0] <= min(1,(L-1)/2^m).
```

With `k=2^25`, `L=100663296`, and `m=187`, the untruncated bound is
`100663295/2^187 < 2^-160`, since `100663295 < 2^27`. At degree 186 this
same general bound exceeds `2^-160`. The paper correctly restricts this
minimality observation to that bound; it is not an optimality result for all
binary fingerprints.

All of the following cases are covered:

* `t=0` is sampled normally, with `t^0=1`; it is a root precisely when the
  constant coefficient is zero. There is no division by `t`.
* A nonzero constant has no roots. Leading zero coefficients lower the actual
  degree. The all-zero residual passes for every challenge, as completeness
  requires.
* Repeated roots count only once. Elements in proper subfields are already
  included in the root count and need not be rejected.
* The extension field modulus and the formal fingerprint polynomial have
  different roles. The latter may have degree much greater than 187.

For `f(U)=U^187+U^20+U^2+U+1`, the reviewed checker verifies the standard
irreducibility criterion: the 187th Frobenius remainder is `U`, while
`gcd(U^(2^17)-U,f)=gcd(U^(2^11)-U,f)=1`. Because `187=11*17`, these exclude
every proper divisor degree after the Frobenius identity ensures square-free
factorization into divisor degrees. Primitivity is not needed.

An independent Sage invocation also returned degree 187, `is_irreducible=True`,
and `is_squarefree=True` for this exact polynomial. The mathematical call was

```python
from sage.all import GF, PolynomialRing
R = PolynomialRing(GF(2), 'U')
U = R.gen()
f = U**187 + U**20 + U**2 + U + 1
assert f.is_irreducible() and f.is_squarefree()
```

Uniform sampling means 187 independent unbiased bits in the specified basis.
A 24-byte canonical representation has five fixed padding bits; it must not
silently change the distribution. No production random generator is supplied
or certified by either arithmetic checker.

## 4. The source binding loss really remains applicable

At one saved source prefix, let `p_v` be the unnormalized probability that a
fresh complete suffix returns a verified target with original opening `v`.
The suffix includes the fresh uniform field element and all fresh core-extractor
kernel coins. Put `a=sum_v p_v`, select a modal `v_*`, and write
`e_nm=a-p_(v_*)`. For two independent such suffixes, the probability of two
different verified original openings is

```text
c=a^2-sum_v p_v^2 >= e_nm^2.
```

Indeed `sum p_v^2 <= p_(v_*) a`, hence `c>=a e_nm>=e_nm^2`. Different binary
openings of the same source commitment supply a nonzero source kernel vector
with coefficient infinity norm at most 1 and squared Euclidean norm at most
`n+3k`. Averaging the complete collision experiment and using Cauchy--Schwarz
gives nonmodal accepted mass at most `sqrt(eta_src)`.

For each prefix whose fixed mode is invalid, any modal accepted branch belongs
to the root event for that single fixed residual. Its unconditional probability
at that prefix is at most `(L-1)/2^m`, independently of how the prover chooses
replies and whether the core kernel later succeeds. Integrating over prefixes
therefore gives the same upper bound; no conditioning on accepted challenges is
performed. Combining with the reviewed ordinary-core guarantee yields exactly

```text
Pr[valid source extraction]
 >= epsilon-kappa_core-nu_core-(L-1)/2^m-sqrt(eta_src).
```

This establishes compatibility with the existing reduction. It does not make
the source binding advantage negligible for free. Its actual two-suffix cost,
core-kernel costs, CRS embedding, and expected-time handling remain required.
For bounded complete restarts, use the earlier initialized-attempt/first-real-
acceptance theorem and sum these source errors; the old conservative `2^-160`
source summand stays valid. Uncharged adaptive source-challenge retries are not
part of this statement.

## 5. Independent checks and accounting

The peer checker uses explicit binary coefficient convolution followed by long
reduction, separately implemented from the original bit-serial multiplier.
Its completed checks were:

* 3,104 polynomial/evaluation pairs and 264 binary polynomials over the small
  fields of orders 4, 8, and 16: coordinate identity, actual-degree root bound,
  zero polynomial, and zero challenge.
* 16,384 complete small native instances, giving 49,152 scalar rows: every
  `n=2,k=1` binary matrix triple, every original binary opening, and every
  challenge in `F_8`. These verify the combined-before-lifting `delta`, the
  integer interval, the coordinate parity identity, and interval uniqueness
  modulo `q=17`.
* Exact rational parameter and encoding calculations, including the 186/187
  root-bound comparison and dense matrix size.

These are arithmetic checks, not a simulation of the cryptographic prover or
a proof of the general theorem. The theorem rests on the preceding algebra.

The independent accounting agrees with the main note. The new scalar replies
use `187*27=5049` bits; their difference from 4320 bits is 729 bits. Packing all
new replies as one byte string takes 632 bytes versus 540, a 92-byte difference.
Per-row byte rounding would be a different encoding. The 187-bit challenge
occupies 24 bytes after five padding bits. With the separately chosen rank-6
source commitment and the recorded core encoding, the ledger is

```text
1270976 + 1536*8 + 5049 = 1288313 bits,
ceil(1288313/8) = 161040 bytes = 157.265625 KiB.
```

This is one-attempt prover communication for the stated encoding. It excludes
public input/setup, verifier traffic, framing, prior rejected attempts, and
Fiat--Shamir material. The rank-6 source model screen is a separate conditional
cost-model result; this review does not convert it to a numerical MSIS advantage.

Materializing every coordinate row still takes `187*L=18824036352` bits,
or `561/256=2.19140625 GiB`. One straightforward streaming generation uses
`L-1` multiplications by `t`, each on 187-bit field elements. It avoids storing
the complete row matrix but does not make its construction, public matrix
combinations, or target coefficient processing free. The large core JL traffic
is unchanged. Only the source challenge wire has been compressed by this lemma.

## 6. Precise attribution and claim boundary

The probability argument is classical random-evaluation polynomial identity
testing. In the original paper, Schwartz's Lemma 1 and its one-variable base case
give exactly the degree-versus-number-of-roots reasoning used here; the paper
then describes testing by random evaluations. See
[Schwartz, JACM 27(4), 701--717 (1980)](https://doi.org/10.1145/322217.322225).
The primary-paper text at page 702 was checked in the indexed
[paper copy](https://pages.cs.wisc.edu/~cs787-1/Schwartz1980.pdf); the host's direct
PDF endpoint returned an error during this review, so the DOI is the stable
bibliographic reference.

Thaler's author-hosted
[Proofs, Arguments, and Zero-Knowledge](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf),
Sections 2.1 and 2.2, explicitly describes random-point Reed--Solomon fingerprints
and powers of one random field element for linear checks. Section 6.6.2 also
discusses fixing the witness before the random fingerprint challenge. These
sources support treating the method and its chronology as established ideas.

The present field is fixed and the evaluation point is random. A construction
that instead samples an irreducible modulus and computes a polynomial remainder
is a different family; the two should not be conflated merely because both are
called fingerprinting. This review establishes an application with explicit
native coefficient/parity constraints and parameter accounting. It makes no
claim that random-point fingerprinting, the root theorem, or commitment-before-
challenge chronology is new, and no claim that this application is the first
such use in lattice proof systems.

Archived original result files are in [../notes/parameter-results](../notes/parameter-results); the `work/` paths above describe ignored rerun outputs. Historical review hashes identify the original reviewed bytes.
