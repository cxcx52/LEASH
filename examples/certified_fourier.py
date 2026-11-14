"""Deterministic arithmetic comparison; no sampling or performance estimate."""

import json
import random

from labrador_repair.challenges import exact_operator_norm_below
from labrador_repair.fourier import certified_operator_norm_below


rng = random.Random(20261114)  # Only reproducible test inputs, never prover coins.
inputs = [tuple(rng.randrange(-2, 3) for _ in range(64)) for _ in range(16)]
paths = {}
for coefficients in inputs:
    for threshold in (16, 24, 31, 40):
        answer, path = certified_operator_norm_below(coefficients, threshold, with_path=True)
        assert answer == exact_operator_norm_below(coefficients, threshold)
        paths[path] = paths.get(path, 0) + 1

print(json.dumps({
    'scope': 'Finite exact predicate checks, not security or probability estimates',
    'degree': 64,
    'seed': 20261114,
    'cases': 64,
    'all_decisions_match': True,
    'diagnostic_path_counts': paths,
}, indent=2))
