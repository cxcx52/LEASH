//! A fixed-profile completeness check and a LEASH proof round trip.
//! The first computes a Gram norm lower bound using the paper's parameter
//! formulas. The second proves and verifies the same binary identity instance
//! with LEASH's default profile. See docs/completeness.md for the checked scope.

use leash::algebra::{D, Q};
use leash::frontend::{Assignment, BinaryR1cs};
use leash::{prove, setup, verify, Config, Proof};
use serde::Serialize;
use serde_json::json;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
struct Rational {
    numerator: u128,
    denominator: u128,
}

fn gcd(mut a: u128, mut b: u128) -> u128 {
    while b != 0 {
        (a, b) = (b, a % b);
    }
    a
}

impl Rational {
    fn new(numerator: u128, denominator: u128) -> Self {
        assert_ne!(denominator, 0);
        let g = gcd(numerator, denominator);
        Self {
            numerator: numerator / g,
            denominator: denominator / g,
        }
    }

    fn add(self, rhs: Self) -> Self {
        Self::new(
            self.numerator * rhs.denominator + rhs.numerator * self.denominator,
            self.denominator * rhs.denominator,
        )
    }

    fn greater_than(self, rhs: Self) -> bool {
        // The fixed certificate's integers fit u128. No floating-point
        // comparisons, logarithms, or approximate norm calculations are used.
        self.numerator * rhs.denominator > rhs.numerator * self.denominator
    }

    fn positive_difference(self, rhs: Self) -> Self {
        assert!(self.greater_than(rhs));
        Self::new(
            self.numerator * rhs.denominator - rhs.numerator * self.denominator,
            self.denominator * rhs.denominator,
        )
    }
}

// Return the nearest integer to value^(1/degree), proving strict separation
// from both half-integer rounding boundaries. This fixed example has no ties.
fn nearest_root(value: u128, degree: u32) -> u128 {
    let scaled = value * 2u128.pow(degree);
    let mut candidate = 1u128;
    while (2 * candidate + 1).pow(degree) < scaled {
        candidate += 1;
    }
    assert!((2 * candidate - 1).pow(degree) < scaled);
    assert!(scaled < (2 * candidate + 1).pow(degree));
    candidate
}

// If squared_value=x^2, certify t=round(log(x)/log(base)) by
// base^(2t-1) < x^2 < base^(2t+1), avoiding logarithms entirely.
fn nearest_log(squared_value: u128, base: u128) -> u32 {
    let mut t = 1u32;
    while base.pow(2 * t + 1) < squared_value {
        t += 1;
    }
    assert!(base.pow(2 * t - 1) < squared_value);
    assert!(squared_value < base.pow(2 * t + 1));
    t
}

fn ceil_root(value: u128, degree: u32) -> u128 {
    let mut candidate = 1u128;
    while candidate.pow(degree) < value {
        candidate += 1;
    }
    assert!((candidate - 1).pow(degree) < value);
    assert!(value <= candidate.pow(degree));
    candidate
}

fn negacyclic_product(a: &[i64; D], b: &[i64; D]) -> [i64; D] {
    let mut out = [0; D];
    for (i, &x) in a.iter().enumerate() {
        for (j, &y) in b.iter().enumerate() {
            out[(i + j) % D] += if i + j < D { x * y } else { -x * y };
        }
    }
    out
}

fn identity_statement() -> (BinaryR1cs, Assignment) {
    let variables = 3 * D;
    let identity: Vec<Vec<usize>> = (0..variables).map(|i| vec![i]).collect();
    (
        BinaryR1cs {
            variables,
            a: identity.clone(),
            b: identity.clone(),
            c: identity,
            public_pins: Vec::new(),
        },
        Assignment {
            values: vec![true; variables],
        },
    )
}

#[derive(Debug, Serialize)]
struct OriginalCertificate {
    source_variables: usize,
    source_constraints: usize,
    modulus: u64,
    ring_degree: usize,
    input_blocks: usize,
    input_block_length: usize,
    input_norm_squared: u128,
    challenge_energy_convention_tau: u128,
    inner_commitment_rank: u128,
    z_base: u128,
    residue_digit_count_t1: u32,
    residue_base_b1: u128,
    gram_digit_count_t2: u32,
    gram_base_b2: u128,
    upper_triangular_gram_entries: usize,
    gram_energy: u128,
    digit_cauchy_factor: u128,
    target_energy_lower_bound: Rational,
    original_target_budget: Rational,
    positive_gap: Rational,
    every_modular_two_digit_reconstruction_exceeds_budget: bool,
}

fn original_certificate() -> OriginalCertificate {
    // Source anchors: LaBRADOR ePrint 2022/1341, supplied 34-page version,
    // SHA256 87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581.
    // pp.22--24: binary coefficient packing and conjugate copies. We use the
    // stated coefficientwise bitness semantics, not the ambiguous printed ring
    // constant "1" in those formulas. The public binary worst-case cap is
    // beta^2=2*(n_src+3*k_src), a valid strengthening of the source norm bound.
    let source_variables = 3 * D;
    let source_constraints = source_variables;
    let n = source_variables / D;
    let j = [1i64; D];
    let mut j_bar = j;
    for coefficient in j_bar.iter_mut().skip(1) {
        *coefficient = -1;
    }
    let mut blocks = vec![vec![j; n]; 4];
    blocks.extend(vec![vec![j_bar; n]; 4]);
    let r = blocks.len();
    let beta_squared: u128 = blocks
        .iter()
        .flatten()
        .flat_map(|p| p.iter())
        .map(|&x| (x as i128 * x as i128) as u128)
        .sum();
    assert_eq!(
        beta_squared,
        2 * (source_variables + 3 * source_constraints) as u128
    );
    assert_eq!(beta_squared, (r * n * D) as u128); // s^2=beta^2/(rnd)=1.

    // The paper's source lift and original modular-JL size premises hold.
    assert!((source_variables + 3 * source_constraints) as u128 * 128 < 15 * Q as u128);
    assert!(6 * (source_constraints as u128) < Q as u128);
    assert!(beta_squared * 128 * 125u128.pow(2) < 30 * (Q as u128).pow(2));

    // p.6 uses the concrete tau=71 convention. pp.16,19 (Section 5.4):
    // b=round((12*r*tau*s^2)^(1/4)), t1=round(log(q)/log(b)),
    // b1=ceil(q^(1/t1)), t2=round(log(sqrt(24nd)*s^2)/log(b)),
    // b2=round((sqrt(24nd)*s^2)^(1/t2)). Here s^2=1 exactly.
    let tau = 71u128;
    let b = nearest_root(12 * r as u128 * tau, 4);
    let t1 = nearest_log((Q as u128).pow(2), b);
    let b1 = ceil_root(Q as u128, t1);
    let gram_scale_squared = (24 * n * D) as u128;
    let t2 = nearest_log(gram_scale_squared, b);
    let b2 = nearest_root(gram_scale_squared, 2 * t2);
    assert_eq!(t2, 2); // The argument below specializes to two Gram digits.
    let kappa = 1u128; // Explicit test rank; no hardness claim is attached to it.

    // Compute every Gram entry directly in Z[X]/(X^64+1), counting i<=j
    // once. No assumption about Gaussian or independent witness coefficients.
    let mut gram_energy = 0u128;
    let mut gram_count = 0usize;
    for (i, left) in blocks.iter().enumerate() {
        for right in blocks.iter().skip(i) {
            let mut gram = [0i64; D];
            for (a, b) in left.iter().zip(right) {
                for (out, term) in gram.iter_mut().zip(negacyclic_product(a, b)) {
                    *out += term;
                }
            }
            // Hence this integer polynomial is its centered lift modulo q.
            assert!(gram.iter().all(|&x| 2 * x.unsigned_abs() < Q));
            gram_energy += gram
                .iter()
                .map(|&x| (x as i128 * x as i128) as u128)
                .sum::<u128>();
            gram_count += 1;
        }
    }
    assert_eq!(gram_count, r * (r + 1) / 2);

    // For ANY u0,u1 in R_q with g=u0+b2*u1 mod q, let L be centered
    // coefficient lifting. L(g) has minimum coefficient magnitude among its
    // integer representatives. Thus
    // ||L(g)||^2 <= ||L(u0)+b2*L(u1)||^2
    //            <= (1+b2^2)*(||L(u0)||^2+||L(u1)||^2).
    // Summing all upper-triangular entries lower-bounds the COMPLETE target
    // norm: all z,t,h contributions are nonnegative. This proof permits
    // modular reconstruction, arbitrary high digits, and any digit tie rule.
    let cauchy_factor = 1 + b2.pow(2);
    let lower = Rational::new(gram_energy, cauchy_factor);

    // p.15 Eq.(5), p.19 Section 5.4:
    // beta'^2 = 2*beta^2*tau/b^2
    //         + (b1^2*t1/12)*r*kappa*d
    //         + ((b2^2*t2+b1^2*t1)/12)*[r(r+1)/2]*d.
    // This even gives the budget the favorable upper-triangle convention;
    // the full i,j norm sum printed in Fig.3 line14 cannot reduce our bound.
    let budget = Rational::new(2 * beta_squared * tau, b.pow(2))
        .add(Rational::new(
            b1.pow(2) * t1 as u128 * r as u128 * kappa * D as u128,
            12,
        ))
        .add(Rational::new(
            (b2.pow(2) * t2 as u128 + b1.pow(2) * t1 as u128) * gram_count as u128 * D as u128,
            12,
        ));
    let exceeds = lower.greater_than(budget);
    assert!(exceeds);

    OriginalCertificate {
        source_variables,
        source_constraints,
        modulus: Q,
        ring_degree: D,
        input_blocks: r,
        input_block_length: n,
        input_norm_squared: beta_squared,
        challenge_energy_convention_tau: tau,
        inner_commitment_rank: kappa,
        z_base: b,
        residue_digit_count_t1: t1,
        residue_base_b1: b1,
        gram_digit_count_t2: t2,
        gram_base_b2: b2,
        upper_triangular_gram_entries: gram_count,
        gram_energy,
        digit_cauchy_factor: cauchy_factor,
        target_energy_lower_bound: lower,
        original_target_budget: budget,
        positive_gap: lower.positive_difference(budget),
        every_modular_two_digit_reconstruction_exceeds_budget: exceeds,
    }
}

fn main() -> Result<(), String> {
    let (instance, assignment) = identity_statement();
    instance.check_assignment(&assignment.values)?;
    let certificate = original_certificate();
    assert_eq!(instance.variables, certificate.source_variables);
    assert_eq!(instance.a.len(), certificate.source_constraints);
    println!(
        "{}",
        json!({
            "kind": "original_fixed_profile_norm_budget_certificate",
            "source": "A=B=C=I over F2; supplied witness is all ones",
            "source_assignment_valid": true,
            "certificate": certificate,
            "interpretation": "Intended coefficientwise binary packing and its public worst-case norm cap",
            "result": "Gram digits alone exceed the fixed ordinary-round target norm budget",
            "original_protocol_or_library_executed": false
        })
    );

    // Execute the complete LEASH path with its supported default profile.
    let parameters = setup(Config::default())?;
    let proof = prove(&parameters, &instance, &assignment)?;
    let bytes = proof.to_bytes()?;
    let decoded = Proof::from_bytes(&bytes)?;
    let reencoded = decoded.to_bytes()?;
    if reencoded != bytes {
        return Err("canonical proof round trip changed bytes".into());
    }
    let report = verify(&parameters, &instance, &decoded)?;
    if !report.accepted {
        return Err("LEASH honest proof was not accepted".into());
    }
    println!(
        "{}",
        json!({
            "kind": "leash_actual_honest_round_trip",
            "source_variables": instance.variables,
            "source_constraints": instance.a.len(),
            "source": "Same binary identity statement and all-one supplied witness",
            "operations": ["prove", "encode", "decode", "reencode", "verify"],
            "canonical_round_trip_matches": true,
            "configuration": parameters.config,
            "same_profile_as_original_certificate": false,
            "proof_bytes": bytes.len(),
            "verification": report
        })
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_gram_identity_and_conjugate_energy() {
        let j = [1; D];
        let mut j_bar = j;
        j_bar.iter_mut().skip(1).for_each(|x| *x = -1);
        let square = negacyclic_product(&j, &j);
        for (index, &value) in square.iter().enumerate() {
            assert_eq!(value, 2 * index as i64 + 2 - D as i64);
        }
        for (a, b) in [(j, j), (j, j_bar), (j_bar, j_bar)] {
            assert_eq!(
                negacyclic_product(&a, &b)
                    .iter()
                    .map(|x| x * x)
                    .sum::<i64>(),
                87424
            );
        }
    }

    #[test]
    fn fixed_formula_rounding_and_exact_strict_gap() {
        let c = original_certificate();
        assert_eq!(
            (
                c.z_base,
                c.residue_digit_count_t1,
                c.residue_base_b1,
                c.gram_digit_count_t2,
                c.gram_base_b2
            ),
            (9, 10, 10, 2, 8)
        );
        assert_eq!(c.target_energy_lower_bound, Rational::new(28325376, 65));
        assert_eq!(c.original_target_budget, Rational::new(7072256, 27));
        assert_eq!(c.positive_gap, Rational::new(305088512, 1755));
    }
}
