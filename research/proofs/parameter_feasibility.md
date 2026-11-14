# Parameter feasibility, complete honest norm caps, and remaining cost barriers

Date: 2026-11-14. Scope: the repaired **ordinary** LaBRADOR core, with all outer commitments retained, and the binary/affine source relations already repaired in this workspace. This is a mathematical parameter certificate. It is not a lattice hardness estimate, an implementation benchmark, or a Fiat--Shamir security claim.

The principal conclusion is positive but limited: the repaired norm, lifting, packing, and statistical conditions have a simultaneous seven-layer solution at degree 64 and a 32-bit prime. Thus these conditions do not establish an impossibility of the architecture. They also do not justify the original concrete security or proof-size claims. A conservative ordinary-core profile has a 163.60 KiB encoding bound and relatively smaller collision radii. A second profile below increases the JL threshold from 552 to 640 and certifies **whole seven-layer honest acceptance greater than 1/2**, at a 160.89 KiB encoding bound and larger collision radii. The extractor call multiplier is about 2^26.98446 in both cases. The hard remaining task is computational concretization at the enlarged MSIS radii and full reduction runtimes.

The reproducible arithmetic is in [parameter_feasibility_checks.py](../scripts/parameter_feasibility_checks.py); its output is [parameter_feasibility_checks.json](../notes/parameter-results/parameter_feasibility_checks.json). Every decisive inequality uses integers or rational numbers. Decimal logarithms and KiB values are presentation only.

## 1. Norm convention and the standard integer-MSIS barrier

LaBRADOR uses coefficient Euclidean norms in R=Z[X]/(X^d+1). In this report, standard integer-MSIS asks for an integer polynomial vector z in R^M with

    A z = 0 mod q,        0 < ||z|| <= L.

The output is an integer vector; it is not required to be nonzero in R_q^M. This is the distinction in Langlois--Stehle, *Worst-Case to Average-Case Reductions for Module Lattices*, Definition 3.5 (the local author version, PDF page 12). Their definition uses the canonical embedding norm. For this power-of-two cyclotomic ring, canonical Euclidean norm is sqrt(d) times coefficient Euclidean norm, so the numerical radius must be converted when citing that definition.

In coefficient norm, q e_j is always a nonzero integer kernel vector of norm q. Hence an assumed hardness statement for standard integer-MSIS at L>=q is vacuous. In the unnormalized canonical convention the corresponding threshold is q sqrt(d). This observation does **not** show that the variant requiring a nonzero residue vector is easy: q e_j is zero modulo q and is excluded by that different definition. The collision reductions here produce a nonzero residue, but if their stated assumption is standard integer-MSIS, the assumption still needs a nontrivial radius.

For the repaired ordinary core the radii are

    L_out = 2 B,
    L_weak = 8 T (b+1) B,
    L_Gram = 2(b+1) B + 4 T s beta,
    s^2 = 23/5.

Thus each of the three radii must be below q before a standard integer-MSIS hardness claim can even be considered. Increasing the commitment rank cannot cure a radius at or above q. Conversely, being below q is only a necessary screen; it gives no security level.

On a recursive edge the actual cap is B_i=s beta_(i+1), or a proved upper bound on that quantity; at the final explicit opening it is B_i=beta_(i+1). This is Remark 5.2 of the original paper and the relation-matching requirement in [composition_repair.md](composition_repair.md). A bound obtained for the honest beta_(i+1) cannot replace B_i in collision analysis. There is no automatic s^D multiplier on the original witness: the slack is accounted for in the actual target relation at each edge.

The JL condition is

    250 s beta <= q.

The Gram term alone requires 4 T s beta < q. Thus when T>62.5 it imposes a stronger restriction on beta than the JL condition. For T=34, the Gram contribution 4 T s beta is at most 136q/250 under JL, leaving a nonzero but parameter-dependent budget for 2(b+1)B.

## 2. Challenge choices and their cost

The original Section 2 does **not** use the full coefficient cube: it specifies a fixed type (23 zero, 31 unit-magnitude, and 10 magnitude-two coefficients), then filters at operator norm 15. Its reported mean of approximately six candidates is an experimental quantity. Our rigorous filtered-cube construction is a different choice. It trades a larger operator threshold for a certified large cardinality and an exact membership predicate; it should not be presented as an improvement over the original T=15.

For comparison, the full cube {-2,-1,0,1,2}^d has exact maximal operator norm

    T_cube = 2 csc(pi/(2d)).

Indeed, multiplication is diagonalized at the odd 2d-th roots. For any fixed root and phase, maximizing the projection over coefficient signs gives twice a sum of absolute cosines. The d roots modulo sign are equally spaced by pi/d; orienting them into one half-plane gives d consecutive points among the 2d-th roots. Their geometric sum has magnitude csc(pi/(2d)), so the projection is at most this value. Equality holds at the primitive root with all d coefficients equal to 2. At d=64 the result is approximately 81.49551, rather than the elementary bound 2d=128. The script also gives a rational upper bound using pi>157/50 and sin(x)>x-x^3/6.

The filtered set

    C_T = {c in {-2,-1,0,1,2}^d : ||c||_op < T}

retains zero. It uses the exact operator test and count certificate proved in [certified_filtered_challenges.md](certified_filtered_challenges.md). For q prime, q=5 mod 8 and q>32, distinct elements have invertible differences, as established there. For rational u/v in (0,1), the following integer inequality certifies rejection probability below u/v:

    (4 d v)^(40d) 60^(17T^2) < u^(40d) 163^(17T^2).

In particular, d=64,T=31 gives acceptance greater than 9/16. Hence

    |C_31| >= floor((9/16)5^64)+1
           = 304931861011548122064596100244671106338500977.

Increasing T improves acceptance and can reduce the honest fold cap enough to compensate for the larger T in the collision radius. Minimizing T alone is therefore the wrong optimization objective. Section 6 reports a joint grid search over T, its certified acceptance, and the decomposition parameters.

## 3. Conditional covariance: a rigorous honest fold bound

Let c be uniform in C_T and let a be a strict lower bound on its acceptance probability when sampling the full cube. Then

    E[c]=0,        E[c c^T]=sigma^2 I_d,        sigma^2 < 2/a.

No independence of the conditioned coefficients is asserted.

Proof. Global negation preserves C_T, so the mean is zero. Multiplication by X acts as a signed cyclic shift, preserving both coefficient support and operator norm. Consequently the covariance diagonal is constant, and every off-diagonal entry is, up to sign, E[c_0 c_delta] for 1<=delta<d. Write delta=2^e t with t odd. Since d is a power of two,

    k=1+d/2^e

is odd and X -> X^k is a Galois automorphism. It acts as a signed permutation of coefficients and permutes the evaluation roots, so it preserves C_T. It fixes the constant coefficient and maps the coefficient at delta to its negative, because k delta=delta+d t=delta+d mod 2d. Therefore E[c_0 c_delta]=0. This proves the scalar covariance claim. Finally the unconditioned cube has E||c||^2=2d, and restricting a nonnegative random variable to an event of probability greater than a gives E[||c||^2 | C_T]<2d/a. Taking the trace proves the last inequality. This argument was independently checked in [filtered_challenges_peer_review.md](filtered_challenges_peer_review.md).

For fixed polynomial vectors s_i with sum_i ||s_i||^2<=beta^2 and independent c_i uniform in C_T, put z=sum_i c_i s_i, using integer polynomial products before centering. Every column of the multiplication matrix of s has squared norm ||s||^2. Independence between different challenges and the zero mean therefore imply

    E||z||^2 = sigma^2 d sum_i ||s_i||^2 < (2/a)d beta^2.

For any desired fold rejection upper bound f in (0,1), choose

    Gamma^2 = 2d beta^2/(a f).

Markov gives Pr[||z||>Gamma]<f. Centering modulo q cannot increase the coefficient norm. For f=1/4 this becomes Gamma^2=8d beta^2/a.

The repaired 1024-row JL test with threshold 552 beta^2 accepts with probability at least 25/33. Therefore the two honest checks jointly pass with probability greater than

    25/33 - f.

At f=1/4 the lower bound is 67/132. No independence between the two check events is needed. This estimate holds for every fixed honest witness, including witnesses concentrated on one coordinate. For the simpler T=31,a=9/16 profile, alternatively taking Gamma^2=16d beta^2 gives fold rejection below 2/9 and joint acceptance greater than 53/99. The digit caps below apply to either choice.

If beta=0, all source vectors and z are zero and the projection/fold checks pass with probability one; the t and h digit bounds remain applicable. The strict-moment wording above is only needed when beta>0.

## 4. Complete deterministic target caps from the actual packed witness

The original Sections 5.2--5.4 and Figure 2 pack only the upper triangles of g and h. Write

    G = r(r+1)/2,
    D_z = nd,
    D_u = d(r kappa + G),
    D_g = dG.

D_u counts the underlying coefficients in t and h, whose centered residues are arbitrary modulo q. D_g counts the underlying coefficients of g. Let b>=2 be the two-part z base. Let a_1,a_2>=2 be the t/h and g bases, with digit counts t_1,t_2>=2.

For repeated centered division of an integer x into t digits of base a, the first t-1 digits have absolute value at most a/2. The final quotient satisfies

    |x_high| <= |x|/a^(t-1) + C(a,t),
    C(a,t) = a/(2(a-1)) (1-a^(-(t-1))).

This follows by summing the geometric series of carries. At even-base ties, fix any deterministic centered digit convention; the bounds are unchanged.

For the two-part folded vector z=z_0+b z_1, on ||z||<=Gamma,

    ||z_0||^2+||z_1||^2
      <= D_z b^2/4 + (Gamma/b + sqrt(D_z)/2)^2
      =: E_z.

For arbitrary centered t/h residues,

    E_u = D_u [(t_1-1)a_1^2/4
                  + (q/(2a_1^(t_1-1))+C(a_1,t_1))^2]

bounds all their decomposition digits together. This covers the final quotient without presuming it is uniformly distributed or itself a base-a_1 digit.

For g_ij=<s_i,s_j>, Young's inequality and Cauchy--Schwarz give

    ||g_ij|| <= sqrt(d) ||s_i|| ||s_j||,
    sum_(i<=j) ||g_ij||^2 <= d beta^4.

Centering the residues does not increase this norm. Applying the carry bound vectorially gives

    E_g = D_g (t_2-1)a_2^2/4
            + (sqrt(d) beta^2/a_2^(t_2-1)
                         + sqrt(D_g) C(a_2,t_2))^2.

It follows that a complete honest target cap is

    beta_next = ceil sqrt(E_z+E_u+E_g).

This cap includes every coefficient in z_0,z_1,t,g,h. Honest algebraic verification holds identically; the only probabilistic failure used in this norm argument is the fold event. Thus this is an honest-completeness bound for the full ordinary target, not merely for JL. The script replaces intermediate square roots by integer ceilings and Gamma by its ceiling, preserving the upper-bound direction.

The unpadded target ring dimension is exactly

    W_next = 2n + r t_1 kappa + (t_1+t_2)G.

The packing constraint must also be retained. Write M_aux=W_next-2n. To use multiplicity r_next=2nu+mu with positive integers nu,mu, split z_0 and z_1 into matching nu blocks each and the auxiliary vector into mu blocks. The common rank is

    n_next = max(ceil(n/nu), ceil(M_aux/mu)).

It is generally **not** ceil(W_next/r_next). Using the latter can break the paired dot-product layout in Section 5.3. Zero-padding changes dimension but not the norm cap. Every row of the numerical certificate below uses the former formula.

## 5. A seven-layer feasible profile

Choose

    q=4294967197, d=64, kappa=kappa_1=kappa_2=16,
    J=1024, H=552, s^2=23/5,
    T=34, a=901/1024, f=1/4.

The script certifies that q is prime, q=5 mod 8, the required splitting order is 32, and the challenge tail is below 123/1024. At every level choose a_1=a_2=b. The table is the exact result of the bounded grid described below; the final level is an ordinary level with its explicit target opened, not the optimized Section 5.6 terminal protocol.

| Level | n | r | beta | b | t_1 | t_2 | Gamma ceiling | beta_next | actual B | L_weak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 112 | 16384 | 16 | 8 | 6 | 395224 | 34762 | 74557 | 344751568 |
| 2 | 5418 | 33 | 34762 | 32 | 7 | 6 | 838547 | 30734 | 65918 | 591679968 |
| 3 | 1570 | 15 | 30734 | 64 | 6 | 5 | 741382 | 19764 | 42390 | 749455200 |
| 4 | 785 | 8 | 19764 | 64 | 6 | 5 | 476758 | 13112 | 28123 | 497214640 |
| 5 | 393 | 7 | 13112 | 64 | 6 | 5 | 316295 | 10211 | 21901 | 387209680 |
| 6 | 393 | 5 | 10211 | 64 | 6 | 5 | 246315 | 8735 | 18735 | 331234800 |
| 7 | 393 | 4 | 8735 | 32 | 7 | 6 | 210711 | 7680 | 7680 | 68935680 |

For the first six edges, (nu,mu) is respectively (7,19),(4,7),(2,4),(2,3),(1,3),(1,2). All JL modulus conditions and all three MSIS radii pass the strict q screen. The largest L_Gram is 14,490,340 and the largest L_out is 149,114. These ranks were chosen as an arithmetic example; they have not been certified secure.

The initial shape is the original Table 3 binary example's n=37450,r=112, with coefficient norm beta=16384. For binary source dimensions n_src=k_src=2^25, the coefficient-space bound is 2n_src+6k_src=2^28=beta^2; the slight shape mismatch is zero-padding. The repaired binary lifting condition s^2 beta^2<q holds. Also 6k_src<q and n_src+3k_src<q. Binary scalar aggregation at ell=160 adds no witness coordinates.

For binary scalar replies, use the specified integer representative in [-n_src,3k_src]. In this particular example the stronger inequality 2 max(n_src,3k_src)<q also holds, so direct centered lifting recovers that integer. The weaker span condition n_src+3k_src<q alone would not justify a centered parity test in general. The source relation must also explicitly pin the distinguished constant coordinate and public inputs as required by [r1cs_repair.md](r1cs_repair.md); an arithmetic shape certificate does not add these constraints automatically.

As a separate affine source example, set d=64, r=32,n=4096,beta=2048. Its packed ring dimension is M=131072 and beta^2=Md/2. One compatible shape has 10,000 constraints, 11,072 variables and ell=9 auxiliary affine aggregation polynomials: 11072+(3+9)10000=131072. The least prime divisor of 2^64+1 is 274177, certified in the script by exact division and exhaustive smaller odd divisors; hence 2/274177^9<2^-160. At the relaxed cap beta_aff=s beta the lifting inequality

    sqrt(Md/2) beta_aff + beta_aff^2/2 < q/2

is verified by squaring after checking that the right residual is positive. A first ordinary level using T=31,a=9/16,b=16,t_1=8,t_2=5 has beta_next=8799,B=18872,L_weak=79564352 and L_Gram=1186380. This is a compatible affine shape and norm budget, not a proof that any chosen R1CS has a satisfying witness.

## 6. Joint threshold optimization and a transparent cost ledger

The script searches T=28,...,40; for each T it finds the smallest certified rejection numerator over denominator 1024. It uses b in {2,4,8,16,32,64,128,256}, t_1=max(2,ceil(log_b q)), t_2 in {2,...,19}, the fixed r schedule, and the actual packing formula. It greedily minimizes beta_next, breaking ties by unpadded target dimension. It is not a global optimizer; it is enough to demonstrate that T alone is not the right target.

| T | Certified acceptance > | Peak L_weak | Final beta_next | Fixed-width ordinary payload (KiB) |
|---:|---:|---:|---:|---:|
| 30 | 89/256 | 1361458800 | 10272 | 166.469 |
| 31 | 289/512 | 1205824360 | 8544 | 166.141 |
| 32 | 365/512 | 1187347200 | 8194 | 162.859 |
| 33 | 833/1024 | 750252360 | 7979 | 163.602 |
| 34 | 901/1024 | 749455200 | 7680 | 163.602 |
| 35 | 473/512 | 758248400 | 7448 | 163.602 |
| 36 | 975/1024 | 772125120 | 7286 | 163.602 |
| 40 | 1017/1024 | 846726400 | 7074 | 163.602 |

T=29 has a certificate of acceptance greater than 9/256 but the seven-layer path fails this particular search grid. That failure is not an impossibility result. T=34 gives the smallest peak radius in this grid; T=32 gives the smallest displayed encoding bound. Optimizing global proof size, hardness, and honest runtime is a multi-objective task.

The size ledger uses two rank-16 outer commitments per ordinary layer, six aggregation polynomials per layer (the least m with q^m>=2^160), 1024 JL coordinates per layer, and all last-layer decomposition digits. Residues use 32 bits; low base-b digits use log_2 b bits; bounded high digits and JL coordinates use fixed signed-range indices. The deterministic coordinate bounds follow from Section 4 and ||p||^2<=552 beta^2. For T=34 it gives 688128 bits of early prover messages and 652096 bits of final witness, totaling 1,340,224 bits =163.6015625 KiB.

This is an upper bound on one possible encoding of this ordinary-core example. It omits statement/setup data, verifier challenge messages, framing and any Fiat--Shamir material. It is not a lower bound, does not use Gaussian entropy coding, and does not implement the original optimized final round. The original 53.84 KB Table 3 entry uses different ranks, heuristic width estimates and the optimized final round. Therefore the two figures do not establish a threefold necessary loss or a performance comparison. They do show that the present rigorous certificate has not recovered the original size claim.

At each level the two norm checks pass with probability greater than 67/132, uniformly over every honest input satisfying that level's cap. Conditional application through the seven levels gives a whole-attempt lower bound (67/132)^7 approximately 0.00867973. Independent fresh complete honest attempts would therefore take fewer than 115.211 attempts in expectation by this bound. This arithmetic is not a theorem that arbitrary local challenge retries preserve the security protocol; a restart policy must be part of the proved protocol. The estimate is conservative, and stronger moments or a larger Gamma can improve it. It must nevertheless be charged until a sharper honest-runtime argument is proved.

### A complete seven-layer profile with honest acceptance above one half

The preceding low acceptance is avoidable within the same architecture. For a fixed 1024-row projection and any H>512, the same variance calculation as in [jl_repair_review.md](jl_repair_review.md) gives

    Pr[||Pi w mod q||^2 > H beta^2]
        <= 512/(512+(H-512)^2),
    s^2=H/120.

Indeed E||Pi w||^2<=512 beta^2 and Var(||Pi w||^2)<=512 beta^4 for every ||w||<=beta; centering only reduces the norm. Cantelli yields the displayed bound. The JL lower-tail theorem is unchanged when the relaxed source bound is chosen as s beta, because 120(s beta)^2=H beta^2.

Take H=640, so s^2=16/3 and projection rejection is at most 1/33. Keep d=64,T=34,a=901/1024, and choose f=1/16, hence Gamma^2=32d beta^2/a. Each complete ordinary layer passes with probability greater than

    1-1/33-1/16 = 479/528.

This guarantee is uniform for every honest input within its layer's cap. Applying it successively to the conditional honest inputs gives whole seven-layer acceptance greater than

    (479/528)^7
      = 5785602523725084959 / 11440301174540992512
      > 1/2.

No local-retry modification is needed for that statement. The arithmetic certificate checks the last strict inequality as integers. The following second profile uses the same q and all three ranks 16:

| Level | n | r | beta | b | t_1 | t_2 | beta_next | actual B | L_weak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 112 | 16384 | 32 | 7 | 5 | 49845 | 115113 | 1033254288 |
| 2 | 5205 | 33 | 49845 | 64 | 6 | 5 | 47758 | 110293 | 1949980240 |
| 3 | 1335 | 15 | 47758 | 128 | 5 | 5 | 34414 | 79476 | 2788653888 |
| 4 | 668 | 8 | 34414 | 128 | 5 | 5 | 23592 | 54484 | 1911734592 |
| 5 | 334 | 7 | 23592 | 128 | 5 | 4 | 18494 | 42711 | 1498643568 |
| 6 | 334 | 5 | 18494 | 128 | 5 | 4 | 15836 | 36572 | 1283238336 |
| 7 | 334 | 4 | 15836 | 64 | 6 | 5 | 13896 | 13896 | 245681280 |

The paired splits are (8,17),(4,7),(2,4),(2,3),(1,3),(1,2). All three radius screens, all JL conditions with s^2=16/3, and the initial binary lifting condition pass. The largest collision radius is 2,788,653,888<q. The same fixed-width ledger gives 694272 early-message bits and 623744 final-witness bits, totaling 1,318,016 bits=160.890625 KiB. Its smaller size than the first profile is a consequence of a different decomposition path, not a universal monotonicity claim. Its larger MSIS radius may require larger ranks under a genuine hardness estimate. This second profile establishes simultaneous strict norm/lifting feasibility and constant whole-protocol honest completeness; it remains a mathematical parameter example.

## 7. Statistical budget versus computational loss

For the displayed schedule use the conservative N_min from T=31 even when T is larger. Then

    sum_i (r_i+2)/N_min = 198/N_min < 2^-140.

Its decimal exponent is approximately 140.14396645. With seven JL errors bounded by 2^-164, seven scalar errors q^-6, and seven ring errors q^-32, exact arithmetic gives

    198/N_min + 7*2^-164 + 7/q^6 + 7/q^32 < 2^-140.

The inequality remains true after adding a binary-source error 2^-160. Thus d=64 is sufficient for this particular statistical budget. The convenient all-lambda degree formulas in [statistical_family.md](statistical_family.md) are sufficient families, not mandatory concrete choices. For general parameters, one may instead take the smallest allowed power of two satisfying both 5^d>=(r+2)2^(lambda+32)/a and q^(d/2)>=2^(lambda+32), while retaining all norm and source constraints.

The recursive extractor's multiplier from [composition_repair.md](composition_repair.md) is bounded by

    P = product_i (1+r_i/(1-1/N_min)).

Exact rational arithmetic proves

    132779520 < P < 132779521,
    log_2 P approximately 26.98445740.

This is only the multiplier on nested core costs in the specified recurrence; initialization, local work, and the collision reductions' additional forks remain to be charged. It is not a rule to subtract exactly 27 security bits from an estimate without specifying a cost/advantage model.

More seriously, the current single-layer computational loss contains

    sqrt(L) + eta_E,
    L=eta_0+sqrt(eta_h)+r sqrt(eta_y)+sqrt(eta_g).

All eta values concern the complete reductions at their actual runtime. Even if eta_y were the only term, its contribution is sqrt(r) eta_y^(1/4). To make that contribution at most 2^-128 by this inequality alone requires eta_y<=2^-512/r^2. This is a limitation of the available concrete reduction, not evidence of a 512-bit attack requirement on the scheme. It prevents equating a per-instance 128-bit Core-SVP estimate with a proved 128-bit concrete knowledge-security theorem. Further losses from layer summation and source binding must also be budgeted.

Subsequent refinement: [bad-mass-weighted analysis](computational_loss_refinement.md) improves this earlier bound for the same gated extractor to `sqrt(eta_0)+(2eta_h+2r eta_y+eta_g)^(1/3)+eta_E`, with a tighter exact expression. In the only-eta_y case the exact term is `(r eta_y)^(1/3)`. The formulas above document the original parameter-screen baseline; the full-time, initialized-experiment and concrete-advantage obligations persist under the refined bound.

## 8. A structural MSIS screen that a future estimator must include

For the chosen prime,

    q=44174^2+48411^2.

Let pi=44174+48411 X^(d/2), with conjugate pi_bar=44174-48411 X^(d/2). Then pi pi_bar=q. Since multiplication by X^(d/2) is an orthogonal skew-symmetric map in coefficient coordinates,

    ||pi y||^2=q ||y||^2.

Thus a solution on the relevant single CRT component can be multiplied by pi to obtain a full integer kernel vector, scaling its norm by sqrt(q). Any meaningful hardness screen must account for this module/CRT structure and the q-primary lattice, rather than relying solely on a flat dimension kappa d. This section gives a mathematical dimension/radius transformation, not an algorithm for finding short vectors or a concrete attack estimate. In particular, the displayed kappa=16 has not been vetted against all relevant lattice algorithms.

## 9. New shortness-check literature does not remove the joint constraints

The supplied full text of Geng--Plancon, *Succinct Shortness Check Under a Few Kilobytes via Tensor Train Random Projections*, ePrint 2026/2146, proves concentration for its Rademacher construction without assuming Gaussian rows (Introduction and Sections 3--5). This is a relevant route to reduce the verifier's projection representation. Its quoted LaBRADOR baseline and completeness discussion still use heuristic chi-square language; those baseline claims are not independent repairs of LaBRADOR's original lemma.

In the visually inspected Table 1, the TTRP slack is approximately 2^10, not the decimal string "210" and not 29; the stated increase relative to the baseline is about 2^9. Section 7.2 fixes projection error about 2^-90 for its parameter search. Those are different error/slack targets from this repair. The table reports roughly 6492 MB to 0.2 MB projection representation and roughly 1.84 KB to 3.9 KB shortness-check proof size; these are not full repaired LaBRADOR proof sizes.

For the binary source size in Section 5, keeping beta=2^14 but replacing s by 2^10 requires s^2 beta^2<q, hence q>2^48. It cannot retain the 32-bit modulus. This strict incompatibility is a statement about that combined parameter choice, not about all uses of TTRP. Moreover, with the unfiltered full-cube T approximately 81.5, the Gram term 4 T s beta already exceeds the selected 32-bit q. Any proposed shortness replacement must re-optimize q, the source lift, all decomposition widths, and MSIS radii; its short projection by itself does not settle feasibility.

## 10. What has and has not been established

The following are now rigorous within the ordinary-core setting: a non-Gaussian complete honest norm cap; scalar conditional covariance for the filtered challenges; exact finite acceptance/count certificates; correct upper-triangular dimensions and paired block padding; a feasible recursive norm/lifting profile; and a separated statistical/runtime ledger. These are stronger guarantees than the original heuristic completeness calculation.

The present evidence establishes neither a general architectural impossibility nor a faster/smaller concretely secure system. To reach a defensible performance claim one needs, at minimum, a tighter concrete binding analysis or an explicit advantage budget at the full reduction time; verified lattice estimates including the ring/CRT structure; an implementation evaluation that respects the certified whole-attempt completeness (and a proved policy if retries are introduced); and a re-proved optimized final round or another compact terminal representation. Improving JL rows, fold concentration, digit caps, and threshold selection can reduce costs, but cannot substitute for those missing computational and composition checks.
