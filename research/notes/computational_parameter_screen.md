# Computational parameter screen for the repaired ordinary core

Date: 2026-11-14. This report evaluates cost formulas only. No lattice instance was solved, no BKZ or sieving algorithm was run, and no prover or forgery procedure was constructed. The numerical results are heuristic model outputs, not lower bounds on all algorithms and not a concrete knowledge-security certification.

The principal finding is that the earlier rank-16 arithmetic example is not a plausible 128-bit parameter choice under the screened models. Its Markov profile has a weakest classical Core-SVP exponent of 78.256, and the quantum model exponents are smaller. Recalculating the complete witness packing and all norm bounds while increasing the inner rank raises those model costs, but also changes proof size. The new centered fourth-moment bound makes rank 24 a more promising **model-screened** point: the weakest displayed exponents become 164.104 classical and 144.434 for the quantum-walk Core-SVP model, at a conservative ordinary-core encoding bound of 194.391 KiB. These numbers do not absorb the extraction reduction losses.

## 1. Reproducible tools and scope

The existing clean Lattice Estimator checkout is pinned at

    53da5982597709ba0fdf94ea37a84d822310fd84.

The screen ran using SageMath 10.9. It verifies the checkout's exact commit and absence of tracked changes before importing its cost routines. The driver is [computational_parameter_screen.py](../scripts/computational_parameter_screen.py); it calls `SISLattice.cost_euclidean` and the pinned cost models, not lattice reduction algorithms. All norm and packing inputs are recomputed by [parameter_feasibility_checks.py](../scripts/parameter_feasibility_checks.py).

The primary code references are the pinned [Euclidean SIS routine](https://github.com/malb/lattice-estimator/blob/53da5982597709ba0fdf94ea37a84d822310fd84/estimator/sis_lattice.py), [cost models](https://github.com/malb/lattice-estimator/blob/53da5982597709ba0fdf94ea37a84d822310fd84/estimator/reduction.py), and [SIS documentation](https://github.com/malb/lattice-estimator/blob/53da5982597709ba0fdf94ea37a84d822310fd84/docs/algorithms/sis-lattice.rst). These identify a reproducible model snapshot, not a claim to encompass every algorithm known today.

Recorded outputs:

- [Markov baseline](parameter-results/markov.json): inner ranks 16,20,24,28,32,40,48,64.
- [Paired fourth-moment profile](parameter-results/paired-fourth.json): Gamma^2=12d beta^2.
- [Centered fourth-moment profile](parameter-results/centered-fourth.json): Gamma^2=(21/2)d beta^2, including ranks 21,22,23 around the displayed 128-cost boundary.

Earlier files containing `conditional` in their names are preliminary snapshots. The final fourth-moment results above are backed by [filtered_fourth_moment.md](../proofs/filtered_fourth_moment.md) and its [independent review](../proofs/filtered_fourth_moment_peer_review.md). The driver records the proof file's SHA-256 and checks the displayed rational threshold certificates. This establishes the honest concentration input; it does not establish computational hardness.

All profiles here fix q=4294967197, d=64, T=34, filter acceptance lower bound a=901/1024, H=640 and source slack squared s^2=16/3. The multiplicities are [112,33,15,8,7,5,4], with initial n=37450,beta=16384. The two outer ranks remain 16. The ordinary terminal level retains its outer commitments. Source-reduction commitments, setup size, transcript framing, Fiat--Shamir security, and the original optimized final protocol are outside this screen.

## 2. What the existing Sonata estimator actually does

The supplied `estimate_sis.py` has SHA-256

    1e4a806108405d1769317c2a27900ac01c1266f4baeae5f419db3858c6e19e7a.

It is a driver for the pinned estimator, not an independent SIS solver. Its fixed modulus is 2^48-59 and degree is 64, so its existing numerical table cannot be copied to the present 32-bit-modulus profile. Its six role names and associated column counts are specific to that earlier five-layer ledger.

Its principal model is Euclidean GSA: for n scalar constraints, an available m columns, and selected lattice dimension D, it predicts first-vector length

    delta(b)^(D-1) q^(n/D).

Here b is a BKZ block-size parameter, unrelated to the protocol's decomposition base. The driver chooses D to maximize the admissible root-Hermite factor. Writing V=n ln q and L=ln R, the stationary point of

    (L-V/D)/(D-1)

is `(V+sqrt(V(V-L)))/L`; the driver compares its neighboring integers and endpoints in [n+1,m]. This is the correct stationary expression for this displayed GSA formula. It is not a proof that a structured module lattice has that output quality.

The pinned estimator inverts the Chen root-Hermite model to obtain b and checks b<=D. In its Euclidean (`norm=2`) branch, selecting a BKZ shape simulator such as CN11 does not change this calculation. Accordingly, the Sonata use of MATZOV changes the **cost function** for the inferred block size; it does not run a separate MATZOV dual attack, use the full BKZ 2.0 shape simulation, or estimate a new SIS success distribution.

The single-CRT-component helper uses the exact sum-of-two-squares factorization of the modulus, replaces n by n/2 and the squared radius by floor(R^2/q), and searches feasible GSA block sizes through min(m,65536). It enforces b<=D, then validates the selected block size with the pinned routine. “No fit through 65536” is a bounded-model result, not a hardness lower bound or a proof that the component contains no short vector. Its analytic b=40 formula differs from the pinned small-block interpolation at exactly 40; the present screened instances have larger selected blocks, and the new driver uses the pinned value at that boundary explicitly.

The use of floating-point logarithms to select a candidate dimension is appropriate for an explicitly heuristic estimate, but it is not an exact integer security certificate. The new driver retains the same interpretation. Norm feasibility, lifting, and digit caps are separate exact-arithmetic calculations.

## 3. Norms, ring structure, and problem definitions

All radii in this report use the Euclidean norm of the concatenated polynomial coefficients. For R=Z[X]/(X^64+1), the unnormalized canonical embedding norm is sqrt(64)=8 times that norm. Langlois--Stehle's module-lattice definition uses the canonical embedding, so a numerical radius cannot be transplanted between these conventions without this factor.

Standard integer-MSIS permits any nonzero integer vector z satisfying Az=0 mod q. Its q e_j vector has coefficient norm q, so a standard integer-MSIS hardness assumption at R>=q is vacuous. A nonzero-residue variant excludes that vector. Every collision in the repaired reduction is nonzero modulo q; nevertheless, if the assumption is standard integer-MSIS it must pass R<q. All displayed instances do. This also ensures that any nonzero integer solution within the displayed radius is automatically nonzero modulo q. The estimator's large-norm SIS* branch is not used.

For an a-by-b matrix over the degree-64 ring, the generic scalar screen uses n=64a constraints and m=64b columns. A module matrix's scalar columns are correlated signed shifts; they are not an independently sampled scalar SIS matrix. Applying a generic GSA quality model to its q-ary kernel is a heuristic screen on a structured lattice, not a reduction proving that its distribution is a generic random lattice.

The single-component screen uses

    q=44174^2+48411^2,
    pi=44174+48411 X^32,
    pi*pi_bar=q,
    ||pi y||=sqrt(q)||y||.

Thus it considers n=32a constraints, still m=64b available integer coordinates, and squared radius floor(R^2/q). This transformation is mathematically exact; the GSA prediction applied afterward remains heuristic. Since R<q, a resulting nonzero integer vector within R cannot be a q-vector. This screen does not exhaust other algebraic or module-specific methods.

## 4. Cost labels and primary-source limits

The output records five distinct models:

| Label | Meaning in the pinned code |
|---|---|
| Core classical 0.292 | log_2 cost =0.292 b; asymptotic Core-SVP exponent |
| Core quantum 0.265 | log_2 cost =0.265 b; the ADPS-style quantum sieving convention |
| Core quantum 0.257 | log_2 cost =0.257 b; Chailloux--Loyer quantum-walk convention |
| MATZOV classical | Fitted nearest-neighbor cost, dimensions for free, dimension-dependent overhead and an LLL term |
| MATZOV quantum DW | The estimator's inherited quantum depth-times-width fit; different units from classical operations |

The first three columns omit polynomial lattice-reduction overhead and are not measured CPU cycles or bit-operation costs. The two fitted columns include different modeling choices and cannot be silently substituted into the same advantage-versus-time statement. These labels describe the implementation; no quantum knowledge-extraction theorem follows from including a quantum SIS cost column.

The supplied `SISLWEEstimator.pdf` is Albrecht--Player--Scott, *On the concrete hardness of Learning with Errors*. Its first-page August 2019 warning explicitly says that the accompanying estimator evolved while the paper did not; the paper is not a current SIS security certificate. Chen--Nguyen, *BKZ 2.0: Better Lattice Security Estimates*, describes an experimentally motivated simulation and notes input-shape dependence; the Euclidean call used here is the simpler root-factor model, not that full simulation. MATZOV, *Report on the Security of LWE: Improved Dual Lattice Attack*, Section 6.1 expressly confines its sieving-cost discussion to the classical model. The quantum DW column comes from the estimator's combined fit and inheritance, rather than a quantum theorem in that report. Chailloux--Loyer's cited primary paper is *Lattice Sieving via Quantum Random Walks*, ASIACRYPT 2021.

The pinned MATZOV implementation documents a fitting range through block size 1024. Every inner-row block in the rank-16 baseline is within it; all its outer-row blocks exceed it. The JSON retains a flag for this condition. Any returned fitted value beyond that range is extrapolation and is not treated as calibrated evidence here.

## 5. All seven rank-16 inner instances

The first three radii are often decisive. The complete baseline table is below; the available scalar column count is 64n_protocol and the constraint count is 1024 throughout. `D` is the selected GSA dimension; `b_BKZ` is the model block size. These are cost parameters, not protocol settings.

| Layer | Protocol n | Collision radius R | D | b_BKZ | Core classical | Core quantum .265 | Core quantum .257 | MATZOV classical | Quantum DW |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 1033254288 | 2188 | 309 | 90.228 | 81.885 | 79.413 | 118.538 | 115.442 |
| 2 | 5205 | 1949980240 | 2123 | 282 | 82.344 | 74.730 | 72.474 | 111.036 | 108.692 |
| 3 | 1335 | 2788653888 | 2088 | 268 | 78.256 | 71.020 | 68.876 | 107.149 | 105.193 |
| 4 | 668 | 1911734592 | 2125 | 283 | 82.636 | 74.995 | 72.731 | 111.314 | 108.941 |
| 5 | 334 | 1498643568 | 2150 | 293 | 85.556 | 77.645 | 75.301 | 114.092 | 111.441 |
| 6 | 334 | 1283238336 | 2165 | 299 | 87.308 | 79.235 | 76.843 | 115.759 | 112.942 |
| 7 | 334 | 245681280 | 2351 | 381 | 111.252 | 100.965 | 97.917 | 138.565 | 133.463 |

For the same seven inner rows, the single-CRT selected dimensions are [2350,2205,2131,2209,2263,2298,2760], with blocks [990,836,763,840,896,933,1505]. None gives a smaller Core-SVP cost than the corresponding generic screen. The last CRT block exceeds the MATZOV documented fit range.

The first outer matrix commits to packed t and g and has ring column count r t_1 kappa+G t_2. The second commits to packed h and has G t_1 columns, where G=r(r+1)/2. Both use collision radius 2B and rank 16. Their exact counts and model dimensions are:

| Layer | First / second ring columns | Radius 2B | Generic D first / second | Generic b_BKZ first / second |
|---|---:|---:|---:|---:|
| 1 | 44184 / 44296 | 230226 | 3679 / 3679 | 1292 / 1292 |
| 2 | 5973 / 3366 | 220586 | 3691 / 3691 | 1304 / 1304 |
| 3 | 1800 / 600 | 158952 | 3792 / 3792 | 1398 / 1398 |
| 4 | 820 / 180 | 108968 | 3916 / 3916 | 1518 / 1518 |
| 5 | 672 / 140 | 85422 | 4000 / 4000 | 1603 / 1603 |
| 6 | 460 / 75 | 73144 | 4055 / 4055 | 1660 / 1660 |
| 7 | 434 / 60 | 27792 | 4439 / 3840 | 2088 / 2154 |

The smallest outer ADPS quantum exponent is 342.38. This is a model comparison, not a proof that outer binding can be ignored. The first six layers' outer CRT screens have no feasible GSA fit through the search cap; the last has floor(R^2/q)=0, which rules out a nonzero integer vector in that particular transformed budget.

An independent reviewer confirmed the two outer-column formulas and the recursive/final B convention. The new estimator output tables, including the rank-24 numerical costs, have not yet received a separate independent rerun; their present evidence is the pinned-model execution and saved exact parameter inputs described above.

## 6. Rank changes include a full arithmetic recomputation

For each rank, the driver reruns the exact digit-cap and paired-padding search. It does not freeze B, the layer shapes, or the proof size. It uses B_i=ceil(s beta_(i+1)) on recursive edges and the explicit checked cap at the final level. The outer ranks stay 16. All listed seven-layer paths pass the three strict R<q checks, the JL modulus inequalities, and the initial binary-source lifting inequality. Honest layer acceptance remains greater than 479/528 and the seven-layer product remains greater than 1/2.

The Markov baseline has Gamma^2=(32768/901)d beta^2. Its weakest inner model costs and encoding bounds are:

| Inner rank | Weakest classical Core | Weakest quantum .265 | Weakest quantum .257 | Ordinary-core KiB |
|---:|---:|---:|---:|---:|
| 16 | 78.256 | 71.020 | 68.876 | 160.891 |
| 20 | 108.624 | 98.580 | 95.604 | 173.789 |
| 24 | 140.452 | 127.465 | 123.617 | 187.227 |
| 28 | 173.156 | 157.145 | 152.401 | 201.195 |
| 32 | 207.028 | 187.885 | 182.213 | 215.164 |
| 40 | 277.692 | 252.015 | 244.407 | 248.688 |
| 48 | 350.692 | 318.265 | 308.657 | 277.641 |
| 64 | 503.408 | 456.860 | 443.068 | 335.391 |

Larger rank does not automatically resolve the concrete reduction budget discussed below. It also weakens the outer screen slightly because larger auxiliary witnesses increase B.

The reviewed fourth-moment improvements keep the same H and f. They certify smaller Gamma, after which all dimensions and caps are recomputed. The comparison below shows that a smaller Gamma need not yield a smaller encoding under the current greedy norm objective:

| Fold cap coefficient Gamma^2/(d beta^2) | Inner rank | Weakest classical Core | Weakest quantum .257 | Ordinary-core KiB |
|---|---:|---:|---:|---:|
| 32768/901, Markov | 16 | 78.256 | 68.876 | 160.891 |
| 12, paired fourth moment | 16 | 86.432 | 76.072 | 163.109 |
| 21/2, centered fourth moment | 16 | 86.724 | 76.329 | 162.984 |
| 32768/901, Markov | 24 | 140.452 | 123.617 | 187.227 |
| 12, paired fourth moment | 24 | 154.468 | 135.953 | 194.516 |
| 21/2, centered fourth moment | 24 | 164.104 | 144.434 | 194.391 |

For the centered profile, the uniform-rank boundary in the examined neighborhood is rank 21 -> quantum-walk exponent 120.276 at 180.141 KiB; rank 22 ->128.243 at 183.547 KiB; rank 23 ->136.467 at 190.859 KiB. Rank 22 has effectively no model margin and still does not address reduction losses. Rank 24 is a useful research candidate, not a certified 128-bit choice.

For complete reproducibility, the centered rank-24 path is:

| Layer | n | r | beta | b | t_1 | t_2 | Gamma ceiling | beta_next | actual B | L_weak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 112 | 16384 | 16 | 8 | 6 | 424722 | 36546 | 84400 | 390265600 |
| 2 | 5795 | 33 | 36546 | 32 | 7 | 6 | 947381 | 34195 | 78970 | 708834720 |
| 3 | 1834 | 15 | 34195 | 64 | 6 | 5 | 886436 | 22497 | 51955 | 918564400 |
| 4 | 917 | 8 | 22497 | 64 | 6 | 5 | 583189 | 15155 | 34999 | 618782320 |
| 5 | 516 | 7 | 15155 | 64 | 6 | 5 | 392863 | 12012 | 27741 | 490460880 |
| 6 | 516 | 5 | 12012 | 64 | 6 | 5 | 311387 | 10326 | 23847 | 421614960 |
| 7 | 516 | 4 | 10326 | 64 | 6 | 5 | 267681 | 9460 | 9460 | 167252800 |

The six paired splits (nu,mu) are (7,19),(4,7),(2,4),(2,3),(1,3),(1,2). This respects r_next=2nu+mu and n_next=max(ceil(n/nu),ceil(M_aux/mu)). The source and public-input constraints from the repaired binary relation remain required; the screen does not insert them.

## 7. Audit of the original authors' available parameter code

The read-only upstream checkout is [lattice-dogs/labrador](https://github.com/lattice-dogs/labrador), commit `8b6626b26afd4c0162ddd089759d21d3d51bfbdf`. The checked [data.h](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/data.h) fixes `LOGDELTA=log2(1.00444)`, T=14 and SLACK=2 with a FIXME comment. Its [sis_secure predicate](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/labrador.c) compares log_2 R with `min(LOGQ,2 sqrt(LOGQ LOGDELTA N rank))`.

That expression is a continuous-dimension GSA-style threshold at a fixed root factor. It does not itself name a classical/quantum cost model or charge the knowledge-extraction reductions. Under the present pinned Chen inversion, delta=1.00444 corresponds to block 342, giving Core exponents 99.864 classical, 90.630 for .265, and 87.894 for .257. This documents a cost-model mismatch with treating the boolean name `sis_secure` as a stand-alone 128-bit certification. It is not a demonstrated attack on the implementation or a statement that every instance selected by it has exactly those costs; selected radii can be strictly below its threshold, and the implementation uses other protocol choices.

In particular, its projection and challenge parameters differ from the 2022 PDF and from this repair. The source cannot be used as an unchanged certificate for the repaired threshold, filtered cube, target cap or commitment bound. No upstream code was executed as a prover or modified.

## 8. Why the extraction losses are not handled by these tables

The seven-layer expected-call multiplier is between 132779520 and 132779521, approximately 2^26.98446. It multiplies costs in the recursive extractor's runtime recurrence; local work and the collision experiments' extra calls also enter. A Core-SVP exponent is a cost point in a heuristic model, while a concrete security theorem needs an upper bound eta(t) on each complete reduction's success as a function of its full time. A single model cost does not supply that function. Therefore one cannot mechanically subtract 27 bits from the table and call the remainder a proved security level.

The earlier, unweighted proof used the computational term

    sqrt(L)+eta_E,
    L=eta_0+sqrt(eta_h)+r sqrt(eta_y)+sqrt(eta_g).

With every other term zero, that earlier bound contributes sqrt(r) eta_y^(1/4). It would require eta_y<=2^-512/r^2 to make that contribution at most 2^-128. This describes a loss of the earlier analysis, not an attack or a requirement for a 512-bit lattice instance.

The subsequently proved and independently reviewed [bad-mass refinement](../proofs/computational_loss_refinement.md) retains the same samplers, norms and full time obligations but gives the stronger bound

    nu <= sqrt(eta_0)
          +[(sqrt(eta_h)+sqrt(r eta_y))^2+eta_g]^(1/3)+eta_E
       <= sqrt(eta_0)+(2eta_h+2r eta_y+eta_g)^(1/3)+eta_E.

The exact only-eta_y term is now (r eta_y)^(1/3); making this term at most 2^-128 requires eta_y<=2^-384/r through that formula alone. The bound for eta_0 still has a square root. These are advantage requirements at the complete reduction's time. The new inequality improves the algebraic loss; it still does not supply an eta(time) curve from one heuristic cost point. Layer sums, source-commitment losses and initialized restart experiments remain additional obligations. The parameter rows and estimator outputs in this report are unchanged by this analytical refinement.

Increasing rank until a table reads 128, 160 or even 512 does not close the gap without a stated time/advantage assumption or a tighter reduction. Conversely, these losses are not an attack and do not imply that the architecture cannot attain useful security. They identify the theorem currently missing from a concrete claim.

## 9. A finite domain for the next joint optimization

A useful next search should preserve nondominated complete layer states rather than choose the smallest beta_next at every layer. The following finite domain is an initial proposal, not an already searched space or a claim of global optimality:

| Parameter group | Candidate domain and required checks |
|---|---|
| Ring | d in {64,128}; q in {2^32-99,2^40-195,2^48-59}, each independently primality/splitting certified before use |
| Projection | J=1024 initially; H in {608,624,640,672,704}, exact Cantelli probability and s^2=H/120; larger J only through its separately proved profile |
| Challenges | Integer T from 30 to 40 at d64; certified rational acceptance lower bounds with denominator 1024; degree-dependent thresholds require their own tail certificates |
| Fold | f in {1/8,1/12,1/16,1/20,1/24,1/28,1/32}; use the proved Markov or fourth-moment envelope at that exact d,a,f |
| Inner rank | Each layer in {16,...,64}; recompute all t dimensions, norm caps and scalar/CRT screens |
| Outer ranks | Each in {4,...,32}; recompute commitment sizes and each actual outer MSIS instance |
| Decomposition | b,a_1,a_2 in powers of two 2,...,512; t_1,t_2 in {2,...,20}, retaining the final-quotient carry bounds |
| Shape | Start with the seven-layer r schedule and nearby multiplicities; enforce paired z blocks and zero-padding exactly; optionally six or eight layers with new statistical/runtime accounting |

Changing d also changes affine source modulus 2^d+1 and its least-prime-factor budget; changing q changes digit counts, lifting room, field encoding length and CRT factors. Neither can be varied while keeping those related inputs fixed. The binarity lift, affine lift when used, every actual B, three R<q screens, freshness/chronology, and the statistical sum are feasibility constraints. A no-retry whole-attempt completeness target such as product_i p_i>1/2 is also a constraint; any bounded restart wrapper has its own proven error and runtime charges.

The optimization output should be a Pareto set in at least: deterministic prover-payload bound; honest expected arithmetic or measured runtime; setup/projection memory; smallest classical and each labeled quantum model cost; total statistical error; and full reduction-call/local-work accounting. Treating one Core-SVP number as the complete security constraint would conceal the unresolved eta(t) problem. Source-reduction commitment assumptions must be added before presenting a full R1CS result.

The current greedy search minimizes beta_next and then dimension, which explains why the stronger fourth-moment theorem can increase its encoding bound. A layer-state dynamic program or beam search can retain several choices of (n,r,beta,b,t_1,t_2,kappa), accumulate actual payload and probability, and discard only states proved dominated under all future-relevant quantities. No claim that simple coordinatewise dominance is always sufficient is made: next-step divisibility, paired padding and dimension-limited estimates can matter.

## 10. Research assessment

The repaired work has stronger honest-completeness guarantees and an explicit finite statistical ledger. It does not yet demonstrate a smaller or faster concretely secure argument than the original paper. The rank-16 candidate fails even a modest model-cost screen. Rank 24 with the centered fourth-moment cap is a credible starting point for further joint optimization, while the complete extraction advantage budget remains unresolved. These facts support continued parameter and reduction research; they establish neither a full 128-bit certification nor a general impossibility of the original architecture.
