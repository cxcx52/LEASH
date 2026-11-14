"""Verify imported first-batch records and emit descriptive, scope-limited data."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import statistics
import tarfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def stats(values):
    return {'count':len(values), 'median':statistics.median(values),
            'minimum':min(values), 'maximum':max(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-root', type=Path, required=True)
    parser.add_argument('--source-archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    batches = list((args.import_root/'runs').glob('*/batch.json'))
    require(len(batches)==1, 'expected exactly one batch')
    batch_path = batches[0]
    base = batch_path.parent
    batch = read(batch_path)
    revision = batch['source_revision']
    manifest_path = args.import_root/'bundles'/revision/'deployment-manifest.json'
    inventory_path = args.import_root/'inventory'/'environment-20261114-initial.json'
    manifest, inventory = read(manifest_path), read(inventory_path)
    require(sha(manifest_path)==batch['deployment_manifest_sha256'], 'manifest hash mismatch')
    require(sha(inventory_path)==batch['environment_inventory_sha256'], 'inventory hash mismatch')
    require(sha(args.source_archive)==manifest['archive_sha256']==batch['release_archive_sha256'], 'source tar hash mismatch')
    require(manifest['source_revision']==revision, 'revision mismatch')
    with tarfile.open(args.source_archive) as archive:
        members = [m for m in archive if not m.isdir()]
        require(len(members)==len(manifest['files_sha256']), 'source file count mismatch')
        for member in members:
            require(member.isfile(), 'non-file source member')
            require(hashlib.sha256(archive.extractfile(member).read()).hexdigest()==manifest['files_sha256'][member.name], 'source file mismatch')
    require(batch['status']=='completed' and batch['all_planned_jobs_executed'], 'incomplete batch')
    require(batch['source_files_hash_verified_before']==batch['source_files_hash_verified_after']==len(members), 'remote release verification count mismatch')
    expected = {'package-tests':1, 'archive-check':1}
    expected.update({f'native-n{n}-seed{s}':3 for n in (64,256,1024) for s in (1,2,3)})
    expected.update({f'energy-membership-seed{s}':3 for s in (20261114,20261115,20261116)})
    require({e['label']:len(e['result']['runs']) for e in batch['experiments']}==expected, 'wrong experiment plan')
    native, kernels, provenance, fixtures = defaultdict(list), [], [], defaultdict(set)
    seen = set()
    unit_text = ''
    for experiment in batch['experiments']:
        label = experiment['label']
        for entry in experiment['result']['runs']:
            run_id = PurePosixPath(entry['directory']).name
            require(run_id not in seen, 'duplicate run')
            seen.add(run_id)
            directory = base/'runs'/run_id
            record_path = directory/'record.json'
            record = read(record_path)
            require(record['label']==label and record['run_id']==run_id, 'record identity mismatch')
            require(record['source_revision']==revision and record['environment_inventory']['sha256']==sha(inventory_path), 'record provenance mismatch')
            require(record['exit_code']==0 and record['status']=='completed' and not record['timed_out'] and record['expectations']['status']=='passed', 'unsuccessful process')
            require(all(c['passed'] for c in record['expectations']['checks']), 'failed configured observation')
            for identity in record['logs'].values():
                log = directory/identity['path']
                require(log.stat().st_size==identity['bytes'] and sha(log)==identity['sha256'], 'log hash mismatch')
            provenance.append({'run_id':run_id, 'record_sha256':sha(record_path),
                               'config_sha256':sha(directory/'config.json'), 'logs':record['logs']})
            stdout = (directory/'stdout.log').read_text(encoding='utf-8')
            if label=='package-tests':
                unit_text = (directory/'stderr.log').read_text(encoding='utf-8')
                require(re.search(r'Ran 66 tests in', unit_text) and unit_text.rstrip().endswith('OK'), 'unit suite did not fully pass')
                continue
            data, end = json.JSONDecoder().raw_decode(stdout)
            if label=='archive-check':
                require(data['all_checks_passed'] and data['archived_source_files_checked']==102, 'research archive mismatch')
                continue
            data['harness_wall_seconds'] = record['wall_seconds']
            if label.startswith('native-'):
                require(stdout[end:].strip()=='NATIVE_FRONTEND_REFERENCE_PASS', 'native marker mismatch')
                require(data['status']=='passed' and all(data['checks'].values()) and data['reference_wire_roundtrip'], 'native check failure')
                require(data['transport']['compact_proof_bytes'] is None, 'unexpected compact proof claim')
                fixtures[label].add(data['transport']['full_witness_transport_sha256'])
                native[data['source_n_including_constant']].append(data)
            else:
                require(stdout[end:].strip()=='CHALLENGE_MEMBERSHIP_BENCHMARK_PASS', 'kernel marker mismatch')
                require(data['all_predicate_decisions_match'] and not data['complete_prover_implemented'], 'kernel status mismatch')
                fixtures[label].add(data['fixture_sha256'])
                kernels.append(data)
    require(len(seen)==38 and len(list((base/'runs').glob('*/record.json')))==38, 'missing or extra process record')
    require(all(len(v)==1 for v in fixtures.values()), 'repeated fixture changed')
    native_summary = []
    for n, runs in sorted(native.items()):
        sizes = {r['transport']['bare_source_prover_transport_bytes'] for r in runs}
        require(len(sizes)==1, 'transport sizes differ within n')
        native_summary.append({'n_equals_k':n, 'processes':len(runs), 'seeds':sorted({r['seed'] for r in runs}),
            'all_target_and_oracle_checks_passed':True, 'all_wire_roundtrips_passed':True,
            'bare_source_prover_transport_bytes':sizes.pop(),
            'full_witness_transport_bytes':runs[0]['transport']['full_witness_transport_bytes'],
            'source_commitment_transport_bytes':512, 'source_scalar_transport_bytes':640,
            'source_rank':2, 'source_rows':160,
            'phase_seconds':{key:stats([r['phase_seconds'][key] for r in runs]) for key in runs[0]['phase_seconds']},
            'local_total_wall_seconds':stats([r['local_total_wall_seconds'] for r in runs]),
            'harness_wall_seconds':stats([r['harness_wall_seconds'] for r in runs]),
            'whole_process_peak_rss_kib':stats([r['process_peak_rss_kib'] for r in runs])})
    by_seed = defaultdict(list)
    for data in kernels:
        by_seed[data['configuration']['seed']].append(data)
    per_seed = []
    for seed, runs in sorted(by_seed.items()):
        for key in ('fixture_sha256','accepted_in_this_fixture','fourier_path_counts'):
            require(all(r[key]==runs[0][key] for r in runs), 'kernel repetitions differ')
        per_seed.append({'seed':seed, 'repetitions':len(runs), 'candidates_per_repetition':32,
                         **{key:runs[0][key] for key in ('fixture_sha256','accepted_in_this_fixture','fourier_path_counts')}})
    summary = {'schema':'labrador-first-cpu-summary/v1', 'source_revision':revision,
        'source_archive_sha256':manifest['archive_sha256'], 'batch_sha256':sha(batch_path),
        'inventory_sha256':sha(inventory_path), 'verified_source_files':len(members),
        'started_utc':batch['started_utc'], 'ended_utc':batch['ended_utc'],
        'process_count':38, 'package_tests':{'run':66,'failures':0,'skipped':0},
        'research_archive_files_verified':102, 'environment':{
            'cpu':inventory['cpu'], 'cgroup_memory_limit_bytes':inventory['memory']['cgroup_limit_bytes'],
            'gpu_device_nodes':inventory['gpu']['device_nodes'], 'python':'3.12.3',
            'execution':'Sequential fresh Python processes; one thread per reference workload; no affinity pinning'},
        'native':native_summary, 'kernel':{
            'degree':64,'energy':104,'strict_operator_threshold':30, 'processes':9,
            'fixture_candidate_positions':96, 'candidate_evaluations_with_repetitions':288,
            'all_decisions_match':True, 'per_seed':per_seed,
            'warm_seconds_for_32_inputs':{k:stats([r['warm_predicate_timings'][k] for r in kernels]) for k in kernels[0]['warm_predicate_timings']},
            'warm_spd_over_fourier_ratio_per_process':stats([r['warm_spd_over_fourier_time_ratio'] for r in kernels]),
            'cold_table_initialization_and_zero_query_seconds':stats([r['cold_first_fourier_call_seconds'] for r in kernels]),
            'whole_process_peak_rss_kib':stats([r['process_peak_rss_kib'] for r in kernels])},
        'limits':[
            'Native workload is a deterministic honest toy with fitted C and source rank 2; sends complete witness.',
            'Native check time includes a direct source oracle; encoding time also includes diagnostic JSON construction.',
            'Kernel repeats reuse each seed fixture; 288 is not an independent sample count.',
            'Fourier fallback shares the exact SPD routine; fallback agreement is not independent.',
            'Timings are descriptive single-host observations; no confidence intervals or end-to-end speedup claim.',
            'No recursive core, full compact SNARK, Fiat-Shamir, computational-security estimate or GPU benchmark.',
            'Deployment file checks are recorded by the batch runner; record hashes establish consistency, not external attestation.'
        ], 'records':provenance}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(summary,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps({'processes':38,'native_processes':27,'kernel_processes':9,'output':str(args.output)},indent=2))


if __name__ == '__main__':
    main()
