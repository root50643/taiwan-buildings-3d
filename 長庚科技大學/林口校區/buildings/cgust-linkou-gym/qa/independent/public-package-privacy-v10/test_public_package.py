"""Small integration controls only; never read/decode the historical archive."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, gzip, hashlib, io, json, os, stat, tempfile, types, zipfile

HERE = Path(__file__).absolute().parent
ENTRY_BYTES = 20036
ENTRY_SHA = 'e0abeb905ccfe96a493fa08b5d0c0838f635c706bf5bfe7e6326349c234834ec'


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
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),'Fresh output required')
    m=load_entry();p,tools=m.load_tools()
    own=p._read_regular_snapshot(HERE,Path(__file__).name,None,256*1024)
    g=tools['package_controls_v2.py'];primitive=tools['exact_privacy_primitives.py'];checker=tools['check_cgust_privacy.py']
    policy=types.SimpleNamespace(MAX_BYTES=g.MAX_BYTES,PRIVATE_MARKERS=g.PRIVATE_MARKERS+checker.CGUST_MARKERS,
                                TMP_MARKER=g.TMP_MARKER,SECRET_PATTERNS=g.SECRET_PATTERNS)
    cases=[]
    def case(name,fn,error=None):
        actual=None
        try:fn()
        except Exception as exc:actual=type(exc).__name__+': '+str(exc)
        cases.append({'name':name,'expected_accept':error is None,'accepted':actual is None,
                      'expected_error_substring':error,'error':actual,
                      'passed':actual is None if error is None else actual is not None and error in actual})
    marker=b'/'+b'tmp/'
    def state(value=None):
        data=json.dumps(value or {'render':{'filepath':marker.decode()}},separators=(',',':')).encode()
        at=data.find(marker)
        row={'bytes':len(data),'sha256':m.digest(data),'exact_value_utf8_hex':marker.hex(),
             'encoded_json_string_offset':at-1,'encoded_json_string_bytes':7,'marker_offset':at,'marker_bytes':5}
        return data,row
    def scan(data,name='state.json',rows=None):
        states=rows or {}
        selection=[dict(source_relative_path=n,bytes=r['bytes'],sha256=r['sha256']) for n,r in states.items()]
        s=m.current_scanner(g,primitive,checker,policy,selection,states)
        s.scan({'source_relative_path':name},data)
        if name in states:s.complete()
        return s
    safe,row=state()
    def positive():
        s=scan(safe,rows={'state.json':row})
        projection=m.state_projection(safe,row,g);at=row['marker_offset']
        require(s.state_seen=={'state.json'} and projection[:at]==safe[:at]
                and projection[at:at+5]==b'_'*5 and projection[at+5:]==safe[at+5:],'State projection scope differs')
    case('ordinary_safe_file',lambda:scan(b'ordinary public bytes\n','safe.txt'))
    case('exact_synthetic_state_masks_only_five_bytes',positive)
    case('state_wrong_hash',lambda:m.state_projection(safe+b' ',row,g),'State identity differs')
    case('state_wrong_marker_offset',lambda:m.state_projection(safe,dict(row,marker_offset=row['marker_offset']+1),g),'State exact literal/offset differs')
    case('state_wrong_encoded_offset',lambda:m.state_projection(safe,dict(row,encoded_json_string_offset=row['encoded_json_string_offset']+1),g),'State exact literal/offset differs')
    wrong,wr=state({'render':{'filepath':'other'},'extra':marker.decode()})
    case('state_wrong_typed_pointer',lambda:m.state_projection(wrong,wr,g),'State typed pointer differs')
    wrong,wr=state({'render':{'filepath':marker.decode()},'extra':marker.decode()})
    case('state_duplicate_default_elsewhere',lambda:scan(wrong,rows={'state.json':wr}),'Temporary path outside exact Blender default')
    wrong,wr=state({'render':{'filepath':marker.decode()},'extra':(b'/'+b'workspace/secret').decode()})
    case('state_other_private_bytes_not_masked',lambda:scan(wrong,rows={'state.json':wr}),'Private path marker')
    wrong,wr=state({'render':{'filepath':marker.decode()},'extra':(b'sk-'+b'proj-'+b'A'*40).decode()})
    case('state_other_credential_not_masked',lambda:scan(wrong,rows={'state.json':wr}),'Credential-shaped content')
    case('same_state_at_unapproved_path',lambda:scan(safe,'other.json',{'state.json':row}),'Unreviewed temporary path')
    case('state_exception_not_recursive_gzip',lambda:scan(gzip.compress(safe,mtime=0),'state.json.gz',{'state.json':row}),'Unreviewed temporary path')
    z=io.BytesIO()
    with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED) as archive:archive.writestr('state.json',safe)
    case('state_exception_not_recursive_zip',lambda:scan(z.getvalue(),'nested.zip',{'state.json':row}),'Unreviewed temporary path')
    case('new_cgust_has_no_malformed_fixture_exception',lambda:scan(b'not xz','fixture.xz'),'Unapproved malformed compressed payload')
    case('new_cgust_private_marker_rejected',lambda:scan(checker.CGUST_MARKERS[0],'safe.txt'),'Private path marker')
    case('new_cgust_other_blend_has_no_default_exception',lambda:scan(b'BLENDER-v403'+marker,'other.blend'),'Unreviewed temporary path')
    for n,payload in enumerate((b'',b'foreign archive',b'foreign archive'+b'\0')):
        case('historical_domain_rejects_foreign_identity_%d'%n,
             lambda:m.scan_history(lambda path,desc:payload,g,primitive,policy,tools['archive_verify.py']),
             'Historical domain requires the exact frozen archive')
    table=p._read_regular_snapshot(HERE,'provenance/state-exceptions.reference.json',m.STATE_EXCEPTIONS['bytes'],64*1024)
    rows=g.load_json_bytes(table)['files'];canonical={r['canonical_public_path']:{k:r[k] for k in ('bytes','sha256')} for r in rows}
    case('frozen_state_table_two_unique_canonical_rows',lambda:require(len(m.bind_state_exceptions(table,g,canonical))==2,'Wrong unique count'))
    case('state_table_cannot_be_replaced_by_synthetic_permission',lambda:m.bind_state_exceptions(b'{}',g,canonical),'Exact state exception table differs')
    case('state_table_requires_both_canonical_files',lambda:m.bind_state_exceptions(table,g,{}),'Exact state missing/different')
    changed={k:dict(v,sha256='0'*64) for k,v in canonical.items()}
    case('state_table_requires_exact_canonical_hashes',lambda:m.bind_state_exceptions(table,g,changed),'Exact state missing/different')
    with tempfile.TemporaryDirectory(prefix='.integration-control-',dir=HERE) as td:
        root=Path(td);(root/'safe.txt').write_bytes(b'safe')
        case('all_file_inventory_includes_extra_regular_files',lambda:require(m.inventory(root)=={'safe.txt'},'Inventory missed file'))
        (root/'link').symlink_to('safe.txt')
        case('all_file_inventory_rejects_links',lambda:m.inventory(root),'Symlink in public inventory')
    require(p._read_regular_snapshot(HERE,Path(__file__).name,len(own),256*1024)==own,'Control source changed')
    require(m.digest(p._read_regular_snapshot(HERE,'scan_public_package.py',ENTRY_BYTES,256*1024))==ENTRY_SHA,'Entry source changed')
    report={'passed':all(c['passed'] for c in cases),'optimization_level':sys.flags.optimize,'case_count':len(cases),'cases':cases,
            'source_sha256':m.digest(own),'entry_source_sha256':ENTRY_SHA,'small_synthetic_only':True,
            'historical_archive_or_original_csv_read':False,'model_go':False,'publication_go':False}
    with args.out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('passed','optimization_level','case_count')}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
