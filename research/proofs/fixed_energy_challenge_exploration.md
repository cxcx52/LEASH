# Fixed-energy and bounded-energy challenge certificates

Date: 2026-11-14. Scope: exact cardinality, operator-tail and honest-moment mathematics for degree-64 five-symbol challenges. No prover, cryptographic RNG, lattice algorithm or security estimator is implemented. No novelty is claimed for counting, exponential tilting or the moment inequalities.

**Main findings.** The energy-71 shell admits a rigorous operator-filter certificate at T=27, but its entire cardinality is already too small for the current accept-gated extractor's 128-bit statistical budget. A useful alternative is the energy ball with squared norm at most 104, filtered at operator norm strictly below 30. It retains more than two thirds of that ball, has enough challenges for the specified seven-layer/Q=128 statistical budget, and admits the improved honest fold cap Gamma^2=9d*beta^2 at rejection probability below 1/16. These are arithmetic/probability certificates; ranks, complete recursive dimensions and computational losses still require their own manifest.

The exact checker is `scripts/fixed_energy_challenge_checks.py`; its full output, including exact fractions and a bounded search grid, is `notes/parameter-results/fixed-energy-challenge-checks.json`.

## 1. Exact shell/ball counts

Let

    B_E={c in {-2,-1,0,1,2}^64 : sum_j c_j^2<=E},
    S_E={c in {-2,-1,0,1,2}^64 : sum_j c_j^2=E}.

Write A_d(e) for the coefficient of z^e in (1+2z+2z^4)^d. Then

    |S_E|=A_64(E),       |B_E|=sum_(e=0)^E A_64(e),
    A_d(e)=A_(d-1)(e)+2A_(d-1)(e-1)+2A_(d-1)(e-4),
    A_0(0)=1.

Terms outside the possible energy range are zero. This recurrence is exact integer arithmetic.

For E=71, if j coefficients have magnitude two, there are 71-4j unit coefficients and 3j-7 zeros. Thus

    |S_71|=sum_(j=3)^17
       64!/[j!(71-4j)!(3j-7)!] * 2^(71-3j)
      =914575309776010636758020194460195880960.

Its base-two logarithm is approximately 129.42636958. The original paper's fixed type is the j=10 summand (10 magnitude-two, 31 unit and 23 zero coefficients), of cardinality 361715808335458406596740595030299770880, approximately 2^128.08812426. The paper's reported approximately six draws to pass T=15 is an empirical statement, not a lower bound on the filtered cardinality. The full shell considered here is a larger, different raw family.

## 2. Rational tilting and its conditioning cost

For rational 0<t<=1 define independent coordinates by

    Pr_t[X_j=c]=t^(c^2)/Z_t,
    Z_t=1+2t+2t^4.

For t=2/3 the integer weights, in symbol order (-2,-1,0,1,2), are (16,54,81,54,16), with sum 221. Every vector in S_71 has the same product weight. Consequently the tilted product law conditioned on S_71 is **exactly uniform** on that shell, and

    P_t[S_71]=|S_71|*(2/3)^71/(221/81)^64
             =|S_71|*3^185*2^71/221^64
             approximately 0.03636434524.

A product-law tail bound divided by this probability is therefore a valid shell tail bound. This conditioning factor, approximately 27.5, must not be omitted. It is an analysis cost; an exact shell-count decoder could sample the shell directly, so it is not an unavoidable runtime lower bound.

For a ball, conditioning the tilted law on B_E is generally **not uniform**. Instead use the pointwise counting inequality: for t<=1 and energy at most E, t^(energy)>=t^E. Therefore, for any bad event F_bad,

    |B_E intersect F_bad|
       <=Z_t^64*t^(-E)*Pr_t[F_bad].                 (COUNT-TILT)

The final uniform-ball probability is obtained by dividing this count by |B_E|. No replacement of that conversion factor by the tilted ball probability is made.

## 3. Product MGF and exact operator-tail certificates

Under the tilted product law put

    v_t=E_t[X_j^2]=(2t+8t^4)/Z_t,
    m4_t=E_t[X_j^4]=(2t+32t^4)/Z_t.

Every tilt used by the checker satisfies m4_t<=3v_t^2 and 5v_t>4. The k=1 Gaussian even-moment comparison is equality and k=2 is the checked fourth-moment inequality. For k>=2 the actual consecutive even-moment ratio is less than four, while the Gaussian comparison ratio is (2k+1)v_t>=5v_t>4. Induction and the nonnegative even power series prove

    E_t exp(u X_j)<=exp(v_t*u^2/2)                  (all real u).

For t=2/3, v_t=236/221. For the useful ball certificate t=4/5, the integer symbol weights are (256,500,625,500,256), their sum is 2137, and v_t=3048/2137. The proof uses actual rational moment comparisons, not a Gaussian approximation.

At each root zeta of X^64+1 and phase phi, the projection weights cos(j*arg(zeta)-phi) have squared sum 64/2. Chernoff therefore gives

    Pr_t[Re(exp(-i phi)c(zeta))>=u]
       <=exp(-u^2/(64v_t)).

Use an m-direction equally spaced angular net and one root from each conjugate pair. If gamma_m<cos^2(pi/m), then

    Pr_t[||c||op>=T]
       <=(64m/2)*exp(-gamma_m*T^2/(64v_t)).          (TAIL)

The net constants used here have elementary rational certificates:

| Directions m | Strict lower bound gamma_m |
|---|---:|
| 8 | 1707/2000 |
| 12 | 933/1000 |
| 16 | 9619/10000 |

Indeed (707/500)^2<2 and (433/250)^2<3 give the first two bounds through the half-angle identities. Also (4619/5000)^2<1707/2000, so cos(pi/8)>4619/5000 and cos^2(pi/16)>9619/10000. The bad event is closed and the retained operator event is strict.

For every positive rational x, the finite positive series

    L_80(x)=sum_(k=0)^80 x^k/k! < exp(x)

gives exp(-x)<1/L_80(x). The checker substitutes that rational upper bound in (TAIL). Thus no numerical exponential, trigonometric evaluation or floating-point threshold decides any certificate. Displayed decimal values are presentation only.

## 4. What the energy-71 calculation proves and cannot prove

Applying (TAIL), dividing by the exact shell probability, and taking the best of the three specified angular nets yields:

| T | Net directions | Certified upper bound before truncating at one |
|---|---:|---:|
| 15 | 8 | about 423.89 |
| 26 | 12 | about 1.03703 |
| 27 | 16 | below 0.492750 |
| 28 | 16 | below 0.227218 |
| 30 | 16 | below 0.044402 |
| 31 | 16 | below 0.018817 |

In particular, T=27 retains more than half of S_71. The T=15 and T=26 entries are vacuous certificates; they do not show that the corresponding sets are empty or small.

The raw shell is invariant under signed coefficient permutations. After imposing the operator filter, global negation, signed shifts and odd Galois substitutions still preserve the law. The reviewed covariance symmetry argument gives Cov(C)=v I_64. Since every retained challenge has squared norm exactly 71, taking the trace fixes

    v=71/64

exactly, regardless of the operator acceptance probability. Independence within a retained challenge is not implied.

There is nevertheless a decisive cardinality obstacle **for the current extraction error bound**:

    |S_71| < 3*2^128.

For any positive multiplicity r and any subset C of this shell,

    (r+2)/|C| >=3/|S_71| >2^-128.

Thus no operator threshold or sharper counting proof can certify a single positive-arity layer's challenge term at 2^-128 using this shell and the current (r+2)/N expression. This is a limitation of the proved bound and family, not a protocol attack or an information-theoretic lower bound on actual soundness.

For orientation, raw shell logarithms at energies 84,88,112,116 are approximately 135.4195,136.891,142.525,142.973. The checker gives exact counts. Energy 84 is already too small for the seven-layer numerator 198 at 128 bits, and energy 112 is too small after Q=128 whole-protocol restarts. Having a larger raw count at energies 88 or 116 only removes that necessary obstruction; the operator filter must still retain enough elements.

## 5. A certified energy-ball alternative: E=104, T=30

Define

    C_ball={c in {-2,-1,0,1,2}^64:
               ||c||_2^2<=104 and ||c||op<30}.

The exact raw count is

    N_ball=20905094450944450994971371210796521612779265.

Use t=4/5, m=12 and gamma=933/1000 in (COUNT-TILT) and (TAIL). With

    x=(933/1000)*30^2/[64*(3048/2137)],

the checker proves the following exact rational inequality:

    [(2137/625)^64*(5/4)^104/N_ball] *384/L_80(x)
      <1/3.                                       (BALL-COUNT)

The left side is approximately 0.3302760658. Therefore a uniform raw ball element passes the strict operator filter with probability greater than 2/3, and

    |C_ball| >= floor(2N_ball/3)+1
      =13936729633962967329980914140531014408519511
      =:N_min.

This lower bound has approximately 143.32180014 bits. All selected challenges satisfy the deterministic squared-norm cap 104 and operator cap 30. The old full-cube certificate had squared-norm cap 256 and T=34; this candidate improves both deterministic bounds while giving a smaller certified cardinality.

The zero polynomial is in C_ball. Hence an independent uniform sample equals zero with probability exactly 1/|C_ball| and implements the accept-gated extractor's abort coin without enumerating the final cardinality. Distinct challenges have coefficientwise differences of magnitude at most four, so the already proved unit-difference argument applies for prime q>32 with q=5 mod8. The selected q=4294967197 remains in that family.

An exact uniform raw-ball sampler can conceptually choose an integer rank uniformly in [0,N_ball) and decode it using the DP completion counts. The checker implements only this deterministic rank/unrank map, not a random generator or prover. Independent rejection by the exact SPD operator predicate then gives the exact uniform law on C_ball, with expected raw-ball draws below 3/2. A bounded sampling-abort policy, if desired, must still be specified separately.

## 6. A reusable moment lemma for symmetric raw laws

The iid cube formula must not be applied to the uniform ball: its coordinate magnitudes are dependent. The following lemma supplies the correct replacement.

Let d>=2 be a power of two. Let a real raw challenge vector X in R^d have a law invariant under all coordinate sign flips and coordinate permutations, with finite fourth moments. Put

    v0=E[X_0^2],   m4=E[X_0^4],   m22=E[X_0^2 X_1^2],
    V_U=d*m4+d(d-1)*m22-d^2*v0^2=Var(||X||^2),
    g=2m22-v0^2+(m4-3m22)/d.

These are moments of an actual distribution. In particular

    g=V_U/d^2+(1-2/d)m22>=0                        (d>=2).

Let F be an event of probability p>a>0 such that the selected law has zero mean and covariance v I_d. For the ball operator filter this follows from negation, signed shifts and odd Galois substitutions; arbitrary coefficient permutations need **not** preserve the filtered law.

For any fixed stacked ring multiplier M_s with H=M_s^T M_s and t=||s||^2, raw sign/permutation invariance gives the exact expansion

    E[(X^T H X)^2]
       =m22[(tr H)^2+2tr(H^2)]
            +(m4-3m22)sum_j H_jj^2.

Use H_jj=t, trH=dt and the reviewed paired-spectrum inequality tr(H^2)<=(trH)^2/2. Since m22>=0, this proves

    E[X^T H X]=v0*d*t,
    Var(X^T H X)<=g*d^2*t^2.

Centering before conditioning, rather than conditioning an uncentered fourth moment, yields

    Var(||M_s C||^2)
       <=[g/p-(v-v0)^2]*d^2*t^2,

where C has the selected law. For independent C_i and fixed witnesses s_i with S=sum_i||s_i||^2<=beta^2, the same paired output-covariance trace inequality as in `filtered_fourth_moment.md` gives

    Var(||sum_i C_i s_i||^2)
       <=d^2*S^2*max{g/p-(v-v0)^2,v^2}.             (BALL-VAR)

The raw energy-indicator covariance is exactly

    Cov(||X||^2,1_F)=pd(v-v0).

Consequently

    |v-v0|<=sqrt[V_U(1-p)/(p d^2)]
            <=rho:=sqrt[V_U(1-a)/(a d^2)].

With k=(1-f)/f, split the maximum in (BALL-VAR) into two branches and apply Cauchy--Schwarz to v-v0 in the centered branch. Cantelli then gives the sufficient cap

    Gamma^2/(d beta^2)
       >=max{v0+sqrt(g/(a f)),
              (v0+rho)(1+sqrt((1-f)/f))}.           (GENERAL-CAP)

This is a sufficient envelope, not an exact optimization over all realizable distributions. The s_i must be fixed before the independent selected challenges, including conditionally on preceding transcripts. Zero witnesses are deterministic. Centering integer products modulo q cannot increase their coefficient norm. The lemma uses full permutation symmetry only for the **raw** fourth expansion; filtered isotropy comes from the smaller symmetry group just identified.

## 7. Exact raw ball moments and the coefficient nine

The raw B_104 moments are computed by the same DP. If N=N_ball, then

    E[U]=sum_e e A_64(e)/N,
    E[U^2]=sum_e e^2 A_64(e)/N,
    v0=E[U]/64,
    m4=[2|B_103 in dimension 63|+32|B_100 in dimension 63|]/N,
    m22=[E[U^2]-64m4]/(64*63).

All sums run from zero to 104. For a compact exact representation, let

    D0=6968364816981483664990457070265507204259755,
    A =10812591746746593983990986436377990597623638,
    B =33680962045542507461544592551635026595528126,
    C =16545642724655365897495237925661933034110636.

Then v0=A/D0, m4=B/D0 and m22=C/D0. The resulting values are approximately

    v0=1.551668437392509,
    m4=4.833409692251479,
    m22=2.374393872768348,
    g=2.305335119591999,
    V_U=21.05776270402408.

Set a=2/3 and f=1/16. Then rho^2=V_U/(2*64^2). The checker proves

    (9-v0)^2>24g,       v0<25/16,       rho<1/16.

The first inequality certifies the first branch of (GENERAL-CAP). For the second, sqrt(15)<31/8 gives

    (v0+rho)(1+sqrt(15))
       <(26/16)(39/8)=507/64<9.

These checks can be written entirely as modest integer comparisons. Define

    G=(125C+B)D0-64A^2,
    V=(B+63C)D0-64A^2.

Then g=G/(64D0^2), rho^2=V/(128D0^2), and the three checks are

    8(9D0-A)^2>3G,
    16A<25D0,
    2V<D0^2.

Thus the exact honest-fold choice

    Gamma^2=9d beta^2

has rejection probability below 1/16. The nontrivial first margin is about 0.1496 in squared units; the checker records its exact positive fraction. No decimal rounding selects the coefficient nine.

## 8. Full statistical budget and honest completeness

Use the reviewed seven-layer multiplicities (112,33,15,8,7,5,4), so sum(r_i+2)=198, the same q=4294967197, m=6, d=64 and source scalar error 2^-160. For Q=128 bounded whole-protocol restarts, the checker includes **all** the following terms:

    Q [198/N_min +7*2^-164 +7/q^6 +7/q^32 +2^-160]
      <2^-128.                                    (FULL-STAT)

Its decimal exponent is approximately 128.69244342. N_min by itself certifies only the challenge part; (FULL-STAT) is the explicitly checked combined statistical expression. The computational losses from every binding/extraction reduction remain additional and are not certified by this calculation.

At the reviewed projection threshold H=640, s^2=16/3 and JL honest rejection is at most 1/33. Combining with fold rejection below 1/16 gives per-layer acceptance greater than 479/528. If a complete recursive norm/packing manifest uses these parameters and valid resulting caps, a full seven-layer attempt accepts with probability greater than (479/528)^7>1/2. The bounded-restart theorem then gives honest final rejection below 2^-128 at Q=128 and expected honest attempts below two.

The source slack, actual target-opening bounds, decompositions, dimensions and collision norms must all be checked for the selected manifest. This file supplies a challenge/moment certificate. It does not substitute an optimized new seven-layer table or a hardness estimate for that work.

## 9. Bounded exploration and the trade-off

The checker explores only E in {96,100,104,108,112,116,120,128,144,256}, T in {29,30,31,32,34}, the three displayed angle nets and nine listed rational tilts. It selects the smallest **certified** bad-count bound within that finite grid. No global optimality or impossibility follows from a failed grid point.

At T=30, representative results are:

| Energy cap | Best listed tilt | Certified rejection upper bound, rounded | Certified cardinality bits, rounded |
|---|---:|---:|---:|
| 96 | 3/4 | 0.163790 | 141.467 |
| 100 | 3/4 | 0.232186 | 142.501 |
| 104 | 4/5 | 0.330277 | 143.328 |
| 108 | 4/5 | 0.432368 | 143.989 |
| 112 | 5/6 | 0.530627 | 144.495 |
| 116 | 6/7 | 0.632483 | 144.809 |
| 128 | 19/20 | 0.805415 | 145.290 |

The formal E104 result deliberately uses the simpler 2/3 acceptance certificate and its slightly smaller N_min, rather than the displayed best fractional bound. The same improved angular nets also improve some full-cube certificates; comparisons should not attribute every gain solely to the energy restriction.

Relative to the reviewed T34 full-cube profile, the E104/T30 candidate has lower deterministic energy, a smaller operator cap and an improved certified fold coefficient (9 instead of 21/2), while its smaller challenge set leaves much less statistical margin. These facts establish a meaningful mathematical trade-off. They do not establish faster proving, shorter complete proofs, improved numerical lattice security or top-conference novelty.

## 10. Reproduction and implementation scope

Run `python scripts/fixed_energy_challenge_checks.py`. The decisive assertions use integers and Fraction. The script verifies the shell formula against the DP, tilted MGF prerequisites, all angular rational constants, positive-Taylor tail bounds, the E104 count and moment certificates, the full restart statistical budget, and the deterministic rank decoder on 208 cases. Independent complete small-ball enumerations in d=2 and d=4 check the non-iid raw fourth expansion, filtered covariance, centered variance bound and energy-indicator variance inequality using stacked two-block witnesses. The general probability and moment bounds are proved in this document, not inferred from those finite checks.

The existing exact SPD predicate from `certified_filtered_challenges_checks.py` can decide the strict operator membership without floating-point tolerances. This exploration does not implement a new protocol, change the package, or claim that any original T15 cardinality assertion has been disproved by a loose upper bound.
