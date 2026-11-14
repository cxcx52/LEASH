use crate::{dot, Poly, Result, D, Q};
use serde::Serialize;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256, Shake256Reader,
};

fn frame(h: &mut Shake256, bytes: &[u8]) {
    h.update(
        &u64::try_from(bytes.len())
            .expect("frame length overflow")
            .to_le_bytes(),
    );
    h.update(bytes);
}

/// Deterministic domain-separated SHAKE256 stream. Uniform and ternary methods
/// remove sampling bias; their cryptographic interpretation still relies on
/// the hash/seed model, not an information-theoretic source of fresh entropy.
pub struct Xof {
    reader: Shake256Reader,
}
impl Xof {
    pub fn new(seed: &[u8], domain: &[u8]) -> Self {
        let mut h = Shake256::default();
        h.update(b"LEASH-XOF-v1\0");
        frame(&mut h, domain);
        frame(&mut h, seed);
        Self {
            reader: h.finalize_xof(),
        }
    }
    fn byte(&mut self) -> u8 {
        let mut b = [0u8; 1];
        self.reader.read(&mut b);
        b[0]
    }
    /// Unbiased rejection sampling, for 1 <= modulus <= u64::MAX.
    pub fn uniform(&mut self, modulus: u64) -> u64 {
        assert!(modulus > 0, "zero sampling modulus");
        let range = 1u128 << 64;
        let cutoff = range - range % (modulus as u128);
        loop {
            let mut bytes = [0u8; 8];
            self.reader.read(&mut bytes);
            let x = u64::from_le_bytes(bytes);
            if (x as u128) < cutoff {
                return x % modulus;
            }
        }
    }
    pub fn bit(&mut self) -> bool {
        self.byte() & 1 != 0
    }
    /// One byte per entry; two independent bits give the exact chi weights.
    pub fn ternary(&mut self) -> i64 {
        let b = self.byte();
        (b & 1) as i64 - ((b >> 1) & 1) as i64
    }
    pub fn poly(&mut self) -> Poly {
        Poly((0..D).map(|_| self.uniform(Q)).collect())
    }
    pub fn challenge_poly(&mut self) -> Poly {
        Poly::from_signed(
            &(0..D)
                .map(|_| self.uniform(5) as i64 - 2)
                .collect::<Vec<_>>(),
        )
        .expect("fixed challenge shape")
    }
}

/// Versioned, length-framed transcript with a monotonically increasing
/// challenge counter and ratcheting after every challenge. This primitive is
/// not itself a Fiat--Shamir security proof.
pub struct Transcript {
    state: Shake256,
    counter: u64,
}
impl Transcript {
    pub fn new(domain: &[u8]) -> Self {
        let mut state = Shake256::default();
        state.update(b"LEASH-TRANSCRIPT-v1\0");
        frame(&mut state, domain);
        Self { state, counter: 0 }
    }
    pub fn absorb(&mut self, label: &[u8], bytes: &[u8]) {
        self.state.update(&[1]);
        frame(&mut self.state, label);
        frame(&mut self.state, bytes);
    }
    pub fn absorb_json<T: Serialize>(&mut self, label: &[u8], value: &T) -> Result<()> {
        let bytes =
            serde_json::to_vec(value).map_err(|e| format!("transcript serialization: {e}"))?;
        self.absorb(label, &bytes);
        Ok(())
    }
    pub fn challenge(&mut self, label: &[u8]) -> Xof {
        let counter = self.counter.to_le_bytes();
        self.counter = self
            .counter
            .checked_add(1)
            .expect("transcript challenge counter exhausted");
        let mut h = self.state.clone();
        h.update(&[2]);
        frame(&mut h, label);
        h.update(&counter);
        let mut seed = [0u8; 64];
        h.finalize_xof().read(&mut seed);
        self.state.update(&[3]);
        frame(&mut self.state, label);
        self.state.update(&counter);
        frame(&mut self.state, &seed);
        Xof::new(&seed, b"LEASH-TRANSCRIPT-CHALLENGE-v1")
    }
}

/// Independent row streams; the requested column count is deliberately absent
/// from the seed so every shorter row is the prefix of the corresponding row.
pub fn matrix_row(seed: &[u8; 32], domain: &[u8], row: usize, columns: usize) -> Vec<Poly> {
    let mut row_seed = Vec::with_capacity(40);
    row_seed.extend_from_slice(seed);
    row_seed.extend_from_slice(
        &u64::try_from(row)
            .expect("matrix row overflow")
            .to_le_bytes(),
    );
    let mut row_domain = b"LEASH-MATRIX-v1\0".to_vec();
    row_domain.extend_from_slice(
        &u64::try_from(domain.len())
            .expect("matrix domain length overflow")
            .to_le_bytes(),
    );
    row_domain.extend_from_slice(domain);
    let mut xof = Xof::new(&row_seed, &row_domain);
    (0..columns).map(|_| xof.poly()).collect()
}

pub fn commit(seed: &[u8; 32], domain: &[u8], rank: usize, opening: &[Poly]) -> Vec<Poly> {
    for p in opening {
        p.assert_valid();
    }
    (0..rank)
        .map(|row| dot(&matrix_row(seed, domain, row, opening.len()), opening))
        .collect()
}
