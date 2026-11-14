# A challenge family with exact cardinality

Let d>=2 be a power of two and define C as all degree-<d polynomials whose coefficients lie in `{-2,-1,0,1,2}`. For q>4 these polynomials are distinct modulo q. Uniform independent sampling of each coefficient is uniform on C, and

\[
|C|=5^d,\qquad \|c\|_2\le2\sqrt d,\qquad \|c\|_{op}\le\|c\|_1\le2d.
\]

The operator norm is that of integer negacyclic multiplication on Euclidean coefficient space. Each monomial acts as a signed permutation, so the triangle inequality proves the last bound. These are deterministic bounds, not typical-value estimates.

Assume q is prime, q=5 mod 8, and q>32. For distinct c,c' in C, the integer representative of their difference has infinity norm at most 4. [Lyubashevsky and Seiler, Short, Invertible Elements, Corollary 1.2](https://eprint.iacr.org/2017/523) with splitting parameter k=2 shows that `X^d+1` has two irreducible factors and that every nonzero polynomial of infinity norm less than `sqrt(q/2)` is a unit. Since q>32, every c-c' is invertible.

For d=64 this gives exactly `5^64` challenges (about 148.603 bits), operator bound T=128, and squared Euclidean bound 256. The example q=4294967197 is prime and 5 mod 8. The code verifies these parameter conditions and exhaustively checks all 6560 nonzero coefficient differences for d=4,q=101 as a finite regression test; the general statement follows from the cited theorem.

## Consequences and costs

For a nonzero polynomial of total degree t, evaluation on independent uniform elements of C has zero probability at most `t/|C|`. To see the ring version, first prove the univariate root bound by successive factorization: each difference of two sampled roots is a unit, so a nonzero leading coefficient cannot support more roots than the degree. The usual induction on the number of variables then gives the multivariate bound. No assumption that R_q itself is a field is needed.

This choice repairs the missing exact cardinality guarantee conservatively. It increases T from the original filtered target 15 to 128. All commitment-binding norms depending on T, the decomposition parameters, ranks, and proof sizes must therefore be recomputed. No claim of preserving the reported concrete efficiency follows from this family.

An [optional certified filtered family](certified-filtered-challenges.md) reduces the strict operator threshold to 31 at d=64 and proves that more than `(9/16)*5^64` challenges remain. It has an exact integer membership predicate and retains unit differences under the same modulus hypotheses. Its cardinality bound and conditioned distribution are analyzed separately; the unfiltered API retains the values above.

The helper `statistical_budget` evaluates only

\[
\delta_{JL}+q^{-m}+q^{-d/2}+2/|C|,
\]

under the hypotheses of the repaired main-protocol algebra. It excludes computational binding losses, retries, final-round variants, composition losses, and Fiat-Shamir. The minimal m for `q^m>=2^160` is computed by integer multiplication; for the example q slightly below 2^32 it is **6, not 5**.
