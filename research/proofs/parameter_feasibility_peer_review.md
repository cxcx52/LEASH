# Independent review of the ordinary-core parameter certificate

Date: 2026-11-14. Reviewed `proofs/parameter_feasibility.md` and `scripts/parameter_feasibility_checks.py`, including the added H=640, f=1/16 profile. The script was rerun successfully; the independent output is saved as `notes/parameter-results/parameter_feasibility_peer_rerun.json`.

**Conclusion:** both displayed ordinary profiles satisfy the stated mathematical norm, lifting, pairing, strict-radius and statistical screens. I found no remaining blocker in those calculations after clarification of the binary scalar representative. This is not a certification of rank-16 MSIS hardness, concrete knowledge security, the optimized last round or Fiat--Shamir.

## 1. Honest covariance and acceptance

The signed-shift/Galois covariance proof is valid, as independently proved in `filtered_challenges_peer_review.md`. The s_i entering a fold are fixed before its fresh independent final challenges. Conditioning on preceding transcripts or earlier completed layers therefore leaves precisely the distribution needed for the second-moment calculation. Independence of the conditioned coefficients is neither true in general nor used.

The bound E||z||^2<(2/a)d*beta^2 and Markov at Gamma^2=2d*beta^2/(a*f) give fold rejection below f. Centering coefficientwise cannot enlarge the norm. Combining with JL by a union bound, rather than multiplying dependent events, is correct.

For H>512, Cantelli gives projection rejection at most 512/(512+(H-512)^2). The closed acceptance threshold and strict rejection event are handled correctly. At H=552, f=1/4 the joint lower bound is 67/132. At H=640, f=1/16 it is 479/528. The modulus condition simultaneously changes to 250*sqrt(H/120)*beta<=q; the script recomputes it at each level.

The seven-layer honest inputs after accepted preceding layers can be history-dependent. The layer bound is uniform over every fixed input within its cap, so conditional application proves the product bounds without assuming independence between layers. Exact arithmetic confirms (479/528)^7>1/2.

## 2. Packed norms and actual extraction caps

All three deterministic digit bounds have the correct direction:

- E_z follows from ||z_0||<=sqrt(nd)*b/2 and ||z_1||<=Gamma/b+sqrt(nd)/2.
- E_u counts the entire t,h upper-triangle coefficient population and bounds the final quotient rather than assuming it is a base-b digit.
- E_g uses ||g_ij||<=sqrt(d)||s_i||||s_j|| and sum_(i<=j)||g_ij||^2<=d*beta^4. It is conservative but valid for diagonal and off-diagonal terms.

The script's integer square-root ceilings preserve these upper bounds. It includes every z_0,z_1,t,g,h coordinate in beta_next. Zero padding does not increase the norm.

The first six target caps are B_i=ceil(s*beta_next), while the final explicit target cap is exactly beta_next. The collision bounds use these B_i, not honest beta_next. The Gram term uses a ceiling of s*beta at the source. Both H profiles correctly update s in all those places. There is no implicit product s^7 applied to the original source norm.

The strict q test is a necessary screen for the stated standard integer-MSIS definition. Passing it is not a security estimate. In the H=640 profile the largest screened radius is 2788653888, which is below q but still substantial; no hardness conclusion follows from this inequality or from rank 16 alone.

## 3. Same-partition packing

The code implements

    r_next=2*nu+mu,
    n_next=max(ceil(n/nu),ceil(M_aux/mu)).

It does not replace this by ceil(W_next/r_next). Matching splits of z_0 and z_1 preserve each original inner-product pairing; the paired blocks may be interleaved if a tridiagonal ordering is required. The auxiliary block is separately split and padded. The reported choices and all componentwise coverage assertions pass for both seven-layer schedules.

This is the crucial structural condition for applying the ordinary relation recursively. A dimension-only argument allowing arbitrary rearrangement would not suffice.

## 4. Binary and affine source conditions

For the binary shape n_src=k_src=2^25, beta^2=2*n_src+6*k_src=2^28 is correct for the original coefficient packing, counting each original and conjugated block. The shape's small dimension excess is padding. Both s^2=23/5 and s^2=16/3 satisfy s^2*beta^2<q. Once the conjugation constraints hold, this bounds each nonnegative integer binariness sum sum_j z_j(z_j-1) strictly below q, so its zero congruence implies integer zero. The conditions 6*k_src<q and n_src+3*k_src<q also hold.

I requested one clarification, now included: the binary scalar g_i represents an integer in [-n_src,3*k_src]. Its span being smaller than q permits an interval-based decoder, but does not by itself justify a centered parity test. This instance satisfies the stronger 2*max(n_src,3*k_src)<q, which the script now checks, so centered lifting is valid here.

Constant/public-input pins must be explicitly present in the source relation; the shape calculation cannot supply them. The document now says so. The source error and source computational-binding losses remain separate from core parameter feasibility.

The separate affine example satisfies M=n+(3+ell)k, beta^2=M*d/2, and the repaired strict q/2 lifting condition at the actual relaxed cap. Its squared comparison first checks that the residual right-hand side is positive, so squaring does not reverse or weaken the intended inequality. The exact smallest-divisor test and 2/274177^9<2^-160 check are valid. This example specifies a compatible shape; it does not claim satisfiability of every R1CS of that shape.

## 5. Payload accounting

The reported quantities are ordinary-core **prover payload upper bounds** for specified fixed-width encodings. I checked the inclusion of two outer commitments, 1024 JL coordinates, six aggregation polynomials per layer, and every final decomposition block. The signed coordinate widths and final high-digit bounds are conservative. No Gaussian entropy approximation is used.

The exact results are:

- H=552 profile: 1340224 bits = 167528 bytes = 163.6015625 KiB;
- H=640 profile: 1318016 bits = 164752 bytes = 160.890625 KiB.

These omit public setup/statement data, verifier messages, framing and Fiat--Shamir material, as stated. They do not include a separate source wrapper's messages, and are not end-to-end proof lengths for a complete source-to-SNARK construction. They cannot be compared as a security-matched benchmark with the original optimized 53.84 KB figure. When turning the encoding into a protocol, unused fixed-width codewords must be rejected and the decoding convention specified; this does not change the displayed honest upper bounds.

## 6. Statistical and computational ledgers

The exact inequality

    198/N_min + 7*2^-164 + 7/q^6 + 7/q^32 + 2^-160 < 2^-140

passes. The conservative T=31 cardinality bound is valid for T=34 because the filtered sets are nested. Changing H from 552 to 640 keeps the JL lower-tail statistical lemma unchanged when s^2=H/120 and the modulus condition are updated, as the code does.

The nested call-factor product lies strictly between 132779520 and 132779521. Its logarithm is a runtime multiplier, not an automatic bit-security subtraction. The document correctly retains the fourth-root binding loss: sqrt(r)*eta_y^(1/4)<=2^-128 would alone require eta_y<=2^-512/r^2. No numerical MSIS advantages at the actual reduction runtimes are supplied, and rank 16 remains a mathematical example.

The new high-completeness profile removes the old profile's approximately 115-attempt honest lower-bound cost. It does not remove computational concretization. Bounded, complete, first-acceptance restarts have a separate theorem in `bounded_restart_repair.md`; local challenge retries and Fiat--Shamir selection remain outside this review.

## 7. Final reviewed scope

The parameter certificate establishes simultaneous ordinary-core feasibility and a constant whole-attempt honest acceptance lower bound. It refutes an alleged impossibility based solely on the current norm/lifting inequalities. It does not prove a faster/smaller secure construction, an independently verified security level, or novelty of the arithmetic tools. Those limitations are preserved in the current document.
