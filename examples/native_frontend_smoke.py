"""Run one bounded, deterministic, honest bare native-frontend reference case."""
import argparse
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))

from labrador_repair.native_reference import benchmark_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log-size',type=int,choices=range(6,11),default=6)
    parser.add_argument('--seed',type=int,default=1)
    parser.add_argument('--rows',type=int,choices=(16,160),default=160)
    args = parser.parse_args()
    report = benchmark_report(args.log_size,args.seed,args.rows)
    report['platform'] = platform.platform()
    report['python'] = platform.python_version()
    if sys.platform.startswith('linux'):
        import resource
        report['process_peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report['process_peak_rss_scope'] = 'Entire Python process through reporting, including setup, checking and encoding'
    else:
        report['process_peak_rss_kib'] = None
        report['process_peak_rss_scope'] = 'Not measured: this RSS field is defined only on Linux'
    print(json.dumps(report,indent=2,allow_nan=False))
    if report['status'] != 'passed':
        return 1
    print('NATIVE_FRONTEND_REFERENCE_PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
