# Certified operator-norm-filtered cubical challenges

Date: 2026-11-14. Scope: a new optional challenge family with exact statistical certificates. The original unfiltered cube profile and its API remain unchanged. This module supplies no production CSPRNG, cryptographic prover, or full security estimate. The concentration tools are standard; no novelty is claimed for them.

## 1. Definition and result

Let d≥2 be a power of two and write

    R=Z[X]/(X^d+1),
    B_d={Σ_(j=0)^(d−1)c_j X^j : c_j∈{−2,−1,0,1,2}}.

Let A_c be the integer d×d matrix of multiplication by c in the coefficient basis of R, with negacyclic wraparound. Define its real Euclidean operator norm and the strictly filtered set

    ||c||_op=||A_c||_(2→2),
    C_(d,T)={c∈B_d : ||c||_op<T}.

For independent uniform coefficients in the five-symbol alphabet,

    Pr[||c||_op≥T] ≤4d exp(−17T²/(40d)).       (TAIL)

The displayed bound is conservative; the angular argument below actually gives a strict improvement whenever T>0.

An integer-only sufficient certificate for this rejection probability to be less than 1/2 is

    (8d)^(40d)·60^(17T²) < 163^(17T²).         (HALF)

Consequently,

    |C_(d,T)|>5^d/2,
    E[number of independent candidates until acceptance]<2.

For d=64, the first positive integer T satisfying (HALF) is **31**. A stronger exact certificate proves rejection probability below 7/16, hence

    |C_(64,31)|>(9/16)·5^64,
    E[candidate draws]<16/9.

The zero polynomial is retained. Every selected challenge has deterministic coefficient bound `||c||_∞≤2` and squared Euclidean norm `||c||₂²≤4d`; do not reuse the original fixed norm-squared 71.

For prime q≡5 (mod 8), q>32, reduction of this set into `Rq=Fq[X]/(X^d+1)` is injective and every difference of two distinct selected challenges is a unit. The proof and an alternative hypothesis are in Section 5.

## 2. A scalar MGF certificate

Let X be uniform on {−2,−1,0,1,2}. It is symmetric, and for k≥1,

    E[X^(2k)]=(2+2·4^k)/5.

The k=1 moment equals 2=(2)!/1!. If `b_k=(2+2·4^k)/5`, then `b_(k+1)<4b_k`. If `a_k=(2k)!/k!`, then `a_(k+1)/a_k=2(2k+1)≥6` for k≥1. Induction gives

    E[X^(2k)]≤(2k)!/k!   for all k≥1.

The constant moment is 1; the displayed formula for b_k is not used at k=0. Comparing the nonnegative even power-series coefficients therefore proves, for every real t,

    E exp(tX)≤exp(t²).                         (MGF)

For independent X_j and arbitrary real weights w_j,

    E exp(t Σ_j w_j X_j)≤exp(t² Σ_j w_j²).

This is a precise finite-distribution calculation, not a Gaussian approximation.

## 3. From roots to the operator-norm tail

Let `ζ_k=exp((2k+1)πi/d)` for k=0,...,d−1. The negacyclic shift is unitary and is diagonalized by the normalized evaluation transform at these roots. Therefore

    ||c||_op=max_k |c(ζ_k)|.

Real coefficients give conjugate pairs, so only d/2 roots need be considered.

Fix a root angle θ=(2k+1)π/d and a direction φ. Then

    Re(exp(−iφ)c(exp(iθ)))=Σ_j X_j cos(jθ−φ).

Since d≥2 is even and `exp(2iθ)≠1`, the geometric sum `Σ_(j=0)^(d−1)exp(2ijθ)` vanishes. Hence the weights satisfy exactly

    Σ_j cos²(jθ−φ)=d/2.

Using (MGF), for u≥0 and t≥0,

    Pr[Re(exp(−iφ)c(ζ_k))≥u]
       ≤exp(−tu+t²d/2)
       ≤exp(−u²/(2d)),                         (PROJ)

where the last bound takes t=u/d.

Use the eight directions φ=ℓπ/4, ℓ=0,...,7. Every nonzero complex number has one such direction within angle π/8; therefore a root value of magnitude at least T has a projected value at least `T cos(π/8)` in some direction. The exact identity

    cos²(π/8)=(2+sqrt(2))/4 >17/20

follows from `sqrt(2)>7/5`, equivalently `2>49/25`.

There are `(d/2)·8=4d` root-direction choices. Applying (PROJ) and a union bound gives (TAIL). The bad event is the **closed** event `||c||_op≥T`, and the sampler accepts the complementary strict event `||c||_op<T`; equality is not lost in the argument.

## 4. Fully integral cardinality certificates

The elementary positive exponential series gives

    e > Σ_(k=0)^5 1/k! =163/60.

Put `A=17T²`, `B=40d`. For any rational target rejection level u/v with 0<u<v, the integer comparison

    (4dv)^B ·60^A < u^B ·163^A               (CERT(u/v))

implies `4d exp(−A/B)<u/v`. Indeed, taking the positive B-th root first gives `4dv/u < (163/60)^(A/B)`, and `e>163/60` completes the implication. No numerical exponential or logarithm participates in this certificate.

An inclusive integer lower bound on the filtered cardinality is therefore

    N_min=floor((v−u)5^d/v)+1.                 (COUNT)

For d=64,T=31 the checker establishes:

| Certified quantity | Value |
|---|---:|
| Raw cube cardinality | 542101086242752217003726400434970855712890625 |
| N_min from rejection <1/2 | 271050543121376108501863200217485427856445313 |
| N_min from rejection <7/16 | 304931861011548122064596100244671106338500977 |
| Strict acceptance lower bound | 9/16 |
| Strict expected candidate-draw upper bound | 16/9 |
| Deterministic coefficient norm-squared cap | 256 |
| Operator threshold | 31 |

T=30 does not satisfy (HALF). This means only that this particular sufficient certificate does not certify T=30; it does not prove the actual acceptance probability at T=30 is below one half.

Selecting the first positive integer T satisfying (HALF) produces `T=O(sqrt(d log d))`: it suffices that

    17T² log(163/60) >40d log(8d).

The actual selection/checking routine uses the integer comparison, so this asymptotic explanation introduces no floating-point decision.

## 5. Unit differences: precise modulus conditions

### Preferred two-factor family

Assume q is an odd prime, q≡5 (mod 8), and q>32. Lyubashevsky–Seiler's Corollary 1.2, with k=2, gives both the two irreducible factors and invertibility for `0<||f||_∞<sqrt(q/2)`. Since any distinct cube difference has `0<||f||_∞≤4` and q>32, it meets that criterion. [LS18, *Short, Invertible Elements in Partially Splitting Cyclotomic Rings and Applications to Lattice-Based Zero-Knowledge Proofs*](https://eprint.iacr.org/2017/523)

For clarity, the relevant k=2 special case also has the following direct proof. Choose s∈Fq with s²=−1. The two factors are

    X^(d/2)−s,       X^(d/2)+s.

They are irreducible: for q≡5 mod8, the order of q modulo 2d is d/2, so each primitive 2d-th root has Frobenius orbit of that size; each displayed factor already has degree d/2. For d=2 the factors are linear. The order statement for larger d follows inductively from `v_2(q^(2^t)−1)=t+2`.

Write a nonzero cube difference as

    f=u+X^(d/2)v,

where each coefficient of u,v lies between −4 and 4. If one factor divided f, then coefficientwise `u_j±s v_j=0 mod q`, so

    q divides u_j²+v_j².

But `0≤u_j²+v_j²≤32<q`, forcing u_j=v_j=0 for every j, a contradiction. Thus neither factor divides f, and f is a unit in Rq. Since q>4, distinct cube polynomials also remain distinct modulo q.

The size condition cannot simply be omitted: for q=13 and d=2, the nonzero short polynomial `f=2+3X` has determinant `2²+3²=13` and is not a unit. It is a difference of two cube polynomials. This example is a check on the hypothesis, not a protocol attack.

### More general sufficient alternative

If one assumes instead only that q is prime and X^d+1 splits into two distinct irreducible factors of degree d/2, then **q>16d** is another sufficient condition, without requiring q≡5 mod8.

For a nonzero integer difference f, its negacyclic multiplication matrix has nonzero integer determinant because X^d+1 is irreducible over Q. If f were noninvertible mod q, its matrix would have nullity at least d/2 over Fq; Smith normal form then implies `q^(d/2)` divides its determinant. Hadamard's inequality gives

    0<|det A_f|≤||f||₂^d≤(16d)^(d/2)<q^(d/2),

a contradiction. This alternative is more restrictive for the preferred q≡5 mod8 family and is **not** a necessary condition for it.

The example q=4294967197 is prime, congruent to 5 modulo 8, and greater than 32. The example and tests reuse the existing `validate_ring` condition, including its trial-division primality check. This certifies the challenge ring property, not the hardness of MSIS at that modulus.

## 6. Exact selection without FFT tolerances

For integer T, let

    H_c=T²I−A_c^T A_c.

Then `||c||_op<T` if and only if H_c is positive definite. For a real symmetric matrix, Sylvester's criterion says this holds exactly when every leading principal minor is positive.

The reference checker computes these minors using fraction-free Bareiss elimination with no row exchanges. Each pivot is the next leading principal determinant; while earlier pivots are positive, the exact divisions are valid. A nonpositive pivot rejects immediately. A zero pivot, including an exact equality `||c||_op=T`, therefore rejects. Accepted inputs require all d positive pivots.

All entries are integers. Their bit lengths and the bit lengths of the intermediate minors are polynomial in d and log T, so this is a polynomial-time exact predicate. The reference implementation uses O(d³) integer arithmetic operations; it is a correctness reference, not a performance claim. Faster certified numerical enclosures could be added later, provided uncertain cases fall back to an exact decision and the sampler's distribution remains exactly specified.

The optional [certified Fourier implementation](certified-fourier.md) now provides such an enclosure. Its public API constructs the certified table internally; it returns exactly the same strict decision and falls back to this integer predicate whenever the interval is inconclusive.

The sampler is conceptually:

1. draw d independent unbiased symbols in {−2,−1,0,1,2};
2. accept iff the exact predicate says `||c||_op<T`;
3. otherwise repeat with fresh independent symbols.

Uniform raw sampling followed by this deterministic predicate gives the exact uniform distribution on C_(d,T). The expected number of candidates is the reciprocal of the acceptance probability, hence the certified bounds above. Conditioning destroys independence of the selected coefficients; later proofs must not continue treating them as independent raw symbols.

If an application requires a strict cap of H raw candidates, declare a sampling abort when all H fail. Its probability is less than `(7/16)^H` for the d64,T31 certificate, and conditional on not aborting the accepted output remains exactly uniform on C. Such a generation abort and its completeness/cost implications must be specified; it should not be replaced by a biased fallback challenge.

## 7. Zero and norm accounting in downstream extraction

Zero belongs to C because T>0. Thus an independent selected challenge equals zero with probability exactly `1/|C|`. The accept-gated extractor's abort coin can be implemented by the event

    sample independent c_abort from C; abort iff c_abort=0.

No exact enumeration of |C| is needed. The proof of weak openings only requires nonzero differences of **distinct** challenges, so allowing zero as an individual challenge is compatible with that proof. This is not permission to allow a zero challenge difference in a weak-opening certificate.

Deterministically, every selected challenge has `||c||₂²≤4d`. An additional certified second-moment bound follows without asserting coefficient independence:

    E[||c||₂² | selected]
       ≤E_raw[||c||₂²]/Pr[selected]
       <(2d)/(9/16)=32d/9                     (d64,T31).

Any use of this average in honest folding must still establish the required covariance/chronology statements. The deterministic main soundness bounds may safely use operator threshold T=31 and the appropriate coefficient bound. Replacing the old challenge family changes honest response statistics and MSIS bounds; it does not preserve old proof-size estimates automatically.

The repaired main-layer challenge term becomes `(r+2)/|C|≤(r+2)/N_min`. Using only the weaker half-acceptance N_min, the checker certifies that:

- r=112 gives a challenge term at most 2^(−140);
- summing this term over multiplicities (112,33,15,8,7,5,4) gives at most 2^(−139).

These are **challenge-term-only** certificates. JL, scalar/ring aggregation, affine-R1CS reduction, computational binding losses, composition cost and any compiler loss remain to be charged separately.

## 8. API and reproduction

The optional module is `labrador_repair.challenges`. The existing unfiltered `bounds.challenge_cube` function and all profiles using it retain their original values.

- `filtered_tail_certified(d,T,rejection_upper)` checks (CERT) using integers. The rejection target must be a `fractions.Fraction` strictly between zero and one. A false result means that this sufficient certificate did not pass.
- `filtered_challenge_count_lower(d,T,rejection_upper)` returns the inclusive integer lower bound (COUNT), and raises `ValueError` if its sufficient tail certificate fails. This is a lower bound on cardinality; the function does not enumerate or return the exact cardinality.
- `exact_operator_norm_below(coefficients,T)` applies the strict integer positive-definiteness test. It accepts five-symbol coefficient vectors of power-of-two length at least two. Equality rejects.
- `filtered_challenge_profile(q,degree=64,threshold=31,rejection_upper=Fraction(7,16))` combines these statistical bounds with the existing LS18 unit-difference ring validator. It does not estimate MSIS hardness.

From the repository root, after `python -m pip install -e .`, run:

    python -m unittest discover -s tests -v
    python examples/certified_challenges.py

The implementation uses only Python standard-library integer and rational arithmetic. The example reports the strict operator threshold 31, the inclusive cardinality lower bound, acceptance probability greater than 9/16, and expected raw candidate count less than 16/9. Large exact integers are serialized as decimal strings so JSON readers cannot silently round them.

The tests cover:

- the exact rational lower bound on e and 32 scalar even-moment comparisons;
- the d64 integer rejection certificates, failure of the T=30 sufficient certificate, and the inclusive integer rounding in (COUNT);
- the d2 count lower bound against the fully enumerated filtered set;
- 100 d=2 and 3750 d=4 exact operator decisions against independent closed spectral formulae, including the exact d4,T4 count of 449;
- rejection of the equality case c=2 at T=2;
- d64 acceptance of zero/constant 2 and rejection of the all-2 polynomial at T=31;
- the q=13 counterexample when the modulus-size condition is dropped;
- the example modulus through the existing ring validator and preservation of the original cube profile;
- exact challenge-error fractions and validation of malformed inputs.

The existing `test_repairs.py` suite additionally enumerates all 6560 nonzero d=4 cube differences at q=101 and checks their unit property by modular polynomial gcd. This inherited property applies to every subset defined by the new filter.

The d=4 comparison uses `max_k|c(ζ_k)|²=Σc_j²+sqrt(2)|c_0c_1+c_1c_2+c_2c_3−c_0c_3|`; its strict comparison is performed by integer squaring after checking the margin is positive. No floating-point spectral output is treated as a proof.

The general statements are established by the mathematical arguments above. Finite checks validate the implementation and displayed instances; they are not substitutes for those arguments.
