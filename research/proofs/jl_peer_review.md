# 1024-row modular JL repair: independent peer review

Date: 2026-11-14.

Reviewed files:

- `proofs/jl_repair_review.md`
- `scripts/jl_repair_review_checks.py`

This review checks the new mathematical theorem and its honest-projection corollary. It does not review the complete LaBRADOR extractor, transcript chronology, MSIS parameters, recursion, retries, or Fiat–Shamir.

## Verdict

**No blocking mathematical error found in the reviewed version.** The proof establishes the stated closed event for every fixed centered integer vector:

    0<b≤q/250, ||w||≥b
      ⇒ Pr(||Πw mod q||²≤120b²)<2^(−164),

with 1024 independent ternary rows. The honest threshold 552β² gives acceptance probability at least 25/33, slack sqrt(23/5), and the corresponding modulus restriction sqrt(23/5)β≤q/250.

The strict/open distinctions in the reviewed text are necessary and have been checked below. In particular, the earlier “strictly larger than q/144 with probability at least one half” claim must not reappear in downstream code or prose.

## 1. Case 1: b versus ||w|| and modular wraparound

The proof correctly uses the hypothesis ||w||≥b. Thus a real, unreduced projection satisfying ||Πw||²≤120b² also satisfies

    Σ_j (<π_j,w>/||w||)²≤120.

It does not need ||w||=b. Division by ||w|| is legitimate because b>0.

The fourth-moment identity is correct:

    E Z²=||w||²/2,
    E Z⁴=3||w||⁴/4−Σ_i w_i⁴/4.

Together with exp(−x)≤1−x+x²/2 at x=Z²/(2||w||²), it gives the row MGF bound 27/32. Independent rows yield the closed lower-tail bound exp(60)(27/32)^1024. Markov's inequality here handles “≤” without discarding equality atoms.

Let t=sqrt(120)b. On the modular closed event, every centered modular coordinate has absolute value at most t. If a row differs from its unreduced integer coordinate by a nonzero multiple of q, the unreduced coordinate has absolute value at least q−t. This containment is valid even at equality. Since t<q/2, ties at ±q/2 cannot be part of a successful small-coordinate event unless handled by the same integer-multiple reasoning.

The cutoff in this repaired argument is ||w||<q/12, not the old q/10. Substituting q/12 into the two-sided subgaussian bound gives the factor 2048 exp[−144(1−sqrt(120)/250)²]. This improvement is substantial: silently reverting to q/10 would not certify the new 2^(−164) target via this union-bound calculation.

The two rational bounds on e used by the certificate have the correct direction. The exact certificate ran successfully and returns a Case 1 rational upper bound with base-2 logarithm approximately −164.4184602. Direct numerical evaluation of the sharper analytic expression gives approximately −164.4334334. The proof uses the rational certificate, not the displayed decimals.

## 2. Case 2: the circle, masses, equality, and binomial count

The small set is the **open** circular arc

    I={x mod q : dist(x,qZ)<q/144},

of length q/72. The selected coordinate obeys q/72≤|w_i|≤q/2, so the circular distances from a to a+w_i and from a to a−w_i are both at least q/72.

Any two points of the open arc are at circular distance strictly less than its length. Hence, if the mass-1/2 atom a is inside I, the two mass-1/4 atoms are outside. If a is outside, the two nonzero atoms contribute total mass at most 1/2. The argument remains true when the two nonzero atoms coincide, as they do at |w_i|=q/2.

Therefore the correct conclusion is

    Pr(dist(<π,w>,qZ)≥q/144)≥1/2.

It is not generally valid with a strict “>”. The included counterexample q=144,w_i=2,a=−1 has strictly-large probability only 1/4. This is a useful regression condition.

Counting rows with distance **at least** q/144 is compatible with the closed target event because

    40/144² > 120/250².

Thus 40 such rows are impossible on the target event, and the count is at most 39. The rows are independent and identically distributed for fixed w; their count is Bin(1024,p) with p≥1/2, or equivalently stochastically dominates Bin(1024,1/2). The exact binomial probability through 39 is approximately 2^(−788.8362703), comfortably below the desired bound.

As an additional independent finite check, I enumerated all integer circular configurations with 2≤q≤160, q/72≤w_i≤q/2 and a ranging over all residues: **673,188 configurations**. Using integer comparisons 144·dist<q, the conditional small-arc mass never exceeded 1/2. The strict endpoint counterexample was also checked exactly. These computations support the endpoint implementation but do not replace the circular argument for arbitrary q.

## 3. Case 3: deleting coordinates and Berry–Esseen normalization

In the remaining case, ||w||≥q/12 and ||w||∞<q/72. Deleting coordinates until the norm first becomes strictly less than q/12 leaves

    ||v||² > q²/144−q²/72² = 35q²/72².

The strict lower inequality is justified because the last deleted squared coordinate is strictly smaller than q²/72². Consequently v is nonzero. Its support and that of w−v are disjoint, so the two row sums are independent. The choice of support depends only on fixed w, not on the sampled row.

Splitting χ into two independent Rademachers is normalized correctly. The total variance of their weighted sum is ||v||²/2, while the sum of their absolute third moments is Σ_i|v_i|³/4. Hence the standardized third-moment ratio is

    (1/sqrt(2)) Σ_i|v_i|³ / ||v||³,

and the stated bound δ<0.56/sqrt(70) follows.

The external constant's scope has been checked against the original journal entry and abstract: [Shevtsova (2013), *On the absolute constants in the Berry–Esseen inequality and its structural and nonuniform improvements*](https://www.mathnet.ru/eng/ia252). That source distinguishes 0.5583 for the general case from its stronger iid bound. Using 0.56 for this independent, generally nonidentically distributed weighted sum is therefore appropriate. This review relies on the standard general Berry–Esseen theorem; it does not reprove that external theorem.

## 4. Case 3: closed intervals, complements and both tails

The treatment of atoms is correct. G is closed inside I_0=[−q/2,q/2]. For a single closed interval [u,v],

    P(X∈[u,v])=F_X(v)−F_X(u−),

and continuity of the normal CDF allows the same Kolmogorov-distance bound at the left limit. Thus the error is 2δ even when X has endpoint atoms.

When G consists of the two boundary intervals, its complement within I_0 is one open interval J. This remains true if one boundary interval degenerates to a singleton. For an open interval, the lower probability comparison also costs 2δ, using the right endpoint's CDF left limit. Consequently

    P(X∈G)≤P(Y∈G)+P(Y∉I_0)+2δ.

The explicit Gaussian outside-tail term is necessary. The reviewed proof retains it and separately adds P(X∉I_0) when bounding the full modular event. Each tail is at most 2exp(−36), so the combined contribution is 4exp(−36). No extra unaccounted endpoint mass is present.

The density bound uses the correct maximum normal density 1/(sqrt(π)||v||). It yields 144sqrt(120)/(250sqrt(35π)); the square root includes π. The final per-row bound is less than 0.736. Independence across rows then bounds the vector event by 0.736^1024. This estimate only uses that the vector event implies each row is small; it is conservative but valid.

The exact arithmetic certificate, including its rational bounds using π>3.14, passed. Its Case 3 upper bound has logarithm approximately −452.8356645.

## 5. Honest completeness: rejection is strict, acceptance is closed

For S=Σ_j <π_j,w>², the variance calculation is correct:

    Var(S)=m(||w||⁴/2−Σ_i w_i⁴/4)≤(m/2)β⁴

when ||w||≤β. With m=1024, E S≤512β². The strict rejection event S>552β² implies S−E S>40β², which is contained in the non-strict tail to which Cantelli applies. Therefore

    Pr(S>552β²)≤512/(512+1600)=8/33.

Centered modular reduction only decreases coordinate magnitudes, so the modular rejection probability has the same upper bound. The complement is exactly the verifier's closed acceptance event, yielding probability at least 25/33.

I separately checked the second and fourth moment identities by exact enumeration for five small row distributions, including unequal signed coordinates and zeros. All identities matched.

The resulting slack relation 120·(23/5)=552 is exact. Applying the modular theorem requires b=sqrt(23/5)β≤q/250. The document correctly states this condition rather than treating the completeness calculation as sufficient on its own.

## 6. General template and minor clarity suggestions

The three-case template is consistent with the concrete theorem. In particular, the count cutoff floor(4αC²/K²) is correct for a closed event. If that expression is an integer, subtracting one would be unjustified. The p_0 cap at 1 and the finite-binomial cutoff at m also have the correct direction.

Two nonblocking clarifications would make the standalone specification more explicit:

1. State α>0 and K>0 in the template's hypotheses, in addition to C>A≥2.
2. State β>0 in the displayed Cantelli derivation, or handle β=0 separately: then w=0 and honest acceptance is exactly one.

Neither changes the fixed public parameters or the substantive result.

## 7. Scope of this sign-off

This review supports the new **fixed-vector, one-attempt mathematical JL lemma** and its honest-projection corollary. Three deterministic cases are chosen from w, so taking the maximum of their bounds is correct; their errors are not summed.

It does not establish that a protocol witness is fixed before Π, that computational commitment binding can be conditioned upon without altering Π's law, or that Q fresh attempts retain the one-attempt error. Those are separate protocol obligations. It also does not certify original proof sizes or a 128-bit concrete security claim.
