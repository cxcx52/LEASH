use crate::Result;
use serde::{
    de::{Error as DeError, SeqAccess, Visitor},
    Deserialize, Deserializer, Serialize,
};
use std::fmt;

pub const Q: u64 = 4_294_967_197;
pub const D: usize = 64;

/// Canonical residues of an element of `Z_Q[X]/(X^64 + 1)`.
#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
#[serde(transparent)]
pub struct Poly(pub Vec<u64>);

impl<'de> Deserialize<'de> for Poly {
    fn deserialize<T: Deserializer<'de>>(deserializer: T) -> std::result::Result<Self, T::Error> {
        struct PolyVisitor;
        impl<'de> Visitor<'de> for PolyVisitor {
            type Value = Poly;
            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
                write!(f, "exactly {D} canonical residues below {Q}")
            }
            fn visit_seq<A: SeqAccess<'de>>(
                self,
                mut seq: A,
            ) -> std::result::Result<Poly, A::Error> {
                let mut coefficients = Vec::with_capacity(D);
                for _ in 0..D {
                    let x: u64 = seq
                        .next_element()?
                        .ok_or_else(|| A::Error::custom("short polynomial"))?;
                    if x >= Q {
                        return Err(A::Error::custom("noncanonical polynomial coefficient"));
                    }
                    coefficients.push(x);
                }
                if seq.next_element::<serde::de::IgnoredAny>()?.is_some() {
                    return Err(A::Error::custom("long polynomial"));
                }
                Ok(Poly(coefficients))
            }
        }
        deserializer.deserialize_seq(PolyVisitor)
    }
}

pub fn residue(x: i128) -> u64 {
    x.rem_euclid(Q as i128) as u64
}

/// Map a canonical residue into [-(Q-1)/2, (Q-1)/2].
pub fn centered(x: u64) -> i64 {
    assert!(x < Q, "centered requires a canonical residue");
    if x > Q / 2 {
        x as i64 - Q as i64
    } else {
        x as i64
    }
}

impl Poly {
    pub fn zero() -> Self {
        Self(vec![0; D])
    }
    pub fn constant(x: i64) -> Self {
        let mut p = Self::zero();
        p.0[0] = residue(x as i128);
        p
    }
    /// Short coefficient arrays are zero-extended; arrays longer than D fail.
    pub fn from_signed(x: &[i64]) -> Result<Self> {
        if x.len() > D {
            return Err("too many signed polynomial coefficients".into());
        }
        let mut p = Self::zero();
        for (a, b) in p.0.iter_mut().zip(x) {
            *a = residue(*b as i128);
        }
        Ok(p)
    }
    pub fn validate(&self) -> Result<()> {
        if self.0.len() != D {
            return Err("polynomial length must be 64".into());
        }
        if self.0.iter().any(|x| *x >= Q) {
            return Err("polynomial coefficient is not canonical".into());
        }
        Ok(())
    }
    pub(crate) fn assert_valid(&self) {
        self.validate().expect("invalid internal polynomial");
    }
    pub fn add(&self, rhs: &Self) -> Self {
        self.assert_valid();
        rhs.assert_valid();
        Self(
            self.0
                .iter()
                .zip(&rhs.0)
                .map(|(a, b)| (a + b) % Q)
                .collect(),
        )
    }
    pub fn sub(&self, rhs: &Self) -> Self {
        self.assert_valid();
        rhs.assert_valid();
        Self(
            self.0
                .iter()
                .zip(&rhs.0)
                .map(|(a, b)| (a + Q - b) % Q)
                .collect(),
        )
    }
    pub fn mul(&self, rhs: &Self) -> Self {
        self.assert_valid();
        rhs.assert_valid();
        // Each output has at most D summands of magnitude <Q^2. Thus i128
        // accumulation is exact, including the negacyclic wrap sign. Skipping
        // zeros also covers the common zero/constant/monomial constraint case.
        let mut accum = [0i128; D];
        for (i, a) in self.0.iter().enumerate() {
            if *a == 0 {
                continue;
            }
            for (j, b) in rhs.0.iter().enumerate() {
                if *b == 0 {
                    continue;
                }
                let product = (*a as i128) * (*b as i128);
                if i + j < D {
                    accum[i + j] += product;
                } else {
                    accum[i + j - D] -= product;
                }
            }
        }
        Self(accum.into_iter().map(residue).collect())
    }
    pub fn scale(&self, scalar: u64) -> Self {
        self.assert_valid();
        Self(
            self.0
                .iter()
                .map(|x| ((*x as u128) * (scalar as u128) % Q as u128) as u64)
                .collect(),
        )
    }
    pub fn conjugate(&self) -> Self {
        self.assert_valid();
        let mut out = Self::zero();
        out.0[0] = self.0[0];
        for i in 1..D {
            out.0[D - i] = if self.0[i] == 0 { 0 } else { Q - self.0[i] };
        }
        out
    }
    pub fn norm_squared(&self) -> u128 {
        self.assert_valid();
        self.0
            .iter()
            .map(|x| {
                let c = centered(*x) as i128;
                (c * c) as u128
            })
            .sum()
    }
    pub fn coefficient(&self, index: usize) -> i64 {
        self.assert_valid();
        assert!(index < D, "coefficient index out of range");
        centered(self.0[index])
    }
}

pub fn dot(a: &[Poly], b: &[Poly]) -> Poly {
    assert_eq!(a.len(), b.len(), "dot-product lengths differ");
    a.iter()
        .zip(b)
        .fold(Poly::zero(), |acc, (x, y)| acc.add(&x.mul(y)))
}
