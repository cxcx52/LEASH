# An executable cross-characteristic exact-relation bridge

Date: 2026-11-14. Status: an exact arithmetic/Boolean relation construction and its checked dimensions. This is not a cryptographic prover, a parameterized MSIS security estimate, or evidence of a faster backend.

## 1. The old relation

Use the prime

    q_old = 4294967197 = 2^32 - 99.

The public statement fixes q_old, t=7 and B_old^2=65. A witness consists of two **canonical unsigned residues** x,y, each represented by 32 input bits. Define

    center_q(z) = z                     if z <= (q_old-1)/2,
                  z-q_old              otherwise.

The relation is

    0 <= x,y < q_old,
    x+y = 7 mod q_old,
    center_q(x)^2 + center_q(y)^2 <= 65.                 (OLD)

There is no ambiguity at q_old/2 because q_old is odd. The public values are fixed circuit constants, not unconstrained private wires.

The pair (q_old-1,8) lies exactly on the norm boundary: its centered values are (-1,8) and the squared norm is 65. The pair (q_old-2,9) satisfies the same modular equation but has squared norm 85 and is rejected. The noncanonical 32-bit value x=q_old+3 is explicitly rejected by the range check.

The relation has exactly ten solutions, namely (a mod q_old,(7-a) mod q_old) for -1<=a<=8. Indeed, the norm bound forces both centered magnitudes to be at most eight. Their sum has absolute value at most sixteen, so congruence to seven modulo this q_old implies integer sum seven. Substitution gives a^2+(7-a)^2<=65, equivalently (a+1)(a-8)<=0.

## 2. An explicit complete Boolean verifier

The implementation is `scripts/boolean_bridge_toy.py`. Its primitive gates are AND, XOR and NOT. No constant propagation, common-subexpression elimination, or square-specific optimization is applied; the reported counts refer to exactly the emitted gates.

The verifier performs all of the following:

1. Compare both 32-bit inputs with q_old-1.
2. Form the full 33-bit unsigned sum. Test equality to seven or q_old+seven. For canonical inputs these are exactly the possible integer sums giving the required residue.
3. Compare each residue to (q_old-1)/2, form q_old-z by 32-bit two's-complement subtraction, and select z or q_old-z to obtain the exact centered magnitude. The range checks make the selected value meaningful.
4. Compute each magnitude's full 64-bit square using the ordinary schoolbook multiplier.
5. Add the squares into a **65-bit** accumulator and compare this integer with 65.
6. Conjoin the two range checks, the modular equation check and the norm check.

The 65-bit accumulator is deliberately retained even though the canonical centered magnitudes give a smaller true maximum. No modular truncation is used in the norm comparison.

Each L-bit ripple adder emits 3L XOR and 2L AND gates and returns L+1 bits. Its carry is `(u AND v) XOR ((u XOR v) AND carry)`: the terms are disjoint, so XOR equals OR here. The comparator `a<=K` computes the carry of `a + complement(K+1) + 1`, then negates it. These formulas establish correctness for all input bit strings, independently of the finite checks.

Schoolbook multiplication uses L^2 partial-product AND gates and L adders of width 2L, totaling 11L^2 gates. Discarding each final carry is harmless: every partial sum is a nonnegative subset of the full product, which is strictly less than 2^(2L). Invalid/noncanonical residues still have well-defined circuit outputs and are rejected by the explicit range conjunction.

The source circuit has the following exact ledger at L=32:

| Verifier component | AND | XOR | NOT | Total |
|---|---:|---:|---:|---:|
| Both canonical ranges | 128 | 192 | 2 | 322 |
| Old modular equation | 129 | 292 | 2 | 423 |
| Centered magnitudes | 320 | 512 | 68 | 900 |
| Two full squares | 10240 | 12288 | 0 | 22528 |
| Norm addition/comparison | 258 | 387 | 1 | 646 |
| Conjunction | 3 | 0 | 0 | 3 |
| **Total** | **11078** | **13671** | **73** | **24822** |

For this construction the exact formulas are

    G_AND = 10L^2+26L+6,
    G_XOR = 12L^2+43L+7,
    G_NOT = 2L+9,
    G     = 22L^2+71L+22.

These count the actual old-relation verifier, including range and norm checks. They do not infer verifier complexity from the number of old witness elements.

## 3. Exact F2 affine-R1CS compilation

Allocate a wire w_0 pinned to one, a wire w_zero constrained to zero, the 64 input wires and one output wire for every gate. Over F2 every wire is already Boolean. Compile:

    AND(a,b)=t  ->  a*b=t,
    XOR(a,b)=t  ->  a+b+t=0,
    NOT(a)=t    ->  a+t+w_0=0.

Finally impose output+w_0=0. All coefficients are in F2, and repeated indices cancel. The program explicitly emits sparse triples of A,B,C rows and sparse H rows; it evaluates each of these constraints on every tested assignment. The independent pin w_0=1 is part of the repaired source relation.

The exact dimensions are

    n = 24888  (includes the one/zero wires, inputs and all gate outputs),
    k = 11078  (AND constraints),
    h = 13746  (affine gate constraints, zero pin and accepting-output pin).

There are 3G+3=74469 stored coefficient occurrences across the sparse A,B,C,H row lists, before cancelling repeated indices. The separate constant-one pin is not an H row. The constraint evaluator is therefore linear in this explicitly reported sparse representation.

**Equivalence theorem.** The resulting affine-R1CS has a satisfying assignment extending input bits (x,y) if and only if (OLD) holds. The extension is unique once input bits and constant pins are fixed.

Proof: topologically induct on gate order. Each gate equation uniquely determines its output over F2 and agrees with its Boolean truth table. The accepting-output pin therefore holds exactly when the explicitly verified predicate accepts. The arithmetic argument in Section 2 identifies that predicate with (OLD). The converse uses the deterministic wire assignment generated by circuit evaluation.

## 4. A smaller target prime satisfying the lifting inequalities

Use the parity frontend of `notes/backend_directions.md` with

    R = Z[X]/(X^d+1),        d = 64,
    phi_2(f) = f(1) mod 2,   Enc(0)=0, Enc(1)=1,
    ell = 129.

The frontend opening length is

    M = n+(3+ell)k = 1487184.

The conservative honest bound is beta_h^2=M. To account for the reviewed core's norm slack, explicitly use

    s^2 = 23/5,
    beta_actual^2 = (23/5)M = 34205232/5.

Take

    q_new = 13384741,

a 24-bit prime congruent to five modulo eight, strictly smaller than q_old. The script proves both prime claims by integer trial division. Congruence five modulo eight gives the ordinary two-factor ring family at d=64; this says nothing by itself about MSIS hardness.

The required source lifting condition is

    sqrt(M)*beta_actual + beta_actual^2/2 < q_new/2.

Equivalently q_new>(2sqrt(23/5)+23/5)M. The script avoids numerical square roots and certifies

    5q_new-23M > 0,
    (5q_new-23M)^2 - 460M^2 = 53109000517969 > 0.

It additionally checks the reviewed single-layer JL parameter inequality for honest budget beta_h:

    beta_h <= q_new/(250sqrt(23/5)),
    q_new^2 - 287500M = 178723726237081 > 0.

The F2 frontend's two aggregation stages contribute 2^(1-ell)=2^(-128). Commitment-binding bounds still require actual norm 2beta_actual, and the backend's remaining aggregation, challenge, norm and runtime conditions remain separate obligations. No ranks or security estimates are claimed here.

### Direct target-verifier and preparation costs are also substantial

The 24822-gate count describes the old Boolean relation only. It is not the cost of verifying the parity frontend's bare target. If the two commitment row counts are m_0,m_1, the target matrix products have 58122*m_0 and 1429062*m_1 ring-product terms, respectively. Checking all ell aggregate equations directly has the following unoptimized ledger:

    ell*M = 191846736 linear ring-product terms,
    ell*k =   1429062 quadratic ring-product terms,
    total = 193275798 terms.

The target norm check reads d*M=95179776 scalar coefficients at d=64. The source challenge array delta_(i,j) already has ell^2*k=184348998 F2 entries. Its naive aggregation into the public coefficients charges that work explicitly, before any selected backend verification is counted. Some F2 encodings are zero/one and can save operations in particular rows; these displayed figures specify the direct dense layout, not a lower bound against every optimized representation.

These counts are output by the script. They make this conservative toy unsuitable as evidence of a practical bridge even though its modulus inequality holds. Sparse source arithmetization, specialized squaring, batching structure and a complete backend would all need separate analysis; none is silently assumed here.

No field homomorphism from F_(q_old) to F_(q_new) is used. The old arithmetic is checked as a Boolean predicate, and the repaired parity frontend lifts integer residuals before applying phi_2. Arbitrary extracted target polynomials decode to F2 wire values; soundness does not assume that extracted polynomials themselves are constant-bit encodings.

Thus a verified extracted source assignment satisfies the original **exact** bound 65, even though the new target opening may have the specified norm slack. This is the narrow exact-interface property established by the construction.

## 5. Reproduction and limits

Run

    python scripts/boolean_bridge_toy.py

The program tests 515 input pairs: boundary cases, all centered pairs in [-10,10]^2, and 64 reproducibly selected 32-bit pairs. These include all ten actual solutions. For every case it checks the independent old predicate, circuit acceptance, every sparse R1CS/affine gate row, the accepting-output row and the exact integer norm accumulator for canonical inputs. It also checks detection of a modified AND output. The general relation equivalence follows from the gate/arithmetic proof, not finite testing.

This experiment reduces the coefficient modulus width from 32 to 24 bits while expanding two old residues to a frontend opening with 1487184 ring coordinates. It gives **no communication or speed improvement**. Its purpose is to make cross-characteristic feasibility and exact old-norm preservation concrete, with a complete cost ledger.

The public preparation cost for this toy consists only of fixed integer constants. There is no dense matrix, challenge-derived vector, or JL preparation hidden in the example. Applying the same idea to an actual MAIN target requires charging its full arithmetic verifier and its public-preparation work separately. In particular, the original dense projection cost remains proportional to the original witness dimension unless another mechanism changes it. This toy neither implements that mechanism nor establishes a fully succinct verifier.
