# Parameters and communication

The final recorded path uses modulus `4294967197`, ring degree 64, seven ordinary-core layers, inner rank 24, outer rank 9 and source rank 6. The challenge family has squared coefficient norm at most 104 and operator norm strictly below 30. The complete-attempt limit is 128.

| Quantity | Recorded value |
| --- | ---: |
| Ordinary-core prover-message encoding, one attempt | 155.1484375 KiB |
| Core plus native binary source | 157.17578125 KiB |
| Source-fingerprint variant, including byte padding | 161,040 bytes = 157.265625 KiB |
| Source fingerprint challenge | 187 bits |
| Core aggregation challenges across seven layers | 1,960 bytes |
| Explicit verifier messages in the fingerprint variant | About 67.54 GiB |

These are encoding bounds for the specified parameter path. The dense JL matrices dominate verifier communication. The exact statistical expression for the fingerprint variant is approximately `2^-128.69244`; computational extraction advantages and their running times are accounted for separately in the [claim ledger](../docs/status.md).

The standalone completeness theorem uses `552 beta^2` and slack `sqrt(23/5)`. The final path above uses `H=640` and squared slack `16/3`.

## Saved ledgers

| Record | Location |
| --- | --- |
| Final source and core accounting | [Native frontend ledger](../research/notes/binary_frontend_audit.md) |
| Cube and energy comparison | [Joint parameter search](../research/notes/joint_energy_parameter_search.md) |
| Outer-rank selection | [Rank screen](../research/notes/outer_rank_parameter_screen.md) |
| Cost-model assumptions | [Computational parameter screen](../research/notes/computational_parameter_screen.md) |
| Machine-readable paths and model outputs | [Preserved result files](../research/notes/parameter-results/) |

The result files stay with their original manifest in `research/notes/parameter-results/`, so their hashes and replay commands remain stable.

## Reproduce

From the repository root:

```sh
python research/scripts/verify_archive.py
```

To regenerate the arithmetic paths:

```sh
cd research
python -c "from pathlib import Path; Path('work').mkdir(exist_ok=True)"
python scripts/joint_parameter_search.py
python scripts/joint_energy_parameter_search.py
```

Sage cost-model runs take an external estimator checkout through `--estimator`. The pinned revision and command sequence are in the [research reproduction guide](../research/README.md#pinned-sage-cost-reproduction).
