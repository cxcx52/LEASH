use leash::{
    algebra::{Relation, Witness},
    frontend::{Assignment, BinaryR1cs, CircuitBuilder},
    plan_binary, prove_relation_with_context, prove_with_context, setup,
    verify_relation_with_context, verify_with_context, Config, Proof, PublicParameters,
    MAX_PROOF_BYTES,
};
use serde::Serialize;
use std::{
    collections::BTreeMap,
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
    process::ExitCode,
    time::Instant,
};

type Result<T> = std::result::Result<T, String>;
const JSON_LIMIT: usize = 64 * 1024 * 1024;
const HELP: &str = "LEASH proof library

leash demo --out demo-output [--rounds N] [--development]
leash setup --out parameters.json [--rounds N] [--development]
leash plan --parameters parameters.json --circuit circuit.json
leash prove --parameters parameters.json --circuit circuit.json --witness witness.json --out proof.leash [--context TEXT]
leash verify --parameters parameters.json --circuit circuit.json --proof proof.leash [--context TEXT]
leash prove-relation --parameters parameters.json --relation relation.json --witness witness.json --out proof.leash [--context TEXT]
leash verify-relation --parameters parameters.json --relation relation.json --proof proof.leash [--context TEXT]

Outputs are created without overwriting existing files. --development selects
small test ranks. The seed-expanded CRS / SHAKE Fiat-Shamir compiler is
experimental, has no certified security level, and is not zero knowledge.
";

struct Args {
    command: String,
    values: BTreeMap<String, String>,
    development: bool,
}
impl Args {
    fn parse() -> Result<Self> {
        let mut argv = std::env::args().skip(1);
        let command = argv.next().unwrap_or_else(|| "help".into());
        let mut result = Self {
            command,
            values: BTreeMap::new(),
            development: false,
        };
        while let Some(key) = argv.next() {
            if key == "--development" {
                if result.development {
                    return Err("duplicate --development".into());
                }
                result.development = true;
            } else {
                if !key.starts_with("--") {
                    return Err(format!("unexpected argument {key}"));
                }
                let value = argv
                    .next()
                    .ok_or_else(|| format!("missing value for {key}"))?;
                if result.values.insert(key.clone(), value).is_some() {
                    return Err(format!("duplicate {key}"));
                }
            }
        }
        Ok(result)
    }
    fn get(&self, key: &str) -> Result<&str> {
        self.values
            .get(key)
            .map(String::as_str)
            .ok_or_else(|| format!("missing {key}"))
    }
    fn allow(&self, names: &[&str], development: bool) -> Result<()> {
        for key in self.values.keys() {
            if !names.contains(&key.as_str()) {
                return Err(format!("unsupported option {key}"));
            }
        }
        if self.development && !development {
            return Err("--development is only a setup/demo option".into());
        }
        Ok(())
    }
    fn context(&self) -> &[u8] {
        self.values
            .get("--context")
            .map(String::as_bytes)
            .unwrap_or(b"")
    }
    fn config(&self) -> Result<Config> {
        let mut config = if self.development {
            Config::development()
        } else {
            Config::default()
        };
        if let Some(rounds) = self.values.get("--rounds") {
            config.rounds = rounds.parse().map_err(|_| "--rounds must be an integer")?;
        }
        config.validate()?;
        Ok(config)
    }
}

fn read(path: impl AsRef<Path>, maximum: usize) -> Result<Vec<u8>> {
    let path = path.as_ref();
    let mut data = Vec::new();
    File::open(path)
        .map_err(|e| format!("{}: {e}", path.display()))?
        .take((maximum + 1) as u64)
        .read_to_end(&mut data)
        .map_err(|e| e.to_string())?;
    if data.len() > maximum {
        return Err(format!("{} exceeds the file size limit", path.display()));
    }
    Ok(data)
}

fn write(path: impl AsRef<Path>, bytes: &[u8]) -> Result<()> {
    let path = path.as_ref();
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|e| format!("{}: {e}", path.display()))?;
    file.write_all(bytes).map_err(|e| e.to_string())
}

fn print_json<T: Serialize>(value: &T) -> Result<()> {
    println!(
        "{}",
        serde_json::to_string_pretty(value).map_err(|e| e.to_string())?
    );
    Ok(())
}

fn parameters(args: &Args) -> Result<PublicParameters> {
    PublicParameters::from_json(&read(args.get("--parameters")?, 16384)?)
}

fn demo(args: &Args) -> Result<()> {
    args.allow(&["--out", "--rounds"], true)?;
    let dir = PathBuf::from(args.get("--out")?);
    let names = [
        "parameters.json",
        "circuit.json",
        "witness.json",
        "proof.leash",
        "report.json",
    ];
    if names.iter().any(|name| dir.join(name).exists()) {
        return Err("demo output files already exist".into());
    }
    let mut builder = CircuitBuilder::new();
    let secret = builder.input(true)?;
    let public = builder.public_input(false)?;
    let xor = builder.xor(secret, public)?;
    let inverse = builder.not(public)?;
    let output = builder.and(xor, inverse)?;
    builder.pin_public(output, true)?;
    let (instance, witness) = builder.finish()?;
    let pp = setup(args.config()?)?;
    let plan = plan_binary(&instance, &pp.config)?;
    let started = Instant::now();
    let proof = prove_with_context(&pp, &instance, &witness, b"leash/example/v1")?;
    let prove_ms = started.elapsed().as_secs_f64() * 1000.0;
    let bytes = proof.to_bytes()?;
    let decoded = Proof::from_bytes(&bytes)?;
    let started = Instant::now();
    let verified = verify_with_context(&pp, &instance, &decoded, b"leash/example/v1")?;
    let verify_ms = started.elapsed().as_secs_f64() * 1000.0;
    #[derive(Serialize)]
    struct Report<'a> {
        fixture: &'static str,
        context: &'static str,
        prove_ms: f64,
        verify_ms: f64,
        plan: &'a leash::ParameterPlan,
        verification: &'a leash::VerificationReport,
    }
    let report = Report {
        fixture: "synthetic AND/XOR/NOT circuit",
        context: "leash/example/v1",
        prove_ms,
        verify_ms,
        plan: &plan,
        verification: &verified,
    };
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    write(dir.join(names[0]), &pp.to_json()?)?;
    write(dir.join(names[1]), &instance.to_json()?)?;
    write(dir.join(names[2]), &witness.to_json()?)?;
    write(dir.join(names[3]), &bytes)?;
    write(
        dir.join(names[4]),
        &serde_json::to_vec_pretty(&report).map_err(|e| e.to_string())?,
    )?;
    print_json(&report)
}

fn run(args: Args) -> Result<()> {
    match args.command.as_str() {
        "help" | "--help" | "-h" => {
            println!("{HELP}");
            Ok(())
        }
        "demo" => demo(&args),
        "setup" => {
            args.allow(&["--out", "--rounds"], true)?;
            let pp = setup(args.config()?)?;
            write(args.get("--out")?, &pp.to_json()?)?;
            print_json(&pp)
        }
        "plan" => {
            args.allow(&["--parameters", "--circuit"], false)?;
            let pp = parameters(&args)?;
            let instance = BinaryR1cs::from_json(&read(args.get("--circuit")?, JSON_LIMIT)?)?;
            print_json(&plan_binary(&instance, &pp.config)?)
        }
        "prove" | "prove-relation" => {
            let relation_mode = args.command == "prove-relation";
            let statement_flag = if relation_mode {
                "--relation"
            } else {
                "--circuit"
            };
            args.allow(
                &[
                    "--parameters",
                    statement_flag,
                    "--witness",
                    "--out",
                    "--context",
                ],
                false,
            )?;
            let pp = parameters(&args)?;
            let statement = read(args.get(statement_flag)?, JSON_LIMIT)?;
            let witness = read(args.get("--witness")?, JSON_LIMIT)?;
            let start = Instant::now();
            let proof = if relation_mode {
                let relation: Relation =
                    serde_json::from_slice(&statement).map_err(|e| e.to_string())?;
                let witness: Witness =
                    serde_json::from_slice(&witness).map_err(|e| e.to_string())?;
                prove_relation_with_context(&pp, &relation, &witness, args.context())?
            } else {
                prove_with_context(
                    &pp,
                    &BinaryR1cs::from_json(&statement)?,
                    &Assignment::from_json(&witness)?,
                    args.context(),
                )?
            };
            let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;
            let bytes = proof.to_bytes()?;
            write(args.get("--out")?, &bytes)?;
            print_json(
                &serde_json::json!({"proof_bytes":bytes.len(), "prove_ms":elapsed_ms,
                "rounds":proof.rounds.len(), "attempt":proof.attempt, "security_level":"not certified"}),
            )
        }
        "verify" | "verify-relation" => {
            let relation_mode = args.command == "verify-relation";
            let statement_flag = if relation_mode {
                "--relation"
            } else {
                "--circuit"
            };
            args.allow(
                &["--parameters", statement_flag, "--proof", "--context"],
                false,
            )?;
            let pp = parameters(&args)?;
            let statement = read(args.get(statement_flag)?, JSON_LIMIT)?;
            let proof = Proof::from_bytes(&read(args.get("--proof")?, MAX_PROOF_BYTES)?)?;
            let report = if relation_mode {
                let relation: Relation =
                    serde_json::from_slice(&statement).map_err(|e| e.to_string())?;
                verify_relation_with_context(&pp, &relation, &proof, args.context())?
            } else {
                verify_with_context(
                    &pp,
                    &BinaryR1cs::from_json(&statement)?,
                    &proof,
                    args.context(),
                )?
            };
            print_json(&report)
        }
        _ => Err(format!("unknown command {}\n{HELP}", args.command)),
    }
}

fn main() -> ExitCode {
    match Args::parse().and_then(run) {
        Ok(()) => ExitCode::SUCCESS,
        Err(message) => {
            eprintln!("LEASH: {message}");
            ExitCode::from(2)
        }
    }
}
