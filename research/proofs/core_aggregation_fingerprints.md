# Information-theoretic compression of the ordinary aggregation challenges

Date: 2026-11-14. This applies classical polynomial fingerprinting to the repaired
ordinary core. The result concerns the two aggregation stages, not the JL
projection, CRS generation, zero knowledge or Fiat--Shamir. It is conditional
on the full extraction and composition interfaces already specified in this
workspace. All complete computational experiments must use the new law below.

## 1. Scalar aggregation

Let q be the current prime 4294967197. The ordinary core has M=|F'|+1024 scalar
residuals after the projection reply p, and sends six extended aggregate
polynomials b''. Fix the public field

    E=F_q[Z]/(Z^6+Z+2),

with its polynomial basis. The defining polynomial is irreducible, certified
by the Frobenius and Bezout identities described in Section 5 below.

Replace the six independently random scalar coefficient rows by the six
coordinate rows of powers of one fresh uniform t in E:

    t^j=sum_(i=0)^5 R_(i,j)(t) Z^i,  j=0,...,M-1.

Use these entries for the existing psi and omega coefficients in their fixed
public order. The prover still sends six b'' polynomials, and their constant
coefficients are checked against these six combinations. The point t is drawn
after p, and before any b''. This is a changed probability distribution, not
lossless compression of the old independent rows.

**Lemma 1.** For every fixed nonzero e in F_q^M, all six combinations vanish
with probability at most min(1,(M-1)/q^6).

Indeed, P(Y)=sum_j e_j Y^j is nonzero over E, because the base-field embedding
is injective. Its degree is at most M-1, and it has at most that many roots.
All coordinate combinations vanish precisely when P(t)=0. No independence
between the six rows, full-rank assertion at every point, or unit condition on
t is needed. The convention t^0=1 includes t=0.

The residual vector here is the same fixed residual used by the original
anchored proof. Before Gram correctness is proved it includes the bilinear
forms using the anchor's fixed Gram entries; it is not replaced prematurely
by a valid-witness residual. After conditioning on the data preceding t, the
root bound applies to that vector as well.

## 2. Ring aggregation

Let K=|F|. After all six b'' replies and their constant checks, replace the
K+6 independent ring coefficients by powers of one fresh uniform rho in R_q:

    F=sum_(j=0)^(K+5) rho^j v_j,

where the ordered v_j are the K original ring constraints and the six extended
scalar constraints. The point rho is independent of t and is drawn after b''.

**Lemma 2.** For a fixed nonzero residual vector v in R_q^(K+6), the probability
F=0 is at most min(1,(K+5)/q^32).

At q=4294967197 the order of q modulo 128 is 32, so X^64+1 has two irreducible
degree-32 factors. Choose a CRT component in which at least one v_j is nonzero,
before rho is realized. The image of F is a nonzero formal polynomial of degree
at most K+5 in that field. Uniform rho has a uniform image in it. The field
root bound proves the claim. Residuals and rho can be zero divisors; requiring
units is unnecessary. The second CRT component need not also be nonzero.

## 3. Extraction and norm preservation

In the ordinary extraction theorem replace the per-layer statistical term by

    delta_JL + min(1,(M-1)/q^6) + min(1,(K+5)/q^32) + (r+2)/N.   (STAT)

The final filtered challenge law is unchanged. The selected bad coordinate is
still fixed before all final challenges, and fresh final-reply kernels remain
independent between invocations. The gate adds the same r/N term as before.
The modal/collision inequalities, including the cubic-root refinement, continue
to hold for the new complete experiments. Their eta values and runtimes must
be defined for those experiments; old numerical advantages cannot be reused
merely because matrix dimensions are unchanged.

Proof: Lemmas 1 and 2 replace exactly the two cancellation events in the fixed
candidate argument. Their chronology leaves a nonzero ring residual outside
the scalar cancellation event, since the six constant coefficients have been
checked before rho. Other root arguments operate on the independent final
filtered challenges and are unchanged. Integrating over the pre-point data
gives unconditional event bounds. One must not first condition on acceptance
and then assume a uniform point. The reviewed independent audits check each
use of the old coefficient laws in the extraction proof.

The number and width of the six b'' messages do not change. Nor do the ring
dimension, packed witness dimensions, commitments, final folding distribution,
or collision norm formulas. The deterministic decomposition bounds hold for
arbitrary residues, so they do not require the old aggregation distribution.
All public coefficient functions and actual target equations must nevertheless
be regenerated. This construction does not edit an old transcript.

For general growing parameters choose an extension degree m satisfying
q^m >= (M-1)2^lambda if scalar error 2^-lambda is required. Keeping m fixed
while increasing M without revisiting (STAT) would invalidate the claimed
security-parameter family. Field arithmetic and power generation also enter
every local runtime and the complete nested reductions.

## 4. Concrete combined variant

Use the independently reviewed native binary frontend, the degree-187 source
fingerprint, source rank 6, the bounded-energy challenge family, inner rank 24,
outer ranks 9, and the saved seven-layer parameter path. The source dimensions
include the constant wire and have no additional public pins in this example.
Let N_min=13936729633962967329980914140531014408519511.

For the first layer M=134218945 and K=102. For each later layer M=1024 and K=45.
Thus the sums of scalar and ring polynomial degree bounds are respectively
134225082 and 407. The final folding terms sum to 198/N_min.
With Q=128 complete attempts, the exact statistical expression is

    128 [198/N_min + 7*2^-164
         + 134225082/q^6 + 407/q^32
         + 100663295/2^187] < 2^-128.                      (BUDGET)

The recorded decimal exponent is approximately 128.6924434363. This is a
statistical budget, not complete 128-bit knowledge security. Add the sum of
all core computational losses and sqrt(eta_src) over the properly initialized
attempts, at their complete runtimes. Honest source and aggregate equations
pass deterministically, so the existing per-attempt honest acceptance bound
greater than (479/528)^7>1/2 is preserved under the existing norm premises.
The bounded-complete-restart theorem then gives honest failure below 2^-128
and expected honest attempts below 2. It does not cover local or hidden retries.

The prover-message encoding remains 1288313 raw bits, or 161040 bytes when
rounded to bytes once: **157.265625 KiB for one complete attempt**, with source
and core included. Statement, setup, framing, verifier traffic, rejected
attempts and Fiat--Shamir material are separate.

The two aggregation challenges now use six base-field coordinates plus one
ring element per layer: 192+2048 bits. Across seven layers this is 15680 bits,
or 1960 bytes. The current explicit verifier ledger becomes

    JL:                       580126375936 bits
    two aggregations:               15680 bits
    final filtered challenges:      35328 bits
    binary-source fingerprint:        187 bits
    total:                    580126427131 bits.

This is about 67.5356047148 GiB, dominated by unchanged JL matrices encoded
with two bits per ternary entry. The two-bit figure is an encoding choice,
not an unconditional communication lower bound for all architectures. Under
fresh independent ternary entries and no pre-shared randomness, their entropy
is 1.5 bits per entry; changing that distribution requires a different JL
theorem. No claim of a succinct verifier or practical full interactive traffic
follows from compressing the aggregation challenges.

## 5. Reproduction and attribution

[ordinary_power_aggregation_checks.py](../scripts/ordinary_power_aggregation_checks.py)
checks the exact budget and communication ledger and exhausts small field and
two-factor ring examples, including zero divisors.
[core_aggregation_field_certificate.py](../scripts/core_aggregation_field_certificate.py)
constructs the degree-six field certificate with Sage. The saved identities are

    Z^(q^6)=Z mod f,
    gcd(Z^(q^2)-Z,f)=gcd(Z^(q^3)-Z,f)=1.

Frobenius and Bezout certificates are independently replayed with ordinary
Python by [core_aggregation_fingerprint_peer_checks.py](../scripts/core_aggregation_fingerprint_peer_checks.py).
The identities show that f is a product of distinct irreducibles with degrees
dividing 6, with degrees 1,2,3 excluded; degree 6 then implies irreducibility.
Finite examples do not replace the general field/CRT proofs above.

Independent reviews are [ordinary_power_aggregation_review.md](ordinary_power_aggregation_review.md)
and [core_aggregation_fingerprint_peer.md](../notes/core_aggregation_fingerprint_peer.md).
The underlying random-evaluation method is classical; see Thaler,
[Proofs, Arguments, and Zero-Knowledge](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf),
Sections 2.1 and 2.2. The contribution recorded here is its explicit integration
with this repaired scalar/ring interface, chronology, field certificates and
updated error ledger. It is not a priority claim for polynomial fingerprinting.

Archived original result files are in [../notes/parameter-results](../notes/parameter-results); `work/` paths describe ignored rerun outputs. Historical source hashes identify the original reviewed bytes.
