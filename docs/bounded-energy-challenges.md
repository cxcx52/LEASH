# Bounded-energy challenge certificates

This optional construction uses degree `d=64`, coefficients in `{-2,-1,0,1,2}`, squared coefficient norm at most `104`, and multiplication operator norm strictly below `30`. Its exact count certificate retains more than two thirds of the raw energy ball. A separate honest-moment certificate permits `Gamma^2=9*d*beta^2` with fold rejection at most `1/16`.

These are mathematical component certificates. They do not certify a recursive parameter schedule, numerical Module-SIS hardness, complete knowledge security, proof size, or Fiat--Shamir security. The existing cube and folding APIs are unchanged.

The implementation is [energy.py](../src/labrador_repair/energy.py), with independent checks in [test_energy.py](../tests/test_energy.py) and a runnable [example](../examples/bounded_energy.py). It contains no RNG or cryptographic prover.

## Exact sets and counting

For a nonnegative integer dimension `d`, define

```text
B_E = {c in {-2,-1,0,1,2}^d : sum_j c_j^2 <= E},
S_E = {c in {-2,-1,0,1,2}^d : sum_j c_j^2 = E}.
```

The generating polynomial `(1+2z+2z^4)^d` counts squared energies. Its coefficients satisfy

```text
A_d(e) = A_(d-1)(e) + 2 A_(d-1)(e-1) + 2 A_(d-1)(e-4),
A_0(0) = 1.
```

Out-of-range terms in this recurrence are zero. Summing through `E` gives the exact ball cardinality. At degree 64 and energy 104,

```text
N_ball = 20905094450944450994971371210796521612779265.
```

The count routines accept arbitrary nonnegative integer dimensions, including zero. Ring, operator-tail and moment routines require a **power-of-two degree at least two**. Public energy bounds must be integers in `[0,4d]`.

### Deterministic rank encoding

`energy_ball_unrank(d,E,j)` maps an integer `0<=j<|B_E|` to its lexicographically indexed vector, in symbol order `(-2,-1,0,1,2)`. At each coordinate it uses the exact number of completions under the remaining energy budget. `energy_ball_rank(c,E)` is its inverse.

A uniform integer rank would induce a uniform raw ball element. The module performs only the deterministic bijection; it does not generate that random integer. Applying an independent deterministic operator filter to genuinely uniform raw draws gives the uniform distribution on the retained set.

`bounded_energy_member` checks the energy cap and reuses the existing [certified Fourier predicate](certified-fourier.md), including its exact integer-SPD fallback. The strict operator boundary rejects equality. No new spectral approximation is introduced.

## The tilted count certificate

Let rational `0<t<=1` define an independent product distribution with symbol probabilities

```text
P_t[X_j=c] = t^(c^2)/Z_t,
Z_t = 1+2t+2t^4.
```

Its variance and fourth moment are

```text
v_t = (2t+8t^4)/Z_t,
m4_t = (2t+32t^4)/Z_t.
```

The API checks `m4_t<=3v_t^2` and `5v_t>4`. These conditions establish the sub-Gaussian MGF comparison with variance proxy `v_t`: the first even moment is exact, the second comparison is checked, and subsequent actual even-moment ratios are less than four while Gaussian ratios are at least `5v_t`. Comparing even power series gives

```text
E_t exp(u X_j) <= exp(v_t*u^2/2)
```

for every real `u`. A failed sufficient moment comparison is not a proof that no other MGF bound exists.

For each root of `X^d+1` and any phase, the squared projection weights sum to `d/2`. Chernoff and an `m`-direction angular net, using one root per conjugate pair, imply

```text
P_t[||c||op >= T] <= (dm/2) exp(-gamma_m*T^2/(d v_t)),
gamma_m < cos^2(pi/m).
```

The supported rational constants are

| Directions | `gamma_m` |
|---|---:|
| 8 | `1707/2000` |
| 12 | `933/1000` |
| 16 | `9619/10000` |

They follow from `(707/500)^2<2`, `(433/250)^2<3`, `(4619/5000)^2<1707/2000`, and the half-angle identities. No numerical trigonometry participates in the certificate.

For positive rational `x`, the finite positive sum

```text
L_K(x) = sum_(k=0)^K x^k/k! < exp(x)
```

gives the strict rational upper bound `exp(-x)<1/L_K(x)`. The default is `K=80`. Bounds exceeding one are valid but vacuous; they do not imply large actual rejection probability.

### Converting a product-law tail into a uniform-ball count

Conditioning the tilted law on a ball does not make it uniform. Instead, for every vector with energy at most `E`, `t^(energy)>=t^E`. Therefore

```text
|B_E intersect bad| <= Z_t^d * t^(-E) * P_t[bad].
```

Dividing by the exact ball count converts this to a probability bound under a uniform raw ball. This factor is retained in `energy_ball_rejection_upper`.

For the stated profile use `t=4/5`, whose integer symbol weights are `(256,500,625,500,256)`, summing to 2137. Its variance is `3048/2137`. With 12 directions and

```text
x = (933/1000)*30^2 / [64*(3048/2137)],
```

exact rational arithmetic proves

```text
[(2137/625)^64 * (5/4)^104 / N_ball] * 384/L_80(x) < 1/3.
```

Thus the operator filter accepts with probability greater than `2/3`. The inclusive cardinality lower bound is

```text
N_min = floor(2*N_ball/3)+1
      = 13936729633962967329980914140531014408519511.
```

This is a lower bound, not an enumeration of the filtered set. Uniform raw-ball rejection sampling would need fewer than `3/2` candidates in expectation. A strict sampling-time cap and its abort rule require separate specification.

Zero belongs to the set. An independent uniform selected challenge equals zero with probability exactly `1/|C|`, so the reference-zero abort coin in the reviewed accept-gated extractor remains available. Distinct selected challenges differ coefficientwise by at most four; the existing sufficient unit-difference condition, prime `q>32` with `q=5 mod8`, therefore applies.

## General symmetric raw-law moment lemma

Let `d>=2` be a power of two. Suppose a real raw vector `X` has a distribution invariant under all coordinate sign flips and permutations, with actual finite fourth moments

```text
v0  = E X_0^2,
m4  = E X_0^4,
m22 = E X_0^2 X_1^2,
V_U = d*m4 + d(d-1)*m22 - d^2*v0^2 = Var(||X||^2),
g   = 2m22-v0^2+(m4-3m22)/d.
```

In particular `g=V_U/d^2+(1-2/d)m22>=0`. These are moments of an actual symmetric distribution; arbitrary numbers satisfying a few inequalities need not be realizable. `SymmetricRawMoments` validates necessary consistency only. `raw_energy_ball_moments` obtains actual moments from exact ball counts.

Let a filter event have probability `p>a>0`, and assume its selected law has zero mean and covariance `v I_d`. For the operator-filtered ball, negation, signed shifts and odd Galois substitutions prove this isotropy as in the [filtered cube proof](certified-filtered-challenges.md). The filtered law need not retain arbitrary coordinate-permutation symmetry.

For a fixed stacked ring multiplier `M_s`, let `H=M_s^T M_s` and `t=||s||^2`. Its columns have squared norm `t`. Raw sign/permutation symmetry gives

```text
E[(X^T H X)^2]
 = m22[(tr H)^2+2tr(H^2)] + (m4-3m22) sum_j H_jj^2.
```

The [paired-spectrum argument](filtered-folding-moments.md) gives `tr(H^2)<=(tr H)^2/2`, including stacked vectors. Since `H_jj=t` and `tr H=dt`, the raw mean is `v0*d*t` and its variance is at most `g*d^2*t^2`. Centering before conditioning gives

```text
Var(||M_s C||^2) <= [g/p-(v-v0)^2] d^2 t^2.
```

For independent selected challenges `C_i` and fixed witnesses `s_i`, with `S=sum_i ||s_i||^2<=beta^2`, the output covariance trace bound implies

```text
Var(||sum_i C_i s_i||^2)
 <= d^2 S^2 max{g/p-(v-v0)^2, v^2}.
```

The exact covariance identity `Cov(||X||^2,1_filter)=pd(v-v0)` also yields

```text
|v-v0| <= rho = sqrt[V_U(1-a)/(a*d^2)].
```

Splitting the variance maximum into two branches, applying Cauchy--Schwarz, then Cantelli gives the sufficient cap

```text
Gamma^2/(d*beta^2)
 >= max{v0+sqrt(g/(a*f)),
        (v0+rho)(1+sqrt((1-f)/f))}.
```

It bounds fold rejection by `f`. It is a sufficient envelope, not an exact extremal optimization. Witnesses must be fixed before the independent challenges; the argument also applies conditionally on a preceding history with that property. Coefficientwise centering modulo `q` cannot enlarge the norm. The zero-witness case accepts deterministically.

## Exact ball moments and the coefficient nine

The uniform raw ball has dependent coordinate magnitudes. The DP computes

```text
v0 = E[U]/64,
m4 = [2*|B_103 in dimension 63|+32*|B_100 in dimension 63|]/N_ball,
m22 = [E[U^2]-64*m4]/(64*63),
```

with `E[U^j]=sum_(e=0)^104 e^j*A_64(e)/N_ball`. Approximate displays are

```text
v0  = 1.551668437392509,
m4  = 4.833409692251479,
m22 = 2.374393872768348,
g   = 2.305335119591999,
V_U = 21.05776270402408.
```

The implementation retains exact Fractions. At `a=2/3`, `f=1/16`, it checks

```text
(9-v0)^2 > 24*g,
rho^2 = V_U/(2*64^2) < (1/16)^2,
sqrt(15) < 31/8.
```

The first comparison handles the first cap branch; the second branch obeys
`(v0+1/16)(1+31/8)<9`. Thus `Gamma^2=9*d*beta^2` is certified. In the public API the two radical upper bounds are explicit rational witnesses, not silently rounded approximations.

## Conditional statistical ledger and limitations

For `q=4294967197`, seven multiplicities whose `sum(r_i+2)=198`, and `Q=128` bounded complete-protocol restarts, exact arithmetic verifies

```text
128 [198/N_min + 7*2^-164 + 7/q^6 + 7/q^32 + 2^-160] < 2^-128.
```

The terms represent the reviewed challenge, JL, scalar, ring and source statistical bounds. The example labels these premises explicitly. Computational binding/extraction losses are additional. This inequality is not a concrete full-security assertion.

With projection threshold 640, the reviewed JL honest rejection is at most `1/33`; the certified fold rejection is at most `1/16`. Their union bound gives per-layer acceptance at least `479/528`. Applying this through a valid seven-layer norm/packing manifest gives a whole-attempt lower bound above one half. The [bounded restart theorem](bounded-restarts.md) then applies with its own assumptions. All digit caps, actual opening bounds, dimensions, collision radii and computational costs still need that complete manifest.

For comparison of families, the entire energy-71 shell has only

```text
914575309776010636758020194460195880960 < 3*2^128
```

elements. Every subset therefore fails to make the current `(r+2)/N` challenge expression at most `2^-128` for any `r>=1`. This is a restriction of that proved expression and family, not an attack or an actual-soundness lower bound. The bounded-energy family trades a larger energy cap for enough certified cardinality. No shorter-proof or security-estimate conclusion is drawn here.

## API and checks

Probability, tilt, moment and cap arguments require `fractions.Fraction`; floats are rejected. Integer arguments reject booleans, negative values and out-of-range ranks or energies. Incompatible ring degrees and unsupported angular nets raise `ValueError`. A failed sufficient count or profile certificate also raises `ValueError`; standalone `*_certified` moment predicates return `False` for valid inputs whose sufficient inequalities fail.

Run:

```text
python -m unittest discover -s tests -p test_energy.py -v
python examples/bounded_energy.py
```

Tests independently enumerate small raw balls, shells and all rank mappings; compare membership with degree-two/four closed spectral formulas; verify the non-iid raw fourth expansion and selected centered variance; and check the degree-64 count, fold and conditional statistical certificates. The general statements follow from the proofs above, not finite enumeration.
