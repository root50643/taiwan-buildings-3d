"""Restore the sealed public control selection and replay its original archive tools.
Caller owns the single shared qa/.heavy.lock and pins this process to one CPU.
No model science, synthetic suite, rendering, or CSV copying is performed.
"""
import argparse, ast, hashlib, json, os, stat, subprocess, sys, tempfile, types
from pathlib import Path

VERIFIER_SHA = '1af27c8212057503323899b7a5f9f9171de42f78a28ff1e3e07f82d688e021fd'
BUILDER_SHA = 'e4b23d35449c6321abbfea94e85f4d733ce58be65658255e1e5ba5065b33f637'
RESTORE_SHA = '60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e'
PRIMITIVES_SHA = '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273'
CAPTURE_SHA = 'f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244'
BUILDER_MEMBER = 'independent/reuse-preflight-v1/tooling/tools/build_controls_archive.py'
FORMAT = 'original-stl-controls-ustar-xz-v1'
LIMIT = 536870912

def need(value, message):
    if not value:
        raise ValueError(message)
def digest(data):
    return hashlib.sha256(data).hexdigest()
def sha(path):
    return digest(Path(path).read_bytes())
def write(path, data):
    with Path(path).open('xb') as stream:
        stream.write(data)
def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
def regular_tree(root, members):
    actual = []
    for path in root.rglob('*'):
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        need(stat.S_ISREG(mode), 'Nonregular staged/extracted member')
        actual.append(path.relative_to(root).as_posix())
    need(sorted(actual) == [row['path'] for row in members], 'Complete member path set differs')
    for row in members:
        data = (root / row['path']).read_bytes()
        need(len(data) == row['bytes'] and digest(data) == row['sha256'], 'Actual member bytes differ')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root', type=Path, required=True)
    ap.add_argument('--copy-map', default='qa/NEW-CONTROLS-STAGING-MAP.json')
    ap.add_argument('--selection', default='qa/NEW-CONTROLS-SELECTION.json')
    ap.add_argument('--expected-map-sha256', required=True)
    ap.add_argument('--expected-selection-sha256', required=True)
    ap.add_argument('--capture-source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need(len(os.sched_getaffinity(0)) == 1 and sys.flags.optimize == 0, 'Normal parent and one CPU required')
    root, out = args.public_root.absolute(), args.out.absolute()
    need(not out.exists() and not out.is_symlink(), 'Fresh private output required')
    need(root not in out.parents and out not in root.parents and root != out, 'Public and private trees overlap')
    own_sha = sha(__file__)
    restore = root / 'qa/restore_scientific_layout.py'
    primitives = root / 'qa/roster_primitives.py'
    verifier = root / 'qa/tools/archive_verify.py'
    builder = root / 'qa/tools/build_controls_archive.py'
    sources = {restore: RESTORE_SHA, primitives: PRIMITIVES_SHA, verifier: VERIFIER_SHA,
               builder: BUILDER_SHA, args.capture_source: CAPTURE_SHA}
    source_bytes = {}
    for path, expected in sources.items():
        need(path.is_file() and not path.is_symlink(), 'Trusted source is not regular')
        source_bytes[path] = path.read_bytes()
        need(digest(source_bytes[path]) == expected, 'Trusted source identity differs')
    # Load the exact controlled restorer; its fixed helper verifies every ancestor.
    module = types.ModuleType('exact_public_restorer')
    module.__file__ = str(restore)
    exec(compile(source_bytes[restore], str(restore), 'exec'), module.__dict__)
    for relative in [args.copy_map, args.selection]:
        module.safe_relative(relative)
    read_public = module._m._read_regular_snapshot
    map_bytes = read_public(root, args.copy_map, None, 16 * 1024 * 1024)
    selection_bytes = read_public(root, args.selection, None, 16 * 1024 * 1024)
    need(digest(map_bytes) == args.expected_map_sha256 and digest(selection_bytes) == args.expected_selection_sha256,
         'Actual public map/selection differs from sealed identities')
    mapping, selection = module.parse(map_bytes), module.parse(selection_bytes)
    module.validated_map(mapping)
    need(selection.get('schema') == 'wfu-new-control-logical-selection-v1' and
         mapping['copy_map'] == selection['files'], 'Map and selection differ')
    need(all(row.get('new_controls_member') is True and '.csv' not in row['restore_path'].lower()
             and '.csv' not in row['canonical_public_path'].lower() for row in selection['files']),
         'Only new controls are allowed; no CSV source or member')
    members = sorted([{'path': row['restore_path'], 'bytes': row['bytes'], 'sha256': row['sha256']}
                      for row in selection['files']], key=lambda row: row['path'])
    need(sum(row['bytes'] for row in members) < LIMIT, 'Unchanged generic archive size limit exceeded')
    need(any(row['path'] == BUILDER_MEMBER and row['sha256'] == BUILDER_SHA for row in members),
         'Original builder is absent from selected members')
    # The controlled writer owns destination safety; create only the private parent here.
    module._m.write_new_tree(out, [])
    assignments = [node for node in ast.parse(source_bytes[args.capture_source]).body
                   if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'BOOT'
                                                          for target in node.targets)]
    need(len(assignments) == 1, 'One original controlled BOOT required')
    boot = out / 'runtime_launcher.py'
    write(boot, ast.literal_eval(assignments[0].value).encode())
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        env[key] = '1'
    runtimes = []
    def child(label, target, arguments, level):
        record = out / (label + '.runtime.json')
        expected_source = sha(target)
        command = [sys.executable, '-B', *(['-O'] if level else []), str(boot), str(record), str(target), *arguments]
        completed = subprocess.run(command, capture_output=True, env=env)
        write(out / (label + '.stdout.log'), completed.stdout)
        write(out / (label + '.stderr.log'), completed.stderr)
        need(record.is_file(), 'Actual child runtime missing')
        actual = json.loads(record.read_bytes())
        need(type(actual['optimization_level']) is int and actual['optimization_level'] == level
             and actual['cpu_affinity'] == sorted(os.sched_getaffinity(0))
             and actual['python_executable'] == sys.executable
             and actual['target_sha256'] == expected_source == sha(target)
             and actual['target_arguments'] == arguments, 'Actual child mode/CPU/source/arguments differ')
        runtimes.append({'stage': label, 'optimization_level': actual['optimization_level'],
                         'cpu_affinity': actual['cpu_affinity'], 'target_source_sha256': expected_source,
                         'actual_arguments_verified': True, 'python_executable_verified': True,
                         'private_runtime_record_sha256': sha(record),
                         'stdout_sha256': digest(completed.stdout), 'stderr_sha256': digest(completed.stderr),
                         'returncode': completed.returncode})
        need(completed.returncode == 0, 'Original child tool failed: ' + label)
        result = json.loads(completed.stdout)
        need(result.get('passed') is True, 'Original child did not pass: ' + label)
        return result
    stage = out / 'selected-controls-stage'
    restored = child('public-restore', restore, ['--public-root', str(root), '--copy-map', args.copy_map,
                                                '--out', str(stage)], 0)
    need(restored['copy_map_sha256'] == args.expected_map_sha256 and restored['restore_source_sha256'] == RESTORE_SHA
         and restored['logical_files_restored'] == len(members) and restored['all_written_bytes_reauthenticated'] is True,
         'Restore completion/binding differs')
    regular_tree(stage, members)
    original_builder = types.ModuleType('exact_original_archive_builder')
    original_builder.__file__ = str(builder)
    exec(compile(source_bytes[builder], str(builder), 'exec'), original_builder.__dict__)
    raw, archive_bytes = original_builder.make_archive(stage, members)
    need(len(raw) <= LIMIT, 'Unchanged generic decoded archive limit exceeded')
    index = {'format': FORMAT, 'archive_sha256': digest(archive_bytes), 'tar_sha256': digest(raw), 'members': members}
    archive, index_path = out / 'controls.tar.xz', out / 'controls-index.json'
    write(archive, archive_bytes)
    write(index_path, encode(index))
    modes = {}
    for name, level in [('normal', 0), ('optimized', 1)]:
        with tempfile.TemporaryDirectory(dir=out, prefix=name + '-replay-') as temporary:
            temporary = Path(temporary)
            extracted, rebuilt = temporary / 'extracted', temporary / 'rebuilt.tar.xz'
            vr = child(name + '-verify', verifier, ['--archive', str(archive), '--index', str(index_path),
                                                   '--out', str(extracted)], level)
            need(vr.get('extracted') is True and vr['archive_sha256'] == index['archive_sha256'], 'Safe extraction differs')
            regular_tree(extracted, members)
            extracted_builder = extracted / BUILDER_MEMBER
            need(sha(extracted_builder) == BUILDER_SHA, 'Extracted original builder differs')
            br = child(name + '-rebuild', extracted_builder, ['--root', str(extracted), '--index', str(index_path),
                                                             '--out', str(rebuilt)], level)
            need(rebuilt.read_bytes() == archive_bytes and br['tar_sha256'] == index['tar_sha256'], 'Rebuild is not bitwise exact')
            modes[name] = {'optimization_level': level, 'safe_validation_and_extraction': vr, 'rebuild': br,
                           'all_member_bytes_rehashed': True, 'archive_bitwise_identical': True}
    regular_tree(stage, members)
    need(archive.read_bytes() == archive_bytes and index_path.read_bytes() == encode(index), 'Private archive/index changed')
    need(read_public(root, args.copy_map, None, 16 * 1024 * 1024) == map_bytes and
         read_public(root, args.selection, None, 16 * 1024 * 1024) == selection_bytes, 'Public map/selection changed')
    for row in mapping['files']:
        module.read_exact(root, row['canonical_public_path'], row)
    for path, expected in sources.items():
        need(sha(path) == expected, 'Original source changed during replay')
    need(sha(__file__) == own_sha, 'Orchestrator changed during replay')
    report = {'schema': 'wfu-public-new-controls-deterministic-replay-v1', 'passed': True,
              'model_go': False, 'publication_go': False, 'original_numerical_strict_passed': False,
              'actual_public_tree_used': True, 'public_copy_map_sha256': digest(map_bytes),
              'public_selection_sha256': digest(selection_bytes), 'canonical_files': len(mapping['files']),
              'logical_members': len(members), 'archive_sha256': index['archive_sha256'],
              'index_sha256': sha(index_path), 'tar_sha256': index['tar_sha256'],
              'archive_bytes': len(archive_bytes), 'tar_bytes': len(raw), 'modes': modes,
              'actual_child_runtime': runtimes, 'runtime_capture_source_sha256': CAPTURE_SHA,
              'runtime_boot_sha256': sha(boot), 'orchestration_source_sha256': own_sha,
              'restore_source_sha256': RESTORE_SHA, 'verifier_source_sha256': VERIFIER_SHA,
              'builder_source_sha256': BUILDER_SHA, 'all_public_inputs_and_tools_unchanged': True,
              'generic_decoded_byte_limit_unchanged': LIMIT, 'synthetic_suites_rerun': False,
              'scope': 'Actual canonical public payload restored into the sealed small control layout, then original deterministic archive creation and both-mode safe extraction/all-member rehash/bitwise rebuild. Public JSON projections remain explicitly labeled projections; no original private labels are invented. The compressed archive remains private.'}
    write(out / 'replay-proof.json', encode(report))
    print(json.dumps({key: report[key] for key in ['passed', 'logical_members', 'archive_sha256', 'index_sha256', 'tar_sha256']}))

if __name__ == '__main__':
    main()
