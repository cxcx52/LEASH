//! Sparse binary circuits and the complete native source-to-ring reduction.
//!
//! Fixed Q/D, public pins, explicit padding and conjugation are part of the
//! relation. Seed-expanded setup and transcript challenges are experimental;
//! this crate makes no Fiat--Shamir, zero-knowledge, or security-level claim.

use leash_core::{
    commit, matrix_row, Constraint, LinearTerm, Poly, QuadraticTerm, Relation, Result, Transcript,
    Witness, D, Q,
};
use serde::{Deserialize, Serialize};

pub type Wire = usize;
pub const MAX_VARIABLES: usize = 4096;
pub const MAX_GATES: usize = 4096;
pub const MAX_NONZEROS: usize = 65536;
pub const MAX_JSON_BYTES: usize = 4 * 1024 * 1024;
pub const SOURCE_MATRIX_DOMAIN: &[u8] = b"leash/native-source/commitment/v1";

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PublicPin {
    pub wire: Wire,
    pub value: bool,
}

/// A row lists precisely the columns with coefficient one, in increasing order.
/// Variable zero is the constant wire and is included in `variables`.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BinaryR1cs {
    pub variables: usize,
    pub a: Vec<Vec<Wire>>,
    pub b: Vec<Vec<Wire>>,
    pub c: Vec<Vec<Wire>>,
    pub public_pins: Vec<PublicPin>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Assignment {
    pub values: Vec<bool>,
}

fn decode_json<T: for<'de> Deserialize<'de>>(data: &[u8]) -> Result<T> {
    if data.len() > MAX_JSON_BYTES {
        return Err("frontend JSON exceeds byte limit".into());
    }
    serde_json::from_slice(data).map_err(|e| format!("invalid frontend JSON: {e}"))
}

fn parity(row: &[Wire], assignment: &[bool]) -> bool {
    row.iter().fold(false, |acc, &i| acc ^ assignment[i])
}

impl BinaryR1cs {
    pub fn validate(&self) -> Result<()> {
        if self.variables == 0 || self.variables > MAX_VARIABLES {
            return Err("variable count is outside frontend limits".into());
        }
        if self.a.len() > MAX_GATES || self.a.len() != self.b.len() || self.a.len() != self.c.len()
        {
            return Err("R1CS matrices have invalid or unequal row counts".into());
        }
        let mut nnz = 0usize;
        for row in self.a.iter().chain(&self.b).chain(&self.c) {
            nnz = nnz.checked_add(row.len()).ok_or("nonzero count overflow")?;
            if nnz > MAX_NONZEROS
                || row.iter().any(|&i| i >= self.variables)
                || row.windows(2).any(|p| p[0] >= p[1])
            {
                return Err(
                    "sparse rows must have bounded, distinct, increasing valid indices".into(),
                );
            }
        }
        if self.public_pins.len() > self.variables
            || self.public_pins.iter().any(|p| p.wire >= self.variables)
            || self.public_pins.windows(2).any(|p| p[0].wire >= p[1].wire)
        {
            return Err("public pins must be distinct, increasing valid coordinates".into());
        }
        Ok(())
    }
    pub fn check_assignment(&self, values: &[bool]) -> Result<()> {
        self.validate()?;
        if values.len() != self.variables || !values.first().copied().unwrap_or(false) {
            return Err("assignment must have the stated length and constant wire one".into());
        }
        if self.public_pins.iter().any(|p| values[p.wire] != p.value) {
            return Err("assignment does not match public inputs".into());
        }
        for i in 0..self.a.len() {
            if (parity(&self.a[i], values) & parity(&self.b[i], values))
                != parity(&self.c[i], values)
            {
                return Err(format!("assignment violates binary gate {i}"));
            }
        }
        Ok(())
    }
    pub fn from_json(data: &[u8]) -> Result<Self> {
        let value: Self = decode_json(data)?;
        value.validate()?;
        Ok(value)
    }
    pub fn to_json(&self) -> Result<Vec<u8>> {
        self.validate()?;
        serde_json::to_vec(self).map_err(|e| e.to_string())
    }
}

impl Assignment {
    pub fn from_json(data: &[u8]) -> Result<Self> {
        let value: Self = decode_json(data)?;
        if value.values.is_empty() || value.values.len() > MAX_VARIABLES {
            return Err("assignment size is outside frontend limits".into());
        }
        Ok(value)
    }
    pub fn to_json(&self) -> Result<Vec<u8>> {
        if self.values.is_empty() || self.values.len() > MAX_VARIABLES {
            return Err("assignment size is outside frontend limits".into());
        }
        serde_json::to_vec(self).map_err(|e| e.to_string())
    }
}

/// A small honest-assignment builder. Public constraints are retained separately.
#[derive(Clone, Debug)]
pub struct CircuitBuilder {
    instance: BinaryR1cs,
    values: Vec<bool>,
}
impl Default for CircuitBuilder {
    fn default() -> Self {
        Self::new()
    }
}
impl CircuitBuilder {
    pub fn new() -> Self {
        Self {
            instance: BinaryR1cs {
                variables: 1,
                a: vec![],
                b: vec![],
                c: vec![],
                public_pins: vec![],
            },
            values: vec![true],
        }
    }
    pub fn input(&mut self, value: bool) -> Result<Wire> {
        if self.values.len() >= MAX_VARIABLES {
            return Err("variable limit reached".into());
        }
        let wire = self.values.len();
        self.values.push(value);
        self.instance.variables += 1;
        Ok(wire)
    }
    pub fn public_input(&mut self, value: bool) -> Result<Wire> {
        let wire = self.input(value)?;
        self.pin_public(wire, value)?;
        Ok(wire)
    }
    fn value(&self, wire: Wire) -> Result<bool> {
        self.values
            .get(wire)
            .copied()
            .ok_or_else(|| "unknown circuit wire".into())
    }
    fn output(&mut self, a: Vec<Wire>, b: Vec<Wire>, value: bool) -> Result<Wire> {
        if self.instance.a.len() >= MAX_GATES {
            return Err("gate limit reached".into());
        }
        let wire = self.input(value)?;
        self.instance.a.push(a);
        self.instance.b.push(b);
        self.instance.c.push(vec![wire]);
        Ok(wire)
    }
    pub fn and(&mut self, left: Wire, right: Wire) -> Result<Wire> {
        let value = self.value(left)? & self.value(right)?;
        self.output(vec![left], vec![right], value)
    }
    pub fn xor(&mut self, left: Wire, right: Wire) -> Result<Wire> {
        let value = self.value(left)? ^ self.value(right)?;
        self.output(xor_pair(left, right), vec![0], value)
    }
    pub fn not(&mut self, input: Wire) -> Result<Wire> {
        let value = !self.value(input)?;
        self.output(xor_pair(0, input), vec![0], value)
    }
    pub fn assert_equal(&mut self, left: Wire, right: Wire) -> Result<()> {
        self.value(left)?;
        self.value(right)?;
        if self.instance.a.len() >= MAX_GATES {
            return Err("gate limit reached".into());
        }
        self.instance.a.push(xor_pair(left, right));
        self.instance.b.push(vec![0]);
        self.instance.c.push(vec![]);
        Ok(())
    }
    pub fn pin_public(&mut self, wire: Wire, value: bool) -> Result<()> {
        self.value(wire)?;
        match self
            .instance
            .public_pins
            .binary_search_by_key(&wire, |p| p.wire)
        {
            Ok(i) if self.instance.public_pins[i].value == value => Ok(()),
            Ok(_) => Err("conflicting public pin".into()),
            Err(i) => {
                self.instance
                    .public_pins
                    .insert(i, PublicPin { wire, value });
                Ok(())
            }
        }
    }
    pub fn finish(self) -> Result<(BinaryR1cs, Assignment)> {
        self.instance.check_assignment(&self.values)?;
        Ok((
            self.instance,
            Assignment {
                values: self.values,
            },
        ))
    }
}
fn xor_pair(a: Wire, b: Wire) -> Vec<Wire> {
    match a.cmp(&b) {
        std::cmp::Ordering::Equal => vec![],
        std::cmp::Ordering::Less => vec![a, b],
        std::cmp::Ordering::Greater => vec![b, a],
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SourceConfig {
    pub rank: usize,
    pub challenge_rows: usize,
    pub chunks: usize,
}
impl Default for SourceConfig {
    fn default() -> Self {
        Self {
            rank: 6,
            challenge_rows: 160,
            chunks: 1,
        }
    }
}
impl SourceConfig {
    pub fn validate(&self) -> Result<()> {
        if self.rank == 0
            || self.rank > 32
            || self.challenge_rows == 0
            || self.challenge_rows > 256
            || self.chunks == 0
            || self.chunks > 64
        {
            return Err("source configuration exceeds resource limits".into());
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SourceMessage {
    pub commitment: Vec<Poly>,
    pub replies: Vec<i64>,
}

#[derive(Clone, Debug)]
struct Layout {
    np: usize,
    kp: usize,
    original: [usize; 4],
    real: [usize; 4],
    width: usize,
    rings: usize,
    bound: u128,
}
impl Layout {
    fn new(instance: &BinaryR1cs, config: &SourceConfig) -> Result<Self> {
        instance.validate()?;
        config.validate()?;
        let np = instance
            .variables
            .checked_add(D - 1)
            .ok_or("padding overflow")?
            / D
            * D;
        // An empty circuit is represented by D zero gate rows, explicitly pinned.
        let kp = instance
            .a
            .len()
            .max(1)
            .checked_add(D - 1)
            .ok_or("padding overflow")?
            / D
            * D;
        let largest = np.max(kp) / D;
        let width = largest
            .checked_add(config.chunks - 1)
            .ok_or("layout overflow")?
            / config.chunks;
        let rings = width.checked_mul(config.chunks).ok_or("layout overflow")?;
        let total = np
            .checked_add(kp.checked_mul(3).ok_or("dimension overflow")?)
            .ok_or("dimension overflow")?;
        let bound = 2 * (total as u128);
        if 23 * bound >= 5 * (Q as u128)
            || 6 * (kp as u128) >= Q as u128
            || total as u128 >= Q as u128
        {
            return Err("source lifting/slack conditions fail".into());
        }
        Ok(Self {
            np,
            kp,
            original: [kp / D, kp / D, kp / D, np / D],
            real: [
                instance.a.len(),
                instance.a.len(),
                instance.a.len(),
                instance.variables,
            ],
            width,
            rings,
            bound,
        })
    }
    fn slot(&self, group: usize, ring: usize, chunks: usize) -> (usize, usize) {
        (group * chunks + ring / self.width, ring % self.width)
    }
}

/// Return (block count, polynomials per block, squared honest norm bound)
/// without expanding setup matrices or constructing target constraints.
/// The bound is closed: target membership requires norm squared <= this value.
pub fn source_shape_and_bound(
    instance: &BinaryR1cs,
    config: &SourceConfig,
) -> Result<(usize, usize, u128)> {
    let layout = Layout::new(instance, config)?;
    Ok((8 * config.chunks, layout.width, layout.bound))
}

#[derive(Clone)]
struct Row {
    a: Vec<bool>,
    b: Vec<bool>,
    c: Vec<bool>,
    delta: Vec<bool>,
}
fn bind_statement(
    instance: &BinaryR1cs,
    seed: &[u8; 32],
    config: &SourceConfig,
    tr: &mut Transcript,
) -> Result<()> {
    tr.absorb(b"source.version", b"native-coefficient-v1");
    tr.absorb_json(b"source.instance", instance)?;
    tr.absorb_json(b"source.config", config)?;
    tr.absorb(b"source.setup-seed", seed);
    Ok(())
}
fn challenge_rows(
    instance: &BinaryR1cs,
    config: &SourceConfig,
    layout: &Layout,
    commitment: &[Poly],
    tr: &mut Transcript,
) -> Result<Vec<Row>> {
    tr.absorb_json(b"source.commitment", &commitment)?;
    let mut rng = tr.challenge(b"source.binary-rows");
    let mut rows = Vec::with_capacity(config.challenge_rows);
    for _ in 0..config.challenge_rows {
        let a: Vec<bool> = (0..layout.kp).map(|_| rng.bit()).collect();
        let b: Vec<bool> = (0..layout.kp).map(|_| rng.bit()).collect();
        let c: Vec<bool> = (0..layout.kp).map(|_| rng.bit()).collect();
        let mut delta = vec![false; layout.np];
        for (matrix, weights) in [(&instance.a, &a), (&instance.b, &b), (&instance.c, &c)] {
            for (indices, active) in matrix.iter().zip(weights) {
                if *active {
                    for &column in indices {
                        delta[column] ^= true;
                    }
                }
            }
        }
        rows.push(Row { a, b, c, delta });
    }
    Ok(rows)
}

fn empty_constraint() -> Constraint {
    Constraint {
        quadratic: vec![],
        linear: vec![],
        constant: Poly::zero(),
    }
}
fn selector(index: usize) -> Poly {
    let mut p = Poly::zero();
    if index == 0 {
        p.0[0] = 1;
    } else {
        p.0[D - index] = Q - 1;
    }
    p
}
fn term(
    layout: &Layout,
    chunks: usize,
    group: usize,
    ring: usize,
    coefficient: Poly,
) -> LinearTerm {
    let (block, position) = layout.slot(group, ring, chunks);
    LinearTerm {
        block,
        position,
        coefficient,
    }
}
fn scalar_pin(
    layout: &Layout,
    config: &SourceConfig,
    group: usize,
    coefficient_index: usize,
    value: bool,
) -> Constraint {
    Constraint {
        quadratic: vec![],
        linear: vec![term(
            layout,
            config.chunks,
            group,
            coefficient_index / D,
            selector(coefficient_index % D),
        )],
        constant: Poly::constant(-i64::from(value)),
    }
}
fn packed_bits(bits: &[bool]) -> Vec<Poly> {
    bits.chunks_exact(D)
        .map(|chunk| Poly(chunk.iter().map(|&b| u64::from(b)).collect()))
        .collect()
}

fn compile(
    instance: &BinaryR1cs,
    message: &SourceMessage,
    seed: &[u8; 32],
    config: &SourceConfig,
    layout: &Layout,
    rows: &[Row],
) -> Result<Relation> {
    if message.commitment.len() != config.rank
        || message.replies.len() != config.challenge_rows
        || rows.len() != config.challenge_rows
    {
        return Err("source message shape does not match public configuration".into());
    }
    for p in &message.commitment {
        p.validate()?;
    }
    if message
        .replies
        .iter()
        .any(|&g| g < -(layout.np as i64) || g > 3 * layout.kp as i64 || g % 2 != 0)
    {
        return Err("source replies must be even integers in the specified interval".into());
    }
    let mut relation = Relation {
        r: 8 * config.chunks,
        n: layout.width,
        bound_squared: layout.bound,
        full: vec![],
        scalar: vec![],
    };
    let columns: usize = layout.original.iter().sum();
    for (row_index, commitment) in message.commitment.iter().enumerate() {
        let coefficients = matrix_row(seed, SOURCE_MATRIX_DOMAIN, row_index, columns);
        let mut equation = empty_constraint();
        equation.constant = Poly::zero().sub(commitment);
        let mut column = 0;
        for group in 0..4 {
            for ring in 0..layout.original[group] {
                equation.linear.push(term(
                    layout,
                    config.chunks,
                    group,
                    ring,
                    coefficients[column].clone(),
                ));
                column += 1;
            }
        }
        relation.full.push(equation);
    }
    // Coordinate conjugation is F_q-linear, never silently R_q-linear.
    for group in 0..4 {
        for ring in 0..layout.original[group] {
            for j in 0..D {
                let mut equation = empty_constraint();
                equation
                    .linear
                    .push(term(layout, config.chunks, group + 4, ring, selector(j)));
                let original_index = if j == 0 { 0 } else { D - j };
                let sign = if j == 0 { Q - 1 } else { 1 };
                equation.linear.push(term(
                    layout,
                    config.chunks,
                    group,
                    ring,
                    selector(original_index).scale(sign),
                ));
                relation.scalar.push(equation);
            }
        }
    }
    // Whole ring padding plus partial coefficient padding, including its signed
    // conjugate location. The high coefficients of a conjugate are NOT simply
    // the padding locations of the original last polynomial.
    for group in 0..4 {
        let real = layout.real[group];
        for ring in 0..layout.rings {
            if ring * D >= real {
                for g in [group, group + 4] {
                    let mut equation = empty_constraint();
                    equation
                        .linear
                        .push(term(layout, config.chunks, g, ring, Poly::constant(1)));
                    relation.full.push(equation);
                }
            } else if real < (ring + 1) * D {
                for j in real % D..D {
                    relation
                        .scalar
                        .push(scalar_pin(layout, config, group, ring * D + j, false));
                    let conjugate_j = if j == 0 { 0 } else { D - j };
                    relation.scalar.push(scalar_pin(
                        layout,
                        config,
                        group + 4,
                        ring * D + conjugate_j,
                        false,
                    ));
                }
            }
        }
    }
    let jbar = Poly(vec![1; D]).conjugate();
    for group in 0..4 {
        let mut equation = empty_constraint();
        for chunk in 0..config.chunks {
            equation.quadratic.push(QuadraticTerm {
                left: group * config.chunks + chunk,
                right: (group + 4) * config.chunks + chunk,
                coefficient: Poly::constant(1),
            });
        }
        for ring in 0..layout.rings {
            equation.linear.push(term(
                layout,
                config.chunks,
                group,
                ring,
                Poly::zero().sub(&jbar),
            ));
        }
        relation.scalar.push(equation);
    }
    let mut product = empty_constraint();
    let signs = [1i64, 1, -2];
    for chunk in 0..config.chunks {
        for left in 0..3 {
            for right in 0..3 {
                product.quadratic.push(QuadraticTerm {
                    left: left * config.chunks + chunk,
                    right: (right + 4) * config.chunks + chunk,
                    coefficient: Poly::constant(signs[left] * signs[right]),
                });
            }
        }
    }
    for (group, sign) in signs.iter().enumerate() {
        for ring in 0..layout.rings {
            product.linear.push(term(
                layout,
                config.chunks,
                group,
                ring,
                jbar.scale(leash_core::residue(-(*sign as i128))),
            ));
        }
    }
    relation.scalar.push(product);
    relation.scalar.push(scalar_pin(layout, config, 3, 0, true));
    for pin in &instance.public_pins {
        relation
            .scalar
            .push(scalar_pin(layout, config, 3, pin.wire, pin.value));
    }
    for (row, &reply) in rows.iter().zip(&message.replies) {
        let mut equation = empty_constraint();
        equation.constant = Poly::constant(-reply);
        for (group, bits) in [&row.a, &row.b, &row.c, &row.delta].iter().enumerate() {
            for (ring, packed) in packed_bits(bits).into_iter().enumerate() {
                let coefficient = packed.conjugate();
                let coefficient = if group == 3 {
                    Poly::zero().sub(&coefficient)
                } else {
                    coefficient
                };
                if coefficient.0.iter().any(|&x| x != 0) {
                    equation
                        .linear
                        .push(term(layout, config.chunks, group, ring, coefficient));
                }
            }
        }
        relation.scalar.push(equation);
    }
    relation.validate()?;
    Ok(relation)
}

/// Produce the full native target witness. The downstream core must prove this
/// exact relation; source replies alone are not a proof or an acceptance result.
pub fn prove_source(
    instance: &BinaryR1cs,
    assignment: &[bool],
    seed: &[u8; 32],
    config: &SourceConfig,
    transcript: &mut Transcript,
) -> Result<(SourceMessage, Relation, Witness)> {
    let layout = Layout::new(instance, config)?;
    instance.check_assignment(assignment)?;
    let mut vectors: Vec<Vec<bool>> = [&instance.a, &instance.b, &instance.c]
        .iter()
        .map(|matrix| {
            let mut v: Vec<bool> = matrix.iter().map(|r| parity(r, assignment)).collect();
            v.resize(layout.kp, false);
            v
        })
        .collect();
    let mut w = assignment.to_vec();
    w.resize(layout.np, false);
    vectors.push(w);
    let originals: Vec<Vec<Poly>> = vectors.iter().map(|v| packed_bits(v)).collect();
    let opening: Vec<Poly> = originals.iter().flatten().cloned().collect();
    let commitment = commit(seed, SOURCE_MATRIX_DOMAIN, config.rank, &opening);
    bind_statement(instance, seed, config, transcript)?;
    let rows = challenge_rows(instance, config, &layout, &commitment, transcript)?;
    let replies = rows
        .iter()
        .map(|row| {
            let count = |a: &[bool], b: &[bool]| -> i64 {
                a.iter().zip(b).filter(|(x, y)| **x && **y).count() as i64
            };
            count(&row.a, &vectors[0]) + count(&row.b, &vectors[1]) + count(&row.c, &vectors[2])
                - count(&row.delta, &vectors[3])
        })
        .collect();
    let message = SourceMessage {
        commitment,
        replies,
    };
    let relation = compile(instance, &message, seed, config, &layout, &rows)?;
    let mut witness = vec![vec![Poly::zero(); layout.width]; 8 * config.chunks];
    for (group, polys) in originals.iter().enumerate() {
        for (ring, poly) in polys.iter().enumerate() {
            let (block, position) = layout.slot(group, ring, config.chunks);
            witness[block][position] = poly.clone();
            let (block, position) = layout.slot(group + 4, ring, config.chunks);
            witness[block][position] = poly.conjugate();
        }
    }
    relation.check(&witness)?;
    transcript.absorb_json(b"source.replies", &message.replies)?;
    Ok((message, relation, witness))
}

/// Rebuild the same public target relation without using an assignment. A caller
/// must verify a downstream proof of this returned relation before accepting.
pub fn verify_source(
    instance: &BinaryR1cs,
    message: &SourceMessage,
    seed: &[u8; 32],
    config: &SourceConfig,
    transcript: &mut Transcript,
) -> Result<Relation> {
    let layout = Layout::new(instance, config)?;
    if message.commitment.len() != config.rank || message.replies.len() != config.challenge_rows {
        return Err("source message shape does not match public configuration".into());
    }
    for poly in &message.commitment {
        poly.validate()?;
    }
    if message
        .replies
        .iter()
        .any(|&g| g < -(layout.np as i64) || g > 3 * layout.kp as i64 || g % 2 != 0)
    {
        return Err("source replies must be even integers in the specified interval".into());
    }
    bind_statement(instance, seed, config, transcript)?;
    let rows = challenge_rows(instance, config, &layout, &message.commitment, transcript)?;
    let relation = compile(instance, message, seed, config, &layout, &rows)?;
    transcript.absorb_json(b"source.replies", &message.replies)?;
    Ok(relation)
}
