use leash_core::{witness_norm_squared, Poly, Transcript, D, Q};
use leash_frontend::{
    prove_source, source_shape_and_bound, verify_source, Assignment, BinaryR1cs, CircuitBuilder,
    PublicPin, SourceConfig, SourceMessage, MAX_GATES, MAX_JSON_BYTES, MAX_VARIABLES,
};

const SEED: [u8; 32] = [37; 32];
fn config(chunks: usize) -> SourceConfig {
    SourceConfig {
        rank: 1,
        challenge_rows: 4,
        chunks,
    }
}
fn transcript() -> Transcript {
    Transcript::new(b"leash frontend integration test")
}
fn identity(size: usize) -> (BinaryR1cs, Assignment) {
    let rows: Vec<Vec<usize>> = (0..size).map(|i| vec![i]).collect();
    (
        BinaryR1cs {
            variables: size,
            a: rows.clone(),
            b: rows.clone(),
            c: rows,
            public_pins: vec![],
        },
        Assignment {
            values: vec![true; size],
        },
    )
}

#[test]
fn builder_truth_tables_and_constant_wire() {
    for x in [false, true] {
        for y in [false, true] {
            let mut builder = CircuitBuilder::new();
            let a = builder.public_input(x).unwrap();
            let b = builder.input(y).unwrap();
            let both = builder.and(a, b).unwrap();
            let exclusive = builder.xor(a, b).unwrap();
            let inverse = builder.not(a).unwrap();
            let zero = builder.xor(a, a).unwrap();
            let constant_zero = builder.not(0).unwrap();
            builder.assert_equal(zero, constant_zero).unwrap();
            builder.pin_public(both, x & y).unwrap();
            let (instance, assignment) = builder.finish().unwrap();
            assert_eq!(assignment.values[both], x & y);
            assert_eq!(assignment.values[exclusive], x ^ y);
            assert_eq!(assignment.values[inverse], !x);
            assert!(!assignment.values[zero]);
            instance.check_assignment(&assignment.values).unwrap();
            let mut wrong = assignment.values.clone();
            wrong[0] = false;
            assert!(instance.check_assignment(&wrong).is_err());
        }
    }
    let mut builder = CircuitBuilder::new();
    assert!(builder.and(usize::MAX, 0).is_err());
    assert!(builder.not(1).is_err());
    let zero = builder.input(false).unwrap();
    builder.assert_equal(zero, 0).unwrap();
    assert!(builder.finish().is_err());
}

#[test]
fn sparse_xor_reduction_and_transcript_match() {
    let mut builder = CircuitBuilder::new();
    let a = builder.public_input(true).unwrap();
    let b = builder.input(false).unwrap();
    let x = builder.xor(a, b).unwrap();
    let z = builder.and(a, x).unwrap();
    let inverse = builder.not(b).unwrap();
    builder.assert_equal(z, inverse).unwrap();
    let (instance, assignment) = builder.finish().unwrap();
    let cfg = config(3);
    let mut pt = transcript();
    let (message, relation, witness) =
        prove_source(&instance, &assignment.values, &SEED, &cfg, &mut pt).unwrap();
    assert_eq!(
        source_shape_and_bound(&instance, &cfg).unwrap(),
        (relation.r, relation.n, relation.bound_squared)
    );
    let mut vt = transcript();
    let verified = verify_source(&instance, &message, &SEED, &cfg, &mut vt).unwrap();
    assert_eq!(relation, verified);
    verified.check(&witness).unwrap();
    assert_eq!(
        pt.challenge(b"after-source").uniform(Q),
        vt.challenge(b"after-source").uniform(Q)
    );
    assert!(message.replies.iter().all(|g| g % 2 == 0));
}

#[test]
fn all_one_coefficients_use_jbar_and_correct_partial_conjugation() {
    // The second polynomial has one live coefficient; its conjugate must not
    // accidentally inherit the original's high-coefficient padding convention.
    let (instance, assignment) = identity(D + 1);
    let cfg = config(3);
    let (message, relation, witness) = prove_source(
        &instance,
        &assignment.values,
        &SEED,
        &cfg,
        &mut transcript(),
    )
    .unwrap();
    assert_eq!((relation.r, relation.n), (24, 1));
    assert_eq!(witness_norm_squared(&witness), 8 * (D as u128 + 1));
    assert_eq!(witness[0][0], Poly(vec![1; D]));
    assert_eq!(witness[12][0], Poly(vec![1; D]).conjugate());
    assert_eq!(witness[1][0], Poly::constant(1));
    assert_eq!(witness[13][0], Poly::constant(1));
    for group in 0..8 {
        assert_eq!(witness[group * 3 + 2][0], Poly::zero());
    }
    let verified = verify_source(&instance, &message, &SEED, &cfg, &mut transcript()).unwrap();
    assert_eq!(relation, verified);
    verified.check(&witness).unwrap();
    let mut changed = witness.clone();
    changed[13][0].0[63] = Q - 1;
    assert!(verified.check(&changed).is_err());
}

#[test]
fn a_live_nonconstant_coefficient_moves_under_conjugation() {
    let (instance, assignment) = identity(D + 3);
    let cfg = config(2);
    let (_, relation, witness) = prove_source(
        &instance,
        &assignment.values,
        &SEED,
        &cfg,
        &mut transcript(),
    )
    .unwrap();
    assert_eq!(witness[1][0].0[..4], [1, 1, 1, 0]);
    assert_eq!(witness[9][0].0[1], 0);
    assert_eq!(witness[9][0].0[62..], [Q - 1, Q - 1]);
    relation.check(&witness).unwrap();
}

#[test]
fn zero_gate_circuit_has_explicit_zero_padded_gate_blocks() {
    for inputs in [0, 1, D] {
        let mut builder = CircuitBuilder::new();
        for i in 0..inputs {
            builder.public_input(i % 2 == 0).unwrap();
        }
        let (instance, assignment) = builder.finish().unwrap();
        assert!(instance.a.is_empty());
        let cfg = config(2);
        let (message, relation, witness) = prove_source(
            &instance,
            &assignment.values,
            &SEED,
            &cfg,
            &mut transcript(),
        )
        .unwrap();
        for group in [0, 1, 2, 4, 5, 6] {
            for chunk in 0..2 {
                assert!(witness[group * 2 + chunk]
                    .iter()
                    .all(|p| *p == Poly::zero()));
            }
        }
        let rebuilt = verify_source(&instance, &message, &SEED, &cfg, &mut transcript()).unwrap();
        assert_eq!(rebuilt, relation);
        rebuilt.check(&witness).unwrap();
    }
}

#[test]
fn public_pins_are_exact_target_constraints() {
    let mut builder = CircuitBuilder::new();
    builder.public_input(true).unwrap();
    let (instance, assignment) = builder.finish().unwrap();
    let cfg = config(1);
    let (message, _, witness) = prove_source(
        &instance,
        &assignment.values,
        &SEED,
        &cfg,
        &mut transcript(),
    )
    .unwrap();
    let mut changed = instance.clone();
    changed.public_pins[0].value = false;
    assert!(prove_source(&changed, &assignment.values, &SEED, &cfg, &mut transcript()).is_err());
    let rebuilt = verify_source(&changed, &message, &SEED, &cfg, &mut transcript()).unwrap();
    assert!(rebuilt.check(&witness).is_err());
    let mut removed = instance.clone();
    removed.public_pins.clear();
    let rebuilt = verify_source(&removed, &message, &SEED, &cfg, &mut transcript()).unwrap();
    // The two statements produce different target relations even if the removed
    // pin was redundant for this particular assignment.
    let original = verify_source(&instance, &message, &SEED, &cfg, &mut transcript()).unwrap();
    assert_ne!(rebuilt, original);
}

#[test]
fn source_message_validation_and_local_constraint_rejection() {
    let (instance, assignment) = identity(3);
    let cfg = config(1);
    let (message, _, witness) = prove_source(
        &instance,
        &assignment.values,
        &SEED,
        &cfg,
        &mut transcript(),
    )
    .unwrap();
    let mut changed = message.clone();
    changed.commitment[0].0[0] = (changed.commitment[0].0[0] + 1) % Q;
    let rebuilt = verify_source(&instance, &changed, &SEED, &cfg, &mut transcript()).unwrap();
    assert!(rebuilt.check(&witness).is_err());
    let mut changed = message.clone();
    changed.replies[0] += 2;
    let rebuilt = verify_source(&instance, &changed, &SEED, &cfg, &mut transcript()).unwrap();
    assert!(rebuilt.check(&witness).is_err());
    let mut bad = Vec::new();
    let mut m = message.clone();
    m.commitment.clear();
    bad.push(m);
    let mut m = message.clone();
    m.replies.pop();
    bad.push(m);
    let mut m = message.clone();
    m.replies[0] = 1;
    bad.push(m);
    let mut m = message.clone();
    m.replies[0] = i64::MIN;
    bad.push(m);
    let mut m = message.clone();
    m.replies[0] = i64::MAX;
    bad.push(m);
    let mut m = message.clone();
    m.commitment[0] = Poly(vec![]);
    bad.push(m);
    let mut m = message.clone();
    m.commitment[0].0[0] = Q;
    bad.push(m);
    for malformed in bad {
        assert!(verify_source(&instance, &malformed, &SEED, &cfg, &mut transcript()).is_err());
    }
    let mut different = cfg.clone();
    different.challenge_rows += 1;
    assert!(verify_source(&instance, &message, &SEED, &different, &mut transcript()).is_err());
}

#[test]
fn strict_json_roundtrip_and_resource_limits() {
    let (instance, assignment) = identity(3);
    assert_eq!(
        BinaryR1cs::from_json(&instance.to_json().unwrap()).unwrap(),
        instance
    );
    assert_eq!(
        Assignment::from_json(&assignment.to_json().unwrap()).unwrap(),
        assignment
    );
    let mut value = serde_json::to_value(&instance).unwrap();
    value["unknown"] = true.into();
    assert!(BinaryR1cs::from_json(&serde_json::to_vec(&value).unwrap()).is_err());
    assert!(Assignment::from_json(br#"{"values":[1]}"#).is_err());
    assert!(Assignment::from_json(br#"{"values":[true],"unknown":false}"#).is_err());
    assert!(BinaryR1cs::from_json(&vec![b' '; MAX_JSON_BYTES + 1]).is_err());
    let mut malformed = Vec::new();
    let mut i = instance.clone();
    i.variables = 0;
    malformed.push(i);
    let mut i = instance.clone();
    i.variables = MAX_VARIABLES + 1;
    malformed.push(i);
    let mut i = instance.clone();
    i.a[0] = vec![0, 0];
    malformed.push(i);
    let mut i = instance.clone();
    i.a[0] = vec![1, 0];
    malformed.push(i);
    let mut i = instance.clone();
    i.a[0] = vec![usize::MAX];
    malformed.push(i);
    let mut i = instance.clone();
    i.b.pop();
    malformed.push(i);
    let mut i = instance.clone();
    i.a = vec![vec![]; MAX_GATES + 1];
    malformed.push(i);
    let mut i = instance.clone();
    i.public_pins = vec![
        PublicPin {
            wire: 0,
            value: true,
        },
        PublicPin {
            wire: 0,
            value: true,
        },
    ];
    malformed.push(i);
    for i in malformed {
        assert!(i.validate().is_err());
        assert!(
            prove_source(&i, &assignment.values, &SEED, &config(1), &mut transcript()).is_err()
        );
    }
    for cfg in [
        SourceConfig {
            rank: 0,
            ..config(1)
        },
        SourceConfig {
            challenge_rows: 0,
            ..config(1)
        },
        SourceConfig {
            chunks: 0,
            ..config(1)
        },
        SourceConfig {
            chunks: usize::MAX,
            ..config(1)
        },
    ] {
        assert!(source_shape_and_bound(&instance, &cfg).is_err());
    }
    let unknown = r#"{"rank":1,"challenge_rows":4,"chunks":1,"unknown":0}"#;
    assert!(serde_json::from_str::<SourceConfig>(unknown).is_err());
    let invalid_poly = serde_json::json!({"commitment":[[0]],"replies":[0,0,0,0]});
    assert!(serde_json::from_value::<SourceMessage>(invalid_poly).is_err());
}
