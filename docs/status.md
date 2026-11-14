# Claims, evidence, and remaining obligations

| Claim | Status | Evidence |
|---|---|---|
| 1024-row fixed-vector modular JL bound <2^-164 | Proved and independently reviewed | Full three-case proof; rational constants; endpoint enumeration |
| Honest threshold 552 beta^2; rejection <=8/33 | Proved | Exact second/fourth moments and Cantelli |
| Cube challenge cardinality and norms | Proved | Product count and triangle inequality |
| Invertible challenge differences | Derived from LS18 under stated ring conditions | Corollary 1.2; small exhaustive regression |
| Centered-lift sufficient inequality | Proved | Coefficientwise Cauchy-Schwarz and disjoint quadratic blocks |
| Affine-R1CS bare reduction | Proposed complete proof, internal review | Explicit chronology, composite-modulus aggregation, canonical-opening lemma |
| Finite, gap-parameterized main-protocol extraction | Proved under explicit classical reset/MSIS model; independently reviewed | Full bounded samplers, norms, canonical-mass losses and runtime |
| Exact paper-style universal main-protocol extractor | Not yet certified | Unknown-gap expected-time wrapper remains open here |
| General knowledge composition and unknown-success extractor wrapper | Not yet certified here | Requires a complete quantified theorem |
| Optimized final round and all retry schedules | Not certified | Must be budgeted separately |
| Fiat-Shamir / QROM | Not certified | Interactive extraction alone is insufficient |
| 58 KB or refreshed 128-bit Module-SIS estimate | Not certified | Changed norms and ranks require new accounting |

The code certifies arithmetic steps of the mathematical arguments. It is not a machine-checked proof in a proof assistant, and passing tests do not discharge the open obligations in this table.

No independent external peer review has been claimed. “Independently reviewed” means a separate analysis pass during development, with explicit cross-checks of hypotheses and endpoints.
