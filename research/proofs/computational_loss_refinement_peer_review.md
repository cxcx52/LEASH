# Independent review of the cubic-root computational loss

Date: 2026-11-14. Reviewed source: `computational_loss_refinement.md`, SHA256
`e01193409c3511e3fd146361e637836049579f2611e845c4674e730c65b5c0e6`.
The author checker has SHA256
`2b0fbfe011a360ddfd9b42854c2469e1c913f8c4701824e87052f9c5813d1837`.

**Verdict:** the refinement is valid under the original algebraic and extractor
premises. No blocking error was found. In particular, the factor `sqrt(r)` in
the selected-coordinate error, the disjoint bad-mass partition, and the
constant-one explicit cubic-root bound all survive independent checking.
This review does not establish a numerical security level, replace the original
MSIS collision validity proofs, or verify an implementation of an extractor.

## 1. Probability space and what is being bounded

I compared the new note with `computational_binding_review.md`, Sections 2–7,
`composition_repair.md`, Sections 4–10, and `bounded_restart_repair.md`.
The new argument uses the same **complete** anchor law as the collision
reductions, including the failure/collision output bottom. Fresh masses are
zero at bottom. It does not divide any advantage by the probability of getting
an anchor, reaching a particular upper prefix, or being on a bad instance.

For a local accepted subprobability distribution `(p_v)`, let
`a=sum p_v`, `e=a-max p_v`, and `c=a^2-sum p_v^2`.
The elementary inequality `c >= a e >= e^2` is correct. If `D` is an event in
the anchor/prefix law, weighted Cauchy–Schwarz gives

    (E[1_D e])^2 <= Pr[D] E[1_D e^2] <= Pr[D] E[c].

The collision event here compares two independent suffixes sampled at the
same saved prefix. Its probability is unnormalized, exactly as required by
the actual samplers. Conditioning on acceptance would change this formula.

The partition is correctly defined as

    Bad_G = Bad intersect {norm valid and anchored Gram wrong},
    Bad_N = Bad minus Bad_G.

The explicit intersection with `Bad` is essential: a valid source witness can
have an inconsistent auxiliary Gram value in an anchor. Such an anchor is not
an invalid extracted source witness. With this definition, `B_N+B_G=B` and the
two-dimensional Cauchy–Schwarz step has the claimed total mass `B`.

## 2. The selector and the coordinate factor

The selected diagonal `iota(A,U)` depends only on the completed anchor and on
the fresh prefix through the second outer commitment. The modal packed `h`
is a function of the distribution of future suffixes. It is not a function
of their realized challenges or final-reply coins. Thus the selector is fixed
before all final challenges, including `c_{-i}`.

The collision sampler still chooses `I` uniformly and independently of
`A,U`. No efficient evaluation of the mode or selector is needed. With

    W = 1_Bad_N 1_{I=iota(A,U)},

we have `E W <= B_N/r`. The selected nonmodal mass is `r E[W e_I]`, so

    (r E[W e_I])^2
        <= r^2 E[W] E[W e_I^2]
        <= r B_N E[c_I]
        =  r B_N eta_y.

This checks both the factor `r` under the square root and the unconditional
definition of `eta_y`. The remaining complement challenges have the correct
conditional product distribution; they are integrated after fixing `I`.

For a public varying `r`, Cauchy–Schwarz can be applied to
`sqrt(r W)` and `sqrt(r W) e_I`. Then `E[r W] <= B_N` and
`E[r W e_I^2] <= r_max eta_y`. Hence the stated `r_max` extension is also
valid. It is not necessary to pretend that the random `r` is a fixed number
inside an expectation.

The root containment from the original diagonal argument remains available:
discarding nonmodal `h` fixes the selected nonzero quadratic coefficient;
discarding nonmodal `y` on the selected slice fixes the other coefficients
before varying its challenge. A union over all `r` errors is unnecessary.

The selector cannot be allowed to inspect `I` or the realized final
challenges. In the first case the indicator mass can be `B_N` rather than
`B_N/r`; in the second the polynomial being counted need not be fixed. The
reviewed source explicitly excludes both changes.

## 3. Combined bound and gate calculation

Weighted integration gives the three masses

    sqrt(B_N eta_h), sqrt(r B_N eta_y), sqrt(B_G eta_g).

Combining the first two on `Bad_N`, then applying Cauchy–Schwarz between the
two disjoint parts, gives

    E[1_Bad (epsilon_theta-kappa)_+]
        <= eta_0 + sqrt(B) K,
    K^2 = (sqrt(eta_h)+sqrt(r eta_y))^2 + eta_g
        <= 2 eta_h + 2 r eta_y + eta_g.

No factor two is required on `eta_g`. The first-opening mismatch is already
measured against a known anchor opening, so its integrated contribution is
`eta_0`, with no local square root. Using its unconditional value remains a
valid upper bound after restricting to `Bad`.

For the universal extractor only, the initial ordinary acceptance gate gives
`b_theta=Pr[Bad|theta] <= epsilon_theta`. Consequently

    E[b_theta (epsilon_theta-kappa)_+]
        >= E[b_theta^2] - kappa B
        >= B^2 - kappa B.

This proves the new scalar inequality with the same statistical `kappa`.
For `A=sqrt(eta_0)` and `C=K^(2/3)`, suppose `B>kappa+A+C`.
Then `A^2<=AB` and `K sqrt(B)=C^(3/2)sqrt(B)<=CB`, contradicting
`B(B-kappa)<=eta_0+K sqrt(B)`. Thus

    B <= kappa + sqrt(eta_0) + (K^2)^(1/3).

The proof includes zero parameters and uses no numerical approximation.
Subtracting this bad mass and `eta_E` from the unchanged
candidate-or-collision mass `epsilon_bar-r/N` yields precisely the claimed
witness-only theorem.

The exact-root certificate is correct. For positive `R>=kappa`, the function
`(R^2-kappa R-eta_0)/sqrt(R)` is strictly increasing and crosses `K` at most
once. Nonnegative `D=R^2-kappa R-eta_0` and `D^2>=H R`, with `H>=K^2`,
therefore certify an upper root. The explicit special handling of `R=0`
avoids the spurious root produced by squaring when `K>0`.

## 4. Bounded anchors, randomized replies, and restarts

The finite non-gated anchor searches for an acceptance, and in general its
bad-candidate probability need not be at most the original acceptance
probability. The new note correctly uses a different theorem there. On
`High={epsilon_theta>=kappa+Delta}`, weighted integration yields
`Delta B_H<=eta_0+K sqrt(B_H)`. Its quadratic solution and the simpler
`2 eta_0/Delta+H/Delta^2` upper bound are both correct. Applying the cubic-root
gate theorem to this extractor would be invalid; no such application occurs.

Fresh randomized final replies only enlarge the suffix probability space.
All nonmodal masses average their fresh kernel coins; two suffixes use
independent kernel coins at the same prefix. The selected mode and polynomial
remain fixed before the realized suffix. At a polynomial root the total
kernel acceptance probability is at most one, so the root-count argument is
unchanged. This reasoning depends on the reviewed fresh-kernel, no-shared-cache
wrapper and its uniform per-state expected runtime bound.

For ordinary composition, replacing the old per-layer loss by the new one
does not change the virtual prover, relation matching, or the expected-time
product. Every `eta` still charges the complete nested anchor and suffix
experiment. For bounded restarts, the correct application is to each complete
initializer `Gen_j`, including rejected history and the dummy branch after
earlier real acceptance. Gate preservation gives the same first-acceptance
coupling. One sums these initialized losses; one does not silently condition
them on reaching or accepting attempt `j`.

Expected-time reductions still require the stated truncation argument when
invoking strict-PPT MSIS hardness. Nothing in this improvement removes a
runtime or norm obligation. In particular it does not convert one estimator
cost point into an advantage-versus-time theorem.

## 5. Abstract scale example

The author's two-label example is internally consistent. For bad-anchor and
ordinary acceptance probability `b`, the two accepted suffix labels have
mass `b/2` each, with no accepted joint modal pair. The unconditional pair
collision probabilities are `eta_h=eta_y=b^3/2`. The finite uniform space of
size `N=2m^4` at `b=1/m` gives integral label sizes `m^3` and allowance
`2/N=b^4` as stated.

It follows that these **summary probability constraints** allow
`B-kappa` of order `eta^(1/3)`. This is not a realizable protocol example and
does not prove a reduction lower bound for LaBRADOR. The reviewed note
explicitly makes this distinction; its conclusion is appropriately limited.

## 6. Independent exact checks

The new independent checker is
`scripts/computational_loss_peer_checks.py`; output is
`notes/parameter-results/computational_loss_peer_checks.json`. It does not import the author's
checker or implement any cryptographic transcript. It checks:

- 165 accepted subprobability tables;
- 3,900 exact scalar implication cases, using rational squaring;
- 36 selector-scale examples with varying bad mass, index count, acceptance
  mass, and mode count;
- two negative controls showing failure if the gate premise is removed or
  if the selector sees the sampled coordinate;
- a common-anchor finite game containing bottom, two initial states,
  nonuniform anchor probabilities, three fresh upper prefixes, all three
  selected coordinates, and independently randomized final replies.

For the last game, `B_N=1/6`, `B_G=5/24`,
`eta_h=2093/104976`, `eta_y=2483/34992`, and `eta_g=475/17496`.
The weighted errors are respectively `17/1944`, `31/972`, and `203/3888`.
The selected indicator mass is `5/108<=B_N/3=1/18`; all three weighted
inequalities and the combined bound pass exactly. This game validates
probability bookkeeping, not the protocol-specific polynomial containment.

In the selector-scale examples, one preselected coordinate has `M` equally
likely accepted labels. Then

    (selected_error)^2 / (r B_N eta_y) = 1-1/M.

Thus the `sqrt(r)` scale cannot be dropped using only this uniform-coordinate
information. Equality in the comparison without `r` occurs at `r=M=2`;
larger examples give a strict violation. The checker accounts for that
boundary explicitly.

The author's checker was also rerun successfully: 4,900 weighted cases,
140 selector cases, 6,075 gate/Jensen cases, and 48,048 root-bound candidate
checks, together with its finite-gap and five abstract-scale checks. These
finite checks support the independently verified general proof.

No public package, old parameter baseline, protocol implementation, or git
commit was changed by this review.
