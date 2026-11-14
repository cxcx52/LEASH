# Papers and implementation dependencies

Reviewed on **14 November 2026**. The register covers 24 distinct papers, including LaBRADOR. It identifies **12 downstream papers** with a numerical premise or substantial composition dependency, plus three optional compression configurations and one comparison baseline.

Each entry follows a specific claim to its source. The paper register fixes the reviewed PDF by SHA-256 and records physical page numbers. The repository register fixes source evidence to a Git commit.

[Paper versions and full evidence](papers.json) · [Repository register](REPOSITORIES.md) · [Repository evidence as JSON](repositories.json)

## Twelve substantive dependencies

| Category | Count | Meaning |
| --- | ---: | --- |
| A1 | 2 | Exact lower-tail statements contradicted by the existing certificate |
| A2 | 5 | Heuristic numerical premises or derived norm slack requiring recalibration |
| B | 5 | A concrete backend or composition whose guarantees require revalidation |

The original LaBRADOR is counted separately. Including it gives 13 papers in this core count. The classifications concern the claims listed below; the hypotheses of conditional composition theorems remain explicit.

### Exact numerical statements

| Paper | Evidence | Scope |
| --- | --- | --- |
| [RoKoko](https://eprint.iacr.org/2026/575) (2026/575) | p19; pp21–23; p57: Lemma 5 repeats the exact 256-row, sqrt(30) lower-tail budget; Lemmas 6–7 use it in structured projection. | Independent commitments and sumcheck claims have their own proof obligations. |
| [Orthus](https://eprint.iacr.org/2026/398) (2026/398) | PDF p32 (printed p30); pp20,22,38: Theorem 5 repeats the strict lower-tail bound; Theorems 3–4 use its failure budget. | The revised compressed configuration uses a separate infinity-norm theorem with threshold 0.49. |

### Numerical premises and derived parameters

| Paper | Evidence | Scope |
| --- | --- | --- |
| [Grand Danois](https://eprint.iacr.org/2026/1196) (2026/1196) | p15; p17; p22: Lemma 2.5 uses the same numerical lower-tail premise, introduced explicitly as heuristic; later projection proofs use it. | The existing strict lower-tail certificate also covers this lemma’s norm-relative event. |
| [Falcon 聚合](https://eprint.iacr.org/2024/311) (2024/311) | p10; p19; pp67–69: The heuristic JL lemma sets C2=30 at lambda=128; the later failure-density analysis uses a 2^-lambda term. | The numerical instantiation needs recalibration; the general predicate-special-soundness framework is a separate contribution. |
| [Symphony](https://eprint.iacr.org/2025/1905) (2025/1905) | p12; p24; p27: Lemma 2.2 imports the approximate JL constants used by the range-proof slack and extraction analysis. | The paper uses approximate inequalities. Its generic compiler remains a conditional result. |
| [Toolkit](https://eprint.iacr.org/2026/1289) (2026/1289) | p4; pp15–16; p27; p42: The terminal uses sqrt(128/30), 256-row Bin1 projections and the original LaBRADOR composition theorem. | The November revision also includes a distinct infinity-norm result and changes to LNP-Lite. |
| [Lemur+](https://eprint.iacr.org/2026/2054) (2026/2054) | p15; p19: The extracted-norm and MSIS estimates use delta_LB=sqrt(128/30); opening soundness relies on the selected backend. | The generic HVC-SOP/KOTS construction is stated separately from this instantiation. |

### Concrete backends and compositions

| Paper | Evidence | Scope |
| --- | --- | --- |
| [Greyhound](https://eprint.iacr.org/2024/1293) (2024/1293) | p6; pp23–24; pp27–28: The succinct evaluation proof delegates its final short relation to LaBRADOR. | The C implementation uses Rademacher projection entries. The ternary mathematical example requires a separate implementation-level analysis. |
| [Hachi](https://eprint.iacr.org/2026/156) (2026/156) | p26; pp27–28: The 55.1KB composition estimate includes a Greyhound tail, which in turn invokes LaBRADOR. | The Rust prototype measures the first Hachi round; ring switching and sumcheck are independently described. |
| [LaZer](https://eprint.iacr.org/2024/1846) (2024/1846) | p8 §4; pp8–9: The succinct-proof branch uses the LaBRADOR implementation and its parameter assumptions. | LaZer also exposes a separate linear-size proof branch. |
| [Unmasking TRaccoon](https://eprint.iacr.org/2025/849) (2025/849) | p53 Lemma B.6; p67 §B.6.2: The LaBRADOR-based ZK composition imports failure-density and knowledge-error premises from the Falcon analysis. | Its binary-projection lemma uses a different distribution and constants; the underlying TRaccoon signature is a separate layer. |
| [LaBinius](https://eprint.iacr.org/2026/2103) (2026/2103) | p23; p27; pp47–48: Recursive opening links a vendored LaBRADOR backend; Theorem 2 explicitly includes kappa_Lab. | The nonrecursive PCS and binary-field arithmetic have separate analysis and measurements. |

## Optional configurations and comparison baselines

| Paper | Configuration | PDF pages |
| --- | --- | --- |
| [RoK, Paper, SISsors](https://eprint.iacr.org/2024/1972) | An optional LaBRADOR second compression underlies the roughly 100KB estimate. The main subtractive-set/vSIS protocol has its own proof chain. | p49; pp54–55 |
| [LatticeFold](https://eprint.iacr.org/2024/257) | LaBRADOR is one possible final compressor for the IVC proof. The paper also offers a Stark terminal and uses sumcheck for its core range checks. | p52; pp7,55 |
| [Serval（旧名 HyperWolf）](https://eprint.iacr.org/2025/1903) | The optional compressed construction includes epsilon_La in its error expression. The measured prototype implements the baseline. LaBRADOR compression is an analytical extension in the reviewed version. | pp25–27; p28; pp40–41 |
| [TTRP shortness check](https://eprint.iacr.org/2026/2146) | The comparison table and host-integration examples use the older JL calibration. TTRP replaces the old projection with its own probability and composition results. | p5; pp17–19 |

The three optional configurations increase the downstream dependency count from 12 to 15. The TTRP comparison entry is listed separately. Serval and its former title HyperWolf under ePrint 2025/1903 are one paper in this census.

## Separate result paths

The following papers were reviewed and kept outside the confirmed dependency count.

| Paper | Evidence and reason |
| --- | --- |
| [Non-Malleable Reductions of Knowledge](https://eprint.iacr.org/2026/1822) | p10; p34; p43; p49: The zk-LaBRADot case study uses separate heuristic premises. Bin2, 512 rows and sqrt(26) differ from the audited event; a transfer of the existing counterexample remains unestablished. |
| [RoK and Roll](https://eprint.iacr.org/2025/1220) | p21; pp36–37; p20: Independent direct projection bounds and a final explicit witness. The concrete parameters use the paper’s own Lemmas 4–5. |
| [SALSAA](https://eprint.iacr.org/2025/2124) | pp27–30; p39: Projection guarantees follow RoK and Roll; the terminal sends the remaining witness. The dependency direction runs from SALSAA to later RoKoko work, rather than importing RoKoko’s numerical lemma into SALSAA. |
| [LatticeFold+](https://eprint.iacr.org/2025/247) | pp7,43,46: LaBRADOR appears in related work and performance comparisons. The reviewed construction has no identified LaBRADOR terminal dependency. |
| [Akita](https://eprint.iacr.org/2026/1983) | pp8,10,74; pp151–152: Exact norm sumchecks and a separate filtered-challenge support certificate. The paper expressly avoids JL projection and develops its own commitment-opening analysis. |
| [Jindo](https://eprint.iacr.org/2026/044) | p2 footnote; p12: Its own Quad/Agg/Split composition. The paper explicitly evaluates the construction without LaBRADOR composition. |
| [LatticeBlindFold](https://eprint.iacr.org/2026/1857) | p31; pp1,52: An ABDLOP-based construction. The reviewed work leaves a complete decider as a further step. |

The independent PikkuFold audit is outside this LaBRADOR propagation census.

## Version and evidence notes

Orthus and Toolkit published revisions on 3 November 2026. The entries distinguish their retained L2 premises from the revised infinity-norm construction. Local and official abstract text differ slightly for Lemur+ and SALSAA, so the technical judgments remain tied to the recorded local PDF hashes.

The search combined the local paper collection with official ePrint records and author-provided artifacts. The counts describe this reviewed set. Download copies, alternative titles, source-code forks and the author’s own drafts each have separate identities and are not added as extra papers.

The underlying mathematical evidence is summarized in the [proof-chain assessment](../research/notes/critical_path_assessment.md). The [strict probability checker](../research/scripts/jl_exact_checks.py) and replacement proofs are preserved in the research archive.
