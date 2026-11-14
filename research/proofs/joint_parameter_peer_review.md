# Independent review: fixed-domain payload optimization

Date: 2026-11-14. The root reviewer read `notes/joint_parameter_search.md` and `scripts/joint_parameter_search.py`, checked the dominance proof against the cap/encoding formulae, and reran the search. No blocker was found. This is a development review of arithmetic optimization, not an independent lattice-security assessment.

For a fixed stage and digit choice, the cap is nondecreasing in n and beta. The auxiliary length depends on the fixed stage, rank and digits; each legal paired split has a next-n bound nondecreasing in n, and taking its minimum preserves monotonicity. Future choices depend only on the fixed remaining schedule. All feasibility conditions are upper bounds on these monotone quantities. Early bits and the terminal encoding are also monotone for each fixed choice. Thus a smaller `(n,beta,accumulated_bits)` state can copy any feasible future path from a dominated state at no greater objective value.

The search keeps the entire skyline rather than a beam. The initial greedy path is in the searched domain and satisfies the imposed radius caps. Duplicate-state removal is valid for this objective because the relevant future constraints are captured by the retained state. The Fenwick implementation sorts by n, beta and cost and uses a prefix minimum over beta; the supplied independent quadratic skyline check covers its finite behavior.

The final integer quotient is allowed to exceed the base-digit range and is explicitly charged by the carry and Euclidean norm formulae. This is stated as a repaired decomposition convention. It must not be confused with applying an all-digits-small estimate when the shortened t1 does not cover the modulus.

The final witness is checked directly, so its actual B is its checked cap. Recursive predecessors still use the slackened cap of the next extraction. The higher final cap does not propagate backward as a replacement for the previous layer's source cap.

The independent rerun reproduced the same frontier sizes (2,2,3,2,2,2), transition counts, complete path and 1,521,536-bit objective. This is 70,912 bits less than the 1,592,448-bit baseline. It proves optimality only for the stated finite digit domain, fixed shapes/ranks and arithmetic caps. The separate pinned estimator rerun is recorded in the author's output; this review has not independently rerun that estimator and does not upgrade its model outputs to a security certificate.
