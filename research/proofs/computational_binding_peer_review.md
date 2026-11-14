# Peer review of the finite-anchor computational binding argument

Date: 2026-11-14.

Reviewed: `proofs/computational_binding_review.md`, together with the algebraic cases in `proofs/protocol_repair.md`. This review concerns the repaired ordinary single-attempt protocol with visible final openings. It does not certify optimized final rounds, recursive composition, Fiat–Shamir, QROM, or concrete parameters.

## Verdict

**No blocking algebraic or probability error was found in the finite bound (F), under the model and relation clarifications below.** The anchor construction, collision norms, mode-mass conversions, coordinate factor, invalid-candidate classification, and final averaging can be justified as written.

This is a reviewed *finite, gap-parameterized* result. It should not be relabelled as the paper's exact single-extractor expected-time knowledge theorem: that wrapper is still absent. Nor does this review certify an implementation or instantiate the MSIS assumptions.

There are three publication corrections that should be made explicitly before presenting the scope of the theorem without qualifications:

1. Define the output relation as the **relaxed relation R_(sβ)**: it contains witnesses satisfying all input equations with norm at most sβ. Computational soundness is for statements false in that relaxed relation, not merely false in the strict norm-β relation.
2. Specify a reproducible PPT initial-state experiment and classical reset model, so each alleged sampler is actually an MSIS algorithm. CRS-dependent public instances are allowed when produced efficiently from the challenged CRS; unexplained correlated trapdoors or CRS-dependent auxiliary advice are not covered.
3. Define the anchor experiment's output space to include a failure/collision symbol ⊥ from the beginning, and define all masses as zero there. Every η is an **unconditional complete-algorithm** success probability, not a probability conditioned on producing an anchor.

These corrections make implicit conventions explicit. I did not find a need to change the displayed bound after making them.

## 1. A precise form of the claim being reviewed

Fix a parameter family with common q,d,N,T,b,B,β,s,r and a common upper bound κ_stat<1 throughout the initial-state experiment. If parameters vary with the public instance, use uniform upper bounds, or write a correspondingly conditional theorem; do not average varying quantities as if they were constants.

Let G be a PPT experiment that receives the CRS, generates the public instance and permitted prover initialization, and supplies a classical prover whose state and random tape can be restored. Any nonuniform advice must be permitted by the stated MSIS model; ordinary advice depending only on the security parameter is harmless. Private state or advice with an unexplained correlation to an MSIS challenge is not.

Define

    R_out(x)={S : every input equation holds and ||S||≤sβ}.

Let η_0,η_h,η_y,η_g be the success probabilities of the complete bounded algorithms in the manuscript, including G, the anchor-generation phase and its aborts, and the fresh suffixes. Under these definitions, the reviewed inequality is

    Pr[E outputs S∈R_out(x) OR a checked MSIS solution]
      ≥ E_θ[ε_θ]−κ_stat−Δ−ζ−L/Δ,

where

    L=η_0+sqrt(η_h)+r sqrt(η_y)+sqrt(η_g),
    ρ=κ_stat+Δ<1,
    ζ=exp(−K_0ρ)+r exp(−Kρ(ρ−1/N)).

The adversary's running time is bounded per execution. If an expected-time prover is intended instead, a separate truncation argument is needed; the current (M+2)T_P accounting presupposes a fixed execution-time bound.

## 2. Finite anchor construction and its failure probability

With θ and the prover tape fixed, fixing all verifier coins U except c_i determines a Boolean accepting set in C. If its density is p_U, two independent c_i samples both accept with distinct values with probability

    p_U²−p_U/N.

Averaging and using Jensen gives ε_θ(ε_θ−1/N). This is the correct *unconditioned* pair probability; it does not assume that a row selected after acceptance has typical density.

On such an accepted distinct pair, either an accepted first packed opening differs from the saved a_0, producing a first-outer collision, or both first openings equal a_0. In the latter case the decoded t vectors coincide and subtraction gives

    A(z−z')=(c_i−c_i')t_i.

The inverse challenge difference exists by hypothesis. The resulting s_i* is therefore a valid weak opening, with centered norm of (c_i−c_i')s_i* at most 2Z.

The initial accept-search failure is at most exp(−K_0ρ) on ε_θ≥ρ. The r coordinate failures sum to at most r exp(−Kρ(ρ−1/N)). Previously generated anchor data do not change the fresh U/coin distribution: the prover is reset to the same initial θ, and future pair coins are sampled independently. Early collision outputs are successful outcomes in this part of the proof. The stated ζ and cap M=K_0+2rK therefore have the correct direction.

Since κ_stat≥2/N and Δ>0, the manuscript's requirement ρ>2/N follows from its definitions. It would need to be stated independently if κ_stat were changed.

## 3. Collision samplers and MSIS domination

Each sampler is executable without computing a modal opening. Its actual MSIS success can therefore be bounded by the applicable MSIS advantage at the sampler's full running time, provided the initial-state model above is enforced.

| Sampler | Matrix attacked | Checked collision and norm | Review |
|---|---|---|---|
| C_0 | First outer, concatenated blocks | Difference from the accepted anchor opening, ≤2B | Correct; one fresh execution suffices |
| C_h | Second outer | Difference between two accepted packed h openings at the same upper prefix, ≤2B | Correct |
| C_y | Inner A | d_i(y−y'), ≤8TZ | Correct; d_i is the saved unit and is the same on both branches |
| C_g | Inner A | y−y', ≤2Z+4Tsβ | Correct; only invoked at valid candidate norm |
| E's collision output | First outer | Difference of two valid packed first openings, ≤2B | Correct; its probability is η_E, separate from L |

For C_y,

    A y=Σ_(j≠i)c_j t_j,
    ||d_i y||≤||d_i z||+||c_i d_i s_i*||≤2TZ+2TZ=4TZ.

The challenge-difference operator bound uses the difference of the specified integer lifts, so it is at most 2T. Centered modular reduction can only lower the norm used in these estimates. Because d_i is a unit, y≠y' in R_q^n implies d_i(y−y')≠0. Thus the returned object is a nonzero kernel vector, not merely a difference that might vanish after multiplication.

For C_g the two selected coordinates have individual norm at most sβ, so ||y||≤Z+2Tsβ is a valid conservative bound. The diagonal case needs only one coordinate and obeys the same upper bound.

The independently uniform CRS assumption permits the reduction to embed its challenged matrix and sample all the other matrices. In particular, the first outer matrix must mean the actual concatenation of all blocks multiplying the packed (t,g) opening. A correlated or seeded replacement is not covered merely because it has the same intended dimensions.

Running the whole anchor experiment before each sampler is charged in M. Generating one prefix and then two suffixes costs at most two further full executions, so (M+2)T_P plus polynomial arithmetic is a valid cap. There is no missing M-fold union bound when η already bounds this complete algorithm. A bound on a different one-query game cannot be substituted for η without proving the conversion.

## 4. Modes and unnormalized masses

The elementary inequality is correct:

    c=a²−Σ_v p_v² ≥ a(a−max_v p_v) ≥ (a−max_v p_v)².

Here p_v includes acceptance probability; it is not normalized by acceptance. The canonical mode is an analysis object and is fixed before the *realized* fresh suffix challenges. Selecting a mode using the distribution of possible future challenges does not make it depend on the actual sampled challenge.

For clarity, let A_ext be the extended anchor outcome, taking value ⊥ when candidate generation fails or already emits a collision. Set every e(A_ext)=0 when A_ext=⊥. With this convention,

    E[e_0]=η_0,
    E[e_h]≤sqrt(η_h).

For coordinate slices, define η_(y,i) using an otherwise identical complete sampler with index i fixed. Uniformly sampling i gives η_y=(1/r)Σ_i η_(y,i). Therefore

    Σ_i E[e_(y,i)]≤Σ_i sqrt(η_(y,i))≤r sqrt(η_y).

The factor r is necessary for the sampler currently specified. There is no corresponding r² factor for C_g, because its bad Gram pair is computed efficiently from the anchor and S before the fresh execution.

The manuscript eventually states the extended-zero convention; moving it to the initial definitions would remove the potentially misleading notation E_A when A could be read as conditioned on successful anchor generation.

## 5. Actual h, modal h, and the slice polynomial

The transition from actual bad h to modal h is valid.

At a fixed upper prefix, first discard accepted anchor-consistent transcripts with nonmodal packed h. If the remaining h has a bad diagonal, select one such index i based only on that upper prefix and its modal h. For every fixed c_−i, discard the nonmodal y values on that coordinate slice. Substituting z=y+c_i s_i* into the h-check produces a quadratic with coefficient

    <φ_i,s_i*>−h_ii

at c_i². It is nonzero independently of c_i. The CRT projection where it is nonzero and the unit-difference property of C justify the 2/N root bound. No conditioning on acceptance is needed: the accepted modal transcripts form a subset of the roots under the original uniform c_i law.

The selected i may be noncomputable, because it depends on modal h. Summing the nonmodal y masses over all coordinates and then using the uniform-index C_y sampler correctly handles this fact. The bound

    2/N+e_h(A)+Σ_i e_(y,i)(A)

is therefore justified. No hidden dependence of i on the realized final c vector was found.

The bad-Gram branch is also correct: selecting the first bad pair from known S and anchored g is efficient. The off-diagonal polynomial has coefficient 2(<s_i*,s_j*>−g_ij), which is nonzero because q is odd; the diagonal case is univariate. The 2/N multivariate degree bound uses total degree two and the injective image of C in the relevant CRT field.

## 6. Norm/input cases and the fresh JL test

The anchor and candidate S may depend on projections used during extraction. That is allowed because the analysis uses an additional fresh ordinary execution after the anchor is complete. Conditional on θ and any completed anchor, its new projection matrix has the original independent law. The centered coefficient vector of S is fixed for this new experiment, so the uniform JL lemma applies.

The proof discards inconsistent first openings as **unnormalized mass e_0**, not by conditioning the remaining challenge distribution. This distinction is essential and is respected in the case argument.

For the norm-invalid branch, the four events in the companion algebraic proof remain legitimate:

1. correct projection accepted: bounded by δ_JL;
2. incorrect projection with correctly evaluated b'' relative to fixed g,S: bounded by q^(−m), since p was chosen before scalar aggregation;
3. a residual before ring aggregation is nonzero but disappears: bounded by q^(−d/2);
4. remaining nonzero aggregate accepted: requires some bad actual h diagonal, handled above.

A false input equation at valid norm and correct Gram matrix is handled similarly. In particular, retaining q^(−m) for constant-term constraints is correct. These are event containments under the original challenge law, not conditional-uniformity assertions after accepting or after a collision-free event.

## 7. Integrated invalid-candidate inequality

The invalid candidate classification is exhaustive in the following order:

- norm exceeds sβ;
- norm is valid, but anchored g differs from the Gram matrix of S;
- norm is valid, g is correct, but an input equation fails.

It does not claim that every bad Gram matrix makes S itself invalid; it only uses that bound on the subset where S is invalid. This does not lose or duplicate probability incorrectly.

For each completed invalid anchor, the pointwise estimate ε_θ−κ_stat≤e_0+e_h+Σ_i e_(y,i)+e_g has a nonnegative right side. Thus the same estimate holds after replacing the left side by its positive part. Multiplying by 1_Bad and averaging gives

    E[1_Bad(ε_θ−κ_stat)_+]≤L.

The C_g masses are set to zero outside the norm-valid/bad-Gram branch; all other masses can be retained on every completed anchor, which is conservative. Jensen is applied on the extended unconditional experiment, so no factor for successful anchor generation is missing.

## 8. Verification of the finite bound

Set High={θ:ε_θ≥κ_stat+Δ}. Since ε_θ≤1,

    Pr(High)≥ε_bar−κ_stat−Δ.

On High, the capped anchor procedure produces a candidate or collision except with probability at most ζ, conditional on θ. Integrating loses at most ζ, not ζ times an inverse conditional probability. Also,

    Pr(Bad∩High)≤L/Δ.

Subtracting gives exactly

    Pr(valid relaxed witness OR E's valid MSIS collision)
      ≥ε_bar−κ_stat−Δ−ζ−L/Δ.

This averaging step does not assume a high acceptance probability for every CRS, tape or public instance. The stronger optional bound (ε_bar−ρ)/(1−ρ), when positive, is also correct.

Because E's only collision outputs are already counted as success in (F), η_E should not be added to L. Subtracting η_E to obtain the witness-only statement (W) is correct.

## 9. Consequences and remaining limits

For a statement false in **R_out=R_(sβ)**, the witness-only output probability is zero, yielding the stated computational-soundness inequality. Under an efficiently samplable parameter family, polynomial r, the appropriate MSIS assumptions against these complete samplers, and the proved uniform JL premise, square roots of negligible η values and multiplication/division by inverse-polynomial gaps remain negligible. Choosing an inverse-polynomial Δ from a hypothetical nonnegligible acceptance excess and a negligible ζ gives the intended asymptotic contradiction with polynomial sampling budgets.

This argument is a gap-parameterized family. It does not establish one universal expected-time extractor with the exact success convention ε_bar−κ_stat−negl. The manuscript appropriately leaves that scheduler/wrapper unproved. One must not erase that limitation merely because (F) has passed this review.

Further limitations remain:

- the relation is relaxed by norm slack;
- complete final openings are available in this single-layer experiment;
- replacing them with a recursive proof requires the appropriate composition theorem and charged extraction costs;
- optimized-final-round adaptivity is excluded;
- no ROM/QROM or Fiat–Shamir guarantee is supplied;
- the η values are not numerically instantiated MSIS estimates;
- concrete 128-bit security and proof size remain uncertified.

## Suggested public wording

> For the repaired ordinary single-attempt protocol, in a classical resettable PPT experiment with independently uniform commitment matrices, we prove the explicit finite extraction bound (F) for the relaxed norm-sβ relation, with losses determined by the stated bounded MSIS samplers. This implies asymptotic computational soundness for that relaxed relation under the stated assumptions. A universal extractor meeting the original expected-time convention, recursive composition, and Fiat–Shamir security remain separate obligations.
