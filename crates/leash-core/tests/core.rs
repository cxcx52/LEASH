use leash_core::*;
use serde::Serialize;
use serde_json::{json, Value};
use sha3::{Digest, Sha3_256};
use std::fmt::Write;

fn kat() -> Value {
    serde_json::from_str(include_str!("known_answers.json")).unwrap()
}
fn numbers(value: &Value) -> Vec<u64> {
    value
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_u64().unwrap())
        .collect()
}
fn hash(polys: &[Poly]) -> String {
    let mut h = Sha3_256::new();
    for p in polys {
        for x in &p.0 {
            h.update(x.to_le_bytes());
        }
    }
    h.finalize().iter().fold(String::new(), |mut text, b| {
        write!(&mut text, "{b:02x}").unwrap();
        text
    })
}
fn scalar(value: i64) -> Poly {
    Poly::constant(value)
}
fn constraint() -> Constraint {
    Constraint {
        quadratic: vec![],
        linear: vec![],
        constant: Poly::zero(),
    }
}
fn relation() -> Relation {
    Relation {
        r: 2,
        n: 1,
        bound_squared: 25,
        full: vec![],
        scalar: vec![],
    }
}

#[test]
fn negacyclic_basis_and_dense_python_answer() {
    for i in 0..D {
        for j in 0..D {
            let mut a = Poly::zero();
            a.0[i] = 1;
            let mut b = Poly::zero();
            b.0[j] = 1;
            let mut expected = Poly::zero();
            expected.0[(i + j) % D] = if i + j < D { 1 } else { Q - 1 };
            assert_eq!(a.mul(&b), expected);
        }
    }
    let a = Poly::from_signed(
        &(0..D)
            .map(|i| {
                if i % 2 == 0 {
                    (i * i + 13) as i64
                } else {
                    -((i * i + 13) as i64)
                }
            })
            .collect::<Vec<_>>(),
    )
    .unwrap();
    let b = Poly::from_signed(
        &(0..D)
            .map(|i| {
                if (i / 3) % 2 == 0 {
                    (7 * i + 2) as i64
                } else {
                    -((7 * i + 2) as i64)
                }
            })
            .collect::<Vec<_>>(),
    )
    .unwrap();
    assert_eq!(a.mul(&b).0, numbers(&kat()["dense_product"]));
    assert_eq!(a.mul(&b), b.mul(&a));
    assert_eq!(a.conjugate().conjugate(), a);
    assert_eq!(a.mul(&b).conjugate(), a.conjugate().mul(&b.conjugate()));
    assert_eq!(
        a.mul(&a.conjugate()).0[0],
        (a.norm_squared() % Q as u128) as u64
    );
}

#[test]
fn arithmetic_near_machine_and_ring_boundaries() {
    assert_eq!(residue(i128::MIN), i128::MIN.rem_euclid(Q as i128) as u64);
    assert_eq!(centered(Q / 2), Q as i64 / 2);
    assert_eq!(centered(Q / 2 + 1), -(Q as i64 / 2));
    let a = Poly(vec![Q - 1; D]);
    let b = Poly(vec![Q - 2; D]);
    assert_eq!(a.add(&b).sub(&b), a);
    assert_eq!(
        a.scale(u64::MAX).0[0],
        ((Q as u128 - 1) * u64::MAX as u128 % Q as u128) as u64
    );
    assert_eq!(
        a.mul(&b).0,
        (0..D)
            .map(|i| residue(2 * (2 * i as i128 + 2 - D as i128)))
            .collect::<Vec<_>>()
    );
    assert_eq!(Poly::constant(i64::MIN).0[0], residue(i64::MIN as i128));
    assert_eq!(a.norm_squared(), D as u128);
    assert!(Poly::from_signed(&[0; D + 1]).is_err());
    assert_eq!(dot(&[], &[]), Poly::zero());
}

#[test]
fn relation_distinguishes_full_scalar_cross_term_and_closed_norm() {
    let witness = vec![vec![scalar(3)], vec![scalar(4)]];
    let mut r = relation();
    let mut c = constraint();
    c.quadratic.push(QuadraticTerm {
        left: 0,
        right: 1,
        coefficient: scalar(1),
    });
    c.constant = scalar(-12);
    r.full.push(c);
    assert!(r.check(&witness).is_ok()); // Cross term 3*4 counted once, norm exactly 25.
    r.bound_squared = 24;
    assert!(r.check(&witness).is_err());
    r.bound_squared = 25;
    let mut x = Poly::zero();
    x.0[1] = 1;
    let mut nonconstant = constraint();
    nonconstant.constant = x;
    r.scalar.push(nonconstant.clone());
    assert!(r.check(&witness).is_ok());
    r.full.push(nonconstant);
    assert!(r.check(&witness).is_err());
    let mut linear = constraint();
    linear.linear.push(LinearTerm {
        block: 1,
        position: 0,
        coefficient: scalar(-2),
    });
    linear.constant = scalar(8);
    assert_eq!(linear.evaluate(&witness).unwrap(), Poly::zero());
}

#[test]
fn relations_reject_malformed_untrusted_coordinates_without_panics() {
    let mut r = relation();
    let good = vec![vec![scalar(3)], vec![scalar(4)]];
    assert!(r.check(&vec![vec![scalar(3)]]).is_err());
    assert!(r.check(&vec![vec![scalar(3)], vec![]]).is_err());
    assert!(r
        .check(&vec![vec![Poly(vec![0; D - 1])], vec![scalar(4)]])
        .is_err());
    let mut bad_coeff = Poly::zero();
    bad_coeff.0[4] = Q;
    assert!(r.check(&vec![vec![bad_coeff], vec![scalar(4)]]).is_err());
    let mut c = constraint();
    c.linear.push(LinearTerm {
        block: 2,
        position: 0,
        coefficient: scalar(1),
    });
    assert!(c.evaluate(&good).is_err());
    r.full.push(c);
    assert!(r.check(&good).is_err());
    r = relation();
    r.r = usize::MAX;
    r.n = 2;
    assert!(r.validate().is_err());
    r = relation();
    r.n = MAX_WITNESS_POLYS;
    assert!(r.validate().is_err());
    r = relation();
    r.n = 0;
    assert!(r.validate().is_err());
    let mut c = constraint();
    c.quadratic.push(QuadraticTerm {
        left: 0,
        right: 3,
        coefficient: scalar(1),
    });
    assert!(c.evaluate(&good).is_err());
}

#[test]
fn strict_wire_types_and_polynomial_serde() {
    let r = relation();
    let bytes = serde_json::to_vec(&r).unwrap();
    assert_eq!(serde_json::from_slice::<Relation>(&bytes).unwrap(), r);
    let mut large_bound = r.clone();
    large_bound.bound_squared = (1u128 << 110) + 123;
    let bytes = serde_json::to_vec(&large_bound).unwrap();
    assert_eq!(
        serde_json::from_slice::<Relation>(&bytes).unwrap(),
        large_bound
    );
    let mut v = serde_json::to_value(&r).unwrap();
    v["unexpected"] = json!(1);
    assert!(serde_json::from_value::<Relation>(v).is_err());
    assert!(serde_json::from_str::<Poly>("[]").is_err());
    assert!(serde_json::from_value::<Poly>(json!(vec![0; D + 1])).is_err());
    let mut p = vec![0u64; D];
    p[0] = Q;
    assert!(serde_json::from_value::<Poly>(json!(p)).is_err());
    let mut p = vec![0i64; D];
    p[0] = -1;
    assert!(serde_json::from_value::<Poly>(json!(p)).is_err());
    let c = constraint();
    let mut v = serde_json::to_value(&c).unwrap();
    v["unknown"] = json!(true);
    assert!(serde_json::from_value::<Constraint>(v).is_err());
    let duplicate = r#"{"r":2,"r":3,"n":1,"bound_squared":25,"full":[],"scalar":[]}"#;
    assert!(serde_json::from_str::<Relation>(duplicate).is_err());
}

#[test]
fn independent_python_shake_sampling_answers_include_rejections() {
    let expected = kat();
    let mut x = Xof::new(b"known-answer seed", b"core/test");
    assert_eq!(
        (0..16).map(|_| x.uniform(Q)).collect::<Vec<_>>(),
        numbers(&expected["uniform_q"])
    );
    let mut x = Xof::new(b"known-answer seed", b"core/test");
    assert_eq!(
        (0..16)
            .map(|_| x.uniform((1u64 << 63) + 17))
            .collect::<Vec<_>>(),
        numbers(&expected["uniform_large"])
    );
    let mut x = Xof::new(b"known-answer seed", b"core/test");
    let bits = (0..32).map(|_| x.bit()).collect::<Vec<_>>();
    assert_eq!(serde_json::to_value(bits).unwrap(), expected["bits"]);
    let mut x = Xof::new(b"known-answer seed", b"core/test");
    let chi = (0..32).map(|_| x.ternary()).collect::<Vec<_>>();
    assert_eq!(serde_json::to_value(chi).unwrap(), expected["ternary"]);
    let mut x = Xof::new(b"edge", b"modulus");
    assert_eq!(x.uniform(1), 0);
    for _ in 0..100 {
        assert!(x.uniform(u64::MAX) < u64::MAX);
    }
    let p = x.challenge_poly();
    assert!((0..D).all(|i| p.coefficient(i).abs() <= 2));
    assert!(p.norm_squared() <= 4 * D as u128);
}

#[test]
fn python_transcript_answers_and_length_domain_counter_separation() {
    let expected = kat();
    let mut t = Transcript::new(b"test/root");
    t.absorb(b"a", b"bc");
    t.absorb(b"ab", b"c");
    let mut x = t.challenge(b"coins");
    assert_eq!(
        (0..8).map(|_| x.uniform(Q)).collect::<Vec<_>>(),
        numbers(&expected["transcript_first"])
    );
    t.absorb(b"reply", b"\0hello");
    let mut x = t.challenge(b"coins");
    assert_eq!(
        (0..8).map(|_| x.uniform(5)).collect::<Vec<_>>(),
        numbers(&expected["transcript_second"])
    );
    let mut x = t.challenge(b"coins");
    assert_eq!(
        (0..8).map(|_| x.uniform(Q)).collect::<Vec<_>>(),
        numbers(&expected["transcript_third"])
    );
    let first = |domain: &[u8], label: &[u8], data: &[u8]| {
        let mut t = Transcript::new(domain);
        t.absorb(label, data);
        t.challenge(b"c").poly()
    };
    assert_ne!(first(b"d", b"a", b"bc"), first(b"d", b"ab", b"c"));
    assert_ne!(first(b"d", b"a", b"bc"), first(b"d2", b"a", b"bc"));
    let mut t = Transcript::new(b"d");
    assert_ne!(t.challenge(b"c").poly(), t.challenge(b"c").poly());
    #[derive(Serialize)]
    struct Record {
        alpha: Vec<u64>,
        beta: String,
    }
    let mut a = Transcript::new(b"json");
    let mut b = Transcript::new(b"json");
    a.absorb_json(
        b"value",
        &Record {
            alpha: vec![1, 2],
            beta: "x".into(),
        },
    )
    .unwrap();
    b.absorb(b"value", br#"{"alpha":[1,2],"beta":"x"}"#);
    assert_eq!(a.challenge(b"c").poly(), b.challenge(b"c").poly());
}

#[test]
fn public_matrix_commitment_same_stream_prefix_and_python_answers() {
    let seed = std::array::from_fn(|i| i as u8);
    let rows = (0..2)
        .map(|i| matrix_row(&seed, b"public/setup", i, 3))
        .collect::<Vec<_>>();
    let all = rows.iter().flatten().cloned().collect::<Vec<_>>();
    assert_eq!(hash(&all), kat()["matrix_sha3_256"].as_str().unwrap());
    assert_eq!(matrix_row(&seed, b"public/setup", 0, 1), rows[0][..1]);
    assert_ne!(rows[0], rows[1]);
    assert_ne!(rows[0], matrix_row(&seed, b"other/setup", 0, 3));
    let opening = vec![
        Poly::from_signed(&[1, -2, 3]).unwrap(),
        Poly::from_signed(&[-4, 5]).unwrap(),
        scalar(7),
    ];
    let commitment = commit(&seed, b"public/setup", 2, &opening);
    assert_eq!(
        commitment,
        rows.iter().map(|r| dot(r, &opening)).collect::<Vec<_>>()
    );
    assert_eq!(
        hash(&commitment),
        kat()["commitment_sha3_256"].as_str().unwrap()
    );
    let mut opening_padded = opening;
    opening_padded.push(Poly::zero());
    assert_eq!(
        commitment,
        commit(&seed, b"public/setup", 2, &opening_padded)
    );
}
