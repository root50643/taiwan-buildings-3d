#!/usr/bin/env python3
"""Tiny replay-entry controls; no real model inputs or model computation."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import lzma
import os
from pathlib import Path
import sys
import tarfile


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.out)
    root.mkdir(exist_ok=False)
    tool = Path(__file__).with_name('prepare_control_replay.py')
    sys.path.insert(0, str(tool.parent))
    spec = importlib.util.spec_from_file_location('prepare_control_replay_under_test', tool)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    real_verify, real_extract = module.verify, module.extract_new
    helper_names = ['verification/' + name for name in (
        'check_controls.py', 'check_dense_surface.py', 'check_intersection_controls.py',
        'check_original_intersections.py', 'check_raw_mesh.py', 'check_sections.py',
        'dense_original.cpp', 'qa_common.py', 'run_qa.py')]
    helper_names += ['independent-tools/' + name for name in (
        'diagnose_recorded_cpp_rays.py', 'exact_ray_diagnosis.py', 'png_exact_compare.py',
        'sanitize_png_previews.py', 'postflight_acceptance.py')]
    entries = [('audit/original-hex-box/baseline.bin', b'synthetic baseline\0'),
               ('predicate-review/control.py', b'# synthetic replay control\n'),
               ('predicate-review/observed/result.json', b'{"observed": true}\n')]
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, data in entries:
            item = tarfile.TarInfo(name)
            item.size, item.mode = len(data), 0o644
            item.uid = item.gid = item.mtime = 0
            item.uname = item.gname = ''
            archive.addfile(item, io.BytesIO(data))
    tar = stream.getvalue()
    compressed = lzma.compress(tar, format=lzma.FORMAT_XZ, preset=0)
    index = {'format': 'bwbc-controls-ustar-xz-v1', 'archive_sha256': sha(compressed),
             'tar_sha256': sha(tar), 'members': [
                 {'path': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in entries]}
    cases = ['valid_fresh_replay', 'late_archive_substitution', 'late_index_substitution',
             'missing_helper', 'helper_content_mismatch', 'archive_content_mismatch',
             'existing_output']
    reports = []
    for label in cases:
        directory = root / label
        package = directory / 'qa'
        package.mkdir(parents=True)
        files = {'controls.tar.xz': compressed,
                 'controls-index.json': (json.dumps(index, sort_keys=True) + '\n').encode()}
        files.update({name: ('# synthetic helper ' + name + '\n').encode() for name in helper_names})
        manifest = {name: {'bytes': len(data), 'sha256': sha(data)} for name, data in files.items()}
        if label == 'missing_helper':
            del manifest[helper_names[0]]
        if label == 'helper_content_mismatch':
            files[helper_names[0]] += b'changed\n'
        if label == 'archive_content_mismatch':
            files['controls.tar.xz'] += b'changed'
        for name, data in files.items():
            path = package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (package / 'FILES-SHA256.json').write_text(json.dumps(manifest, sort_keys=True) + '\n')
        output = directory / 'replay'
        if label == 'existing_output':
            output.mkdir()
            (output / 'sentinel').write_bytes(b'unchanged')
        calls = {'verify': 0, 'extract': 0}

        def verified(archive_path, index_path):
            calls['verify'] += 1
            result, payload, records = real_verify(archive_path, index_path)
            # Model a second-read swap: verify returns different actual-input SHA.
            # This is deliberately a mock bridge check, not a timed filesystem race.
            if label == 'late_archive_substitution':
                result['archive_sha256'] = 'f' * 64
            elif label == 'late_index_substitution':
                result['index_sha256'] = 'f' * 64
            return result, payload, records

        def extracted(out, payload, records):
            calls['extract'] += 1
            return real_extract(out, payload, records)

        module.verify, module.extract_new = verified, extracted
        original_argv = sys.argv
        stdout = io.StringIO()
        error = None
        try:
            sys.argv = [tool.name, '--qa', str(package), '--out', str(output)]
            with contextlib.redirect_stdout(stdout):
                module.main()
        except Exception as caught:
            error = type(caught).__name__ + ': ' + str(caught)
        finally:
            sys.argv = original_argv
        accepted = label == 'valid_fresh_replay'
        check((error is None) == accepted, label + ': unexpected acceptance/rejection')
        if accepted:
            check(calls == {'verify': 1, 'extract': 1}, label + ': invocation count')
            expected = sorted(helper_names + [entries[0][0], entries[1][0], 'REPLAY-INPUTS.json'])
            actual = sorted(p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file())
            check(actual == expected, label + ': replay membership mismatch')
            check(not (output / entries[2][0]).exists(), label + ': old observed output copied')
            for name in helper_names:
                check((output / name).read_bytes() == files[name], label + ': helper bytes differ')
            replay_report = json.loads((output / 'REPLAY-INPUTS.json').read_text())
            check(replay_report['archive_validation']['archive_sha256'] == sha(compressed),
                  label + ': missing archive binding')
        elif label == 'existing_output':
            check(calls['extract'] == 1 and isinstance(error, str) and error.startswith('FileExistsError:'),
                  label + ': wrong existing-output refusal')
            check(list(output.iterdir()) == [output / 'sentinel'] and
                  (output / 'sentinel').read_bytes() == b'unchanged', label + ': existing output changed')
        else:
            check(calls['extract'] == 0 and not output.exists(), label + ': rejection after extraction')
            if label.startswith('late_'):
                check('changed after package integrity check' in error, label + ': wrong failure gate')
        report = {'case': label, 'expected_accept': accepted, 'passed': True,
                  'calls': calls, 'error': error,
                  'stdout': json.loads(stdout.getvalue()) if stdout.getvalue() else None}
        encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
        check(not any(private in encoded for private in ('/workspace/', '/home/', '/tmp/')),
              label + ': private path in public report')
        (directory / 'result.json').write_text(encoded)
        reports.append(report)
    module.verify, module.extract_new = real_verify, real_extract
    result = {'passed': True, 'case_count': len(reports), 'python_optimized': bool(sys.flags.optimize),
              'tool': tool.name, 'tool_sha256': sha(tool.read_bytes()),
              'archive_validator_sha256': sha(tool.with_name('archive_verify.py').read_bytes()),
              'cases': reports}
    (root / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
