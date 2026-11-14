"""Read-only, credential-free hardware/cgroup/toolchain inventory.

No package installation, device mutation, network request, or GPU workload.
Host-visible memory/CPUs are kept separate from container allocation limits.
"""
import argparse
from datetime import datetime, timezone
import glob
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def read_optional(path):
    try:
        return Path(path).read_text(encoding='utf-8').strip()
    except (OSError, UnicodeError):
        return None


def command(argv, timeout=20):
    try:
        done = subprocess.run(argv, capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=timeout)
        return {'argv': argv, 'returncode': done.returncode,
                'stdout': done.stdout[:16000], 'stderr': done.stderr[:4000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'argv': argv, 'returncode': None,
                'unavailable': type(exc).__name__, 'detail': str(exc)}


def inventory():
    cpu_text = read_optional('/proc/cpuinfo') or ''
    cpu_fields = {}
    for line in cpu_text.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            cpu_fields.setdefault(key.strip(), value.strip())
    features = set(cpu_fields.get('flags', '').split())
    relevant = ['avx2', 'avx512f', 'avx512bw', 'avx512vl', 'avx512dq',
                'avx512vbmi', 'avx512_vbmi2', 'avx512_vnni', 'aes', 'vaes']
    cgroup = {name: read_optional('/sys/fs/cgroup/' + name)
              for name in ('cpu.max', 'memory.max', 'memory.current',
                           'cpuset.cpus.effective', 'memory.swap.max')}
    quota_cores = None
    if cgroup['cpu.max']:
        quota, period = cgroup['cpu.max'].split()
        if quota != 'max':
            quota_cores = int(quota) / int(period)
    memlimit = cgroup['memory.max']
    memory_limit_bytes = int(memlimit) if memlimit and memlimit != 'max' else None
    meminfo = read_optional('/proc/meminfo') or ''
    host_memory_kib = next((int(line.split()[1]) for line in meminfo.splitlines()
                            if line.startswith('MemTotal:')), None)
    tools = {}
    for name in ('gcc', 'clang', 'cmake', 'make', 'cargo', 'rustc', 'git'):
        executable = shutil.which(name)
        tools[name] = command([executable, '--version']) if executable else None
    cuda_candidates = [shutil.which('nvcc'), '/usr/local/cuda/bin/nvcc']
    nvcc = next((p for p in cuda_candidates if p and Path(p).is_file()), None)
    smi_candidates = [shutil.which('nvidia-smi'), '/usr/bin/nvidia-smi',
                      '/usr/local/nvidia/bin/nvidia-smi']
    smi = next((p for p in smi_candidates if p and Path(p).is_file()), None)
    torch_probe = '''import importlib.util,json,sys
r={'python':sys.version,'torch_installed':importlib.util.find_spec('torch') is not None}
if r['torch_installed']:
    try:
        import torch
        r.update(torch_version=torch.__version__,build_cuda=torch.version.cuda,
                 cuda_available=torch.cuda.is_available(),cuda_device_count=torch.cuda.device_count())
    except Exception as exc:
        r.update(torch_probe_error=type(exc).__name__+': '+str(exc))
print(json.dumps(r))
'''
    python_executables = list(dict.fromkeys(p for p in
        [sys.executable, '/opt/conda/bin/python', '/usr/bin/python3']
        if Path(p).is_file()))
    storage = shutil.disk_usage(Path.cwd())
    return {
        'schema': 'labrador-environment/v1',
        'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Read-only runtime visibility; no security or benchmark conclusion',
        'platform': {'system': platform.system(), 'release': platform.release(),
                     'machine': platform.machine(), 'os_release': read_optional('/etc/os-release')},
        'cpu': {'model': cpu_fields.get('model name'), 'host_logical_cpus': os.cpu_count(),
                'affinity_logical_cpus': len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
                'cgroup_quota_cores': quota_cores,
                'features': {f: f in features for f in relevant}},
        'memory': {'host_total_kib': host_memory_kib,
                   'cgroup_limit_bytes': memory_limit_bytes},
        'cgroup_v2': cgroup,
        'storage_current_filesystem': {'total_bytes': storage.total, 'free_bytes': storage.free},
        'gpu': {'device_nodes': sorted(glob.glob('/dev/nvidia*')),
                'driver_report': read_optional('/proc/driver/nvidia/version'),
                'visibility_variables': {k: os.environ.get(k) for k in
                      ('CUDA_VISIBLE_DEVICES', 'NVIDIA_VISIBLE_DEVICES')},
                'nvidia_smi': command([smi, '--query-gpu=name,memory.total,driver_version',
                                      '--format=csv,noheader']) if smi else None,
                'nvcc': command([nvcc, '--version']) if nvcc else None},
        'toolchains': tools,
        'python_probes': [command([p, '-c', torch_probe], timeout=40) for p in python_executables],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = inventory()
    encoded = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(encoded)
    print(encoded)


if __name__ == '__main__':
    main()
