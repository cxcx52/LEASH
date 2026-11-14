"""Export one committed source revision and its raw-byte deployment manifest."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    revision = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    archive = output/'source.tar'
    with archive.open('xb') as stream:
        subprocess.run(['git','archive','--format=tar',revision],cwd=ROOT,stdout=stream,check=True)
    hashes = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():
                continue
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or '\\' in member.name:
                raise ValueError('unsupported source-archive member: '+member.name)
            hashes[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    manifest = {'schema':'labrador-source-release/v1','source_revision':revision,
                'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                'files_sha256':hashes,
                'scope':'Tracked Git commit only; excludes untracked files, local environments and Git credentials'}
    with (output/'deployment-manifest.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(manifest,stream,indent=2)
        stream.write('\n')
    print(json.dumps({'source_revision':revision,'tracked_files':len(hashes),
                      'archive_sha256':manifest['archive_sha256'],'output_directory':str(output)},indent=2))


if __name__ == '__main__':
    main()
