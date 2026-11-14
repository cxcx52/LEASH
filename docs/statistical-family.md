# A statistical parameter family for the ordinary main protocol

This note parameterizes the statistical part of (MAIN) in [the ordinary-main extraction argument](unknown-gap-extraction.md):

$$
\delta_{\mathrm{main}}
\le\delta_{\mathrm{JL}}+q^{-m}+q^{-d/2}+\frac{r+2}{5^d}.
\tag{1}
$$

The computational reduction terms in (MAIN) are additional and are not absorbed into the estimates below. This note proves the statistical parameter accounting; it does not certify Module-SIS hardness.

## Parameters and required conditions

Let $\lambda\ge128$ be an integer, and let $r=r(\lambda)\ge1$ be an integer bounded by a polynomial in $\lambda$. Put

$$
L=\lambda+32,
\qquad h=\lceil\log_2(r+2)\rceil,
\qquad d=2^{\lceil\log_2(L+h)\rceil}.
\tag{2}
$$

Thus $d$ is the smallest power of two at least $L+h$. Choose a prime $q$ with $q\equiv5\pmod8$ and $q>32$, and set

$$
m=\min\{j\in\mathbb Z_{\ge1}:q^j\ge2^L\}.
\tag{3}
$$

Here $m$ is the scalar aggregation repetition count. The projection uses the independent notation $J$ for its rows and $H$ for its honest threshold multiplier.

Use the [JL security family](jl-security-family.md):

$$
k=\lceil L/164\rceil,\quad n=\lceil\sqrt{k}\rceil,
\quad J=1024k,\quad\alpha=120k,\quad H=552k,\quad K=250n^2.
$$

For a positive honest norm parameter $\beta$, the projection acceptance threshold is $H\beta^2$, and its soundness premise requires

$$
b=\sqrt{23/5}\,\beta\le q/K,
\quad\text{equivalently}\quad
K^2(23/5)\beta^2\le q^2.
\tag{4}
$$

The fixed-vector independence and centered-representative hypotheses of that JL theorem remain required. The case $\beta=0$ gives trivial honest completeness; it is not an application of the JL theorem's $b>0$ soundness premise.

For the optional [affine reduction](affine-r1cs.md), separately impose its centered integer-lifting condition. If $M$ is its packed witness length and $\beta_{\mathrm{aff}}$ its applicable norm bound, the sufficient condition is

$$
\sqrt{Md/2}\,\beta_{\mathrm{aff}}+\beta_{\mathrm{aff}}^2/2<q/2.
\tag{5}
$$

The two norm parameters must not be identified unless the reduction establishes that identification. Other commitment and extraction hypotheses are unchanged obligations.

## Ordinary-main budget

Let $\epsilon_0=2^{-L}$. Each term in (1) is bounded as follows.

1. The uniform JL family proves $\delta_{\mathrm{JL}}<2^{-164k}\le\epsilon_0$.
2. Definition (3) gives $q^{-m}\le\epsilon_0$ exactly.
3. Since $q>32>4$ and $d\ge L$, we have $q^{-d/2}<4^{-d/2}=2^{-d}\le\epsilon_0$. The exponent $d/2$ is an integer.
4. By $r+2\le2^h$ and $d\ge L+h$,
   $$
   \frac{r+2}{5^d}\le\frac{2^h}{2^d}
   =2^{h-d}\le2^{-L}=\epsilon_0.
   $$

Therefore the right-hand side of (1) is strictly smaller than

$$
4\epsilon_0=2^{-(\lambda+30)}.
\tag{6}
$$

Strictness already follows from the JL term. Increasing $d$ is essential to this family: keeping $d=64$ fixed would leave $(r+2)/5^{64}$ non-negligible as a function of $\lambda$.

The cube challenge set consists of all degree-less-than-$d$ coefficient vectors in $\{-2,-1,0,1,2\}^d$ and has exactly $5^d$ elements. The ring choice $d$ a power of two, $q\equiv5\pmod8$, $q>32$ is compatible with the separately established factorization and invertible-difference conditions; (6) concerns the statistical expression once those conditions are supplied.

## Optional affine contribution

Let the source arithmetic modulus be $N_{\mathrm{source}}=2^d+1$, and let $p$ be its smallest prime divisor. This integer is odd and greater than one, so $p\ge3$; its factorization is not needed for the following conservative estimate. Set the affine repetition count to

$$
\ell=L=\lambda+32.
$$

If the affine reduction contributes at most $2p^{-\ell}$, then

$$
2p^{-\ell}\le2\cdot2^{-L}=2\epsilon_0
=2^{-(\lambda+31)}.
$$

Adding this contribution to (6) gives

$$
\delta_{\mathrm{main}}+2p^{-\ell}
<6\cdot2^{-(\lambda+32)}
<2^{-(\lambda+29)}.
\tag{7}
$$

Equation (7) is an arithmetic sum of the stated contributions. A composition theorem must justify using that sum for a composed protocol.

## Parameter size and polynomial dependence

Because $r$ is polynomially bounded, $h=O(\log\lambda)$. From $L+h\le d<2(L+h)$, we obtain $d=O(\lambda)$. The JL family gives $J,H,\alpha,K=O(\lambda)$, and $\ell=O(\lambda)$. Also, $q>32$ implies

$$
m\le\lceil L/5\rceil=O(\lambda).
$$

Choose $q=q(\lambda)$ with polynomial bit length while satisfying (4), and (5) when applicable. Require explicit binary rational descriptions of the squared norm bounds and binary descriptions of source dimension counts to have polynomial bit length; any ranks or witness lengths included in a running-time claim must likewise have the stated polynomial bounds. These are explicit size conditions: the phrase “a sufficiently large prime” alone does not rule out unnecessarily large bit lengths. This note does not claim a deterministic polynomial-time prime-search algorithm.

Under these conditions, the relevant integers have polynomial bit length. In particular, $N_{\mathrm{source}}$ has bit length $d+1$, and $5^d$ has bit length $O(d)$ despite their exponential numerical values. Minimality of $m$ gives $q^m<q2^L$, so this aggregation denominator has bit length at most $L+O(\log q)$. The CRT denominator $q^{d/2}$ has bit length $O(d\log q)$.

Thus the statistical budgets in (6) and (7) are negligible functions of $\lambda$ under an explicit parameter family, and their arithmetic descriptions remain polynomial in size. No lattice hardness level, proof-size estimate, optimized-final-round guarantee, or Fiat–Shamir claim follows from this accounting alone.

The example [statistical_family.py](../examples/statistical_family.py) verifies exact arithmetic at security parameters 128, 256, and 512, using the package parameter and ring-checking functions. Its fixed example modulus is not a specification for every security parameter. The example uses `beta_squared=1` only to check the JL modulus condition. It does not supply an affine witness dimension or affine norm bound and therefore does not check condition (5). The inequalities above prove the all-$\lambda$ statement.
