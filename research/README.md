# Research evidence and parameter archive

This directory preserves the mathematical repairs, exact arithmetic searches, internal review notes, and pinned heuristic cost outputs underlying the current ordinary-core parameter examples. It is self-contained for the standard-Python arithmetic runs. SageMath and a clean external Lattice Estimator checkout are needed only to rerun the cost formulas; no third-party source or paper PDFs are bundled.

The smallest recorded ordinary-core encoding bound is **155.1484375 KiB per complete attempt**. It excludes the source frontend, public instance and setup, verifier messages, framing, Fiat–Shamir material, and rejected attempts. It is an upper bound for a specified encoding, not a measured proof size or a concrete 128-bit knowledge-security claim. This core manifest does not complete the source-to-core interface or its end-to-end communication ledger; those remain separate work items.

| Comparable stage | Challenge/fold profile | Inner / outer ranks | Core encoding bound |
|---|---|---:|---:|
| Greedy norm-minimizing path | Filtered cube, T34, Γ²=(21/2)dβ² | 24 / 16 | 194.390625 KiB |
| Joint optimum in the fixed digit domain | Same filtered cube | 24 / 16 | 185.734375 KiB |
| Same-domain joint optimum | Energy ≤104, T30, Γ²=9dβ² | 24 / 16 | 179.6484375 KiB |
| Fixed energy path, screened outer rank | Same bounded-energy family | 24 / 9 | 155.1484375 KiB |

The cube joint path with outer rank 9 has bound 161.234375 KiB. Changing outer rank requires a fresh dimension-matched setup and target relations; this is not a way to trim an existing transcript. Rank 9 is the minimum passing rank in the tested common-outer-rank domain 4,...,16 under the stated five-model threshold rule. The generic, structured-lattice, fit-range, and computational-reduction limitations remain material.

## Start with the reports

- [Joint cube optimization and its exact domain](notes/joint_parameter_search.md).
- [Fair cube/energy comparison and full recomputed norm path](notes/joint_energy_parameter_search.md).
- [Outer-rank comparison, including all boundary ranks](notes/outer_rank_parameter_screen.md).
- [Model definitions, units, and computational-security limits](notes/computational_parameter_screen.md).

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

The current ordinary-layer computational loss can be bounded by

    sqrt(eta_0) + (2 eta_h + 2 r eta_y + eta_g)^(1/3) + eta_E,

with a sharper expression in the refinement document. Each eta is the success probability of a complete specified collision reduction, including its anchor, nested extraction, initialization, and runtime. It is not a per-query binding probability. The earlier fourth-root bounds remain valid historical upper bounds; the refinement is the stronger current result. Neither expression supplies numerical advantages from heuristic model exponents by itself.

Internal review notes accompany the main constructions. They are development evidence, not external peer-review acceptance or independent security certification. Optional [architecture limits](proofs/architecture_limits.md), [Boolean bridge toy ledger](proofs/boolean_bridge_toy.md), and [backend propositions](notes/backend_directions.md) retain their own stated scope and standalone checkers.

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

## Pinned Sage cost reproduction

The recorded model runs used SageMath 10.9 and an unmodified checkout of [Lattice Estimator](https://github.com/malb/lattice-estimator) at commit

    53da5982597709ba0fdf94ea37a84d822310fd84.

Obtain that external checkout separately and set `ESTIMATOR` to its location. Both drivers require `--estimator` explicitly and verify the exact commit and absence of tracked modifications. They call the Euclidean SIS cost routine and cost models only. They do not invoke BKZ, sieving, a lattice solver, challenge sampling, or a cryptographic prover.

For fresh model outputs, keep this order so every recorded raw input hash matches its generated path:

```sh
python -c "from pathlib import Path; Path('work').mkdir(exist_ok=True)"
python scripts/joint_parameter_search.py
sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile centered-fourth --path-input work/joint_parameter_search.json --output work/joint_parameter_model_screen.json
python scripts/joint_energy_parameter_search.py
sage -python scripts/computational_parameter_screen.py --estimator "$ESTIMATOR" --fold-profile bounded-energy --path-input work/joint_energy_parameter_search.json --output work/joint_energy_model_screen.json
sage -python scripts/outer_rank_parameter_screen.py --estimator "$ESTIMATOR" --output work/outer_rank_parameter_screen.json
```

The outer-rank wrapper reads both regenerated path files and their matching model files from `work/`. It checks 14 outer roles for each common rank 4,...,16 on both fixed paths, preserves their seven inner roles, and compares unrounded model-specific minima. It does not redo the joint digit search at every outer rank, because outer row counts do not change the witnessed packing dimensions or norm caps in this model.

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
- [Source/archive hash manifest](notes/parameter-results/archive-manifest.json).

All archived original JSON files are byte-for-byte copies. In particular, `path_input_sha256` and the outer wrapper's prior-model hashes authenticate the original raw bytes, including their original line endings. The local `.gitattributes` marks result JSON as `-text` to prevent Git line-ending conversion and fixes authored Python/Markdown files to LF for stable archive hashes. Do not reformat these JSON files and then expect their historical cross-file hashes to remain valid.

Authored proofs and scripts were copied with portable references, explicit external-estimator arguments, and normalized text line endings. The manifest records both original and archived hashes for those files and identifies editorial changes. Historical `source_hashes` inside the untouched JSON describe the files at the original run, not a claim that every archived proof has the same bytes. Later cross-references to the cubic-root refinement do not alter the saved numerical input, and archiving these files does not re-prove the theorems or security.

If using archived inputs for a cost-only rerun, copy their raw bytes to the corresponding `work/` names and keep each path paired with its matching model file. For example:

```sh
python -c "from pathlib import Path; import shutil; p=Path('notes/parameter-results'); w=Path('work'); w.mkdir(exist_ok=True); pairs={'joint-cube.json':'joint_parameter_search.json','joint-cube-models.json':'joint_parameter_model_screen.json','joint-energy.json':'joint_energy_parameter_search.json','joint-energy-models.json':'joint_energy_model_screen.json'}; [shutil.copyfile(p/a,w/b) for a,b in pairs.items()]"
```

A newly generated path JSON has new timing and provenance bytes even when its mathematics matches an archived path. Generate its matching cost output before invoking the outer wrapper; do not mix it with an old model record whose raw path hash differs.

The archive contains no third-party PDFs or estimator source, no account credentials, and no machine-specific user-directory paths. Its mathematical bounds, finite-domain optimization, and heuristic model outputs remain explicitly separated.
