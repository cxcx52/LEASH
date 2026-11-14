"""Offline preparation of pinned upstream honest tests; never builds/runs C.

The only subprocess used here is Git for read-only source identity checks.
Prepared C files live outside this repository, not in a vendored directory.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys

PIN = "8b6626b26afd4c0162ddd089759d21d3d51bfbdf"
TARGETS = ("chihuahua", "dachshund", "greyhound")
REPO_ROOT = Path(__file__).resolve().parents[3]
REQUIRED_FLAGS = ("avx2", "aes", "avx512f", "avx512bw", "avx512dq",
                  "avx512vl", "avx512vbmi", "avx512_vbmi2", "avx512_vnni", "vaes")
FLAG_ALIASES = {"avx512_vbmi": "avx512vbmi", "avx512vbmi2": "avx512_vbmi2",
                "avx512vnni": "avx512_vnni"}
RELATIONS = {
    "chihuahua": "honest ternary witness for principal linear constraints; two-layer and composite tests",
    "dachshund": "honest ternary prepare_linear simple relation; NOT native binary R1CS",
    "greyhound": "honest uniform polynomial commitment/evaluation; reduction and composite tests",
}


class PreparationError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(source: Path, *args: str, input_data: bytes | None = None) -> bytes:
    env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0")
    try:
        return subprocess.run(["git", "-C", str(source), *args], input=input_data,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=True, env=env).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PreparationError(f"Read-only Git check failed: {args[0]}") from exc


def read_pinned_checkout(source: Path) -> tuple[dict[str, bytes], dict]:
    source = source.resolve(strict=True)
    top = Path(_git(source, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if top != source:
        raise PreparationError("--source must be the checkout root")
    revision = _git(source, "rev-parse", "HEAD").decode().strip()
    if revision != PIN:
        raise PreparationError(f"Expected clean upstream pin {PIN}, got {revision}")
    if _git(source, "status", "--porcelain=v1", "--untracked-files=all").strip():
        raise PreparationError("Source checkout is not clean (including untracked files)")
    entries = []
    for entry in _git(source, "ls-files", "-s", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = raw_name.decode("utf-8")
        path = PurePosixPath(name)
        if (mode not in {"100644", "100755"} or stage != "0" or path.is_absolute()
                or ".." in path.parts or "\\" in name or ":" in name):
            raise PreparationError(f"Unsupported tracked entry: {name}")
        entries.append((name, mode, oid))
    batch = _git(source, "cat-file", "--batch",
                 input_data="".join(oid+"\n" for _, _, oid in entries).encode())
    offset, files, records = 0, {}, {}
    for name, mode, oid in entries:
        end = batch.index(b"\n", offset)
        actual_oid, kind, length = batch[offset:end].decode().split()
        if actual_oid != oid or kind != "blob":
            raise PreparationError("Unexpected Git batch object")
        start, size = end+1, int(length)
        data = batch[start:start+size]
        offset = start+size+1
        if len(data) != size or batch[offset-1:offset] != b"\n":
            raise PreparationError("Truncated Git blob")
        working = source.joinpath(*PurePosixPath(name).parts)
        if working.is_symlink() or not working.is_file():
            raise PreparationError(f"Tracked path is not a regular file: {name}")
        files[name] = data
        records[name] = {"git_blob": oid, "mode": mode, "pinned_sha256": digest(data),
                         "checkout_sha256": digest(working.read_bytes()), "bytes": len(data)}
    if offset != len(batch):
        raise PreparationError("Unexpected trailing Git batch data")
    validate_source_metadata(files)
    return files, {"commit": revision, "clean": True, "files": records}


def validate_source_metadata(files: dict[str, bytes]) -> None:
    required = {"README", "LICENSE", "Makefile", "pack.c", "pack.h", "data.h",
                "labrador.c", "randombytes.c", *(f"test_{t}.c" for t in TARGETS)}
    if required-files.keys():
        raise PreparationError(f"Missing upstream inputs: {sorted(required-files.keys())}")
    readme = files["README"].decode()
    if "AVX512 instruction set" not in readme:
        raise PreparationError("Pinned README AVX512 requirement was not found")
    license_text = files["LICENSE"].decode()
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise PreparationError("Expected upstream Apache-2.0 license")
    makefile = files["Makefile"].decode()
    for token in ("-std=c2x", "-march=native", "-mtune=native", "-O3", "-flto=auto"):
        if token not in makefile:
            raise PreparationError(f"Expected upstream build flag missing: {token}")


def replace_once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise PreparationError(f"Expected one patch anchor, got {text.count(before)}: {before!r}")
    return text.replace(before, after, 1)


def checked_call(call: str, label: str) -> str:
    # Test-driver fail-fast only; no library behavior or verification is changed.
    return (f"  ret = {call};\n  if(ret) {{\n"
            f'    fprintf(stderr,"LABRADOR_ADAPTER_CALL_FAILED {label} %d\\n",ret);\n'
            "    return ret;\n  }")


def patch_test(target: str, data: bytes, log_size: int = 10) -> bytes:
    if target not in TARGETS or type(log_size) is not int or not 10 <= log_size <= 19:
        raise PreparationError("Smoke log-size must be an integer in [10,19]")
    text = data.decode("utf-8")
    original = {"chihuahua": "    n[i] = 1<<11;",
                "dachshund": "    n[i] = 1<<16;",
                "greyhound": "  len = 1 << 19;"}[target]
    replacement = (f"  len = 1 << {log_size};" if target == "greyhound"
                   else f"    n[i] = 1<<{log_size};")
    text = replace_once(text, original, replacement)
    if target == "dachshund":
        for call in ("simple_prove(&st1,&wt1,&pi0,&com,&st0,&wt0,0)",
                     "prove(&st2,&wt2,&pi1,&st1,&wt1,0)"):
            text = replace_once(text, "  "+call+";", checked_call(call, target))
        call = "composite_prove_simple(&p,&com,&st,&wt)"
        text = replace_once(text, "  "+call+";;", checked_call(call, target))
    if target == "greyhound":
        # Failure cleanup of the upstream small test can visit these objects.
        for declaration in ("polcomctx ctx", "polcomprf pi", "prncplstmnt st", "witness wt"):
            text = replace_once(text, "  "+declaration+";", "  "+declaration+" = {};")
        call = "polcom_commit(&ctx,s,len)"
        if text.count("  "+call+";") != 2:
            raise PreparationError("Expected both Greyhound honest commitment calls")
        text = text.replace("  "+call+";", checked_call(call, target))
        call = "composite_prove_polcom(&p,&pi,&ctx,x,y)"
        text = replace_once(text, "  "+call+";", checked_call(call, target))
    first_call = "test_polcom(len)" if target == "greyhound" else "test_twolayer()"
    second_call = "test_pack(len)" if target == "greyhound" else "test_pack()"
    first_label = "evaluation_reduction" if target == "greyhound" else "two_layer"
    for call, stage in ((first_call, first_label), (second_call, "composite")):
        before = f"  ret = {call};\n  if(ret) goto end;"
        text = replace_once(text, before, before+
            f'\n  printf("LABRADOR_ADAPTER_STAGE_OK {target} {stage}\\n");')
    text = replace_once(text, "end:\n  free_comkey();\n  return ret;\n}",
        "end:\n  free_comkey();\n"
        f'  if(!ret) printf("LABRADOR_ADAPTER_SUCCESS {target}\\n");\n'
        f'  else fprintf(stderr,"LABRADOR_ADAPTER_FAILURE {target} %d\\n",ret);\n'
        "  return ret ? EXIT_FAILURE : EXIT_SUCCESS;\n}")
    return text.encode("utf-8")


def capability_report(system: str | None = None, machine: str | None = None,
                      cpuinfo: str | None = None) -> dict:
    system = platform.system() if system is None else system
    machine = platform.machine() if machine is None else machine
    if cpuinfo is None:
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text() if system == "Linux" else ""
        except OSError:
            cpuinfo = ""
    per_cpu = []
    for line in cpuinfo.splitlines():
        if line.partition(":")[0].strip() == "flags":
            per_cpu.append({FLAG_ALIASES.get(f, f) for f in line.partition(":")[2].split()})
    flags = set.intersection(*per_cpu) if per_cpu else set()
    missing = sorted(set(REQUIRED_FLAGS)-flags)
    reasons = []
    if system != "Linux" or machine.lower() not in {"x86_64", "amd64"}:
        reasons.append("This adapter only prepares execution on Linux x86-64")
    if missing:
        reasons.append("Required CPU features are not exposed on every visible CPU")
    return {"status": "unsupported_capability" if reasons else "cpu_capability_present",
            "execution_status": "blocked-hardware" if reasons else "not_executed",
            "system": system, "machine": machine, "required_flags": list(REQUIRED_FLAGS),
            "missing_flags": missing, "reasons": reasons,
            "compiler_and_OS_execution_still_unverified": True}


def _outside(path: Path, protected: Path) -> bool:
    return path != protected and protected not in path.parents and path not in protected.parents


def validate_destinations(source: Path, work: Path, artifacts: Path) -> None:
    for destination in (work, artifacts):
        if destination.exists():
            raise PreparationError(f"Destination must be new: {destination}")
        if not _outside(destination, source) or not _outside(destination, REPO_ROOT):
            raise PreparationError("Outputs must be outside both checkouts, with no ancestor overlap")
    if not _outside(work, artifacts):
        raise PreparationError("Work and artifact directories must be separate")


def make_plan(source: Path, work: Path, files: dict[str, bytes], identity: dict,
              log_size: int) -> tuple[dict, str, dict[str, bytes]]:
    modified, patches = {}, []
    for target in TARGETS:
        name = f"test_{target}.c"
        modified[name] = patch_test(target, files[name], log_size)
        patches.extend(difflib.unified_diff(files[name].decode().splitlines(True),
            modified[name].decode().splitlines(True), fromfile="a/"+name, tofile="b/"+name))
    commands = {"cwd": str(work), "capability_check_required_before_build_or_run":
        [sys.executable, str(Path(__file__).resolve()), "capabilities"],
        "build": ["make", "-j1", *(f"test_{t}" for t in TARGETS)],
        "run": {t: [str(work/f"test_{t}")] for t in TARGETS}}
    manifest = {"schema": "upstream-labrador-honest-smoke-v1", "upstream_commit": PIN,
        "source": str(source), "work_directory": str(work), "upstream_license": "Apache-2.0",
        "status": "prepared_not_executed", "source_identity": identity,
        "patch_policy": "test sizes, ignored error checks, safe zero-init, success markers only; no library edits",
        "modified_files": {name: {"original_sha256": digest(files[name]),
            "prepared_sha256": digest(data)} for name, data in modified.items()},
        "parameters": {"N": 64, "LOGQ": 32, "q": 4294967197,
            "chihuahua": {"r": 1, "rings_per_vector": 1 << log_size},
            "dachshund": {"r": 2, "rings_per_vector": 1 << log_size},
            "greyhound": {"ring_length": 1 << log_size, "polynomial_coefficient_count": 64 << log_size}},
        "relations": RELATIONS, "parameters_unchanged": "upstream T=14, SLACK=2 and automatic parameter selection",
        "size_measurement": "upstream printed formula estimate in 1024-byte units, not serialization",
        "actual_serialized_proof_bytes": None, "randomness": "unchanged upstream OS randombytes; no deterministic seed",
        "timing": "upstream clock() labels are process CPU seconds; end-to-end wall time requires external measurement",
        "energy_joules": None, "hardware_execution_validated": False,
        "required_cpu_flags_conservative": list(REQUIRED_FLAGS), "commands": commands}
    return manifest, "".join(patches), modified


def prepare(source: Path, work: Path, artifacts: Path, *, dry_run: bool = True,
            log_size: int = 10) -> dict:
    source, work, artifacts = source.resolve(strict=True), work.resolve(), artifacts.resolve()
    validate_destinations(source, work, artifacts)
    files, identity = read_pinned_checkout(source)
    manifest, patch, modified = make_plan(source, work, files, identity, log_size)
    manifest["status"] = "dry_run_not_executed" if dry_run else "prepared_not_executed"
    if not dry_run:
        work.mkdir(parents=True, exist_ok=False)
        for name, data in files.items():
            dest = work.joinpath(*PurePosixPath(name).parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(modified.get(name, data))
            if identity["files"][name]["mode"] == "100755":
                dest.chmod(dest.stat().st_mode | 0o111)
    artifacts.mkdir(parents=True, exist_ok=False)
    (artifacts/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    (artifacts/"commands.json").write_text(json.dumps(manifest["commands"], indent=2)+"\n", encoding="utf-8")
    (artifacts/"tests.patch").write_text(patch, encoding="utf-8", newline="\n")
    return manifest


def check_result(target: str, returncode: int, stdout: str, stderr: str) -> dict:
    if target not in TARGETS:
        raise PreparationError("Unknown upstream test")
    stage = "evaluation_reduction" if target == "greyhound" else "two_layer"
    required = [f"LABRADOR_ADAPTER_STAGE_OK {target} {stage}",
                f"LABRADOR_ADAPTER_STAGE_OK {target} composite",
                f"LABRADOR_ADAPTER_SUCCESS {target}"]
    lines = stdout.splitlines()
    reasons = []
    if returncode != 0:
        reasons.append(f"process returned {returncode}")
    if any(lines.count(marker) != 1 for marker in required):
        reasons.append("missing or repeated verification/success marker")
    elif [lines.index(marker) for marker in required] != sorted(lines.index(marker) for marker in required):
        reasons.append("success markers out of order")
    if "ERROR" in stdout+stderr or "LABRADOR_ADAPTER_FAILURE" in stdout+stderr or "LABRADOR_ADAPTER_CALL_FAILED" in stdout+stderr:
        reasons.append("upstream or adapter reported failure")
    estimates = []
    for line in lines:
        match = re.fullmatch(r"\s*(.*?)size: ([0-9]+(?:\.[0-9]+)?) KB", line)
        if match:
            estimates.append({"label": match[1].strip()+"size", "estimated_KiB": float(match[2])})
    return {"schema": "upstream-labrador-honest-smoke-result-v1", "target": target,
            "status": "passed" if not reasons else "failed", "returncode": returncode,
            "reasons": reasons, "relation": RELATIONS[target],
            "upstream_printed_size_estimates": estimates,
            "actual_serialized_proof_bytes": None,
            "stdout_sha256": digest(stdout.encode()), "stderr_sha256": digest(stderr.encode()),
            "security_equivalence_to_repair": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    for action in ("plan", "prepare"):
        command = subs.add_parser(action)
        command.add_argument("--source", required=True, type=Path)
        command.add_argument("--work-dir", required=True, type=Path)
        command.add_argument("--artifacts", required=True, type=Path)
        command.add_argument("--log-size", type=int, default=10)
    subs.add_parser("capabilities")
    command = subs.add_parser("check-result")
    command.add_argument("--target", choices=TARGETS, required=True)
    command.add_argument("--returncode", type=int, required=True)
    command.add_argument("--stdout", type=Path, required=True)
    command.add_argument("--stderr", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action in {"plan", "prepare"}:
            result = prepare(args.source, args.work_dir, args.artifacts,
                             dry_run=args.action == "plan", log_size=args.log_size)
            print(json.dumps({"status": result["status"], "artifacts": str(args.artifacts)}))
            return 0
        if args.action == "capabilities":
            result = capability_report()
            print(json.dumps(result, indent=2))
            return 77 if result["status"] == "unsupported_capability" else 0
        result = check_result(args.target, args.returncode,
                              args.stdout.read_text(encoding="utf-8", errors="replace"),
                              args.stderr.read_text(encoding="utf-8", errors="replace"))
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "passed" else 1
    except (PreparationError, OSError) as exc:
        print(json.dumps({"status": "preparation_failed", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
