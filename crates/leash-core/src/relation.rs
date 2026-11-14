use crate::{dot, Poly, Result};
use serde::{Deserialize, Serialize};

pub const MAX_WITNESS_POLYS: usize = 1 << 20;
pub const MAX_CONSTRAINTS: usize = 1 << 20;
pub const MAX_TERMS: usize = 1 << 22;
pub type Witness = Vec<Vec<Poly>>;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LinearTerm {
    pub block: usize,
    pub position: usize,
    pub coefficient: Poly,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct QuadraticTerm {
    pub left: usize,
    pub right: usize,
    pub coefficient: Poly,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Constraint {
    pub quadratic: Vec<QuadraticTerm>,
    pub linear: Vec<LinearTerm>,
    pub constant: Poly,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Relation {
    pub r: usize,
    pub n: usize,
    pub bound_squared: u128,
    pub full: Vec<Constraint>,
    pub scalar: Vec<Constraint>,
}

fn shape_size(r: usize, n: usize) -> Result<usize> {
    if r == 0 || n == 0 {
        return Err("relation dimensions must be positive".into());
    }
    let size = r.checked_mul(n).ok_or("relation dimension overflow")?;
    if size > MAX_WITNESS_POLYS {
        return Err("witness polynomial limit exceeded".into());
    }
    Ok(size)
}

impl Constraint {
    fn validate_at(&self, r: usize, n: usize) -> Result<()> {
        self.constant.validate()?;
        let size = self
            .linear
            .len()
            .checked_add(self.quadratic.len())
            .ok_or("constraint size overflow")?;
        if size > MAX_TERMS {
            return Err("constraint term limit exceeded".into());
        }
        for term in &self.linear {
            if term.block >= r || term.position >= n {
                return Err("linear coordinate out of bounds".into());
            }
            term.coefficient.validate()?;
        }
        for term in &self.quadratic {
            if term.left >= r || term.right >= r {
                return Err("quadratic block out of bounds".into());
            }
            term.coefficient.validate()?;
        }
        Ok(())
    }
    fn evaluate_validated(&self, witness: &Witness) -> Poly {
        let mut out = self.constant.clone();
        for term in &self.linear {
            out = out.add(&term.coefficient.mul(&witness[term.block][term.position]));
        }
        for term in &self.quadratic {
            out = out.add(
                &term
                    .coefficient
                    .mul(&dot(&witness[term.left], &witness[term.right])),
            );
        }
        out
    }
    pub fn evaluate(&self, witness: &Witness) -> Result<Poly> {
        let n = witness.first().ok_or("empty witness")?.len();
        shape_size(witness.len(), n)?;
        for block in witness {
            if block.len() != n {
                return Err("ragged witness".into());
            }
            for p in block {
                p.validate()?;
            }
        }
        self.validate_at(witness.len(), n)?;
        Ok(self.evaluate_validated(witness))
    }
}

impl Relation {
    pub fn validate(&self) -> Result<()> {
        shape_size(self.r, self.n)?;
        let count = self
            .full
            .len()
            .checked_add(self.scalar.len())
            .ok_or("constraint count overflow")?;
        if count > MAX_CONSTRAINTS {
            return Err("constraint count limit exceeded".into());
        }
        let mut terms = 0usize;
        for c in self.full.iter().chain(&self.scalar) {
            terms = terms
                .checked_add(c.linear.len())
                .and_then(|t| t.checked_add(c.quadratic.len()))
                .ok_or("relation term count overflow")?;
            if terms > MAX_TERMS {
                return Err("relation term limit exceeded".into());
            }
            c.validate_at(self.r, self.n)?;
        }
        Ok(())
    }
    pub fn check_shape(&self, witness: &Witness) -> Result<()> {
        shape_size(self.r, self.n)?;
        if witness.len() != self.r {
            return Err("witness block count mismatch".into());
        }
        for block in witness {
            if block.len() != self.n {
                return Err("witness block length mismatch".into());
            }
            for p in block {
                p.validate()?;
            }
        }
        Ok(())
    }
    /// Check the closed norm cap and each declared equation. Quadratic terms
    /// are counted exactly once, including off-diagonal block pairs.
    pub fn check(&self, witness: &Witness) -> Result<()> {
        self.validate()?;
        self.check_shape(witness)?;
        if witness_norm_squared(witness) > self.bound_squared {
            return Err("witness exceeds squared norm bound".into());
        }
        for (i, c) in self.full.iter().enumerate() {
            if c.evaluate_validated(witness).0.iter().any(|x| *x != 0) {
                return Err(format!("full constraint {i} failed"));
            }
        }
        for (i, c) in self.scalar.iter().enumerate() {
            if c.evaluate_validated(witness).0[0] != 0 {
                return Err(format!("scalar constraint {i} failed"));
            }
        }
        Ok(())
    }
}

/// Centered coefficient norm; malformed internal polynomials panic.
pub fn witness_norm_squared(witness: &Witness) -> u128 {
    witness.iter().flatten().fold(0u128, |sum, p| {
        sum.checked_add(p.norm_squared())
            .expect("witness norm overflow")
    })
}
