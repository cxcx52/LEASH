"""Run bounded CPU reference experiments from a hash-verified source release.

All inputs are deterministic public fixtures. This is a correctness/performance
batch, not a security test, attack workflow, or full compact-protocol benchmark.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.harness.runner import run_experiments, validate_config


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_release(manifest):
    if not isinstance(manifest.get('source_revision'), str) or not manifest.get('files_sha256'):
        raise ValueError('missing release revision or per-file hashes')
    for name, expected in manifest['files_sha256'].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            raise ValueError('unsafe release path')
        path = ROOT.joinpath(*relative.parts)
        if path.is_symlink() or digest(path) != expected:
            raise ValueError('source release mismatch: ' + name)
    return len(manifest['files_sha256'])


def write_new(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment-manifest', type=Path, required=True)
    parser.add_argument('--environment-inventory', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.deployment_manifest.read_text(encoding='utf-8'))
    checked = verify_release(manifest)
    inventory = args.environment_inventory.resolve(strict=True)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    configs = output/'configs'
    configs.mkdir()
    run_root = output/'runs'
    started = datetime.now(timezone.utc).isoformat()
    specs = [
        ('package-tests', [sys.executable, '-c',
         "import sys,unittest;sys.path.insert(0,'src');r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests'));sys.exit(not r.wasSuccessful())"],
         120, 1, 'stderr', 'OK', 'Package regression tests; no security-level inference'),
        ('archive-check', [sys.executable, 'research/scripts/verify_archive.py'],
         60, 1, 'stdout', '"all_checks_passed": true', 'Saved arithmetic and provenance consistency'),
    ]
    for size in (6, 8, 10):
        for seed in (1, 2, 3):
            specs.append((f'native-n{1<<size}-seed{seed}',
                [sys.executable, 'examples/native_frontend_smoke.py', '--log-size', str(size),
                 '--rows', '160', '--seed', str(seed)],
                120, 3, 'stdout', 'NATIVE_FRONTEND_REFERENCE_PASS',
                'Bare native source reduction with full witness and diagnostic source oracle; no recursive core'))
    for seed in (20261114, 20261115, 20261116):
        specs.append((f'energy-membership-seed{seed}',
            [sys.executable, 'benchmarks/challenge_membership.py',
             '--degree','64','--energy','104','--threshold','30','--samples','32','--seed',str(seed)],
            120, 3, 'stdout', 'CHALLENGE_MEMBERSHIP_BENCHMARK_PASS',
            'Exact Python predicate microbenchmark; acceptance count is fixture-only'))
    batch = {
        'schema':'labrador-first-cpu-batch/v1', 'started_utc':started,
        'source_revision':manifest['source_revision'],
        'release_archive_sha256':manifest['archive_sha256'],
        'source_files_hash_verified_before':checked,
        'deployment_manifest_sha256':digest(args.deployment_manifest),
        'environment_inventory_sha256':digest(inventory),
        'environment_inventory':str(inventory),
        'execution_order':'sequential; repeated fresh processes; no affinity pinning',
        'scope':'Functional smoke and preliminary local timings only; no full compact protocol or security certification',
        'experiments':[],
    }
    failed = False
    for label, argv, timeout, repeats, stream, marker, scope in specs:
        config = {
            'argv':argv, 'cwd':str(ROOT), 'timeout':timeout, 'repetitions':repeats,
            'label':label, 'source_revision':manifest['source_revision'],
            'evidence_scope':scope, 'environment_inventory':str(inventory),
            'expectations':{'exit_codes':[0], stream+'_contains':[marker]},
            'metadata':{'release_hash_verified_by_batch':True,
                        'release_archive_sha256':manifest['archive_sha256'],
                        'workload':'public deterministic fixtures',
                        'computational_security_claimed':False},
        }
        config_path = configs/(label+'.json')
        write_new(config_path, config)
        result = run_experiments(validate_config(config, configs), run_root)
        batch['experiments'].append({'label':label, 'config':str(config_path), 'result':result})
        passed = all(r['status']=='completed' and r['exit_code']==0 and r['expectations']=='passed'
                     for r in result['runs'])
        print(json.dumps({'label':label, 'processes':len(result['runs']), 'configured_observations_passed':passed}), flush=True)
        if not passed:
            failed = True
            break
    batch['source_files_hash_verified_after'] = verify_release(manifest)
    batch['ended_utc'] = datetime.now(timezone.utc).isoformat()
    batch['status'] = 'failed' if failed else 'completed'
    batch['all_planned_jobs_executed'] = len(batch['experiments'])==len(specs)
    write_new(output/'batch.json', batch)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
