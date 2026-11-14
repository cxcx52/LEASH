use leash::{frontend::CircuitBuilder, prove, setup, verify, Config, Proof};

fn main() -> Result<(), String> {
    let mut circuit = CircuitBuilder::new();
    let a = circuit.input(true)?;
    let b = circuit.public_input(false)?;
    let c = circuit.xor(a, b)?;
    circuit.pin_public(c, true)?;
    let (statement, assignment) = circuit.finish()?;
    let parameters = setup(Config::default())?;
    let proof = prove(&parameters, &statement, &assignment)?;
    let bytes = proof.to_bytes()?;
    let decoded = Proof::from_bytes(&bytes)?;
    let report = verify(&parameters, &statement, &decoded)?;
    println!(
        "accepted={}, rounds={}, proof_bytes={}",
        report.accepted, report.recursive_rounds, report.proof_bytes
    );
    Ok(())
}
