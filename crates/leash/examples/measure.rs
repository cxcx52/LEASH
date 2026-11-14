//! Sequential local measurements of the actual Rust source-to-core pipeline.
use leash::{
    frontend::{Assignment, BinaryR1cs, PublicPin},
    prove, setup, verify, Config, Proof,
};
use serde::Serialize;
use std::time::Instant;

#[derive(Serialize)]
struct Measurement {
    size: usize,
    repetition: usize,
    fixture: &'static str,
    rounds: usize,
    setup_ms: f64,
    prove_ms: f64,
    encode_ms: f64,
    decode_ms: f64,
    verify_ms: f64,
    proof_bytes: usize,
    attempt: u32,
    accepted: bool,
}

fn main() -> Result<(), String> {
    let rounds = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "1".into())
        .parse::<usize>()
        .map_err(|e| e.to_string())?;
    for size in [64, 256, 1024] {
        let identity = (0..size).map(|i| vec![i]).collect::<Vec<_>>();
        let statement = BinaryR1cs {
            variables: size,
            a: identity.clone(),
            b: identity.clone(),
            c: identity,
            public_pins: vec![PublicPin {
                wire: 0,
                value: true,
            }],
        };
        let assignment = Assignment {
            values: vec![true; size],
        };
        for repetition in 0..3 {
            let start = Instant::now();
            let pp = setup(Config {
                rounds,
                ..Config::default()
            })?;
            let setup_ms = start.elapsed().as_secs_f64() * 1000.0;
            let start = Instant::now();
            let proof = prove(&pp, &statement, &assignment)?;
            let prove_ms = start.elapsed().as_secs_f64() * 1000.0;
            let start = Instant::now();
            let bytes = proof.to_bytes()?;
            let encode_ms = start.elapsed().as_secs_f64() * 1000.0;
            let start = Instant::now();
            let decoded = Proof::from_bytes(&bytes)?;
            let decode_ms = start.elapsed().as_secs_f64() * 1000.0;
            let start = Instant::now();
            let accepted = verify(&pp, &statement, &decoded)?.accepted;
            let verify_ms = start.elapsed().as_secs_f64() * 1000.0;
            let row = Measurement {
                size,
                repetition,
                fixture: "A=B=C=identity, all-one binary witness",
                rounds,
                setup_ms,
                prove_ms,
                encode_ms,
                decode_ms,
                verify_ms,
                proof_bytes: bytes.len(),
                attempt: proof.attempt,
                accepted,
            };
            println!(
                "{}",
                serde_json::to_string(&row).map_err(|e| e.to_string())?
            );
        }
    }
    Ok(())
}
