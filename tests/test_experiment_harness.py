"""Recorder contract tests, independent of protocol or security claims."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from experiments.harness import runner


class ExperimentHarness(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='labrador-harness-')
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def config(self, code, **changes):
        value = dict(argv=[sys.executable, '-c', code], cwd='.', timeout=5,
                     repetitions=1, label='functional smoke', source_revision='test-fixture',
                     evidence_scope='Harness contract checks only')
        value.update(changes)
        return runner.validate_config(value, self.root)

    def execute(self, config):
        with patch.object(runner, 'find_gnu_time', return_value=(None, 'test without instrumentation')):
            summary = runner.run_experiments(config, self.root / 'runs')
        path = Path(summary['runs'][0]['directory'])
        return path, json.loads((path / 'record.json').read_text())

    def test_validation_and_dry_run_are_side_effect_free(self):
        config = self.config("print('unused')")
        for invalid in ({'argv': 'echo hello'}, {'timeout': float('inf')},
                        {'timeout': True}, {'repetitions': 0}, {'cwd': 'absent'},
                        {'argv': ['python', '\0']}, {'env': {'SECRET': 'not accepted'}}):
            bad = dict(config, **invalid)
            with self.assertRaises(ValueError):
                runner.validate_config(bad, self.root)
        output = self.root / 'does-not-exist'
        with patch.object(runner, 'find_gnu_time', side_effect=AssertionError('probe')):
            with patch.object(runner.subprocess, 'Popen', side_effect=AssertionError('execution')):
                plan = runner.run_experiments(config, output, dry_run=True)
        self.assertEqual(plan['processes_started'], 0)
        self.assertFalse(output.exists())

    def test_logs_hashes_inventory_and_unique_repetitions(self):
        inventory = self.root / 'inventory.json'
        inventory.write_bytes(b'{"cpu":"public-test"}\n')
        payload = b'OK\x00\xff\n'
        code = "import sys; sys.stdout.buffer.write(b'OK\\x00\\xff\\n'); sys.stderr.write('DIAGNOSTIC\\n')"
        config = self.config(code, repetitions=2, environment_inventory='inventory.json',
                             expectations={'exit_codes': [0], 'stdout_contains': ['OK'],
                                           'stderr_contains': ['DIAGNOSTIC'],
                                           'stderr_not_contains': ['ERROR']})
        with patch.object(runner, 'find_gnu_time', return_value=(None, 'not present')):
            first = runner.run_experiments(config, self.root / 'runs')
            second = runner.run_experiments(config, self.root / 'runs')
        paths = [Path(run['directory']) for run in first['runs'] + second['runs']]
        self.assertEqual(len(set(paths)), 4)
        for path in paths:
            record = json.loads((path / 'record.json').read_text())
            self.assertEqual((path / 'stdout.log').read_bytes(), payload)
            self.assertEqual(record['logs']['stdout']['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertEqual(record['logs']['stdout']['bytes'], len(payload))
            self.assertEqual(record['environment_inventory']['sha256'], hashlib.sha256(inventory.read_bytes()).hexdigest())
            self.assertEqual(record['expectations']['status'], 'passed')
            self.assertFalse(record['source_revision_verified'])
            self.assertFalse(record['environment_variables_recorded'])
            self.assertIsNone(record['resources']['max_rss_kib'])
            self.assertEqual(record['resources']['unavailable_reason'], 'not present')
            self.assertTrue(record['started_utc'].endswith('Z'))
            self.assertTrue(record['ended_utc'].endswith('Z'))
            self.assertGreaterEqual(record['wall_seconds'], 0)

    def test_exit_zero_is_not_verification_and_markers_can_fail(self):
        _, unconfigured = self.execute(self.config("print('hello')"))
        self.assertEqual(unconfigured['status'], 'completed')
        self.assertEqual(unconfigured['expectations']['status'], 'not_configured')
        self.assertEqual(unconfigured['semantic_verification'], 'not inferred by this harness')
        _, missing = self.execute(self.config("print('hello')", expectations={'stdout_contains': ['INDEPENDENT_CHECK_OK']}))
        self.assertEqual(missing['exit_code'], 0)
        self.assertEqual(missing['expectations']['status'], 'failed')
        _, nonzero = self.execute(self.config('raise SystemExit(7)', expectations={'exit_codes': [7]}))
        self.assertEqual(nonzero['exit_code'], 7)
        self.assertEqual(nonzero['expectations']['status'], 'passed')

    def test_no_shell_and_launch_failure_records(self):
        literal = '; echo not-a-shell && $(not-executed)'
        config = self.config('import sys; print(sys.argv[1])')
        config['argv'].append(literal)
        path, record = self.execute(config)
        self.assertEqual((path / 'stdout.log').read_text().strip(), literal)
        self.assertEqual(record['exit_code'], 0)
        bad = self.config('unused')
        bad['argv'] = [str(self.root / 'absent-executable')]
        _, failed = self.execute(bad)
        self.assertEqual(failed['status'], 'launch_error')
        self.assertIsNone(failed['exit_code'])
        self.assertEqual(failed['logs']['stdout']['bytes'], 0)

    def test_timeout_has_a_record_even_if_marker_was_printed(self):
        _, record = self.execute(self.config("import time; print('MARK', flush=True); time.sleep(30)",
                                             timeout=0.3, expectations={'stdout_contains': ['MARK']}))
        self.assertEqual(record['status'], 'timed_out')
        self.assertTrue(record['timed_out'])
        self.assertEqual(record['expectations']['status'], 'failed')
        self.assertIsNotNone(record['exit_code'])
        self.assertLess(record['wall_seconds'], 10)

    def test_literal_marker_crosses_streaming_chunk_boundary(self):
        path = self.root / 'large.log'
        path.write_bytes(b'x' * (1024 * 1024 - 2) + b'BOUNDARY' + b'y')
        self.assertTrue(runner._contains(path, 'BOUNDARY'))
        self.assertFalse(runner._contains(path, 'missing'))

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux process-group ownership contract')
    def test_linux_timeout_kills_grandchild_but_not_unrelated_process(self):
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                                     start_new_session=True, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        pid_path = self.root / 'grandchild.pid'
        child = 'import os,sys,time; from pathlib import Path; Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(30)'
        parent = ('import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",'
                  + repr(child) + ',' + repr(str(pid_path)) + ']); time.sleep(30)')
        try:
            _, record = self.execute(self.config(parent, timeout=0.8))
            self.assertEqual(record['status'], 'timed_out')
            self.assertEqual(record['cleanup']['method'], 'process_group')
            self.assertTrue(pid_path.exists(), 'grandchild never launched')
            grandchild = int(pid_path.read_text())
            stat = Path(f'/proc/{grandchild}/stat')
            if stat.exists():
                state = stat.read_text().split(')')[-1].split()[0]
                self.assertIn(state, ('Z', 'X'), 'grandchild remained live')
            self.assertIsNone(unrelated.poll(), 'unrelated process was killed')
        finally:
            unrelated.kill()
            unrelated.wait()

    @unittest.skipUnless(sys.platform.startswith('linux'), 'GNU time is supported on Linux')
    def test_available_gnu_time_has_explicit_units(self):
        capability = runner.find_gnu_time()
        path, record = runner.run_one(self.config("print('RESOURCE_OK')"), self.root / 'runs', 1, capability)
        if capability[0]:
            self.assertIsInstance(record['resources']['max_rss_kib'], int)
            self.assertEqual(record['resources']['max_rss_bytes'], record['resources']['max_rss_kib'] * 1024)
            identity = record['resources']['log']
            self.assertEqual(identity['sha256'], hashlib.sha256((path / identity['path']).read_bytes()).hexdigest())
        else:
            self.assertIsNone(record['resources']['max_rss_kib'])
            self.assertTrue(record['resources']['unavailable_reason'])


if __name__ == '__main__':
    unittest.main()
