# Core aggregation fingerprints: independent mathematical review

Date: 2026-11-14. Verdict: **the proposed replacements are algebraically valid
under the chronology and fixed-candidate premises of the repaired ordinary
core**. They change the verifier law and statistical error. The existing scalar
and ring aggregation errors cannot be retained unchanged. No prover, extractor,
attack, or lattice solver was implemented for this review.

The reviewed proposal is a fresh random point in `GF(q^6)` after the projection
reply, followed by a fresh point in `R_q` after the six aggregate polynomial
replies. The final filtered folding challenges are unchanged. Relevant original
proof positions are `protocol_repair.md` Sections 5.2 and 5.4; computational
anchoring, gating, and composition are the separate reviewed arguments.

## 1. Scalar aggregation over a separate extension field

Let `M=|F'|+J` be the number of original scalar constraints plus projection rows,
with `J=1024`. At the point after the projection reply `p`, the fixed candidate
and anchor data determine a residual vector `e in F_q^M`. This includes, where
needed, the bilinear forms evaluated using the anchor's fixed Gram entries,
before those entries have been shown to be correct. The old argument uses the
fact that this vector is nonzero and fixed before the scalar challenges.

Choose a public irreducible degree-six polynomial `f` over `F_q`, independently
of the statement and transcript. In the specified polynomial basis of
`E=F_q[Z]/(f)`, draw a fresh uniform `t in E` and expand

```text
t^j = sum_(i=0)^5 R_(i,j)(t) Z^i,  j=0,...,M-1.
```

Use these six coordinate rows as the scalar aggregation coefficients. The
polynomial `P_e(Y)=sum_j e_j Y^j` is a nonzero polynomial over `E` whenever
`e!=0`; the embedding `F_q -> E` is injective. All six aggregate residuals vanish
exactly when `P_e(t)=0`. Therefore

```text
Pr[scalar cancellation] <= min(1,(M-1)/q^6).             (SCALAR)
```

The six rows are correlated and need not have full rank at every `t`. The root
bound covers that circumstance, zero, and proper-subfield points. Row
independence is not used. The field `E` is separate from
`R_q=F_q[X]/(X^64+1)`; six scalar coordinates are embedded into the usual
coefficient field `F_q` of the ordinary ring constraints. No identification of
the two algebras is made.

The prover still sends six `b''` polynomials. The verifier still checks all six
constant coefficients against the respective scalar combinations. These
messages are sent before the next ring challenge. A nonzero scalar residual
outside (SCALAR) therefore forces a nonzero ring residual, exactly as in the
original chronological argument.

For general parameters, the condition to retain a target scalar error
`2^-lambda` is `q^m >= (M-1)2^lambda`, not merely `q^m >= 2^lambda`.
Degree six happens to suffice for the current `q,M,lambda=160`.

## 2. Ring aggregation through the two CRT factors

Let `K=|F|`. After the six `b''` replies, the relevant residual vector
`(v_0,...,v_(K+5))` in `R_q^(K+6)` is fixed. Draw an independent fresh uniform
`rho in R_q` and form `sum_j rho^j v_j`.

If this vector is nonzero, it has a nonzero image in at least one of the two
degree-32 CRT fields. In that field the corresponding formal polynomial in the
variable `Y` is nonzero and has degree at most `K+5`. A uniform `rho` induces
a uniform coordinate in that CRT field, so

```text
Pr[ring cancellation] <= min(1,(K+5)/q^32).              (RING)
```

Neither a nonzero residual nor the fresh ring point needs to be a unit. One
CRT field suffices for the bound. Choosing one field with a nonzero coefficient
is an analysis choice fixed before `rho`; it need not be sampled or computed
by a reduction. The exponent starts at zero, so `rho^0=1` also at `rho=0`.

For this modulus, `q` has multiplicative order 32 modulo 128. Hence the
cyclotomic polynomial `X^64+1=Phi_128(X)` has exactly two irreducible degree-32
factors over `F_q`, as required by the original core. The separate degree-six
field is not used for this ring aggregation.

## 3. What survives and what changes in extraction

In each complete collision experiment, use the new fresh point distributions
consistently for the anchor and every fresh upper-prefix invocation. At an
anchored candidate, `p` precedes the scalar point and `b''` precedes the ring
point. Conditioning on the data before the respective point therefore gives
(SCALAR) and (RING). The proof must not condition on acceptance and then assert
uniformity, or reuse an old advantage whose sampler had a different law.

The modal `h` selector is still fixed before all final folding challenges.
Those challenges retain their original independent uniform filtered law. The
univariate/two-variable root arguments in final `c`, the selected-coordinate
factor, fresh-kernel requirements, gate calculation, and bad-mass-weighted
collision inequalities do not require independent scalar/ring coefficient rows.
Their only affected statistical inputs are the two cancellation bounds above.

Thus the corresponding per-layer statistical quantity is

```text
kappa_new = delta_JL + (M-1)/q^6 + (K+5)/q^32 + 2/N,
```

and the gate's additional `r/N` remains. Safe caps at one can be used for general
sizes. No other statistical term is silently removed. The existing computational
loss expression uses the new complete experiments' advantages and unchanged
norm formulas, with their updated full runtimes.

The source statement coefficients, six `b''` messages, `z`, and packed
commitment/Gram data have the same dimensions. The next relation still consists
of the same ordinary verification equations, so the existing honest norm caps,
decomposition lengths, aligned packing, and chosen path remain applicable.
Their actual coefficients change and must be regenerated. The argument is not
permission to reuse or edit an old transcript. Deterministic digit caps remain
valid for arbitrary residues; they do not depend on the old aggregation law.

Call-count multipliers of the reviewed recursive extractor are unchanged.
Generating and using the power coefficients changes local work `tau_i` and the
complete sampler runtimes; those costs must be reaccounted. Polynomial-time
field arithmetic supports the asymptotic argument. It does not itself certify
any concrete advantage or performance improvement.

## 4. Current exact parameters

At source rank 6 and outer ranks 9, the first ring count is `K=102`, and each of
the remaining six layers has `K=45`. Their ring degree bounds sum to
`107+6*50=407`.

The independent-row native source has first `|F'|=2^27+166`; its seven scalar
degree bounds sum to `134225055`. With the degree-187 binary-source fingerprint,
the first scalar count is `2^27+193`, so

```text
M_first=134218945,
sum_(seven layers)(M_i-1)=134225082.
```

All later `M_i=1024`. Adding more exact public-coordinate pins changes this
scalar degree sum and must be included, even though it does not change the six
aggregate outputs or the witness length.

One core layer sends a 192-bit canonical encoding of its `GF(q^6)` point and a
2048-bit canonical encoding of its `R_q` point. Seven layers therefore use
15680 raw bits for these two aggregation challenges. Under the fingerprint
source and fixed two-bit JL encoding, the complete source-plus-core verifier
raw count becomes

```text
580126375936 JL bits + 15680 aggregation bits
 + 35328 final-fold bits + 187 binary-source bits
 = 580126427131 bits.
```

This is still dominated by fresh dense JL matrices. The replacement does not
change that challenge family or its cost. It does not establish a succinct
verifier, short total interactive transcript, Fiat--Shamir theorem, or SNARK.

## 5. Explicit extension-field certificate and independent checks

Sage 10.9 constructs the public field using

```text
q=4294967197,
f(Z)=Z^6+Z+2.
```

The irreducibility certificate is

```text
Z^(q^6)=Z mod f,
gcd(Z^(q^2)-Z,f)=1,
gcd(Z^(q^3)-Z,f)=1.
```

The degree-six Frobenius identity makes `f` divide the square-free product of
all irreducibles whose degrees divide six. The two gcd conditions exclude
degrees 1,2,3, leaving degree six. The certificate therefore proves
irreducibility, not just a successful software construction.

`scripts/core_aggregation_field_certificate.py` performs only Sage public field
arithmetic and writes `work/core_aggregation_field_certificate.json`. The file
contains exact checkpoint residues and Bezout polynomials for both gcds.
`scripts/core_aggregation_fingerprint_peer_checks.py` independently verifies
them using schoolbook polynomial arithmetic in standard Python, including both
Bezout equalities, the final Frobenius remainder, primality by trial division,
and the order of `q` modulo 128.

Its additional finite checks cover 720 scalar coordinate evaluations over
`F_9` and 17415 ring evaluations over `F_3[X]/(X^4+1)`, explicitly including
zero-divisor residuals. The latter reaches 18 roots among 81 points at degree
two, consistent with the bound `2/9` from one degree-two CRT field. All checks
passed; results are in `work/core_aggregation_fingerprint_peer_checks.json`.
These support the arithmetic certificates. The general cancellation bounds are
the proofs in Sections 1 and 2.

Archived original result files are in [parameter-results](parameter-results); `work/` paths describe ignored rerun outputs. Historical source hashes identify the original reviewed bytes.
