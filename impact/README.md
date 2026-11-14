# Affected papers

LaBRADOR's numerical bounds, norm slack, and proof backend appear in 12 substantive downstream dependencies and three optional configurations. The tables identify the specific claims and configurations involved. Page references use physical PDF pages unless printed pagination is also given.

[Implementation dependencies](REPOSITORIES.md)

## LaBRADOR

| Paper | Affected claim | Pages |
| --- | --- | --- |
| [LaBRADOR](https://eprint.iacr.org/2022/1341) ([CRYPTO](https://link.springer.com/chapter/10.1007/978-3-031-38554-4_17)) | The exact lower-tail probability exceeds the nominal `2^-128` budget in its JL calibration. Parts of the paper use approximate notation; the discrepancy concerns the numerical calibration and its use in the projection analysis. | pp10,30–31 |

## Exact lower-tail statements

| Paper | Affected claim | Pages |
| --- | --- | --- |
| [RoKoko](https://eprint.iacr.org/2026/575) ([ASIACRYPT](https://eprint.iacr.org/2026/575)) | Lemma 5 repeats the exact 256-row, `sqrt(30)` lower-tail bound; Lemmas 6–7 use it for structured projections. | p19; pp21–23; p57 |
| [Orthus](https://eprint.iacr.org/2026/398) ([CRYPTO](https://link.springer.com/chapter/10.1007/978-3-032-35377-1_4)) | Theorem 5 repeats the strict L2 lower-tail bound, and Theorems 3–4 use its failure budget. | p32 (printed p30); pp20,22,38 |

## Numerical premises and derived parameters

| Paper | Affected claim or configuration | Pages |
| --- | --- | --- |
| [Grand Danois](https://eprint.iacr.org/2026/1196) (ePrint) | Lemma 2.5 explicitly introduces the same numerical lower-tail premise as a heuristic. Later projection proofs use it; the strict lower-tail calculation also covers its norm-relative event. | p15; p17; p22 |
| [Aggregating Falcon Signatures with LaBRADOR](https://eprint.iacr.org/2024/311) ([CRYPTO](https://link.springer.com/chapter/10.1007/978-3-031-68376-3_3)) | The heuristic JL lemma sets `C2=30` at `lambda=128`; the later failure-density analysis uses a `2^-lambda` term. This numerical instantiation requires recalibration. | p10; p19; pp67–69 |
| [Symphony](https://eprint.iacr.org/2025/1905) ([ASIACRYPT](https://eprint.iacr.org/2025/1905)) | Lemma 2.2 imports approximate JL constants used in the range-proof slack, completeness budget, and extraction retries. LaBRADOR also appears as a candidate terminal backend. | p12; p24; p27; pp42–44 |
| [A Toolkit for Succinct Lattice-Based Zero Knowledge Proofs](https://eprint.iacr.org/2026/1289) ([CCS](https://www.sigsac.org/ccs/CCS2026/program/accepted-papers.html)) | The L2 terminal uses `sqrt(128/30)`, 256-row Bin1 projections, and the original LaBRADOR composition theorem. | p4; pp15–16; p27; p42 |
| [Lemur+](https://eprint.iacr.org/2026/2054) (ePrint) | The selected backend's extracted-norm and MSIS estimates use `delta_LB=sqrt(128/30)`. Its opening-soundness instantiation depends on that backend. | p15; p19 |

## Backend and composition dependencies

| Paper | Affected configuration | Pages |
| --- | --- | --- |
| [Greyhound](https://eprint.iacr.org/2024/1293) ([CRYPTO](https://link.springer.com/chapter/10.1007/978-3-031-68403-6_8)) | The succinct evaluation proof delegates its final short relation to LaBRADOR. The C implementation uses Rademacher projection entries, so the ternary calculation requires a separate implementation-level analysis. | p6; pp23–24; pp27–28 |
| [Hachi](https://eprint.iacr.org/2026/156) (ePrint) | The 55.1KB composition estimate includes a Greyhound terminal, which invokes LaBRADOR. The Rust prototype measures the first Hachi round. | p26; pp27–28 |
| [LaZer](https://eprint.iacr.org/2024/1846) ([CCS](https://doi.org/10.1145/3658644.3690330)) | The succinct-proof branch uses the LaBRADOR implementation and its parameter assumptions. | p8 §4; pp8–9 |
| [Unmasking TRaccoon](https://eprint.iacr.org/2025/849) ([CRYPTO](https://link.springer.com/chapter/10.1007/978-3-032-01887-8_14)) | The LaBRADOR-based ZK composition imports failure-density and knowledge-error premises from the Falcon analysis. Its binary-projection lemma uses a different distribution and constants. | p53 Lemma B.6; p67 §B.6.2 |
| [LaBinius](https://eprint.iacr.org/2026/2103) (ePrint) | Recursive opening links a vendored LaBRADOR backend; Theorem 2 explicitly includes `kappa_Lab`. | p23; p27; pp47–48 |

## Optional configurations

| Paper | Affected configuration | Pages |
| --- | --- | --- |
| [RoK, Paper, SISsors](https://eprint.iacr.org/2024/1972) ([ASIACRYPT](https://link.springer.com/chapter/10.1007/978-981-96-0935-2_7)) | An optional second compression with LaBRADOR underlies the roughly 100KB estimate. | p49; pp54–55 |
| [LatticeFold](https://eprint.iacr.org/2024/257) ([ASIACRYPT](https://link.springer.com/chapter/10.1007/978-981-95-5099-9_11)) | The configuration that uses LaBRADOR as the final compressor for the IVC proof. | p52; pp7,55 |
| [Serval (formerly HyperWolf)](https://eprint.iacr.org/2025/1903) (ePrint) | The optional compressed construction includes `epsilon_La` in its error expression. LaBRADOR compression is an analytical extension; the measured prototype implements the baseline. | pp25–27; p28; pp40–41 |
