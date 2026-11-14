"""Exact finite probability checks for bad-mass-weighted collision losses.

These are abstract probability distributions, not protocol transcripts, forgeries,
or an attack implementation. The proof is in computational_loss_refinement.md.
"""

from fractions import Fraction as F
from itertools import product
import json


def canonical_masses(accepted_masses):
    accepted = sum(accepted_masses, F(0))
    nonmodal = accepted-max(accepted_masses, default=F(0))
    collision = accepted*accepted-sum((x*x for x in accepted_masses), F(0))
    assert 0 <= accepted <= 1
    assert collision >= accepted*nonmodal >= nonmodal*nonmodal
    return accepted, nonmodal, collision


def mass_inequality_holds(bad_mass, kappa, eta0, k_squared):
    difference = bad_mass*bad_mass-kappa*bad_mass-eta0
    return difference <= 0 or difference*difference <= k_squared*bad_mass


def upper_root_certified(bound, kappa, eta0, k_squared):
    """Check the upper root by rational squaring, with the zero-root trap excluded."""
    assert min(bound, kappa, eta0, k_squared) >= 0
    if bound == 0:
        return kappa == eta0 == k_squared == 0
    difference = bound*bound-kappa*bound-eta0
    return (bound >= kappa and difference >= 0
            and difference*difference >= k_squared*bound)


def checks():
    distributions = [tuple(F(x, 4) for x in row)
                     for row in product(range(5), repeat=3) if sum(row) <= 4]
    masses = [canonical_masses(row) for row in distributions]
    weighted_cases = 0
    for left, right in product(masses, repeat=2):
        for bad_flags in product((0, 1), repeat=2):
            bad = F(sum(bad_flags), 2)
            weighted_error = sum((F(flag, 2)*entry[1]
                                  for flag, entry in zip(bad_flags, (left, right))), F(0))
            eta = F(left[2]+right[2], 2)
            assert weighted_error*weighted_error <= bad*eta
            weighted_cases += 1

    selector_cases = 0
    anchor_weights = (F(1, 3), F(2, 3))
    prefix_weights = (F(1, 6), F(1, 3), F(1, 2))
    r = 3
    for bad_flags in product((0, 1), repeat=2):
        for offset in range(len(masses)):
            bad = sum((w*flag for w, flag in zip(anchor_weights, bad_flags)), F(0))
            selected_error = eta_y = F(0)
            for anchor, anchor_weight in enumerate(anchor_weights):
                for prefix, prefix_weight in enumerate(prefix_weights):
                    chosen = (anchor+prefix+offset) % r
                    for coordinate in range(r):
                        _, error, collision = masses[(offset+7*anchor+5*prefix+coordinate) % len(masses)]
                        weight = anchor_weight*prefix_weight
                        eta_y += weight*collision/r
                        if bad_flags[anchor] and coordinate == chosen:
                            selected_error += weight*error
            assert selected_error*selected_error <= r*bad*eta_y
            selector_cases += 1
    # If only one of r coordinates carries two equal accepted modes, omitting
    # the r under the square root fails even in this elementary finite model.
    _, error, collision = canonical_masses((F(1, 2), F(1, 2)))
    assert error*error > collision/3
    assert error*error <= 3*(collision/3)

    gate_cases = 0
    for numerator0, numerator1 in product(range(9), repeat=2):
        epsilon0, epsilon1 = F(numerator0, 8), F(numerator1, 8)
        for bad0 in range(numerator0+1):
            for bad1 in range(numerator1+1):
                b0, b1 = F(bad0, 8), F(bad1, 8)
                bad = (b0+b1)/2
                for kappa in (F(0), F(1, 8), F(1, 2)):
                    weighted_gap = (b0*max(epsilon0-kappa, 0)
                                    + b1*max(epsilon1-kappa, 0))/2
                    assert weighted_gap >= bad*bad-kappa*bad
                    gate_cases += 1

    root_cases = 0
    for kappa, square_root_eta0, cube_root_k_squared in product(
            (F(0), F(1, 100), F(1, 8)),
            (F(0), F(1, 1000), F(1, 32), F(1, 4)),
            (F(0), F(1, 1000), F(1, 32), F(1, 4))):
        eta0 = square_root_eta0**2
        k_squared = cube_root_k_squared**3
        upper = kappa+square_root_eta0+cube_root_k_squared
        assert upper_root_certified(upper, kappa, eta0, k_squared)
        for numerator in range(1001):
            candidate = F(numerator, 1000)
            if mass_inequality_holds(candidate, kappa, eta0, k_squared):
                assert candidate <= upper
            root_cases += 1
        for delta in (F(1, 100), F(1, 8), F(1, 2)):
            finite_upper = 2*eta0/delta+k_squared/(delta*delta)
            difference = delta*finite_upper-eta0
            assert difference >= 0
            assert difference*difference >= k_squared*finite_upper
    assert not upper_root_certified(F(0), F(0), F(0), F(1, 1000))

    tightness_instances = []
    for denominator in (2, 4, 8, 16, 32):
        b = F(1, denominator)
        # Accepted labels are (h0,y1) and (h1,y0), each with mass b/2.
        # Rejection has mass 1-b. Lexicographic modal labels h0,y0 never cooccur.
        labels = ((0, 1, b/2), (1, 0, b/2))
        assert sum(mass for h, y, mass in labels if h == 0 and y == 0) == 0
        _, error_h, collision_h = canonical_masses((b/2, b/2))
        _, error_y, collision_y = canonical_masses((b/2, b/2))
        bad_mass, epsilon, kappa = b, b, b**4
        eta_h, eta_y = b*collision_h, b*collision_y
        assert error_h+error_y == epsilon
        assert eta_h == eta_y == b**3/2
        exact_k_squared = 4*eta_h
        assert exact_k_squared == 2*b**3
        assert mass_inequality_holds(bad_mass, kappa, F(0), exact_k_squared)
        assert upper_root_certified(kappa+F(4, 3)*b, kappa, F(0), exact_k_squared)
        # N=2*m^4 makes the illustrative root-count allowance 2/N=b^4.
        challenge_count = 2*denominator**4
        assert F(2, challenge_count) == kappa
        assert challenge_count*b/2 == denominator**3
        tightness_instances.append({"b": str(b), "kappa": str(kappa),
                                    "eta_h": str(eta_h), "eta_y": str(eta_y)})
    return {
        "scope": "Abstract finite probability checks; not a protocol attack",
        "canonical_distributions": len(distributions),
        "weighted_cauchy_cases": weighted_cases,
        "uniform_coordinate_selector_cases": selector_cases,
        "gate_jensen_cases": gate_cases,
        "root_bound_candidate_checks": root_cases,
        "abstract_cube_root_scale_instances": tightness_instances,
        "all_checks_passed": True,
    }


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))
