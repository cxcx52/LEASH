# Concrete backend candidates and their limits

Date: 2026-11-14. This is a research note with explicit candidate propositions, not a claim of an implemented faster backend or S&P-ready novelty. The ordinary-core extraction/composition theorem and the affine-R1CS repair are prerequisites, with their current scopes and hypotheses.

## 1. Candidate proposition: a parity-source frontend

Let d be an even power of two, R=Z[X]/(X^d+1), and let q_t be an odd target prime. Define

    φ_2:R→F_2,     φ_2(f)=f(1) mod 2.

This is a well-defined ring homomorphism because 1^d+1=0 in F_2. Set E(0)=0 and E(1)=1, and Enc=ρ_(q_t)∘E. Then φ_2(E(a))=a and ||E(a)||²≤1.

Use the repaired affine-R1CS source relation over F_2:

    w_0=1,    Hw=0,    (Aw)∘(Bw)=Cw.

Use exactly the corrected two-stage protocol of `proofs/r1cs_repair.md`: all j-indexed residuals, both commitment equations, the pin w_0,bold=1, and F_i−g_i are retained. Combine the source linear coefficients in F_2 before applying Enc. Interpret every sent g_i by its centered lift in R, then apply φ_2.

Put M=n+(3+ℓ)k. A sufficient condition is

    sqrt(M) β_actual + β_actual²/2 < q_t/2.             (P)

The honest opening norm is at most sqrt(M). The source aggregation error is 2^(1−ℓ), and the ordinary source commitments require MSIS collision bounds at 2β_actual. If the target backend has knowledge error κ_backend and extracts openings of norm at most β_actual, the source extraction error is

    κ_backend+2^(1−ℓ)+source-binding losses.

For ℓ=λ+1, the source's statistical contribution is at most 2^(−λ).

### Proof and a crucial soundness distinction

Every linear coefficient encoding has squared norm at most one, so the coefficientwise Cauchy–Schwarz argument from the R1CS repair gives sqrt(M)β_actual instead of sqrt(Md/2)β_actual. The quadratic part is still bounded by β_actual²/2. Condition (P) therefore makes centered lifting exact for the aggregate residuals.

Applying φ_2 gives the genuine source equations over F_2. The two fixed-opening aggregation stages have error at most 2·2^(−ℓ), and the same two canonical-opening collision experiments supply the computational binding terms.

**Soundness does not assume that extracted target ring elements have constant coefficients or equal Enc(bit).** Extracted elements may be arbitrary centered polynomials satisfying the norm bound. Their decoded values φ_2(Lift(element)) are nevertheless bits, and the source equations hold on those decoded bits. Only honest completeness uses the constant encodings 0 and 1. This avoids importing an unproved coefficient-binariness claim.

If β_actual=s sqrt(M), condition (P) becomes

    q_t > (2s+s²)M.

The backend's own modular-JL restriction and all of its MSIS collision parameters must also hold. For the current concrete slack s=sqrt(23/5), this source-lifting coefficient is 2sqrt(23/5)+23/5, approximately 8.889522118. This number alone is not a full parameter certificate.

This proposition is a direct specialization/generalization of the repaired proof, using a different source homomorphism. It is not claimed to be a new general arithmetization technique.

## 2. Candidate proposition: an exact-relation Boolean bridge

Let P_x(z) be a decidable relation with an explicitly specified Boolean verifier circuit C_x of G gates. The witness input has L_w bits. The public instance x is either fixed in the circuit or bound through explicit public-input wires; it must not be silently supplied as an unconstrained private input.

Compile C_x to affine R1CS over F_2:

- an AND gate u·v=t is one rank-1 constraint;
- an XOR or NOT gate is an affine linear equation, expressed using w_0=1;
- the output is pinned to one;
- constant/public wires are pinned by H.

The number of witness wires and constraints is O(G+L_w), so the parity frontend uses

    M=O(ℓ(G+L_w)).

Applying Proposition 1 yields a knowledge-preserving reduction from P_x to the target principal relation over R_(q_t), provided (P), commitment hardness and the target backend hypotheses hold. Extraction decodes the F_2 wire assignment, checks the circuit constraints, and returns its witness-input bits. No homomorphism between the old and new coefficient prime fields is required.

The bridge is perfectly correct as a bare relation reduction: a satisfying Boolean assignment maps to the honest constant encodings. A composed proof inherits the honest completeness limitations of its chosen backend and must count them separately.

### Exact old-modulus and old-norm semantics

In particular, let P_x describe a witness z∈R_(q_s)^V satisfying specified modular equations and an **exact** centered norm bound ||z||²≤B_s². The Boolean checker must verify:

1. canonical residues 0≤z_(j,k)<q_s for every coefficient;
2. every modular equation at q_s;
3. the centered representative convention, including tie conventions if a nonprime/even source modulus is allowed;
4. the integer sum of centered coefficient squares and the exact comparison with B_s²;
5. all relevant public-input/constant constraints.

An extracted satisfying Boolean assignment then yields an actual q_s witness with norm at most B_s. The lower backend's opening slack affects β_actual and condition (P), but **does not enlarge the decoded old bound B_s**. In this precise interface sense the bridge resets propagation of the norm slack across that edge.

This is a stronger interface than merely reducing every old ring coefficient modulo q_t. It is also a standard circuit-verification mechanism at its core; novelty and practical advantage have not been established.

## 3. Checker size: count the operations, not just witness length

Let L_arith be the number of scalar/ring arithmetic operations in the exact public predicate being checked, after its public coefficients are available. Let L_s=ceil(log_2 q_s), and include in L_bnd the bit length of the exact rational/integer norm threshold. A straightforward schoolbook Boolean compilation has size bounded by a polynomial in

    L_arith, d, L_s, log V, L_bnd,

and is linear in L_arith up to the usual bit-arithmetic factors. For example, a conservative bound using naive negacyclic multiplication is

    G=O((d² L_arith+dV)·(L_s+log(dV)+L_bnd)²),        (B-size)

when L_arith counts ring-level operations and the public constants have the stated bounded size. Tighter compilers may improve this; the displayed bound is a construction upper bound, not an optimality claim.

For a completely general dense quadratic system, L_arith may be quadratic in V. Witness length alone does not imply a near-linear checker. That case would not preserve the desired recursion contraction.

### What the ordinary LaBRADOR target actually supplies

The p. 15 target equations are stated to be linear in the packed t,g,h part, with a sparse/tridiagonal quadratic pattern confined to the two z pieces. Given the already prepared public coefficients, their checking arithmetic is O(K'V) ring operations up to rank/dimension bookkeeping, where K'=κ+κ_1+κ_2+3. Equivalently, count directly the inner matrix-vector product, two outer matrix-vector products and the three dot-product equations; all matrix dimensions must be charged.

This makes a Boolean bridge after an ordinary fold *plausibly* of size V times polylogarithmic and security-parameter factors. It is not automatic from V alone, and an implementation must emit L_arith and the gate count for each actual target.

### Public preparation is a different cost

Preparing these public coefficients from the original challenges can still take Θ(W_i d) dense work. For example, forming Σ_i c_i φ_i before checking its inner product with z scans the original collection of public coefficient vectors. The dense JL construction has the same issue.

There are two different experiments:

- **Bridge only the prepared target relation:** G can depend on the small target arithmetic, but the verifier still pays the original public-preparation cost.
- **Bridge the whole public preparation as well:** a literal circuit compilation must count all that dense work in L_arith/G. It can make the next witness Ω(W_i) up to factors and destroy the desired shrinking recurrence.

A new structured, preprocessed or delegated verification mechanism is needed to avoid this trade-off. The Boolean bridge alone does not turn the construction into a SNARK with a fully succinct verifier.

## 4. Conditional communication improvement from modulus resetting

Suppose an ordinary fold produces V_i=O(W_i^(2/3)poly_λ(log W_i)) ring elements, and suppose its **actual prepared target checker** has G_i=O(V_i poly_λ(log W_i)) Boolean gates. The parity bridge then has M_i=O(ℓG_i).

If a next-layer modulus/rank schedule can be instantiated with log q_(i+1)=O_λ(log M_i), honest/actual norm budgets satisfying (P), the backend's JL condition, the enlarged (r+2)/|C| challenge budget, and appropriate MSIS hardness, the recursion can retain

    W_(i+1)=O(W_i^(2/3)poly_λ(log W_i)).

This is compatible with the local-modulus accounting in `proofs/architecture_limits.md`, so the specific fixed-global-q multiplicative log log factor need not persist. The frontend's extra commitments and ℓ residual ring messages must be included; they contribute their own security-dependent multiples of log q_(i+1).

This is a **conditional communication proposition**. The following have not been shown:

- an optimized concrete Boolean compiler for the complete prepared target;
- a full modulus/rank/challenge family preserving the required MSIS hardness;
- polynomial extractor runtime for the chosen cross-modulus schedule, including the reviewed composition product;
- competitive proof size or prover time;
- a fully succinct verifier;
- Fiat–Shamir or QROM security for the resulting composed protocol.

In particular, fixed d,T and a fixed challenge cube do not support arbitrarily growing r with fixed knowledge error under the current extractor. The challenge-entropy constraints in the architecture note must be met. Bounds that hide a growing ring rank or challenge norm inside a constant are not an instantiated O_λ(log W_0) proof.

## 5. Related-work checks that constrain novelty

The following descriptions are deliberately narrow and based on checked primary records and the listed local PDFs. They do not assert absence of a result elsewhere in the literature.

| Work | Checked fact relevant here | Consequence for this project |
|---|---|---|
| [Greyhound, 2024/1293](https://eprint.iacr.org/2024/1293) | Uses LaBRADOR on a smaller relation to obtain sublinear polynomial-evaluation verification. Local introduction read. | Composing LaBRADOR into a PCS is already established. |
| [Hachi, 2026/156](https://eprint.iacr.org/2026/156) | Uses same-characteristic extension-field/ring switching and offers a generic extension-field evaluation reduction; local pp. 4 and 7–8 read. | Generic extension-field support or “ring switching” alone is not a new claim. It does not itself establish cross-prime coefficient-modulus resetting. |
| [RPS, 2024/1972](https://eprint.iacr.org/2024/1972) | Gives modular verifier-succinct reductions, exact-norm/binary relations and CRT/embedding consistency tools; the primary record notes a later CRT theorem correction. Local relevant sections searched/read. | Exact norm interfaces and CRT consistency have substantial prior art. A new bridge must compare assumptions and cost, not merely name the property. |
| [RoK and Roll, 2025/1220](https://eprint.iacr.org/2025/1220) | Uses structured projections and intermediate ring towers to obtain verifier-efficient arguments; local norm-gap discussion and parameter table read. | Replacing dense projection and controlling recursive norm growth are already explicit research lines. |
| [SALSAA, 2025/2124](https://eprint.iacr.org/2025/2124) | Exposes sumcheck over bounded-norm relations and develops more expressive applications; the local PDF includes AIR and norm-aware interfaces. | A universal norm-aware frontend/backend or AIR support is not sufficient novelty. |
| [Non-Malleable Reductions of Knowledge, 2026/1822](https://eprint.iacr.org/2026/1822) | The checked primary abstract explicitly analyzes LaBRADOR simulation extractability and presents a ZK variant. Full text was not available in this branch. | “Add ZK/non-malleability to LaBRADOR” is not a viable novelty claim without a narrower new theorem. |

### Version provenance

The local files used here have hashes:

- LaBRADOR: `87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581`;
- Hachi: `c7c98591c2576ecd8403d22e63861cb322d2995b0a88f0bc234f161afd5e6a15`;
- Greyhound: `cec9aa888c5a26733b78d61e5002265b6bc44571d43d94fc4d70b70511ce1cf9`;
- SALSAA: `d5788e068508afbf730c5b79cd76287246586ae4d902c2e8ac071103f8f522fe`.

The current SALSAA ePrint abstract and the local PDF contain different performance numbers and application wording. This note does not mix them into a numerical comparison. No claim is made to have read the full 2026/1822 paper.

## 6. Falsifiable next milestones

The most useful next artifact is an explicit prepared-target Boolean checker with a machine-readable operation/gate ledger. It should report separately:

1. public preparation cost L_pre, including dense JL-derived coefficient formation;
2. target arithmetic count L_arith and actual Boolean gate count G;
3. old modulus q_s, new modulus q_t, old exact norm B_s and new β_actual;
4. M=n+(3+ℓ)k, all source commitments, ℓ, and statistical/binding errors;
5. per-layer challenge cardinality and T, actual MSIS ranks/norms, and extractor runtime factor;
6. proof messages added by the bridge and the preserved online verification work.

A concrete candidate passes only if it improves a specified metric against a fully counted baseline while preserving a stronger exact interface. If G is effectively Ω(W_i) for the required verifier workload, or the new ranks/norms erase the commitment savings, the proposed route should be recorded as a negative result rather than marketed as a faster backend.

At present, the parity frontend and exact Boolean bridge have a defensible mathematical specification. Their novelty, efficient instantiation and superiority to existing norm-aware/SNARK backends remain unproved. The discrete recursion floor and fixed-global-modulus lower bound are useful architecture diagnostics, but alone do not establish a top-conference contribution.
