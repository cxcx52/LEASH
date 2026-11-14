# Assessment of the main proof chain and the resulting contributions

Scope: the local 34-page version of LaBRADOR, ePrint 2022/1341, SHA-256
`87b99030c9cc11d922ebcb7cc475a5f44ccb20188ec18b1442c2d8f45412e581`.
This assessment concerns the mathematical claims in that version. It does not
assert that every other version or related construction has the same defects.

## Main conclusion

The audited presentation does not establish its advertised end-to-end security
and concrete parameter conclusions. The problems affect several necessary
links: the security definition and extraction interface, quantitative norm
testing, source arithmetic and commitment relations, and the final parameter
and session-error accounting. Correctness of other components does not supply
the missing premises in this chain. A substantive reconstruction is required;
the findings cannot all be resolved as typographical corrections.

This conclusion does not require disproving every lemma or counting a majority
of pages as erroneous. It follows from necessary dependencies. It also does
not imply that all protocols following the broad design are impossible, or
that a concrete deployed forgery has been demonstrated. The successful
conditional reconstruction in this repository is positive evidence that parts
of the design can be retained with changed hypotheses and costs.

## Evidence and the inference it supports

| Necessary link | Evidence in the audit | Supported conclusion |
|---|---|---|
| Quantitative JL soundness | Exact rational lower-tail counterexample exceeds both 2^-128 and 2^-127; a separate upper-tail example contradicts the stated numerical pair | The strict bounds used in those steps cannot be retained unchanged. A local error probability does not by itself determine the full protocol's failure rate. |
| Meaning of knowledge soundness | The printed true-statement quantification does not supply the usual all-statement guarantee needed by subsequent composition | A stronger, explicit extraction definition and theorem are necessary. |
| Affine source arithmetic | Honest short encodings can satisfy the stated numerical premise while centered reduction changes the decoded residual; X-2 is a unit in R_q when coprime to 2^d+1 | The asserted lifting inference and an in-ring divisibility interpretation cannot justify the intended target test. |
| Source-to-core relation | Missing residual/commitment equations in the affine presentation; native coefficient pins, conjugates and all-coefficient-ones terms must be specified | The complete target relation and chronology must be reconstructed before composition can be applied. |
| Norm and packing interface | Upper-triangle packing and a full-matrix norm sum are different expressions | A consistent norm relation and its parameter costs must be selected. This mismatch alone is not a soundness attack. |
| Challenge and session budgets | The original raw fixed-type count precedes rejection; optimized final rounds and retries have additional obligations | The raw count and ordinary single-attempt bounds cannot certify the final advertised instance without additional analysis. |
| Recursive bit complexity | Under the explicitly specified fixed-modulus, ordinary-recursion and full-coefficient encoding model, additional growth factors remain | A ring-element count alone does not establish the claimed bit cost. This is a restricted-model result. |

The exact probability checker is
[jl_exact_checks.py](../scripts/jl_exact_checks.py). The source-lifting checker
and repaired proof are [r1cs_checks.py](../scripts/r1cs_checks.py) and
[r1cs_repair.md](../proofs/r1cs_repair.md). The repaired main algebra and its
remaining premises are [protocol_repair.md](../proofs/protocol_repair.md).
The architecture result is [architecture_limits.md](../proofs/architecture_limits.md).
Monte Carlo evidence, where retained in the earlier audit, is not an exact
cardinality proof and is not promoted to one here.

## Contributions beyond a protocol modification

1. **A dependency-based mathematical audit.** Counterexamples and specification
   checks identify which premises fail and which top-level conclusions lose
   their justification. Each inference has a defined scope; correctness of
   unrelated components does not repair a necessary missing premise.
2. **Strict replacement theorems.** A uniform modular JL bound, explicit source
   lifting and pinning, all-statement extraction interfaces, fresh-kernel
   composition, and bounded complete restarts make the assumptions and error
   terms inspectable. Classical probability and extraction devices are credited.
3. **Sharper proved quantities.** Exact challenge counting, conditional fourth
   moments, bounded-energy families, and a cubic-root computational-loss
   refinement improve specified rigorous baselines. These improvements are
   stated with their changed norms, entropies and runtime obligations.
4. **A reproducible parameter and cost audit.** Actual extracted norms, every
   commitment role, digit padding, exact finite-domain optimization, and pinned
   heuristic models expose the difference between statistical error and
   complete computational security. Parameter feasibility is also evidence
   against a blanket impossibility conclusion.
5. **Explicit design variants and limits.** Native and affine frontends are
   separated. Classical polynomial fingerprints yield short source and
   aggregation challenges without a PRG assumption, while the JL communication
   and verifier work remain material. A restricted architecture lower bound
   identifies which claimed improvements need a change of model.

## What is stronger, and what is not claimed

The reconstruction supplies stronger explicit guarantees at several individual
proof interfaces and tighter bounds than earlier rigorous repair baselines.
It does not establish dominance over the original advertised system on every
axis. The ordinary core/source prover encoding is about 157.27 KiB in the final
fingerprint variant, with changed parameters and a different final-round
convention. Comparing that directly with the original 58 KB headline would
hide differences in protocol and accounting.

The final exact Q=128 statistical budget is below 2^-128. Complete computational
advantages at the nested reductions' runtimes, Fiat--Shamir/QROM, zero knowledge,
optimized last-round behavior, and a practical succinct-verifier backend remain
unproved here. Pinned lattice cost outputs are heuristic model evaluations,
not computational security lower bounds. No concrete forgery or lattice-solving
experiment is claimed.

A defensible paper thesis is therefore: **the existing proof chain does not
justify the claimed end-to-end guarantees; explicit reconstruction gives
corrected conditional guarantees, new quantitative refinements, and a revised
account of their actual costs and architectural limits.** A stronger-SNARK or
universal-impossibility thesis would require additional results. This audit
does not certify venue acceptance or claim novelty for classical tools.
