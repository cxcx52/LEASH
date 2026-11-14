"""Exact scalar certificates for refined computational-loss inequalities.

All eta inputs are supplied probabilities/upper bounds for complete collision
experiments. This module does not obtain them from lattice cost estimates,
implement an extractor, or establish that a protocol satisfies the premises.
Gate and finite non-gated formulas are deliberately separate APIs.
"""

from fractions import Fraction as F


def _nonnegative(value, name):
    if not isinstance(value, F) or value < 0:
        raise ValueError(name + " must be a nonnegative Fraction")


def _probability(value, name):
    _nonnegative(value, name)
    if value > 1:
        raise ValueError(name + " must be at most one")


def _kappa(value):
    _probability(value, "kappa")
    if value == 1:
        raise ValueError("kappa must be strictly below one")


def _gap(value):
    _probability(value, "delta")
    if not 0 < value < 1:
        raise ValueError("delta must be strictly between zero and one")


def _positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(name + " must be a positive integer")


def collision_loss_envelope(multiplicity, eta_h, eta_y, eta_g):
    """Return H=2*eta_h+2*r*eta_y+eta_g >= K_exact^2.

    eta_y is the UNCONDITIONAL success probability of the experiment selecting
    one coordinate uniformly. multiplicity can be the proved uniform r_max.
    H itself can exceed one; it is an envelope, not a probability.
    """
    _positive_integer(multiplicity, "multiplicity")
    for name, value in (("eta_h", eta_h), ("eta_y", eta_y), ("eta_g", eta_g)):
        _probability(value, name)
    return 2*eta_h+2*multiplicity*eta_y+eta_g


def gated_upper_root_certified(kappa, eta_0, h, upper):
    """Certify an upper root of B^2-kappa*B <= eta_0+sqrt(h*B).

    h must already upper-bound K_exact^2 for the common-anchor experiments.
    For positive upper, require upper>=kappa, D>=0 and D^2>=h*upper, where
    D=upper^2-kappa*upper-eta_0. Zero is certified ONLY when all three inputs
    kappa, eta_0 and h vanish; otherwise squaring could accept a spurious zero.
    A False result only means this upper-root certificate failed.
    """
    _kappa(kappa)
    _probability(eta_0, "eta_0")
    _nonnegative(h, "h")
    _nonnegative(upper, "upper")
    if upper == 0:
        return kappa == eta_0 == h == 0
    difference = upper*upper-kappa*upper-eta_0
    return upper >= kappa and difference >= 0 and difference*difference >= h*upper


def gated_bad_mass_upper(kappa, eta_0, h, root_upper):
    """Return min(1,root_upper) after validating the gate root certificate."""
    if not gated_upper_root_certified(kappa, eta_0, h, root_upper):
        raise ValueError("the gated upper-root certificate did not pass")
    return min(F(1), root_upper)


def simple_gated_root_upper(kappa, eta_0, h, sqrt_eta_0_upper, cuberoot_h_upper):
    """Certify kappa+A+C with rational A^2>=eta_0 and C^3>=h.

    The result is an uncapped ROOT bound, so it can be passed directly to the
    root-certificate API. It implements the constant-one cubic-root loss bound
    without approximating either radical.
    """
    _kappa(kappa)
    _probability(eta_0, "eta_0")
    _nonnegative(h, "h")
    _nonnegative(sqrt_eta_0_upper, "sqrt_eta_0_upper")
    _nonnegative(cuberoot_h_upper, "cuberoot_h_upper")
    if sqrt_eta_0_upper**2 < eta_0 or cuberoot_h_upper**3 < h:
        raise ValueError("the supplied rational radical upper bound is too small")
    return kappa+sqrt_eta_0_upper+cuberoot_h_upper


def gated_witness_lower(acceptance, kappa, multiplicity, challenge_count,
                        eta_0, h, eta_e, *, root_upper):
    """Conditional gate witness bound max(0,epsilon-r/N-B_upper-eta_E).

    kappa is already inside the bad-mass root equation and is NOT subtracted
    again. Requires the original single-gate premise b_theta<=epsilon_theta,
    the same anchor law and the reviewed selector/root arguments.
    """
    _probability(acceptance, "acceptance")
    _positive_integer(multiplicity, "multiplicity")
    _positive_integer(challenge_count, "challenge_count")
    if challenge_count <= 2:
        raise ValueError("challenge_count must be greater than two")
    _probability(eta_e, "eta_e")
    bad = gated_bad_mass_upper(kappa, eta_0, h, root_upper)
    return max(F(0), acceptance-F(multiplicity, challenge_count)-bad-eta_e)


def finite_upper_root_certified(delta, eta_0, h, upper):
    """Certify the DIFFERENT non-gated inequality delta*B<=eta_0+sqrt(h*B).

    For positive upper, D=delta*upper-eta_0 must be nonnegative and satisfy
    D^2>=h*upper. Zero is valid only when eta_0=h=0. This is not a cubic-root
    gate certificate and makes no b_theta<=epsilon_theta assumption.
    """
    _gap(delta)
    _probability(eta_0, "eta_0")
    _nonnegative(h, "h")
    _nonnegative(upper, "upper")
    if upper == 0:
        return eta_0 == h == 0
    difference = delta*upper-eta_0
    return difference >= 0 and difference*difference >= h*upper


def finite_bad_mass_upper(delta, eta_0, h, *, root_upper=None):
    """Bound Bad intersect High for the finite non-gated anchor experiment.

    With no root_upper, return min(1,2*eta_0/delta+h/delta^2). An explicit
    root_upper may instead certify the tighter finite scalar root. The cap at
    one is a probability cap and need not itself be an upper ROOT certificate.
    """
    _gap(delta)
    _probability(eta_0, "eta_0")
    _nonnegative(h, "h")
    if root_upper is None:
        return min(F(1), 2*eta_0/delta+h/(delta*delta))
    if not finite_upper_root_certified(delta, eta_0, h, root_upper):
        raise ValueError("the finite non-gated upper-root certificate did not pass")
    return min(F(1), root_upper)


def finite_witness_lower(acceptance, kappa, delta, zeta, eta_0, h, eta_e, *,
                         root_upper=None):
    """Finite non-gated witness bound epsilon-kappa-delta-zeta-B_H-eta_E.

    Requires kappa+delta<1 and the original finite anchor/execution-cap theorem.
    zeta is its supplied failure bound. No runtime or zeta estimate is computed
    here. The gate cubic-root bound must not be substituted for B_H.
    """
    _probability(acceptance, "acceptance")
    _kappa(kappa)
    _gap(delta)
    if kappa+delta >= 1:
        raise ValueError("the finite theorem requires kappa+delta<1")
    _probability(zeta, "zeta")
    _probability(eta_e, "eta_e")
    bad = finite_bad_mass_upper(delta, eta_0, h, root_upper=root_upper)
    return max(F(0), acceptance-kappa-delta-zeta-bad-eta_e)
