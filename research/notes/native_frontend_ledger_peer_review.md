# Native frontend ledger and fingerprint: independent review

Date: 2026-11-14. Verdict: **no mathematical or arithmetic blocker found in the
reviewed baseline ledger or binary-source fingerprint interface**. This review
does not certify the optional lattice cost model or concrete MSIS advantages.
No reviewed author's file, package, or bundle was changed.

Reviewed `scripts/binary_frontend_ledger.py`, arithmetic mode, SHA-256
`b91eec94dc9de91f41f541f2805256729c39e83f1ef6087e0af2a84a915c3490`, and
`proofs/binary_fingerprint_frontend.md`, SHA-256
`193a44a568a53377c62ed3bd64566b2f351eb5d786fa552193d5060d2a262fec`.
The baseline script was rerun into `work/binary_frontend_peer_rerun.json`.
Independent explicit-path sums are in
`scripts/native_frontend_ledger_peer_checks.py` and
`work/native_frontend_ledger_peer_checks.json`; all assertions passed.

## 1. Constraint and challenge counts

With no extra public-coordinate pins and no `H` rows, the native first target has
`D+166` scalar constraints, where `D=2^27`: `D` conjugation coordinates, four
bitness checks, one product check, 160 source scalar rows, and one constant-wire
pin. Its full-ring count is `96+rho_src=102` at source rank 6. Padding is eight
aligned source/conjugate blocks, each with 12 zero ring elements.

Later core inputs have no remaining constant-term constraints and have
`kappa+3+kappa_1+kappa_2=24+3+9+9=45` full-ring equations. This follows from
Figure 3, Lines 15--20: 24 inner commitment equations, three scalar ring
identities, and two nine-row outer commitments. This uses the previously
specified ordinary target relation and retains every outer commitment.

At each layer, six scalar aggregation rows suffice because
`q^5<2^160<=q^6`. For input scalar count `L` and ring count `K`, the baseline
wire formulas are exactly

```text
JL entries:                  1024*r*n*64;
JL two-bit encoding:         2 times that entry count;
scalar aggregation:          6*(L+1024)*32 bits;
ring aggregation:            (K+6)*64*32 bits;
final fold challenges:       r*64*3 bits.
```

The `3/2` bits per ternary entry is both Shannon entropy and the expected length
of the explicit prefix code assigning length 1 to zero and length 2 to each
nonzero sign. It is an expected count, not a worst-case fixed wire bound.

The independently checked seven-layer path is
`(r,n)=(112,37450),(33,5795),(15,1754),(8,877),(7,440),(5,440),(4,443)`.
The sum of each baseline category is:

| Category | Bits |
| --- | ---: |
| JL, two-bit entries | 580126375936 |
| Scalar aggregation | 25771211904 |
| Ring aggregation | 847872 |
| Final fold challenges | 35328 |
| Core verifier total | 605898471040 |
| Independent source challenge | 16106127360 |
| Source plus core verifier total | 622004598400 |

The large verifier total is distinct from prover proof-size accounting. These
figures are raw bit counts before protocol framing and, where needed, byte
padding. Adding `p` further public-coordinate pins adds `192p` first-layer
scalar-aggregation bits in this baseline. They are not included in the table.

## 2. Binary source fingerprint

The formal polynomial `P_e(Y)=sum e_j Y^j` is nonzero for a nonzero binary
residual, under the injective embedding into `GF(2^187)`. Its degree is at most
`3k-1`, giving error `(3k-1)/2^187<2^-160`. The coordinate rows are correlated;
the proof correctly uses the one polynomial's root bound. Zero, repeated roots,
and proper-subfield points are covered without exclusions.

The original source opening remains fixed before the field challenge in the
canonical-mode analysis. Integer lifting and parity apply separately to every
coordinate row, with `delta` combined in `F_2` before lifting. Two source suffixes
use fresh field elements and fresh core kernels. Thus the source MSIS role and
the `sqrt(eta_src)` loss remain valid on the complete experiment law. No change
to a per-CRS or conditional binding assumption is made.

The stated irreducibility argument for
`Z^187+Z^20+Z^2+Z+1` is correct. The author's exact checker was rerun successfully,
including its 3104 small-field evaluation/coordinate pairs. This is a finite-
field arithmetic certificate, not a cryptographic implementation.

Replacing 160 source rows by 187 raises only the first input scalar count to
`D+193`. Under the current independent core aggregation, it adds
`27*6*32=5184` verifier bits. The core still returns **six** `b''` polynomials:
the six aggregation outputs are independent of the input equation count. Ring
aggregation continues to receive `K+6` polynomials. The source witness, aligned
layout, norms, decomposition dimensions, and packed target-witness lengths do
not change. The actual coefficients, verification work, and sampler runtimes
do change and must be regenerated/reaccounted; this is not a transcript rewrite.

The source challenge drops to 187 bits, so the source-plus-core verifier raw
count for this substitution is `605898476411` bits. The baseline ledger file
still labels its optional fingerprint section as arithmetic only and its core
totals use the original 160 rows; those baseline totals must not be presented
as already including the 5184-bit change.

The prover count in the formal note also checks out:
`1270976+6*64*32+187*27=1288313` bits, or 161040 bytes after final byte padding,
which is 157.265625 KiB. It is one complete attempt's prover-message encoding,
excluding verifier traffic, prior rejected attempts, setup, and framing.

## 3. Scope

The reviewed fingerprint changes the source challenge law. It leaves the huge
dense JL challenge family and verifier computation intact, and supplies no
Fiat--Shamir or succinct-verifier theorem. Source and core MSIS advantages still
need their actual initialized reduction costs and norms. The ledger's separate
cost-model section was not rerun or independently endorsed in this review.

Archived original result files are in [parameter-results](parameter-results); the `work/` paths above describe ignored rerun outputs. Historical review hashes identify the original reviewed bytes.

Archive note: this review records the earlier baseline script status. The subsequently reviewed 187-bit variant is separately recorded in [binary_frontend_audit.md](binary_frontend_audit.md) and in the current ledger, including its additional 5,184 core scalar-aggregation bits.
