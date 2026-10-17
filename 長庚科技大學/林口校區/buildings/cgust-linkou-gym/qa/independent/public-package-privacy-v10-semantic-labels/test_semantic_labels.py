"""Small exact semantic-label controls; original fixtures remain in memory only.
All patterns and fixture values are derived from authenticated existing sources.
No full-package, history, scene, CSV, geometry or render execution occurs.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, ast, copy, gzip, hashlib, json, os, stat, types
HERE = Path(__file__).absolute().parent
ENTRY_BYTES = 28871
ENTRY_SHA = '500d93a6669327034758b9dbb1f224407bdf1e702aeb72a9563d84ac81daee96'


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


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    require(os.sched_getaffinity(0)=={0},'CPU0 under shared lock required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),'Fresh report required')
    m=load_entry();reader,tools=m.load_tools()
    own=reader._read_regular_snapshot(HERE,Path(__file__).name,None,256*1024)
    g=tools['package_controls_v2.py'];p=tools['exact_privacy_primitives.py'];c=tools['check_cgust_privacy.py']
    policy=types.SimpleNamespace(MAX_BYTES=g.MAX_BYTES,PRIVATE_MARKERS=g.PRIVATE_MARKERS+c.CGUST_MARKERS,
                                 TMP_MARKER=g.TMP_MARKER,SECRET_PATTERNS=g.SECRET_PATTERNS)
    raw={}
    for name,row in m.SEMANTIC_LABEL_PROFILES.items():
        data=reader._read_regular_snapshot(args.public_root,name,row['bytes'],64*1024)
        require(m.digest(data)==row['sha256'],'Exact original semantic fixture differs')
        raw[name]=data
    pyname=next(n for n,r in m.SEMANTIC_LABEL_PROFILES.items() if r['kind']=='relative_synthetic_python')
    diffname=next(n for n,r in m.SEMANTIC_LABEL_PROFILES.items() if r['kind']=='relative_synthetic_diff')
    jsonname=next(n for n,r in m.SEMANTIC_LABEL_PROFILES.items() if r['kind']=='empty_detection_rule_labels')
    source_line=raw[pyname].splitlines()[206]
    before=json.dumps(m.SEMANTIC_LABEL_PROFILES,sort_keys=True)
    cases=[]
    def case(name,fn,error=None,recipe=None):
        actual=None
        try:fn()
        except (ValueError,SyntaxError,TypeError,KeyError) as exc:actual=str(exc)
        cases.append({'logical_case':name,'expected_accept':error is None,'accepted':actual is None,
            'expected_error_substring':error,'error':actual,'passed':actual is None if error is None else actual is not None and error in actual,
            **({'fixture_reconstruction':recipe} if recipe else {})})
    def scanner():return m.current_scanner(g,p,c,policy,[],{})
    shared=scanner()
    for name in (pyname,diffname,jsonname):
        def positive(name=name):
            projected=shared.plain(raw[name],name,top=True)
            spans=m.SEMANTIC_LABEL_PROFILES[name]['spans'];mask={i for s in spans for i in range(s['offset'],s['offset']+s['bytes'])}
            require(len(projected)==len(raw[name]) and all(projected[i]==(95 if i in mask else b) for i,b in enumerate(raw[name])),
                    'Mask changed bytes outside exact semantic spans')
        case('exact_'+m.SEMANTIC_LABEL_PROFILES[name]['kind']+'_positive',positive)
    require(shared.semantic_seen==set(raw),'Three exact positive classes required')
    def patched(name,offset,old_len,replacement,label):
        base=raw[name];one=base[:offset]+replacement+base[offset+old_len:]
        two=bytearray(base);two[offset:offset+old_len]=replacement;two=bytes(two)
        require(one==two,'Actual fixture rebuild differs')
        return one,{'generator_case':label,'base_logical':name,'base_sha256':m.digest(base),
                    'fixture_bytes':len(one),'fixture_sha256':m.digest(one),'actual_rebuilt_sha256':m.digest(two),
                    'actual_bitwise_equal':True,'fixture_file_written':False}
    def json_fixture(index,key,value,label):
        obj=g.load_json_bytes(raw[jsonname]);obj['limited_raw_path_marker_observations'][index][key]=value
        one=(json.dumps(obj,indent=2)+'\n').encode()
        other=copy.deepcopy(obj);two=(json.dumps(other,indent=2)+'\n').encode()
        require(one==two,'Actual JSON fixture rebuild differs')
        return one,{'generator_case':label,'base_logical':jsonname,'base_sha256':m.digest(raw[jsonname]),
                    'fixture_bytes':len(one),'fixture_sha256':m.digest(one),'actual_rebuilt_sha256':m.digest(two),
                    'actual_bitwise_equal':True,'fixture_file_written':False}
    def isolated(name,data,mutate=None,line=source_line):
        # Explicit isolated lower-guard test only. Production globals never change.
        profiles=copy.deepcopy(m.SEMANTIC_LABEL_PROFILES);spec=profiles[name]
        spec.update(bytes=len(data),sha256=m.digest(data))
        for rule in set(s['rule_index'] for s in spec['spans']):
            marker=p.ADDITIONAL_PRIVATE_MARKERS[rule]
            offsets=[i for i in range(len(data)) if data.startswith(marker,i)]
            same=[s for s in spec['spans'] if s['rule_index']==rule]
            for s,off in zip(same,offsets):s['offset']=off
        if mutate:mutate(spec)
        env=dict(m.__dict__,SEMANTIC_LABEL_PROFILES=profiles)
        f=types.FunctionType(m.semantic_label_projection.__code__,env)
        projected=f(data,name,True,p,g,line)
        p.scan_complete_plain_buffer(policy,projected)
    changed,evidence=patched(pyname,len(raw[pyname]),0,b'\n','append_newline')
    case('wrong_whole_file_sha_rejected',lambda:m.semantic_label_projection(changed,pyname,True,p,g),
         'Semantic-label exact file identity differs',evidence)
    value=next(n.value for n in ast.walk(ast.parse(raw[pyname])) if isinstance(n,ast.Constant)
               and n.lineno==207 and n.col_offset==115)
    absolute=p.ADDITIONAL_PRIVATE_MARKERS[1].decode()+Path(value).parts[0]
    absolute_py=raw[pyname].replace(value.encode(),absolute.encode())
    rebuilt_py=bytes(bytearray(raw[pyname]).replace(value.encode(),absolute.encode()))
    require(absolute_py==rebuilt_py,'Absolute fixture reconstruction differs')
    ev={'generator_case':'replace_two_relative_fixture_constants_with_policy_derived_absolute_value','base_sha256':m.digest(raw[pyname]),
        'fixture_sha256':m.digest(absolute_py),'actual_rebuilt_sha256':m.digest(rebuilt_py),'actual_bitwise_equal':True,'fixture_file_written':False}
    case('true_absolute_python_fixture_rejected',lambda:isolated(pyname,absolute_py),
         'Synthetic fixture must be exact normalized relative prefix',ev)
    data,ev=json_fixture(1,'marker_utf8',absolute,'absolute_value_in_marker_metadata')
    case('true_absolute_json_value_rejected',lambda:isolated(jsonname,data),
         'Semantic rule label must have exact string and empty observation offsets',ev)
    data,ev=json_fixture(1,'offsets',[0],'nonempty_observed_offsets')
    case('nonempty_observation_offsets_rejected',lambda:isolated(jsonname,data),
         'Semantic rule label must have exact string and empty observation offsets',ev)
    data,ev=json_fixture(1,'offsets',{},'wrong_offsets_type')
    case('wrong_json_offsets_type_rejected',lambda:isolated(jsonname,data),
         'Semantic rule label must have exact string and empty observation offsets',ev)
    for label,change,error in [
        ('wrong_position',lambda r:r['spans'][0].update(offset=r['spans'][0]['offset']+1),'Semantic-label exact marker/range differs'),
        ('wrong_range',lambda r:r['spans'][0].update(bytes=r['spans'][0]['bytes']+1),'Semantic-label exact marker/range differs'),
        ('wrong_span_type',lambda r:r['spans'][0].update(bytes=float(r['spans'][0]['bytes'])),'Semantic-label span metadata type differs')]:
        case(label+'_rejected',lambda change=change:isolated(pyname,raw[pyname],change),error)
    extra,evidence=patched(pyname,len(raw[pyname]),0,b'\n# '+p.ADDITIONAL_PRIVATE_MARKERS[0]+b'synthetic', 'outside_additional_private_marker')
    case('extra_true_private_marker_outside_spans_rejected',lambda:isolated(pyname,extra),'Private path marker',evidence)
    at=raw[diffname].find(b'accept_nested_safe_source_prefix')
    changed,evidence=patched(diffname,at,1,b'X','alter_added_diff_case_name')
    case('diff_must_match_authenticated_source_line',lambda:isolated(diffname,changed),
         'Diff added line differs from authenticated source',evidence)
    case('diff_without_original_source_proof_rejected',lambda:isolated(diffname,raw[diffname],line=None),
         'Diff requires previously authenticated original source line')
    for name in (pyname,diffname,jsonname):
        case('non_top_'+m.SEMANTIC_LABEL_PROFILES[name]['kind']+'_rejected',
             lambda name=name:scanner().plain(raw[name],name,top=False),'Private path marker')
    case('nested_gzip_does_not_inherit_source_allowance',
         lambda:scanner().scan({'source_relative_path':'nested-synthetic.py.gz'},gzip.compress(raw[pyname],mtime=0)),
         'Private path marker')
    case('unlisted_top_path_does_not_inherit_by_sha',lambda:scanner().plain(raw[pyname],'other-source.py',top=True),
         'Private path marker')
    require(before==json.dumps(m.SEMANTIC_LABEL_PROFILES,sort_keys=True),'Production exact profiles mutated')
    require(reader._read_regular_snapshot(HERE,Path(__file__).name,len(own),256*1024)==own,'Control source changed')
    for name,row in m.SEMANTIC_LABEL_PROFILES.items():
        require(reader._read_regular_snapshot(args.public_root,name,row['bytes'],64*1024)==raw[name],'Original fixture bytes changed')
    result={'schema':'cgust-exact-semantic-label-controls-v1','passed':all(r['passed'] for r in cases),
        'case_count':len(cases),'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),
        'source_sha256':m.digest(own),'scanner_source_sha256':ENTRY_SHA,'cases':cases,
        'exact_original_inputs':[{ 'logical_path':n,'bytes':len(b),'sha256':m.digest(b)} for n,b in raw.items()],
        'production_profiles_unchanged':True,'original_public_inputs_unchanged':True,
        'isolated_identity_rebinding_is_test_only':True,'negative_fixtures_process_memory_only':True,
        'actual_second_reconstruction_compared':True,'full_scanner_run_invoked':False,
        'archive_csv_scene_geometry_render_executed':False,'previous_generic_suites_rerun':False,
        'model_go':False,'publication_go':False}
    with args.out.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'passed':result['passed'],'case_count':len(cases),'optimization_level':sys.flags.optimize}))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
