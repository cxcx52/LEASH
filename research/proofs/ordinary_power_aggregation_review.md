# Review of power-based aggregation in the ordinary core

Date: 2026-11-14. Scope: a separately specified ordinary-core variant. This
review changes only two verifier challenge distributions and their statistical
error bounds. It does not modify the old independent-row baseline or claim
Fiat–Shamir, computational-security, or implementation certification.

**Verdict:** the replacement is compatible with the reviewed ordinary
extraction and composition arguments. The original independence of scalar
aggregation rows, and of the ring aggregation coefficients, is used to bound
their respective residual-annihilation events. The power constructions below
supply replacement bounds. All required chronology must be preserved, and
every computational advantage must refer to the new complete sampler law.

## 1. Scalar aggregation over an extension field

Let the coefficient field be F_q, let `m>=1`, and let E=F_(q^m) with a fixed
public F_q basis. At the point where the original verifier would draw m
independent scalar aggregation rows, sample one fresh uniform `zeta in E`.
For the M ordered scalar residuals, let the coefficient of residual j in
row i be coordinate i of `zeta^j`, for `j=0,...,M-1`.

If the residual vector `e in F_q^M` is nonzero and fixed before zeta, its
polynomial

    P_e(Z)=sum_(j=0)^(M-1) e_j Z^j

is a nonzero polynomial over E of degree at most M-1. All m aggregated
scalar residuals vanish exactly when `P_e(zeta)=0`. Consequently

    Pr[all aggregated scalar residuals vanish]
      <= min(1,(M-1)/q^m).                         (SCALAR)

This is the ordinary univariate field root bound, not a claim that the
resulting rows are independent. Their dependence is intentional. The basis
must be fixed independently of the fresh sample; its precise choice does not
affect the proof.

For the current core, `m=6` and `M=|F'|+1024`. The ordered residual vector
contains the input constant-term equations followed by the 1024 projection
equations. The six public response polynomials `b''` remain six polynomials.
The verifier's constant-term checks and the prover's aggregate calculations
use the new row coefficients in precisely the same algebraic positions.

The source-independent residual is fixed after the projection response p
and **before** zeta. Although p may depend on the preceding projection, and
`b''` may depend on zeta, the constant-term identity forces the selected
aggregate residuals to be these field-coordinate sums. A dishonest choice of
the higher coefficients of `b''` cannot change their constant terms. Thus if
the scalar root event does not occur, at least one resulting full-ring
residual remains nonzero for the next stage.

For `q=4294967197`, the field may be represented by

    E=F_q[U]/(U^6+U+2).

The independent certificate at `work/core_aggregation_field_certificate.json`
contains the q^2/q^3 Frobenius/Bezout data and the q^6 remainder. It was
generated with Sage and independently verified using standard Python by
`scripts/core_aggregation_fingerprint_peer_checks.py`; see
`notes/core_aggregation_fingerprint_peer.md`. These data establish
irreducibility for the concrete field. Six uniform F_q coefficients specify
zeta, requiring 192 transmitted bits under the 32-bit residue encoding.

## 2. Full-ring aggregation

Assume the existing factorization

    R_q = F_q[X]/(X^d+1) is isomorphic to
          F_(q^(d/2)) x F_(q^(d/2)).

After all K input full-ring equations and the m scalar-derived ring equations
are fixed, sample fresh uniform `rho in R_q`. Weight their ordered residuals
`v_0,...,v_(K+m-1)` by `1,rho,...,rho^(K+m-1)`.

If v is nonzero, at least one CRT component of its coefficient polynomial is
nonzero. Select such a component as a deterministic analysis function of v,
before rho is sampled. Its degree is at most `K+m-1`, and the corresponding
component of uniform rho is uniform in F_(q^(d/2)). Hence

    Pr[sum_j rho^j v_j=0 in R_q]
      <= min(1,(K+m-1)/q^(d/2)).                    (RING)

There is no factor two: it suffices to require vanishing in one fixed
nonzero component. The polynomial may have zero-divisor coefficients in
R_q; the argument does not apply a field root theorem directly to that ring.
It first passes to the selected field component.

The fresh ring challenge is sampled **after** all `b''` replies. Its 64
uniform F_q coefficients cost 2048 transmitted bits. The final independent
fold challenges `c_i` and their filtered challenge set are unchanged.

## 3. Check against the existing extraction proof

I checked `protocol_repair.md`, `computational_binding_review.md`,
`composition_repair.md`, and `computational_loss_refinement.md` against these
changes. The following requirements remain in force:

- The candidate/anchor is fixed before its fresh JL test. The JL matrix still
  has the proved independent ternary distribution.
- The projection response and source residual vector precede zeta; the
  scalar-derived ring residuals and `b''` precede rho.
- The modal h selector is fixed before every final c challenge. Its prefix
  may contain the new zeta and rho, with no need for their coordinates or
  powers to be independent.
- Each weak or Gram collision slice still varies independent uniform final
  c challenges with fresh final-reply kernel coins. Its saved denominator
  and norm argument are unchanged.
- The initial ordinary acceptance gate, abort coin, and original saved-gate
  coupling remain those of the reviewed extraction algorithm.

The norm/equation branch now uses (SCALAR) and (RING) at exactly the old two
annihilation steps. The ensuing h-root event still has bound `2/N`; the
extraction gate still adds `r/N`. Thus the replacement single-layer
statistical quantity is

    kappa_main = delta_JL + (M-1)/q^m
                 + (K+m-1)/q^(d/2) + (r+2)/N,      (POWER-MAIN)

with each probability term capped at one if necessary outside the concrete
regime. The stated profiles lie far inside the uncapped regime.

The canonical mass and weighted Cauchy–Schwarz arguments apply to arbitrary
fresh-prefix distributions, so they retain the reviewed cubic-root form.
The eta quantities must be **redefined as the success probabilities of the
complete collision experiments for this new protocol**. Old numeric or
symbolic advantages cannot silently be reused as the same probabilities.
The matrix dimensions, collision radii, and independent uniform CRS roles
are unchanged, but runtime must charge generating powers and processing
their coefficients.

Honest digit and witness caps are deterministic in the coefficient bounds
and original witness/fold bounds. They do not require independent aggregate
coefficients. Filtered final challenges are unchanged and independent of the
earlier fixed witness. Thus the reviewed per-layer honest rejection bounds,
recursive caps, paired padding, complete prover payload, and invocation
factors remain valid. Local work may change substantially; this review does
not assert faster evaluation or an unchanged numeric runtime.

Composition and bounded complete restarts use (POWER-MAIN) and the new
initialized computational losses. No per-CRS or per-prefix binding bound is
inferred. The expected-time-to-strict-PPT truncation obligation remains.

## 4. Exact current statistical and communication budgets

Use the energy-ball path with inner rank 24, outer ranks 9, source rank 6,
q as above, d=64, m=6, and seven multiplicities
`112,33,15,8,7,5,4`. Let

    N_min=13936729633962967329980914140531014408519511.

With no general H rows and no public-coordinate pins beyond the constant,
the native independent-160 source gives

    M_1=134218918,  M_2=...=M_7=1024,
    sum_i(M_i-1)=134225055.

For the separately reviewed 187-row binary-fingerprint source, `M_1` increases
by 27 and the degree sum becomes 134225082. The source error becomes
`(3*2^25-1)/2^187 < 2^-160`. This source change is optional and distinct from
the core aggregation change.

The full-ring counts in both cases are `K_1=102`, `K_2=...=K_7=45`, giving

    sum_i(K_i+5)=107+6*50=407.

For Q=128 full attempts the exact rational upper bound checked by the script
is

    128 [198/N_min + 7/2^164
         + scalar_degree_sum/q^6 + 407/q^32 + source_error].

Both versions are strictly below `2^-128`:

| Source variant | Approximate negative log2 of the exact bound |
|---|---:|
| Native independent 160 rows | 128.69244341891655 |
| Native field fingerprint, 187 rows | 128.69244343628700 |

The decimal values are descriptive; the pass/fail inequalities use integers
and `Fraction`. The strictly bounded JL term makes the actual statistical
error strictly smaller than its displayed upper allowance. Computational
losses have not been absorbed into this statistical calculation.

Each layer now transmits 24 bytes for zeta and 256 bytes for rho, or **1960
bytes for both aggregation stages across seven layers**. The six `b''`
responses per layer, all source/core witness coordinates, and prover payload
remain unchanged by the core modification. The independent source-160 and
fingerprint-source-187 alternatives keep their separately stated prover
payloads from `notes/binary_frontend_audit.md`.

The seven JL matrices still take 580126375936 bits under the two-bit encoding;
the fold challenges take 35328 bits. Therefore the new explicit core verifier
ledger is

    580126375936 + 35328 + 15680 = 580126426944 bits.

With the native independent source challenges the total is
596232554304 bits, approximately 69.410604693 GiB. With the 187-bit source
fingerprint it is 580126427131 raw bits, approximately 67.535604715 GiB.
These exclude setup/public inputs/framing and rejected attempts. Byte framing
of the 187-bit source challenge adds five bits. The dense JL challenge law
has not been compressed by this change.

## 5. Independent checks and evidence boundary

`scripts/ordinary_power_aggregation_checks.py` performs 358 nonzero polynomial
checks over `F_9=F_3[X]/(X^2+1)`. It verifies both the root bound and the
equivalence between vanishing of the field value and of its two coordinate
aggregate rows. It also checks 16,272 nonzero polynomial cases over
`F_5 x F_5`, including zero-divisor coefficient cases, against the selected
CRT-component bound. These are finite probability checks, not protocol
transcripts or attacks.

The same script reads the saved source/core ledgers and checks the current
two complete statistical budgets and message counts exactly. Output is
`work/ordinary_power_aggregation_checks.json`. The field construction and
further independent tests are in the separate R1CS peer evidence named
above. All completed checks pass.

The result is a valid separately specified aggregation variant with a
controlled statistical trade-off. It neither contradicts the entropy of
the old independent challenge distribution nor makes its new correlated
coefficients independent. It does not settle dense-JL cost, practical
runtime, end-to-end concrete MSIS security, or a noninteractive theorem.

Archived original result files are in [../notes/parameter-results](../notes/parameter-results); `work/` paths describe ignored rerun outputs. Historical source hashes identify the original reviewed bytes.
