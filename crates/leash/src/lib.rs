//! Callable binary-circuit frontend and ordinary recursive lattice backend.
//!
//! This research implementation uses a seed-expanded CRS and SHAKE Fiat--Shamir.
//! The archived interactive theorems do not certify this compiler's ROM/QROM
//! security, and the protocol is not zero knowledge.

mod codec;
pub mod ordinary;
mod pipeline;

pub use codec::MAX_PROOF_BYTES;
pub use leash_core as algebra;
pub use leash_frontend as frontend;
pub use pipeline::{
    plan_binary, plan_relation, prove, prove_relation, prove_relation_with_context,
    prove_with_context, setup, verify, verify_relation, verify_relation_with_context,
    verify_with_context, Config, LayerPlan, ParameterPlan, Proof, ProofKind, PublicParameters,
    VerificationReport,
};
