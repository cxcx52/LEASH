//! Ordinary outer-commitment reduction with explicit recursive target equations.
//!
//! This is an executable algebraic reduction. Seed-expanded setup and transcript
//! challenges do not establish Fiat--Shamir security or zero knowledge.

use leash_core::{
    centered, commit, dot, matrix_row, residue, Constraint, LinearTerm, Poly, QuadraticTerm,
    Relation, Result, Transcript, Witness, Xof, D, MAX_CONSTRAINTS, MAX_TERMS, MAX_WITNESS_POLYS,
    Q,
};
use serde::{Deserialize, Serialize};

const BASE: u64 = 16;
const DIGITS: usize = 8;

/// Supported implementation profile: ranks 1..=64, exactly 1024 projection
/// rows, and 6..=8 scalar aggregations. These are not security-level claims.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CoreConfig {
    pub inner_rank: usize,
    pub outer_rank: usize,
    pub projection_rows: usize,
    pub aggregation_repetitions: usize,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RoundMessage {
    pub u1: Vec<Poly>,
    pub projection: Vec<i64>,
    pub aggregates: Vec<Poly>,
    pub u2: Vec<Poly>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Reduction {
    pub relation: Relation,
    pub witness: Witness,
}

#[derive(Clone, Debug)]
struct Layout {
    pairs: Vec<(usize, usize)>,
    t_count: usize,
    g_count: usize,
    m: usize,
    z_stride: usize,
    v_stride: usize,
    target_n: usize,
    bound_squared: u128,
}

fn mul_size(a: usize, b: usize) -> Result<usize> {
    a.checked_mul(b)
        .ok_or_else(|| "ordinary dimension overflow".into())
}
fn add_size(a: usize, b: usize) -> Result<usize> {
    a.checked_add(b)
        .ok_or_else(|| "ordinary dimension overflow".into())
}
fn ceil_div(a: usize, b: usize) -> usize {
    a / b + usize::from(a % b != 0)
}
fn norm_add(a: u128, b: u128) -> Result<u128> {
    a.checked_add(b)
        .ok_or_else(|| "ordinary norm budget overflow".into())
}
fn norm_mul(a: u128, b: u128) -> Result<u128> {
    a.checked_mul(b)
        .ok_or_else(|| "ordinary norm budget overflow".into())
}
fn domain(round: usize, role: &str) -> Vec<u8> {
    format!("leash/ordinary/{round}/{role}").into_bytes()
}
fn is_zero(p: &Poly) -> bool {
    p.0.iter().all(|&x| x == 0)
}
fn pair_index(r: usize, i: usize, j: usize) -> usize {
    let (i, j) = if i <= j { (i, j) } else { (j, i) };
    i * (2 * r - i + 1) / 2 + j - i
}

fn layout_shape(relation: &Relation, config: &CoreConfig) -> Result<Layout> {
    relation.validate()?;
    if !(1..=64).contains(&config.inner_rank) || !(1..=64).contains(&config.outer_rank) {
        return Err("ordinary supported commitment ranks are 1..=64".into());
    }
    if config.projection_rows != 1024 || !(6..=8).contains(&config.aggregation_repetitions) {
        return Err(
            "ordinary supported profile requires 1024 JL rows and 6..=8 scalar aggregations".into(),
        );
    }
    let jl_lhs = norm_mul(23 * 250 * 250, relation.bound_squared)?;
    if jl_lhs > 5 * (Q as u128) * (Q as u128) {
        return Err("ordinary input violates 23*250^2*beta^2 <= 5*q^2".into());
    }
    let pair_count = mul_size(relation.r, add_size(relation.r, 1)?)? / 2;
    let t_count = mul_size(mul_size(relation.r, DIGITS)?, config.inner_rank)?;
    let g_count = mul_size(pair_count, DIGITS)?;
    let m = add_size(t_count, mul_size(2, g_count)?)?;
    let z_stride = ceil_div(relation.n, 2);
    let v_stride = ceil_div(m, 4);
    let target_n = z_stride.max(v_stride);
    let target_size = mul_size(8, target_n)?;
    if target_size > MAX_WITNESS_POLYS {
        return Err("ordinary target witness polynomial limit exceeded".into());
    }
    let pins = target_size - add_size(mul_size(2, relation.n)?, m)?;
    let constraints = add_size(
        add_size(config.inner_rank, mul_size(2, config.outer_rank)?)?,
        add_size(3, pins)?,
    )?;
    if constraints > MAX_CONSTRAINTS {
        return Err("ordinary target constraint limit exceeded".into());
    }
    // An upper bound, before dropping zero coefficients, on every generated
    // target term; all arithmetic and checks precede allocating the pair list.
    let inner_terms = mul_size(
        config.inner_rank,
        add_size(mul_size(2, relation.n)?, mul_size(DIGITS, relation.r)?)?,
    )?;
    let terms = add_size(
        add_size(inner_terms, mul_size(config.outer_rank, m)?)?,
        add_size(
            add_size(
                add_size(6, mul_size(2, relation.n)?)?,
                mul_size(3, g_count)?,
            )?,
            add_size(mul_size(DIGITS, relation.r)?, pins)?,
        )?,
    )?;
    if terms > MAX_TERMS {
        return Err("ordinary target term limit exceeded".into());
    }
    let dense_polynomials = mul_size(
        config.aggregation_repetitions,
        add_size(pair_count, mul_size(relation.r, relation.n)?)?,
    )?;
    if dense_polynomials > MAX_TERMS {
        return Err("ordinary aggregation working polynomial limit exceeded".into());
    }
    let nd = mul_size(relation.n, D)? as u128;
    // ||z||^2 <= r*128^2*beta^2, centered reduction can only decrease it.
    // Balanced low digits have magnitude <=8; (a+b)^2 <=2a^2+2b^2.
    let bound_squared = norm_add(
        norm_add(
            norm_mul(nd, 64)?,
            norm_mul(128 * relation.r as u128, relation.bound_squared)?,
        )?,
        norm_add(
            ceil_div(nd as usize, 2) as u128,
            norm_mul(m as u128, (D * 64) as u128)?,
        )?,
    )?;
    Ok(Layout {
        pairs: Vec::new(),
        t_count,
        g_count,
        m,
        z_stride,
        v_stride,
        target_n,
        bound_squared,
    })
}

fn layout(relation: &Relation, config: &CoreConfig) -> Result<Layout> {
    let mut layout = layout_shape(relation, config)?;
    layout.pairs = (0..relation.r)
        .flat_map(|i| (i..relation.r).map(move |j| (i, j)))
        .collect();
    Ok(layout)
}

/// Return the recursive target's `(r, n, squared_norm_cap)` before any round.
///
/// This checks this module's input profile and JL hypothesis. It does not certify
/// any binding radius, cryptographic security level, or future round's profile.
/// Structural count limits are checked without allocating challenge matrices or
/// the triangular pair list; they are not a byte-accurate peak-memory estimate.
pub fn target_shape_and_bound(
    relation: &Relation,
    config: &CoreConfig,
) -> Result<(usize, usize, u128)> {
    let layout = layout_shape(relation, config)?;
    Ok((8, layout.target_n, layout.bound_squared))
}

fn context(
    relation: &Relation,
    seed: &[u8; 32],
    round: usize,
    config: &CoreConfig,
    transcript: &mut Transcript,
) -> Result<()> {
    transcript.absorb_json(b"ordinary/context", &(round, config, seed, relation))
}

fn projection_seed(u1: &[Poly], transcript: &mut Transcript) -> Result<[u8; 32]> {
    transcript.absorb_json(b"ordinary/u1", &u1)?;
    let mut rng = transcript.challenge(b"ordinary/JL");
    let mut seed = [0u8; 32];
    for value in &mut seed {
        *value = rng.uniform(256) as u8;
    }
    Ok(seed)
}

fn project(witness: &Witness, seed: &[u8; 32], rows: usize) -> Vec<i64> {
    let mut rng = Xof::new(seed, b"ordinary/JL/entries");
    (0..rows)
        .map(|_| {
            let mut sum = 0i128;
            for block in witness {
                for p in block {
                    for &coefficient in &p.0 {
                        sum += rng.ternary() as i128 * centered(coefficient) as i128;
                    }
                }
            }
            centered(residue(sum))
        })
        .collect()
}

fn check_projection(relation: &Relation, p: &[i64], config: &CoreConfig) -> Result<()> {
    if p.len() != config.projection_rows {
        return Err("incorrect projection length".into());
    }
    let mut squared = 0u128;
    for &x in p {
        if x != centered(residue(x as i128)) {
            return Err("noncanonical projection representative".into());
        }
        squared = norm_add(squared, (x as i128 * x as i128) as u128)?;
    }
    if squared > norm_mul(552, relation.bound_squared)? {
        return Err("honest-restart: projection exceeds the fixed norm threshold".into());
    }
    Ok(())
}

#[derive(Clone)]
struct DenseEquation {
    quadratic: Vec<Poly>,
    linear: Witness,
    constant: Poly,
}

impl DenseEquation {
    fn zero(relation: &Relation, layout: &Layout) -> Self {
        Self {
            quadratic: vec![Poly::zero(); layout.pairs.len()],
            linear: vec![vec![Poly::zero(); relation.n]; relation.r],
            constant: Poly::zero(),
        }
    }
    fn add_scalar_constraint(&mut self, eq: &Constraint, weight: u64, r: usize) {
        for term in &eq.quadratic {
            let index = pair_index(r, term.left, term.right);
            self.quadratic[index] = self.quadratic[index].add(&term.coefficient.scale(weight));
        }
        for term in &eq.linear {
            let value = &mut self.linear[term.block][term.position];
            *value = value.add(&term.coefficient.scale(weight));
        }
        self.constant = self.constant.add(&eq.constant.scale(weight));
    }
    fn add_ring_constraint(&mut self, eq: &Constraint, weight: &Poly, r: usize) {
        for term in &eq.quadratic {
            let index = pair_index(r, term.left, term.right);
            self.quadratic[index] = self.quadratic[index].add(&term.coefficient.mul(weight));
        }
        for term in &eq.linear {
            let value = &mut self.linear[term.block][term.position];
            *value = value.add(&term.coefficient.mul(weight));
        }
        self.constant = self.constant.add(&eq.constant.mul(weight));
    }
    fn add_dense(&mut self, other: &Self, weight: &Poly) {
        for (a, b) in self.quadratic.iter_mut().zip(&other.quadratic) {
            *a = a.add(&b.mul(weight));
        }
        for (left, right) in self.linear.iter_mut().zip(&other.linear) {
            for (a, b) in left.iter_mut().zip(right) {
                *a = a.add(&b.mul(weight));
            }
        }
        self.constant = self.constant.add(&other.constant.mul(weight));
    }
    fn evaluate_without_constant(&self, witness: &Witness, gram: &[Poly]) -> Poly {
        let mut value = dot(&self.quadratic, gram);
        for (coefficients, block) in self.linear.iter().zip(witness) {
            value = value.add(&dot(coefficients, block));
        }
        value
    }
}

fn scalar_aggregations(
    relation: &Relation,
    layout: &Layout,
    projection: &[i64],
    pi_seed: &[u8; 32],
    config: &CoreConfig,
    transcript: &mut Transcript,
) -> Result<(Vec<DenseEquation>, Vec<u64>)> {
    check_projection(relation, projection, config)?;
    transcript.absorb_json(b"ordinary/p", &projection)?;
    let mut rng = transcript.challenge(b"ordinary/psi-omega");
    let count = config.aggregation_repetitions;
    let mut equations = Vec::with_capacity(count);
    let mut omega = Vec::with_capacity(count);
    let mut expected_constants = Vec::with_capacity(count);
    for _ in 0..count {
        let mut equation = DenseEquation::zero(relation, layout);
        for scalar in &relation.scalar {
            equation.add_scalar_constraint(scalar, rng.uniform(Q), relation.r);
        }
        let weights: Vec<u64> = (0..config.projection_rows)
            .map(|_| rng.uniform(Q))
            .collect();
        let mut expected = -(equation.constant.0[0] as i128);
        for (&weight, &p) in weights.iter().zip(projection) {
            expected = (expected + weight as i128 * p as i128).rem_euclid(Q as i128);
        }
        expected_constants.push(residue(expected));
        omega.push(weights);
        equations.push(equation);
    }
    let mut pi = Xof::new(pi_seed, b"ordinary/JL/entries");
    for (row, _) in projection.iter().enumerate() {
        for block in 0..relation.r {
            for position in 0..relation.n {
                let coefficients: Vec<i64> = (0..D).map(|_| pi.ternary()).collect();
                let coefficient = Poly::from_signed(&coefficients)?.conjugate();
                for k in 0..count {
                    let value = &mut equations[k].linear[block][position];
                    *value = value.add(&coefficient.scale(omega[k][row]));
                }
            }
        }
    }
    Ok((equations, expected_constants))
}

fn ring_aggregation(
    relation: &Relation,
    layout: &Layout,
    scalar: &[DenseEquation],
    aggregates: &[Poly],
    constants: &[u64],
    transcript: &mut Transcript,
) -> Result<DenseEquation> {
    if aggregates.len() != scalar.len() {
        return Err("incorrect scalar aggregate count".into());
    }
    for (aggregate, &expected) in aggregates.iter().zip(constants) {
        aggregate.validate()?;
        if aggregate.0[0] != expected {
            return Err("incorrect scalar aggregate constant term".into());
        }
    }
    transcript.absorb_json(b"ordinary/b-double-prime", &aggregates)?;
    let mut rng = transcript.challenge(b"ordinary/alpha-beta");
    let mut equation = DenseEquation::zero(relation, layout);
    for full in &relation.full {
        equation.add_ring_constraint(full, &rng.poly(), relation.r);
    }
    for (original, aggregate) in scalar.iter().zip(aggregates) {
        let mut extension = original.clone();
        extension.constant = Poly::zero().sub(aggregate);
        equation.add_dense(&extension, &rng.poly());
    }
    Ok(equation)
}

fn fold_challenges(u2: &[Poly], r: usize, transcript: &mut Transcript) -> Result<Vec<Poly>> {
    transcript.absorb_json(b"ordinary/u2", &u2)?;
    let mut rng = transcript.challenge(b"ordinary/final-c");
    Ok((0..r).map(|_| rng.challenge_poly()).collect())
}

fn radix_digits(poly: &Poly) -> Result<Vec<Poly>> {
    let mut coefficients = vec![vec![0i64; D]; DIGITS];
    for (index, &coefficient) in poly.0.iter().enumerate() {
        let mut value = centered(coefficient);
        for digit in coefficients.iter_mut().take(DIGITS - 1) {
            let low = (value + 8).rem_euclid(16) - 8;
            digit[index] = low;
            value = (value - low) / 16;
        }
        if value.abs() > 8 {
            return Err("full-q radix decomposition exceeded eight digits".into());
        }
        coefficients[DIGITS - 1][index] = value;
    }
    coefficients.iter().map(|c| Poly::from_signed(c)).collect()
}

fn z_digits(poly: &Poly) -> Result<(Poly, Poly)> {
    let mut low = Vec::with_capacity(D);
    let mut high = Vec::with_capacity(D);
    for index in 0..D {
        let value = poly.coefficient(index);
        let digit = (value + 8).rem_euclid(16) - 8;
        low.push(digit);
        high.push((value - digit) / 16);
    }
    Ok((Poly::from_signed(&low)?, Poly::from_signed(&high)?))
}

fn z_slot(layout: &Layout, part: usize, index: usize) -> (usize, usize) {
    (part * 2 + index / layout.z_stride, index % layout.z_stride)
}
fn v_slot(layout: &Layout, index: usize) -> (usize, usize) {
    (4 + index / layout.v_stride, index % layout.v_stride)
}
fn empty_constraint() -> Constraint {
    Constraint {
        quadratic: Vec::new(),
        linear: Vec::new(),
        constant: Poly::zero(),
    }
}
fn linear_at(eq: &mut Constraint, slot: (usize, usize), coefficient: Poly) {
    if !is_zero(&coefficient) {
        eq.linear.push(LinearTerm {
            block: slot.0,
            position: slot.1,
            coefficient,
        });
    }
}
fn add_z(eq: &mut Constraint, layout: &Layout, position: usize, coefficient: &Poly) {
    linear_at(eq, z_slot(layout, 0, position), coefficient.clone());
    linear_at(eq, z_slot(layout, 1, position), coefficient.scale(BASE));
}
fn add_v_digits(
    eq: &mut Constraint,
    layout: &Layout,
    start: usize,
    stride: usize,
    coefficient: &Poly,
) {
    let mut power = 1u64;
    for digit in 0..DIGITS {
        linear_at(
            eq,
            v_slot(layout, start + digit * stride),
            coefficient.scale(power),
        );
        power = (power * BASE) % Q;
    }
}

// Keep public statement/setup inputs explicit and separate from the derived
// layout, aggregate, and challenges used by both prover and verifier.
#[allow(clippy::too_many_arguments)]
fn build_target(
    relation: &Relation,
    layout: &Layout,
    message: &RoundMessage,
    aggregated: &DenseEquation,
    challenges: &[Poly],
    seed: &[u8; 32],
    round: usize,
    config: &CoreConfig,
) -> Result<Relation> {
    let mut full = Vec::new();
    // A z = sum_i c_i t_i. A's columns refer to the original n positions.
    for row in 0..config.inner_rank {
        let mut equation = empty_constraint();
        let coefficients = matrix_row(seed, &domain(round, "inner"), row, relation.n);
        for (position, coefficient) in coefficients.iter().enumerate() {
            add_z(&mut equation, layout, position, coefficient);
        }
        for (i, challenge) in challenges.iter().enumerate() {
            add_v_digits(
                &mut equation,
                layout,
                i * DIGITS * config.inner_rank + row,
                config.inner_rank,
                &Poly::zero().sub(challenge),
            );
        }
        full.push(equation);
    }
    // ||z|| here means the ring bilinear dot product, not the coefficient norm.
    let mut gram = empty_constraint();
    for chunk in 0..2 {
        gram.quadratic.push(QuadraticTerm {
            left: chunk,
            right: chunk,
            coefficient: Poly::constant(1),
        });
        gram.quadratic.push(QuadraticTerm {
            left: chunk,
            right: chunk + 2,
            coefficient: Poly::constant(32),
        });
        gram.quadratic.push(QuadraticTerm {
            left: chunk + 2,
            right: chunk + 2,
            coefficient: Poly::constant(256),
        });
    }
    let mut linear_fold = empty_constraint();
    for position in 0..relation.n {
        let mut coefficient = Poly::zero();
        for (challenge, linear) in challenges.iter().zip(&aggregated.linear) {
            coefficient = coefficient.add(&challenge.mul(&linear[position]));
        }
        add_z(&mut linear_fold, layout, position, &coefficient);
    }
    let mut consistency = empty_constraint();
    consistency.constant = aggregated.constant.clone();
    for (index, &(i, j)) in layout.pairs.iter().enumerate() {
        let folded = challenges[i]
            .mul(&challenges[j])
            .scale(if i == j { 1 } else { 2 });
        add_v_digits(
            &mut gram,
            layout,
            layout.t_count + index * DIGITS,
            1,
            &Poly::zero().sub(&folded),
        );
        add_v_digits(
            &mut linear_fold,
            layout,
            layout.t_count + layout.g_count + index * DIGITS,
            1,
            &Poly::zero().sub(&folded),
        );
        add_v_digits(
            &mut consistency,
            layout,
            layout.t_count + index * DIGITS,
            1,
            &aggregated.quadratic[index],
        );
        if i == j {
            add_v_digits(
                &mut consistency,
                layout,
                layout.t_count + layout.g_count + index * DIGITS,
                1,
                &Poly::constant(1),
            );
        }
    }
    full.extend([gram, linear_fold, consistency]);
    for row in 0..config.outer_rank {
        let mut equation = empty_constraint();
        equation.constant = Poly::zero().sub(&message.u1[row]);
        let coefficients = matrix_row(
            seed,
            &domain(round, "outer-u1"),
            row,
            layout.t_count + layout.g_count,
        );
        for (index, coefficient) in coefficients.into_iter().enumerate() {
            linear_at(&mut equation, v_slot(layout, index), coefficient);
        }
        full.push(equation);
    }
    for row in 0..config.outer_rank {
        let mut equation = empty_constraint();
        equation.constant = Poly::zero().sub(&message.u2[row]);
        let coefficients = matrix_row(seed, &domain(round, "outer-u2"), row, layout.g_count);
        for (index, coefficient) in coefficients.into_iter().enumerate() {
            linear_at(
                &mut equation,
                v_slot(layout, layout.t_count + layout.g_count + index),
                coefficient,
            );
        }
        full.push(equation);
    }
    // Required pins: otherwise whole-block quadratic terms would include
    // unassigned z-padding coordinates. These are extra full equations.
    let mut assigned = vec![vec![false; layout.target_n]; 8];
    for part in 0..2 {
        for index in 0..relation.n {
            let (block, position) = z_slot(layout, part, index);
            assigned[block][position] = true;
        }
    }
    for index in 0..layout.m {
        let (block, position) = v_slot(layout, index);
        assigned[block][position] = true;
    }
    for (block, mask) in assigned.iter().enumerate() {
        for (position, &used) in mask.iter().enumerate() {
            if !used {
                let mut pin = empty_constraint();
                linear_at(&mut pin, (block, position), Poly::constant(1));
                full.push(pin);
            }
        }
    }
    let target = Relation {
        r: 8,
        n: layout.target_n,
        bound_squared: layout.bound_squared,
        full,
        scalar: Vec::new(),
    };
    target.validate()?;
    Ok(target)
}

pub fn prove_round(
    relation: &Relation,
    witness: &Witness,
    seed: &[u8; 32],
    round: usize,
    config: &CoreConfig,
    transcript: &mut Transcript,
) -> Result<(RoundMessage, Reduction)> {
    let layout = layout(relation, config)?;
    relation.check(witness)?;
    context(relation, seed, round, config, transcript)?;
    let inner: Vec<Vec<Poly>> = witness
        .iter()
        .map(|block| commit(seed, &domain(round, "inner"), config.inner_rank, block))
        .collect();
    let gram: Vec<Poly> = layout
        .pairs
        .iter()
        .map(|&(i, j)| dot(&witness[i], &witness[j]))
        .collect();
    let mut v = Vec::with_capacity(layout.m);
    for row in &inner {
        let digits: Vec<Vec<Poly>> = row.iter().map(radix_digits).collect::<Result<_>>()?;
        for digit in 0..DIGITS {
            for item in &digits {
                v.push(item[digit].clone());
            }
        }
    }
    for entry in &gram {
        v.extend(radix_digits(entry)?);
    }
    let u1 = commit(seed, &domain(round, "outer-u1"), config.outer_rank, &v);
    let pi_seed = projection_seed(&u1, transcript)?;
    let projection = project(witness, &pi_seed, config.projection_rows);
    let (scalar, constants) =
        scalar_aggregations(relation, &layout, &projection, &pi_seed, config, transcript)?;
    let aggregates: Vec<Poly> = scalar
        .iter()
        .map(|eq| eq.evaluate_without_constant(witness, &gram))
        .collect();
    let aggregated = ring_aggregation(
        relation,
        &layout,
        &scalar,
        &aggregates,
        &constants,
        transcript,
    )?;
    let mut h_digits = Vec::with_capacity(layout.g_count);
    for &(i, j) in &layout.pairs {
        let h = dot(&aggregated.linear[i], &witness[j])
            .add(&dot(&aggregated.linear[j], &witness[i]))
            .scale(Q.div_ceil(2));
        h_digits.extend(radix_digits(&h)?);
    }
    let u2 = commit(
        seed,
        &domain(round, "outer-u2"),
        config.outer_rank,
        &h_digits,
    );
    v.extend(h_digits);
    let challenges = fold_challenges(&u2, relation.r, transcript)?;
    let message = RoundMessage {
        u1,
        projection,
        aggregates,
        u2,
    };
    let target = build_target(
        relation,
        &layout,
        &message,
        &aggregated,
        &challenges,
        seed,
        round,
        config,
    )?;
    let mut output = vec![vec![Poly::zero(); layout.target_n]; 8];
    // The validated first block supplies the common column index; each column
    // is folded across all blocks in its original order.
    for (position, _) in witness[0].iter().enumerate() {
        let mut z = Poly::zero();
        for (challenge, block) in challenges.iter().zip(witness) {
            z = z.add(&challenge.mul(&block[position]));
        }
        let (low, high) = z_digits(&z)?;
        let a = z_slot(&layout, 0, position);
        let b = z_slot(&layout, 1, position);
        output[a.0][a.1] = low;
        output[b.0][b.1] = high;
    }
    for (index, polynomial) in v.into_iter().enumerate() {
        let slot = v_slot(&layout, index);
        output[slot.0][slot.1] = polynomial;
    }
    target.check(&output)?;
    Ok((
        message,
        Reduction {
            relation: target,
            witness: output,
        },
    ))
}

pub fn verify_round(
    relation: &Relation,
    message: &RoundMessage,
    seed: &[u8; 32],
    round: usize,
    config: &CoreConfig,
    transcript: &mut Transcript,
) -> Result<Relation> {
    let layout = layout(relation, config)?;
    if message.u1.len() != config.outer_rank || message.u2.len() != config.outer_rank {
        return Err("incorrect outer commitment dimension".into());
    }
    if message.aggregates.len() != config.aggregation_repetitions {
        return Err("incorrect aggregate count".into());
    }
    for polynomial in message
        .u1
        .iter()
        .chain(&message.u2)
        .chain(&message.aggregates)
    {
        polynomial.validate()?;
    }
    context(relation, seed, round, config, transcript)?;
    let pi_seed = projection_seed(&message.u1, transcript)?;
    let (scalar, constants) = scalar_aggregations(
        relation,
        &layout,
        &message.projection,
        &pi_seed,
        config,
        transcript,
    )?;
    let aggregated = ring_aggregation(
        relation,
        &layout,
        &scalar,
        &message.aggregates,
        &constants,
        transcript,
    )?;
    let challenges = fold_challenges(&message.u2, relation.r, transcript)?;
    build_target(
        relation,
        &layout,
        message,
        &aggregated,
        &challenges,
        seed,
        round,
        config,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn config() -> CoreConfig {
        CoreConfig {
            inner_rank: 2,
            outer_rank: 2,
            projection_rows: 1024,
            aggregation_repetitions: 6,
        }
    }

    fn example() -> (Relation, Witness) {
        let witness = vec![
            vec![
                Poly::from_signed(&[1, 1]).unwrap(),
                Poly::constant(2),
                Poly::constant(-1),
            ],
            vec![
                Poly::from_signed(&[0, 1]).unwrap(),
                Poly::constant(1),
                Poly::constant(2),
            ],
        ];
        let mut full = empty_constraint();
        // Deliberately reversed off-diagonal indices: each term is counted once.
        full.quadratic.push(QuadraticTerm {
            left: 1,
            right: 0,
            coefficient: Poly::constant(3),
        });
        full.linear.push(LinearTerm {
            block: 0,
            position: 2,
            coefficient: Poly::from_signed(&[1, -2]).unwrap(),
        });
        full.constant = Poly::zero().sub(&full.evaluate(&witness).unwrap());
        let mut scalar = empty_constraint();
        scalar.quadratic.push(QuadraticTerm {
            left: 0,
            right: 0,
            coefficient: Poly::constant(2),
        });
        scalar.linear.push(LinearTerm {
            block: 1,
            position: 0,
            coefficient: Poly::from_signed(&[4, 2]).unwrap(),
        });
        scalar.constant = Poly::constant(-scalar.evaluate(&witness).unwrap().coefficient(0));
        // Higher coefficients of a scalar equation must remain unconstrained.
        scalar.constant.0[7] = 9;
        let relation = Relation {
            r: 2,
            n: 3,
            bound_squared: 32,
            full: vec![full],
            scalar: vec![scalar],
        };
        relation.check(&witness).unwrap();
        assert!(!is_zero(&relation.scalar[0].evaluate(&witness).unwrap()));
        (relation, witness)
    }

    #[test]
    fn balanced_radix_reconstructs_centered_boundary_values() {
        for value in [
            -(Q as i64 / 2),
            -129,
            -128,
            -9,
            -8,
            -1,
            0,
            7,
            8,
            127,
            128,
            Q as i64 / 2,
        ] {
            let poly = Poly::constant(value);
            let digits = radix_digits(&poly).unwrap();
            let mut rebuilt = Poly::zero();
            let mut power = 1;
            for digit in digits {
                assert!(digit.0.iter().all(|&c| centered(c).abs() <= 8));
                rebuilt = rebuilt.add(&digit.scale(power));
                power = power * BASE % Q;
            }
            assert_eq!(rebuilt, poly);
            let (low, high) = z_digits(&poly).unwrap();
            assert_eq!(low.add(&high.scale(BASE)), poly);
            assert!(low.coefficient(0).abs() <= 8);
        }
    }

    #[test]
    fn honest_round_public_reconstruction_padding_and_message_checks() {
        let (relation, witness) = example();
        let seed = [17; 32];
        let config = config();
        let (message, reduction) = prove_round(
            &relation,
            &witness,
            &seed,
            0,
            &config,
            &mut Transcript::new(b"ordinary/test"),
        )
        .unwrap();
        let public = verify_round(
            &relation,
            &message,
            &seed,
            0,
            &config,
            &mut Transcript::new(b"ordinary/test"),
        )
        .unwrap();
        assert_eq!(public, reduction.relation);
        public.check(&reduction.witness).unwrap();
        assert_eq!(
            target_shape_and_bound(&relation, &config).unwrap(),
            (public.r, public.n, public.bound_squared)
        );
        let layout = layout(&relation, &config).unwrap();
        let pins = 8 * public.n - (2 * relation.n + layout.m);
        assert_eq!(
            public.full.len(),
            config.inner_rank + 2 * config.outer_rank + 3 + pins
        );
        assert!(pins > 0);
        // A trailing z slot is outside every assigned chunk. Its explicit pin
        // must reject even though the honest norm cap has ample slack.
        let mut padded = reduction.witness.clone();
        padded[0][public.n - 1] = Poly::constant(1);
        assert!(public.check(&padded).is_err());
        assert!(public.full.iter().any(|eq| eq.quadratic.is_empty()
            && eq.linear.len() == 1
            && eq.linear[0].block == 0
            && eq.linear[0].position == public.n - 1
            && eq.linear[0].coefficient == Poly::constant(1)
            && is_zero(&eq.constant)));

        let mut modified = message.clone();
        modified.aggregates[0].0[0] = (modified.aggregates[0].0[0] + 1) % Q;
        assert!(verify_round(
            &relation,
            &modified,
            &seed,
            0,
            &config,
            &mut Transcript::new(b"ordinary/test")
        )
        .unwrap_err()
        .contains("constant term"));
        let mut modified = message.clone();
        modified.projection[0] = Q as i64;
        assert!(verify_round(
            &relation,
            &modified,
            &seed,
            0,
            &config,
            &mut Transcript::new(b"ordinary/test")
        )
        .is_err());
        let mut modified = message;
        modified.u2[0].0[0] = (modified.u2[0].0[0] + 1) % Q;
        let altered_target = verify_round(
            &relation,
            &modified,
            &seed,
            0,
            &config,
            &mut Transcript::new(b"ordinary/test"),
        )
        .unwrap();
        assert!(altered_target.check(&reduction.witness).is_err());
    }

    #[test]
    fn rejects_invalid_profile_before_sampling() {
        let (mut relation, _) = example();
        let mut cfg = config();
        cfg.projection_rows = 128;
        assert!(target_shape_and_bound(&relation, &cfg).is_err());
        cfg = config();
        cfg.aggregation_repetitions = 5;
        assert!(target_shape_and_bound(&relation, &cfg).is_err());
        relation.bound_squared = 5 * Q as u128 * Q as u128 / (23 * 250 * 250) + 1;
        assert!(target_shape_and_bound(&relation, &config())
            .unwrap_err()
            .contains("250"));
    }

    #[test]
    fn planning_rejects_large_shapes_without_materializing_pairs() {
        let relation = Relation {
            r: MAX_WITNESS_POLYS,
            n: 1,
            bound_squared: 0,
            full: Vec::new(),
            scalar: Vec::new(),
        };
        assert!(target_shape_and_bound(&relation, &config())
            .unwrap_err()
            .contains("target witness"));
        let (relation, _) = example();
        let mut cfg = config();
        cfg.aggregation_repetitions = usize::MAX;
        assert!(target_shape_and_bound(&relation, &cfg).is_err());
        cfg = config();
        cfg.outer_rank = usize::MAX;
        assert!(target_shape_and_bound(&relation, &cfg).is_err());
    }

    #[test]
    fn recursive_output_is_an_actual_second_round_input() {
        let (mut relation, mut witness) = example();
        let seed = [29; 32];
        let cfg = config();
        let mut prover_transcript = Transcript::new(b"ordinary/two-rounds");
        let mut verifier_transcript = Transcript::new(b"ordinary/two-rounds");
        for round in 0..2 {
            let (message, output) = prove_round(
                &relation,
                &witness,
                &seed,
                round,
                &cfg,
                &mut prover_transcript,
            )
            .unwrap();
            let rebuilt = verify_round(
                &relation,
                &message,
                &seed,
                round,
                &cfg,
                &mut verifier_transcript,
            )
            .unwrap();
            assert_eq!(rebuilt, output.relation);
            rebuilt.check(&output.witness).unwrap();
            relation = output.relation;
            witness = output.witness;
        }
    }
}
