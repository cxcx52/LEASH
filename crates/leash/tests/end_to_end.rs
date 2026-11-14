use leash::{
    algebra::{Constraint, LinearTerm, Poly, QuadraticTerm, Relation},
    frontend::CircuitBuilder,
    plan_binary, plan_relation, prove, prove_relation, prove_with_context, setup, verify,
    verify_relation, verify_with_context, Config, Proof, PublicParameters,
};

fn circuit() -> (leash::frontend::BinaryR1cs, leash::frontend::Assignment) {
    let mut builder = CircuitBuilder::new();
    let a = builder.input(true).unwrap();
    let b = builder.public_input(false).unwrap();
    let c = builder.xor(a, b).unwrap();
    let d = builder.not(b).unwrap();
    let e = builder.and(c, d).unwrap();
    builder.pin_public(e, true).unwrap();
    builder.finish().unwrap()
}

#[test]
fn binary_api_complete_roundtrip_and_binding() {
    let (statement, assignment) = circuit();
    let pp = setup(Config::development()).unwrap();
    let plan = plan_binary(&statement, &pp.config).unwrap();
    assert_eq!(plan.layers.len(), 1);
    let proof = prove_with_context(&pp, &statement, &assignment, b"application/invoice/7").unwrap();
    assert_eq!(proof.rounds.len(), 1);
    assert_eq!(proof.opening.len(), plan.terminal_blocks);
    let bytes = proof.to_bytes().unwrap();
    let decoded = Proof::from_bytes(&bytes).unwrap();
    assert_eq!(decoded, proof);
    let report = verify_with_context(&pp, &statement, &decoded, b"application/invoice/7").unwrap();
    assert!(report.accepted && !report.zero_knowledge);
    assert_eq!(report.proof_bytes, bytes.len());
    let mut malformed = proof.clone();
    malformed.version += 1;
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    let mut malformed = proof.clone();
    malformed.attempt = pp.config.max_attempts as u32;
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    let mut malformed = proof.clone();
    malformed.kind = leash::ProofKind::QuadraticRelation;
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    let mut malformed = proof.clone();
    malformed.source = None;
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    let mut malformed = proof.clone();
    malformed.source.as_mut().unwrap().replies.pop();
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    let mut malformed = proof.clone();
    malformed.rounds[0].aggregates.pop();
    assert!(verify_with_context(&pp, &statement, &malformed, b"application/invoice/7").is_err());
    assert!(verify(&pp, &statement, &proof).is_err());
    let mut changed = statement.clone();
    changed.public_pins[0].value ^= true;
    assert!(verify_with_context(&pp, &changed, &proof, b"application/invoice/7").is_err());
    let mut changed_pp = pp.clone();
    changed_pp.seed[0] ^= 1;
    assert!(
        verify_with_context(&changed_pp, &statement, &proof, b"application/invoice/7").is_err()
    );
    let mut damaged = proof.clone();
    damaged.rounds[0].u1[0] = damaged.rounds[0].u1[0].add(&Poly::constant(1));
    assert!(verify_with_context(&pp, &statement, &damaged, b"application/invoice/7").is_err());
    let mut damaged = proof;
    damaged.opening[0][0] = damaged.opening[0][0].add(&Poly::constant(1));
    assert!(verify_with_context(&pp, &statement, &damaged, b"application/invoice/7").is_err());
    assert_eq!(
        PublicParameters::from_json(&pp.to_json().unwrap()).unwrap(),
        pp
    );
}

#[test]
fn generic_relation_two_recursive_rounds() {
    let relation = Relation {
        r: 2,
        n: 2,
        bound_squared: 4,
        full: vec![Constraint {
            quadratic: vec![QuadraticTerm {
                left: 0,
                right: 1,
                coefficient: Poly::constant(1),
            }],
            linear: vec![],
            constant: Poly::constant(-2),
        }],
        scalar: vec![Constraint {
            quadratic: vec![],
            linear: vec![LinearTerm {
                block: 0,
                position: 0,
                coefficient: Poly::constant(1),
            }],
            constant: Poly::constant(-1),
        }],
    };
    let witness = vec![vec![Poly::constant(1); 2]; 2];
    let pp = setup(Config {
        rounds: 2,
        ..Config::development()
    })
    .unwrap();
    assert_eq!(
        plan_relation(&relation, &pp.config).unwrap().layers.len(),
        2
    );
    let proof = prove_relation(&pp, &relation, &witness).unwrap();
    let decoded = Proof::from_bytes(&proof.to_bytes().unwrap()).unwrap();
    let verified = verify_relation(&pp, &relation, &decoded).unwrap();
    assert!(verified.accepted);
    assert_eq!(verified.input_honest_bound_squared, 4);
    assert_eq!(
        verified.interactive_extracted_input_bound_squared_ceiling,
        19
    );
    let mut damaged = decoded;
    damaged.rounds[1].projection[0] += 1;
    assert!(verify_relation(&pp, &relation, &damaged).is_err());
    let mut changed = relation;
    changed.bound_squared = 3;
    assert!(prove_relation(&pp, &changed, &witness).is_err());
}

#[test]
fn explicit_zero_round_path_and_invalid_configuration() {
    let (statement, assignment) = circuit();
    let pp = setup(Config {
        rounds: 0,
        ..Config::development()
    })
    .unwrap();
    let proof = prove(&pp, &statement, &assignment).unwrap();
    assert!(proof.rounds.is_empty());
    assert!(verify(&pp, &statement, &proof).unwrap().accepted);
    let mut bad_assignment = assignment;
    bad_assignment.values[0] = false;
    assert!(prove(&pp, &statement, &bad_assignment).is_err());
    assert!(setup(Config {
        rounds: 4,
        ..Config::default()
    })
    .is_err());
    let mut bad_config = Config::default();
    bad_config.source.challenge_rows = 16;
    assert!(setup(bad_config).is_err());
    let huge = Relation {
        r: 1,
        n: 1,
        bound_squared: u128::MAX,
        full: vec![],
        scalar: vec![],
    };
    assert!(plan_relation(&huge, &Config::default()).is_err());
    let trivial_radius = Relation {
        r: 8,
        n: 1,
        bound_squared: 1u128 << 32,
        full: vec![],
        scalar: vec![],
    };
    assert!(plan_relation(&trivial_radius, &Config::default())
        .unwrap_err()
        .contains("collision radius"));
}

#[test]
fn default_profile_all_one_binary_witness() {
    // Honest structured coefficients, not the old Gaussian norm heuristic.
    let identity = (0..64).map(|i| vec![i]).collect::<Vec<_>>();
    let statement = leash::frontend::BinaryR1cs {
        variables: 64,
        a: identity.clone(),
        b: identity.clone(),
        c: identity,
        public_pins: vec![],
    };
    let assignment = leash::frontend::Assignment {
        values: vec![true; 64],
    };
    let pp = setup(Config::default()).unwrap();
    let proof = prove(&pp, &statement, &assignment).unwrap();
    assert!(verify(&pp, &statement, &proof).unwrap().accepted);
}
