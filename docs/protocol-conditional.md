# A parameterized repair of the LaBRADOR main-protocol argument

Status: conditional algebraic/extraction theorem for the ordinary outer-commitment protocol. This document isolates the algebraic argument. The [finite computational theorem](finite-extraction.md) and [universal expected-time extractor](unknown-gap-extraction.md) separately replace its uniqueness promises. These results do not certify an implementation, the optimized final round, or Fiat–Shamir.

Source: the local 34-page LaBRADOR PDF, SHA-256 `87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581`; principally pp. 6–9, 12–19, and 32–34. The corrections below are derived from its equations. Date: 2026-11-14.

## 1. First repair the specification

1. Knowledge soundness must quantify over **every public statement x**, not only pairs `(x,w)∈R`. The extractor receives x and oracle access to the prover, not a supplied witness. State the efficient-adversary and auxiliary-input conventions explicitly when claiming computational knowledge soundness.
2. A weak opening `(s*,cbar)` must have `cbar∈(C−C)\{0}` and `t=A s*`. Every such cbar is a unit by the challenge-set hypothesis. Its bound is `||cbar s*||≤Bweak`, using the specified centered coefficient norm.
3. Fix one packed representation for symmetric g,h: retain the upper triangle `i≤j` exactly once. Figure 3 Line14 must use this same index set for the g,h norm terms. The algebraic checks involving `Σ_{i,j} g_ij c_i c_j` still use all ordered pairs; changing the norm packing does not change those algebraic sums.
4. Include the checks on the projection p and the constant coefficients of every b'' in the complete verifier predicate. They occur before the final witness check in Figure 2 and must not disappear from an executable verifier.
5. Define one attempted session to contain exactly one fresh projection matrix. Retries and Fiat–Shamir queries are outside the theorem below and require an explicit policy.
6. In the first outer commitment, the matrices multiplying g must have the output rank of u1. Retaining the paper's `κ1=κ2` avoids the dimensional conflict in the Figure 2 caption; if allowing different ranks, correct the C-matrix dimensions accordingly.

## 2. Parameters and explicit hypotheses

Let q be an odd prime and let

`Rq = Fq[X]/(X^d+1) ≅ F_(q^(d/2)) × F_(q^(d/2))`,

where the two factors are distinct and irreducible of degree d/2. More general factorization patterns would change the `q^(−d/2)` term.

Let `C⊂Rq` be a finite set of size `N>2`. Its law is exactly uniform; for any distinct c,c' in C, `c−c'` is a unit. For fixed integer lifts of these challenges, multiplication has operator norm at most T. The N in this theorem is the size **after** every rejection condition, not the number of raw candidates. A rigorously certified lower bound `N_min≤N` can replace N in conservative error budgets.

The main-protocol instance has r witness blocks of n ring elements, an input norm parameter β, a decomposition base b≥2, and an actual target-opening norm cap B. From the consolidated norm check and `z=z^(0)+b z^(1)` we use the safe bound

`||z||≤(b+1)B`.

Here B is the cap actually guaranteed by the verifier or by extraction from the next layer. It must not silently stand for a smaller honest-prover estimate.

Let λ>0 be the desired first-aggregation budget and choose an integer

`m=ceil(λ/log2(q))`,

so `q^(−m)≤2^(−λ)`. Direct integer comparison `q^m≥2^λ` is preferable to floating-point ceilings in a parameter checker.

The projection has J rows and is sampled independently of the witness fixed below. Its acceptance check is exactly

`||center_q(Πw)||₂ ≤ α β`.

For some extraction slack s≥1, assume a **proved uniform modular lower-tail bound**:

> For every fixed centered coefficient vector w in the required dimension with `||w||₂>sβ`,
> `Pr_Π[||center_q(Πw)||₂≤αβ] ≤ δ_JL`.

This hypothesis must include its valid q, β, s, α, J, and dimension range. In particular, a theorem only covering `<αβ` cannot be silently used for a verifier accepting `≤αβ`. The present repair does not assert a numerical value of δ_JL; that value must be supplied by a separate valid theorem or certificate. Ordinary real-valued JL concentration alone does not establish this modular hypothesis.

All verifier challenges are independent and uniform in their specified domains. The scalar aggregation coefficients ψ,ω are sampled only after p. The ring aggregation coefficients are sampled only after b''. The final C-challenges are sampled only after h is committed.

### The bounded-opening uniqueness promise

For the algebraic theorem, assume the following exact uniqueness properties hold for the deterministic prover and all of its accepting transcripts under consideration:

- The first outer commitment fixes its short packed opening (t,g), independently of all verifier challenges.
- Once the upper challenges are fixed, the second outer commitment fixes h independently of the final C-challenges.
- Each inner commitment has a unique weak opening of bound `2(b+1)B`, among all nonzero challenge differences.
- For the slice arguments below, openings with a common challenge difference and weak bound `4T(b+1)B` are unique.
- Strong openings of bound `(b+1)B+2Tsβ` are unique.

These are exact mathematical promises for this theorem. They are **not an automatic consequence of computational binding for every possible transcript**. Section 7 states what remains necessary to replace these promises with Module-SIS assumptions.

## 3. Conditional main-protocol theorem

Define

`δ_norm = δ_JL + q^(−m) + q^(−d/2) + 2/N`,

`δ_dot = q^(−m) + q^(−d/2) + 2/N`,

and

`κ_stat = max{δ_norm, δ_dot, 2/N} = δ_JL + q^(−m) + q^(−d/2) + 2/N`.

Assume `κ_stat<1`. Under all hypotheses in Section 2, a fixed deterministic prover with acceptance probability `ε>κ_stat` has an extractable witness satisfying all the input full-polynomial and constant-term equations, with coefficient norm at most sβ.

A universal restarting pair extractor needs no knowledge of ε and obtains the r weak openings in expected

`O(r/[ε(ε−1/N)])`

complete-protocol oracle executions. Thus its runtime is polynomial in the instance size and the inverse acceptance gap when the gap is inverse-polynomial. A more efficient capped-heavy extractor with a supplied valid lower bound `ε≥ρ>2/N` takes expected

`O(r/(ρ−2/N))`

oracle executions. Local ring arithmetic and challenge generation costs must be included in an implementation-level runtime.

This statement deliberately distinguishes two claims:

- the conditional algebraic/extraction theorem proved here;
- the exact expected-polynomial/success-probability definition in a final computational proof of knowledge.

The computational replacement of uniqueness is supplied in [finite-extraction.md](finite-extraction.md); [unknown-gap-extraction.md](unknown-gap-extraction.md) gives the universal extractor with the larger statistical error `κ_stat+r/N`. The quadratic inverse-gap bound of the simple pair extractor in this document is distinct from that accept-gated algorithm.

## 4. Extraction and its finite expected runtime

Freeze the prover's random tape; the first message u1 is then fixed. Let all verifier coins except final ci be denoted U, including the other final challenges. Let `p_U` be the fraction of ci∈C producing an accepting transcript at this U. Then `E_U[p_U]=ε`.

Run the prover twice with the same U and independently uniform ci,ci'. The probability of two accepting transcripts with distinct challenges is exactly

`E_U[p_U²−p_U/N] ≥ ε²−ε/N = ε(ε−1/N)`.

The inequality is Jensen (or nonnegativity of variance). On success, the fixed outer opening ensures the same t_j in both transcripts, and subtraction of the commitment equations gives

`A(z−z')=(ci−ci')t_i`.

Since `ci−ci'` is a unit, set

`s_i*=(ci−ci')^(−1)(z−z')`.

Then `A s_i*=t_i` and

`||(ci−ci')s_i*||≤2(b+1)B`.

Restart the entire pair when it fails. This avoids the unbounded wait on a light row left implicit in the original prose. Repeat for i=1,…,r; weak-opening uniqueness makes the resulting tuple canonical for the fixed commitments.

For the alternative capped-heavy construction, first obtain one accepting transcript. Among its induced rows, the conditional probability of `p_U≥ρ/2` is at least 1/2: rows of smaller mass contribute at most `(ρ/2)/ε≤1/2` of the accepted distribution. In a heavy row, a fresh challenge gives a distinct accepting transcript with probability at least

`ρ/2−1/N`.

Try at most

`L=ceil(ln(2)/(ρ/2−1/N))`

fresh challenges, then restart with a newly sampled accepting transcript. Conditional on a heavy row, success within the cap is at least 1/2; a cycle therefore succeeds with probability at least 1/4. Its expected work is at most `1/ε+L` plus fixed overhead, giving the asserted `O(1/(ρ−2/N))` cost per coordinate. This algorithm is stated with the valid supplied lower bound ρ; no success-rate oracle is silently presumed for the universal extractor.

## 5. Algebraic proof of the statistical threshold

### 5.1 A bad diagonal of h costs at most 2/N

Fix the upper transcript and a bad index i, where

`h_ii != <φ_i,s_i*>`.

It is fixed before all final challenges. In an accepting transcript write `z=y+ci s_i*`. Multiplying by the particular nonzero challenge difference used for s_i* shows

`||cbar_i y|| ≤ ||cbar_i z|| + ||ci(cbar_i s_i*)|| ≤ 4T(b+1)B`.

When only ci varies, y opens the same commitment with the same cbar_i. The uniqueness promise fixes y throughout that slice. The h verification equation is then a polynomial in ci of degree at most two, with nonzero quadratic coefficient `<φ_i,s_i*>−h_ii`.

A nonzero polynomial over Rq has a nonzero image in at least one CRT field. The image of C in either field has N distinct points because all pairwise differences are units. Consequently there are at most two roots in C, giving a bound 2/N. No factor r is needed: for each fixed upper transcript, select one bad index before the final challenges, and the same 2/N bound applies to the entire event.

### 5.2 A witness exceeding sβ forces ε≤δ_norm

Let the extracted canonical coefficient vector w have norm greater than sβ. Partition accepting transcripts as follows.

1. If p equals the true modular projection of w, the projection check passes with probability at most δ_JL by the explicit hypothesis.
2. If p is not the true projection, but all b'' are honestly evaluated relative to the fixed g and extracted s*, the m constant checks vanish with probability at most q^(−m). A nonzero projection residual is multiplied in each row by an independent uniform ω coefficient; p was sent before these coefficients. This argument does not yet require g to equal the true Gram matrix.
3. If some b'' is not that evaluation, the vector of residual ring equations is nonzero before the second aggregation. Its independently uniform ring coefficient makes the aggregate zero with probability at most q^(−d/2), because at least one CRT component is nonzero.
4. If the aggregate residual is nonzero while the final verifier accepts, at least one h diagonal is bad. Section 5.1 bounds this event by 2/N.

Their union yields `ε≤δ_norm`, contradicting the assumed success probability. Therefore `||w||≤sβ`.

All these are unconditional event bounds over the original challenge experiment. One must not condition on acceptance and then continue treating verifier randomness as uniform.

### 5.3 The fixed g equals the true Gram matrix

For a bad diagonal entry, the same univariate slice argument applies. For a bad off-diagonal entry (i,j), write

`z=y+ci s_i*+cj s_j*`.

Now that the norm bound is established, y is a strong opening of norm at most

`(b+1)B+2Tsβ`.

With all challenges except ci,cj fixed, the relevant commitment is fixed, so uniqueness fixes y on this two-dimensional slice. The Gram equation becomes a nonzero polynomial of total degree at most two in ci,cj, since its ci cj coefficient differs by twice the bad Gram entry. q is odd, so multiplication by 2 is invertible.

Apply the usual two-variable degree bound in a CRT field where the polynomial is nonzero, on the injective image of C. Its acceptance probability is at most 2/N. The bad index is global because g and the extracted witness are fixed. Thus any bad g would imply `ε≤2/N`; the hypothesis rules this out.

### 5.4 A violated input equation forces ε≤δ_dot

Now substitute the correct Gram matrix.

If any constant-term input constraint is false, its nonzero residual vector is subjected to m independent scalar aggregation rows. All such rows can lose the residual with probability at most q^(−m). This is precisely the term missing from the last paragraph of the original Appendix B.

Outside that event, at least one residual ring equation supplied to the second aggregation is nonzero (including a dishonest b'', if necessary). If a full-polynomial input constraint was already false, this conclusion holds without requiring the scalar-cancellation event. In either case the second random ring aggregation loses it with probability at most q^(−d/2). If it is not lost, acceptance requires a bad h diagonal, which contributes at most 2/N.

Hence `ε≤δ_dot` if any required input equation fails, a contradiction.

### 5.5 Why the norm and dot budgets are not added

These are contradiction bounds for different possible properties of the **fixed canonical extracted witness**, not independent failure events of separate randomized outputs:

- if its norm is too large, `ε≤δ_norm`;
- once the norm is valid, a wrong fixed Gram matrix implies `ε≤2/N`;
- once the Gram matrix is correct, a false input equation implies `ε≤δ_dot`.

Therefore the sufficient threshold is their maximum, not `δ_norm+δ_dot+2/N`. No claim is made that κ_stat is a tight lower bound or the actual failure probability.

## 6. Mapping the uniqueness bounds to candidate MSIS parameters

The same algebra as the original Appendix B gives these **candidate reduction bounds**:

| Role | Collision bound needed |
|---|---:|
| First/second outer commitments | `2B` at their respective ranks |
| Arbitrary-denominator inner weak openings, and same-denominator slice openings | `8T(b+1)B` at inner rank κ |
| Strong two-coordinate slice openings | `2(b+1)B+4Tsβ` at inner rank κ |

Thus the candidate inner bound is

`max{8T(b+1)B, 2(b+1)B+4Tsβ}`.

These bounds control collision-vector length; they do not by themselves establish hardness at the chosen modulus, rank, dimension, or challenge law. A Core-SVP estimate is not a proof of the computational reduction or of κ_stat.

For recursion, use the **actual extracted cap at each edge**, for example `B=s_next·β_next` if the next layer proves only that enlarged relation. Recompute all collision bounds at that B. State compatible completeness and soundness relations at each edge; applying the composition lemma to mismatched exact and slack relations is not justified merely by naming a slack factor. Once the relations and actual single-layer theorems match, the corrected composition lemma gives the sum of their individual knowledge errors.

## 7. Computational proof obligations and their resolution

The phrase “MSIS is hard” cannot turn a computational commitment into an injective function on every mathematical opening. The separate finite and accept-gated proofs address the following obligations for the ordinary core:

- Run a finite-time version of the relevant extractor with explicit time/oracle-call bounds.
- Whenever the needed consistency fails on two sampled transcripts, output the corresponding nonzero MSIS vector, proving both the norm bound and nonzeroness.
- Account for adaptive transcript selection, r coordinates, all calls, truncation, and success losses.
- Justify that the witness used in each fresh JL test is fixed independently of that test's projection randomness. Conditioning on “no collision found” is not a substitute for this independence argument.
- Extend the deterministic-prover argument to the prescribed randomized/advice-bearing prover model.
- Supply the appropriate unknown-success-rate wrapper if claiming precisely the paper's expected-polynomial extractor/success-probability convention.

Only after those steps can an explicit computational failure/reduction term be attached to κ_stat. An expression such as `κ_stat+Adv_MSIS` is a placeholder unless the reduction and its multiplicative/query/time losses are actually proved. If a separate coupling theorem supplies a concrete statistical bad-event bound η while preserving the required challenge laws, adding η is legitimate; computational binding alone does not supply that coupling theorem for free.

## 8. Items explicitly excluded from this repaired theorem

- **Optimized last round (§5.6):** it sends garbage terms adaptively and removes outer commitments. The “fixed h before all c” hypothesis used above fails. The text's `2r/N` analysis must be rebuilt for its complete h/g checks and combined with the norm and aggregation checks. Do not reuse κ_stat unchanged.
- **Projection retries:** Q fresh independent attempts against a fixed bad witness have a bad-projection probability `1−(1−p)^Q≤Qp`. Adaptive full restarts require their own overall experiment and computational accounting. The theorem is for one attempt.
- **Fiat–Shamir and QROM:** this document gives no ROM/QROM compiler theorem or query loss. A noninteractive implementation must label that guarantee as unproved until supplied.
- **Completeness/performance:** δ_JL is a soundness hypothesis. Honest acceptance rates, decomposition tails, actual serialization size, and expected retry costs require separate bounds or explicitly labelled experiments. The old Gaussian heuristics do not become theorems through this repair.
- **R1CS encoding:** correctness of the upstream binary/arithmetic reductions, public-input handling, integer lifting, and their own error terms are separate obligations.
- **128-bit security and 58 KB:** neither is certified by this document. Filtered challenge counting, modular JL, concrete MSIS estimates, all rounds, encoding, and compiler losses must all be instantiated first.

## 9. Open-source release gates

An initial release can honestly provide an experimental implementation and reproducible audit, accompanied by this conditional theorem. It should expose a machine-readable parameter manifest with q,d, the complete factorization certificate, N or a certified N_min, challenge law, T, J, α, β, s, m, B at every edge, all commitment ranks and collision bounds, retry policy, and the exact protocol variant.

The parameter checker should refuse to print a certified end-to-end security level when any of these entries lacks a proof/certificate. Keep exact rational error terms separate from numerical logarithmic displays and distinguish measured challenge acceptance rates from proven cardinality bounds. Publish test vectors for packed upper-triangle norm accounting, centered modular projection, aggregation order, nonzero challenge differences, and transcript serialization. Those are correctness tests, not a replacement for the cryptographic proof.

Recommended release label: **experimental repaired-specification prototype; conditional single-attempt algebraic/extraction guarantee; no certified Fiat–Shamir or optimized-final-round security yet**.
