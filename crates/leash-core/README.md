# leash-core

Fixed arithmetic in `Z_4294967197[X]/(X^64+1)`, sparse relations,
versioned SHAKE256 streams and seed-expanded matrix commitments for the
experimental Leash library. No production, side-channel, zero-knowledge or
Fiat--Shamir security claim is made.

All serialized polynomials contain exactly 64 canonical unsigned coefficients.
Wire structs reject unknown and duplicate fields. Result-returning relation
boundaries validate dimensions, coordinates and coefficients before arithmetic.
Infallible arithmetic methods panic on invalid internal values; callers must
validate directly constructed public `Poly(Vec<u64>)` values. A relation checks
the closed centered squared norm cap, every full polynomial equation, and the
constant coefficient of every scalar equation. The constant term is added;
quadratic terms are counted once.

Typed JSON serialization is deterministic for the protocol structs. Arbitrary
unordered maps passed to `absorb_json` are not made canonical by this crate.
Protocol callers must use identical typed serialization and bind their public
statement, configuration and setup seed before deriving challenges.

## Stream encoding, version 1

`frame(x) = uint64_le(len(x)) || x`. Tags below are literal ASCII bytes; a
displayed `\0` is a single zero byte.

- XOF input: `"LEASH-XOF-v1\0" || frame(domain) || frame(seed)`.
- Transcript initial state: `"LEASH-TRANSCRIPT-v1\0" || frame(domain)`.
- Absorb: append `0x01 || frame(label) || frame(message)`.
- Challenge seed: the first 64 bytes of SHAKE256 of the current state followed
  by `0x02 || frame(label) || uint64_le(counter)`; counter starts at zero.
- Ratchet: append `0x03 || frame(label) || uint64_le(counter) || frame(seed)`
  to the state, then increment the counter. Return the XOF with that seed and
  domain `"LEASH-TRANSCRIPT-CHALLENGE-v1"`.
- Matrix row: XOF seed `setup_seed[32] || uint64_le(row)`, domain
  `"LEASH-MATRIX-v1\0" || frame(caller_domain)`. Column count is absent,
  so prefixes agree. Coefficients are sampled in row, column, coefficient order.

Uniform sampling consumes little-endian 64-bit words and accepts only words
below `2^64 - (2^64 mod modulus)`, then takes the remainder. Modulus zero
panics. A bit consumes one byte and returns its low bit. A ternary value consumes
one byte and subtracts bit 1 from bit 0; ideal bytes give probabilities
`1/4,1/2,1/4` for `-1,0,1`. A challenge polynomial uses 64 uniform samples
modulo 5, each shifted by -2. The interpretation of hash-derived coefficients
still requires the protocol's cryptographic model.

Run `cargo test -p leash-core`. The checked-in known answers are produced by
`python crates/leash-core/tests/python_reference.py`, using only Python's
independent hashlib implementation and arbitrary-precision arithmetic.
