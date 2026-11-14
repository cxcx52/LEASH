# Repositories and backend dependencies

These eight repositories contain the backends, parameter calculations or paper artifacts linked to the [affected claims](README.md). The scope below identifies the relevant configuration; source links are pinned to exact commits.

| Repository | Relevant configuration | Source commit |
| --- | --- | --- |
| [lattice-dogs/labrador](https://github.com/lattice-dogs/labrador) | LaBRADOR backend and Greyhound composition | [8b6626b26afd](https://github.com/lattice-dogs/labrador/commit/8b6626b26afd4c0162ddd089759d21d3d51bfbdf) |
| [lazer-crypto/labrador](https://github.com/lazer-crypto/labrador) | Orthus and Toolkit core and terminal backend | [c1ae0e612d5a](https://github.com/lazer-crypto/labrador/commit/c1ae0e612d5accd9e7d9d1c264951c1afe949c83) |
| [lazer-crypto/lazer](https://github.com/lazer-crypto/lazer) | LaBRADOR-backed succinct proofs and Toolkit benchmarks | [b958e247a2fd](https://github.com/lazer-crypto/lazer/commit/b958e247a2fdb9593b3c25c9603c6c5305c19420) |
| [dfaranha/aggregate-falcon](https://github.com/dfaranha/aggregate-falcon) | Falcon aggregation parameter and size estimator | [971472cd8f75](https://github.com/dfaranha/aggregate-falcon/commit/971472cd8f75513ed963f3b3e4ffa8adc490b794) |
| [georgeorourke/hachi-pcs](https://github.com/georgeorourke/hachi-pcs) | Hachi paper's Greyhound terminal composition estimate | [6d90caca6438](https://github.com/georgeorourke/hachi-pcs/commit/6d90caca64386e506bdd5d0097f87ccb98fc0926) |
| [osdnk/labinius](https://github.com/osdnk/labinius) | LaBinius recursive-opening backend | [96b57f724fc1](https://github.com/osdnk/labinius/commit/96b57f724fc15c8e40495015c01dc3e6d8dfe595) |
| [lattice-arguments/rokoko](https://github.com/lattice-arguments/rokoko) | RoKoko coarse/fine projection and norm checks | [c7c4d9e5d684](https://github.com/lattice-arguments/rokoko/commit/c7c4d9e5d684eee71efac5bc8059fcb94559a9d3) |
| [dingdangdangwhx/Lemur-plus](https://github.com/dingdangdangwhx/Lemur-plus) | Lemur+ Chihuahua/LaBRADOR composition | [8b9b1beb2461](https://github.com/dingdangdangwhx/Lemur-plus/commit/8b9b1beb246113ff5fcee26cf52f197f5231dfbb) |

## lattice-dogs/labrador

The shared C backend composes the Greyhound frontend with LaBRADOR iterations.

Code evidence: [README:3](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/README#L3-L5) · [test_greyhound.c:88](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/test_greyhound.c#L88-L89) · [pack.c:164](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/pack.c#L164) · [pack.c:292](https://github.com/lattice-dogs/labrador/blob/8b6626b26afd4c0162ddd089759d21d3d51bfbdf/pack.c#L292-L310).

## lazer-crypto/labrador

The composable LaBRADOR core and terminal backend used by Orthus and Toolkit.

Code evidence: [README.md:1](https://github.com/lazer-crypto/labrador/blob/c1ae0e612d5accd9e7d9d1c264951c1afe949c83/README.md#L1-L5) · [Makefile:12](https://github.com/lazer-crypto/labrador/blob/c1ae0e612d5accd9e7d9d1c264951c1afe949c83/Makefile#L12-L19) · [Makefile:97](https://github.com/lazer-crypto/labrador/blob/c1ae0e612d5accd9e7d9d1c264951c1afe949c83/Makefile#L97-L104) · [pack.c:280](https://github.com/lazer-crypto/labrador/blob/c1ae0e612d5accd9e7d9d1c264951c1afe949c83/pack.c#L280-L312).

## lazer-crypto/lazer

The LaBRADOR-backed succinct-proof configuration and Toolkit benchmarks, through the src/labrados submodule.

Code evidence: [.gitmodules:1](https://github.com/lazer-crypto/lazer/blob/b958e247a2fdb9593b3c25c9603c6c5305c19420/.gitmodules#L1-L4) · [Makefile:206](https://github.com/lazer-crypto/lazer/blob/b958e247a2fdb9593b3c25c9603c6c5305c19420/Makefile#L206) · [Makefile:232](https://github.com/lazer-crypto/lazer/blob/b958e247a2fdb9593b3c25c9603c6c5305c19420/Makefile#L232-L265) · [README.md:36](https://github.com/lazer-crypto/lazer/blob/b958e247a2fdb9593b3c25c9603c6c5305c19420/README.md#L36-L40).

## dfaranha/aggregate-falcon

The Falcon aggregation parameter and size calculations that use JL_slack = sqrt(128/30).

Code evidence: [README.md:2](https://github.com/dfaranha/aggregate-falcon/blob/971472cd8f75513ed963f3b3e4ffa8adc490b794/README.md#L2-L7) · [proof_size_estimate.py:36](https://github.com/dfaranha/aggregate-falcon/blob/971472cd8f75513ed963f3b3e4ffa8adc490b794/proof_size_estimate.py#L36-L37) · [proof_size_estimate.py:47](https://github.com/dfaranha/aggregate-falcon/blob/971472cd8f75513ed963f3b3e4ffa8adc490b794/proof_size_estimate.py#L47-L70) · [proof_size_estimate.py:200](https://github.com/dfaranha/aggregate-falcon/blob/971472cd8f75513ed963f3b3e4ffa8adc490b794/proof_size_estimate.py#L200-L202).

## georgeorourke/hachi-pcs

The Hachi paper's Greyhound terminal composition estimate; this repository supplies the associated Rust prototype.

Code evidence: [README.md:1](https://github.com/georgeorourke/hachi-pcs/blob/6d90caca64386e506bdd5d0097f87ccb98fc0926/README.md#L1-L8) · [Cargo.toml:8](https://github.com/georgeorourke/hachi-pcs/blob/6d90caca64386e506bdd5d0097f87ccb98fc0926/Cargo.toml#L8-L18) · [src/main.rs:29](https://github.com/georgeorourke/hachi-pcs/blob/6d90caca64386e506bdd5d0097f87ccb98fc0926/src/main.rs#L29-L63).

## osdnk/labinius

The recursive-opening configuration that calls the vendored LaBRADOR C backend.

Code evidence: [README.md:6](https://github.com/osdnk/labinius/blob/96b57f724fc15c8e40495015c01dc3e6d8dfe595/README.md#L6-L12) · [crates/pcs/labrador/VENDORED.md:3](https://github.com/osdnk/labinius/blob/96b57f724fc15c8e40495015c01dc3e6d8dfe595/crates/pcs/labrador/VENDORED.md#L3-L7) · [crates/pcs/build.rs:11](https://github.com/osdnk/labinius/blob/96b57f724fc15c8e40495015c01dc3e6d8dfe595/crates/pcs/build.rs#L11-L16) · [crates/pcs/build.rs:105](https://github.com/osdnk/labinius/blob/96b57f724fc15c8e40495015c01dc3e6d8dfe595/crates/pcs/build.rs#L105-L107) · [crates/pcs/src/labrador/ffi.rs:27](https://github.com/osdnk/labinius/blob/96b57f724fc15c8e40495015c01dc3e6d8dfe595/crates/pcs/src/labrador/ffi.rs#L27-L33).

## lattice-arguments/rokoko

The coarse/fine projection and norm-check configuration in the independent RoKoko Rust implementation.

Code evidence: [README.md:5](https://github.com/lattice-arguments/rokoko/blob/c7c4d9e5d684eee71efac5bc8059fcb94559a9d3/README.md#L5-L13) · [README.md:99](https://github.com/lattice-arguments/rokoko/blob/c7c4d9e5d684eee71efac5bc8059fcb94559a9d3/README.md#L99-L103) · [src/common/projection_matrix.rs:1](https://github.com/lattice-arguments/rokoko/blob/c7c4d9e5d684eee71efac5bc8059fcb94559a9d3/src/common/projection_matrix.rs#L1-L20) · [.gitmodules:1](https://github.com/lattice-arguments/rokoko/blob/c7c4d9e5d684eee71efac5bc8059fcb94559a9d3/.gitmodules#L1-L3).

## dingdangdangwhx/Lemur-plus

The Lemur+ relation driver that calls the vendored Chihuahua/LaBRADOR composition.

Code evidence: [README.md:3](https://github.com/dingdangdangwhx/Lemur-plus/blob/8b9b1beb246113ff5fcee26cf52f197f5231dfbb/README.md#L3-L17) · [NOTICE.md:10](https://github.com/dingdangdangwhx/Lemur-plus/blob/8b9b1beb246113ff5fcee26cf52f197f5231dfbb/NOTICE.md#L10-L12) · [labrador/lemur_plus/proof_driver.c:23](https://github.com/dingdangdangwhx/Lemur-plus/blob/8b9b1beb246113ff5fcee26cf52f197f5231dfbb/labrador/lemur_plus/proof_driver.c#L23-L25) · [labrador/lemur_plus/proof_driver.c:1082](https://github.com/dingdangdangwhx/Lemur-plus/blob/8b9b1beb246113ff5fcee26cf52f197f5231dfbb/labrador/lemur_plus/proof_driver.c#L1082-L1084).

The [paper table](README.md) identifies the corresponding claim and PDF page.
