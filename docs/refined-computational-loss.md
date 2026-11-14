# Bad-mass-weighted computational loss

This note refines the probability analysis of the ordinary classical extractors
in [unknown-gap extraction](unknown-gap-extraction.md) and
[finite extraction](finite-extraction.md). It uses their algebraic root bounds,
candidate construction, and collision-validity arguments. It changes neither an
extractor nor a collision sampler. Its conclusions remain conditional on the
[protocol obligations](protocol-conditional.md), including the actual matrix,
norm, and complete running time of each reduction.

The improvement is an averaging inequality: the invalid-candidate mass is kept
inside Cauchy--Schwarz. For the single accept-gated extractor, this replaces the
earlier sufficient fourth-root computational term by a cubic-root term. The
finite non-gated extractor has a different scalar inequality and a separate API.
No numerical hardness advantage is established here.

## 1. Quantities and theorem

Let the original statistical allowance be

```text
kappa = delta_JL + q^(-m) + q^(-d/2) + 2/N.
```

Here `N` is the challenge-set cardinality and `r` the number of coordinates. Let
`eta_0, eta_h, eta_y, eta_g` be the success probabilities, or valid upper bounds
on those probabilities, of the complete collision experiments in the extraction
theorem. The `y` experiment chooses a coordinate uniformly from `1,...,r`. Let
`eta_E` bound the anchor extractor's own collision output. These are unconditional
probabilities: initialization, failed anchors, and all subsequent coins are part
of each experiment.

Define

```text
K^2 = (sqrt(eta_h) + sqrt(r eta_y))^2 + eta_g,
H   = 2 eta_h + 2 r eta_y + eta_g.
```

Thus `K^2 <= H`. For the single accept-gated extractor, let `B` be the
unconditional probability of producing a completed candidate outside the required
relaxed source relation. Then

```text
B^2 - kappa B <= eta_0 + K sqrt(B),                         (1)
B <= kappa + sqrt(eta_0) + (K^2)^(1/3)
  <= kappa + sqrt(eta_0) + H^(1/3).                         (2)
```

The unchanged candidate-or-collision success bound is `epsilon - r/N`. Therefore

```text
Pr[valid relaxed witness]
  >= epsilon - (kappa + r/N) - sqrt(eta_0) - H^(1/3) - eta_E. (3)
```

All probability lower bounds may be clipped at zero. A sharper upper-root
certificate for (1) can replace the sum on the right side of (2).

If only `eta_y` is nonzero, the exact cubic-root term is `(r eta_y)^(1/3)`.
The convenient expression `H` is then larger than necessary. The scalar APIs
accept any independently proved rational `h >= K^2`; `collision_loss_envelope`
provides the conservative, always valid expression `H` above.

## 2. The probability space must remain the same

Let `theta` include the CRS, public instance, and original prover state and tape.
Let `A` be the complete anchor experiment together with `theta`; its output is a
completed candidate or bottom. All suffix masses below are zero at bottom.
The extraction analysis and every collision experiment use exactly this same
law of `A`.

After a completed anchor, draw a fresh upper prefix `U` through the second outer
commitment. Its verifier coins are fresh and independent of the anchor coins,
with the dependence on the original state prescribed by the extraction theorem.
The coordinate sampler draws `I` uniformly and independently of `A,U`. The other
final challenges follow their prescribed product law. Its two forks use
independent draws of the remaining challenge. For a stochastic late reply, each
branch also uses fresh independent kernel coins, with no restored virtual reply
tape or shared mutable cache.

An event or mode may appear in the analysis without being computable by the
sampler. None of these collision experiments conditions its execution on an
invalid candidate or on a modal value.

## 3. Local masses and the selected coordinate

At a fixed saved prefix let `p_v` be the unnormalized probability of an
anchor-consistent accepting suffix with value `v`. Put

```text
a = sum_v p_v,
e = a - max_v p_v,
c = a^2 - sum_v p_v^2.
```

Two independent suffixes give different accepted values with probability `c`.
Since `sum_v p_v^2 <= a max_v p_v`,

```text
c >= a e >= e^2.
```

For an anchor event `D` of mass `b_D`, Cauchy--Schwarz on the unconditional joint
law of anchor and fresh prefix gives

```text
(E[1_D e])^2 <= b_D E[1_D e^2] <= b_D E[c].                 (4)
```

Keeping the first factor `b_D` is the useful step. The last expectation is
bounded by the success probability of the complete collision experiment.

For the diagonal argument, fix `A,U` and its modal packed `h`, with a fixed tie
rule. If some modal diagonal is wrong relative to the anchor candidate, select
the first such index `iota(A,U)`. This selector is fixed **before all final
challenges**, including the challenges at coordinates other than the selected
one. It may be uncomputable; it is only an analysis function. It is undefined
when no modal diagonal is wrong.

For coordinate `i`, let `e_i(A,U,c_-i)` be the nonmodal accepted mass on its slice
for the original value `y = z - c_i s_i*`. Its two-suffix collision probability
`c_i` satisfies `e_i^2 <= c_i`. The original saved nonzero unit denominator and
the original norm argument are still needed to turn this collision into the
claimed MSIS output.

The needed exception mass is

```text
e_sel(A) = E_U[sum_i 1_{iota(A,U)=i} E_{c_-i} e_i(A,U,c_-i)].
```

Using the actual uniform-coordinate experiment,

```text
E[1_D e_sel] = r E[1_D 1_{I=iota(A,U)} e_I],
E[1_D 1_{I=iota(A,U)}] <= b_D/r,
E[1_D e_sel] <= sqrt(r b_D eta_y).                           (5)
```

The final line follows from Cauchy--Schwarz and `e_I^2 <= c_I`. The factor `r`
inside the square root cannot be dropped for uniform coordinate sampling. A
uniform public bound `r_max` also suffices when `r` depends on the statement:
apply Cauchy--Schwarz to `sqrt(r W)` and `sqrt(r W)e_I`, where
`W=1_D 1_{I=iota}`, using `E[r W] <= b_D` and
`E[r W e_I^2] <= r_max eta_y`.

## 4. Disjoint invalid-candidate cases

Define events

```text
Bad   = {a completed candidate S is outside the required source relation},
Bad_G = Bad intersect {S has valid norm and anchored g != Gram(S)},
Bad_N = Bad \ Bad_G,
B_G = Pr[Bad_G],  B_N = Pr[Bad_N],  B = B_G + B_N.
```

The intersection with `Bad` matters. A valid source witness with an incorrect
auxiliary `g` is not an invalid source output.

Write `epsilon_theta` for ordinary acceptance from state `theta`. The original
algebraic norm/equation argument, retaining the selected diagonal, gives on
`Bad_N`

```text
(epsilon_theta - kappa)_+ <= e_0(A) + e_h(A) + e_sel(A).
```

The original selected Gram-entry argument gives on `Bad_G`

```text
(epsilon_theta - kappa)_+ <= e_0(A) + e_g(A).
```

These two pointwise inequalities are premises inherited from the extraction
proof; scalar arithmetic alone does not establish them for a protocol.
The first-opening mismatch mass has `E[e_0] <= eta_0` directly, without a square
root. Applying (4) and (5), then two-dimensional Cauchy--Schwarz, yields

```text
E[1_Bad (epsilon_theta - kappa)_+]
 <= eta_0 + sqrt(B_N)(sqrt(eta_h) + sqrt(r eta_y))
          + sqrt(B_G)sqrt(eta_g)
 <= eta_0 + sqrt(B) K.                                      (6)
```

This explains the coefficients `2,2r,1` in `H`. In particular, `eta_g` does not
need an additional factor two. No pointwise binding assumption conditional on
the CRS, a bad candidate, or a chosen upper prefix is used.

## 5. The gate and its scalar certificate

For the single accept gate, `b_theta = Pr[Bad | theta] <= epsilon_theta`.
Consequently

```text
E[1_Bad (epsilon_theta - kappa)_+]
 = E_theta[b_theta (epsilon_theta - kappa)_+]
 >= E_theta[b_theta^2] - kappa B
 >= B^2 - kappa B.
```

Together with (6), this proves (1). Its largest nonnegative root is the useful
upper bound. When `eta_0` or `K` is positive, there is one root strictly above
`kappa`; when both vanish, choose the root `kappa`. For `R >= kappa`, `R > 0`,
the function `(R^2 - kappa R - eta_0)/sqrt(R)` is strictly increasing. Thus a
positive rational `R` certifies an upper bound whenever

```text
R >= kappa,
D = R^2 - kappa R - eta_0 >= 0,
D^2 >= h R,                      where h >= K^2.           (7)
```

Then `B <= min(1,R)`. The value `R=0` is certified only if
`kappa=eta_0=h=0`. Checking only the squared inequality would incorrectly accept
a zero root, for example when `kappa=eta_0=0` but `h>0`. A failed certificate says
that this particular proposed upper bound was not certified.

To prove (2), set `A_0=sqrt(eta_0)` and `C=(K^2)^(1/3)`. If
`B > kappa+A_0+C`, then `eta_0=A_0^2 <= A_0 B` and
`K sqrt(B)=C^(3/2)sqrt(B) <= C B`, contradicting (1). The package can certify
rational upper bounds on the two radicals using `A_0^2 >= eta_0` and `C^3 >= h`.

When using the sharper root certificate, the witness lower bound is

```text
epsilon - r/N - min(1,R) - eta_E.                           (8)
```

The allowance `kappa` is already in `R`; it must not be subtracted again.

## 6. Finite non-gated anchors require a different bound

The finite anchor procedure may retry initial executions before choosing an
accepting anchor. It need not satisfy `b_theta <= epsilon_theta`; the gate
cubic-root conclusion does not apply to that procedure.

For its original positive gap `Delta`, let
`High={theta: epsilon_theta >= kappa+Delta}` and
`B_H=Pr[Bad intersect High]`. The same weighted argument gives

```text
Delta B_H <= eta_0 + K sqrt(B_H),
B_H <= [(K + sqrt(K^2 + 4 Delta eta_0))/(2 Delta)]^2.         (9)
```

A rational upper bound is

```text
B_H <= min(1, 2 eta_0/Delta + h/Delta^2).                    (10)
```

This follows by applying Young's inequality with coefficient `Delta/2` to
`K sqrt(B_H)`. A tighter rational `R>0` may instead be certified by

```text
D = Delta R - eta_0 >= 0,
D^2 >= h R.                                                (11)
```

For this finite bound, `R=0` is certified only when `eta_0=h=0`.
The original finite theorem then gives

```text
Pr[valid witness] >= epsilon - kappa - Delta - zeta
                             - B_H_upper - eta_E.          (12)
```

Its execution cap, failure allowance `zeta`, initialization distribution, and
running-time obligations remain unchanged. The finite and gated examples may
use the same numerical inputs for illustration, but actual advantages must be
proved separately for their respective complete anchor laws.

## 7. Reduction obligations remain unchanged

The complete collision experiments still run initialization and the anchor phase
followed by at most two fresh complete suffixes. Their original norm obligations
are:

| Advantage | Matrix and output norm bound |
| --- | --- |
| `eta_0`, `eta_h`, `eta_E` | The corresponding outer matrix, `2 B_target` |
| `eta_y` | Inner matrix, `8 T (b+1) B_target` |
| `eta_g` | Inner matrix, `2(b+1) B_target + 4 T s beta` |

Here `B_target` is the bound on a target opening, and `b` is the original
decomposition parameter. Neither is the bad-output probability `B` in this note.
The matrix embedding, nonzero output, denominator, and norm checks from the
protocol theorem remain necessary.

Expected-time reductions still require the stated truncation argument when the
MSIS assumption quantifies over strict polynomial time. Full initialization,
nested late-reply kernels, and truncation losses cannot be omitted. A finite
cutoff does not incur zero loss merely because the underlying expectation is
bounded.

For recursive composition, retain the original fresh-kernel, no-cache model,
uniform conditional cost bounds, and polynomial runtime-product condition.
Only the corresponding per-layer loss is replaced. For
[bounded complete-protocol restarts](bounded-restarts.md), each initializer
includes its own preceding rejected ordinary attempts. Apply the refined bound
to each such complete experiment and sum its losses using the first-real-
acceptance coupling. A single advantage estimate is not automatically valid for
all initialized samplers, and the result does not assume per-CRS binding.

The `eta` inputs are complete reduction advantages at their actual runtimes,
dimensions, distributions, and norms. A lattice cost estimate or Core-SVP model
point is not an upper bound `eta=2^(-cost)`. This note therefore supplies no
concrete numerical security certification. Under the original uniformly
quantified asymptotic assumptions, roots of negligible advantages remain
negligible.

## 8. Exact arithmetic interface

`labrador_repair.extraction_bounds` accepts `Fraction` probabilities and strictly
validated integer multiplicities and challenge cardinalities. It exposes the
following separate certificates:

| API | Meaning |
| --- | --- |
| `collision_loss_envelope` | Compute `H=2 eta_h+2r eta_y+eta_g` |
| `gated_upper_root_certified` | Check (7), including the zero-root exception |
| `gated_bad_mass_upper` | Validate a gate root and return its probability cap |
| `simple_gated_root_upper` | Check rational radical bounds and return an uncapped root bound |
| `gated_witness_lower` | Compute (8), subtracting `kappa` only through the root |
| `finite_upper_root_certified` | Check the separate finite certificate (11) |
| `finite_bad_mass_upper` | Use (10) or an explicitly certified finite root |
| `finite_witness_lower` | Compute (12) with the supplied finite failure allowance |

The module implements no extractor, prover, RNG, lattice solver, or advantage
estimator. It does not verify that a cryptographic protocol satisfies the
probabilistic premises. `H` may exceed one: it is an algebraic envelope, not a
probability. Probability caps are applied after the appropriate root is
certified; the capped value need not itself certify the scalar root.

Run the abstract example and tests from an installed source checkout:

```console
python examples/refined_loss.py
python -m unittest discover -s tests -p test_extraction_bounds.py -v
```

The tests enumerate independent accepted-mass tables, weighted common-anchor
cases, and rational scalar grids. Negative controls cover a missing coordinate
factor, the spurious zero, squaring a negative branch, and transferring a gate
certificate to a finite non-gated experiment. These tests check arithmetic and
bookkeeping; the proof above supplies the general inequalities.
