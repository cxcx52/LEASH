# A rigorous modular projection bound

This document proves a replacement projection lemma with 1024 rows, together with an honest-prover acceptance bound. Its starting point is the distribution and three-case argument in Lemma 4.2 and Appendix A of [LaBRADOR, ePrint 2022/1341](https://eprint.iacr.org/2022/1341). The parameters here differ from the original 256-row construction. The resulting probability bounds concern a fixed vector sampled independently of the projection matrix.

The proof uses exact moment calculations, exponential bounds, and a general independent-summand Berry–Esseen theorem. The finite numerical comparisons are certified by `family_constants_certificate()` in [`jl_family_checks.py`](../scripts/jl_family_checks.py). This is a mathematical replacement lemma; its use in a full protocol additionally requires the appropriate binding, extraction, composition, and challenge-sampling arguments.

## Notation and theorem

For a positive integer $q$, write

$$
|x|_q=\min_{k\in\mathbb Z}|x-kq|,
\qquad
\|z\bmod q\|_2^2=\sum_j |z_j|_q^2.
$$

The choice between the two centered representatives at an even-modulus endpoint does not affect this norm. Let $\chi$ have distribution

$$
\Pr(\chi=0)=\frac12,
\qquad
\Pr(\chi=1)=\Pr(\chi=-1)=\frac14.
$$

**Theorem 1 (1024-row modular projection).** Let $q,D$ be positive integers and let $0<b\le q/250$. Fix $w\in\mathbb Z^D$ with $|w_i|\le q/2$ for every $i$ and $\|w\|_2\ge b$. Sample a matrix $\Pi\in\{-1,0,1\}^{1024\times D}$ with independent entries distributed as $\chi$. Then

$$
\Pr\left(\|\Pi w\bmod q\|_2^2\le120b^2\right)<2^{-164}.
$$

In particular, the event includes equality at the verification threshold. The theorem requires neither a prime modulus nor a ring-factorization assumption. It does require that $w$ be fixed independently of $\Pi$.

## Moment and exponential estimates

For a row $\pi$ and a nonzero real vector $u$, put $Z=\langle\pi,u\rangle$ and $Y=Z/\|u\|_2$. Since

$$
\mathbb E\chi=0,
\qquad \mathbb E\chi^2=\mathbb E\chi^4=\frac12,
$$

expanding the second and fourth moments gives

$$
\mathbb EY^2=\frac12,
\qquad
\mathbb EY^4=\frac34-\frac{\sum_i u_i^4}{4\|u\|_2^4}\le\frac34.
$$

For $x\ge0$, the inequality $e^{-x}\le1-x+x^2/2$ therefore implies

$$
\mathbb E e^{-Y^2/2}
\le1-\frac14+\frac18\frac34
=\frac{27}{32}.
\tag{1}
$$

We also use $\chi=(\varepsilon+\varepsilon')/2$, where the two signs are independent and uniform on $\{-1,1\}$. For any real $s$,

$$
\mathbb Ee^{sZ}
=\prod_i\cosh^2(su_i/2)
\le \exp(s^2\|u\|_2^2/4),
$$

using $\cosh x\le e^{x^2/2}$. Chernoff's argument yields, for $t>0$,

$$
\Pr(|Z|\ge t)\le2\exp(-t^2/\|u\|_2^2).
\tag{2}
$$

Zero coordinates cause no difficulty in these calculations.

## Proof of Theorem 1

Write $t=\sqrt{120}\,b$. In particular, $t/q\le\sqrt{120}/250<1/2$. We distinguish three exhaustive cases for the fixed vector $w$.

### Case 1: $\|w\|_2<q/12$

If the modular projection has squared norm at most $t^2$, then either the unmodded projection also has squared norm at most $t^2$, or some coordinate has a nonzero wrap. In the latter case, a coordinate of the unmodded projection has absolute value at least $q-t$: its centered residue has absolute value at most $t$, and it differs from that residue by a nonzero multiple of $q$.

Because $\|w\|_2\ge b>0$, the unmodded small-norm event implies

$$
\sum_{j=1}^{1024}
\left(\frac{\langle\pi_j,w\rangle}{\|w\|_2}\right)^2\le120.
$$

Applying Markov's inequality to the negative exponential, and then (1) to the independent rows, gives

$$
\Pr(\|\Pi w\|_2^2\le120b^2)
\le e^{60}\left(\frac{27}{32}\right)^{1024}.
$$

For the wrap contribution, (2), the bound on $\|w\|_2$, and a union bound give

$$
\Pr(\text{a wrap compatible with the small-residue event})
\le2048\exp\left[-144\left(1-\frac{\sqrt{120}}{250}\right)^2\right].
$$

Their sum is strictly below $2^{-164}$. The following rational certificate avoids floating-point comparisons. Taylor bounds give

$$
\frac{163}{60}=\sum_{k=0}^{5}\frac1{k!}<e
<\sum_{k=0}^{6}\frac1{k!}+\frac1{7!}\frac87
=\frac{31967}{11760}<\frac{87}{32}.
$$

The geometric-series factor $8/7$ bounds the remaining ratios from the seventh term onward. Moreover,

$$
\sqrt{120}<11,
\qquad
144\left(\frac{239}{250}\right)^2
=\frac{2056356}{15625}>131.
$$

Consequently, the sum of the two probability bounds is strictly below

$$
U=\left(\frac{87}{32}\right)^{60}
\left(\frac{27}{32}\right)^{1024}
+2048\left(\frac{60}{163}\right)^{131}
<2^{-164}.
\tag{3}
$$

The last inequality is a comparison of integers after clearing denominators, as checked in `family_constants_certificate()`.

### Case 2: $\|w\|_\infty\ge q/72$

Choose an index $i$ with $|w_i|\ge q/72$ and condition on every other entry in a row. Let their contribution modulo $q$ be $a$. Consider the open arc

$$
I=\{x\bmod q:|x|_q<q/144\}
$$

on the circle $\mathbb R/q\mathbb Z$. Its length is $q/72$. Since $q/72\le|w_i|\le q/2$, the circular distance from $a$ to each of $a+w_i$ and $a-w_i$ is at least the length of this arc. Thus, if $a\in I$, both shifted points lie outside $I$. If $a\notin I$, the only atoms that can lie inside are the two nonzero challenge atoms, whose total mass is $1/2$. Therefore

$$
\Pr(|\langle\pi,w\rangle|_q<q/144)\le\frac12,
\qquad
\Pr(|\langle\pi,w\rangle|_q\ge q/144)\ge\frac12.
\tag{4}
$$

The two shifted points may coincide, as they do when $|w_i|=q/2$; their combined mass is still only $1/2$.

The strict inequality in the small arc is essential. For example, if $q=144$, $w_i=2$, and $a=-1$, then the values $-1,1,-3$ have masses $1/2,1/4,1/4$. The probability of absolute value strictly greater than $q/144=1$ is only $1/4$. This is why the counted rows in (4) use $\ge$, rather than $>$.

Let $N$ count rows with modular absolute value at least $q/144$. Independent rows and (4) imply that $N$ stochastically dominates $\operatorname{Bin}(1024,1/2)$. If $N\ge40$, then

$$
\|\Pi w\bmod q\|_2^2
\ge\frac{40q^2}{144^2}
>\frac{120q^2}{250^2}
\ge120b^2.
$$

Indeed, $120\cdot144^2/250^2=124416/3125<40$. Hence the closed target event requires $N\le39$, and its probability is at most

$$
2^{-1024}\sum_{k=0}^{39}\binom{1024}{k}
<2^{-788}<2^{-164}.
\tag{5}
$$

The binomial sum is evaluated exactly. The argument makes no assumption that $q/144$ is an integer.

### Case 3: $\|w\|_2\ge q/12$ and $\|w\|_\infty<q/72$

Delete coordinates of $w$ until the remaining vector $v$ first satisfies $\|v\|_2<q/12$. Immediately before the last deletion, its squared norm was at least $q^2/144$, while the deleted squared coordinate was smaller than $q^2/72^2$. Thus

$$
\frac{\sqrt{35}\,q}{72}<\|v\|_2<\frac q{12},
\qquad
\|v\|_\infty<\frac q{72}.
\tag{6}
$$

The supports of $v$ and $w-v$ are disjoint, so their row projections are independent.

Put $X=\langle\pi,v\rangle$ and let $Y$ be normal with mean zero and variance $\|v\|_2^2/2$. Apply the general Berry–Esseen inequality to the independent summands $v_i\varepsilon_i/2$ and $v_i\varepsilon'_i/2$, omitting zero summands. With the valid general constant $0.56$, this gives

$$
\begin{aligned}
\delta&:=\sup_x|\Pr(X\le x)-\Pr(Y\le x)|\\
&\le\frac{0.56}{\sqrt2}\frac{\sum_i|v_i|^3}{\|v\|_2^3}
\le\frac{0.56}{\sqrt2}\frac{\|v\|_\infty}{\|v\|_2}
<\frac{0.56}{\sqrt{70}}.
\end{aligned}
\tag{7}
$$

The factor $1/\sqrt2$ follows because the total third absolute moment of the split summands is $\sum_i|v_i|^3/4$, whereas their total variance is $\|v\|_2^2/2$. [Shevtsova (2013)](https://www.mathnet.ru/eng/ia252) gives the general independent-summand constant $0.5583$; using $0.56$ is conservative. A smaller constant proved only for identically distributed summands would not justify (7).

Condition on the modulo-$q$ value $a$ of the independent remaining projection. Define

$$
I_0=[-q/2,q/2],
\qquad
G=\{x:|x+a|_q\le t\}\cap I_0.
$$

Because $t<q/2$, this is one closed interval or two closed intervals at the ends of $I_0$, with total Lebesgue measure $2t$. The maximum density of $Y$ is $1/(\sqrt\pi\|v\|_2)$, so (6) implies

$$
\Pr(Y\in G)
\le\frac{2t}{\sqrt\pi\|v\|_2}
\le\frac{144\sqrt{120}}{250\sqrt{35\pi}}.
\tag{8}
$$

When $G$ is one interval, its probability differs under $X$ and $Y$ by at most $2\delta$. This remains true for closed endpoints by taking a CDF left limit at the left endpoint; the normal CDF is continuous.

When $G$ consists of two boundary intervals, its complement $J=I_0\setminus G$ is one open interval. In that case,

$$
\begin{aligned}
\Pr(X\in G)
&\le1-\Pr(X\in J)\\
&\le1-\Pr(Y\in J)+2\delta\\
&=\Pr(Y\in G)+\Pr(Y\notin I_0)+2\delta.
\end{aligned}
$$

The normal tail outside $I_0$ is required in this complement argument. Adding the possibility that $X$ lies outside $I_0$ but has a small modular residue gives the uniform conditional bound

$$
\Pr(|X+a|_q\le t)
\le\Pr(Y\in G)+2\delta
+\Pr(|X|>q/2)+\Pr(|Y|>q/2).
\tag{9}
$$

By (2) and $\|v\|_2<q/12$, the $X$ tail is at most $2e^{-36}$. The same bound holds for $Y$ from its normal moment-generating function. Combining (7)–(9), every row has conditional, and hence unconditional, small-residue probability at most

$$
p_0=\frac{144\sqrt{120}}{250\sqrt{35\pi}}
+\frac{1.12}{\sqrt{70}}+4e^{-36}<\frac{736}{1000}.
\tag{10}
$$

The final comparison can be certified using only rational inequalities:

$$
\frac{144^2\cdot120}{250^2\cdot35\cdot(157/50)}
<\left(\frac{6019}{10000}\right)^2,
\qquad
\frac{(28/25)^2}{70}
<\left(\frac{1339}{10000}\right)^2,
$$

and $4e^{-36}<4\cdot2^{-36}<1/10000$. Since $\pi>157/50$, their sum is smaller than $7359/10000<736/1000$. For an explicit certificate of the bound on $\pi$, Machin's identity and the alternating arctangent series give

$$
\begin{aligned}
\pi&=16\arctan(1/5)-4\arctan(1/239)\\
&>16\left(\frac15-\frac{1}{3\cdot5^3}\right)-\frac4{239}
=\frac{281476}{89625}>\frac{157}{50}.
\end{aligned}
$$

The target vector event requires every row to have modular absolute value at most $t$. Since rows are independent, (10) yields

$$
\Pr(\|\Pi w\bmod q\|_2^2\le120b^2)
\le p_0^{1024}
<\left(\frac{736}{1000}\right)^{1024}
<2^{-452}<2^{-164}.
\tag{11}
$$

The last comparison again uses integer powers after clearing denominators. Cases 1–3 exhaust the fixed vector $w$, so the maximum of their upper bounds proves Theorem 1. The three case bounds do not need to be added.

## Honest completeness and the threshold 552

**Theorem 2 (one-attempt completeness).** Let $m\ge1$ and $\beta>0$, and fix a vector $w$ with $\|w\|_2\le\beta$. Sample $m$ independent projection rows with the distribution above. For any $T>m/2$,

$$
\Pr(\|\Pi w\bmod q\|_2^2>T\beta^2)
\le\frac{m/2}{m/2+(T-m/2)^2}.
\tag{12}
$$

If $\beta=0$, the only possible vector is zero and acceptance at the closed threshold is certain.

**Proof.** Put $S=\sum_{j=1}^m\langle\pi_j,w\rangle^2$. The moment calculation above and independence give

$$
\mathbb ES=\frac m2\|w\|_2^2,
\qquad
\operatorname{Var}(S)
=m\left(\frac12\|w\|_2^4-\frac14\sum_iw_i^4\right)
\le\frac m2\beta^4.
$$

Centered modular reduction cannot increase any coordinate's absolute value. Therefore rejection implies $S>T\beta^2$, which in turn implies

$$
S-\mathbb ES>(T-m/2)\beta^2.
$$

Cantelli's inequality gives (12). For completeness, if a centered variable $V$ has variance $\sigma^2$ and $a>0$, Markov's inequality applied to $(V+\lambda)^2$ gives

$$
\Pr(V\ge a)\le\frac{\sigma^2+\lambda^2}{(a+\lambda)^2}
\quad(\lambda\ge0).
$$

Choosing $\lambda=\sigma^2/a$ yields $\sigma^2/(\sigma^2+a^2)$. The bound is increasing in $\sigma^2$, which justifies substituting the variance upper bound above.

For $m=1024$ and $T=552$, equation (12) becomes

$$
\Pr(\|\Pi w\bmod q\|_2^2>552\beta^2)
\le\frac{512}{512+40^2}=\frac8{33}.
$$

Thus acceptance at the **closed** threshold $552\beta^2$ has probability at least $25/33$. To combine this threshold with Theorem 1, set

$$
b=\sqrt{\frac{552}{120}}\,\beta
=\sqrt{\frac{23}{5}}\,\beta,
\qquad
\sqrt{\frac{23}{5}}\,\beta\le\frac q{250}.
\tag{13}
$$

The resulting norm slack is $\sqrt{23/5}$. For an alternative desired rejection probability $\eta\in(0,1)$, (12) allows

$$
T_\eta=\frac m2+\sqrt{\frac m2\frac{1-\eta}{\eta}}.
$$

These are one-attempt bounds. Any retry rule or random-oracle challenge derivation requires its own protocol-level treatment.

## A general parameter template

The same argument gives a parameterized lemma. Let $m,D,q$ be positive integers, and let $\alpha,K,A,C$ be positive real constants satisfying

$$
C>A\ge2,
\qquad
r:=\frac{\sqrt\alpha}{K}<\frac12,
\qquad
s:=\sqrt{A^{-2}-C^{-2}}.
$$

Fix a centered vector $w\in\mathbb Z^D$ with $\|w\|_2\ge b>0$ and $b\le q/K$. Then the closed event $\|\Pi w\bmod q\|_2^2\le\alpha b^2$ has probability at most

$$
\min\{1,\max(B_1,B_2,B_3)\},
$$

where

$$
B_1=e^{\alpha/2}(27/32)^m+2m e^{-A^2(1-r)^2},
$$

$$
B_2=2^{-m}
\sum_{k=0}^{\min\{m,\lfloor4\alpha C^2/K^2\rfloor\}}\binom mk,
$$

$$
B_3=\left[
\min\left\{1,
\frac{2r}{\sqrt\pi s}
+\frac{0.56\sqrt2}{Cs}
+4e^{-A^2/4}
\right\}\right]^m.
\tag{14}
$$

To verify (14), use the same cases with cutoffs $q/A$ and $q/C$. In Case 1, the normalized squared threshold is $\alpha$ and the wrap distance is at least $q(1-r)$. In Case 2, count rows with modular magnitude at least $q/(2C)$. The closed target event allows at most $\lfloor4\alpha C^2/K^2\rfloor$ such rows; the floor cannot be reduced by one when its argument happens to be an integer. In Case 3, the truncated vector satisfies $sq<\|v\|_2<q/A$ and $\|v\|_\infty<q/C$. Its density, twice its Berry–Esseen discrepancy, and the two tails give the three terms in $B_3$.

Theorem 1 specializes this template to

$$
(m,\alpha,K,A,C)=(1024,120,250,12,72).
$$

## Code correspondence and scope

In the standalone [`jl_family_checks.py`](../scripts/jl_family_checks.py), `family_constants_certificate()` returns the three case bounds, and `security_profile(128)` supplies the base parameter fields:

| Field | Mathematical quantity |
| --- | --- |
| `case1_base` | The rational upper bound $U$ in (3) |
| `case2_base` | The exact binomial sum in (5) |
| `case3_base` | $(736/1000)^{1024}$ in (11) |
| `certified_failure_exponent` | $164$, the exponent of a uniform upper bound larger than each case certificate |
| `honest_rejection_upper` | $8/33$ from Theorem 2 |
| `slack_squared` | $23/5$ from (13) |

The standalone [`jl_repair_review_checks.py`](../scripts/jl_repair_review_checks.py) independently repeats the rational threshold certificates, the closed-event count boundary, and the honest completeness arithmetic. These finite checks support the arithmetic review; the arguments above establish the universal statements.

The change to 1024 rows and to the modulus and norm conditions affects a complete protocol's messages and parameters. This document does not certify Module-SIS hardness, a Fiat–Shamir theorem, a recursive error budget, or the original proof-size measurements.

## References

1. Ward Beullens and Gregor Seiler. **LaBRADOR: Compact Proofs for R1CS from Module-SIS.** Cryptology ePrint Archive, Paper 2022/1341, 2022. [Primary source](https://eprint.iacr.org/2022/1341). The motivating modular projection argument is Lemma 4.2 and Appendix A in the 34-page version.
2. I. G. Shevtsova. **On the absolute constants in the Berry–Esseen inequality and its structural and nonuniform improvements.** *Informatika i Ee Primeneniya*, 7(1):124–125, 2013. [Primary publication record and full-text link](https://www.mathnet.ru/eng/ia252). The general independent-summand constant stated there is $0.5583$; this document uses $0.56$.
