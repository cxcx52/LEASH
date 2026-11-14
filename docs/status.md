# Claims, evidence, and remaining obligations

| Claim | Status | Evidence |
|---|---|---|
| 1024-row fixed-vector modular JL bound <2^-164 | Proved and independently reviewed | Full three-case proof; rational constants; endpoint enumeration |
| Honest threshold 552 beta^2; rejection <=8/33 | Proved | Exact second/fourth moments and Cantelli |
| JL family for every integer lambda>=128 | Proved and independently reviewed | Uniform scaling proof, exact base certificates, integer parameter generator |
| Cube challenge cardinality and norms | Proved | Product count and triangle inequality |
| Filtered d64 challenges with strict operator norm below 31 | Proved and independently reviewed | Exact rational tail certificate; cardinality above (9/16)5^64; integer Sylvester/Bareiss predicate; independent small spectral formula checks |
| Certified Fourier membership predicate | Proved and independently reviewed | Rational twiddle enclosures, strict integer comparisons and exact fallback; equality and low-precision tests |
| Invertible challenge differences | Derived from LS18 under stated ring conditions | Corollary 1.2; small exhaustive regression |
| Centered-lift sufficient inequality | Proved | Coefficientwise Cauchy-Schwarz and disjoint quadratic blocks |
| Affine-R1CS bare reduction | Proposed complete proof, internal review | Explicit chronology, composite-modulus aggregation, canonical-opening lemma |
| Finite, gap-parameterized main-protocol extraction | Proved under explicit classical reset/MSIS model; independently reviewed | Full bounded samplers, norms, canonical-mass losses and runtime |
| Universal expected-time ordinary-core extractor | Proved under explicit classical reset/MSIS model; independently reviewed | Original accept gate, at most 1+r/(1-1/N) expected executions, additional r/N statistical loss |
| Ordinary-core statistical parameter family | Proved | Ring degree, challenge size, aggregation count and JL parameters all scale; exact examples |
| Ordinary-layer composition and affine-plus-core corollary | Proved under explicit wrapper conditions; independently reviewed | Fresh final-reply coins, exact relaxed relations, actual norm caps and a checked polynomial runtime product |
| Bounded complete ordinary restarts | Proved under the gate-preserving interface; independently reviewed | Disjoint first-acceptance coupling, adaptive rejected histories, additive errors, uniform expected cost and exact completeness bound |
| Original concrete recursive schedule | Not certified | Must instantiate those conditions and every computational norm bound |
| Optimized final round, local retries and noninteractive retry selection | Not certified | The complete-protocol restart theorem does not cover these changes |
| Fiat-Shamir / QROM | Not certified | Interactive extraction alone is insufficient |
| 58 KB or refreshed 128-bit Module-SIS estimate | Not certified | Changed norms and ranks require new accounting |
| Stronger backend or new security property | Research in progress | Parameter feasibility, structural limits and current prior art must be checked together |

The code certifies arithmetic steps of the mathematical arguments. It is not a machine-checked proof in a proof assistant, and passing tests do not discharge the open obligations in this table.

No independent external peer review has been claimed. “Independently reviewed” means a separate analysis pass during development, with explicit cross-checks of hypotheses and endpoints.
