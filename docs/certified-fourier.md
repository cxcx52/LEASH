# Exact fixed-point Fourier predicate with an integer fallback

Date: 2026-11-14. Status: proved and independently reviewed; an optional reference implementation is included in this package. This changes the cost of evaluating the optional filtered challenge predicate; it does not change the challenge set, the strict threshold, or any of its established probability bounds. The ingredients are standard certified numerical approximation and exact linear algebra; no novelty claim is made.

Implementation: `src/labrador_repair/fourier.py`. Its fallback imports the independently checked integer SPD predicate from `labrador_repair.challenges`. The public entry point is `certified_operator_norm_below(coefficients, threshold, *, bits=40, with_path=False)`. There is no production CSPRNG, cryptographic prover, or challenge-sampling service in this prototype.

## 1. Exact statement and scope

Let d be a power of two at least two, and let c have d integer coefficients in {−2,−1,0,1,2}. Let A_c be its negacyclic multiplication matrix. For any positive integer T, the prototype returns true exactly when

    ||A_c||_(2→2) < T.

The fast path uses an exactly certified table of rational approximations to the relevant complex roots. All its decisions use integer arithmetic. When the enclosure cannot settle the strict comparison, it calls the exact predicate

    T² I − A_cᵀ A_c is positive definite,

implemented by Sylvester's criterion and fraction-free Bareiss elimination. Thus the fast path accepts exactly the same set as the previous implementation, including at equality boundaries.

The table is internal trusted state produced by `_build_certified_table`; the public function builds and caches it internally and takes no externally supplied table or numerical-certificate file. The immutable record documents the table's origin but is not an authentication mechanism for arbitrary Python objects.

The tested parameters are

    Q=2^40,   N=24 atan-series terms,
    P=2^80 for the outward pi enclosure,
    K=32 terms in each sine/cosine polynomial.

The construction validates the rational error inequality rather than assuming these values are adequate. A request with inadequate approximation precision raises an error.

## 2. A rational interval containing pi

For an integer a>1, use the alternating expansion

    atan(1/a) = Σ_(k≥0) (−1)^k / ((2k+1)a^(2k+1)).

The finite sum of N terms and that sum plus its next signed term bracket the exact value. The terms decrease to zero, so this is a rigorous alternating-series remainder bound. Define the resulting intervals [L_5,U_5] and [L_239,U_239]. Machin's identity gives the interval

    pi ∈ [16 L_5 − 4 U_239, 16 U_5 − 4 L_239].

For completeness, put a=atan(1/5), b=atan(1/239). The tangent double-angle formula gives tan(2a)=5/12 and tan(4a)=120/119. Therefore

    tan(4a−b)
      = (120/119−1/239)/(1+(120/119)(1/239))
      = 1.

The alternating-series lower bound gives `4a−b>4(1/5−1/(3·5³))−1/239>0`. The bound atan(x)<x gives `4a−b<4/5<1<pi/2`; the last inequality follows, for example, from `atan(1)=∫_0^1(1+x²)^(-1)dx>1/2`. The angle is consequently pi/4, establishing the chosen branch of Machin's identity.

To keep subsequent rational numerators and denominators short, round the rational lower endpoint down to a multiple of 1/P and the upper endpoint up to a multiple of 1/P. This preserves enclosure. Let the outward endpoints be L,U, their midpoint p=(L+U)/2, and their radius rho=(U−L)/2. The implementation checks `0<L<U<4`. This outward rounding is useful: directly taking high powers of the exact Machin denominators would enlarge the one-time computation without improving the final Q-bit enclosure.

For the specified constants the exact arithmetic check also verifies `U−L≤2^(−79)`. The proof of the final predicate uses the computed rational radius, not this displayed auxiliary bound.

## 3. Certified integer twiddles

Only 2d angles are required. For each m modulo 2d, select its representative in [−d,d−1] and let r=m/d. The target angle is r·pi and the rational evaluation point is x=r·p. Since |r|≤1,

    |x−r·pi|≤rho,       |x|<4.

Use the rational polynomials

    C_K(x)=Σ_(k=0)^(K−1) (−1)^k x^(2k)/(2k)!,
    S_K(x)=Σ_(k=0)^(K−1) (−1)^k x^(2k+1)/(2k+1)!.

Taylor's theorem, using the fact that all derivatives of sine/cosine have absolute value at most one, gives

    |cos(x)−C_K(x)| ≤ |x|^(2K)/(2K)!,
    |sin(x)−S_K(x)| ≤ |x|^(2K+1)/(2K+1)!.

For cosine use the Taylor polynomial through degree 2K−1, whose last odd coefficient is zero. For sine use the Taylor polynomial through degree 2K, whose last even coefficient is zero. This explains the two remainder exponents without an off-by-one assumption.

Sine and cosine are globally 1-Lipschitz. Consequently both approximations at the true target angle have error at most

    e_poly = rho + max(4^(2K)/(2K)!, 4^(2K+1)/(2K+1)!).

The constructor checks the exact rational inequality

    e_poly < 1/(2Q).

Round Q·C_K(x) and Q·S_K(x) to their nearest integers, with ties upward. Each rounding introduces at most 1/(2Q) of error after rescaling. If the stored integer pair is (C_m,S_m), it therefore satisfies

    |cos(m·pi/d)−C_m/Q| < 1/Q,
    |sin(m·pi/d)−S_m/Q| < 1/Q.                 (TWIDDLE)

For negative inputs, the integer formula `floor(y+1/2)` still has error at most one half; it does not rely on truncation toward zero. All Taylor terms, the outward enclosure, and this rounding are computed exactly with Python integers and `Fraction`.

## 4. From twiddles to a certified decision

The negacyclic matrix is unitarily diagonalized by evaluation at

    zeta_k=exp((2k+1)pi i/d),     k=0,...,d−1.

Thus `||A_c||op=max_k|c(zeta_k)|`. Since c is real, conjugate roots have equal magnitudes, so k=0,...,d/2−1 suffice.

For one such root, form integer dot products

    R_k=Σ_j c_j C_((2k+1)j mod 2d),
    I_k=Σ_j c_j S_((2k+1)j mod 2d),
    E=Σ_j |c_j|.

By (TWIDDLE), the true real and imaginary parts lie in the respective closed intervals

    [(R_k−E)/Q,(R_k+E)/Q],
    [(I_k−E)/Q,(I_k+E)/Q].

Using closed intervals is conservative even though each nonzero component approximation has a strict error bound. It also treats E=0 without a special limiting argument. Define integer bounds

    L_k=max(|R_k|−E,0)²+max(|I_k|−E,0)²,
    U_k=(|R_k|+E)²+(|I_k|+E)².

They obey

    L_k ≤ Q² |c(zeta_k)|² ≤ U_k.

The decision rules are therefore sound:

1. If any L_k≥T²Q², return false.
2. If every U_k<T²Q², return true.
3. Otherwise, return the exact integer SPD predicate.

Rule 1 has a non-strict comparison because the rejected event includes equality. Rule 2 must be strict. The two certified decisions cannot disagree on the same input because the true root magnitudes lie between their bounds. If neither rule decides, the exact fallback proves the claimed equivalence for every input. No empirical claim about the frequency of fallback is needed for correctness.

In particular, replacing the earlier exact predicate with this algorithm leaves `C_(64,31)={c:||A_c||op<31}` unchanged. The prior cardinality, unit-difference, strict acceptance-probability, and exact-uniform-conditioning statements therefore carry over verbatim.

## 5. Cost and remaining limitations

The table has 2d integer pairs and is computed once for a given d and chosen precision. The direct Fourier evaluation uses at most d²/2 coefficient/twiddle-pair scalings, or d² scalar integer multiplications, hence O(d²) integer operations. It is not an FFT implementation.

The worst case still invokes O(d³) exact SPD arithmetic after the O(d²) enclosure. This prototype establishes no worst-case O(d²) bound and no analytic small-fallback-probability claim. A fixed Q remains correct as d grows, but its width `E/Q≤2d/Q` can increase the frequency of fallback. Precision may be raised if desired; the constructor must then pass its correspondingly stronger error check.

If C is the cost of one raw candidate predicate and p is its acceptance probability, independent repetition has expected predicate cost E[C]/p, regardless of correlation between that candidate's cost and acceptance. This follows from the renewal identity `W=C+1_reject W'`, where W' is a fresh copy independent of the first candidate. At d64,T31, p>9/16, giving expected cost less than `(16/9)E[C]`, plus the one-time table construction. This identity does not supply a bound on fallback probability; E[C] must still include its exact cost. The prototype provides neither a production sampler nor a complete protocol implementation.

## 6. Reproducible checks

Run from the package root after installing the package:

    python -m unittest discover -s tests -v
    python examples/certified_fourier.py

The detailed historical counts below refer to the reviewed standalone research prototype. The package tests independently cover the same strict spectral formulas, low-precision ambiguity, negative rounding and equality boundaries. The example checks a deterministic d64 batch against the integer reference; it makes no timing or acceptance-probability claim.

All decisions use integer/rational arithmetic. Floating-point values appear only in elapsed-time measurements from `perf_counter`.

The completed checks are:

- All 25 d2 coefficient vectors at all positive integer thresholds 1,...,5: 125 comparisons with exact SPD and the independent formula `c0²+c1²<T²`.
- All 625 d4 coefficient vectors at thresholds 1,...,9: 5625 comparisons with exact SPD and the independent formula `Σc_j²+sqrt(2)|c0c1+c1c2+c2c3−c0c3|<T²`, compared by exact integer squaring after a positive-margin check.
- These ranges include every relevant positive integer threshold through 2d+1. Larger thresholds always accept because `||A_c||op≤Σ|c_j|≤2d`.
- Six explicit equality cases (constant 1 at T1 and constant 2 at T2, for d2,d4,d64) take the fallback and reject.
- The exhaustive small-degree comparisons exercise 3886 interval accepts, 1824 interval rejects, and 40 exact fallbacks.
- An inadequate Taylor-precision request rejects, and invalid coefficient types/ranges or mismatched dimensions reject.
- 128 seeded d64 inputs at T31 and 48 additional comparisons on the first 16 inputs at T16,T24,T40 all agree with exact SPD.

The seed is 20261114, using Python's `random.Random` solely to define reproducible test inputs. No cryptographic randomness property is assumed. Finite comparisons validate the implementation; the preceding interval proof is what establishes correctness for all inputs.

## 7. Historical standalone-reference timing

This is one local observation on 2026-11-14, without CPU pinning, repeated-trial confidence intervals, or a claim that timings generalize to other machines. Hardware: 13th Gen Intel Core i9-13980HX, 24 physical cores, 32 logical processors. The prototype executes the loops serially. Environment: Windows 11 build 26300, AMD64, CPython 3.12.10, MSC v.1943 64 bit.

| Quantity | Observed value |
|---|---:|
| d2 table construction | 0.005303 s |
| d4 table construction | 0.012840 s |
| d64 table construction | 0.246290 s |
| Exact SPD on 128 seeded d64,T31 inputs | 6.202563 s |
| Certified Fourier plus any fallback on the same inputs | 0.042086 s |
| Observed speed ratio excluding table construction | 147.38 |
| Interval accepts / interval rejects / fallbacks in that batch | 127 / 1 / 0 |

Including the d64 table construction, this batch took approximately 0.288376 s for the new path. The baseline is the standalone exact SPD reference, not a separately optimized linear-algebra implementation. The measured acceptance and fallback counts are descriptive performance data and are not estimates substituted for the proven acceptance/cardinality bounds. No proof-size, end-to-end protocol speed, or security claim follows from this timing comparison.
