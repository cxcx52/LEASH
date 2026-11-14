# Same-domain comparison for the bounded-energy challenge profile

Date: 2026-11-14. Scope: exact deterministic norm/packing/payload optimization in a fixed finite domain, followed by pinned heuristic cost formulas for all 21 matrix roles. No lattice instance, reduction algorithm, prover, or forgery was run.

The energy-104/operator-30 profile reduces the same-domain optimum from **185.734375 KiB to 179.6484375 KiB**, saving 49,856 bits =6,232 bytes =6.0859375 KiB, or approximately 3.27669%. The minimum of each of the five screened cost models increases. The complete statistical bound after Q=128 restarts remains below 2^−128, with less margin than the previous cube profile. These are distinct arithmetic, probability, and heuristic-cost statements; they do not constitute a concrete 128-bit knowledge-security result.

Artifacts:

- Exact search: `scripts/joint_energy_parameter_search.py`.
- Complete optimized path, source hashes, replayed old choices, and Pareto frontiers: `notes/parameter-results/joint-energy.json`.
- All 21 pinned model roles: `notes/parameter-results/joint-energy-models.json`.
- Comparison ledger and hashes: `notes/parameter-results/joint-energy-comparison.json`.
- Regression rerun of the original cube model: `notes/parameter-results/joint-cube-regression.json`.

The original `joint_parameter_search.py`, `notes/parameter-results/joint-cube.json`, and `notes/parameter-results/joint-cube-models.json` are preserved. The pure cost driver adds an explicit `bounded-energy` profile with a separate full-path validator; its existing centered-fourth profile was rerun and its complete `profiles` output exactly matches the previous result.

## 1. Shared domain and the changed challenge family

Both searches fix

    q=4294967197, d=64, J=1024, H=640,
    f=1/16, s²=16/3,
    inner rank κ=24, both outer ranks=16,
    r=(112,33,15,8,7,5,4),
    initial n=37450, beta=16384.

They use exactly the same variable domain:

    b∈{2,4,8,16,32,64,128,256},
    t1∈{max(2,nominal−1),max(2,nominal),max(2,nominal+1)},
    nominal=max(2,ceil(log_b q)),
    t2∈{2,...,19}.

The same three collision-radius limits are imposed before optimization:

    inner weak radius ≤918564400,
    inner Gram radius ≤918564400,
    outer radius 2B ≤168800.

The same strict R<q checks, JL modulus inequalities, initial source lifting, and centered-representative conditions are required. Recursive edges use `B=ceil(s beta_next)`; the final explicit opening uses `B=beta_next`. The last decomposition quotient retains the complete carry bound and its actual signed encoding range, including when t1 is one less than the nominal count. This is the same decomposition convention as the previous joint search, not an uncharged change in its relation.

Only the challenge family and its proved concentration inputs change:

| Quantity | Previous filtered cube | New filtered energy ball |
|---|---:|---:|
| Raw coefficient set | Full five-symbol cube | Five-symbol cube with energy ≤104 |
| Strict operator threshold T | 34 | 30 |
| Deterministic challenge energy cap | 256 | 104 |
| Certified operator-filter acceptance within its raw family | >901/1024 | >2/3 |
| Honest fold cap Γ²/(d beta²) | 21/2 | 9 |
| Certified final challenge cardinality lower bound | 476985428422577878437849108195223379880189896 | 13936729633962967329980914140531014408519511 |

The new count and non-iid raw-ball moment theorem are proved in `proofs/fixed_energy_challenge_exploration.md`. In particular, the raw ball's dependent coordinate magnitudes are handled by their exact m2,m4,m22 values. The cube's iid fourth-moment formula is not reused for the ball.

The new search recomputes the raw ball count, the tilted counting tail, the exact coefficient-nine moment inequalities, and the entire Q=128 statistical expression before optimizing. It also reuses the existing unit-difference ring certificate. The zero challenge remains available, including for the exact 1/|C| abort-coin construction.

## 2. Why same-domain arithmetic dominance is valid

Consider any old feasible digit path, with its fixed sequence of b,t1,t2 and paired padding. Apply those choices to the new challenge profile, starting at the same n,beta.

For fixed incoming n,beta and digits, replacing Γ²=(21/2)d beta² by 9d beta² decreases or preserves the integer Gamma ceiling. All remaining deterministic decomposition terms are unchanged. Therefore beta_next and the actual B do not increase. Replacing T34 by T30 then decreases or preserves both inner bounds

    8T(b+1)B,
    2(b+1)B+4T ceil(s beta),

and the outer bound 2B also does not increase.

For fixed digits, the auxiliary ring length is independent of beta and T. The paired next rank is the minimum of

    max(ceil(n/nu),ceil(M_aux/mu)),       2nu+mu=r_next.

Thus copying a complete old digit path preserves its n sequence, while induction gives a no-larger beta sequence. All old radius/JL constraints remain satisfied. Early-message bit ranges are nondecreasing in beta; final z and g ranges are nondecreasing in Gamma and beta; t/h ranges are unchanged. The copied path's payload therefore cannot increase.

This proves that the new optimum is no greater than the old optimum **under these common arithmetic constraints and payload objective**. Both profiles separately satisfy the common final statistical target. It does not prove that the new statistical error is smaller, or that every role of the separately optimized new path is harder than its old counterpart.

The search still uses states (n,beta,C), where C is the accumulated early-message bit count. Its componentwise state dominance proof is the one in `notes/joint_parameter_search.md`, with coefficient 9 replacing 21/2. Every transition remains monotone, and the allowed future digits depend only on the stage and fixed modulus. The same exact skyline routine and its independent quadratic check are reused. There is no beam cutoff or heuristic deletion of states. Consequently the result is an exact minimum of this finite arithmetic domain; it is not a global protocol or implementation optimum.

## 3. Full recomputed path

The chosen path is:

| Layer | n | r | beta | b | t1 | t2 | Gamma | beta_next | Actual B | Weak radius | Gram radius | Outer radius |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37450 | 112 | 16384 | 16 | 8 | 6 | 393216 | 35098 | 81056 | 330708480 | 7296464 | 162112 |
| 2 | 5795 | 33 | 35098 | 32 | 7 | 5 | 842352 | 32627 | 75349 | 596764080 | 14699754 | 150698 |
| 3 | 1754 | 15 | 32627 | 64 | 6 | 5 | 783048 | 21402 | 49426 | 771045600 | 15467260 | 98852 |
| 4 | 877 | 8 | 21402 | 64 | 5 | 5 | 513648 | 20834 | 48115 | 750594000 | 12186070 | 96230 |
| 5 | 440 | 7 | 20834 | 64 | 6 | 5 | 500016 | 12763 | 29475 | 459810000 | 9605550 | 58950 |
| 6 | 440 | 5 | 12763 | 64 | 6 | 5 | 306312 | 10040 | 23187 | 361717200 | 6551310 | 46374 |
| 7 | 443 | 4 | 10040 | 4 | 15 | 8 | 240960 | 77874 | 77874 | 93448800 | 3561180 | 155748 |

Gamma is exactly 24 beta in this d64 profile. The paired splits are (7,19),(4,7),(2,4),(2,3),(1,3),(1,2). Every dimension, padding requirement, target cap, actual B, and collision radius is reconstructed from the formulas during validation; no old B value is retained after changing T or Gamma.

The largest inner radius is 771045600 and the largest outer radius is 162112, both below the original fixed limits. The final B=77874 is a directly checked explicit-opening cap. It is larger than the old optimum's final B=68879 because the new optimizer selects fewer final g digits. This is allowed at the terminal level and must not be copied to a recursive edge without the extraction slack.

## 4. Isolating profile improvement from path optimization

| Quantity | Old cube optimum | Old digits recomputed with energy profile | New energy optimum |
|---|---:|---:|---:|
| Early-message bits | 692224 | 691200 | 691200 |
| Final-opening bits | 829312 | 799936 | 780480 |
| Total bits | 1521536 | 1491136 | 1471680 |
| Total KiB | 185.734375 | 182.0234375 | 179.6484375 |

The copied old choices already save 30,400 bits. Joint optimization saves another 19,456 bits. This separates the change in proved challenge/fold parameters from the benefit of adapting the digit path. The final saving fraction relative to the old optimum is exactly 779/23774.

Search counts and retained frontiers are recorded in the JSON. The stage counts are:

| Layer | Input states | Feasible transitions | Unique successors | Pareto successors |
|---|---:|---:|---:|---:|
| 1 | 1 | 10 | 10 | 2 |
| 2 | 2 | 63 | 63 | 3 |
| 3 | 3 | 225 | 225 | 3 |
| 4 | 3 | 390 | 390 | 4 |
| 5 | 4 | 500 | 500 | 4 |
| 6 | 4 | 594 | 593 | 6 |
| 7 | 6 | 1500 | terminal | terminal |

The ledger retains two outer commitments at every ordinary layer, six aggregation polynomials, 1024 JL coordinates per layer, and all final digits. It omits the source wrapper's messages, statement/setup data, verifier messages, framing, and Fiat–Shamir material. The result is a conservative encoding upper bound, not measured network traffic or a comparison with the paper's optimized 53.84 KB terminal protocol.

## 5. Independent model execution for all 21 roles

The pure cost driver ran under SageMath 10.9 in WSL, against the clean pinned estimator commit

    53da5982597709ba0fdf94ea37a84d822310fd84.

The driver invokes `SISLattice.cost_euclidean` and model cost formulas only. Before screening, its new profile branch invokes the complete bounded-energy path validator, including the count/moment/statistical certificates. The result records the path SHA-256. Deliberate changes to T, actual B, total payload, or the certified cardinality were rejected by the validator.

All seven inner roles have 24 ring rows. Their generic scalar constraint count is 1536, and their available scalar columns are 64n. The resulting model block parameters are:

| Layer | Inner ring columns | Inner radius | Generic block | Single-CRT block |
|---|---:|---:|---:|---:|
| 1 | 37450 | 330708480 | 647 | 2300 |
| 2 | 5795 | 596764080 | 596 | 1943 |
| 3 | 1754 | 771045600 | 576 | 1812 |
| 4 | 877 | 750594000 | 578 | 1825 |
| 5 | 440 | 459810000 | 618 | 2091 |
| 6 | 440 | 361717200 | 639 | 2241 |
| 7 | 443 | 93448800 | 775 | 3427 |

The fourteen outer roles each have 16 ring rows. With G=r(r+1)/2, their ring-column counts are `r t1 κ+G t2` and `G t1`, respectively:

| Layer | First / second outer ring columns | Radius | Generic blocks, first / second | Single-CRT result |
|---|---:|---:|---:|---|
| 1 | 59472 / 50624 | 162112 | 1392 / 1392 | No fit through min(m,65536) |
| 2 | 8349 / 3927 | 150698 | 1414 / 1414 | No fit through min(m,65536) |
| 3 | 2760 / 720 | 98852 | 1551 / 1551 | No fit through min(m,65536) |
| 4 | 1140 / 180 | 96230 | 1561 / 1561 | No fit through min(m,65536) |
| 5 | 1148 / 168 | 58950 | 1745 / 1745 | Reduced integer energy zero |
| 6 | 795 / 90 | 46374 | 1845 / 1845 | Reduced integer energy zero |
| 7 | 1520 / 150 | 155748 | 1404 / 1404 | No fit through min(m,65536) |

No single-CRT row lowers the minimum of any displayed model. Across all 21 roles and both modeled routes, every minimum occurs at the third-layer generic inner role:

| Model | Old cube minimum | Energy minimum |
|---|---:|---:|
| Classical Core-SVP .292 | 164.104 | 168.192 |
| Quantum Core-SVP .265 | 148.930 | 152.640 |
| Quantum-walk Core-SVP .257 | 144.434 | 148.032 |
| Fitted MATZOV classical | 189.390660 | 193.300747 |
| Estimator quantum depth-times-width fit | 179.227505 | 182.745291 |

The generic inner blocks are within the fitted model's documented 1024-block range; outer and inner-CRT fitted outputs are extrapolations, as flagged in the JSON. “No fit through 65536” is a bounded model statement, not a security lower bound. The structured module lattice and coefficient-norm conventions, model units, and other limits remain those documented in `notes/computational_parameter_screen.md`.

The optimized paths do not have componentwise identical roles. In particular, the new terminal outer radius 155748 exceeds the old terminal radius 137758. The fixed cap is preserved and the overall screened minima improve; claiming every one of the 21 individual roles improved would be false.

## 6. Statistical margin and completeness are reported separately

For N_min=13936729633962967329980914140531014408519511, the new profile explicitly checks

    128 [198/N_min+7·2^−164+7/q^6+7/q^32+2^−160] < 2^−128.

Its displayed exponent is approximately 128.69244342, compared with approximately 133.78942133 for the previous cube count under the same expression. The ball gives up about five bits of this statistical margin. Both meet the fixed target, but the new challenge family does not dominate the old statistical error numerically.

The per-layer honest acceptance remains greater than 479/528 because the JL and fold rejection targets remain 1/33 and 1/16. The seven-layer product is greater than one half. Under the reviewed complete-restart policy, Q=128 gives honest final rejection below 2^−128 and expected honest attempts below two. These are conditional mathematical guarantees for this fully checked arithmetic path; sampling implementation and the cost of rejected attempts are not measured here.

Computational binding/extraction losses remain additional. The improved cube-root loss theorem, where applicable, still needs actual advantages and complete reduction runtimes. The heuristic exponents in Section 5 cannot be substituted for those advantages without a concrete model and budget. The report does not claim 128-bit knowledge security, a quantum extraction theorem, or an end-to-end noninteractive proof size.

## 7. Reproduction

From the research workspace:

    python scripts/joint_energy_parameter_search.py

The WSL pure-model command used was:

    sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile bounded-energy --path-input work/joint_energy_parameter_search.json --output work/joint_energy_model_screen.json

The old centered-fourth command was rerun into the new `joint_cube_model_regression.json` file, and the complete profile output was checked for exact equality with the saved old result. Existing reports and results were not overwritten. Decisive count, moment, norm, feasibility, payload, and dominance comparisons use integers or Fraction. Floating-point logarithms are confined to the explicitly heuristic cost model and displayed exponents; elapsed search times are descriptive only.
