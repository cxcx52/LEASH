# A parameterized modular projection family

The [1024-row modular projection theorem](modular-jl.md) gives a fixed error bound. This document specifies an integer parameter family and proves, for every integer $\lambda\ge128$, a projection error smaller than $2^{-(\lambda+32)}$. The proof uses three fixed rational certificates and inequalities valid at every scale. It does not rely on checking a finite list of security parameters.

We use $J$ for the projection row count and $H$ for the honest squared-norm threshold multiplier. These symbols are separate from a protocol's aggregation repetition count and challenge operator-norm bound.

## Integer parameters

For an integer $\lambda\ge128$, define

$$
k=\left\lceil\frac{\lambda+32}{164}\right\rceil,
\qquad n=\lceil\sqrt{k}\rceil.
$$

Set

| Parameter | Value | Meaning |
| --- | --- | --- |
| $J$ | $1024k$ | Projection row count |
| $\alpha$ | $120k$ | Small-projection squared-norm multiplier |
| $H$ | $552k$ | Honest acceptance squared-norm multiplier |
| $A$ | $12n$ | Small-norm case cutoff $q/A$ |
| $C$ | $72n$ | Large-coordinate case cutoff $q/C$ |
| $K$ | $250n^2$ | Modulus condition $b\le q/K$ |

The square-root ceiling can be computed exactly as $n=1+\operatorname{isqrt}(k-1)$. For all positive integers $k$,

$$
k\le n^2\le2k.
\tag{1}
$$

The lower inequality is immediate. For the upper inequality, the integer $k$ satisfies $k\ge(n-1)^2+1$, so

$$
2k\ge2(n-1)^2+2=n^2+(n-2)^2\ge n^2.
$$

Consequently, $J,\alpha,H,K=O(\lambda)$ and $A,C=O(\sqrt\lambda)$. In particular, $250k\le K\le500k$. At $\lambda=128$, the parameters are exactly the original replacement profile $(J,\alpha,H,A,C,K)=(1024,120,552,12,72,250)$.

## Uniform family theorem

Let $\chi$ have probabilities $\Pr(0)=1/2$ and $\Pr(1)=\Pr(-1)=1/4$. As in [the fixed-parameter proof](modular-jl.md), $|x|_q$ denotes the distance from $x$ to $q\mathbb Z$, and the modular vector norm is the Euclidean norm of these coordinate distances.

**Theorem.** For every integer $\lambda\ge128$, use the parameters above. Let $q,D$ be positive integers, let $0<b\le q/K$, and fix a vector $w\in\mathbb Z^D$ satisfying

$$
|w_i|\le q/2\quad\text{for every }i,
\qquad \|w\|_2\ge b.
$$

Sample $\Pi\in\{-1,0,1\}^{J\times D}$ with mutually independent entries distributed as $\chi$. Then

$$
\Pr\left(\|\Pi w\bmod q\|_2^2\le\alpha b^2\right)
<2^{-164k}\le2^{-(\lambda+32)}.
\tag{2}
$$

The vector may depend on $\lambda$ but must be fixed before the projection matrix for that parameter is sampled. The event includes equality. No primality or ring-factorization condition on $q$ is needed for this projection theorem.

## Fixed certificates

The moment calculation and exponential estimates in [modular-jl.md](modular-jl.md) give, for any nonzero vector $u$ and one projection row $\pi$,

$$
\mathbb E\exp\left(-\frac{\langle\pi,u\rangle^2}{2\|u\|_2^2}\right)
\le\frac{27}{32},
\qquad
\Pr(|\langle\pi,u\rangle|\ge t)
\le2e^{-t^2/\|u\|_2^2}.
\tag{3}
$$

We reuse these three rational certificates:

$$
\begin{aligned}
a_0&=\left(\frac{87}{32}\right)^{60}
       \left(\frac{27}{32}\right)^{1024},\\
c_0&=2048\left(\frac{60}{163}\right)^{131},\\
U&=a_0+c_0<2^{-164};
\end{aligned}
\tag{4}
$$

$$
V=2^{-1024}\sum_{j=0}^{39}\binom{1024}{j}<2^{-788},
\qquad
W=\left(\frac{736}{1000}\right)^{1024}<2^{-452}.
\tag{5}
$$

All three are independent of $\lambda$. They use the elementary bounds

$$
\frac{163}{60}<e<\frac{87}{32},
\qquad \pi>\frac{157}{50},
\qquad \sqrt{120}<11,
\qquad 144(239/250)^2>131.
$$

Taylor-series and Machin-identity certificates for these constants are given in the fixed-parameter proof and checked by [`jl_certificate()`](../src/labrador_repair/bounds.py). The analytic input for the spread-vector case is the general independent-summand Berry–Esseen inequality with constant $0.56$. This is a conservative enlargement of the general constant $0.5583$ reported by [Shevtsova (2013)](https://www.mathnet.ru/eng/ia252); it is applicable to the weighted, not necessarily identically distributed, summands used here.

## Proof: the three cases at every scale

### Case 1: $\|w\|_2<q/(12n)$

The unmodded small-norm event is bounded using (3) and independent rows:

$$
\Pr(\|\Pi w\|_2^2\le\alpha b^2)
\le e^{\alpha/2}(27/32)^J
=e^{60k}(27/32)^{1024k}
<a_0^k.
\tag{6}
$$

For a wrap compatible with the small-residue event, some unmodded coordinate has absolute value at least $q-\sqrt\alpha b$. Write

$$
r=\frac{\sqrt\alpha}{K}
=\frac{\sqrt{120}\sqrt{k}}{250n^2},
\qquad r_0=\frac{\sqrt{120}}{250}.
$$

Since $n^2\ge k\ge1$, we have $r\le r_0/\sqrt{k}\le r_0$. Hence

$$
A^2(1-r)^2
=144n^2(1-r)^2
\ge144k(1-r_0)^2>131k.
$$

The union bound over $J=1024k$ rows and the tail in (3) therefore bound the wrap contribution by

$$
2048k e^{-131k}
<2048k\left(\frac{60}{163}\right)^{131k}
\le c_0^k.
\tag{7}
$$

The last inequality follows from $k\le2^{k-1}\le2048^{k-1}$ for every positive integer $k$. The first inequality in this elementary sequence follows by induction: it holds at $k=1$, and $k+1\le2k$ for $k\ge1$ supplies the induction step.

Thus the union factor growing with $k$ is explicitly absorbed. Combining (6) and (7) yields

$$
\Pr(\|\Pi w\bmod q\|_2^2\le\alpha b^2)
<a_0^k+c_0^k
\le(a_0+c_0)^k
=U^k<2^{-164k}.
\tag{8}
$$

### Case 2: $\|w\|_\infty\ge q/(72n)$

Condition on all but one large coordinate of a row. The circular open-arc argument in [modular-jl.md](modular-jl.md) applies with arc length $q/C$ and proves

$$
\Pr\left(|\langle\pi,w\rangle|_q\ge\frac{q}{2C}\right)\ge\frac12.
$$

The counted-row condition is $\ge$. This preserves the endpoint argument, including when $q/(2C)$ is an integer.

The closed target event allows at most

$$
\left\lfloor\frac{4\alpha C^2}{K^2}\right\rfloor
=\left\lfloor\frac{124416}{3125}\frac{k}{n^2}\right\rfloor
\le39
\tag{9}
$$

counted rows. Consequently its probability is at most
$\Pr(\operatorname{Bin}(1024k,1/2)\le39)$.

Partition the $1024k$ independent fair Bernoulli variables into $k$ independent blocks of length 1024. If their total sum is at most 39, each block's sum is at most 39. Therefore

$$
\Pr(\operatorname{Bin}(1024k,1/2)\le39)
\le V^k<2^{-788k}<2^{-164k}.
\tag{10}
$$

This block-event inclusion proves the estimate uniformly, without approximating a growing binomial sum.

### Case 3: the remaining vectors

Now $\|w\|_2\ge q/(12n)$ and $\|w\|_\infty<q/(72n)$. Deleting coordinates until the norm first falls below $q/(12n)$ gives a vector $v$ satisfying

$$
\frac{\sqrt{35}\,q}{72n}<\|v\|_2<\frac q{12n},
\qquad \|v\|_\infty<\frac q{72n}.
$$

Its support is disjoint from that of $w-v$. Splitting each ternary variable into two independent Rademacher variables gives the same Berry–Esseen discrepancy as in the fixed-parameter proof:

$$
\delta_{\mathrm{BE}}
\le\frac{0.56}{\sqrt2}\frac{\|v\|_\infty}{\|v\|_2}
<\frac{0.56}{\sqrt{70}}.
$$

Condition on the independent remaining projection. The normal density contribution for a modular interval of radius $\sqrt\alpha b$ is at most

$$
\frac{2\sqrt\alpha}{K\sqrt\pi\,[\sqrt{35}/(72n)]}
=\frac{144\sqrt{120}}{250\sqrt{35\pi}}\frac{\sqrt{k}}n
\le\frac{144\sqrt{120}}{250\sqrt{35\pi}}.
$$

The finite-interval complement argument requires two tails: the unmodded projection outside the centered interval and the comparison normal variable outside that interval. Their sum is at most $4e^{-36n^2}\le4e^{-36}$. Both the closed interval and two-boundary-interval cases are covered by the CDF argument in [modular-jl.md](modular-jl.md).

Thus every row has conditional, and hence unconditional, small-residue probability at most

$$
p_k\le\frac{144\sqrt{120}}{250\sqrt{35\pi}}
+\frac{1.12}{\sqrt{70}}+4e^{-36}
<\frac{736}{1000}.
$$

Since the target vector event requires every row to have a sufficiently small residue and rows are independent,

$$
\Pr(\|\Pi w\bmod q\|_2^2\le\alpha b^2)
\le p_k^{1024k}<W^k<2^{-452k}<2^{-164k}.
\tag{11}
$$

The cases exhaust the fixed vector. Their maximum bound is smaller than $2^{-164k}$, and $164k\ge\lambda+32$ proves (2).

## Completeness, constant slack, and the modulus

For $\beta>0$, fix an honest vector $w$ with $\|w\|_2\le\beta$ and use the closed acceptance threshold

$$
\|\Pi w\bmod q\|_2^2\le H\beta^2=552k\beta^2.
$$

For the unmodded squared projection norm $S$, the exact moments give

$$
\mathbb ES\le512k\beta^2,
\qquad \operatorname{Var}(S)\le512k\beta^4.
$$

Centered modular reduction cannot increase this norm. Cantelli's inequality, applied with excess $40k\beta^2$, therefore gives

$$
\Pr(\text{reject})
\le\frac{512k}{512k+(40k)^2}
=\frac8{8+25k},
\qquad
\Pr(\text{accept})\ge\frac{25k}{8+25k}\ge\frac{25}{33}.
\tag{12}
$$

If $\beta=0$, the honest vector is zero and is accepted with probability one. This trivial completeness case does not invoke the projection theorem, which assumes $b>0$.

For every scale, $H/\alpha=23/5$. The compatible soundness threshold and modulus condition are therefore

$$
b=\sqrt{\frac{23}{5}}\,\beta,
\qquad
\sqrt{\frac{23}{5}}\,\beta\le\frac{q}{250n^2}.
\tag{13}
$$

The norm slack is constant. By (1), the modulus lower bound at a fixed positive $\beta$ grows linearly in $k$, within a factor of two from the square-root ceiling. Equation (12) describes a single independently sampled attempt; retries and challenge derivation belong to the protocol analysis.

## Negligibility and its scope

A fixed constant such as $2^{-164}$ is not a negligible function of a growing security parameter. This family instead specifies parameters at every integer $\lambda\ge128$ and proves

$$
\delta_{\mathrm{JL}}(\lambda)<2^{-(\lambda+32)}.
$$

Hence $\lambda^c\delta_{\mathrm{JL}}(\lambda)\to0$ for every fixed positive integer $c$. This is a negligible bound for the fixed-vector projection event in (2).

To obtain a full protocol family, other contributions must also be parameterized: challenge-set errors, aggregation errors, recursion depth, computational binding and extraction losses, and any Fiat–Shamir reduction. For example, leaving a challenge set of size $5^{64}$ fixed leaves the term $2/5^{64}$ constant. This JL family alone does not address that term or certify a lattice hardness estimate.

## Implementation and checks

[`jl_security_profile(security_bits)`](../src/labrador_repair/bounds.py) accepts integers at least 128 and returns exact integer parameters and rational probability bounds. It reuses `jl_certificate()` for the three base certificates. Its `uniform_failure_bound` is $2^{-164k}$; the mathematical theorem gives a strict inequality below this bound.

| Field | Quantity |
| --- | --- |
| `projection_rows_J` | $1024k$ |
| `bad_projection_squared_multiplier_alpha` | $120k$ |
| `honest_projection_squared_multiplier_H` | $552k$ |
| `modulus_cutoff_denominator_K` | $250n^2$ |
| `uniform_failure_bound` | $2^{-164k}$ |
| `honest_acceptance_lower` | $25k/(8+25k)$ |
| `slack_squared` | $23/5$ |

The tests exercise both sides of the security-bit ceiling and perfect-square boundaries, check the exact case-count and density ratios, and recompute the Cantelli expression from the generated parameters. These checks validate parameter generation; the inequalities above establish the statement for all $\lambda$.

[`examples/certify.py`](../examples/certify.py) displays the profiles for $\lambda=128,256,512$. All decisions use integers or rational numbers. Displayed logarithms are informational.
