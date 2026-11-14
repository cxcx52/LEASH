# Native binary frontend: complete interface and omitted costs

Date: 2026-11-14. Sources are the local 34-page LaBRADOR PDF, Section 6 and
Figure 4 on PDF pages 22–24, `proofs/r1cs_repair.md`, and the independent
`proofs/native_binary_source_interface.md`. This report adds a complete
arithmetic/communication ledger and a separate source-commitment cost screen.
It does not modify the reviewed package or parameter bundle.

**Conclusion.** The current first core shape can support the corrected native
binary frontend with `ell=160`, without new witness slots. That statement
requires the explicit eight-block layout, all source equations, and an
independent source commitment. The previously reported **155.1484375 KiB is
core-only**. A source-rank-6 example adds 2076 bytes of prover messages, giving
157.17578125 KiB per complete attempt under the specified encoding. This is
not total interactive communication or a certified security level. Explicit
independent verifier challenges are much larger, as quantified below.

## 1. Two different binary routes

The current shape uses the native coefficient-packed binary route:

    n_src=k_src=2^25, d=64, q=4294967197,
    D=n_src+3k_src=2^27,
    honest beta^2=2D=2^28, beta=16384.

One source bit occupies one coefficient. The witness contains original
`a,b,c,w` blocks and their conjugates, for `2D` coefficients. There is one
source commitment and one stage of random binary linear aggregation. Its
fixed-opening error is `2^-ell`, hence `2^-160` at `ell=160`.

This is different from the parity specialization of the repaired affine
frontend in `notes/backend_directions.md`. There one source bit is honestly
encoded as one **ring element**, and the witness includes `ell` additional
`d_i` blocks. With the same nominal source dimensions and `ell=160`, it has

    M=n_src+(3+ell)k_src=5,502,926,848 ring elements,

two source commitments, first/second column counts 134,217,728 and
5,368,709,120, and statistical error `2^(1-ell)=2^-159`. At the current slack,
even `(16/3)M>q`; its sufficient lifting condition fails before adding the
positive linear term. Its shape and lifting bound cannot be used with the
current 4,194,400-ring core input. In particular, combining that route's
two-stage proof with the native route's zero-extra-coordinate claim would
be incorrect.

The original nonbinary affine repair over `Z_(2^d+1)` is a third instantiation
with its own encoding and smallest-prime-factor error. It does not supply a
native-binary theorem merely because the documents share an R1CS label.

## 2. Exact native layout and required target equations

The source `n_src` **includes** its constant wire. The other public source
data are the F2 matrices and any public bit values. If an additional constant
coordinate is needed for a different circuit, dimensions, norm, and packing
must be recomputed; it is not a free extra bit at the old worst-case cap.

Each of the eight source/conjugate blocks has 524,288 ring elements. Pad
each separately to `14*37450=524300` rings and split it into 14 vectors.
This gives `r=8*14=112`, vector length 37,450, and 96 total padding rings.
The 96 rings must be constrained to zero. Padding only the tail of the
concatenation would not implement this aligned same-position quadratic
representation. The layout has 6144 padding coefficients, already present
in the current core shape; it adds no new slots or honest norm.

For a source rank `rho_src`, an explicit target has:

- `rho_src+96` full-ring equations: the source commitment rows and padding
  ring-zero constraints;
- `D` scalar conjugation equations on real source coefficients;
- four scalar bitness equations and one scalar product equation;
- `ell=160` scalar response equations;
- one coefficient pin for the constant wire and one for each other public
  bit coordinate;
- the complete norm check at actual extracted squared norm
  `(16/3)*2^28=4294967296/3`.

Thus at source rank 6 the initial core statement has 102 full-ring equations
and `134217894+|P|` constant-term equations, where `P` is the set of additional
public bit pins. All these rows must be constructed in the initial target.
The large scalar count affects verifier work and challenge formation even
though the ordinary aggregation error does not grow with the number of rows.

The pins are coefficient-linear constraints. Copying the affine frontend's
whole-ring `w_0=1` into this packing would also incorrectly fix the other 63
bits sharing that ring element. General F2 linear constraints `Hw=0` can be
included by adding random `eta_i` rows and combining `H^T eta_i` into the
binary coefficient vector `delta_i`. They do not add witness coordinates,
but add `ell*h` explicit verifier bits and coefficient-formation work.

The bitness equations must explicitly use the all-coefficient-ones vector:
if `J=1+X+...+X^(d-1)` and bar denotes `X -> X^-1`, the needed identity is

    ct <u,bar(u)-bar(J)_vector> = sum_j u_j(u_j-1).

Interpreting the printed `1` as scalar ring one does not give this identity;
`u=X` is an immediate algebraic check. The independent interface document
specifies the corrected expression. This is a clarification/repair of the
target relation, not something supplied by a dimension or norm certificate.

The strict lift conditions hold exactly:

    beta_actual^2=4294967296/3 < q,
    6k_src=201326592 < q,
    n_src+3k_src=134217728 < q,
    2 max(n_src,3k_src)=201326592 < q.

With conjugation enforced, each nonnegative integer bitness sum is at most
the full extracted squared norm and below q. Zero modulo q therefore implies
actual bitness. The product check then has integer range `[0,6k_src]` and
proves coefficientwise multiplication. These are zero-congruence arguments;
they are not applications of the affine centered-polynomial lift theorem.

## 3. Source message order, values, and encoding

The order is:

1. Send `t=K_src(a||b||c||w)` before every source aggregation challenge.
2. Receive `ell` independently uniform binary triples `(alpha_i,beta_i,gamma_i)`.
3. Compute `delta_i=Lift(A^T alpha_i+B^T beta_i+C^T gamma_i mod 2)`.
4. Send the integer scalar
   `g_i=<alpha_i,a>+<beta_i,b>+<gamma_i,c>-<delta_i,w>`.
   The verifier checks its specified range and parity.
5. Run the complete core on the resulting fixed target statement, including
   each equation tying `g_i` to the committed original blocks.

The scalar `g_i` is a source message. It is not the core's Gram entry `g_ij`,
the affine frontend's ring-valued `g_i`, or the core's six `b''` ring replies
per layer. Those six core replies are already in the existing core ledger.
Source `g_i` messages precede the first core `u_1`; they cannot be absorbed by
reusing that later commitment as the earlier source commitment.

Each scalar lies in `[-2^25,3*2^25]`. The verifier must interpret it as that
integer, or use the valid centered lift in this concrete instance. Parity
of an arbitrary mod-q representative is wrong: adding odd q changes parity.
The interval has span less than q, so the target congruence and range check
identify a unique integer.

There are `2^26+1` permitted even integers in the interval. Encode the integer
index `(g_i+n_src)/2` using 27 bits and reject unused indices. This gives
4320 bits = 540 bytes for 160 responses. A fixed 32-bit residue encoding gives
5120 bits = 640 bytes, with the same explicit range/parity test. A shifted
integer encoding without exploiting evenness takes 28 bits per scalar.

## 4. The separate source commitment and binding radius

The source CRS role is an independently uniform matrix

    K_src in R_q^(rho_src x 2097152).

It commits only to the original half. Conjugate copies and layout padding
are linked by target equations and are not extra commitment columns. The
matrix is over the odd-q target ring; replacing it by a binary-field linear
map is not the same assumption. Nor is its rank inherited from an inner
rank-24 or outer rank-9 core matrix with different dimensions. Reusing a
correlated CRS would require an independent embedding argument.

The collision experiment runs two independently randomized complete source
suffixes, each including a fresh core-extractor kernel, and keeps only fully
verified target outputs. Both original openings then have binary
coefficients. Their nonzero difference has

    infinity norm <=1,
    squared coefficient Euclidean norm <=D=2^27.

It is nonzero modulo q, since each nonzero coefficient is plus or minus one.
The cost screen conservatively rounds the Euclidean radius up to 11586.
This is a deterministic consequence of verified target bitness. It does not
replace an adversarial opening bound by an honest-prover bound.

Without that semantic lemma, comparing two extracted openings would require
their actual two norm bounds. An expression `beta_honest+beta_extracted`
would be justified only if the first compared opening were known to satisfy
the honest bound. An adversarial source prefix has no such promise. The
canonical-opening proof here compares two verified binary openings instead.

The complete source collision probability is `eta_src`. Canonical accepted
mass gives the explicit source loss `sqrt(eta_src)`. This advantage includes
source initialization, two fresh source suffixes, and two full core extraction
costs. It is not a one-query or per-CRS advantage.

## 5. Separate pinned cost-model screen

`scripts/binary_frontend_ledger.py --models` evaluated source ranks 1–16 with
Sage 10.9 and clean lattice-estimator commit
`53da5982597709ba0fdf94ea37a84d822310fd84`. Scalar dimensions are
`n=64*rho_src`, `m=134217728`; q and the conservative radius are as above.
Only cost functions are called. No matrix, short vector, lattice solver, or
proof transcript is constructed.

| Source rank | Selected dimension | Block | Core classical .292 | Core quantum .265 | Core quantum .257 | MATZOV classical | MATZOV quantum depth-width |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | 1213 | 418 | 122.056 | 110.770 | 107.426 | 147.530441 | 141.395665 |
| 5 | 1517 | 572 | 167.024 | 151.580 | 147.004 | 190.642958 | 180.199598 |
| 6 | 1820 | 735 | 214.620 | 194.775 | 188.895 | 236.346001 | 221.328627 |

Rank 5 is the minimum in the tested domain preserving all five old cube
minimum estimates. It is slightly below the new energy-ball core minima.
Rank 6 is the minimum preserving all five energy-ball core minima. Both
selected ranks are within the estimator's MATZOV fit interval through block
1024. These model values have their respective different cost units and are
not security-bit certifications. The reviewed single-CRT lift calculation
has `floor(11586^2/q)=0`; that particular lift cannot have a nonzero integer
reduced vector. No exhaustive claim about all module-specific methods follows.

At rank 6 the source commitment is 1536 bytes, so the native source adds
`1536+540=2076` bytes. Adding the current energy-ball core gives:

| Encoding | Added source bytes | Source plus core prover payload |
|---|---:|---:|
| Source rank 6, even-interval replies | 2076 | 157.17578125 KiB |
| Source rank 6, 32-bit residue replies | 2176 | 157.2734375 KiB |
| Source rank 5, even-interval replies | 1820 | 156.92578125 KiB |

The rank-5 row preserves the old cube model thresholds, not the slightly
stronger ball minima. Source and core CRT/generic models, their norm
conventions, and computational losses remain separate obligations.

A fully expanded independent rank-6 source CRS has
`6*2097152*64*4=3221225472` bytes = 3 GiB at 32 bits per coefficient. This is
setup/public data rather than prover payload. A seeded representation would
need an explicitly specified distribution and its corresponding setup/MSIS
assumption; it is not literally uniform over all such matrices.

## 6. Explicit verifier communication, including the core

The native source baseline sends `160*(3*2^25)=16106127360` independent
challenge bits, or **1.875 GiB**, when every sampled coefficient is explicitly
transmitted and `H` is absent. Additional general H rows add `160*h` bits.
This is not part of a prover-only payload number.

The core's first JL matrix has `1024*r*n*d` independently ternary entries.
For the current first layer this is 274,884,198,400 entries. A fixed two-bit
encoding costs **64.00146484375 GiB**. Across the entire energy-ball path:

| Layer | r | n | Ternary entries | Two-bit encoding GiB | Entropy / prefix-code expected GiB |
|---|---:|---:|---:|---:|---:|
| 1 | 112 | 37450 | 274884198400 | 64.001464844 | 48.001098633 |
| 2 | 33 | 5795 | 12532776960 | 2.918014526 | 2.188510895 |
| 3 | 15 | 1754 | 1724252160 | 0.401458740 | 0.301094055 |
| 4 | 8 | 877 | 459800576 | 0.107055664 | 0.080291748 |
| 5 | 7 | 440 | 201850880 | 0.046997070 | 0.035247803 |
| 6 | 5 | 440 | 144179200 | 0.033569336 | 0.025177002 |
| 7 | 4 | 443 | 116129792 | 0.027038574 | 0.020278931 |
| Total | | | 290063187968 | 67.535598755 | 50.651699066 |

The ternary probabilities are `1/2,1/4,1/4`, so entropy is exactly 1.5 bits
per entry. The prefix code `0 -> 0`, `+1 -> 10`, `-1 -> 11` attains that
expected length and is losslessly decodable for a known matrix size. Thus
two bits per entry is a convenient fixed-width upper bound, not an
impossibility result. In the model where the verifier privately samples the
fresh independent matrix and must transmit it losslessly without fresh
shared randomness, its entropy bounds the expected length of uniquely
decodable communication. The bound is on that model and distribution.

The current native first target also has 134,217,894 constant-term equations
before extra public pins. With six scalar aggregation rows, this creates
substantial additional challenge arrays. A direct fixed-width ledger at
source rank 6, outer rank 9, `|P|=h=0` gives:

| Core verifier item | Bits | GiB |
|---|---:|---:|
| Seven JL matrices, two bits per entry | 580126375936 | 67.535598755 |
| Scalar aggregation coefficients, 32 bits each | 25771211904 | 3.000163928 |
| Ring aggregation coefficients, 32 bits each | 847872 | 0.000098705 |
| Fold challenges, three bits per coefficient | 35328 | 0.000004113 |
| Total listed core verifier messages | 605898471040 | 70.535865501 |

Adding the independent source challenges gives 72.410865501 GiB per attempt
in this explicit encoding, before framing, public input/CRS transmission,
and any rejected attempts. Each extra direct public pin adds six 32-bit
scalar aggregation coefficients in the first layer. This ledger samples
uniform field elements and encodes their residues; it does not pretend that
every 32-bit string is a uniform mod-q element.

An ideal public random tape or fresh public randomness beacon can change
what the communication model charges. It must reveal the needed fresh coins
at the prescribed point after the relevant commitment. A seed known to the
prover before that commitment does not automatically meet the independence
premise. A short PRG seed replaces the independent distribution by a
computationally pseudorandom one and requires an appropriate hybrid and
advantage accounting. Fiat–Shamir additionally changes adaptivity, grinding,
and extraction obligations and needs its own ROM/QROM analysis. None is an
information-theoretically equivalent compression of the current fresh
independent private sample. These devices also do not by themselves remove
the work of processing the resulting dense coefficients.

## 7. Composition, restarts, and what is now supported

For one corrected native source plus one complete ordinary core, the reviewed
interface gives

    Pr[valid source witness]
      >= epsilon - kappa_core - 2^-160 - nu_core - sqrt(eta_src).

All statements include the public pins and source target rows above. The
actual extracted bound is the relaxed core cap, not the honest cap. Source
checks are honestly deterministic, so the seven-layer honest lower bound
`(479/528)^7>1/2` is preserved.

For Q=128 complete source-plus-core restarts, the existing gate-preserving
wrapper yields the sum over the independently initialized attempts. Its
statistical part is

    128 [sum_i(delta_JL,i+q^-6+q^-32+(r_i+2)/N_i) + 2^-160].

This is the same native statistical budget already checked below `2^-128`
for the energy-ball profile. There is no missing factor two from the native
source. Its computational part must include `sqrt(eta_src,j)` in addition to
each attempt's full core losses. The source collision reduction has two
fresh core kernels, and the relevant runtime includes source matrix work,
challenge generation/processing, and preceding rejected histories. The new
cubic-root improvement for ordinary layers does not erase this source term.

The prover payload figures are per complete attempt. Worst-case transmitted
payload over Q attempts can be Q times that figure; the reviewed honest
success bound gives fewer than two attempts in expectation. Neither measure
is the size of a noninteractive proof with invisible discarded attempts.

An alternative policy may run the source once, then restart only the complete
core on its now fixed target statement. It must retain the source early
checks and use the independently reviewed restarted core as the target
argument. In that different composition the source statistical term occurs
once, with a source collision advantage whose suffix kernels are complete
restarted cores. This is a separately stated policy, not the baseline ledger
used for the existing full-attempt budget.

The preceding native interface closes the mathematical relation-matching
gap left by the old arithmetic shape statement. It does not supply a target
compiler implementation, practical verifier benchmark, end-to-end concrete
MSIS advantage curve, or Fiat–Shamir theorem. Dense statement/challenge work
and the complete extraction losses remain material costs.

## 8. Optional source-only algebraic compression

The parent audit has independently checked a different information-theoretic
source challenge family in `proofs/binary_fingerprint_frontend.md` and
`proofs/binary_fingerprint_peer_review.md`. Its arithmetic is recorded
separately in the ledger:
for residual length `L=3k=100663296`, a uniform field point in `GF(2^187)`
and the coefficient rows of `1,t,...,t^(L-1)` would give root-count allowance

    (L-1)/2^187 < 2^-160.

It uses 187 binary aggregate equations, 187 challenge bits, and 187 scalar
responses, rather than 160 independent rows. The responses take 5984 bits
as 32-bit residues or 5049 bits as even-interval indices. It still adds no
native witness coordinates. It is a separately reviewed variant and is not
substituted into the independent-160-row baseline costs above. It adds 27
constant-term target rows, so the existing six-row core scalar aggregation
also sends 5184 extra explicit bits. At source rank 6, source plus core prover
messages total 1288313 raw bits, or 161040 bytes = 157.265625 KiB with a byte
boundary around the source message block. The source challenge and unchanged
explicit core verifier messages total 605898476411 raw bits, including those
5184 extra core bits. This source-only change does not compress any of the
core JL matrices in Section 6 or prove faster verification.

Reproduction artifacts are `scripts/binary_frontend_ledger.py`,
`work/binary_frontend_arithmetic.json`, and `work/binary_frontend_ledger.json`.
The plain Python mode checks exact dimensions, ranges, lift inequalities,
and challenge ledgers. Optional Sage mode adds the pinned pure cost outputs.
No original package, old baseline, prover, or solver was changed.

Archived original result files are in [parameter-results](parameter-results); the `work/` paths above describe ignored rerun outputs. Historical review hashes identify the original reviewed bytes.
