# Unknown-gap extraction and composition repair

Date: 2026-11-14. This document closes the single-extractor wrapper for the **repaired ordinary main protocol**, with an explicitly enlarged challenge error. It retains the all-statements knowledge-soundness definition and does not take a limit of gap-parameterized extractors. A separate section below treats composition and its runtime conditions.

## 1. Model, output relation, and fixed parameters

Adopt the model corrections in `finite-extraction.md`: a reproducible PPT initial-state generator receives independently uniform CRS matrices; it produces an efficiently generated public instance and a classical resettable prover. No unexplained CRS-correlated advice or trapdoor is available. The original prover has a fixed per-execution polynomial time bound. Its original random tape can be restored. Nonuniform advice is allowed only as permitted by the stated MSIS model.

The output relation is the relaxed relation

    R_out(x)={S : all input equations hold and ||S||≤sβ}.

Soundness below is for that relation, not for the strict norm-β relation. Use the q,d,N,T,b,B,β,s,r,m and uniform modular-JL premise in `protocol-conditional.md`. Let

    a=1/N,
    Z=(b+1)B,
    κ=δ_JL+q^(−m)+q^(−d/2)+2/N.

Require N>2 and polynomially bounded r. Parameters are common throughout the initial-state experiment, or are bounded uniformly before invoking these formulae. All failed/collision anchor outcomes are included as ⊥ in the probability space; their modal error masses are zero.

## 2. One universal accept-gated extractor E_gate

This algorithm receives no acceptance probability, gap, lower bound, or success-rate oracle.

1. Run the original prover once with ordinary fresh verifier challenges. If the verifier rejects, return failure.
2. Save this **original accepted gate transcript**, its packed first outer opening a_0, and its original final challenge vector c^0. Never replace the gate transcript with a later successful fork.
3. For each i=1,...,r, restore the original prover prefix before the final C-challenges. Keep every verifier challenge except c_i equal to its value in the original gate transcript. Independently sample a new c_i uniformly from C and run the suffix.
4. If that suffix accepts with c_i≠c_i^0, compare its packed first outer opening with a_0. If different, output their verified nonzero outer-MSiS difference of norm at most 2B. If equal, compute

       d_i=c_i−c_i^0,
       S_i=d_i^(−1)(z−z^0),

   save the certificate, and continue with coordinate i+1.
5. After **every unsuccessful trial**, including an accepting trial with c_i=c_i^0, toss a fresh independent Bernoulli(a) abort coin. If it is 1, return failure; otherwise repeat Step 3 for the same coordinate.
6. After all coordinates succeed, verify the candidate S against every input equation and the norm bound sβ. Return it only if valid; otherwise return failure.

The abort coin can be implemented without enumerating C: draw an independent uniform c_abort∈C and abort if it equals any fixed c_ref∈C. This has exactly probability 1/N. The draw must be independent of the suffix trial. Challenge-generation work is included in the runtime accounting.

Every saved certificate has d_i≠0, d_i a unit, `A S_i=t_i`, and `||d_i S_i||≤2Z`. A collision is a separate verified output, not a successful witness. For the witness-only extractor it may instead be reported as failure.

## 3. Exact gate calculation

First fix an initial state θ, including the original prover tape. For coordinate i, let U denote all verifier coins except c_i, and let p=p_U be the fraction of c_i values giving an accepting transcript. Rows with no accepting challenge never pass the gate.

On a reached row, p≥a. Conditional on the gate's accepted c_i^0, a fresh suffix accepts with a distinct c_i with probability

    s=p−a.

A trial cycle stops either by obtaining that distinct acceptance, or by aborting after an unsuccessful trial. Its stopping probability is

    D=s+(1−s)a=p(1−a)+a².

Thus the expected number of suffix trials is 1/D, and the eventual abort probability is a(1−s)/D.

### Uniform expected work

The gate has unnormalized mass p on this row, so its contribution to expected suffix work is p/D. Since D≥p(1−a),

    p/D≤1/(1−a).

For coordinate i>1, survival of earlier coordinates only multiplies this mass by a number in [0,1]; it cannot increase the bound. Consequently, for **every** fixed initial state θ,

    E[number of ordinary/suffix executions | θ]
       ≤1+r/(1−a).                             (E)

There is no dependence on ε_θ or a gap. Each loop terminates almost surely because D≥a>0 on a reached row. Expected runtime is polynomial whenever one original execution, challenge generation, and the certificate arithmetic have the stated polynomial cost. It is this per-state uniform expectation, rather than a runtime averaged over the CRS, that will be relevant to composition.

### Gate-mass loss

The unnormalized probability of aborting on a coordinate is bounded by

    p·a(1−p+a)/D≤a,

because the exact identity

    D−p(1−p+a)=(p−a)²≥0

holds. Survival of previous coordinates again only decreases this mass. A union bound over coordinates therefore gives

    Pr[complete candidate OR verified MSIS output | θ]
       ≥ε_θ−r/N.                               (C)

This improves the coarser 2r/N bound. No probability is conditioned on successful extraction when applying (E) or (C).

## 4. Computational binding with the gated anchor law

Replace the finite capped anchor procedure in `finite-extraction.md` by E_gate, stopping before its final candidate-validity check. Use exactly its fresh-transcript collision experiments C_0,C_h,C_y,C_g, and call their unconditional success probabilities η_0,η_h,η_y,η_g. Let η_E be the probability E_gate itself returns an outer MSIS collision.

Their norm bounds remain:

- C_0,C_h and E_gate: 2B at the respective outer matrix;
- C_y: 8T(b+1)B at the inner matrix;
- C_g: 2(b+1)B+4Tsβ at the inner matrix.

Each experiment is an actual expected-polynomial-time algorithm: its anchor phase has the per-state bound (E), and it performs at most two additional fresh complete executions. Those fresh verifier coins are independent of the completed anchor. Modes are still analysis devices, not computed values.

The previously established modal-mass and polynomial-root arguments require no finite cap on the anchor, only its almost-sure termination and the specified independent fresh suffix. They therefore give the same integrated inequality

    E[1_Bad (ε_θ−κ)_+] ≤ L,
    L=η_0+sqrt(η_h)+r sqrt(η_y)+sqrt(η_g),      (B)

where Bad means that a complete candidate is outside R_out. All masses are zero on ⊥ outcomes. In particular, the fresh JL vector is fixed by the anchor before its independent test projection, even though the anchor used earlier projections.

The coordinate factor r in L is retained. The bad h index can depend on a noncomputable modal h; it is covered by the uniform-coordinate C_y experiment. The bad Gram index can be computed from the anchor and S, so C_g needs no r² factor.

## 5. Bounding invalid candidates without an unknown-gap limit

Let

    b_θ=Pr[Bad | θ],           B_bad=E_θ[b_θ].

The initial accept gate gives the pointwise inequality b_θ≤ε_θ. From (B),

    L ≥ E[b_θ(ε_θ−κ)_+]
      ≥ E[b_θ(ε_θ−κ)]
      ≥ E[b_θ²]−κ B_bad
      ≥ B_bad²−κ B_bad.

Hence

    B_bad ≤ (κ+sqrt(κ²+4L))/2 ≤ κ+sqrt(L).    (Q)

This is a direct quadratic inequality. No extractor gap is selected, no Δ tends to zero, and no single average acceptance probability is substituted for all ε_θ.

Combining (C) and (Q), the witness-only extractor satisfies

    Pr[E_gate outputs S∈R_out(x)]
      ≥ε_bar−r/N−(κ+sqrt(κ²+4L))/2−η_E
      ≥ε_bar−(κ+r/N)−sqrt(L)−η_E.             (KS)

All success probabilities refer to the original initial-state distribution. The algorithm always verifies its output witness.

## 6. Expected-time reductions versus standard PPT MSIS

An expected-polynomial-time reduction cannot be described as a strict-PPT reduction without an argument. Here the required argument is asymptotic and uses a hypothetical nonnegligible success probability, not a fixed truncation cutoff.

Suppose an MSIS solver A has expected runtime at most P(λ), uniformly in the permitted experiment, but succeeds with nonnegligible probability δ(λ). On an infinite subsequence suppose δ(λ)≥1/p(λ) for a polynomial p. Truncate A after `2P(λ)p(λ)` steps. Markov's inequality makes the timeout probability at most `1/(2p(λ))≤δ(λ)/2`, so the resulting strict-PPT solver succeeds with at least δ(λ)/2 on that subsequence. This contradicts standard PPT MSIS hardness.

Therefore each of η_0,η_h,η_y,η_g,η_E is negligible under the relevant ordinary PPT MSIS assumptions, provided these complete expected-time algorithms have the proven polynomial expectation and the permitted initial-state generator. Polynomial r, square roots, and fourth roots preserve negligibility, so sqrt(L)+η_E is negligible.

This is **not** a statement that an arbitrary fixed polynomial cutoff incurs negligible loss. For concrete finite-time security, use (KS) with actual expected-time reduction bounds or explicitly include `P/time_limit` truncation terms at the chosen limits.

## 7. Closed single-layer theorem

Under the mathematical hypotheses of `protocol-conditional.md`, the repaired ordinary single-attempt main protocol has one universal expected-polynomial-time classical extractor, independent of the prover's acceptance probability, with

    Pr[valid relaxed witness]
      ≥ε_bar−κ_main−negl,

    κ_main=δ_JL+q^(−m)+q^(−d/2)+(r+2)/N.     (MAIN)

The explicit computational loss before using asymptotic hardness is sqrt(L)+η_E, or the sharper expression in (KS). This preserves the knowledge-soundness definition; it explicitly changes the claimed statistical challenge budget from 2/N to (r+2)/N. If this enlarged budget is unsuitable, enlarge the challenge set or prove a sharper extraction method. Do not continue advertising the old numerical threshold unchanged.

The theorem quantifies over every public statement and extracts into R_out=R_(sβ). It neither proves strict norm-β soundness nor relies on the defective true-statements-only Definition 3.3.

The result applies to the ordinary core with outer commitments. It does not certify §5.6's optimized last round, projection retries, Fiat–Shamir, QROM, or a concrete security estimate. Those exclusions are unchanged.

## 8. Composition status

The single-layer theorem above is complete subject to the explicitly cited algebraic/JL/MSIS premises. The remaining sections give a composition theorem for a specified wrapper class, with explicit freshness, relation-matching, and polynomial runtime-product conditions. They do not infer these conditions merely from the number of layers.


## 9. Late-randomized final replies: the required closure lemma

The composition wrapper below has a special form. With the original prover tape fixed, every message before the final reply of a bare reduction is determined by its verifier prefix. The final reply is generated by a kernel

    K(prefix; ξ),

which may return a witness or ⊥. Its internal coins ξ are freshly sampled **after** the prefix on every invocation; the invocation has no mutable cross-call cache. Restoring an original prover prefix does not restore or freeze the wrapper's old ξ. The distribution of a repeated kernel invocation at the same prefix is identical and independent of previous invocation coins.

Assume there is a bound C on the kernel's expected running time conditional on **every** permitted prefix and original prover state, including prefixes selected by an outer extractor. Ordinary prefix work has a uniform polynomial bound. The uniform bound C is an explicit requirement; an expectation only over honestly generated prefixes is insufficient.

### Row calculation with randomized replies

Fix U, the verifier coins other than c_i. Let a_c∈[0,1] be the acceptance probability of the fresh final-reply kernel at challenge c, and put

    p=(1/N)Σ_(c∈C) a_c.

Unlike a deterministic row, p can lie strictly between 0 and a=1/N. If the original gate accepted at c_0, a new trial is both accepting and distinct with probability

    s_(c_0)=p−a a_(c_0)≥max{0,p−a}.

Its stopping probability is `D_(c_0)=s_(c_0)+(1−s_(c_0))a`. The initial gate's unnormalized weight for c_0 is `a a_(c_0)`.

If p≥a, the functions `1/[s+(1−s)a]` and `a(1−s)/[s+(1−s)a]` decrease with s. Replacing s_(c_0) by p−a and summing the gate weights gives respectively

    Σ_c a a_c /D_c ≤ p/[p(1−a)+a²]≤1/(1−a),

    Σ_c a a_c ·a(1−s_c)/D_c
       ≤p a(1−p+a)/[p(1−a)+a²]≤a.

If p<a, then D_c≥a, so the expected-work sum is at most p/a<1, and the abort mass is at most the total gate mass p<a. Thus the same bounds hold for **all** rows. Rows with p=0 are never reached.

The original gate remains fixed across coordinates. Surviving earlier coordinates only decreases the measure charged to the next one. Therefore (E) and (C) hold unchanged for this class of randomized final replies.

### Algebraic and computational parts

All modal masses in Section 4 are now over the fresh final-reply coins as well as the relevant verifier challenges. The root argument remains valid: a modal accepted transcript must use a root of the fixed polynomial, and the total kernel probability at any root is at most 1. The final C-challenge remains uniform. There is no need to turn the kernel into a deterministic prover by freezing its entire future tape.

The first outer commitment, projection p, b'', and second outer commitment were already sent before the final kernel. Their chronological roles remain unchanged. All returned candidate witnesses are verified. The anchor's fresh JL test is still independent of the anchor's extraction coins. Thus (B), (Q), and (KS) continue to hold.

For runtime, immediately before each new kernel invocation, its chosen prefix and the past are fixed, while its ξ is fresh. The conditional expected cost is at most C. By the tower property, summing over reached invocations bounds total kernel time by C times their expected number. Correlation between an invocation's cost and its own acceptance does not affect this argument: reachability is determined before its fresh coins are sampled.

This proves the closure lemma for the stated wrapper class. It is **not** an extension to arbitrary expected-time provers, to frozen virtual tapes, or to stateful caches with only an average runtime bound.

## 10. Ordinary-layer composition theorem

Consider D repaired ordinary reductions Π_i for i=1,...,D, followed by explicit verification of a final target witness. Each ordinary layer retains its outer commitments; the optimized final round from the original §5.6 is not used.

For each layer define its relaxed source relation R_i and the exact target relation R_(i+1) appearing in its bare verifier. The bare verifier accepts precisely when its early checks hold and its supplied final witness belongs to R_(i+1). The next layer's extractor must return a witness for **this same relation**, including every equation and the actual norm cap.

In particular, if layer i+1 extracts norm at most `s_(i+1)β_(i+1)`, use

    B_i=s_(i+1)β_(i+1)

(or another proved upper bound on that actual norm) in layer i's target check and all its MSIS collision bounds. A smaller honest norm estimate cannot replace B_i. At the final explicit verification use its exact checked cap. Early failures always force ⊥: no inner extraction result can revive a prefix rejected by an outer early check.

Parameters r_i,N_i,κ_i and dimension/runtime bounds must have uniform bounds over all reachable prefixes. They may be fixed in advance as in a parameter manifest; if they vary with public statements, use a proved common envelope. Define

    κ_i=δ_(JL,i)+q_i^(−m_i)+q_i^(−d_i/2)+(r_i+2)/N_i.

At each layer the computational loss ν_i means the actual `sqrt(L_i)+η_(E,i)` for that layer's complete sampler with the wrapper below. No per-CRS or per-prefix computational-binding probability bound is presumed.

### Construction of the recursive extractor

Build from the bottom upward. The base extractor reads and verifies the final explicit witness. To construct E_i:

1. Define a virtual bare prover Q_i which follows the original composed prover through Π_i's complete verifier prefix.
2. If an early check fails, Q_i returns ⊥. Equivalently, for averaging an inner theorem, use an always-rejecting dummy continuation on this branch.
3. At the point where a bare Π_i prover would send its final target witness, run E_(i+1) against the original prover's saved continuation. Use fresh E_(i+1) coins on **each** invocation, restore the original continuation state, and retain no mutable extraction cache between invocations.
4. Q_i sends the inner extracted witness only if it verifies in R_(i+1); otherwise it returns ⊥.
5. Apply the accept-gated E_gate for Π_i to Q_i. Return only a verified source witness, treating any MSIS output as failure in this witness extractor.

Q_i has exactly the late-randomized-final-reply form of Section 9. Its early messages are the original prover's messages, not messages recomputed using a previously selected inner witness.

### Semantic error proof

Inductively assume E_(i+1) extracts a witness for the remaining suffix with error at most

    δ_tail=Σ_(j=i+1)^D (κ_j+ν_j).

Apply that theorem to the efficiently generated **ordinary** Π_i-prefix distribution. Its initial-state generator runs the original prover and the honest Π_i verifier through the prefix. The original composed acceptance probability at this level is ε_i. With the rejected-prefix dummy convention, the virtual bare prover's success is therefore at least

    ε(Q_i)≥ε_i−δ_tail.

Applying the late-reply single-layer theorem to Q_i gives

    Pr[E_i returns a verified R_i witness]
       ≥ε(Q_i)−κ_i−ν_i
       ≥ε_i−Σ_(j=i)^D (κ_j+ν_j).

This proves additive semantic composition. The inner error is **not** multiplied by the number of rewinds. The reason is precise: the inner theorem is used once to compare the ordinary acceptance probabilities of the original continuation and Q_i; the outer theorem then analyzes Q_i as an entire prover, including all of its behavior on rewound prefixes. A separate inner semantic guarantee on every adversarially selected prefix is not assumed.

Computational reductions at layer i do execute inner extractors on many prefixes. Those executions must be charged in their total expected runtime and in the relevant MSIS advantages; they are not free oracle calls.

### Runtime proof and required product bound

Let τ_i upper-bound local original-prefix work, challenge generation, candidate arithmetic and verification at layer i, excluding recursive calls, uniformly over its permitted states. Define

    c_i=1+r_i/(1−1/N_i).

If C_(i+1) is a uniform expected-time bound for E_(i+1) at every continuation state, Section 9 gives, enlarging τ_i to include local bookkeeping,

    C_i≤c_i(τ_i+C_(i+1)).                      (R)

This follows by conditioning before each fresh inner invocation, not by multiplying averages after conditioning on a successful fork. The induction preserves a uniform per-state expected bound.

Expanding (R) gives a sum of local costs multiplied by products of the c_i. A sufficient condition for an expected-polynomial-time extractor is that the number of layers, local costs, dimensions, and the relevant product

    Π_(i=1)^D c_i

are polynomially bounded in the original input/security-parameter size. Fixed D and polynomial local parameters meet this condition. A polynomial number of layers by itself does **not** imply a polynomial product. A growing-depth parameter schedule must check (R) or a sharper bound explicitly.

The MSIS samplers' expected runtimes include the same nested costs plus their extra forks. Under the product bound they are expected-polynomial, and the truncation contradiction of Section 6 converts their nonnegligible success into a strict-PPT MSIS violation.

For fixed D, ordinary per-layer assumptions suffice to make Σ_iν_i negligible. For a growing polynomial layer family require a uniform hardness bound for the efficiently indexed MSIS parameter family, or give an explicit layer-selection reduction with its polynomial loss. One cannot sum an uncontrolled family of differently quantified negligible functions. Independently uniform matrices for every layer, or another explicitly proved efficient embedding of the attacked matrix with the required joint setup distribution, are part of this assumption.

### Result and scope

Under the relation, freshness, setup, and polynomial runtime-product conditions above,

    Pr[E_1 returns a verified relaxed source witness]
       ≥ε_total−Σ_(i=1)^D κ_i−negl.            (COMP)

This is a single expected-polynomial-time extractor for the fixed composed protocol and parameter schedule. It needs no acceptance probability or gap as input. The error is additive with the explicitly enlarged per-layer challenge budgets. It is not a claim that every original LaBRADOR parameter schedule, setup, optimized final round, or slack relation already satisfies these conditions.

The original strict-PPT prover remains strict-PPT. Only the reduction's controlled virtual final-reply kernels are expected-time; their closure is proved in Section 9 and their state-uniform runtimes are tracked by (R). No blanket assertion about arbitrary expected-time adversaries is used.

## 11. Affine-R1CS reduction followed by an ordinary core

A useful narrower corollary follows even without a growing-depth runtime analysis. Use the repaired affine-R1CS bare reduction in `affine-r1cs.md`, including its public-input/constant-wire equations, all target equations, and the centered-lift condition computed at the actual extracted target norm β_actual.

Replace its final target witness by the ordinary core extractor. That extractor's internal coins are sampled only after the bare prefix, independently for each wrapper invocation. Its output is checked against the complete target relation; any early bare rejection forces ⊥.

The virtual bare prover then has acceptance probability at least

    ε_composed−κ_main−ν_core.

The bare reduction's two canonical-opening collision experiments each make at most two such fresh core-extractor calls. Their expected runtime is bounded by two times the core's uniform state bound plus the bounded bare-prefix work. Hence their MSIS success probabilities, η_(src,0),η_(src,1), are negligible under the corresponding 2β_actual assumptions, by Section 6. The bare reduction's fixed-opening algebra and mode-mass proof allow these fresh final-output coins: they are included in each suffix probability, while the mode remains fixed before the relevant scalar challenges.

The source extractor runs one bare prefix, obtains the core target witness once, decodes it, and verifies the affine-R1CS witness. Its success is at least

    ε_composed−κ_main−2p^(−ℓ)
      −ν_core−sqrt(η_(src,0))−sqrt(η_(src,1)),  (AR)

where p is the smallest prime factor of 2^d+1. Its expected time is one bare-prefix cost plus one core-extractor bound and polynomial decoding/verification. Thus the source knowledge error is κ_main+2p^(−ℓ)+negl under the stated assumptions. If the core consists of a composition meeting Section 10, replace κ_main by the corresponding sum.

This corollary still requires the upstream lifting bound at β_actual, source commitment hardness at 2β_actual, and exact matching of every target equation. It supplies no shortcut around those parameter checks.

## 12. What has and has not been completed

Completed here, conditional on the explicitly separated JL and MSIS premises:

- one acceptance-probability-independent extractor for an ordinary main layer;
- the all-statements relaxed-witness guarantee with explicit additional r/N error;
- uniform per-state expected runtime for that extractor;
- extension to controlled fresh final-reply kernels, with the p<1/N case included;
- additive ordinary-layer composition under exact relation matching and a checked polynomial runtime product;
- the affine-R1CS-plus-core extraction corollary.

Still not supplied by these theorems:

- an end-to-end instantiated parameter family with certified challenge cardinalities, strict JL bounds, and refreshed MSIS estimates at every actual norm;
- evidence that the original concrete schedule meets the new error and runtime budgets;
- §5.6's adaptive no-outer-commitment final round;
- a Fiat–Shamir/ROM/QROM theorem or a non-malleability/simulation-extractability theorem;
- a complete honest-completeness/performance analysis for the original decomposition heuristics;
- a proof that the accept-gating method or the composition framework is novel relative to the proof-of-knowledge literature.

In particular, this is a repaired extraction argument for the specified protocol family. It must not be marketed as a new general extraction paradigm without a separate literature comparison.
