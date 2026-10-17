"""Run case-specific logical restore sequentially in both captured Python modes.
The original restorer/helpers remain byte-identical. One pinned history archive
is hardlinked rather than newly allocated. Successful derived trees alone are
removed, after exact fileset/type/size/SHA verification. No archive decoding.
"""
from pathlib import Path
import argparse, ast, hashlib, json, os, shutil, subprocess, sys, types
sys.dont_write_bytecode = True
CASE_RESTORE_SHA = '9cc1954fea71ed83425f3e3c58db60b1b69f65cdbe2460d624b19f651d7613c4'
PINS = {'qa/restore_scientific_layout.py': '60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e',
        'qa/roster_primitives.py': '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273',
        'qa/independent-tools/capture_process.py': 'f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244'}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--archive-source', type=Path, required=True)
    ap.add_argument('--archive-proof', type=Path, required=True)
    a = ap.parse_args()
    root, out = a.public_root.absolute(), a.out.absolute()
    own = sha(__file__)
    target = Path(__file__).absolute().with_name('restore_low_disk.py')
    target_sha = sha(target)
    require(target_sha == CASE_RESTORE_SHA, 'Reviewed case restore source differs')
    # Captured target bytes are rechecked before and after both children.
    low = types.ModuleType('case_low_disk_restore')
    low.__file__ = str(target)
    raw = target.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == target_sha, 'Case target changed')
    exec(compile(raw, str(target), 'exec'), low.__dict__)
    require(low.MAP_SHA is not None and low.CANONICAL_COUNT is not None and low.LOGICAL_COUNT is not None,
            'Final case map identity has not been pinned; actual replay is disabled')
    require(len(os.sched_getaffinity(0)) == 1, 'Single CPU required')
    require(not out.is_relative_to(root) and not root.is_relative_to(out) and not out.exists(),
            'Fresh independent result directory required')
    with low.DirectoryChain(out.parent) as parent:
        s = os.fstat(parent.fd)
        require(s.st_uid == os.geteuid() and not s.st_mode & 0o022, 'Unsafe result parent')
        parent.check()
    originals = {p: low.read_source(root / p, h) for p, h in PINS.items()}
    mapping = low.read_source(root / 'qa/PUBLIC-COPY-MAP.json', low.MAP_SHA, 16 * 1024 * 1024)
    original = low.load_original(root / 'qa/restore_scientific_layout.py')
    d = original.parse(mapping)
    require(len(d['files']) == low.CANONICAL_COUNT and len(d['copy_map']) == low.LOGICAL_COUNT,
            'Exact map counts differ')
    _, files, targets = low.split_map(original, d)
    low.verify_official_proof(original, a.archive_proof, a.archive_source)
    disk = [low.disk_checkpoint(out.parent, 'before_replay', 2 * 1024 * 1024)]
    out.mkdir(mode=0o700)
    nodes = [n for n in ast.parse(originals['qa/independent-tools/capture_process.py']).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BOOT' for t in n.targets)]
    require(len(nodes) == 1, 'Exact original BOOT absent')
    boot = out / 'runtime_launcher.py'
    boot.write_text(ast.literal_eval(nodes[0].value))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    rows = []
    for mode, level in [('normal', 0), ('optimized', 1)]:
        derived = out / ('derived-' + mode)
        runtime = out / (mode + '.runtime.json')
        resultpath = out / (mode + '.result.json')
        args = ['--public-root', str(root), '--out', str(derived),
                '--archive-source', str(a.archive_source.absolute()), '--archive-proof', str(a.archive_proof.absolute())]
        command = [sys.executable, '-B', *(['-O'] if level else []), str(boot), str(runtime), str(target), *args]
        p = subprocess.run(command, capture_output=True, text=True, env=env)
        for label, value in [('stdout', p.stdout), ('stderr', p.stderr)]:
            with (out / (mode + '.' + label + '.log')).open('x') as f:
                f.write(value)
        (out / (mode + '.exit.txt')).write_text(str(p.returncode) + '\n')
        require(p.returncode == 0, 'Case restore failed; its incomplete derived tree is retained')
        actual = json.loads(runtime.read_text())
        require(type(actual['optimization_level']) is int and actual['optimization_level'] == level and
                actual['cpu_affinity'] == sorted(os.sched_getaffinity(0)) and actual['python_executable'] == sys.executable and
                actual['target'] == str(target) and actual['target_sha256'] == target_sha and
                actual['target_arguments'] == args, 'Actual child runtime differs')
        result = original.parse(p.stdout)
        require(result['passed'] is True and result['all_written_bytes_reauthenticated'] is True and
                result['complete_logical_fileset_type_size_sha256_verified'] is True and
                result['canonical_files_verified'] == low.CANONICAL_COUNT and
                result['logical_files_restored'] == low.LOGICAL_COUNT and
                result['newly_written_logical_files'] == low.LOGICAL_COUNT - 1 and
                result['hardlinked_logical_files'] == 1 and result['copy_map_sha256'] == low.MAP_SHA and
                result['restore_source_sha256'] == low.RESTORE_SHA, 'Complete actual logical restore absent')
        # Parent independently verifies the complete roster before destructive cleanup.
        verified = low.verify_tree(derived, targets)
        require(verified == result['files'], 'Parent and child complete roster differs')
        dump(resultpath, result)
        disk.append(low.disk_checkpoint(out.parent, 'before_' + mode + '_cleanup'))
        shutil.rmtree(derived)
        require(not derived.exists(), 'Own successful derived tree was not removed')
        low.read_source(a.archive_source, low.ARCHIVE['sha256'], low.MAX_FILE)
        disk.append(low.disk_checkpoint(out.parent, 'after_' + mode + '_cleanup'))
        rows.append({'mode': mode, 'actual_optimization_level': level, 'actual_cpu_affinity': actual['cpu_affinity'],
                     'returncode': p.returncode, 'result_sha256': sha(resultpath),
                     'runtime_record_sha256': sha(runtime), 'stdout_sha256': sha(out / (mode + '.stdout.log')),
                     'stderr_sha256': sha(out / (mode + '.stderr.log')),
                     'runtime_record_original_retained_privately': True,
                     'complete_roster_sha256': hashlib.sha256(original.dump(verified)).hexdigest(),
                     'temporary_derived_tree_reauthenticated_before_removal': True})
    require(rows[0]['complete_roster_sha256'] == rows[1]['complete_roster_sha256'], 'Actual mode rosters differ')
    low.read_source(root / 'qa/PUBLIC-COPY-MAP.json', low.MAP_SHA, 16 * 1024 * 1024)
    for path, h in PINS.items():
        low.read_source(root / path, h)
    require(sha(__file__) == own and sha(target) == target_sha, 'Case source changed')
    report = {'passed': True, 'both_actual_modes_passed': True, 'copy_map_sha256': low.MAP_SHA,
              'canonical_files': low.CANONICAL_COUNT, 'logical_files': low.LOGICAL_COUNT,
              'newly_written_logical_files_per_mode': low.LOGICAL_COUNT - 1, 'hardlinked_logical_files_per_mode': 1,
              'hardlinked_archive': low.ARCHIVE, 'all_written_bytes_reauthenticated': True,
              'source_sha256': own, 'case_restore_source_sha256': target_sha, 'original_tool_source_sha256': PINS,
              'original_boot_sha256': sha(boot), 'executions': rows, 'disk_checkpoints': disk,
              'original_sources_and_map_unchanged': True, 'official_archive_bytes_unchanged': True,
              'temporary_derived_trees_removed_after_full_verification': True,
              'original_numerical_strict_passed': False, 'publication_go': False,
              'scope': 'Actual logical-layout replay in two modes: new writes plus one authenticated regular hardlink. Not wholly new payload allocation. Private omissions remain omitted; public JSON projections remain projections. No archive decoding or geometry/render rerun.'}
    dump(out / 'public-restore-proof.json', report)
    print(json.dumps({'passed': True, 'modes': 2, 'canonical': low.CANONICAL_COUNT, 'logical': low.LOGICAL_COUNT}))


if __name__ == '__main__':
    main()
