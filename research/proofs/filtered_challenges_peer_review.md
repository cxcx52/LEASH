# Independent review: filtered challenges and covariance

Date: 2026-11-14. Reviewed `proofs/certified_filtered_challenges.md`, its reference checker, and the covariance proposition supplied by the JL reviewer for `proofs/parameter_feasibility.md` (that latter file was not yet present when this review was written).

Update: the complete parameter document has now been reviewed, including both H=552 and H=640 profiles. See `proofs/parameter_feasibility_peer_review.md`. Its use of this covariance proposition, chronological hypotheses and norm accounting passed that separate review.

**Result:** no mathematical blocker found in the tail/cardinality construction, exact operator predicate, unit-difference conditions, or the stated covariance proposition. This review certifies those conditional statements, not an instantiated full protocol, original proof-size estimate or numerical MSIS security level.

## 1. Tail, strict boundaries and cardinality

The five-symbol scalar MGF proof is correct: the k=1 moment is exactly two and the even-moment comparison yields E exp(tX)<=exp(t^2). For every root and every direction the trigonometric squared-weight sum is exactly d/2, including d=2, so the one-sided projection bound is exp(-u^2/(2d)).

Using d/2 conjugate representatives and eight directions gives 4d events. Since cos^2(pi/8)>17/20, the closed event ||c||op>=T has probability at most 4d exp(-17T^2/(40d)). Consequently the deterministic acceptance predicate is the strict event ||c||op<T. No equality point is discarded or inadvertently accepted.

The bound e>163/60 has the correct direction for the integer certificate. Raising positive quantities to the integer denominator B=40d yields exactly CERT(u/v). Strict rejection probability below u/v gives cardinality strictly greater than (1-u/v)5^d, hence the inclusive integer lower bound floor((1-u/v)5^d)+1.

The d=64,T=31 checks, including rejection below 7/16 and cardinality at least 304931861011548122064596100244671106338500977, passed independently by running the reference script. Failure of its T=30 certificate is correctly not interpreted as a statement about the true T=30 acceptance probability.

## 2. Exact SPD selection and unit differences

The negacyclic multiplication matrix is a normal real matrix diagonalized by the unitary root-evaluation transform. Therefore T^2 I-A_c^T A_c is positive definite exactly when ||c||op<T.

The reference Bareiss algorithm implements Sylvester's criterion correctly. Before each division the earlier leading minors are positive; the current pivot is the next leading principal determinant. The row/column entries used by that step are not overwritten before their uses. A nonpositive pivot rejects, including a final zero determinant in an equality case. This is an exact polynomial-time integer predicate; it does not need an FFT tolerance.

For prime q>32 with q=5 mod8, the two factors X^(d/2)+s and X^(d/2)-s are irreducible, with the d=2 case linear. If a nonzero cube difference u+X^(d/2)v vanished modulo either factor, each integer u_j^2+v_j^2 would be divisible by q and at most 32, forcing every coefficient to vanish. Thus all distinct selected challenges have unit differences. The more general q>16d determinant argument is also valid under its explicitly stated two-equal-factor assumption.

## 3. Independent covariance proof

Let C be uniform on the selected cube. Its distribution is invariant under global negation, multiplication by X, and every automorphism sigma_a:X->X^a for odd a. These transformations are signed coefficient permutations. They preserve the cube; multiplication by X preserves operator norm because its root values have magnitude one, and sigma_a preserves operator norm because it permutes the roots. Thus E[C]=0.

Write Q=E[CC^T]. Signed shifts make all diagonal entries equal. For i!=j, shift the two coordinates so that one is zero; the covariance is, up to sign, Q_(0,delta) with 1<=delta<d. Write delta=2^e*t with t odd and put

    a=1+d/2^e.

Since e<log_2 d, a is odd and is a unit modulo 2d. Furthermore

    a*delta=delta+d*t=delta+d mod 2d.

The signed permutation sigma_a therefore fixes the constant coefficient and negates coefficient delta. Distributional invariance implies Q_(0,delta)=-Q_(0,delta), hence it is zero. This proves

    E[CC^T]=sigma^2 I_d.

This argument does not assert independent selected coefficients. That stronger assertion would be unjustified.

If the raw acceptance probability P_acc exceeds a_0>0, then

    d*sigma^2=E[||C||^2 | selected]
       <= E_raw[||C||^2]/P_acc =2d/P_acc <2d/a_0.

For independent selected challenges C_i and vectors s_i fixed before these challenges,

    E ||sum_i C_i*s_i||^2 = d*sigma^2 sum_i ||s_i||^2.

Here multiplication is negacyclic and the norm is over every ring coefficient. A coefficient vector with covariance sigma^2 I gives E||C*s||^2=sigma^2||A_s||_F^2=d*sigma^2||s||^2; independence and zero means cancel cross terms. The same argument applies conditionally on any preceding history that fixes the s_i and leaves the challenges independently sampled from this specified distribution. It does not cover s_i chosen adaptively after seeing these challenges.

With the d64,T31 certificate a_0=9/16 one gets sigma^2<32/9 and d*sigma^2<2048/9. The deterministic cap remains ||C||_2^2<=256. Replacing the latter by the former requires precisely the independence/chronology just stated.

## 4. Checks and scope

I ran `python scripts/certified_filtered_challenges_checks.py` successfully and added `scripts/filtered_covariance_peer_checks.py` as independent finite evidence. The latter verifies 502 basis-sign-flip constructions for degrees two through 256 and exact covariance matrices for five small filtered sets. In particular, d=4,T=4 retains 449 vectors and has covariance (738/449)I. All global-negation, signed-shift and odd-Galois images were checked to remain in each enumerated set.

These checks support the implementation and illustrative instances. The general covariance statement is established by the group-invariance proof above.

The remaining application obligations are honest-message chronology, updated norm/completeness accounting, any sampling-abort policy, recalculated MSIS bounds and full relation/recursion parameters. This review does not certify those steps before their complete statements are available.
