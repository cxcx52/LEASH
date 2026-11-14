# Peer review: accept-gated unknown-gap extraction

Date: 2026-11-14.

Reviewed snapshots: first Sections 1–7 of `proofs/composition_repair.md`, then the completed Sections 9–12. The addendum below records the second review and supersedes the initial pending-composition status. The finite-anchor and modal-mass foundations were separately reviewed in `proofs/computational_binding_peer_review.md`.

## Verdict for Sections 1–7

**The single-layer unknown-gap extraction argument passes this independent review. No blocking error was found.** It gives one accept-gated expected-polynomial-time extractor, independent of an acceptance-rate or gap estimate, for the relaxed relation R_(sβ), with the explicitly enlarged statistical error

    κ_main = δ_JL + q^(−m) + q^(−d/2) + (r+2)/N.

Before invoking MSIS hardness, the additional computational term is sqrt(L)+η_E, with L and the complete collision samplers defined in the proof. The sharper quadratic-root version of the bound is also valid.

This sign-off is conditional on the cited ordinary-protocol algebra, strict modular-JL premise, uniform independent CRS, allowed initial-state model, and MSIS norm/rank assumptions. It does not certify a concrete parameter set or software implementation. The initial review signed off only the single layer. The later addendum signs off the specified conditional ordinary-layer composition theorem after checking Sections 9–12; it does not assert that the original LaBRADOR schedule satisfies those conditions.

## 1. The executable gate and the saved state

The algorithm makes exactly one initial ordinary run. It does not resample until acceptance. Thus a complete candidate or collision can occur only on the original acceptance event.

The proof correctly preserves the same original accepted gate transcript for every coordinate. For coordinate i, the upper transcript and every c_j with j≠i stay equal to their gate values. A successful fork at a previous coordinate is not substituted as the new gate. This is essential both for the commitment equation used by the certificate and for the gate-weighted runtime calculation.

The step producing a certificate is verifiable. On a distinct accepting fork with the same first packed opening,

    A(z−z^0)=(c_i−c_i^0)t_i.

The challenge difference is a nonzero unit, so S_i is well defined and A S_i=t_i. Centered modular reduction cannot increase the norm of the integer difference, giving ||(c_i−c_i^0)S_i||≤2Z. If the packed openings differ, they open the same first commitment and their difference is a nonzero kernel vector of norm at most 2B.

The algorithm compares openings only on a distinct accepting fork. That is sufficient for this proof. An accepting repetition of the original challenge is treated as an unsuccessful trial; any extra collision detectable on such a repetition need not be exploited.

After all coordinates have certificates, checking the actual input equations and the norm sβ before returning S is necessary and is present. A candidate is not automatically a valid witness. A checked MSIS output is distinguished from a successful witness, and its probability is subtracted in the witness-only bound.

## 2. The stopping probability and exact runtime

Write a=1/N. After fixing the original prover tape and all verifier coins U except c_i, the accepted fraction p is either zero or at least a. The zero case cannot pass the gate and contributes zero mass.

For a row that passes the gate, the probability of a distinct accepting fresh challenge is s=p−a. The independent abort coin is tossed after every other outcome, including an accepting repetition of c_i^0. Therefore

    D=s+(1−s)a=p(1−a)+a²

is the exact per-cycle stopping probability. The expected number of suffix trials is 1/D. Since p≥a, D≥a>0, so every reached loop terminates almost surely.

The expectation must include the unnormalized gate mass p. The relevant quantity is p/D, not 1/D by itself. The inequality

    p/D≤1/(1−a)

is correct. For later coordinates, conditional on the original gate transcript, reaching that coordinate is an event determined by earlier fresh loop coins; it cannot increase expected work beyond always reaching it. All later trial laws remain unchanged because the gate is never updated. Summing gives the pointwise-in-θ bound

    E[number of executions | θ]≤1+r/(1−a).

This is stronger than merely having a polynomial expectation averaged over CRS values. Multiplying by a fixed polynomial per-execution bound and adding polynomial certificate arithmetic establishes the claimed single-layer expected runtime.

## 3. The sharper r/N loss

The abort probability conditional on the accepted row is a(1−p+a)/D. Multiplying by gate mass gives

    p·a(1−p+a)/D≤a,

because

    D−p(1−p+a)=(p−a)²≥0.

This proves a loss of at most 1/N per coordinate, not merely the earlier conservative 2/N. Previous-coordinate aborts can only reduce the mass reaching a later loop. The union bound therefore gives

    Pr[complete candidate or collision | θ]≥ε_θ−r/N.

The original gate coins and all abort coins must have exactly the specified independent laws. Reusing a suffix challenge as the abort coin, omitting the abort trial after a repeated accepted c_i, or changing the saved gate would require a different calculation.

## 4. The gated anchor law in the collision samplers

Replacing the finite capped anchor generator by the gate generator does not invalidate the canonical-mass lemma. That lemma only needs a well-defined completed-anchor distribution and fresh independent suffixes. The gate generator terminates almost surely, and the error functions are zero on failed or collision outcomes ⊥.

Every η remains the unconditional success probability of a complete algorithm:

- run the gate generator once;
- abort the designated sampler on ⊥;
- otherwise perform the stated fresh suffix experiment.

There is no rejection sampling conditioned on obtaining a candidate, and no normalization by the probability of gate success. The modal error mass and Jensen arguments therefore retain

    E[1_Bad(ε_θ−κ)_+]≤L,
    L=η_0+sqrt(η_h)+r sqrt(η_y)+sqrt(η_g).

The saved denominators and norm bounds are unchanged. The fresh projection used by the norm argument is independent of the completed anchor, despite the anchor's dependence on its own earlier projection matrices. The analysis does not condition that fresh projection on absence of collisions.

## 5. The quadratic invalid-candidate bound

Let b_θ be the probability of obtaining a complete invalid candidate at fixed θ. Since the algorithm begins with one original acceptance gate,

    b_θ≤ε_θ.

This is the key property that would fail for the old repeated search until an accepted anchor is found. With B_bad=E[b_θ], the chain

    L ≥ E[b_θ(ε_θ−κ)_+]
      ≥ E[b_θ ε_θ]−κB_bad
      ≥ E[b_θ²]−κB_bad
      ≥ B_bad²−κB_bad

has the correct directions. It does not replace state-dependent ε_θ by ε_bar inside a product. Solving the quadratic yields

    B_bad≤(κ+sqrt(κ²+4L))/2≤κ+sqrt(L).

Subtracting invalid candidates and E's collision outputs from the candidate-or-collision probability proves

    Pr[valid witness]
      ≥ε_bar−r/N−(κ+sqrt(κ²+4L))/2−η_E
      ≥ε_bar−κ−r/N−sqrt(L)−η_E.

No unknown-gap limit or gap oracle is used. The additional r/N term must remain in the reported statistical error, unless a different argument removes it.

## 6. Expected-time MSIS reductions and truncation

The manuscript's expected-time-to-strict-PPT argument is correct **in its stated asymptotic form**.

If an expected-time solver has a uniform polynomial expected runtime P(λ) and nonnegligible success δ(λ), choose a polynomial p witnessing δ≥1/p on an infinite subsequence. Truncation at 2Pp has timeout probability at most 1/(2p), leaving at least δ/2 success on that subsequence. This contradicts ordinary PPT MSIS hardness. The polynomial cutoff may be chosen in this contradiction argument; the extractor itself does not need to know δ or p.

A fixed polynomial cutoff does not automatically have negligible loss. The gate-weighted runtime need not have a uniform rapidly decaying exponential tail. For example, when p is about 1/T and a≪p, a row contributes a gate-and-survival probability of order p(1−p)^T, which is of order 1/T. The conditional loop is geometric, but its rate can be very small. Thus a claim of a uniformly negligible timeout at an arbitrary polynomial T would be false.

The reviewed proof does **not** make that claim. It uses the nonnegligible-success contradiction correctly and separately warns that concrete finite-time bounds need explicit truncation terms, such as

    η_expected ≤ Adv_MSIS(time_limit)+P/time_limit.

Polynomial r and successive square roots preserve negligibility. In particular, sqrt(L) may contain fourth-root losses in the underlying η values; that is asymptotically negligible but may be material in concrete security accounting.

## 7. Model and relation scope

The corrections from the earlier peer review are now explicit:

- the extractor outputs into R_(sβ), not the strict norm-β relation;
- initial instances and prover initialization are generated in a permitted reproducible experiment;
- unexplained CRS-correlated trapdoors/advice are excluded;
- the original prover has a fixed polynomial execution bound and a classical restorable random tape;
- failed/collision anchor outcomes are included in the probability space;
- the matrices attacked by the complete samplers have the stated independently uniform CRS law.

These conditions are sufficient for the single-layer argument reviewed here. If κ_main≥1 for a chosen parameter set, the resulting success lower bound can be vacuous; the implementation's parameter checker should require a useful target error rather than treating the symbolic theorem as a numerical certificate.

## 8. Reproducible arithmetic checks

The independent script `scripts/gated_row_checks.py` is a pure finite probability calculation; it contains no prover or protocol attack implementation.

It verifies:

- 32,893 deterministic rows p=k/N for 3≤N≤256, including the exact D identity, the runtime bound, and the tighter abort-mass bound 1/N;
- 351 distributions of late-final acceptance probabilities for N=3,4,5 with each acceptance probability in {0,1/2,1};
- 12 nonzero late-final examples with p<1/N, which require separate treatment in the planned randomized-final-reply extension.

All assertions passed. These finite checks do not replace the universal proofs above.

## 9. Composition extension: initial checklist, now addressed by the addendum

The complete document available for this review reserves composition in Section 8. The following points have been checked algebraically in preparation, but this section is **not a sign-off on an unwritten recursive theorem**.

For a saved row with late-final acceptance probabilities A_c∈[0,1], put p=N^(−1)Σ_c A_c. Conditional on the gate accepting at c_0, a fresh independent late-final reply gives distinct-success probability

    s_c0=p−A_c0/N,
    D_c0=s_c0+(1−s_c0)/N.

Weighting each gate value by A_c0/N proves the same per-coordinate work bound 1/(1−1/N) and abort-mass bound 1/N. For p≥1/N, use s_c0≥p−1/N and monotonicity; for p<1/N, the entire gate mass is already below 1/N. The finite checks above cover both regimes.

A recursive proof must additionally specify:

1. Every virtual final reply resets the original prover continuation and uses fresh independent extractor-control coins; it must not freeze and replay an inner extractor's unbounded random tape or keep mutable state across calls.
2. All outer-prefix guards remain enforced. An already rejected prefix returns ⊥; when averaging an inner guarantee, an always-reject dummy continuation can represent that branch.
3. The inner semantic extraction guarantee is used on the ordinary original-prefix distribution. Biased fork distributions need the inner extractor's uniform per-state expected **cost**, not an unjustified pointwise semantic negligible-error claim.
4. The extracted cap on the next layer is the cap used by the preceding layer, for example B_i=s_(i+1)β_(i+1). All commitment collision norms must be recalculated at that cap.
5. The runtime multiplication is polynomial. A sufficient explicit condition is that the product of the layer factors 1+r_i/(1−1/N_i), together with uniform local overhead, remains polynomial.
6. For a growing number of layers, MSIS hardness/negligible terms are uniform across the parameter family, or a layer-selection reduction accounts for their sum.
7. A finite base case with verifiable final witness output is supplied.

These requirements cannot be inferred solely from a bound on the expected number of outer oracle calls. They are the remaining checks before signing off the composition section.

## 10. Addendum: completed Sections 9–12 reviewed

**The late-final-reply closure lemma and the conditional ordinary-layer composition theorem pass this independent review.** No blocking error was found in the completed extension. This supersedes the initial pending status in Section 9 of this review. The conditions in the theorem are substantive; this approval does not infer them for an unexamined parameter schedule.

### 10.1 Late-final row calculation

The completed text uses the correct unnormalized gate weight A_c/N, not a distribution conditioned on acceptance. Given an accepted gate challenge c_0, independent new reply coins make the distinct accepted trial probability

    s_c0=p−A_c0/N.

This differs from p−1/N in the deterministic case. The p<1/N case is real, and the completed text handles it separately. When p≥1/N, both the expected-work function and the abort-probability function decrease with s, so replacing s_c0 by p−1/N gives the deterministic upper bounds. When p<1/N, D_c≥1/N bounds work by Np<1, while all abort mass is at most the entire gate mass p<1/N. These steps prove the stated bounds for every row.

The gate is not updated between coordinates. New reply coins are fresh after each restored original prefix, and no persistent cache changes their conditional law. Thus earlier-coordinate survival cannot increase later-coordinate charged work or abort mass. All 351 finite row distributions checked by the accompanying script are consistent with this proof, including the 12 sub-1/N examples.

### 10.2 Modal and polynomial arguments with late coins

The original outer commitments and all other nonfinal messages are fixed by the original prover's tape and the verifier prefix. The late kernel changes only the final reply. Consequently the fresh-projection chronology and the ordering of scalar/ring aggregations are preserved.

Modal distributions now include the late coins. This is legitimate: two suffixes in each collision sampler use independent challenges and fresh independent kernel coins, so their collision probabilities still have the form a²−Σ_v p_v². A selected mode remains independent of the realized varying challenge. On accepted modal branches the same polynomial equation must hold; at each potential root the late kernel can contribute at most probability one. The root set therefore still gives the 2/N bound. No determinization of an unbounded virtual tape is needed or claimed.

The pointwise candidate inequality b_θ≤ε_θ still follows from the single initial gate, now including its late coins. Thus the quadratic bound on invalid candidates is preserved.

### 10.3 Expected cost versus acceptance-correlated cost

A kernel's running time may correlate with whether that invocation accepts. The runtime proof does not assume otherwise. Immediately before an invocation, its input prefix and prior history are fixed; its new coins are independent and its conditional expected time is bounded by C. Reachability of that invocation depends only on earlier coins. The tower property therefore bounds total expected kernel cost by C times the expected invocation count.

This is precisely why the uniform per-prefix bound and fresh coins are needed. An average bound only over honest prefixes, or freezing and replaying an inner extractor's infinite random tape, would not justify the multiplication. The completed text expressly excludes both situations.

### 10.4 Semantic induction and early guards

At layer i, the virtual bare prover's prefix is generated by the original composed prover, not by extracted witnesses from earlier successful forks. Its final response is a verified output of E_(i+1), or ⊥. The inner theorem is applied to the ordinary original-prefix distribution, which is efficiently generated before invoking the inner extractor.

The dummy always-reject continuation on early-failed prefixes is appropriate. Gated extractors, and the explicit-witness base case, return no witness on that dummy acceptance-zero branch. Hence an inner output on an already rejected outer prefix cannot inflate the virtual acceptance probability.

The resulting comparison

    ε(Q_i)≥ε_i−δ_tail

is then used once. The outer theorem treats Q_i as a complete late-final-reply prover on all its rewound prefixes. Thus the semantic error need not be multiplied by the number of outer rewinds. This reasoning does not assume a negligible inner semantic failure bound at every biased or adversarially selected prefix.

### 10.5 Runtime induction and computational reductions

The recurrence

    C_i≤c_i(τ_i+C_(i+1)),
    c_i=1+r_i/(1−1/N_i),

follows from the row work bound and the uniform expected inner cost. Local verifier work, witness checks, arithmetic and challenge generation must remain included in τ_i, as the document states. The explicit final witness provides a finite, verifiable base case.

Requiring polynomial local costs, a polynomial number of layers, and a polynomial product of the c_i is sufficient for polynomial expected total time. A polynomial layer count alone is not sufficient. The completed proof correctly makes the product condition explicit rather than importing it from the informal recursion-depth discussion.

The collision samplers at outer layers execute these nested kernels and must pay their full expected costs. Under the same product condition, the expected-PPT-to-PPT contradiction from Section 6 remains available. The document also correctly requires uniformly quantified hardness/negligible bounds for a growing layer family, or a layer-selection reduction; an uncontrolled sum of individually described negligible functions would not suffice.

### 10.6 Relation and norm matching

The next extractor must return a witness satisfying the exact equations and norm cap checked by the preceding bare verifier. The completed theorem explicitly uses B_i=s_(i+1)β_(i+1), or another proved cap, and recalculates the preceding layer's collision bounds at B_i. This addresses the important distinction between an honest target norm and an extracted target norm.

The resulting source relation is still relaxed by its own specified norm slack. The composition theorem does not establish strict norm-β knowledge, and it does not license retaining ranks or norms chosen for smaller honest caps.

### 10.7 Affine-R1CS corollary

The canonical-opening mass argument for the repaired affine-R1CS reduction accommodates fresh late core-extractor coins. Its two collision experiments each use two fresh calls at the appropriate saved bare prefix. Their norm bound remains 2β_actual, and their expected time is bounded by the core's uniform per-state bound. The fixed-mode chronology relative to the source φ and scalar aggregation challenges is unchanged.

Therefore the corollary's bound

    ε_composed−κ_main−2p^(−ℓ)
      −ν_core−sqrt(η_(src,0))−sqrt(η_(src,1))

is justified under its stated setup, lifting, target-matching and hardness assumptions. The source extractor verifies the decoded affine witness. A core collision or failure is not treated as a source witness.

## 11. Final scope of this review

Reviewed and accepted as conditional mathematics:

- the universal single-layer accept-gated extractor;
- the additional r/N statistical extraction error;
- uniform per-state expected runtime;
- the controlled fresh-final-reply closure lemma;
- additive ordinary-layer semantic composition with a checked polynomial runtime product;
- the affine-R1CS-plus-core extraction corollary.

Not certified by this review:

- a concrete recursive parameter schedule satisfying every premise;
- a numerical MSIS security level after all norm changes;
- the optimized no-outer-commitment final round;
- retries, Fiat–Shamir, ROM/QROM, simulation extractability or non-malleability;
- full honest completeness, performance or the original proof-size claims;
- novelty of the gating or composition method.

The narrow defensible claim is a repaired, explicitly parameterized extraction theorem for the ordinary protocol family. The private repository may preserve it as a reviewable mathematical contribution while retaining these limitations.
