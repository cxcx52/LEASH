# A short random challenge for the native binary frontend

Date: 2026-11-14. This is an application of classical random-evaluation
fingerprinting to the repaired native binary interface. It is not a new
fingerprinting method, a Fiat--Shamir theorem, or a succinct-verifier result.
The source relation and all deterministic target equations are those of
[native_binary_source_interface.md](native_binary_source_interface.md).

## 1. The substitution and its chronology

Let the native source residual be

    e=(a-Aw,b-Bw,c-Cw) in F_2^L,  L=3k.

The source dimension includes the constant wire. Public-coordinate pins and all
bitness, product, conjugation, and layout constraints are enforced exactly as
in the native interface. Here h=0: additional public binary equations can either
be separately justified or included as residual coordinates, in which case L
and the field degree must be recalculated. They are not silently discarded.

Fix an irreducible polynomial f(Z) over F_2 of degree m and let
F=F_2[Z]/(f), with its specified polynomial basis 1,Z,...,Z^(m-1).
This public polynomial is fixed independently of the instance and commitment.
After the source commitment t_src is fixed, the verifier samples a fresh uniform
t in F and sends its m coefficient bits. For j=0,...,L-1 write

    t^j=sum_(i=0)^(m-1) R_(i,j)(t) Z^i,   R_(i,j)(t) in F_2.

Each row R_i is split into alpha_i,beta_i,gamma_i of length k. Both parties
form delta_i=Lift(A^T alpha_i+B^T beta_i+C^T gamma_i mod 2) in {0,1}^n.
For all i=0,...,m-1 the prover supplies the same native integer expression

    g_i=<alpha_i,a>+<beta_i,b>+<gamma_i,c>-<delta_i,w>.

The verifier checks g_i in [-n,3k] and even, then invokes the ordinary core on
the complete native target with these m scalar equations in place of the old
ell equations. All rows and target coefficients are fixed before the core
randomness. The rows are correlated; the proof below does not assert independent
row errors. There are no extra source witness coordinates or source commitments.

Do not replace these integer replies by only a field-valued parity assertion:
the core proves equations modulo the odd prime q, so the native interval lifting
is still needed to recover integer parity. Likewise, no homomorphism from F_q
to F is asserted. The field is used only to generate public binary coefficients.

## 2. Fixed-opening soundness

For a fixed residual e define the formal polynomial

    P_e(Y)=sum_(j=0)^(L-1) e_j Y^j in F[Y].

The embedding F_2 into F is injective. Thus e!=0 implies P_e is a nonzero
formal polynomial of degree at most L-1. It has at most L-1 roots in F.
In coordinates, P_e(t)=0 is equivalent to all m scalar parity equations
R_i(t) dot e=0. The native bitness, product, coefficient pins and interval
lifting show that every accepted invalid source witness entails this event.
Consequently, if the original opening is fixed before t,

    Pr[accepted target and invalid source] <= min(1,(L-1)/2^m).       (FP)

This covers t=0, including the convention t^0=1, and elements lying in proper
subfields. Excluding them is unnecessary and would require changing the sampling
law. If L=1, a nonzero constant has no roots and the error is zero. If L-1
approaches the field size, (FP) becomes weak; one cannot infer a small error
merely because the challenge has many bits.

For n=k=2^25, choose m=187. Then

    L=100663296,
    (L-1)/2^187 = 100663295/2^187 < 2^-160.

Degree 186 would not certify this target error using the same general root
bound. This is a minimum for this bound, not an optimality theorem over binary
fingerprints or all possible challenge distributions.

## 3. Binding and composition

The one-source canonical-opening proof is unchanged except for its final
fixed-opening error. At the prefix following t_src, fix the modal original
opening of the distribution of verified core-extractor outputs. The mode is
an analysis object fixed before the realized field element t. It need not be
efficiently computable. Two independent suffixes use independent uniform field
elements and fresh core-extraction kernels. If their verified original openings
differ, their difference is a source MSIS solution of coefficient infinity norm
at most 1 and squared Euclidean norm at most n+3k, by the native bitness lemma.

For this complete collision experiment's advantage eta_src, nonmodal accepted
mass is at most sqrt(eta_src). The proof uses the distribution of a suffix as
a whole, not independence of its binary rows. Therefore a single complete
source-plus-core attempt has extraction guarantee

    success >= epsilon - kappa_core - (L-1)/2^m
                         - nu_core - sqrt(eta_src).                 (COMP)

Every computational advantage includes the actual reduction runtime, including
coefficient generation and two fresh core kernels. For Q bounded complete
attempts, use the previously proved first-acceptance coupling and add the terms
for each initialized attempt. Since (L-1)/2^187<2^-160, the previous statistical
budget with a 2^-160 source summand remains a valid conservative upper bound.

Honest source checks always pass. The source witness, aligned packing, beta cap,
all ordinary-layer dimensions, and source collision norm remain unchanged. The
core's aggregation error depends on its own fresh q-valued random aggregation,
not the number of source scalar rows. Its work and input coefficient count do
change; they belong in the runtime budget. No numerical MSIS advantage is
deduced from this algebra or from a single cost-model exponent.

## 4. An explicit field certificate

One usable public polynomial is

    f(Z)=Z^187+Z^20+Z^2+Z+1.

Since 187=11*17, its irreducibility follows from

    Z^(2^187)=Z mod f,
    gcd(Z^(2^17)-Z,f)=1,
    gcd(Z^(2^11)-Z,f)=1.

The first condition makes f divide the square-free product of all irreducibles
whose degrees divide 187. The two gcd conditions exclude degrees 1,11,17,
leaving only degree 187. A degree-187 polynomial with those properties is
irreducible. The explicit residues and gcd results are emitted by
[binary_fingerprint_checks.py](../scripts/binary_fingerprint_checks.py).
No assumption that a merely chosen polynomial is irreducible is needed.

The checker also exhausts small fields, checking both the root bound and the
coordinate-row identity, including zero and repeated roots. These finite tests
support the implementation of the arithmetic; the general theorem is the
algebraic argument in Sections 2 and 3.

## 5. Communication versus computation

At the specified source dimensions, the change is:

| Source item | Independent binary rows | Polynomial fingerprint |
|---|---:|---:|
| Verifier random challenge | 16106127360 bits (1.875 GiB) | 187 bits (24 bytes with padding) |
| Scalar replies, 32-bit representation | 5120 bits (640 bytes) | 5984 bits (748 bytes) |
| Scalar replies, canonical even-integer index | 4320 bits (540 bytes) | 5049 bits (632 bytes with padding) |
| Scalar target equations | 160 | 187 |
| Extra witness coordinates | 0 | 0 |

The even-index encoding enumerates the 2^26+1 even integers in [-2^25,3*2^25],
using 27 bits per scalar and rejecting out-of-range indices. Packing all 187
indices uses 5049 bits, with seven final byte-padding bits. The public degree-187
polynomial and its encoding are setup conventions, not fresh challenge traffic.
The 24-byte field-element encoding has five fixed padding bits.

With the separately screened source rank 6, its commitment adds 1536 bytes to
both variants. Adding the fingerprint source messages to the recorded core
1270976-bit encoding gives 1288313 bits, or 161040 bytes after byte padding.
This is **157.265625 KiB of prover messages for one complete attempt**, before
framing, public statement/setup, verifier messages or Fiat--Shamir material.
It is a bound for an encoding, not a benchmark or a security certification.

The random-point family is information-theoretic. Expanding a computational PRG
seed into the old independent rows is a different construction and is not used.
However, expanding the new m-by-L coordinate matrix still creates 18824036352
bits (2.19140625 GiB); streaming can avoid storing the whole matrix but does not
erase its work. Generating t^j successively takes L-1 field multiplications in a
simple algorithm. Forming the field-valued matrix combinations can share work
across the m coordinates, but there is no measured speed claim here.

Only the source challenge has been compressed. The ordinary core still uses
large fresh JL matrices and random aggregation coefficients. This substitution
alone does not provide a short total interactive transcript, a sublinear
verifier, a new backend, zero knowledge, or a noninteractive proof.

## 6. Relation to known methods

Random evaluation of a nonzero low-degree polynomial is classical. Thaler's
[Proofs, Arguments, and Zero-Knowledge](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf),
Sections 2.1 and 2.2, presents Reed--Solomon fingerprinting and the use of powers
of one random field element in linear checks. This note adapts that familiar
device to the native binary coefficient/parity interface while preserving the
explicit binding chronology and integer lifting. No novelty claim is made for
fingerprinting itself. This is also distinct from choosing a random irreducible
modulus and reducing a polynomial modulo it.

Archived original result files are in [../notes/parameter-results](../notes/parameter-results); the `work/` paths above describe ignored rerun outputs. Historical review hashes identify the original reviewed bytes.
