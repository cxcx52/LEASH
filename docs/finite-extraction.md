# Computational binding review: a finite main-protocol extraction theorem

Date: 2026-11-14. This extends `protocol-conditional.md` and uses the canonical-mass lemma developed in `affine-r1cs.md`. It concerns the repaired ordinary main protocol only, with outer commitments, a single projection attempt, and the same strict modular-JL hypothesis as `protocol-conditional.md`.

## Result in brief

The ideal promise that every opening in the prover's entire mathematical transcript tree is unique can be removed from a **finite, gap-parameterized witness-or-MSIS theorem**. One efficiently sampled anchor witness suffices. Two-suffix collision experiments account for subsequent inconsistencies. The resulting binding loss contains square roots and an explicit coordinate factor:

    L = η_0 + sqrt(η_h) + r sqrt(η_y) + sqrt(η_g).

Every η refers to an explicitly defined reduction that runs the full bounded anchor extractor and then at most two fresh complete suffixes. It is not a single-query binding advantage. All adaptivity and the extractor's repeated calls are inside these reductions' time bounds.

For any gap parameter Δ>0 with ρ=κ_stat+Δ<1 and a finite sampling budget with failure ζ, the extractor described below satisfies

    Pr[valid witness OR a valid MSIS solution]
       ≥ ε_bar − κ_stat − Δ − ζ − L/Δ.          (F)

A negative right side is read as the trivial lower bound zero. The probability averages over the actual CRS, prover tape, and extractor randomness. No per-CRS binding assumption or per-CRS acceptance lower bound is smuggled into (F).

This closes an asymptotic **computational soundness** consequence under the specified MSIS assumptions and the rigorous JL premise. It also provides a finite extraction family with explicit losses. It does not yet prove a single universal extractor with exactly the original Definition 3.3's expected-polynomial runtime and success `ε_bar−κ_stat−negl`; converting this family to that exact convention remains a separate wrapper obligation. Final-round optimization, Fiat–Shamir, QROM, retries, and concrete 128-bit parameters remain outside the theorem.

## 1. Parameters and conditioning discipline

The output relation is the relaxed relation `R_out=R_(sβ)`: all original input equations must hold, and the extracted witness norm may be at most sβ. Claims about false statements below mean false in this relaxed relation, not merely false for the stricter norm β.

The initial state is produced by a reproducible PPT experiment given the challenged CRS. It may choose a CRS-dependent public instance efficiently, but may not use unexplained correlated trapdoors or challenge-dependent advice outside the stated MSIS model. The prover has a fixed per-execution polynomial time bound and supports classical reset with its same random tape. Across initial states, parameters and runtime bounds are fixed or have the common upper bounds used in the theorem.

The anchor experiment includes an explicit failure/collision output symbol ⊥. All fresh-suffix masses are defined as zero on that output. Every η is the unconditional success probability of its complete bounded algorithm, including initialization and failed anchor attempts; none is conditioned on successful anchor generation.

Use the q,d,C,N,T,b,B,β,s,m,α,J definitions, CRT factorization, uniform challenge distributions, repaired packing, and chronological message order in `protocol-conditional.md`. Set

    Z=(b+1)B,
    κ_stat=δ_JL+q^(−m)+q^(−d/2)+2/N.

Require κ_stat<1. All matrices in the CRS used as Ajtai commitment matrices are sampled independently and uniformly in their specified matrix spaces. Their dimensions must agree with the repaired packed openings.

Let θ denote the CRS, public instance, and fixed prover tape/state before its first message. The public instance may depend on the CRS according to the security experiment, but is fixed before future verifier coins. Let ε_θ be the ordinary one-attempt acceptance probability with this θ, and let ε_bar=E_θ[ε_θ].

Fresh verifier coins used after an anchor has been generated are independent of the anchor experiment. We never condition fresh projection randomness on acceptance, or on the absence of collisions. The anchor depends on θ and on its own extraction coins; that is permitted by the uniform fixed-vector JL hypothesis.

## 2. The elementary canonical-mass lemma

For any fixed prefix/state, let p_v be the **unnormalized** probability that a fresh suffix accepts and outputs value v. Put a=Σ_v p_v and choose a modal v_star attaining max_v p_v, with a fixed tie rule. Define

    e=a−max_v p_v,
    c=a²−Σ_v p_v².

Two independent suffixes both accept with different values with probability exactly c. Since Σ_v p_v²≤a max_v p_v,

    c≥a(a−max_v p_v)=a e≥e²,

and hence e≤sqrt(c). Averaging over prefixes, anchors, and θ yields E[e]≤sqrt(E[c]). Empty accepted support has e=c=0 and requires no modal opening.

A mode is an analysis device; no algorithm is asked to compute it. The mode depends on the saved prefix and the distribution of future suffixes, not on their realized random challenges. This distinction is essential to the polynomial root arguments.

## 3. A bounded anchor extractor E

Choose integers K_0,K≥1. The extractor starts with the fixed θ and retains the same prover tape when rewinding.

1. Run up to K_0 independent ordinary executions until one accepts. Save its packed first outer opening `a_0=(t_digits,g_digits)` and its decoded `(t,g)`. If none accepts, return failure.
2. For i=1,…,r, perform at most K independent pair trials. A pair trial samples all verifier coins U except final ci, then runs two executions with the same U and independently uniform ci,ci'.
3. On **any** accepted execution inspected during these trials, compare the packed first opening with a_0. If it differs, return their nonzero difference as an outer-commitment MSIS solution of norm at most 2B.
4. If a pair accepts twice with ci≠ci', and its packed first openings agree with a_0, compute

       d_i=ci−ci',
       s_i*=d_i^(−1)(z−z').

   Save this one certificate `(s_i*,d_i)` for coordinate i, and continue with the next coordinate. It satisfies `A s_i*=t_i` and `||d_i s_i*||≤2Z`; d_i is a nonzero unit.
5. If a coordinate exhausts its K trials, return failure. Otherwise the extractor has one candidate tuple S=(s_1*,…,s_r*), one anchor (t,g), and one nonzero denominator d_i per coordinate. Verify S against the input equations and norm sβ. Return S if valid; otherwise return failure in the executable extractor, while retaining this invalid-candidate event for the analysis.

A reduction may inspect the candidate before the final validity test. No invalid witness is returned to the user/verifier as a successful extraction.

The maximum number of full protocol executions is

    M=K_0+2rK.

There is no infinite loop and no uncharged search for a heavy row.

### Finite extraction failure

For fixed θ and coordinate i, let p_U be the acceptance density over ci. Then

    Pr[both accept and ci≠ci']
      =E_U[p_U²−p_U/N]
      ≥ε_θ(ε_θ−1/N).

On every such pair, E either obtains the desired certificate or already has a valid outer MSIS collision. Thus, if ε_θ≥ρ>2/N, the probability of failing to produce a complete candidate or a collision is at most

    ζ(ρ,K_0,K)
       =exp(−K_0ρ)+r exp(−Kρ(ρ−1/N)).         (T)

One may use the sharper exact binomial expressions, but (T) is sufficient. For example, `K_0≥ln(2/ζ_target)/ρ` and `K≥ln(2r/ζ_target)/(ρ(ρ−1/N))` make the failure at most ζ_target.

This bound is conditional only on ε_θ≥ρ. Section 7 integrates over θ rather than pretending that every CRS has that acceptance probability.

## 4. Explicit bounded collision reductions

Each experiment below first runs E through the candidate-generation stage, using the same θ distribution as the actual security experiment. If E fails or itself returns a collision, this particular experiment outputs no designated collision. The collision already returned by E is accounted for separately as η_E when deriving a witness-only theorem.

All future verifier coins below are fresh and independent of the anchor. An accepted transcript is called **anchor-consistent** if its packed first opening is exactly a_0. This condition is efficiently testable.

### C_0: first outer opening versus the anchor

Run one fresh complete execution. If it accepts with a different packed first opening, output its difference from a_0. Let η_0 be its success probability. For an anchor A, let e_0(A) be this fresh-execution probability. Then

    E_A[e_0(A)]=η_0.

There is no square-root loss here: one efficiently known opening is already available. The reduction's norm is 2B and its running time includes at most M+1 full executions.

### C_h: second outer commitment at a saved upper prefix

Generate the entire upper prefix through the prover's second outer commitment u2. From that saved state, run two independent final challenge vectors c∈C^r. If both resulting executions accept, are anchor-consistent, and have different packed h openings, output their difference. Let η_h be this success probability.

The norm is 2B. By the canonical-mass lemma, the average accepted anchor-consistent mass with h different from the modal packed h at its upper prefix is at most sqrt(η_h).

### C_y: a weak single-coordinate slice

Choose i uniformly from [r]. Generate a fresh upper prefix and all final challenges except ci. Fork this state using two independent ci values. For each anchor-consistent accepting branch compute

    y=z−ci s_i*.

This is an opening of the same commitment `Σ_(j≠i)c_j t_j`, with the **same saved denominator d_i**, and

    ||d_i y||≤||d_i z||+||ci(d_i s_i*)||≤4TZ.

If the two y values differ in Rq^n, output `d_i(y−y')`. It is nonzero because d_i is a unit, is in the kernel of the inner matrix A, and has norm at most

    8TZ=8T(b+1)B.

Let η_y be this experiment's success probability. If e_(y,i) denotes the nonmodal accepted mass on coordinate-i slices, then

    Σ_i E[e_(y,i)] ≤ Σ_i sqrt(η_(y,i))
                    ≤ r sqrt((Σ_i η_(y,i))/r)
                    = r sqrt(η_y).            (Y)

This factor r must not be omitted. The bad h index may depend on the upper-prefix modal h, which is not efficiently computable, so the reduction samples i uniformly and pays (Y).

### C_g: a strong Gram slice

If `||S||>sβ`, this experiment does nothing. Otherwise compare the known anchor g with the true Gram matrix of S and, if some entry is bad, choose the lexicographically first bad pair `(i,j)` with i≤j. This selection is efficient and fixed before new verifier coins.

If i<j, generate an upper prefix and all final challenges except ci,cj, and fork with two independent challenge pairs. On each anchor-consistent accepting branch compute

    y=z−ci s_i*−cj s_j*.

Both y values open the same complement commitment and have norm at most `Z+2Tsβ`. A difference is a nonzero inner-matrix MSIS vector of norm at most

    2Z+4Tsβ.

For i=j, use one varying challenge and y=z−ci s_i*; the same displayed bound remains valid. Let η_g be the experiment's success probability. The accepted nonmodal mass on these selected slices is at most sqrt(η_g).

There is no r² factor: the bad Gram entry is computed from the already known anchor and S, unlike the modal-h-dependent bad index.

### Different weak denominators

There is no claim that all possible extracted weak openings coincide. E retains just one certificate per coordinate; every C_y comparison uses its same d_i. Thus the proof avoids a separate global canonical weak-opening assumption and its possible sampling loss.

If one nevertheless compares two certificates `(s,d)` and `(s',d')` for the same commitment, where `||ds||,||d's'||≤2Z`, then

    dd'(s−s') = d'(ds)−d(d's')

is a valid nonzero MSIS vector whenever s≠s', and its norm is at most 8TZ. This checks the cross-denominator algebra, but no uncounted comparison of this kind is needed in the theorem below.

## 5. From collisions to approximate algebraic consistency

Fix θ and one completed anchor/candidate A=(a_0,S,{d_i}). All statements in this section concern a fresh, independent ordinary protocol execution.

First discard accepted transcripts inconsistent with a_0, of total mass e_0(A). On the remaining accepted transcripts t and g are exactly fixed, without a computational uniqueness claim.

### h diagonal lemma with computational losses

At every upper prefix, choose a modal packed h. At every coordinate-i slice choose a modal y. If an actual accepted transcript uses both modal values, substituting `z=y+ci s_i*` gives the same nonzero degree-two polynomial as in `protocol-conditional.md` whenever the modal h diagonal is wrong. Its coefficients are independent of ci, and its nonzero quadratic coefficient is `<φ_i,s_i*>−h_ii`.

Choose one bad diagonal index for each upper prefix. The choice is only for analysis and is made before all final c challenges. The root count gives 2/N. All accepted exceptions are covered by nonmodal h or by one of the nonmodal y masses. Therefore the probability of an anchor-consistent accepted transcript with a bad actual h diagonal is at most

    2/N + e_h(A) + Σ_i e_(y,i)(A).             (H)

This statement handles h changes without assuming an opening is globally fixed by computational binding.

### Norm and input-equation branches

If `||S||>sβ`, repeat the four cases in `protocol-conditional.md`: true projection, first scalar aggregation, second ring aggregation, then the bad-h event. The fresh projection is independent of A, so the stated uniform JL bound applies directly. This gives

    ε_θ ≤ κ_stat + e_0(A)+e_h(A)+Σ_i e_(y,i)(A).  (N)

If S has valid norm and g is the correct Gram matrix, but S violates an input equation, the same argument uses the smaller dot budget and therefore still implies (N). The scalar cancellation term q^(−m) is retained for constant-term constraints.

### Bad Gram branch

If S has valid norm but the anchored g is wrong, use the efficiently selected bad entry in C_g. On every slice with modal y, the Gram check is a nonzero polynomial of total degree at most two. Its bad coefficient is fixed independently of the varying challenge(s), and q is odd. Hence

    ε_θ ≤ 2/N + e_0(A)+e_g(A)
         ≤ κ_stat + e_0(A)+e_g(A).             (G)

### Integrated invalid-candidate inequality

Let Bad denote the event that E produces a complete candidate S which is invalid for the input relation with bound sβ. Partition Bad by its norm, Gram, and input-equation properties and use (N)/(G). Averaging over θ and the anchor randomness gives

    E[1_Bad (ε_θ−κ_stat)_+]
       ≤ η_0 + sqrt(η_h)+r sqrt(η_y)+sqrt(η_g)
       = L.                                   (B)

Modes and error masses may be defined as zero when no candidate exists. Applying Jensen on this extended probability space is valid. Equation (B) does not condition verifier randomness on any successful extraction or absence-of-collision event.

## 6. What the MSIS assumptions actually bound

The experiments C_0,C_h,C_y,C_g are concrete reductions against, respectively:

- the first outer matrix at norm 2B;
- the second outer matrix at norm 2B;
- the inner matrix at norm 8T(b+1)B;
- the inner matrix at norm 2(b+1)B+4Tsβ.

Let η_E be the probability that E itself returns a collision during anchor construction. It is an additional concrete outer-matrix MSIS reduction with at most M complete executions. Then an upper bound on its advantage must use that full time bound as well.

For C_h,C_y,C_g, a saved prefix plus two suffixes can be simulated within the cost of at most two additional full executions. Hence each experiment has running time bounded by `(M+2)·T_P` plus polynomial bookkeeping, where T_P bounds one complete prover execution and challenge generation. The adversary/instance-generation costs and matrix dimensions are also part of the reduction specification.

The number M already contains all repeated extraction trials. No assumption of the form “each individual query is safe” is made, so no hidden M-fold union bound is being discarded. If only a per-query bound is available from a different model, it must first be converted into bounds on these full reductions; it cannot be inserted as η without that conversion.

All other CRS matrices can be sampled independently when embedding the attacked uniform matrix. This relies on the specified independent uniform CRS, not on a correlated setup or an unproved seeded-matrix replacement.

## 7. Finite witness-or-MSIS theorem

Take any Δ>0 with `ρ=κ_stat+Δ<1`. Choose K_0,K and let ζ be the value in (T). Define the high-success set of initial states

    High={θ: ε_θ≥ρ}.

Since `ε_θ≤1`,

    ε_bar ≤ Pr[High]+ρ Pr[not High] ≤ Pr[High]+ρ,

so `Pr[High]≥ε_bar−ρ`. On High, E fails to obtain a complete candidate or a collision with probability at most ζ. Also, by (B),

    Pr[Bad AND High] ≤ L/Δ.

Consequently

    Pr[E returns a valid witness or a valid MSIS solution]
      ≥ Pr[High]−ζ−L/Δ
      ≥ ε_bar−κ_stat−Δ−ζ−L/Δ,

which proves (F). A slightly stronger expression replaces `ε_bar−ρ` by `(ε_bar−ρ)/(1−ρ)` when positive.

Since E only returns an invalid-candidate marker as failure and checks every claimed collision, this is an actual finite algorithm, not a nonconstructive choice of modal openings.

For **witness-only** extraction, subtract the probability of E's collision output:

    Pr[valid witness]
      ≥ ε_bar−κ_stat−Δ−ζ−L/Δ−η_E.              (W)

No assumption about all openings in the transcript tree appears in (F) or (W).

## 8. Consequences and the remaining closure question

### Established computational soundness consequence

For a false public statement there is no valid witness, so (W) implies

    ε_bar ≤ κ_stat+Δ+ζ+L/Δ+η_E.               (S)

If all the stated MSIS problems are hard against the actual polynomial-time reductions, r is polynomially bounded, and the fresh modular-JL hypothesis is proved, every η and hence L is negligible. For any hypothetical inverse-polynomial acceptance excess above κ_stat, choose Δ as a sufficiently small inverse-polynomial fraction of that excess and ζ negligible. The sampling budgets remain polynomial, and (S) contradicts that excess. Thus the repaired ordinary main protocol has computational soundness error `κ_stat+negl` in this asymptotic sense.

This conclusion is conditional on an asymptotic parameter family satisfying the JL and MSIS hypotheses; it does not magically produce such a family or a 128-bit concrete estimate.

### Established finite extraction family

Equation (W), including every norm, coordinate factor, sampling cap, and time parameter, supplies a gap-parameterized computational extraction theorem. For a known inverse-polynomial advantage gap, the extractor runs in polynomial time and obtains the appropriate witness except for its explicitly bounded losses. It does not rely on a computable global mode or on information-theoretic binding.

### What has not been closed

The exact paper-style knowledge-soundness convention asks for a **single** extractor with expected polynomial time and success at least `ε_bar−κ_stat` (or its stated linear inverse-gap equivalent). The family (W) introduces a chosen Δ and bounded budgets. A universal unknown-gap scheduler with the required expected-time accounting and success guarantee has not been proved here.

Merely letting Δ tend to zero is not a proof: K grows roughly like `1/ρ²`, and L is the advantage of reductions whose time itself depends on K. A limiting argument must keep these dependencies and the negligible terms under control. Likewise, repeating an unbounded experiment and invoking PPT MSIS hardness is invalid without truncation.

Accordingly, the defensible current wording is:

> The repaired single-attempt main protocol admits the explicit finite computational witness-or-MSIS extraction bound (F), and computational soundness κ_stat+negl under the stated assumptions. Matching the precise expected-time knowledge-extractor convention remains a wrapper obligation.

The optimized last round still requires a separate adaptive-interaction proof. All recursion edges must use their actual extracted norm cap B and a composition theorem compatible with the exact extraction notion finally adopted. Fiat–Shamir/QROM, honest completeness, strict numerical JL instantiation, and end-to-end concrete security remain separate tasks.
