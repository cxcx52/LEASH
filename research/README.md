# Research evidence and parameter archive

This directory preserves the mathematical repairs, exact arithmetic searches, internal review notes, and pinned heuristic cost outputs underlying the current ordinary-core parameter examples. It is self-contained for the standard-Python arithmetic runs. SageMath and a clean external Lattice Estimator checkout are needed only to rerun the cost formulas; no third-party source or paper PDFs are bundled.

The smallest recorded ordinary-core encoding bound is **155.1484375 KiB per complete attempt**. The reviewed native binary source interface brings the complete prover-message bound to **157.17578125 KiB** with independent source rows, or **157.265625 KiB** with a 187-bit source fingerprint challenge. These bounds exclude public instance and setup, verifier messages, framing, Fiat–Shamir material, and rejected attempts. They describe specified encodings, not measured proof sizes or concrete 128-bit knowledge security. The mathematical source-to-core interface and its conditional ledger are now specified; a target compiler, practical implementation, and concrete reduction-advantage bounds remain outside this archive.

| Comparable stage | Challenge/fold profile | Inner / outer ranks | Core encoding bound |
|---|---|---:|---:|
| Greedy norm-minimizing path | Filtered cube, T34, Γ²=(21/2)dβ² | 24 / 16 | 194.390625 KiB |
| Joint optimum in the fixed digit domain | Same filtered cube | 24 / 16 | 185.734375 KiB |
| Same-domain joint optimum | Energy ≤104, T30, Γ²=9dβ² | 24 / 16 | 179.6484375 KiB |
| Fixed energy path, screened outer rank | Same bounded-energy family | 24 / 9 | 155.1484375 KiB |

The cube joint path with outer rank 9 has bound 161.234375 KiB. Changing outer rank requires a fresh dimension-matched setup and target relations; this is not a way to trim an existing transcript. Rank 9 is the minimum passing rank in the tested common-outer-rank domain 4,...,16 under the stated five-model threshold rule. The generic, structured-lattice, fit-range, and computational-reduction limitations remain material.

## Start with the reports

- [Main proof-chain assessment, evidence, and contribution scope](notes/critical_path_assessment.md).
- [Joint cube optimization and its exact domain](notes/joint_parameter_search.md).
- [Fair cube/energy comparison and full recomputed norm path](notes/joint_energy_parameter_search.md).
- [Outer-rank comparison, including all boundary ranks](notes/outer_rank_parameter_screen.md).
- [Model definitions, units, and computational-security limits](notes/computational_parameter_screen.md).
- [Native source interface, source rank, and complete communication ledger](notes/binary_frontend_audit.md).
- [Source-only random-point fingerprint and its independent review](proofs/binary_fingerprint_frontend.md), [review](proofs/binary_fingerprint_peer_review.md).
- [Optional scalar/ring aggregation fingerprints](proofs/core_aggregation_fingerprints.md), [first review](proofs/ordinary_power_aggregation_review.md), and [independent certificate review](notes/core_aggregation_fingerprint_peer.md).

The energy family has certified cardinality at least 13936729633962967329980914140531014408519511, operator norm strictly below 30, and squared coefficient norm at most 104. Its Q=128 complete-restart **statistical** expression is below 2^−128; its recorded exponent is approximately 128.69244, compared with 133.78942 for the cube family. Computational extraction losses are additional. Honest completeness and the restart policy are specified separately from the model estimates.

## Mathematical dependencies

| Topic | Main document | Associated checks |
|---|---|---|
| Modular JL and scaling family | [Projection proof](proofs/modular-jl.md), [uniform family](proofs/jl_security_family.md) | `jl_family_checks.py` |
| Cube filtering and exact norm predicate | [Challenge construction](proofs/certified_filtered_challenges.md), [certified Fourier fallback](proofs/certified_fourier_predicate.md) | `certified_filtered_challenges_checks.py`, `certified_fourier_predicate.py` |
| Cube fourth moments | [Paired-spectrum and centered conditioning](proofs/filtered_fourth_moment.md) | `filtered_fourth_moment_checks.py` |
| Energy-ball filtering and general symmetric-law moments | [Exact count, tail, and moment theorem](proofs/fixed_energy_challenge_exploration.md) | `fixed_energy_challenge_checks.py` |
| Full packing, norm caps and payload | [Parameter feasibility](proofs/parameter_feasibility.md) | `parameter_feasibility_checks.py` |
| Anchor extraction and controlled composition | [Finite anchor theorem](proofs/computational_binding_review.md), [universal extractor](proofs/composition_repair.md) | `gated_row_checks.py` |
| Current computational loss | [Bad-mass-weighted cubic-root refinement](proofs/computational_loss_refinement.md) | `computational_loss_refinement_checks.py` |
| Verifier-visible complete restarts | [Bounded restart theorem](proofs/bounded_restart_repair.md) | `bounded_restart_checks.py` |
| Source relation and lifting | [Affine R1CS repair](proofs/r1cs_repair.md) | `r1cs_checks.py` |
| Native binary source and aligned target | [Complete native interface](proofs/native_binary_source_interface.md) | `native_binary_source_checks.py`, `binary_frontend_ledger.py` |
| Source-only challenge compression | [Random-point fingerprint](proofs/binary_fingerprint_frontend.md) | `binary_fingerprint_checks.py`, `binary_fingerprint_peer_checks.py` |
| Ordinary aggregation challenge replacement | [Field/CRT fingerprint theorem](proofs/core_aggregation_fingerprints.md) | `ordinary_power_aggregation_checks.py`, `core_aggregation_fingerprint_peer_checks.py` |

The current ordinary-layer computational loss can be bounded by

    sqrt(eta_0) + (2 eta_h + 2 r eta_y + eta_g)^(1/3) + eta_E,

with a sharper expression in the refinement document. Each eta is the success probability of a complete specified collision reduction, including its anchor, nested extraction, initialization, and runtime. It is not a per-query binding probability. The earlier fourth-root bounds remain valid historical upper bounds; the refinement is the stronger current result. Neither expression supplies numerical advantages from heuristic model exponents by itself.

Internal review notes accompany the main constructions. They are development evidence, not external peer-review acceptance or independent security certification. Optional [architecture limits](proofs/architecture_limits.md), [Boolean bridge toy ledger](proofs/boolean_bridge_toy.md), and [backend propositions](notes/backend_directions.md) retain their own stated scope and standalone checkers.

## Native source supplement and its limits

The native source packs one binary coordinate into each ring coefficient. Its corrected target includes coefficient-level public pins, the all-coefficient-ones bitness term, explicit conjugates, eight separately aligned blocks, and padding-zero equations. At the current dimensions it needs no new witness coordinates beyond the recorded first core shape. This is a different relation from the older affine frontend in the archive.

The one source commitment has a separate MSIS role with squared collision radius at most `n+3k=2^27`. In the recorded five-model screen, the minimum source rank is 5 against the old cube thresholds and 6 against the stronger current energy thresholds; the complete ledger uses rank 6. This is a heuristic cost screen, not a concrete advantage bound. The complete extraction statement additionally loses `sqrt(eta_src)` for its full two-suffix source collision experiment, including nested core extraction and runtime.

| One complete attempt | Independent source rows | Source random-point fingerprint |
|---|---:|---:|
| Source scalar rows | 160 | 187 |
| Fresh source challenge | 1.875 GiB | 187 bits, or 24 padded bytes |
| Source replies, packed even-integer indices | 540 bytes | 632 padded bytes |
| Source commitment at rank 6 | 1,536 bytes | 1,536 bytes |
| Core plus source prover messages | 160,948 bytes = 157.17578125 KiB | 161,040 bytes = 157.265625 KiB |
| Source plus core verifier messages, explicit baseline encoding | 622,004,598,400 bits | 605,898,476,411 bits |

The fingerprint uses the classic random-evaluation root bound in `GF(2^187)`, with a certified public irreducible polynomial. Its fixed-opening error is `(3k-1)/2^187<2^-160`. It retains the source binding chronology and integer parity checks. It replaces only the source challenge distribution; 27 additional scalar target rows add 5,184 core aggregation challenge bits under the current independent core aggregation.

The core JL matrices alone still occupy **67.53559875 GiB** in the explicit two-bit-entry encoding per attempt. Their Shannon entropy and the expected length of the specified prefix code are **50.65169907 GiB**, which is not a fixed worst-case wire bound. The baseline source-plus-core verifier total is about **72.41086550 GiB**; the source fingerprint reduces it to about **70.53586613 GiB**, before framing, extra public pins, setup, and rejected attempts. Dense coefficient processing remains substantial. No short-total-challenge, succinct-verifier, PRG, or Fiat–Shamir claim follows from this source-only change.

These counts use no additional public pins beyond the constant wire and no general `H` rows. Extra direct public pins add 192 first-layer scalar-aggregation bits each under the baseline law. Changing the source relation requires updating the explicit target and ledger. The source fingerprint changes neither the ordinary core's existing norm path nor its complete-restart statistical upper bound; computational losses remain additional.

## Optional ordinary aggregation fingerprints

A separate reviewed variant replaces each core layer's six independent scalar aggregation rows by coordinates of powers of a fresh point in `GF(q^6)`, and its ring coefficients by powers of a fresh point in `R_q`. The public degree-six polynomial is `Z^6+Z+2`; exact Frobenius and Bezout certificates are archived. The scalar point follows the projection reply, and the ring point follows the six aggregate replies. These are changed challenge laws with new cancellation bounds, not lossless encodings of the independent rows.

With the source fingerprint, the seven scalar polynomial degrees sum to 134,225,082 and the ring degrees sum to 407. The exact Q=128 statistical budget is

    128 [198/N_min + 7*2^-164 + 134225082/q^6 + 407/q^32 + 100663295/2^187] < 2^-128.

Its recorded exponent is approximately 128.6924434363. The prover-message bound remains **161,040 bytes**. The two aggregation challenges together now use 15,680 bits across seven layers. Including the unchanged two-bit JL encoding, final folding challenges, and source fingerprint, verifier messages total **580,126,427,131 bits**, about **67.5356047148 GiB**. This remains a large interactive verifier transcript.

The new distribution must be used in every complete collision experiment, and its coefficient-generation work must be included in each reduction's runtime. The norm path and message dimensions remain applicable, but the old sampler advantages are not automatically advantages for the new law. This variant does not establish Fiat–Shamir, a succinct verifier, or a stronger SNARK. The independent-row baseline records above remain unchanged for comparison.

## Fast arithmetic reproduction

Use Python 3.10 or newer and run commands **from this `research/` directory**. These scripts use the standard library and do not require installing the package or Sage.

```sh
python -c "from pathlib import Path; Path('work').mkdir(exist_ok=True)"
python scripts/verify_archive.py
python scripts/joint_parameter_search.py
python scripts/joint_energy_parameter_search.py
```

The second search consumes `work/joint_parameter_search.json`, so run the cube search first. The scripts rebuild the exact norm/padding/radius paths and count/moment/statistical certificates. Expected totals are 1,521,536 bits for the cube joint optimum and 1,471,680 bits for the energy joint optimum. Search timings and source-file hashes may differ across platforms; the exact parameter paths and payload totals are the reproducible mathematical output.

`work/` is ignored. The committed reference JSON files are in [notes/parameter-results](notes/parameter-results). Reruns do not overwrite them. Additional proof checkers may be run individually; the fast path above deliberately does not rerun every historical exhaustive or performance check.

After generating the energy path, reproduce the native-source arithmetic with:

```sh
python scripts/native_binary_source_checks.py
python scripts/binary_fingerprint_checks.py
python scripts/binary_fingerprint_peer_checks.py
python scripts/binary_frontend_ledger.py --output work/binary_frontend_arithmetic.json
python scripts/binary_frontend_ledger.py --output work/binary_frontend_peer_rerun.json
python scripts/native_frontend_ledger_peer_checks.py
```

The independent finite-field checker uses a different multiplication implementation and checks the complete small native parity interface. Its separately recorded Sage irreducibility cross-check is described in the peer review; the standard-Python run verifies the original exact Frobenius certificate without Sage. None of these checks executes a prover or a lattice solver.

Then reproduce the optional ordinary aggregation checks with standard Python:

```sh
python -c "import shutil; shutil.copyfile('notes/parameter-results/core_aggregation_field_certificate.json','work/core_aggregation_field_certificate.json')"
python scripts/core_aggregation_fingerprint_peer_checks.py
python scripts/ordinary_power_aggregation_checks.py
```

The peer checker independently replays the saved degree-six field certificate, including its Bezout identities and the modulus's CRT degree, using schoolbook polynomial arithmetic. To regenerate that public certificate independently with Sage, use `sage -python scripts/core_aggregation_field_certificate.py` before the peer checker. This command performs field arithmetic only and needs no estimator checkout.

## Pinned Sage cost reproduction

The recorded model runs used SageMath 10.9 and an unmodified checkout of [Lattice Estimator](https://github.com/malb/lattice-estimator) at commit

    53da5982597709ba0fdf94ea37a84d822310fd84.

Obtain that external checkout separately and set `ESTIMATOR` to its location. All model-mode drivers require `--estimator` explicitly and verify the exact commit and absence of tracked modifications. They call the Euclidean SIS cost routine and cost models only. They do not invoke BKZ, sieving, a lattice solver, challenge sampling, or a cryptographic prover.

For fresh model outputs, keep this order so every recorded raw input hash matches its generated path:

```sh
python -c "from pathlib import Path; Path('work').mkdir(exist_ok=True)"
python scripts/joint_parameter_search.py
sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile centered-fourth --path-input work/joint_parameter_search.json --output work/joint_parameter_model_screen.json
python scripts/joint_energy_parameter_search.py
sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile bounded-energy --path-input work/joint_energy_parameter_search.json --output work/joint_energy_model_screen.json
sage -python scripts/outer_rank_parameter_screen.py --estimator "$ESTIMATOR" --output work/outer_rank_parameter_screen.json
sage -python scripts/binary_frontend_ledger.py --models --estimator "$ESTIMATOR" --output work/binary_frontend_ledger.json
```

The outer-rank wrapper reads both regenerated path files and their matching model files from `work/`. It checks 14 outer roles for each common rank 4,...,16 on both fixed paths, preserves their seven inner roles, and compares unrounded model-specific minima. It does not redo the joint digit search at every outer rank, because outer row counts do not change the witnessed packing dimensions or norm caps in this model.

The source model driver then reads the energy path and the outer-rank result. It screens source ranks 1,...,16 at the native commitment's own column count and collision radius. This additional source role is not one of the 21 ordinary-core matrix roles. Its archived model output is [binary_frontend_ledger.json](notes/parameter-results/binary_frontend_ledger.json); the plain-Python [arithmetic output](notes/parameter-results/binary_frontend_arithmetic.json) contains the same arithmetic ledger without model calls.

To inspect the archived five-model greedy rank-24 baseline, use [centered-fourth.json](notes/parameter-results/centered-fourth.json). A fresh greedy run can be obtained with:

```sh
sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile centered-fourth --ranks 24 --output work/greedy-centered-fourth.json
```

## Archived byte hashes and provenance

The decisive original records are:

- [Greedy parameter/model profiles](notes/parameter-results/centered-fourth.json).
- [Cube joint path](notes/parameter-results/joint-cube.json) and [matching model output](notes/parameter-results/joint-cube-models.json).
- [Energy joint path](notes/parameter-results/joint-energy.json) and [matching model output](notes/parameter-results/joint-energy-models.json).
- [Outer-rank results](notes/parameter-results/outer-ranks.json).
- [Native source exact checks](notes/parameter-results/native_binary_source_checks.json), [fingerprint certificate](notes/parameter-results/binary_fingerprint_checks.json), and [independent field/parity checks](notes/parameter-results/binary_fingerprint_peer_checks.json).
- [Native source and verifier ledger](notes/parameter-results/binary_frontend_ledger.json) and [independent wire-count checks](notes/parameter-results/native_frontend_ledger_peer_checks.json).
- [Ordinary aggregation exact budgets](notes/parameter-results/ordinary_power_aggregation_checks.json), [degree-six field certificate](notes/parameter-results/core_aggregation_field_certificate.json), and [independent certificate checks](notes/parameter-results/core_aggregation_fingerprint_peer_checks.json).
- [Source/archive hash manifest](notes/parameter-results/archive-manifest.json).

All archived original JSON files are byte-for-byte copies. In particular, `path_input_sha256` and the outer wrapper's prior-model hashes authenticate the original raw bytes, including their original line endings. The local `.gitattributes` marks result JSON as `-text` to prevent Git line-ending conversion and fixes authored Python/Markdown files to LF for stable archive hashes. Do not reformat these JSON files and then expect their historical cross-file hashes to remain valid.

Authored proofs and scripts were copied with portable references, explicit external-estimator arguments, and normalized text line endings. The manifest records both original and archived hashes for those files and identifies editorial changes. Historical `source_hashes` inside the untouched JSON describe the files at the original run, not a claim that every archived proof has the same bytes. Later cross-references to the cubic-root refinement do not alter the saved numerical input, and archiving these files does not re-prove the theorems or security.

If using archived inputs for a cost-only rerun, copy their raw bytes to the corresponding `work/` names and keep each path paired with its matching model file. For example:

```sh
python -c "from pathlib import Path; import shutil; p=Path('notes/parameter-results'); w=Path('work'); w.mkdir(exist_ok=True); pairs={'joint-cube.json':'joint_parameter_search.json','joint-cube-models.json':'joint_parameter_model_screen.json','joint-energy.json':'joint_energy_parameter_search.json','joint-energy-models.json':'joint_energy_model_screen.json'}; [shutil.copyfile(p/a,w/b) for a,b in pairs.items()]"
```

A newly generated path JSON has new timing and provenance bytes even when its mathematics matches an archived path. Generate its matching cost output before invoking the outer wrapper; do not mix it with an old model record whose raw path hash differs.

To rerun only the native source model against archived upstream model outputs, also copy `notes/parameter-results/outer-ranks.json` byte-for-byte to `work/outer_rank_parameter_screen.json`. The source record stores hashes of both the energy path and its preceding outer-rank result. The supplement preserves the original 75 archive entries unchanged and appends its own text/source hashes and untouched JSON bytes. Historical review hashes continue to identify the original reviewed source versions, including the earlier baseline ledger before the separate fingerprint option was marked reviewed.

The archive contains no third-party PDFs or estimator source, no account credentials, and no machine-specific user-directory paths. Its mathematical bounds, finite-domain optimization, and heuristic model outputs remain explicitly separated.
