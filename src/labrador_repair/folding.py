"""Rational honest-fold moment certificates for optional filtered challenges.

These are sufficient statistical certificates, not security estimates or a
cryptographic folding implementation. A False result only means the requested
certificate failed. See docs/filtered-folding-moments.md for the general proof.
"""

from fractions import Fraction as F

from .challenges import _validate_degree, filtered_challenge_profile


def _parameters(degree, acceptance_lower, failure_upper, coefficient):
    _validate_degree(degree)
    for name, value in (("acceptance_lower", acceptance_lower),
                        ("failure_upper", failure_upper),
                        ("coefficient", coefficient)):
        if not isinstance(value, F):
            raise ValueError(name + " must be a Fraction")
    if not 0 < acceptance_lower < 1 or not 0 < failure_upper < 1:
        raise ValueError("probability bounds must be strictly between zero and one")
    if coefficient <= 0:
        raise ValueError("coefficient must be positive")
    h = 8 - F(26, 5*degree)
    odds = (1-failure_upper)/failure_upper
    return h, h-4, odds


def elementary_fold_cap_certified(degree, acceptance_lower, failure_upper,
                                  coefficient):
    """Check the independent baseline cap G*a >= 2+sqrt(12*(1-f)/f).

    The squared honest norm cap is Gamma^2=G*d*beta^2. The filter must actually
    accept with probability p>a; this function only checks the moment algebra.
    """
    _, _, odds = _parameters(degree, acceptance_lower, failure_upper, coefficient)
    margin = coefficient*acceptance_lower - 2
    return margin >= 0 and margin*margin >= 12*odds


def paired_fold_cap_certified(degree, acceptance_lower, failure_upper,
                              coefficient):
    """Check the paired-spectrum cap (CAP1) by two rational comparisons."""
    h, _, odds = _parameters(degree, acceptance_lower, failure_upper, coefficient)
    margin = coefficient*acceptance_lower/2 - 1
    return (margin >= 0 and margin*margin >= odds
            and coefficient*coefficient >= h/(acceptance_lower*failure_upper))


def centered_fold_cap_certified(degree, acceptance_lower, failure_upper,
                                coefficient, rho_upper, sqrt_odds_upper):
    """Check centered cap (CAP2) using explicit rational radical upper bounds.

    rho_upper^2 must bound 14*(1-a)/(5*d*a); sqrt_odds_upper^2 must bound
    (1-f)/f. All arguments besides degree are Fraction instances. These supplied
    upper bounds are witnesses to a sufficient certificate, not approximations
    silently treated as exact square roots. This does not optimize the cap.
    """
    _, g, odds = _parameters(degree, acceptance_lower, failure_upper, coefficient)
    for name, value in (("rho_upper", rho_upper), ("sqrt_odds_upper", sqrt_odds_upper)):
        if not isinstance(value, F) or value < 0:
            raise ValueError(name + " must be a nonnegative Fraction")
    rho_squared = F(14, 5*degree)*(1-acceptance_lower)/acceptance_lower
    return (rho_upper*rho_upper >= rho_squared
            and sqrt_odds_upper*sqrt_odds_upper >= odds
            and coefficient >= 2
            and (coefficient-2)**2 >= g/(acceptance_lower*failure_upper)
            and coefficient >= (2+rho_upper)*(1+sqrt_odds_upper))


def filtered_folding_profile(q, degree=64, threshold=34,
                             acceptance_lower=F(901, 1024),
                             failure_upper=F(1, 16), coefficient=F(21, 2),
                             rho_upper=F(1, 12), sqrt_odds_upper=F(31, 8)):
    """Link the exact filter certificate to a centered honest-fold cap.

    Assumes fixed ring vectors s_i before independent filtered c_i are drawn,
    with sum_i ||s_i||^2 <= beta^2. It certifies honest rejection at most f for
    Gamma^2=coefficient*d*beta^2. It does not certify complete protocol parameters.
    """
    if not centered_fold_cap_certified(degree, acceptance_lower, failure_upper,
                                       coefficient, rho_upper, sqrt_odds_upper):
        raise ValueError("the requested sufficient centered cap certificate did not pass")
    challenge = filtered_challenge_profile(q, degree, threshold, 1-acceptance_lower)
    h, g, odds = _parameters(degree, acceptance_lower, failure_upper, coefficient)
    return {
        "scope": "Honest-fold statistical certificate only; not full security",
        "challenge_certificate": challenge,
        "gamma_squared_over_d_beta_squared": coefficient,
        "honest_fold_rejection_probability_upper": failure_upper,
        "raw_fourth_moment_coefficient_h": h,
        "raw_variance_coefficient_g": g,
        "conditional_mean_shift_squared_upper": F(14, 5*degree)*(1-acceptance_lower)/acceptance_lower,
        "failure_odds": odds,
        "rho_rational_upper": rho_upper,
        "sqrt_failure_odds_rational_upper": sqrt_odds_upper,
        "required_chronology": "Fix every s_i before drawing independent filtered c_i",
        "required_witness_energy": "sum_i ||s_i||^2 <= beta^2",
    }
