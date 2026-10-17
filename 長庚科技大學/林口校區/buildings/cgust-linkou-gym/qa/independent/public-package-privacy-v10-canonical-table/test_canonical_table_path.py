"""Four exact canonical-table read-point controls only; never a full package scan.
The original and one-string variant read-point AST statements are evaluated in
an isolated bounded namespace. No archive, CSV, scene or root traversal occurs.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, ast, copy, hashlib, json, os, stat, types
HERE = Path(__file__).absolute().parent
ENTRY_BYTES = 20071
ENTRY_SHA = '2a83fcadc426bed87df3b76eff9caff14f6e9e0d5614b5c1dbfa66f29d72f7ac'
ORIGINAL_BYTES = 20036
ORIGINAL_SHA = 'e0abeb905ccfe96a493fa08b5d0c0838f635c706bf5bfe7e6326349c234834ec'
MAP_BYTES = 2253316
MAP_SHA = '88c242807a32719dd3d77d2bfffb04e5cbefd48ee2d4c29ff24ba58d02e0c486'
OLD_PATH = 'qa/SOURCE-STATE-DEFAULT-EXCEPTIONS.json'
NEW_PATH = 'qa/independent/scene-state-bridge-v10/SOURCE-STATE-DEFAULT-EXCEPTIONS.json'


def require(value,message):
    if not value:
        raise ValueError(message)


def load_entry():
    flags = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    parent = os.open('/',flags)
    try:
        for part in HERE.parts[1:]:
            child = os.open(part,flags,dir_fd=parent);os.close(parent);parent=child
        fd = os.open('scan_public_package.py',os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_size==ENTRY_BYTES,'Entry type/size differs')
        data=stream.read(ENTRY_BYTES+1);after=os.fstat(stream.fileno())
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
            ==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
            and len(data)==ENTRY_BYTES and hashlib.sha256(data).hexdigest()==ENTRY_SHA,'Entry source differs')
    m=types.ModuleType('integration_control_target');m.__file__=str(HERE/'scan_public_package.py')
    exec(compile(data,m.__file__,'exec'),m.__dict__)
    return m


def read_point(source):
    tree = ast.parse(source)
    run = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run']
    require(len(run) == 1, 'Unique original run function required')
    points = [n for n in run[0].body if isinstance(n, ast.Assign)
              and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id == 'states']
    require(len(points) == 1, 'Unique exact table read-point required')
    point = points[0]
    call = point.value
    require(isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == 'bind_state_exceptions', 'Original table binding expression differs')
    read = call.args[0]
    require(isinstance(read, ast.Call) and isinstance(read.func, ast.Name)
            and read.func.id == 'read_file' and len(read.args) == 2
            and isinstance(read.args[0], ast.Constant) and type(read.args[0].value) is str
            and isinstance(read.args[1], ast.Name) and read.args[1].id == 'STATE_EXCEPTIONS',
            'Original exact table read expression differs')
    return point, read.args[0].value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sealed-map', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    require(os.sched_getaffinity(0) == {0}, 'CPU0 under shared lock required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(), 'Fresh output required')
    m = load_entry(); reader, tools = m.load_tools()
    own = reader._read_regular_snapshot(HERE, Path(__file__).name, None, 256*1024)
    original = reader._read_regular_snapshot(HERE.parent / 'public-package-privacy-v10',
        'scan_public_package.py', ORIGINAL_BYTES, 256*1024)
    require(m.digest(original) == ORIGINAL_SHA, 'Exact original scanner differs')
    variant = reader._read_regular_snapshot(HERE, 'scan_public_package.py', ENTRY_BYTES, 256*1024)
    require(m.digest(variant) == ENTRY_SHA and original.count(OLD_PATH.encode()) == 1
            and variant == original.replace(OLD_PATH.encode(), NEW_PATH.encode()),
            'Variant must change exactly one literal byte span')
    old_point, old_path = read_point(original); new_point, new_path = read_point(variant)
    require(old_path == OLD_PATH and new_path == NEW_PATH, 'Read-point paths differ')
    normalized = ast.parse(original)
    for node in ast.walk(normalized):
        if isinstance(node, ast.Constant) and node.value == OLD_PATH: node.value = NEW_PATH
    require(ast.dump(normalized, include_attributes=False) == ast.dump(ast.parse(variant), include_attributes=False),
            'Unapproved AST difference')
    mapping_bytes = reader._read_regular_snapshot(args.sealed_map.absolute().parent,
        args.sealed_map.name, MAP_BYTES, 4*1024*1024)
    require(m.digest(mapping_bytes) == MAP_SHA, 'Exact sealed map differs')
    generic = tools['package_controls_v2.py']
    canonical, aliases = tools['restore_scientific_layout.py'].validated_map(generic.load_json_bytes(mapping_bytes))
    require(NEW_PATH in canonical and OLD_PATH not in canonical, 'Observed sealed canonical mismatch differs')
    require(all(canonical[NEW_PATH][k] == m.STATE_EXCEPTIONS[k] for k in ('bytes','sha256')),
            'Canonical exact table binding differs')
    table = reader._read_regular_snapshot(HERE, 'provenance/state-exceptions.reference.json',
        m.STATE_EXCEPTIONS['bytes'], 64*1024)
    require(m.digest(table) == m.STATE_EXCEPTIONS['sha256'], 'Reference table identity differs')
    cases = []
    def evaluate(point, payloads):
        requested = []
        def read_file(name, expected):
            requested.append(name)
            require(name in canonical and name in payloads, 'Exact canonical table path absent')
            data = payloads[name]
            require(type(data) is bytes and len(data) == expected['bytes'] and m.digest(data) == expected['sha256'],
                    'Exact canonical table size/hash differs')
            return data
        scope = {'bind_state_exceptions':m.bind_state_exceptions, 'read_file':read_file,
                 'STATE_EXCEPTIONS':m.STATE_EXCEPTIONS, 'generic':generic, 'canonical':canonical}
        statement = ast.Module(body=[copy.deepcopy(point)], type_ignores=[])
        exec(compile(ast.fix_missing_locations(statement), '<exact-table-read-point>', 'exec'), scope)
        require(requested == [NEW_PATH] and len(scope['states']) == 2, 'Exact one-read/two-state scope differs')
    def case(name, point, payloads, expected_error=None):
        error = None
        try: evaluate(point, payloads)
        except ValueError as exc: error = str(exc)
        ok = error is None if expected_error is None else error is not None and expected_error in error
        cases.append({'logical_case':name,'expected_accept':expected_error is None,
                      'accepted':error is None,'error':error,'passed':ok})
    case('exact_new_canonical_path_accepts', new_point, {NEW_PATH:table})
    case('original_top_path_is_absent_and_rejected', old_point, {NEW_PATH:table}, 'Exact canonical table path absent')
    case('missing_new_table_payload_rejected', new_point, {}, 'Exact canonical table path absent')
    wrong = table[:-1] + b' '
    rebuilt = bytearray(table); rebuilt[-1:] = bytes.fromhex('20'); rebuilt = bytes(rebuilt)
    require(wrong == rebuilt and m.digest(wrong) != m.digest(table), 'Actual wrong-hash fixture reconstruction differs')
    case('wrong_table_sha256_rejected', new_point, {NEW_PATH:wrong}, 'Exact canonical table size/hash differs')
    require(reader._read_regular_snapshot(HERE, 'scan_public_package.py', ENTRY_BYTES, 256*1024) == variant,
            'Variant source changed')
    require(reader._read_regular_snapshot(HERE, Path(__file__).name, len(own), 256*1024) == own,
            'Control source changed')
    require(reader._read_regular_snapshot(args.sealed_map.absolute().parent,args.sealed_map.name,MAP_BYTES,4*1024*1024) == mapping_bytes,
            'Sealed map changed')
    result = {'schema':'cgust-canonical-table-path-controls-v1','passed':all(c['passed'] for c in cases),
        'case_count':len(cases),'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),
        'source_sha256':m.digest(own),'scanner_source_sha256':ENTRY_SHA,'original_scanner_source_sha256':ORIGINAL_SHA,
        'sealed_map_bytes':MAP_BYTES,'sealed_map_sha256':MAP_SHA,'exact_table':m.STATE_EXCEPTIONS,
        'old_read_path':OLD_PATH,'new_read_path':NEW_PATH,'original_read_point_line':old_point.lineno,
        'variant_read_point_line':new_point.lineno,'original_path_present_in_sealed_canonical':False,
        'new_path_present_in_sealed_canonical':True,'one_literal_change_only':True,'all_other_ast_identical':True,
        'cases':cases,'wrong_hash_fixture':{'recipe':'Replace final byte of exact reference table with hex 20.',
            'base_sha256':m.digest(table),'replacement_hex':'20','offset':len(table)-1,
            'fixture_sha256':m.digest(wrong),'actual_rebuilt_sha256':m.digest(rebuilt),'actual_bitwise_equal':wrong==rebuilt,
            'materialized_fixture':False},
        'probe_scope':'Evaluate only the exact original states-assignment AST with bounded table reads against the authenticated sealed map. Neither original nor adapted run() is called.',
        'full_scanner_run_invoked':False,'actual_fullscan_failure_claimed':False,'archive_csv_scene_payloads_read':False,
        'generic_42_case_suites_rerun':False,'original_inputs_unchanged':True,'model_go':False,'publication_go':False}
    with args.out.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'passed':result['passed'],'case_count':len(cases),'optimization_level':sys.flags.optimize}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
