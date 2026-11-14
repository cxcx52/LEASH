# Exact finite-domain joint search at unchanged collision-radius caps

Date: 2026-11-14. Scope: the fixed seven-layer ordinary-core profile, exact arithmetic norm/payload accounting, and a follow-up cost-model screen. No lattice-solving algorithm or cryptographic prover is implemented.

The finite search reduces the conservative prover-payload bound from **194.390625 KiB to 185.734375 KiB**, saving 70,912 bits =8,864 bytes =8.65625 KiB, approximately 4.45%. It retains the same maximum allowed collision radii and the same weakest output in every one of the five pinned cost models. This is an improvement to the specified arithmetic encoding bound, not a measured protocol size or a concrete security certification.

Reproduction artifacts:

- [Exact search script](../scripts/joint_parameter_search.py).
- [Complete chosen path and search counts](parameter-results/joint-cube.json).
- [Pinned-model rerun on that path](parameter-results/joint-cube-models.json).
- [Cost-model definitions and limitations](computational_parameter_screen.md).

## 1. Fixed inputs and finite domain

The search fixes

    q=4294967197, d=64, J=1024, H=640, T=34,
    a=901/1024, f=1/16, s^2=16/3,
    Gamma^2=(21/2)d beta^2,
    inner rank kappa=24, both outer ranks=16,
    r=(112,33,15,8,7,5,4),
    initial n=37450, beta=16384.

The centered fourth-moment cap is the reviewed result in [filtered_fourth_moment.md](../proofs/filtered_fourth_moment.md). Every per-layer norm cap uses the full deterministic upper-triangular formulas in [parameter_feasibility.md](../proofs/parameter_feasibility.md). Only the following choices vary:

    b in {2,4,8,16,32,64,128,256},
    a_1=a_2=b,
    t_1 in {max(2,nominal-1),nominal,nominal+1},
    nominal=max(2,ceil(log_b q)),
    t_2 in {2,...,19}.

Each transition must satisfy all of

    8T(b+1)B <= 918564400,
    2(b+1)B+4T ceil(s beta) <= 918564400,
    2B <= 168800,
    250^2 s^2 beta^2 <= q^2,
    each of the three MSIS radii < q.

The displayed Gram condition deliberately uses the integer upper bound ceil(s beta), as does the existing arithmetic checker. At recursive edges B=ceil(s beta_next); the final explicitly opened target has B=beta_next. All constants are fixed before the search. The initial binary lifting and centered-representative conditions remain satisfied and are checked exactly.

The search never changes the ring, ranks, challenge distribution, projection distribution, schedule, source slack or computational assumptions. It does not use an unproved improved extraction loss.

## 2. Why a shorter digit decomposition is permitted here

For every decomposition, the first t-1 digits are centered base-b digits; the last digit is the remaining integer quotient. For input x, that quotient is bounded by

    |x_high| <= |x|/b^(t-1)
                  + b/(2(b-1)) (1-b^(-(t-1))).

The last quotient need not lie in [-b/2,b/2]. It is separately included in the Euclidean target cap and in the fixed-width signed encoding. Thus t_1=nominal-1 is a valid choice for this explicitly specified target relation even when b^t_1<q.

This point changes a parameter convention from the original paper's statement that the decomposition parts have coefficient bound b/2. The repaired relation used here checks the actual global Euclidean cap and the exact reconstruction equations; it does not impose that extra coefficient bound on the final quotient. Therefore this is an explicit decomposition variant with its own complete carry bound, not an application of the original all-digits-small estimate outside its range.

For example, the selected fourth layer uses b=64,t_1=5. Its highest t/h quotient can be substantially larger than 32; its contribution is included in E_u. The selected final layer uses b=4,t_1=15 while the nominal count is 16. Its highest t/h quotient is likewise handled by the final-quotient bound. No overflow, discarded carry or implicit uniform-digit assumption is used.

## 3. State definition and dominance theorem

At the beginning of each layer the state is

    (n,beta,C),

where C is the accumulated early prover-message bit bound. Every state also retains a full path for reconstruction. The future r schedule, ranks and allowed digit choices depend only on the stage and fixed inputs.

For a fixed next digit choice, every norm term is nondecreasing in n and beta. In detail, D_z=nd increases with n; Gamma=ceil sqrt((21/2)d beta^2) increases with beta; the z cap

    D_z b^2/4 + (Gamma/b+ceil(sqrt(D_z))/2)^2

is nondecreasing in both. The uniform t/h cap is fixed for that stage and choice. The g cap increases with beta^2. Consequently beta_next, actual B, both inner collision bounds, and the outer bound are nondecreasing. All feasibility inequalities are upper bounds on those quantities, so a fixed choice feasible for a larger state remains feasible for a componentwise smaller state.

For each positive pair nu,mu satisfying 2nu+mu=r_next, the required next rank is

    max(ceil(n/nu),ceil(M_aux/mu)),

where M_aux=r t_1 kappa+(t_1+t_2)r(r+1)/2 is independent of n and beta for that fixed choice. This rank is nondecreasing in n. Taking the minimum over the finite allowed pairs preserves that monotonicity. Since nu and mu introduce no additional norm or payload term in this fixed model, the pair minimizing the next rank dominates other pairs with the same digit choices.

The early-message bound at a stage is

    2*16*64*32 + 6*64*32
      + 1024*ceil(log_2(2 floor(ceil sqrt(640 beta^2))+1)),

using exactly the existing signed-range encoding routine. It is nondecreasing in beta. The final-witness encoding is also nondecreasing in n and beta for fixed digits: the z coordinate count increases with n and its high-digit range with Gamma; t/h ranges are fixed; the g high-digit range uses min(beta^2,q/2), which is nondecreasing.

It follows by induction that if two states at the same stage satisfy

    n_A<=n_B, beta_A<=beta_B, C_A<=C_B,

then every feasible future digit path from B can be copied from A with no greater final payload and no violated arithmetic radius cap. State B may be discarded. This statement concerns the specified arithmetic feasibility conditions and encoding objective. It does not assert dominance of every possible computational security model or of omitted implementation costs.

The script performs this dominance pruning exactly with integer state keys and a prefix-minimum Fenwick tree after sorting by n, beta and C. Duplicate states retain one path. An independent quadratic dominance oracle checks the skyline routine on a finite test set. There is no beam truncation, floating-point norm decision or heuristic pruning. Therefore the final result is an exact minimum of the stated payload formula over the stated finite domain and radius constraints. It is not an optimum over all protocols, all bases, all encoding methods, or a larger parameter domain.

## 4. Complete optimized path

| Layer | n | r | beta | b | t_1 | t_2 | Gamma ceiling | beta_next | actual B | Weak collision bound |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 112 | 16384 | 16 | 8 | 6 | 424722 | 36546 | 84400 | 390265600 |
| 2 | 5795 | 33 | 36546 | 32 | 7 | 6 | 947381 | 34195 | 78970 | 708834720 |
| 3 | 1834 | 15 | 34195 | 64 | 6 | 5 | 886436 | 22497 | 51955 | 918564400 |
| 4 | 917 | 8 | 22497 | 64 | 5 | 5 | 583189 | 21346 | 49297 | 871570960 |
| 5 | 459 | 7 | 21346 | 64 | 6 | 5 | 553352 | 13343 | 30815 | 544809200 |
| 6 | 459 | 5 | 13343 | 64 | 6 | 5 | 345891 | 10415 | 24053 | 425257040 |
| 7 | 459 | 4 | 10415 | 4 | 15 | 9 | 269988 | 68879 | 68879 | 93675440 |

The paired splits are respectively (7,19),(4,7),(2,4),(2,3),(1,3),(1,2). Each row has been independently rebuilt by the same exact cap formula during path verification, and every reconstruction, padding and radius inequality passes. The largest outer radius is 168800 at layer 1; the largest weak radius is 918564400 at layer 3; the largest Gram radius is 17494070, also at layer 3.

The last target cap beta_next=68879 is larger than the greedy path's last cap. It is checked directly on the explicit final witness. There is no following layer that would extract a slackened opening, so its actual collision cap is B=68879, not ceil(s*68879). Its outer radius 137758 remains below the imposed 168800 cap. This larger terminal norm is useful because the smaller digit base gives a cheaper bounded-coordinate encoding. It would not be valid to reuse that B convention on a recursive edge.

## 5. Payload and search accounting

| Quantity | Greedy baseline | Joint optimum | Change |
|---|---:|---:|---:|
| Early prover messages, bits | 690176 | 692224 | +2048 |
| Final explicit target, bits | 902272 | 829312 | -72960 |
| Total, bits | 1592448 | 1521536 | -70912 |
| Total, KiB | 194.390625 | 185.734375 | -8.65625 |

The improvement is a whole-path result. The fourth layer trades a larger norm cap for a smaller padded rank, and the direct terminal layer trades a larger checked cap for cheaper digits. Minimizing only beta_next misses both choices. This is why the current joint objective improves on the earlier greedy cap minimization.

Search counts are:

| Layer | Input Pareto states | Feasible transitions | Unique successors | Retained Pareto states |
|---|---:|---:|---:|---:|
| 1 | 1 | 2 | 2 | 2 |
| 2 | 2 | 60 | 60 | 2 |
| 3 | 2 | 91 | 91 | 3 |
| 4 | 3 | 242 | 242 | 2 |
| 5 | 2 | 255 | 254 | 2 |
| 6 | 2 | 276 | 276 | 2 |
| 7 | 2 | 496 | terminal | terminal |

The payload remains the conservative fixed-width ordinary-core ledger: outer commitments, six aggregation polynomials and 1024 JL coordinates per layer, followed by the final digits. It excludes source-reduction messages, public statements/setup, framing, verifier messages and any Fiat--Shamir material. It is not the original optimized terminal protocol, a measured network transcript or a Gaussian entropy estimate.

## 6. Pinned model recheck and preserved probability guarantees

The chosen path was rerun through clean Lattice Estimator commit `53da5982597709ba0fdf94ea37a84d822310fd84`, SageMath 10.9, using the exact scalar dimensions and collision radii of all seven inner and fourteen outer instances. The full input path is hashed in the saved result. The generic inner blocks are [632,582,562,566,604,625,775]. The single-CRT blocks are [2192,1853,1728,1753,1993,2138,3424]; none lowers the generic Core-SVP screen.

The weakest cost remains the layer-3 inner instance in every displayed model:

| Model | Minimum log_2 cost |
|---|---:|
| Classical Core-SVP, .292 | 164.104 |
| Quantum Core-SVP, .265 | 148.930 |
| Quantum-walk Core-SVP, .257 | 144.434 |
| Fitted MATZOV classical | 189.391 |
| Estimator quantum depth-times-width fit | 179.228 |

These minimum values are unchanged from the greedy rank-24 centered-fourth profile. The relevant inner block is within the fit's documented range; the JSON flags extrapolated outer/CRT fit values separately. The meanings, assumptions and limits of these cost units remain exactly those in [computational_parameter_screen.md](computational_parameter_screen.md).

Every layer still has the same JL acceptance guarantee and fold rejection below 1/16. Thus the whole-attempt honest acceptance remains greater than (479/528)^7>1/2. The q, d, J and r schedule are fixed, so the previously recorded statistical budget and recursive call multiplier are unchanged. No proposed change from a fourth-root to a third-root computational loss is used in this report. All computational-advantage limitations of the existing proof remain in force.

## 7. Conclusion and comparison boundary

The fixed-domain joint optimization produces a real improvement to the complete arithmetic payload bound without loosening the prescribed collision radii or the weakest screened model costs. It demonstrates that the current greedy norm objective is unnecessarily expensive. It does not recover the original paper's reported proof sizes, certify 128-bit knowledge security, establish an optimized implementation's throughput, or prove a global limit of the architecture. A later challenge-distribution change should be compared using this same full-path search and its own proved moment/cardinality conditions, rather than by comparing isolated greedy rows.
