# Independent review of the certified Fourier predicate

Date: 2026-11-14. Reviewer task: independently check the interval proof, exact decision boundaries, reference code, finite checks, and the limited cost claim. This review does not assess a cryptographic sampler, a complete prover, or the original paper's optimized floating-point implementation.

**Verdict:** the stated exact equivalence is correct under its explicit trusted-table precondition. No mathematical or implementation blocker was found. The fast path and the integer fallback decide the same strict operator-norm predicate for every permitted input. The finite tests below independently exercise low precision, ambiguity, and equality; correctness for arbitrary inputs follows from the reviewed interval argument.

Reviewed source versions:

| File | SHA-256 |
|---|---|
| `proofs/certified_fourier_predicate.md` | `fcd9d6da5a687a5c893d0a033e2e56e8ac2cb341d6e52c017dcff1c869515ab8` |
| `scripts/certified_fourier_predicate.py` | `375b2ea1bc82133bea86efbed485b6f835b0c29c6acf905924543ff63bbed16e` |

The additional arithmetic checks are in [certified_fourier_peer_checks.py](../scripts/certified_fourier_peer_checks.py). This review also re-ran the source's own checks. Recorded outputs are [certified_fourier_peer_run.json](../notes/parameter-results/certified_fourier_peer_run.json) and [certified_fourier_peer_extra.json](../notes/parameter-results/certified_fourier_peer_extra.json).

## 1. Machin interval and the angle branch

For a>1 the magnitudes 1/((2k+1)a^(2k+1)) strictly decrease to zero. Therefore the N-term arctangent partial sum and that partial sum plus its next signed term bracket atan(1/a). The code's `min`/`max` construction works for both parities of N; it does not presume that the N-term sum is the upper endpoint.

If a=atan(1/5) and b=atan(1/239), exact tangent formulas give tan(2a)=5/12, tan(4a)=120/119 and tan(4a-b)=1. The proof checks the necessary branch: 4a-b>4(1/5-1/(3*5^3))-1/239>0, while 4a-b<4/5<1<pi/2. Thus 4a-b=pi/4, not merely equality modulo pi. The last bound follows from atan(1)>1/2, so the argument does not assume a numerical approximation to pi.

Multiplication of the b interval by -4 reverses its endpoints. The code correctly uses

    lower=16*lo5-4*hi239,
    upper=16*hi5-4*lo239.

For P=2^pi_bits, integer floor of P*lower and integer ceiling of P*upper enclose the original interval. The ceiling expression `-((-upper.numerator*P)//upper.denominator)` is correct, including the general signed-floor convention. The subsequent exact checks establish positive endpoints below 4. The default width check <=2^-79 was reproduced.

The added tests compare twenty low-term/low-dyadic intervals with strictly finer constructions and verify nesting. These tests support the code path; the alternating-series and directed-rounding argument establishes enclosure generally.

## 2. Taylor remainder and nearest-integer quantization

The cosine polynomial uses powers through 2K-2. It is also the Taylor polynomial through degree 2K-1, since the final odd coefficient vanishes; the remainder is bounded by |x|^(2K)/(2K)!. The sine polynomial uses powers through 2K-1 and is also the Taylor polynomial through degree 2K, giving |x|^(2K+1)/(2K+1)!. Thus neither exponent is one degree too optimistic. The iterative coefficient updates in `_taylor_sin_cos` match these polynomials.

Taking m in [-d,d-1] gives |m/d|<=1 and |x|<4. Each trigonometric function is 1-Lipschitz, so the pi-midpoint substitution contributes at most the computed interval radius rho. The uniform exact bound

    rho+max(4^(2K)/(2K)!,4^(2K+1)/(2K+1)!) < 1/(2Q)

is sufficient for both components and is checked before the table is constructed. It remains sufficient for every allowed degree; large degree can affect interval tightness later but does not invalidate the twiddle certificate.

The nearest-integer expression is floor(y+1/2), with error at most one half for positive and negative y alike. Consequently the final component error is strictly below 1/Q. The extra test suite verifies 9,624 rational cases, including negative half-integer ties, and the source rejects deliberately insufficient Taylor precision. These checks exposed no sign, parity, or truncation error.

## 3. Root coverage and interval decision rules

The real negacyclic multiplication matrix is normal and is unitarily diagonalized by evaluation at the odd 2d-th roots. Its Euclidean operator norm is exactly the maximum modulus of those evaluations. For real coefficients, conjugate evaluations have equal modulus. The code's indices k=0,...,d/2-1 cover roots of angles in (0,pi), one from each conjugate pair. Thus the half-root loop omits no potentially maximal magnitude.

For E=sum_j |c_j|, the certified twiddles give component errors at most E/Q. The closed intervals with endpoints (R-E)/Q and (R+E)/Q, and similarly for I, are valid even though the individual nonzero errors are strict. The zero polynomial has E=0 and is handled directly: every upper square is zero and the positive threshold is accepted.

The minimum absolute coordinate in the real interval is max(|R|-E,0); its maximum is |R|+E. Summing the squared real and imaginary bounds yields

    L_k <= Q^2 |c(zeta_k)|^2 <= U_k.

There is no need to assume that the real and imaginary errors are independent or that the corners of the enclosing rectangle are attained.

The implemented inequalities have the correct orientation:

- `lower_squared >= threshold_squared` certifies rejection, including equality.
- `upper_squared < threshold_squared` is required at every root for acceptance.
- Every unresolved input goes to the exact strict SPD predicate.

In particular, replacing the upper acceptance comparison by a non-strict comparison would be unsound for the intended set; the implementation does not do that. The source's six constant equality cases all took the fallback and rejected. The independent tests add 376 signed monomials at all positions for d=2,4,8,16,64. Their norms equal their coefficient magnitudes exactly, and all were rejected at equality.

## 4. Exact fallback and trusted state

The fallback forms the symmetric integer matrix T^2 I-A_c^T A_c. This matrix is positive definite exactly when every singular value of A_c is strictly below T. Its fraction-free elimination computes leading principal determinants, dividing only by the preceding nonzero determinant. Every positive-definite input has all those determinants positive by Sylvester's criterion. A nonpositive encountered pivot is a valid rejection, and equality at the spectral boundary cannot pass.

The in-place implementation does not overwrite a pivot-row or pivot-column value before it has been used in the relevant trailing update. Exact divisions are asserted. This review found no fallback mismatch in the enlarged test set.

The public-looking dataclass is not a verifiable certificate format: a caller can manually create an object with false twiddles. The proof and function documentation explicitly require tables produced by `build_certified_table`, and the document explicitly says arbitrary externally supplied tables are not authenticated or validated. Under that precondition there is no gap. Any future API accepting untrusted serialized tables would need to reconstruct or independently validate them; a frozen dataclass alone would not suffice.

## 5. Independent finite checks

The source's default run reproduced all stated decision counts:

| Check | Result |
|---|---:|
| All d2 vectors at T=1,...,5 | 125 matches |
| All d4 vectors at T=1,...,9 | 5625 matches |
| Small-degree interval accepts / rejects / fallbacks | 3886 / 1824 / 40 |
| Explicit constant equality fallbacks | 6 rejects |
| Seeded d64,T31 comparisons | 128 matches |
| First 16 d64 samples at T16,T24,T40 | 48 matches |
| d64,T31 fast-path counts | 127 accepts / 1 reject / 0 fallbacks |

The d4 closed formula was independently checked algebraically. Writing S=sum c_j^2 and X=c0*c1+c1*c2+c2*c3-c0*c3, the largest squared magnitude is S+sqrt(2)|X|. The exact comparison is therefore `margin>0 and margin^2>2X^2`, where margin=T^2-S. The positive-margin test is necessary before squaring and is present.

The additional suite changes Q from 2^40 to deliberately coarse values, forcing the fallback on many inputs. It compares every d4 coefficient vector and every threshold 1,...,9 with the closed formula:

| Q | Cases | Interval accepts | Interval rejects | Exact fallbacks |
|---:|---:|---:|---:|---:|
| 2 | 5625 | 2073 | 68 | 3484 |
| 4 | 5625 | 2745 | 1024 | 1856 |
| 16 | 5625 | 3649 | 1544 | 432 |
| 256 | 5625 | 3801 | 1792 | 32 |

All 22,500 comparisons passed. This is useful coverage of the entire composed predicate, rather than only its high-precision fast path. The 376 equality cases, 9,624 nearest-rounding cases, twenty pi interval comparisons, and zero-polynomial cases also passed.

## 6. Cost statements and empirical limits

The asymptotic description is correct as an arithmetic-operation count: table size is O(d), direct evaluation O(d^2), and an unresolved input can incur O(d^3) exact elimination. Integer bit complexity must also account for operand growth; no constant-cost machine-integer assertion or worst-case quadratic bound is justified.

One wording clarification is advisable. There are d^2/2 coefficient/twiddle-pair scalings in the full loop, but each pair uses two scalar integer multiplications, for at most d^2 scalar products. Describing them as complex or pair scalings avoids reading d^2/2 as the count of scalar integer multiplications. The O(d^2) conclusion is unchanged.

The renewal formula E[total predicate work]=E[candidate work]/p is correct for independent identically distributed fresh candidates with finite expected candidate work and p>0. It does not require independence between an individual candidate's cost and its accept/reject outcome. The document correctly includes fallback work in the expectation and table construction as a one-time cost.

The hardware description was independently confirmed: Intel Core i9-13980HX, 24 physical cores, 32 logical processors, Windows build 26300; the Python version and architecture match the source report. The review's own run took 6.2757823 seconds for exact SPD on the 128 seeded inputs, 0.0398822 seconds for the Fourier-plus-fallback path, and 0.2634562 seconds for the d64 table. Its observed ratio excluding table construction was about 157.36, rather than the earlier run's 147.38. This normal timing variation is consistent with the document's explicit one-run, machine-specific framing; exact historical wall-clock values are not mathematical constants.

These measurements compare two Python reference predicates on the same finite input batch. They neither measure the original paper's C/FFT implementation nor establish a cryptographic sampler's throughput, a small fallback probability, or an end-to-end protocol speedup. The document expressly preserves these limitations. No stronger performance claim should be inferred when integrating the reference.

## 7. Integration conclusion

The predicate can replace the previously checked exact SPD predicate without altering the strictly filtered challenge set, provided its table is constructed by the certified builder and the exact fallback is retained. Consequently existing cardinality and covariance statements for that same set remain applicable. This review recommends acceptance of the mathematical reference implementation, with the scalar-product wording clarified; production engineering and protocol-level cost claims remain separate tasks.
