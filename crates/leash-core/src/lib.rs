//! Arithmetic and transcript primitives for an experimental research library.
//!
//! This crate makes no production security, zero-knowledge, or Fiat--Shamir
//! security claim. Public `Result` boundaries reject invalid ring elements.
//! Infallible arithmetic methods require valid internal polynomials and panic
//! on violation; `Poly`'s public field is not an unchecked arithmetic escape.
//!
//! JSON is a typed interchange encoding, not a universal canonical JSON format.
//! Transcript participants must serialize the same typed values and field order.

mod relation;
mod ring;
mod transcript;

pub use relation::{
    witness_norm_squared, Constraint, LinearTerm, QuadraticTerm, Relation, Witness,
    MAX_CONSTRAINTS, MAX_TERMS, MAX_WITNESS_POLYS,
};
pub use ring::{centered, dot, residue, Poly, D, Q};
pub use transcript::{commit, matrix_row, Transcript, Xof};

pub type Error = String;
pub type Result<T> = std::result::Result<T, Error>;
