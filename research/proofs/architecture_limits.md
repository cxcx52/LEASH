# Architecture limits of ordinary LaBRADOR recursion

Date: 2026-11-14. Status: explicit conditional lower bounds and design constraints, not a lower bound for all lattice proofs or SNARKs. These propositions concern the ordinary outer-commitment architecture in the 34-page local LaBRADOR version, principally pp. 15 and 21. The optimized last round is excluded wherever it changes the recurrence.

No novelty claim is made. Several ingredients are elementary and their value here is to specify exactly which architecture changes a stronger backend must make.

## 1. Cost model

At layer i, let W_i=r_i n_i be the number of witness **ring elements**, before padding. Ordinary recursion retains the two decomposition pieces of z and the decomposed t,g,h material. With inner rank κ_i≥1 and t_(1,i),t_(2,i)≥2, its target length obeys

    W_(i+1) ≥ 2W_i/r_i + r_i t_(1,i) κ_i
                  +(t_(1,i)+t_(2,i))(r_i²+r_i)/2.       (1)

Padding can only increase this length. This follows from the explicit m and 2n counts on p. 15; it is not inferred from an informal upper bound on recursion depth.

For the communication statement, assume the two outer commitments are transmitted separately in their ordinary full coefficient representation. Their cost is at least

    d_i(κ_(1,i)+κ_(2,i)) log_2 q_i bits.                 (2)

This is a **wire-format cost assumption** matching p. 21. It is not an entropy lower bound conditional on a public CRS and does not rule out a different commitment representation, preprocessing, or a different proof backend.

## 2. Proposition A: a discrete minimum witness size

Suppose κ_i≥κ_min≥1 at every ordinary layer. Define

    F_κ = min{18κ+72,16κ+80}.

Then an ordinary layer can strictly reduce W only if W>F_(κ_min). Moreover, if W≥F_(κ_min), its next witness length is also at least F_(κ_min). Consequently a chain starting above this threshold cannot cross below it using only these ordinary reductions.

*Proof.* From (1),

    W_next≥2W/r+2r²+2(κ+1)r.

For r≤2, the first term is already at least W. For an integer r≥3, strict shrinkage requires

    W > T_κ(r):=2r²(r+κ+1)/(r−2).

At r=3 this is 18κ+72; at r=4 it is 16κ+80. For r≥4,

    T_κ(r)−T_κ(4)
      = 2(r−4)[κ(r−4)+r²+5r−20]/(r−2)≥0.

Thus the minimum over integer r≥3 occurs at r=3 or r=4. At W=F_κ every r gives W_next≥F_κ; monotonicity of the right side in W proves the invariant for W≥F_κ. ∎

For κ_min=1, the floor is **90 ring elements**, not the weaker continuous-relaxation fixed point 54. For κ≤4, r=3 attains the threshold; for κ≥4, r=4 does, with equality at κ=4. This is a dimension floor, not a claim that each terminal element needs log q transmitted bits: digit bounds and a different terminal format may change its bit cost.

The result explains why a terminal disclosure or a structurally different final backend is necessary. It does not prohibit the original §5.6 optimization or another protocol from bypassing this floor.

## 3. Proposition B: a recursion-depth lower bound

Ignoring the positive linear-in-r terms in (1),

    W_next≥2W/r+2r²≥3·2^(1/3) W^(2/3).                 (3)

The second inequality is the minimum over positive real r, achieved at r=(W/2)^(1/3). Since (3·2^(1/3))³=54,

    W_i ≥ 54 (W_0/54)^((2/3)^i)                       (4)

for W_0>54. If the ordinary chain reaches W_I≤H(W_0), with H>54, then

    I ≥ log_(3/2)( log(W_0/54)/log(H/54) ).             (5)

In particular, H=(log W_0)^O(1) implies I=Ω(log log W_0). If H lies below the discrete floor in Proposition A, ordinary recursion cannot reach it at all; a terminal protocol change is required.

This is a necessary layer-count estimate. It is not obtained by reversing the paper's O(log log W_0) upper bound.

## 4. Corollary: the fixed-global-modulus bit barrier

If every ordinary layer uses the same q, a common d≥1, and both outer ranks are positive, (2) and (5) imply

    communication_outer ≥ 2d log_2(q) · Ω(log log W_0).

In the arithmetic-R1CS route, the repaired centered-lift condition gives q=Ω(W_0 d) when the initial witness consists of W_0 encoded source elements and the honest norm is Θ(sqrt(W_0 d)). Therefore, for fixed d,

    communication_outer=Ω(log W_0 log log W_0).         (6)

Additional projection messages, constraints, terminal disclosure, rank growth and security-parameter dependence can only add costs within this model.

Scope of (6): fixed global q; the ordinary witness recurrence; enough layers to reach a polylogarithmic terminal witness; the stated full-coefficient commitment format. It is **not** a general lower bound for lattice-based arguments, a barrier for all parameterized encodings, or a refutation of every possible O(log n) construction.

## 5. Proposition C: a local-modulus schedule can avoid that particular factor

The global modulus is a substantive hypothesis. Suppose a modified architecture has

    W_(i+1)≤C_λ W_i^(2/3)(log W_i)^c,

until a security-parameter-dependent terminal size, and uses

    log q_i≤a_λ log W_i+b_λ.

Once W_i is sufficiently large, the recurrence implies W_(i+1)≤W_i^(3/4), after enlarging a terminal threshold depending on C_λ,c. Hence

    Σ_i log W_i=O(log W_0)+security-dependent terminal cost.

If d_i(κ_(1,i)+κ_(2,i)) is bounded by A_λ, the **outer-commitment part** can therefore have cost

    O(A_λ a_λ log W_0)+security-dependent terms.

Thus layer-dependent moduli can remove the specific multiplicative log log W_0 cost. This is an accounting proposition, not a construction: it assumes a knowledge-preserving cross-modulus bridge, its witness overhead, valid MSIS parameters, appropriate challenge cardinalities, and the stated rank bound. None follows from simply choosing smaller q_i in an implementation.

At fixed security parameters, an additive per-layer constant contributes O(log log W_0), which is absorbed in O(log W_0). For joint asymptotics, keep all security-dependent terms explicit rather than hiding them in a claim of optimality.

## 6. Proposition D: plain reduction modulo a new prime is not a bridge

For distinct primes q and p, there is no unital ring homomorphism

    Z_q[X]/(X^d+1) → Z_p[Y]/(Y^e+1).

*Proof.* A map preserving 1 would send q·1=0 to q·1=0 in characteristic p, forcing p|q, hence p=q. ∎

This rules out a very specific shortcut: changing the coefficient modulus and expecting all ring equations to remain equivalent by a unital algebra map. It does not rule out a protocol proving cross-modulus consistency, an integer/carry representation, a Boolean circuit bridge, or a randomized evaluation reduction.

### CRT dropping

If P divides a composite Q, a natural quotient map R_Q→R_P does exist. But it has a nontrivial kernel whenever P<Q. For example, the constant P is nonzero modulo Q and zero modulo P. Therefore preserving the reduced equations only proves a weaker relation. If allowed integer residuals include ±P, small-modulus zero checks alone cannot recover their original zero status.

A sound CRT transition must retain enough information to establish the original relation: e.g. all necessary components, certified quotient/carry relations, or an independently proved no-alias bound. Merely dropping components is not knowledge preservation.

### Distinguish Hachi's ring switching

Hachi's local PDF, p. 4 and pp. 7–8, switches R_q relations to polynomial/extension-field statements over characteristic q and evaluates a polynomial indeterminate at an extension-field challenge. This does not lower the coefficient characteristic from q to a different prime. Its generic extension-field reduction and the cross-prime bridge required here are different interfaces. This observation limits our use of the word “ring switching”; it is not a novelty claim against Hachi. [Hachi primary record](https://eprint.iacr.org/2026/156).

## 7. Proposition E: exact limits of same-ring linear batching

Let S=Z_N and let p be its smallest prime factor. For ℓ independent uniform linear aggregation rows, the universal error bound p^(−ℓ) is tight: take a residual vector whose first coordinate is N/p and whose remaining coordinates are zero. Each aggregate is zero exactly when the first challenge coefficient is divisible by p, which has probability 1/p.

Consequently, a frontend retaining this aggregation rule requires

    ℓ≥ceil(λ/log_2 p)

to certify error at most 2^(−λ), before accounting for other stages. Changing the lattice modulus q or ring dimension d does not improve this source-ring batching bound by itself.

For powers-of-two source moduli, p=2 and ℓ grows linearly with λ. For the original Fermat-style source modulus, its larger smallest prime factor permits a smaller ℓ. This is a precise frontend trade-off, not an impossibility of proving binary computations efficiently by a different reduction.

## 8. Challenge budget versus dimension and norm

For the reviewed universal gated extractor, the challenge contribution is (r+2)/|C|. To certify it below 2^(−λ), one must have

    |C|≥2^λ(r+2).                                 (7)

This is a requirement of the current certified extraction bound, not a proven attack lower bound or an intrinsic minimum error of the protocol.

If C has degree-<d integer representatives with multiplication operator norm at most T, then every coefficient has absolute value at most T: applying multiplication to 1 gives ||c||_2≤||c||_op. Thus

    |C|≤(2 floor(T)+1)^d.

Combining with (7) gives the necessary parameter condition

    T≥((2^λ(r+2))^(1/d)−1)/2.

Also, if R_q is the product of two fields of size q^(d/2) and all distinct challenge differences are units, the projection of C into either field is injective. Hence

    |C|≤q^(d/2),
    d log_2 q ≥ 2λ+2log_2(r+2).

Therefore a schedule cannot simultaneously keep d,T and the challenge set fixed, allow r to grow arbitrarily, and retain the new proof's fixed statistical target. It must enlarge the challenge domain, increase d or T, restrict the arity, or improve the extraction analysis. Enlarging T changes the inner MSIS collision bound 8T(b+1)B and must be included in security estimates.

These facts are important when claiming an O_λ(log W_0) architecture: a cost calculation at fixed ring ranks is not an instantiated security family.

## 9. Direct dense-JL verification remains a separate obstacle

The original verifier forms dense projection-derived coefficient vectors, e.g. φ_i''=Σ_j ω_j σ_(−1)(π_i^(j))+other terms. In the direct coefficient-arithmetic implementation, explicitly forming or reading the Θ(W_0 d) initial coefficients costs Ω(W_0 d) operations/entries. Changing folding arity or the later coefficient moduli does not remove that initial work.

This is an implementation/model observation about the specified dense calculation, not an unrestricted decision-tree lower bound against every seeded or structured projection, preprocessing method, or outsourced verification scheme. It also excludes the unavoidable cost of reading a large public instance from claims about witness-succinct verification.

Greyhound already reduces verification by invoking LaBRADOR on a smaller intermediate relation; Hachi further changes the norm-check/evaluation machinery. A route to a polylogarithmic verifier must replace, structure, preprocess, or delegate the dense initial work, not merely reprice the commitments. [Greyhound primary record](https://eprint.iacr.org/2024/1293), [Hachi primary record](https://eprint.iacr.org/2026/156).

## 10. Consequences for a stronger backend

The three bottlenecks should not be conflated:

1. **Ordinary witness recurrence:** imposes a discrete terminal floor and Ω(log log W_0) layers.
2. **Fixed-modulus coefficient representation:** turns those layers into the extra log log factor in bit communication.
3. **Dense initial verification:** prevents a fully succinct verifier in the direct architecture.

A Boolean or carry-certified modulus bridge can in principle address item 2 while preserving the exponent in item 1. It does not by itself address item 3. A PCS/sumcheck backend can address verification structure, but its own proof size, norm interface and assumptions must be compared with existing work.

SALSAA already presents a sumcheck-exposing bounded-norm backend and applications to more expressive relations; simply claiming a universal norm-aware lattice backend is therefore not a safe novelty claim. [SALSAA primary record](https://eprint.iacr.org/2025/2124). The local SALSAA PDF and the current ePrint abstract differ in wording and performance numbers; no performance comparison is certified here.

The accompanying `notes/backend_directions.md` gives a concrete parity/Boolean bridge proposition and its unproved implementation and performance obligations. None of the elementary bounds in this file alone establishes an S&P-level novelty claim.
