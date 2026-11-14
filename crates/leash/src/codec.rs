use crate::ordinary::RoundMessage;
use crate::pipeline::{Proof, ProofKind, VERSION};
use leash_core::{centered, residue, Poly, Result, D, Q};
use leash_frontend::SourceMessage;

/// Maximum accepted encoded proof size, including its terminal opening.
pub const MAX_PROOF_BYTES: usize = 64 * 1024 * 1024;
const MAGIC: &[u8; 8] = b"LEASHR01";
// Independent decoded-element budget: compression must not increase the
// accepted polynomial count. This is a count limit, not a peak-memory estimate.
const MAX_POLYS: usize = MAX_PROOF_BYTES / (D * 4);

struct Writer {
    bytes: Vec<u8>,
    polys: usize,
}
impl Writer {
    fn bytes(&mut self, data: &[u8]) -> Result<()> {
        if self
            .bytes
            .len()
            .checked_add(data.len())
            .ok_or("encoding length overflow")?
            > MAX_PROOF_BYTES
        {
            return Err("proof exceeds transport size limit".into());
        }
        self.bytes.extend_from_slice(data);
        Ok(())
    }
    fn count(&mut self, count: usize, maximum: usize) -> Result<()> {
        if count > maximum {
            return Err("encoded field exceeds element limit".into());
        }
        self.bytes(
            &u32::try_from(count)
                .map_err(|_| "encoded count overflows u32")?
                .to_le_bytes(),
        )
    }
    fn poly(&mut self, p: &Poly) -> Result<()> {
        p.validate()?;
        if self.polys >= MAX_POLYS {
            return Err("decoded polynomial count limit exceeded".into());
        }
        let mut values = [0u32; D];
        let mut largest = 0u32;
        for (value, &coefficient) in values.iter_mut().zip(&p.0) {
            let c = centered(coefficient);
            *value = if c >= 0 {
                (2 * c) as u32
            } else {
                (-2 * c - 1) as u32
            };
            largest = largest.max(*value);
        }
        let width = (u32::BITS - largest.leading_zeros()) as u8;
        self.bytes(&[width])?;
        let mut payload = [0u8; D * 4];
        let mut at = 0;
        let mut buffer = 0u64;
        let mut bits = 0usize;
        for value in values {
            buffer |= (value as u64) << bits;
            bits += width as usize;
            while bits >= 8 {
                payload[at] = buffer as u8;
                at += 1;
                buffer >>= 8;
                bits -= 8;
            }
        }
        // D=64 makes every width an exact number of payload bytes.
        debug_assert_eq!(bits, 0);
        debug_assert_eq!(at, 8 * width as usize);
        self.bytes(&payload[..at])?;
        self.polys += 1;
        Ok(())
    }
    fn polys(&mut self, values: &[Poly], maximum: usize) -> Result<()> {
        self.count(values.len(), maximum)?;
        for p in values {
            self.poly(p)?;
        }
        Ok(())
    }
    fn integers(&mut self, values: &[i64], maximum: usize) -> Result<()> {
        self.count(values.len(), maximum)?;
        for n in values {
            self.bytes(&n.to_le_bytes())?;
        }
        Ok(())
    }
}

struct Reader<'a> {
    bytes: &'a [u8],
    at: usize,
    polys: usize,
}
impl<'a> Reader<'a> {
    fn take(&mut self, length: usize) -> Result<&'a [u8]> {
        let end = self
            .at
            .checked_add(length)
            .ok_or("decoding length overflow")?;
        let value = self.bytes.get(self.at..end).ok_or("truncated proof")?;
        self.at = end;
        Ok(value)
    }
    fn u32(&mut self) -> Result<u32> {
        Ok(u32::from_le_bytes(
            self.take(4)?.try_into().map_err(|_| "invalid u32")?,
        ))
    }
    fn digest(&mut self) -> Result<[u8; 32]> {
        self.take(32)?
            .try_into()
            .map_err(|_| "invalid digest".into())
    }
    fn count(&mut self, maximum: usize, bytes_per_element: usize) -> Result<usize> {
        let count = self.u32()? as usize;
        let minimum = count
            .checked_mul(bytes_per_element)
            .ok_or("decoded count overflow")?;
        if count > maximum || minimum > self.bytes.len() - self.at {
            return Err("invalid field count or truncated field".into());
        }
        Ok(count)
    }
    fn poly(&mut self) -> Result<Poly> {
        if self.polys >= MAX_POLYS {
            return Err("decoded polynomial count limit exceeded".into());
        }
        let width = self.take(1)?[0];
        if width > 32 {
            return Err("polynomial width exceeds 32 bits".into());
        }
        let payload = self.take(8 * width as usize)?;
        let mut coefficients = Vec::with_capacity(D);
        let mut at = 0;
        let mut buffer = 0u64;
        let mut bits = 0usize;
        let mask = (1u64 << width) - 1;
        let mut largest = 0u32;
        for _ in 0..D {
            while bits < width as usize {
                buffer |= (payload[at] as u64) << bits;
                at += 1;
                bits += 8;
            }
            let value = (buffer & mask) as u32;
            buffer >>= width;
            bits -= width as usize;
            let c = if value & 1 == 0 {
                (value / 2) as i64
            } else {
                -((value as i64 + 1) / 2)
            };
            let half = (Q / 2) as i64;
            if c < -half || c > half {
                return Err("noncanonical centered coefficient in proof".into());
            }
            largest = largest.max(value);
            coefficients.push(residue(c as i128));
        }
        if width as u32 != u32::BITS - largest.leading_zeros() {
            return Err("nonminimal polynomial width".into());
        }
        debug_assert_eq!(bits, 0);
        debug_assert_eq!(at, payload.len());
        self.polys += 1;
        Ok(Poly(coefficients))
    }
    fn polys(&mut self, maximum: usize) -> Result<Vec<Poly>> {
        let count = self.count(maximum.min(MAX_POLYS - self.polys), 1)?;
        (0..count).map(|_| self.poly()).collect()
    }
    fn integers(&mut self, maximum: usize) -> Result<Vec<i64>> {
        let count = self.count(maximum, 8)?;
        (0..count)
            .map(|_| {
                Ok(i64::from_le_bytes(
                    self.take(8)?.try_into().map_err(|_| "invalid i64")?,
                ))
            })
            .collect()
    }
}

impl Proof {
    /// Canonical transport; no verifier randomness is serialized.
    ///
    /// Every polynomial uses a one-byte minimal centered-zigzag width followed
    /// by 64 values packed LSB-first at that width (exactly 8*width bytes).
    /// All count fields and signed scalar fields remain little-endian.
    pub fn to_bytes(&self) -> Result<Vec<u8>> {
        if self.version != VERSION || self.source.is_some() != (self.kind == ProofKind::BinaryR1cs)
        {
            return Err("unsupported proof version or source kind".into());
        }
        let mut out = Writer {
            bytes: Vec::new(),
            polys: 0,
        };
        out.bytes(MAGIC)?;
        out.bytes(&self.version.to_le_bytes())?;
        out.bytes(&[match self.kind {
            ProofKind::BinaryR1cs => 0,
            ProofKind::QuadraticRelation => 1,
        }])?;
        for hash in [
            &self.parameter_digest,
            &self.statement_digest,
            &self.context_digest,
            &self.nonce,
        ] {
            out.bytes(hash)?;
        }
        out.bytes(&self.attempt.to_le_bytes())?;
        if let Some(source) = &self.source {
            out.polys(&source.commitment, 32)?;
            out.integers(&source.replies, 256)?;
        }
        out.count(self.rounds.len(), 3)?;
        for message in &self.rounds {
            out.polys(&message.u1, 64)?;
            out.integers(&message.projection, 1024)?;
            out.polys(&message.aggregates, 8)?;
            out.polys(&message.u2, 64)?;
        }
        let n = self.opening.first().ok_or("empty terminal opening")?.len();
        if n == 0 || self.opening.iter().any(|block| block.len() != n) {
            return Err("ragged or empty terminal opening".into());
        }
        let count = self
            .opening
            .len()
            .checked_mul(n)
            .ok_or("terminal dimensions overflow")?;
        if count > MAX_POLYS - out.polys {
            return Err("terminal opening exceeds decoded polynomial limit".into());
        }
        out.count(self.opening.len(), MAX_POLYS)?;
        out.count(n, MAX_POLYS)?;
        for p in self.opening.iter().flatten() {
            out.poly(p)?;
        }
        Ok(out.bytes)
    }

    /// Decode with explicit byte/count bounds. Successful decoding is not verification.
    pub fn from_bytes(bytes: &[u8]) -> Result<Self> {
        if bytes.len() > MAX_PROOF_BYTES {
            return Err("proof exceeds transport size limit".into());
        }
        let mut input = Reader {
            bytes,
            at: 0,
            polys: 0,
        };
        if input.take(8)? != MAGIC {
            return Err("incorrect proof magic".into());
        }
        let version = input.u32()?;
        if version != VERSION {
            return Err("unsupported proof version".into());
        }
        let kind = match input.take(1)?[0] {
            0 => ProofKind::BinaryR1cs,
            1 => ProofKind::QuadraticRelation,
            _ => return Err("unknown proof kind".into()),
        };
        let parameter_digest = input.digest()?;
        let statement_digest = input.digest()?;
        let context_digest = input.digest()?;
        let nonce = input.digest()?;
        let attempt = input.u32()?;
        let source = if kind == ProofKind::BinaryR1cs {
            Some(SourceMessage {
                commitment: input.polys(32)?,
                replies: input.integers(256)?,
            })
        } else {
            None
        };
        let rounds_count = input.count(3, 16)?;
        let mut rounds = Vec::with_capacity(rounds_count);
        for _ in 0..rounds_count {
            rounds.push(RoundMessage {
                u1: input.polys(64)?,
                projection: input.integers(1024)?,
                aggregates: input.polys(8)?,
                u2: input.polys(64)?,
            });
        }
        let r = input.count(MAX_POLYS, 0)?;
        let n = input.count(MAX_POLYS, 0)?;
        let count = r.checked_mul(n).ok_or("terminal dimensions overflow")?;
        if r == 0 || n == 0 || count > MAX_POLYS - input.polys || count > bytes.len() - input.at {
            return Err("invalid terminal shape or truncated opening".into());
        }
        let mut opening = Vec::with_capacity(r);
        for _ in 0..r {
            opening.push((0..n).map(|_| input.poly()).collect::<Result<Vec<_>>>()?);
        }
        if input.at != bytes.len() {
            return Err("trailing bytes after terminal opening".into());
        }
        Ok(Proof {
            version,
            kind,
            parameter_digest,
            statement_digest,
            context_digest,
            nonce,
            attempt,
            source,
            rounds,
            opening,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn encode_poly(p: &Poly) -> Vec<u8> {
        let mut writer = Writer {
            bytes: Vec::new(),
            polys: 0,
        };
        writer.poly(p).unwrap();
        writer.bytes
    }
    fn decode_poly(bytes: &[u8]) -> Result<Poly> {
        let mut reader = Reader {
            bytes,
            at: 0,
            polys: 0,
        };
        let p = reader.poly()?;
        if reader.at != bytes.len() {
            return Err("trailing polynomial bytes".into());
        }
        Ok(p)
    }
    // Independently pack raw test values one bit at a time, avoiding the
    // production byte-accumulator implementation.
    fn pack_raw(width: u8, values: &[u32; D]) -> Vec<u8> {
        let mut out = vec![0u8; 1 + 8 * width as usize];
        out[0] = width;
        for (i, &value) in values.iter().enumerate() {
            for bit in 0..width as usize {
                let offset = i * width as usize + bit;
                out[1 + offset / 8] |= (((value >> bit) & 1) as u8) << (offset % 8);
            }
        }
        out
    }
    fn fixture() -> Proof {
        Proof {
            version: VERSION,
            kind: ProofKind::QuadraticRelation,
            parameter_digest: [1; 32],
            statement_digest: [2; 32],
            context_digest: [3; 32],
            nonce: [4; 32],
            attempt: 0,
            source: None,
            rounds: vec![],
            opening: vec![vec![Poly::constant(-1)]],
        }
    }
    #[test]
    fn canonical_roundtrip_and_all_truncations() {
        let proof = fixture();
        let bytes = proof.to_bytes().unwrap();
        assert_eq!(Proof::from_bytes(&bytes).unwrap(), proof);
        for end in 0..bytes.len() {
            assert!(Proof::from_bytes(&bytes[..end]).is_err());
        }
        let mut trailing = bytes.clone();
        trailing.push(0);
        assert!(Proof::from_bytes(&trailing).is_err());
        let poly_offset = bytes.len() - encode_poly(&proof.opening[0][0]).len();
        let mut noncanonical = bytes[..poly_offset].to_vec();
        let mut values = [0u32; D];
        values[0] = Q as u32; // -(Q+1)/2 is outside the centered interval.
        noncanonical.extend(pack_raw(32, &values));
        assert!(Proof::from_bytes(&noncanonical)
            .unwrap_err()
            .contains("centered"));
        let mut oversized = bytes;
        let dimension_offset = poly_offset - 8;
        oversized[dimension_offset..dimension_offset + 4].copy_from_slice(&u32::MAX.to_le_bytes());
        assert!(Proof::from_bytes(&oversized).is_err());
    }

    #[test]
    fn independent_python_known_answer_and_every_width() {
        // Reproduce with Python's arbitrary-precision integer packing:
        // c = [-13,-8,-1,0,1,7,8,13] + [0]*56
        // z = [2*x if x >= 0 else -2*x-1 for x in c]
        // w = max(z).bit_length()
        // print((bytes([w]) + sum(v << (w*i) for i,v in enumerate(z))
        //        .to_bytes(8*w, "little")).hex())
        let p = Poly::from_signed(&[-13, -8, -1, 0, 1, 7, 8, 13]).unwrap();
        let hex: String = encode_poly(&p).iter().map(|b| format!("{b:02x}")).collect();
        assert_eq!(
            hex,
            "05f905201cd40000000000000000000000000000000000000000000000000000000000000000000000"
        );
        assert_eq!(encode_poly(&Poly::zero()), vec![0]);
        assert_eq!(decode_poly(&[0]).unwrap(), Poly::zero());
        for width in 1u8..=32 {
            let maximum = 1u32 << (width - 1);
            let values = std::array::from_fn(|i| {
                if i == D - 1 {
                    maximum
                } else {
                    i as u32 % maximum
                }
            });
            let coefficients: Vec<i64> = values
                .iter()
                .map(|&v| {
                    if v & 1 == 0 {
                        (v / 2) as i64
                    } else {
                        -((v as i64 + 1) / 2)
                    }
                })
                .collect();
            let polynomial = Poly::from_signed(&coefficients).unwrap();
            let encoded = encode_poly(&polynomial);
            assert_eq!(encoded[0], width);
            assert_eq!(encoded.len(), 1 + 8 * width as usize);
            assert_eq!(encoded, pack_raw(width, &values));
            assert_eq!(decode_poly(&encoded).unwrap(), polynomial);
        }
    }

    #[test]
    fn rejects_nonminimal_width_and_noncanonical_centered_integers() {
        let mut values = [0u32; D];
        assert!(decode_poly(&pack_raw(1, &values))
            .unwrap_err()
            .contains("nonminimal"));
        values[0] = 1; // -1 only needs one bit, not two.
        assert!(decode_poly(&pack_raw(2, &values))
            .unwrap_err()
            .contains("nonminimal"));
        values[0] = Q as u32; // Negative out-of-range centered integer.
        assert!(decode_poly(&pack_raw(32, &values))
            .unwrap_err()
            .contains("centered"));
        values[0] = Q as u32 + 1; // Positive out-of-range centered integer.
        assert!(decode_poly(&pack_raw(32, &values))
            .unwrap_err()
            .contains("centered"));
        assert!(decode_poly(&[33]).unwrap_err().contains("width"));
        assert!(decode_poly(&[32]).unwrap_err().contains("truncated"));
        assert!(decode_poly(&[0, 0]).is_err());
    }

    #[test]
    fn maximum_centered_endpoints_roundtrip_without_modular_aliases() {
        let half = (Q / 2) as i64;
        let p = Poly::from_signed(&[half, -half, 0, -1, 1]).unwrap();
        let encoded = encode_poly(&p);
        assert_eq!(encoded[0], 32);
        assert_eq!(encoded.len(), 257);
        assert_eq!(&encoded[1..5], &((Q - 1) as u32).to_le_bytes());
        assert_eq!(&encoded[5..9], &((Q - 2) as u32).to_le_bytes());
        assert_eq!(decode_poly(&encoded).unwrap(), p);
    }

    #[test]
    fn all_polynomial_roles_use_the_same_canonical_format() {
        let mut proof = fixture();
        proof.kind = ProofKind::BinaryR1cs;
        proof.source = Some(SourceMessage {
            commitment: vec![Poly::zero(), Poly::constant(-13)],
            replies: vec![-2, 0, 12],
        });
        proof.rounds = vec![RoundMessage {
            u1: vec![Poly::constant(7)],
            projection: vec![-1, 0, 1],
            aggregates: vec![Poly::constant(-(Q as i64 / 2))],
            u2: vec![Poly::constant(8), Poly::zero()],
        }];
        proof.opening = vec![
            vec![Poly::zero(), Poly::constant(1)],
            vec![Poly::constant(-1), Poly::constant(Q as i64 / 2)],
        ];
        let bytes = proof.to_bytes().unwrap();
        let decoded = Proof::from_bytes(&bytes).unwrap();
        assert_eq!(decoded, proof);
        assert_eq!(decoded.to_bytes().unwrap(), bytes);
        let mut trailing = bytes.clone();
        trailing.push(0);
        assert!(Proof::from_bytes(&trailing).is_err());
        assert!(Proof::from_bytes(&bytes[..bytes.len() - 1]).is_err());
    }

    #[test]
    fn compressed_polynomials_do_not_relax_decoded_count_cap() {
        assert_eq!(MAX_POLYS, 262_144);
        let mut reader = Reader {
            bytes: &[0],
            at: 0,
            polys: MAX_POLYS,
        };
        assert!(reader.poly().unwrap_err().contains("count limit"));
        let mut writer = Writer {
            bytes: Vec::new(),
            polys: MAX_POLYS,
        };
        assert!(writer
            .poly(&Poly::zero())
            .unwrap_err()
            .contains("count limit"));
        let proof = fixture();
        let bytes = proof.to_bytes().unwrap();
        let poly_offset = bytes.len() - encode_poly(&proof.opening[0][0]).len();
        let dimensions = poly_offset - 8;
        let mut oversized = bytes.clone();
        oversized[dimensions..dimensions + 4]
            .copy_from_slice(&((MAX_POLYS + 1) as u32).to_le_bytes());
        assert!(Proof::from_bytes(&oversized).is_err());
        let mut oversized_product = bytes.clone();
        oversized_product[dimensions..dimensions + 4]
            .copy_from_slice(&(MAX_POLYS as u32).to_le_bytes());
        oversized_product[dimensions + 4..dimensions + 8].copy_from_slice(&2u32.to_le_bytes());
        assert!(Proof::from_bytes(&oversized_product).is_err());
        // Minimum one-byte-per-polynomial precheck rejects before allocating
        // an opening even when the individual dimensions and product fit.
        let mut undersized_payload = bytes[..poly_offset].to_vec();
        undersized_payload[dimensions + 4..dimensions + 8].copy_from_slice(&2u32.to_le_bytes());
        undersized_payload.push(0);
        assert!(Proof::from_bytes(&undersized_payload)
            .unwrap_err()
            .contains("truncated"));
    }
}
