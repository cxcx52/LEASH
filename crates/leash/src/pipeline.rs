use crate::ordinary::{self, CoreConfig, RoundMessage};
use leash_core::{Relation, Result, Transcript, Witness, D, Q};
use leash_frontend::{self as front, Assignment, BinaryR1cs, SourceConfig, SourceMessage};
use serde::{Deserialize, Serialize};
use sha3::{Digest, Sha3_256};

pub const VERSION: u32 = 1;
const MAX_CONTEXT_BYTES: usize = 1024 * 1024;
const MAX_PARAMETER_BYTES: usize = 16384;

/// A concrete research profile. Ranks are choices, not security certificates.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Config {
    pub source: SourceConfig,
    pub core: CoreConfig,
    pub rounds: usize,
    pub max_attempts: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            source: SourceConfig::default(),
            core: CoreConfig {
                inner_rank: 24,
                outer_rank: 9,
                projection_rows: 1024,
                aggregation_repetitions: 6,
            },
            rounds: 1,
            max_attempts: 32,
        }
    }
}

impl Config {
    /// Small commitment ranks for integration tests and local demonstrations.
    /// This profile is deliberately not a cryptographic security instantiation.
    pub fn development() -> Self {
        Self {
            source: SourceConfig {
                rank: 2,
                ..SourceConfig::default()
            },
            core: CoreConfig {
                inner_rank: 2,
                outer_rank: 2,
                projection_rows: 1024,
                aggregation_repetitions: 6,
            },
            ..Self::default()
        }
    }
    pub fn validate(&self) -> Result<()> {
        self.source.validate()?;
        if self.source.challenge_rows < 160 || self.source.chunks > 4 {
            return Err(
                "use at least 160 source challenges and at most four chunks per block".into(),
            );
        }
        if !(1..=64).contains(&self.core.inner_rank)
            || !(1..=64).contains(&self.core.outer_rank)
            || self.core.projection_rows != 1024
            || !(6..=8).contains(&self.core.aggregation_repetitions)
            || self.rounds > 3
            || !(1..=128).contains(&self.max_attempts)
        {
            return Err("unsupported ordinary-core configuration or attempt limit".into());
        }
        Ok(())
    }
}

/// Public seed and profile. Setup contains no secret proving key or trapdoor.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PublicParameters {
    pub version: u32,
    pub seed: [u8; 32],
    pub config: Config,
}

impl PublicParameters {
    pub fn validate(&self) -> Result<()> {
        if self.version != VERSION {
            return Err("unsupported parameter version".into());
        }
        self.config.validate()
    }
    pub fn to_json(&self) -> Result<Vec<u8>> {
        self.validate()?;
        serde_json::to_vec_pretty(self).map_err(|e| e.to_string())
    }
    pub fn from_json(bytes: &[u8]) -> Result<Self> {
        if bytes.len() > MAX_PARAMETER_BYTES {
            return Err("parameter file exceeds size limit".into());
        }
        let value: Self = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        value.validate()?;
        Ok(value)
    }
}

pub fn setup(config: Config) -> Result<PublicParameters> {
    config.validate()?;
    let mut seed = [0; 32];
    getrandom::getrandom(&mut seed)
        .map_err(|e| format!("operating-system randomness failed: {e}"))?;
    Ok(PublicParameters {
        version: VERSION,
        seed,
        config,
    })
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProofKind {
    BinaryR1cs,
    QuadraticRelation,
}

/// Proof bytes contain only prover messages and the terminal opening.
/// Verifier challenges and intermediate witnesses are reconstructed locally.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Proof {
    pub version: u32,
    pub kind: ProofKind,
    pub parameter_digest: [u8; 32],
    pub statement_digest: [u8; 32],
    pub context_digest: [u8; 32],
    pub nonce: [u8; 32],
    pub attempt: u32,
    pub source: Option<SourceMessage>,
    pub rounds: Vec<RoundMessage>,
    pub opening: Witness,
}

#[derive(Clone, Debug, Serialize)]
pub struct LayerPlan {
    pub layer: usize,
    pub input_blocks: usize,
    pub input_length: usize,
    pub input_bound_squared: u128,
    pub target_blocks: usize,
    pub target_length: usize,
    pub target_bound_squared: u128,
    pub extracted_target_bound_squared_ceiling: u128,
    pub outer_collision_norm_upper: u128,
    pub inner_collision_norm_upper: u128,
}

#[derive(Clone, Debug, Serialize)]
pub struct ParameterPlan {
    pub input_honest_bound_squared: u128,
    pub interactive_extracted_input_bound_squared_ceiling: u128,
    pub layers: Vec<LayerPlan>,
    pub terminal_blocks: usize,
    pub terminal_length: usize,
    pub terminal_bound_squared: u128,
    pub terminal_opening_u32_bytes: usize,
    pub compiler: &'static str,
    pub security_level: &'static str,
}

#[derive(Clone, Debug, Serialize)]
pub struct VerificationReport {
    pub accepted: bool,
    pub recursive_rounds: usize,
    pub attempt: u32,
    pub proof_bytes: usize,
    pub terminal_polynomials: usize,
    pub input_honest_bound_squared: u128,
    pub interactive_extracted_input_bound_squared_ceiling: u128,
    pub relation_semantics: &'static str,
    pub compiler: &'static str,
    pub zero_knowledge: bool,
    pub security_level: &'static str,
}

fn ceil_sqrt(x: u128) -> u128 {
    if x <= 1 {
        return x;
    }
    let (mut lo, mut hi) = (1u128, 1u128 << 64);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        // Compare mid^2 >= x without overflowing when mid=2^64.
        if mid >= x / mid + u128::from(x % mid != 0) {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    lo
}

fn relaxed_squared(x: u128) -> Result<u128> {
    x.checked_mul(23)
        .and_then(|v| v.checked_add(4))
        .map(|v| v / 5)
        .ok_or_else(|| "relaxed norm overflow".into())
}

fn plan_shape(r: usize, n: usize, bound: u128, config: &Config) -> Result<ParameterPlan> {
    config.validate()?;
    if bound == 0 {
        return Err("positive input norm bound required".into());
    }
    let mut shape = Relation {
        r,
        n,
        bound_squared: bound,
        full: vec![],
        scalar: vec![],
    };
    shape.validate()?;
    let mut layers = Vec::new();
    for index in 0..config.rounds {
        let (r_next, n_next, beta_next) = ordinary::target_shape_and_bound(&shape, &config.core)?;
        let actual = if index + 1 == config.rounds {
            beta_next
        } else {
            relaxed_squared(beta_next)?
        };
        let root_actual = ceil_sqrt(actual);
        let outer = 2 * root_actual;
        let weak = 8 * 128 * 17 * root_actual;
        let strong =
            2 * 17 * root_actual + 4 * 128 * ceil_sqrt(relaxed_squared(shape.bound_squared)?);
        let inner = weak.max(strong);
        // q times a unit vector is always an integer kernel vector. Profiles
        // including it cannot invoke the archived nontrivial MSIS assumptions.
        if outer >= Q as u128 || inner >= Q as u128 {
            return Err(format!("layer {index}: collision radius reaches q; this fixed profile does not support the requested recursion"));
        }
        layers.push(LayerPlan {
            layer: index,
            input_blocks: shape.r,
            input_length: shape.n,
            input_bound_squared: shape.bound_squared,
            target_blocks: r_next,
            target_length: n_next,
            target_bound_squared: beta_next,
            extracted_target_bound_squared_ceiling: actual,
            outer_collision_norm_upper: outer,
            inner_collision_norm_upper: inner,
        });
        shape = Relation {
            r: r_next,
            n: n_next,
            bound_squared: beta_next,
            full: vec![],
            scalar: vec![],
        };
        shape.validate()?;
    }
    let bytes = shape
        .r
        .checked_mul(shape.n)
        .and_then(|v| v.checked_mul(D * 4))
        .ok_or("terminal size overflow")?;
    if bytes > crate::MAX_PROOF_BYTES / 2 {
        return Err("terminal opening exceeds supported transport size".into());
    }
    Ok(ParameterPlan {
        input_honest_bound_squared: bound,
        interactive_extracted_input_bound_squared_ceiling: if config.rounds == 0 {
            bound
        } else {
            relaxed_squared(bound)?
        },
        layers,
        terminal_blocks: shape.r,
        terminal_length: shape.n,
        terminal_bound_squared: shape.bound_squared,
        terminal_opening_u32_bytes: bytes,
        compiler: "experimental SHAKE256 Fiat-Shamir with seed-expanded CRS",
        security_level: "not certified",
    })
}

pub fn plan_binary(instance: &BinaryR1cs, config: &Config) -> Result<ParameterPlan> {
    let (r, n, bound) = front::source_shape_and_bound(instance, &config.source)?;
    plan_shape(r, n, bound, config)
}

pub fn plan_relation(relation: &Relation, config: &Config) -> Result<ParameterPlan> {
    relation.validate()?;
    plan_shape(relation.r, relation.n, relation.bound_squared, config)
}

fn hash_bytes(domain: &[u8], bytes: &[u8]) -> [u8; 32] {
    let mut h = Sha3_256::new();
    h.update(b"LEASH/digest/v1");
    h.update((domain.len() as u64).to_le_bytes());
    h.update(domain);
    h.update((bytes.len() as u64).to_le_bytes());
    h.update(bytes);
    h.finalize().into()
}

fn hash_json<T: Serialize>(domain: &[u8], value: &T) -> Result<[u8; 32]> {
    Ok(hash_bytes(
        domain,
        &serde_json::to_vec(value).map_err(|e| e.to_string())?,
    ))
}

fn header<T: Serialize>(
    pp: &PublicParameters,
    statement: &T,
    kind: ProofKind,
    context: &[u8],
) -> Result<Proof> {
    pp.validate()?;
    if context.len() > MAX_CONTEXT_BYTES {
        return Err("application context exceeds size limit".into());
    }
    let statement_domain: &[u8] = match kind {
        ProofKind::BinaryR1cs => b"binary",
        ProofKind::QuadraticRelation => b"relation",
    };
    Ok(Proof {
        version: VERSION,
        kind,
        parameter_digest: hash_json(b"parameters", pp)?,
        statement_digest: hash_json(statement_domain, statement)?,
        context_digest: hash_bytes(b"context", context),
        nonce: [0; 32],
        attempt: 0,
        source: None,
        rounds: vec![],
        opening: vec![],
    })
}

fn transcript(proof: &Proof) -> Transcript {
    let mut transcript = Transcript::new(b"LEASH/ordinary-recursive-argument/v1");
    transcript.absorb(b"version", &proof.version.to_le_bytes());
    transcript.absorb(
        b"kind",
        &[match proof.kind {
            ProofKind::BinaryR1cs => 0,
            ProofKind::QuadraticRelation => 1,
        }],
    );
    transcript.absorb(b"parameters", &proof.parameter_digest);
    transcript.absorb(b"statement", &proof.statement_digest);
    transcript.absorb(b"application-context", &proof.context_digest);
    transcript.absorb(b"nonce", &proof.nonce);
    transcript.absorb(b"attempt", &proof.attempt.to_le_bytes());
    transcript
}

fn check_header(expected: &Proof, proof: &Proof, config: &Config) -> Result<()> {
    if proof.version != VERSION
        || proof.kind != expected.kind
        || proof.parameter_digest != expected.parameter_digest
        || proof.statement_digest != expected.statement_digest
        || proof.context_digest != expected.context_digest
    {
        return Err(
            "proof is not bound to these parameters, statement and application context".into(),
        );
    }
    if proof.attempt as usize >= config.max_attempts || proof.rounds.len() != config.rounds {
        return Err("unexpected attempt number or recursion depth".into());
    }
    if proof.source.is_some() != (proof.kind == ProofKind::BinaryR1cs) {
        return Err("source message does not match proof kind".into());
    }
    Ok(())
}

fn reduce(
    pp: &PublicParameters,
    mut relation: Relation,
    mut witness: Witness,
    proof: &mut Proof,
    tr: &mut Transcript,
) -> Result<()> {
    for layer in 0..pp.config.rounds {
        let (message, reduction) =
            ordinary::prove_round(&relation, &witness, &pp.seed, layer, &pp.config.core, tr)?;
        proof.rounds.push(message);
        relation = reduction.relation;
        witness = reduction.witness;
    }
    relation.check(&witness)?;
    proof.opening = witness;
    // Ensure every returned proof has the supported canonical transport.
    proof.to_bytes()?;
    Ok(())
}

fn fresh_nonce() -> Result<[u8; 32]> {
    let mut nonce = [0; 32];
    getrandom::getrandom(&mut nonce)
        .map_err(|e| format!("operating-system randomness failed: {e}"))?;
    Ok(nonce)
}

pub fn prove(
    pp: &PublicParameters,
    instance: &BinaryR1cs,
    assignment: &Assignment,
) -> Result<Proof> {
    prove_with_context(pp, instance, assignment, b"")
}

pub fn prove_with_context(
    pp: &PublicParameters,
    instance: &BinaryR1cs,
    assignment: &Assignment,
    context: &[u8],
) -> Result<Proof> {
    pp.validate()?;
    instance.check_assignment(&assignment.values)?;
    plan_binary(instance, &pp.config)?;
    let template = header(pp, instance, ProofKind::BinaryR1cs, context)?;
    let nonce = fresh_nonce()?;
    for attempt in 0..pp.config.max_attempts {
        let mut proof = Proof {
            nonce,
            attempt: attempt as u32,
            ..template.clone()
        };
        let mut tr = transcript(&proof);
        let (message, relation, witness) = front::prove_source(
            instance,
            &assignment.values,
            &pp.seed,
            &pp.config.source,
            &mut tr,
        )?;
        proof.source = Some(message);
        match reduce(pp, relation, witness, &mut proof, &mut tr) {
            Ok(()) => return Ok(proof),
            Err(message) if message.starts_with("honest-restart:") => continue,
            Err(message) => return Err(message),
        }
    }
    Err("complete-session attempt budget exhausted".into())
}

/// Compile a generic relation. The honest witness must meet its strict cap.
/// With reductions, the interactive extraction theorem permits squared norm
/// up to 23/5 times that cap; the plan/report exposes this relaxed bound.
pub fn prove_relation(
    pp: &PublicParameters,
    relation: &Relation,
    witness: &Witness,
) -> Result<Proof> {
    prove_relation_with_context(pp, relation, witness, b"")
}

pub fn prove_relation_with_context(
    pp: &PublicParameters,
    relation: &Relation,
    witness: &Witness,
    context: &[u8],
) -> Result<Proof> {
    pp.validate()?;
    relation.check(witness)?;
    plan_relation(relation, &pp.config)?;
    let template = header(pp, relation, ProofKind::QuadraticRelation, context)?;
    let nonce = fresh_nonce()?;
    for attempt in 0..pp.config.max_attempts {
        let mut proof = Proof {
            nonce,
            attempt: attempt as u32,
            ..template.clone()
        };
        let mut tr = transcript(&proof);
        match reduce(pp, relation.clone(), witness.clone(), &mut proof, &mut tr) {
            Ok(()) => return Ok(proof),
            Err(message) if message.starts_with("honest-restart:") => continue,
            Err(message) => return Err(message),
        }
    }
    Err("complete-session attempt budget exhausted".into())
}

fn verify_suffix(
    pp: &PublicParameters,
    mut relation: Relation,
    proof: &Proof,
    tr: &mut Transcript,
    plan: &ParameterPlan,
) -> Result<VerificationReport> {
    if proof.opening.len() != plan.terminal_blocks
        || proof
            .opening
            .iter()
            .any(|v| v.len() != plan.terminal_length)
    {
        return Err("terminal opening has the wrong shape".into());
    }
    // Validate all supplied messages before constructing large derived relations.
    for message in &proof.rounds {
        if message.u1.len() != pp.config.core.outer_rank
            || message.u2.len() != pp.config.core.outer_rank
            || message.projection.len() != pp.config.core.projection_rows
            || message.aggregates.len() != pp.config.core.aggregation_repetitions
        {
            return Err("ordinary prover message has the wrong shape".into());
        }
        for p in message
            .u1
            .iter()
            .chain(&message.u2)
            .chain(&message.aggregates)
        {
            p.validate()?;
        }
    }
    for p in proof.opening.iter().flatten() {
        p.validate()?;
    }
    if leash_core::witness_norm_squared(&proof.opening) > plan.terminal_bound_squared {
        return Err("terminal opening exceeds its fixed norm cap".into());
    }
    for (layer, message) in proof.rounds.iter().enumerate() {
        relation =
            ordinary::verify_round(&relation, message, &pp.seed, layer, &pp.config.core, tr)?;
    }
    relation.check(&proof.opening)?;
    Ok(VerificationReport { accepted: true, recursive_rounds: proof.rounds.len(), attempt: proof.attempt,
        proof_bytes: proof.to_bytes()?.len(), terminal_polynomials: plan.terminal_blocks * plan.terminal_length,
        input_honest_bound_squared: plan.input_honest_bound_squared,
        interactive_extracted_input_bound_squared_ceiling: plan.interactive_extracted_input_bound_squared_ceiling,
        relation_semantics: match proof.kind {
            ProofKind::BinaryR1cs => "binary R1CS with constant and public-input pins",
            ProofKind::QuadraticRelation if pp.config.rounds == 0 => "exact equations and strict input norm checked directly",
            ProofKind::QuadraticRelation => "equations with the interactive theorem's relaxed input norm; FS compiler remains experimental",
        },
        compiler: plan.compiler, zero_knowledge: false, security_level: plan.security_level })
}

pub fn verify(
    pp: &PublicParameters,
    instance: &BinaryR1cs,
    proof: &Proof,
) -> Result<VerificationReport> {
    verify_with_context(pp, instance, proof, b"")
}

pub fn verify_with_context(
    pp: &PublicParameters,
    instance: &BinaryR1cs,
    proof: &Proof,
    context: &[u8],
) -> Result<VerificationReport> {
    pp.validate()?;
    let plan = plan_binary(instance, &pp.config)?;
    check_header(
        &header(pp, instance, ProofKind::BinaryR1cs, context)?,
        proof,
        &pp.config,
    )?;
    let mut tr = transcript(proof);
    let relation = front::verify_source(
        instance,
        proof.source.as_ref().ok_or("missing source message")?,
        &pp.seed,
        &pp.config.source,
        &mut tr,
    )?;
    verify_suffix(pp, relation, proof, &mut tr, &plan)
}

/// Verify the compiled generic argument. With recursive rounds, its intended
/// extraction relation has the explicit relaxed norm returned in the report.
/// This function does not certify the Fiat--Shamir compiler's security.
pub fn verify_relation(
    pp: &PublicParameters,
    relation: &Relation,
    proof: &Proof,
) -> Result<VerificationReport> {
    verify_relation_with_context(pp, relation, proof, b"")
}

pub fn verify_relation_with_context(
    pp: &PublicParameters,
    relation: &Relation,
    proof: &Proof,
    context: &[u8],
) -> Result<VerificationReport> {
    pp.validate()?;
    let plan = plan_relation(relation, &pp.config)?;
    check_header(
        &header(pp, relation, ProofKind::QuadraticRelation, context)?,
        proof,
        &pp.config,
    )?;
    let mut tr = transcript(proof);
    verify_suffix(pp, relation.clone(), proof, &mut tr, &plan)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn integer_square_root_boundaries() {
        for x in 0..10000u128 {
            let root = ceil_sqrt(x);
            assert!(root * root >= x);
            assert!(root == 0 || (root - 1) * (root - 1) < x);
        }
        assert_eq!(ceil_sqrt(u128::MAX), 1u128 << 64);
    }
}
