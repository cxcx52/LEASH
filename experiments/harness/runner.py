"""Record explicitly configured local commands without invoking a shell.

No environment snapshot, credentials, network client, or SSH deployment is
provided. Caller-configured checks are observations, not semantic verification.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid


SCHEMA_VERSION = 1
REQUIRED = {'argv', 'cwd', 'timeout', 'repetitions', 'label',
            'source_revision', 'evidence_scope'}
OPTIONAL = {'expectations', 'metadata', 'environment_inventory'}
MARKER_KEYS = ('stdout_contains', 'stderr_contains',
               'stdout_not_contains', 'stderr_not_contains')


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def file_identity(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def _nonempty_string(value, name):
    if not isinstance(value, str) or not value.strip() or '\0' in value:
        raise ValueError(f'{name} must be a nonempty string without NUL')


def validate_config(config, base_dir):
    """Return a validated copy; relative paths are relative to the config file."""
    if not isinstance(config, dict):
        raise ValueError('configuration must be a JSON object')
    if REQUIRED - config.keys():
        raise ValueError('missing fields: ' + ', '.join(sorted(REQUIRED - config.keys())))
    if config.keys() - REQUIRED - OPTIONAL:
        raise ValueError('unknown fields: ' + ', '.join(sorted(config.keys() - REQUIRED - OPTIONAL)))
    argv = config['argv']
    if not isinstance(argv, list) or not argv:
        raise ValueError('argv must be a nonempty list; shell command strings are unsupported')
    if any(not isinstance(arg, str) or '\0' in arg for arg in argv) or not argv[0]:
        raise ValueError('argv entries must be strings without NUL, with a nonempty executable')
    for key in ('cwd', 'label', 'source_revision', 'evidence_scope'):
        _nonempty_string(config[key], key)
    timeout = config['timeout']
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout must be a positive finite number of seconds')
    repetitions = config['repetitions']
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError('repetitions must be a positive integer')
    base = Path(base_dir).resolve()
    cwd = Path(config['cwd'])
    cwd = (base / cwd).resolve() if not cwd.is_absolute() else cwd.resolve()
    if not cwd.is_dir():
        raise ValueError(f'cwd is not an existing directory: {cwd}')
    expected = config.get('expectations', {})
    if not isinstance(expected, dict) or expected.keys() - set(MARKER_KEYS) - {'exit_codes'}:
        raise ValueError('expectations supports exit_codes and literal stdout/stderr marker lists')
    if 'exit_codes' in expected:
        codes = expected['exit_codes']
        if not isinstance(codes, list) or not codes or any(isinstance(x, bool) or not isinstance(x, int) for x in codes):
            raise ValueError('expectations.exit_codes must be a nonempty integer list')
    for key in MARKER_KEYS:
        if key in expected:
            markers = expected[key]
            if not isinstance(markers, list):
                raise ValueError(f'expectations.{key} must be a string list')
            for marker in markers:
                _nonempty_string(marker, 'expectations.' + key)
    if 'metadata' in config and not isinstance(config['metadata'], dict):
        raise ValueError('metadata must be a JSON object')
    normalized = json.loads(json.dumps(config, allow_nan=False))
    normalized['cwd'] = str(cwd)
    normalized['timeout'] = float(timeout)
    normalized['expectations'] = expected.copy()
    inventory = config.get('environment_inventory')
    if inventory is not None:
        _nonempty_string(inventory, 'environment_inventory')
        path = Path(inventory)
        path = (base / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file():
            raise ValueError(f'environment_inventory is not an existing file: {path}')
        normalized['environment_inventory'] = str(path)
    return normalized


def load_config(path):
    path = Path(path).resolve()
    return validate_config(json.loads(path.read_text(encoding='utf-8')), path.parent)


def _write_new_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _new_run_directory(output_dir, label, repetition):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^A-Za-z0-9_-]+', '-', label).strip('-')[:48] or 'experiment'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for _ in range(8):
        path = output_dir / f'{stamp}-{slug}-r{repetition:04d}-{uuid.uuid4().hex}'
        try:
            path.mkdir()  # Atomic, never exist_ok: no previous run is reused.
            return path
        except FileExistsError:
            continue
    raise FileExistsError('could not allocate a unique run directory')


def find_gnu_time():
    """Return a verified GNU time executable, or an explicit absence reason."""
    if not sys.platform.startswith('linux'):
        return None, 'GNU time instrumentation is enabled only on Linux'
    candidate = '/usr/bin/time' if Path('/usr/bin/time').is_file() else shutil.which('time')
    if not candidate:
        return None, 'GNU time executable not found'
    try:
        probe = subprocess.run([candidate, '--version'], stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=2, check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f'GNU time capability probe failed: {type(error).__name__}'
    if probe.returncode != 0 or b'gnu time' not in (probe.stdout + probe.stderr).lower():
        return None, 'available time executable is not confirmed GNU time'
    return candidate, None


def _live_group_members(group_id, leader):
    """Linux /proc observation only; never select unrelated groups for killing."""
    members = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdecimal() or int(entry.name) == leader:
            continue
        try:
            stat = (entry / 'stat').read_text(errors='replace')
            fields = stat[stat.rfind(')') + 2:].split()
            # fields start at original stat field 3: state, ppid, pgrp, ...
            if int(fields[2]) == group_id and fields[0] not in ('Z', 'X'):
                members.append(int(entry.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, IndexError):
            continue
    return members


def _terminate_owned_group(process, reason, grace_seconds=0.2):
    """TERM then KILL only this run's new process group, before reaping leader."""
    outcome = {'reason': reason, 'method': 'process_group' if os.name == 'posix' else 'direct_process_only',
               'signals': [], 'grace_seconds': grace_seconds,
               'detached_descendants_supported': False}
    if process.returncode is not None:
        outcome['method'] = 'already_reaped_no_signal'
        return outcome
    if os.name == 'posix':
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
                outcome['signals'].append(sig.name)
            except ProcessLookupError:
                break
            if sig == signal.SIGTERM:
                time.sleep(grace_seconds)
    else:
        # Linux is the process-tree support target. No taskkill or unrelated
        # process enumeration is used on platforms without POSIX groups.
        try:
            process.kill()
            outcome['signals'].append('kill_direct_process')
        except ProcessLookupError:
            pass
    process.wait()
    return outcome


def _wait_for_command(process, timeout):
    deadline = time.monotonic() + timeout
    if sys.platform.startswith('linux') and hasattr(os, 'WNOWAIT'):
        # Keep the leader unreaped until group cleanup is finished. Its PID
        # cannot be recycled into an unrelated process group during cleanup.
        while True:
            status = os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if status is not None:
                remaining = _live_group_members(process.pid, process.pid)
                cleanup = None
                if remaining:
                    cleanup = _terminate_owned_group(process, 'leader_exited_with_group_members')
                    cleanup['live_group_members_observed'] = remaining
                else:
                    process.wait()
                return 'completed', cleanup
            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                return 'timed_out', _terminate_owned_group(process, 'timeout')
            time.sleep(min(0.01, remaining_time))
    try:
        process.wait(timeout=timeout)
        return 'completed', None
    except subprocess.TimeoutExpired:
        return 'timed_out', _terminate_owned_group(process, 'timeout')


def _contains(path, needle):
    needle = needle.encode('utf-8')
    tail = b''
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            combined = tail + chunk
            if needle in combined:
                return True
            tail = combined[-(len(needle)-1):] if len(needle) > 1 else b''
    return False


def evaluate_expectations(expected, record, run_dir):
    checks = []
    if 'exit_codes' in expected:
        checks.append({'kind': 'exit_codes', 'expected': expected['exit_codes'],
                       'observed': record['exit_code'], 'passed': record['exit_code'] in expected['exit_codes']})
    for key in MARKER_KEYS:
        stream = 'stdout' if key.startswith('stdout') else 'stderr'
        absent = '_not_contains' in key
        for marker in expected.get(key, []):
            present = _contains(run_dir / f'{stream}.log', marker)
            checks.append({'kind': key, 'marker': marker, 'passed': not present if absent else present})
    status = 'not_configured' if not checks else (
        'passed' if record['status'] == 'completed' and all(check['passed'] for check in checks) else 'failed')
    return {'status': status, 'checks': checks,
            'meaning': 'Caller-specified observations only; no protocol verification or security conclusion is inferred.'}


def _resource_record(time_binary, unavailable_reason, run_dir):
    resource_file = run_dir / 'gnu-time.log'
    result = {'provider': 'GNU time' if time_binary else None, 'max_rss_kib': None,
              'max_rss_bytes': None, 'unavailable_reason': unavailable_reason,
              'scope': 'GNU time maximum resident set size; not aggregate simultaneous process-tree memory.'}
    if time_binary:
        if resource_file.exists():
            text = resource_file.read_text(encoding='utf-8', errors='replace')
            found = re.findall(r'^HARNESS_MAX_RSS_KIB=(\d+)$', text, flags=re.MULTILINE)
            result['log'] = {'path': resource_file.name, **file_identity(resource_file)}
            if len(found) == 1:
                result['max_rss_kib'] = int(found[0])
                result['max_rss_bytes'] = int(found[0]) * 1024
                result['unavailable_reason'] = None
            else:
                result['unavailable_reason'] = 'GNU time did not produce one complete RSS value, possibly because of termination'
        else:
            result['unavailable_reason'] = 'GNU time resource log absent'
    return result


def run_one(config, output_dir, repetition, resource_capability):
    run_dir = _new_run_directory(output_dir, config['label'], repetition)
    _write_new_json(run_dir / 'config.json', config)
    time_binary, unavailable_reason = resource_capability
    argv = list(config['argv'])
    command = ([time_binary, '-f', 'HARNESS_MAX_RSS_KIB=%M', '-o',
                str(run_dir / 'gnu-time.log'), '--'] + argv) if time_binary else argv
    inventory = config.get('environment_inventory')
    record = {
        'schema_version': SCHEMA_VERSION, 'run_id': run_dir.name,
        'label': config['label'], 'repetition': repetition,
        'argv': argv, 'cwd': config['cwd'], 'timeout_seconds': config['timeout'],
        'source_revision': config['source_revision'], 'source_revision_verified': False,
        'evidence_scope': config['evidence_scope'], 'metadata': config.get('metadata', {}),
        'environment_inventory': ({'path': inventory, **file_identity(inventory)} if inventory else None),
        'started_utc': utc_now(), 'ended_utc': None, 'wall_seconds': None,
        'status': 'launch_error', 'exit_code': None, 'timed_out': False,
        'pid': None, 'process_group': None, 'cleanup': None, 'launch_error': None,
        'semantic_verification': 'not inferred by this harness',
        'environment_variables_recorded': False,
    }
    started = time.perf_counter()
    process = None
    with (run_dir / 'stdout.log').open('xb') as stdout, (run_dir / 'stderr.log').open('xb') as stderr:
        try:
            process = subprocess.Popen(command, cwd=config['cwd'], stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, shell=False,
                                       start_new_session=(os.name == 'posix'))
            record['pid'] = process.pid
            record['process_group'] = process.pid if os.name == 'posix' else None
            record['status'], record['cleanup'] = _wait_for_command(process, config['timeout'])
            record['exit_code'] = process.returncode
        except KeyboardInterrupt:
            record['status'] = 'interrupted'
            if process is not None:
                record['cleanup'] = _terminate_owned_group(process, 'harness_interrupted')
                record['exit_code'] = process.returncode
        except OSError as error:
            record['launch_error'] = {'type': type(error).__name__, 'message': str(error)}
            if process is not None:
                record['cleanup'] = _terminate_owned_group(process, 'harness_os_error')
                record['exit_code'] = process.returncode
    record['wall_seconds'] = time.perf_counter() - started
    record['ended_utc'] = utc_now()
    record['timed_out'] = record['status'] == 'timed_out'
    record['logs'] = {name: {'path': f'{name}.log', **file_identity(run_dir / f'{name}.log')}
                      for name in ('stdout', 'stderr')}
    record['resources'] = _resource_record(time_binary, unavailable_reason, run_dir)
    record['expectations'] = evaluate_expectations(config['expectations'], record, run_dir)
    _write_new_json(run_dir / 'record.json', record)
    return run_dir, record


def run_experiments(config, output_dir, dry_run=False):
    """Execute an already validated config, or print a side-effect-free plan."""
    if dry_run:
        return {'dry_run': True, 'config': config, 'output_directory': str(Path(output_dir).resolve()),
                'processes_started': 0, 'files_written': 0,
                'resource_probe': 'not performed in dry run'}
    capability = find_gnu_time()
    runs = []
    for repetition in range(1, config['repetitions'] + 1):
        directory, record = run_one(config, output_dir, repetition, capability)
        runs.append({'directory': str(directory), 'status': record['status'],
                     'exit_code': record['exit_code'], 'expectations': record['expectations']['status']})
        if record['status'] == 'interrupted':
            break
    return {'dry_run': False, 'runs': runs,
            'meaning': 'Recorded process outcomes and configured checks, not a security or full-verification result.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    result = run_experiments(config, args.output_dir, args.dry_run)
    print(json.dumps(result, indent=2, allow_nan=False))
    if args.dry_run:
        return 0
    if any(run['status'] == 'interrupted' for run in result['runs']):
        return 130
    return 0 if all(run['status'] == 'completed' and run['exit_code'] == 0
                    and run['expectations'] != 'failed' for run in result['runs']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
