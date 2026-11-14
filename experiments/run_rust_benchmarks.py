"""Record a clean-revision Rust end-to-end benchmark, using portable paths."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def command(argv):
    return subprocess.check_output(argv, cwd=ROOT, text=True, encoding="utf-8").strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rounds", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    dirty = command(["git", "status", "--porcelain", "--untracked-files=normal"])
    if dirty:
        raise SystemExit("Commit the source before measuring; this runner records clean revisions.")
    destination = args.out.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    revision = command(["git", "rev-parse", "HEAD"])
    lock_hash = sha256(ROOT / "Cargo.lock")
    argv = ["cargo", "run", "--release", "--locked", "-p", "leash", "--example", "measure", "--", str(args.rounds)]
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    process = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=1800, check=False)
    elapsed = time.perf_counter() - clock
    (destination / "stdout.jsonl").write_bytes(process.stdout)
    (destination / "stderr.log").write_bytes(process.stderr)
    metadata = {
        "source_revision": revision,
        "source_clean_before": True,
        "source_clean_after": not command(["git", "status", "--porcelain", "--untracked-files=normal"]),
        "cargo_lock_sha256": lock_hash,
        "cargo_lock_unchanged": sha256(ROOT / "Cargo.lock") == lock_hash,
        "started_utc": started,
        "argv": argv,
        "cwd": "repository root",
        "rustc": command(["rustc", "--version"]),
        "cargo": command(["cargo", "--version"]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "execution": "sequential fresh setups; one native process; single-threaded protocol",
        "whole_process_seconds_including_cargo_build": elapsed,
        "returncode": process.returncode,
        "stdout_sha256": sha256(destination / "stdout.jsonl"),
        "stderr_sha256": sha256(destination / "stderr.log"),
        "peak_memory": None,
    }
    (destination / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    if process.returncode:
        raise SystemExit("Benchmark process failed; retained stdout, stderr and metadata.")
    rows = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    counts = Counter(row["size"] for row in rows)
    if counts != {64: 3, 256: 3, 1024: 3} or not all(row["accepted"] and row["rounds"] == args.rounds for row in rows):
        raise SystemExit("Benchmark did not produce all nine expected verified results.")
    if not metadata["source_clean_after"] or not metadata["cargo_lock_unchanged"]:
        raise SystemExit("Source changed during the run; records are not accepted as a clean-revision measurement.")
    summary = {"source_revision": revision, "rounds": args.rounds,
               "scope": "Actual default-profile Rust proof bytes for synthetic all-one identity R1CS; no upstream performance or security comparison",
               "sizes": []}
    for size in sorted(counts):
        group = [row for row in rows if row["size"] == size]
        summary["sizes"].append({"size": size, "runs": len(group),
            "proof_bytes_min": min(row["proof_bytes"] for row in group),
            "proof_bytes_max": max(row["proof_bytes"] for row in group),
            **{field + "_median": statistics.median(row[field] for row in group)
               for field in ("prove_ms", "verify_ms", "encode_ms", "decode_ms")}})
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
