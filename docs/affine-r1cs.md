# A repaired affine-R1CS reduction for LaBRADOR

Status: standalone mathematical repair, 2026-11-14. This document gives a precise reduction, an unconditional algebraic theorem for fixed openings, and a computational reduction that accounts for opening changes. It does **not** certify the original 58 KB parameters, the modular-JL theorem, Fiat–Shamir, QROM extraction, or zero knowledge.

The source being repaired is the 34-page version of ePrint 2022/1341, Section 6 and Figure 5. This is a proposed replacement, not a claim about a deployed implementation.

## 1. Rings, representatives, and encoding

Let d≥2 be a power of two, N=2^d+1, and let q≥3 be an odd prime. Set

- R=Z[X]/(X^d+1);
- R_q=Z_q[X]/(X^d+1);
- S=Z_N;
- ρ_q:R→R_q, coefficientwise reduction;
- L_q:R_q→R, the unique degree-<d lift whose coefficients lie in [−(q−1)/2,(q−1)/2];
- φ:R→S, evaluation at X=2 modulo N.

The map φ is a ring homomorphism because 2^d+1=N=0 in S. The composite φ∘L_q is **not** asserted to be a homomorphism on R_q. Norms of R_q vectors always mean Euclidean norms of their coefficientwise centered lifts.

If the principal LaBRADOR protocol requires X^d+1 to have two irreducible factors modulo q, impose that as an additional parameter condition. The algebraic reduction below does not itself need this splitting condition.

### Explicit Enc

For a∈S, let z be its integer representative in [−2^(d−1),2^(d−1)]. Apply the usual signed non-adjacent expansion: for z≠0, choose digit u=0 if z is even and u=2−(z mod 4) if z is odd, output u, and replace z by (z−u)/2. For negative inputs the same recurrence, or sign symmetry, applies. The result is an integer polynomial E(a)∈R; define Enc(a)=ρ_q(E(a)).

The properties used below are:

1. E(a) has coefficients in {−1,0,1}, degree <d, and no two adjacent nonzero digits;
2. φ(E(a))=a;
3. ||E(a)||_2²≤d/2;
4. E(0)=0 and E(1)=1;
5. L_q(Enc(a))=E(a).

For completeness, the recurrence terminates and gives the signed binary identity by induction. If the highest nonzero digit were at position h≥d, the magnitude represented would be at least 2^h−(2^(h−2)+2^(h−4)+...)>2^(h+1)/3≥2^(d+1)/3>2^(d−1), a contradiction. Thus there are at most d digits; non-adjacency gives at most d/2 nonzero digits. These observations prove all the listed properties, including the norm bound. This choice makes Enc fully specified rather than relying on an unspecified short representative.

## 2. The source relation includes constants and public inputs

The public instance is x=(A,B,C,H), with A,B,C∈S^(k×n), H∈S^(h×n). The witness w=(w_0,...,w_(n−1))∈S^n must satisfy

    w_0=1,
    H w=0,
    (A w) ∘ (B w)=C w.                         (AR1CS)

The first coordinate is the constant wire, and **is included in n**.

Public inputs x_j can be fixed by rows w_j−x_j w_0=0 in H. A general affine constraint Lw=u is represented by moving its constant term to the w_0 column. Similarly, affine forms in R1CS are represented in the w_0 columns of A,B,C. Public values and these matrices are part of the statement, not variables chosen by the prover.

This relation does not admit the universal zero witness. It also allows false statements; for example, including the row w_0=0 in H contradicts w_0=1.

**Norm accounting.** If an old formulation counted n_old coordinates without a constant wire, use n=n_old+1 and recompute M below. If its n already counted the constant wire, no extra coordinate is added. The number h of public linear equations increases challenge length but not witness length or the lifting bound, because their coefficients are combined in S *before* encoding.

## 3. Norm budgets and commitments

Choose an integer ℓ≥1 and define

    M=n+(3+ℓ)k,
    β_h²=Md/2,
    B(β)=sqrt(Md/2) β+β²/2.

Here β is the **soundness/extraction** norm budget for the full target witness, not just an honest-prover norm. Require

    β≥β_h,                 B(β)<q/2.           (NW)

The conservative honest bound β_h can be replaced by sqrt((M−1)d/2+1), since Enc(w_0)=1, but no claim below requires that improvement.

Sample independent public uniform matrices

    K_0∈R_q^(m_0×(n+3k)),
    K_1∈R_q^(m_1×(ℓk)).

The necessary ordinary commitment collision bounds are for **MSIS at norm 2β** and these column counts. No claim is made that hardness at norm β suffices.

## 4. Corrected protocol, with chronology made explicit

Boldface variables below denote ring vectors. Plain variables belong to S. The principal relation checks all specified ring equations and the full witness norm.

1. The prover forms a=Aw, b=Bw, c=Cw, encodes all four vectors, and sends

       t_0=K_0 (a_bold || b_bold || c_bold || w_bold).

2. The verifier samples independent uniform vectors φ_1,...,φ_ℓ∈S^k.

3. The honest prover forms d_j=φ_j∘a, encodes them, and sends

       t_1=K_1 (d_1_bold || ... || d_ℓ_bold).

4. For each i∈[ℓ], independently of every other row, the verifier samples

       α_i, b_i, γ_i∈S^k,
       δ_(i,j)∈S^k for every j∈[ℓ],
       η_i∈S^h,

   all uniformly and independently. The name b_i here denotes an aggregation challenge, not the witness vector b.

5. Define the S-valued quadratic function

       f_i(a,b,c,w,{d_j})
         = <α_i,Aw−a> + <b_i,Bw−b> + <γ_i,Cw−c>
           + <η_i,Hw>
           + Σ_(j=1)^ℓ <δ_(i,j), φ_j∘a−d_j>
           + <d_i,b> − <φ_i,c>.                 (F)

   **The residual in the summand is indexed by j.** Every aggregation row tests every d_j relation. The quadratic term retains index i.

6. Before encoding, collect all linear coefficients of (F) in S. In the order (a,b,c,w,d_1,...,d_ℓ), the blocks are

       λ_(i,a) = −α_i + Σ_j δ_(i,j)∘φ_j,
       λ_(i,b) = −b_i,
       λ_(i,c) = −γ_i−φ_i,
       λ_(i,w) = A^T α_i+B^T b_i+C^T γ_i+H^T η_i,
       λ_(i,d_j) = −δ_(i,j).

   Define the R_q-valued function

       F_i(r)=<d_i_bold,b_bold>+Σ_(v=1)^M Enc(λ_(i,v)) r_v,

   for r=(a_bold,b_bold,c_bold,w_bold,d_1_bold,...,d_ℓ_bold).

   In particular, do **not** multiply separately encoded α,A,δ,φ, etc. and then reuse the short-coefficient bound. The operation is “combine in S, then encode each of the M resulting coefficients.”

7. The prover sends g_i=F_i(r)∈R_q. The verifier rejects unless

       φ(L_q(g_i))=0 in S, for every i.          (G)

   This is explicitly a test on centered integer lifts. It is not a divisibility test performed wholly in R_q.

8. In the bare reduction, the prover sends r. The verifier checks the target relation consisting of

       K_0(a_bold||b_bold||c_bold||w_bold)−t_0=0,
       K_1(d_1_bold||...||d_ℓ_bold)−t_1=0,
       w_0_bold−1=0,
       F_i(r)−g_i=0 for every i,
       ||r||_2≤β.                              (T)

   Matrix equations stand for their coordinate equations. All equations in (T) are in R_q and are linear or dot-product equations of the principal relation. In a compiled protocol, replace the transmission of r by an appropriately proved knowledge argument for precisely this target relation.

The extra pin `w_0_bold−1=0` is essential. Merely aggregating a homogeneous representation while leaving w_0 free would reintroduce the zero witness. Honest completeness holds because Enc(1)=1. This exact ring pin does not require a new g value or a new lifting bound.

## 5. Deterministic lifting lemma

**Lemma 1.** Assume ||r||_2≤β and (NW). Set s=L_q(r) coordinatewise. Let

    F_i^Z(s)=<s_(d_i),s_b>+Σ_v E(λ_(i,v))s_v ∈R.

Then every coefficient of F_i^Z(s) has absolute value <q/2, and

    L_q(F_i(r))=F_i^Z(s).

Consequently, if (T) and (G) hold, the decoded S-vectors φ(s_v) satisfy f_i=0 for every i.

*Proof.* A coefficient of a negacyclic product uv is a signed dot product of the coefficient vector of u with a permutation of that of v. Hence its absolute value is at most ||u||_2||v||_2. Applying Cauchy–Schwarz to the M linear products gives

    |coefficient of Σ_v E(λ_(i,v))s_v|
       ≤sqrt(Σ_v ||E(λ_(i,v))||_2²) ||s||_2
       ≤sqrt(Md/2) β.

For the quadratic term, another Cauchy–Schwarz and 2uv≤u²+v² yield

    |coefficient of <s_(d_i),s_b>|
       ≤||s_(d_i)||_2 ||s_b||_2
       ≤(||s_(d_i)||_2²+||s_b||_2²)/2
       ≤β²/2.

The blocks d_i and b are distinct positions in r even when their values happen to agree. Their squared norms therefore both belong to the full norm budget. Summing gives B(β)<q/2, so coefficientwise reduction followed by L_q preserves F_i^Z(s). Applying the ring homomorphism φ now gives exactly (F), by φ(E(λ))=λ. This proves the lemma. ∎

**Why (G) needs this lemma.** When gcd(q,N)=1, X−2 is a unit in R_q: multiplying it by Σ_(j=0)^(d−1)2^(d−1−j)X^j gives −N. Thus “g is divisible by X−2 in R_q” would be vacuous. The repaired test uses φ(L_q(g)), and Lemma 1 supplies the necessary connection to the witness computation.

## 6. Exact aggregation lemma over the composite ring S

Let p be the smallest prime factor of N.

**Lemma 2.** For any nonzero e∈S^t and uniform u∈S^t, and any fixed v∈S,

    Pr[<u,e>=v]≤1/p.

For ℓ independently uniform rows, the corresponding joint affine constraints have probability at most p^(−ℓ).

*Proof.* The image of u↦<u,e> is an additive subgroup/ideal of S with at least p elements: one nonzero coordinate e_j already generates a subgroup of size N/gcd(N,e_j)≥p. A homomorphism maps a uniform input to a uniform point of its image. A prescribed affine target has probability either zero or the reciprocal of the image size. Independence of rows proves the second statement. ∎

No primality of N or invertibility of a nonzero residual is assumed.

## 7. Fixed-opening algebraic theorem

**Theorem 1 (two-stage algebraic error).** Suppose the decoded first block (a,b,c,w) is fixed before the φ challenges, and the decoded d blocks are fixed after φ and before the second-stage challenges. On every branch with w_0=1, the probability that all f_i vanish while w fails (AR1CS) is at most

    κ_alg=2p^(−ℓ).

This statement allows d to depend arbitrarily on φ and on the first transcript. No independence between d and φ is assumed.

*Proof.* Define the first-block linear residual

    U=(Aw−a, Bw−b, Cw−c, Hw).

If U≠0, the second-stage residual vector

    E=(U, φ_1∘a−d_1,...,φ_ℓ∘a−d_ℓ)

is nonzero, regardless of φ and d. Conditional on all the data preceding the second-stage challenges, each f_i is an independent uniform linear combination of E plus the fixed offset <d_i,b>−<φ_i,c>. Lemma 2 bounds joint acceptance by p^(−ℓ).

If U=0 and w is invalid, h=a∘b−c is nonzero. The event

    Q: <φ_i,h>=0 for all i

has probability at most p^(−ℓ), by Lemma 2 and the first-block chronology. Outside Q, if all d residuals vanish, then f_i=<φ_i,h>, so some f_i is nonzero and acceptance is impossible. If some d residual is nonzero, E≠0 and Lemma 2 again bounds second-stage acceptance by p^(−ℓ), conditional on that prefix. A union bound proves the stated 2p^(−ℓ). ∎

## 8. Computational binding is not silently replaced by unique openings

The preceding theorem fixes openings at the right times. Ordinary computational binding alone is not an information-theoretic uniqueness statement: many openings may exist, although finding two short ones is hard. The following argument supplies the missing step with explicit losses.

Fix a polynomial-time prover and its random tape; public-coin provers can be analyzed this way and then averaged over tapes. In the bare reduction, final verification and all openings are efficiently available.

Define two efficient collision experiments:

- **Fork 0:** generate the protocol up to t_0, save the prover state, and run two independent complete verifier suffixes from that state. If both accept and their first-block openings differ, output their difference as a K_0 kernel vector.
- **Fork 1:** generate the protocol up to t_1, including φ, save the state, and run two independent second-stage verifier suffixes. If both accept and their d-block openings differ, output their difference as a K_1 kernel vector.

Let η_0 and η_1 be upper bounds on the respective probabilities, averaged over the CRS, prover tape, and sampled prefix. Each nonzero difference has Euclidean norm at most 2β and is a valid MSIS solution for the relevant matrix. Thus any appropriate MSIS_(m_0,n+3k,2β) and MSIS_(m_1,ℓk,2β) bounds upper-bound these experiments, allowing their actual running times and auxiliary random matrix sampling.

**Lemma 3 (canonical-opening mass).** Except on accepting-transcript probability mass at most sqrt(η_0)+sqrt(η_1), the accepted first-block opening can be treated as fixed before φ and the accepted d-block opening can be treated as fixed before the second challenges.

*Proof.* Fix a first prefix. For each first-block opening v, let a_v be the probability that an independent suffix accepts with opening v, and put a=Σ_v a_v. Select a maximizing v*, breaking ties deterministically. This selection is only for analysis and need not be computed. The probability mass of accepted noncanonical openings is e=a−max_v a_v. The probability that two independent accepting suffixes give different openings is

    c=a²−Σ_v a_v² ≥ a(a−max_v a_v)=a e≥e².

Thus e≤sqrt(c). Average over prefixes and use concavity of square root to obtain E[e]≤sqrt(η_0). The same argument at every second prefix gives the bound sqrt(η_1) for noncanonical d openings. A union bound proves the claim.

The first maximizing opening depends on t_0, the saved prover state and the distribution of future suffixes, not on the realized φ. The second maximizing opening depends on the prefix through t_1, not on the realized second-stage challenges. These are precisely the dependencies required by Theorem 1. If no suffix accepts, choose any canonical opening; its accepted mass is zero. ∎

The square-root losses are deliberately retained. Claiming the exact concrete bound `2p^(−ℓ)+η_0+η_1` from this proof would be incorrect. Under asymptotic MSIS hardness, sqrt of a negligible function is still negligible.

## 9. Repaired standalone theorem and proof

**Theorem 2 (affine-R1CS proof-of-knowledge reduction).** For every public instance x, including false instances, run the bare protocol in Section 4 with the parameter and encoding conditions of Sections 1–3. Let ε(x) be a polynomial-time prover's acceptance probability. There is a polynomial-time extractor with success probability at least

    ε(x)−2p^(−ℓ)−sqrt(η_0)−sqrt(η_1).           (KS)

An honest prover for any witness satisfying (AR1CS) is accepted with probability one in the bare reduction. In particular, under the two stated MSIS assumptions at norm 2β, the reduction has knowledge error 2p^(−ℓ)+negl in the asymptotic formulation.

*Proof of completeness.* Honest encodings have total squared norm at most Md/2≤β². All commitment and constant-wire equations are satisfied. Honest semantic residuals in (F) vanish, including Hw and every φ_j∘a−d_j. Lemma 1 therefore shows that every g_i passes (G). The target equations F_i−g_i=0 hold by construction.

*Proof of extraction.* Run one ordinary protocol execution. Upon acceptance, read the final r, decode w=φ(L_q(w_bold)) coordinatewise, and return it if it satisfies (AR1CS), otherwise return failure. This is polynomial time. On any accepted transcript, the ring pin guarantees decoded w_0=1, and Lemma 1 guarantees all f_i vanish. Remove the noncanonical accepted mass bounded by Lemma 3. On the remaining branches the canonical openings satisfy the required chronology, so Theorem 1 bounds invalid decoded witnesses by 2p^(−ℓ). Subtracting both error contributions from ε proves (KS). ∎

**Quantifiers.** The theorem is for all x and all allowed provers. It does not restrict the assertion to (x,w) already belonging to the source relation. The latter restriction would omit false statements and is insufficient for the claimed result.

## 10. Composition and parameter conditions

Let a separate target proof be complete for honest target witnesses of norm at most β_h and knowledge-sound for all target statements with extracted norm at most β. It must check *all* equations in (T), including the constant-wire pin and both commitments. Its extracted norm β must be used in (NW) and in the 2β MSIS binding assumptions.

The [ordinary-core composition theorem and affine corollary](unknown-gap-extraction.md) supply an all-statements expected-time extractor under explicit fresh-randomness, runtime and relation-matching conditions. With target error κ_core, the composed source knowledge error is bounded by

    κ_core+2p^(−ℓ)+sqrt(η_0)+sqrt(η_1).

This corollary requires those composition conditions and the separate [JL](modular-jl.md) and [challenge](challenges.md) theorems. It does not certify that the original printed Lemma 3.7 or numerical parameters establish its premises. A heuristic norm estimate cannot replace the actual extracted β.

For symbolic slack β=s sqrt(Md/2), the exact sufficient lifting restriction becomes

    Md < q / (s+s²/2).

For the repaired JL slack s=sqrt(23/5), use the exact condition `Md < q/(sqrt(23/5)+23/10)`. The old sufficient value 0.3q should not be retained unchanged. The actual composition must also satisfy the JL modulus restriction and every binding bound.

Adding h public linear constraints does not change this expression or M: their contributions enter the single combined coefficient H^Tη_i on w. It increases second-stage challenges by h scalars per row. If a new constant coordinate is needed, n and M each increase by one. The pin equation adds one principal-relation constraint. Both commitment equations and the ℓ residual equations also contribute to the actual target statement size and must be counted in a full implementation ledger.

## 11. Scope and unresolved obligations

Established here:

- a non-vacuous affine/public-input relation;
- one explicit full-domain short encoding and precise lift;
- the correct aggregation indices and all necessary target equations;
- a deterministic centered-lift bound;
- composite-modulus aggregation with the smallest prime factor;
- a standalone honest-complete reduction and a computational extraction proof;
- explicit 2β binding norm and square-root binding-reduction losses.

Not established here:

- an optimized or necessary lifting threshold;
- a refreshed MSIS estimator result at the changed norms and dimensions;
- preservation of the original principal-protocol JL and challenge parameters;
- a concrete recursive schedule satisfying every condition of the separate composition theorem;
- Fiat–Shamir/ROM/QROM, concurrent or reset-resistant deployment guarantees;
- zero knowledge (the bare reduction deliberately exposes its final witness);
- preservation of the reported proof size or practical running time.

The earlier q=13 honest-lifting example motivates (NW). It is not used as a security attack and is not evidence against a concrete 128-bit MSIS instantiation.
