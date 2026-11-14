# Bad-mass-weighted collision losses: a cubic-root refinement

Date: 2026-11-14. Scope: a probability and reduction-analysis refinement for the already specified ordinary classical extraction algorithms. No attack, forged transcript, new prover, or change to the protocol is constructed. The result improves the earlier fourth-root computational term while preserving every reduction's full runtime and MSIS norm obligation.

Sources within this audit are `computational_binding_review.md`, Sections 2–5 and 7, and `composition_repair.md`, Sections 4–7 and 9–10. Their algebraic root bounds, anchor construction, and collision-validity arguments are premises here. The only modifications are to the averaging inequalities and to how the analysis keeps its one bad-coordinate selector.

## 1. Result and exact constants

Use the original statistical quantity

    κ=δ_JL+q^(−m)+q^(−d/2)+2/N,

and the same complete collision experiments C_0,C_h,C_y,C_g, with unconditional success probabilities η_0,η_h,η_y,η_g. C_y chooses one of r coordinates uniformly. Let η_E be the collision probability of the anchor extractor itself. Every probability includes the complete initialization and anchor experiment, including failed anchors.

Define

    K_exact²=(sqrt(η_h)+sqrt(rη_y))²+η_g,
    H=2η_h+2rη_y+η_g.

Then K_exact²≤H. For the universal accept-gated extractor, its invalid-candidate probability B satisfies

    B²−κB ≤ η_0+K_exact sqrt(B).                    (CUBIC)

Consequently,

    B ≤ κ+sqrt(η_0)+(K_exact²)^(1/3)
      ≤ κ+sqrt(η_0)+H^(1/3).                        (LOSS)

There are no extra multiplicative constants on κ or these displayed losses. The witness-only success bound becomes

    Pr[valid relaxed witness]
      ≥ ε_bar−(κ+r/N)−sqrt(η_0)
        −[(sqrt(η_h)+sqrt(rη_y))²+η_g]^(1/3)−η_E,    (KS-REFINED)

or, more simply, the same expression with H^(1/3) as its cubic-root term. In the special case only η_y is nonzero, the exact term is `(rη_y)^(1/3)`; the simplified H bound would unnecessarily insert a factor 2^(1/3).

The earlier square roots and fourth roots were valid upper bounds. They were not required by these same reduction experiments. The revised term follows from retaining the bad-anchor mass during Cauchy–Schwarz, and from retaining the one selected bad index instead of summing all coordinate error masses first.

## 2. One anchor probability space

Let θ include the CRS, public instance, and original prover state/tape. Let A denote the complete random anchor experiment together with θ. Its output is either a completed anchor/candidate or ⊥. Every fresh-suffix mass is zero on ⊥. The law of A is exactly the same in the extraction analysis and in every collision experiment.

For the bounded theorem this is the bounded extractor of `computational_binding_review.md`. For the universal theorem it is E_gate of `composition_repair.md`. The weighted lemmas below apply to either law; only the universal gate theorem will use `Pr[Bad|θ]≤ε_θ`.

After a completed A, generate a fresh upper prefix U through the second outer commitment. Its law may depend on A through θ, but its verifier coins are fresh and independent of the anchor coins. The coordinate choice I in C_y is uniform and independent of both A and U. Given I, generate the other final challenges in their prescribed product distribution and then fork the remaining coordinate with independent draws. In the late-randomized wrapper, each final reply also uses fresh independent kernel coins on each branch. No old virtual reply tape or mutable cache is restored.

These are precisely the original collision samplers; no condition on an uncomputable mode or on Bad is imposed on the sampler. An event may be used in the analysis without being used as a sampling condition.

## 3. Local canonical mass and weighted integration

At a fixed saved prefix, let p_v be the unnormalized mass of anchor-consistent accepting suffixes with value v. Put

    a=Σ_vp_v,      e=a−max_vp_v,
    c=a²−Σ_vp_v².

Use the same fixed mode tie rule as before. Two independent suffixes accept with different values with probability c. The elementary inequalities are

    c≥ae≥e².

For any event D determined by the anchor and any such fresh-prefix variable,

    (E[1_D e])²
       ≤Pr[D] E[1_D e²]
       ≤Pr[D] E[c].                                (WEIGHT)

This is Cauchy–Schwarz on the **unconditional joint law** of anchor and prefix. The final E[c] is the success probability of the same full collision experiment. The event indicator is not dropped before applying Cauchy–Schwarz.

The h error uses prefixes (A,U), so its collision probability is η_h. A coordinate-i y error uses (A,U,c_−i), and the uniform-coordinate average of its collision probabilities is η_y. The g error uses the bad Gram entry selected efficiently from the completed anchor and the corresponding fresh slice; its collision probability is η_g. Setting all errors to zero when a required branch or candidate is absent makes these identities unconditional.

In particular, each averaged e_h(A), e_y,i(A), or e_g(A) separately has its square bounded by the conditional collision mass after averaging the fresh prefix. Thus even without the selector refinement below, one obtains the conservative valid inequality

    E[1_Bad(ε_θ−κ)_+]
       ≤η_0+sqrt(B)[sqrt(η_h)+r sqrt(η_y)+sqrt(η_g)].

This already changes the fourth-root scaling to cubic-root scaling. The next two sections improve its coordinate and branch factors.

## 4. The bad h coordinate does not need to be computable

Fix a completed anchor A and a fresh upper prefix U. Let h_star(A,U) be its modal packed h among anchor-consistent accepting suffixes. This mode depends on the distribution of all future challenges, not on their realized values. If at least one diagonal of this modal h is wrong relative to the anchor candidate, choose the first such index and denote it by

    ι(A,U)∈{1,...,r}.

If no such index exists, leave ι undefined. This selector is fixed **before every final c challenge**, including c_−i. It may be computationally inaccessible; it is only an analysis function.

For a fixed i, let e_i(A,U,c_−i) be the nonmodal accepted y mass on that slice, where y=z−c_i s_i* and the saved weak denominator is the anchor's fixed nonzero unit d_i. Let c_i(A,U,c_−i) be the two-suffix collision mass. The original denominator and norm argument still turns every such collision into the specified inner MSIS solution.

The y exception mass actually needed for the bad-diagonal root argument is

    e_sel(A)=E_U[Σ_i 1_{ι(A,U)=i} E_(c_−i)e_i(A,U,c_−i)].

It need not be enlarged to Σ_i e_y,i(A). The h argument is unchanged: after discarding nonmodal h, a bad actual diagonal means modal h is bad, and the selected coefficient gives the nonzero polynomial. Except for its at most 2/N root mass, acceptance requires nonmodal y on this selected slice.

For an anchor event D of mass b_D, write the expectation using the actual uniform-coordinate experiment:

    E[1_D e_sel(A)]
      =r E[1_D 1_{I=ι(A,U)} e_I(A,U,c_−I)].

Because I is uniform independently of A,U and ι is already fixed,

    E[1_D 1_{I=ι(A,U)}]≤b_D/r.

Applying Cauchy–Schwarz, e_I²≤c_I, and then dropping the indicators only from the collision term gives

    E[1_D e_sel(A)] ≤sqrt(r b_D η_y).                (SELECT)

There is no algorithm for computing a mode hidden in this step. The sampler still selects I uniformly. Its full unconditional collision probability bounds the selected part. The √r factor reflects this uniform sampling; removing it is not justified by this proof.

If actual r varies with the public statement but is uniformly bounded by r_max, the same argument uses r_max: the weighted indicator moment contains `E[1_D r]≤r_max b_D`. No assumption of a constant public parameter is necessary if the stated envelope is used consistently.

## 5. Partitioning invalid anchors

Bad is the event that the completed candidate S is outside the required relaxed source relation. Define the disjoint events

    Bad_G = Bad ∩ {S has valid norm and anchored g is not Gram(S)},
    Bad_N = Bad \ Bad_G,
    B_G=Pr[Bad_G],      B_N=Pr[Bad_N],      B=B_N+B_G.

The intersection with Bad is essential. An anchor could have a wrong auxiliary g even when S itself is a valid source witness; such an anchor is not part of the invalid-output mass being bounded.

On Bad_N, either the norm is invalid or the norm and Gram are valid but an input equation fails. The original norm/equation argument, with the selected h index retained, gives pointwise in A

    (ε_θ−κ)_+ ≤ e_0(A)+e_h(A)+e_sel(A).

On Bad_G, the original selected Gram-entry argument gives

    (ε_θ−κ)_+ ≤ e_0(A)+e_g(A).

Here e_0 is the fresh accepted first-opening mismatch probability, with E[e_0]=η_0. It needs no canonical-mass square root because the anchor opening is already known.

By (WEIGHT) and (SELECT),

    E[1_Bad(ε_θ−κ)_+]
      ≤η_0+sqrt(B_N)[sqrt(η_h)+sqrt(rη_y)]
             +sqrt(B_G)sqrt(η_g).

A two-dimensional Cauchy–Schwarz inequality now yields

    E[1_Bad(ε_θ−κ)_+]
      ≤η_0+sqrt(B) K_exact,                         (WEIGHTED-B)

where K_exact² is as in Section 1. Finally, `(sqrt(η_h)+sqrt(rη_y))²≤2η_h+2rη_y` gives K_exact²≤H. This explains the asymmetric coefficients 2,2r,1 in the rational linear expression H.

Every occurrence of η is still the success probability of its full collision experiment, on the original complete anchor law. The proof does not assume computational binding pointwise in the CRS, after conditioning on Bad, or on a chosen upper prefix.

## 6. Universal gate: root equation and explicit loss

Let b_θ=Pr[Bad|θ]. The original accept gate ensures b_θ≤ε_θ for every θ. Therefore

    E[1_Bad(ε_θ−κ)_+]
      =E_θ[b_θ(ε_θ−κ)_+]
      ≥E_θ[b_θ²]−κB
      ≥B²−κB.

Combining this with (WEIGHTED-B) proves (CUBIC).

For the sharp scalar bound supplied by this inequality, let R be the largest nonnegative solution of

    R²−κR−η_0−K_exact sqrt(R)=0.                    (ROOT)

When η_0 or K_exact is nonzero, there is a unique solution strictly above κ. When both vanish, take R=κ. Equivalently, t=sqrt(R) is the largest nonnegative root of `t⁴−κt²−K_exact t−η_0=0`. The one positive-root property follows from the single sign change, or by noting that `(R²−κR−η_0)/sqrt(R)` is strictly increasing for R≥κ, R>0. Thus B≤min(1,R).

If a rational upper bound H≥K_exact² is used, a positive rational R_bound≥κ certifies an upper root whenever

    D=R_bound²−κR_bound−η_0≥0,
    D²≥H R_bound.

The zero value must be treated separately: it is an upper bound only when κ=η_0=H=0. Otherwise squaring at R_bound=0 would accidentally certify a spurious zero root.

The simple bound (LOSS) avoids solving the root equation. Put A=sqrt(η_0) and C=K_exact^(2/3). If B>κ+A+C, then B>A,C and

    η_0=A²≤AB,
    K_exact sqrt(B)=C^(3/2)sqrt(B)≤CB.

The right side of (CUBIC) is then at most (A+C)B, strictly below `(B−κ)B`, a contradiction. This proves (LOSS) with no extra factor two. Subtracting B and the extractor's own collision probability η_E from the unchanged candidate-or-collision lower bound `ε_bar−r/N` gives (KS-REFINED).

## 7. The bounded, non-gated anchor theorem is different

The bounded anchor extractor may try several initial executions before choosing an accepting anchor. Its bad-candidate probability need not satisfy b_θ≤ε_θ. The cubic-root conclusion must not be applied to it by silently assuming a single gate.

The weighted inequality still applies. Fix the original gap Δ>0, let High={θ:ε_θ≥κ+Δ}, and let B_H=Pr[Bad∩High]. Repeating the weighted partition with the event Bad∩High gives

    Δ B_H≤η_0+K_exact sqrt(B_H).

Solving the quadratic in sqrt(B_H) yields

    B_H≤[(K_exact+sqrt(K_exact²+4Δη_0))/(2Δ)]².       (FINITE-ROOT)

One may cap this at one. A simpler rational expression, using H≥K_exact², is

    B_H≤2η_0/Δ+H/Δ².                               (FINITE-SIMPLE)

It follows from `K_exact sqrt(B_H)≤(Δ/2)B_H+K_exact²/(2Δ)`. Thus the original finite witness-only theorem remains valid with L/Δ replaced by the right side of (FINITE-ROOT), or by (FINITE-SIMPLE):

    Pr[valid witness]
       ≥ε_bar−κ−Δ−ζ−B_H_upper−η_E.

The finite execution cap, ζ estimate, norm bounds, and advantage time parameters remain exactly those of the bounded theorem. The sampler does not need to compute High; it is only an integration event.

## 8. Runtime, late replies, composition, and restarts

No new collision sampler is required. C_0,C_h,C_y,C_g still run the complete anchor phase and at most two fresh complete suffixes, with the same norm bounds:

- η_0,η_h,η_E: the corresponding outer matrix at norm 2B_target;
- η_y: the inner matrix at norm 8T(b+1)B_target;
- η_g: the inner matrix at norm 2(b+1)B_target+4Tsβ.

Here B_target is the target-opening norm bound denoted B in the original extraction documents; it is not the bad-candidate probability B used in this note.

The expected-time-to-PPT truncation argument remains necessary, unchanged. A fourth root being replaced by a cube root does not justify ignoring the complete nested runtime, truncation losses, or matrix-embedding conditions.

The fresh late-reply kernel model of the reviewed composition theorem supplies the same independent conditional suffix distributions, so all weighted and selector arguments continue to hold. Replace each layer's old computational loss by the corresponding refined term using that layer's complete collision experiments. The semantic composition proof and runtime-product conditions are otherwise unchanged.

For bounded complete-protocol restarts, each initializer Gen_j includes its preceding rejected ordinary attempts. The refined bound applies to that complete initial-state experiment, giving its own η quantities and refined loss. One then uses the reviewed first-real-acceptance coupling and sums those losses. This does not justify multiplying a single unconditional advantage by the attempt count without checking the different initialized samplers, nor does it create a per-CRS binding guarantee.

Under the original uniformly quantified asymptotic MSIS assumptions, square roots and cube roots of negligible functions remain negligible. The result improves concrete algebraic losses but does not itself establish any numerical 128-bit claim.

## 9. An abstract cubic-root scale example

The following finite probability example explains a limitation of these inequalities, not of LaBRADOR as a whole. It supplies no ring elements, commitments, witnesses, or protocol transcripts.

Fix one θ and choose b=1/m with integer m≥2. Let ordinary acceptance be ε_θ=b. The anchor produces a bad candidate with probability b and otherwise ⊥, so B=b and the gate inequality is exact. On a completed bad anchor, there is one upper prefix and r=1. A fresh suffix has three possible outcomes:

| Outcome | Probability |
|---|---:|
| accept with labels (h0,y1) | b/2 |
| accept with labels (h1,y0) | b/2 |
| reject | 1−b |

Break modal ties lexicographically, so the modal labels are h0 and y0. They never occur together in an accepted suffix. Thus the modal-root exception requirement is satisfied even with zero accepted modal-root mass. The nonmodal masses and collision probabilities are

    e_h=e_y=b/2,
    c_h=c_y=2(b/2)²=b²/2.

After the full anchor experiment,

    η_h=η_y=b³/2,
    η_0=η_g=0,
    K_exact²=2b³.

For a small illustrative statistical allowance, choose N=2m⁴ and κ=2/N=b⁴. The probabilities can all be represented by a finite uniform suffix space: each accepted label occupies m³ of its N points. The required inequality `ε_θ≤κ+e_h+e_y` holds, and the no-joint-modal condition is stronger than its root-count requirement.

As b tends to zero, B−κ is of order b while each full two-suffix collision probability is of order b³. Therefore these gate/canonical-mass/root-exception summary conditions alone cannot imply an error `o(η^(1/3))`; in particular they cannot justify a linear loss in η. The example does not prove a lower bound for actual protocol extractors, or rule out exploiting additional algebra, a different sampler, or a better reduction.

## 10. Exact probability checks

Run:

    python scripts/computational_loss_refinement_checks.py

The script uses only integers and `Fraction`. Completed checks cover 35 accepted-mass distributions, 4900 weighted Cauchy cases, 140 upper-prefix/coordinate-selector cases, 6075 gate/Jensen cases, 48048 rational root-bound candidate checks, the spurious-zero-root boundary, finite-gap bounds, and five exact instances of the abstract cubic-root scale example. It also exhibits why dropping the coordinate factor altogether would fail for uniform coordinate sampling.

These finite checks support the probability bookkeeping. The proofs above establish the general claims. No public-package theorem or interface is modified by this research note pending its independent review.
