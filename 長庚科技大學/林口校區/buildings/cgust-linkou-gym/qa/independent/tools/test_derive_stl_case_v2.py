"""Extended original-byte identity/lattice controls; no geometry acceptance tests."""
from pathlib import Path
import argparse, hashlib, json, os, struct, subprocess, sys, tempfile

def require(v, message):
    if not v:
        raise RuntimeError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def stl(value=0.5, negative_zero=False):
    vertices=[-0.0 if negative_zero else 0.0,0.,0.,value,0.,0.,0.,1.,0.]
    return b'Independent identity-only control'.ljust(80,b'\0')+struct.pack('<I',1)+struct.pack('<12fH',0.,0.,1.,*vertices,0)

NEGATIVE_ERRORS = {
    'wrong-sha': 'RuntimeError: Exact original STL bytes/hash differ',
    'count-mismatch': 'RuntimeError: Invalid binary STL count or length',
    'trailing-byte': 'RuntimeError: Invalid binary STL count or length',
    'truncated': 'RuntimeError: Invalid binary STL count or length',
    'empty-count': 'RuntimeError: Invalid binary STL count or length',
    'nan-coordinate': 'RuntimeError: Nonfinite original coordinate',
    'positive-infinity': 'RuntimeError: Nonfinite original coordinate',
    'negative-infinity': 'RuntimeError: Nonfinite original coordinate',
    'invalid-sha': 'RuntimeError: Invalid expected SHA-256',
    'short-header': 'RuntimeError: Wrong STL type or byte count',
    'leaf-symlink': "OSError: [Errno 40] Too many levels of symbolic links: 'link.stl'",
    'parent-symlink': "NotADirectoryError: [Errno 20] Not a directory: 'directory-alias'",
    'fifo': 'RuntimeError: Wrong STL type or byte count',
    'existing-output': 'RuntimeError: Fresh proof output required',
    'oversized-sparse': 'RuntimeError: Wrong STL type or byte count',
}


def main():
    p=argparse.ArgumentParser();p.add_argument('--tool',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    require(not a.out.exists(),'Fresh control output required');a.out.mkdir(parents=True)
    tool=a.tool.resolve();source=tool.read_bytes();test_source=Path(__file__).read_bytes();rows=[]
    positives=[('integer',2.,0,0),('half',0.5,1,0),('v5-coordinate',struct.unpack('<f',bytes.fromhex('6666263f'))[0],23,0),('power30',2.**-30,30,0),('power56',77.*2.**-56,56,0),('subnormal',2.**-149,149,0),('largest-finite',struct.unpack('<f',bytes.fromhex('ffff7f7f'))[0],0,0),('signed-zero',0.5,1,1)]
    with tempfile.TemporaryDirectory(prefix='identity-controls-') as tmp:
        root=Path(tmp)
        cases=[]
        for name,value,power,zeros in positives:
            cases.append((name,stl(value, bool(zeros)),True,power,zeros,None))
        valid=stl()
        tail=bytearray(valid[84:]);struct.pack_into('<f',tail,12+8*4,2.**-31)
        cases.append(('second-face-last-coordinate',valid[:80]+struct.pack('<I',2)+valid[84:]+tail,True,31,0,None))
        cases.extend([
            ('wrong-sha',valid,False,None,None,'0'*64),
            ('count-mismatch',valid[:80]+struct.pack('<I',2)+valid[84:],False,None,None,None),
            ('trailing-byte',valid+b'x',False,None,None,None),
            ('truncated',valid[:-1],False,None,None,None),
            ('empty-count',valid[:80]+struct.pack('<I',0),False,None,None,None),
            ('nan-coordinate',stl(float('nan')),False,None,None,None),
            ('positive-infinity',stl(float('inf')),False,None,None,None),
            ('negative-infinity',stl(-float('inf')),False,None,None,None),
            ('invalid-sha',valid,False,None,None,'z'*64),
            ('short-header',valid[:83],False,None,None,None),
            ('leaf-symlink',valid,False,None,None,None),
            ('parent-symlink',valid,False,None,None,None),
            ('fifo',valid,False,None,None,None),
            ('existing-output',valid,False,None,None,None),
            ('oversized-sparse',valid,False,None,None,None),
        ])
        for name,data,passed,power,zeros,expected in cases:
            sub=root/name;sub.mkdir();path=sub/'input.stl';path.write_bytes(data)
            if name=='leaf-symlink':
                path=sub/'link.stl';path.symlink_to(sub/'input.stl')
            elif name=='parent-symlink':
                alias=root/'directory-alias';alias.symlink_to(sub,target_is_directory=True);path=alias/'input.stl'
            elif name=='fifo':
                path=sub/'named-pipe';os.mkfifo(path)
            out=sub/'proof.json';sha=expected or digest(data)
            protected_output=b'Existing proof must remain byte-for-byte.\n'
            if name=='existing-output':
                out.write_bytes(protected_output)
            if name=='oversized-sparse':
                with path.open('r+b') as stream:
                    stream.truncate(512*1024*1024+1)
                sparse_stat=path.stat()
                require(sparse_stat.st_size==512*1024*1024+1 and sparse_stat.st_blocks*512<=65536,
                        'Oversize fixture must remain sparse')
            command=[sys.executable,'-B',*(['-O'] if sys.flags.optimize else []),str(tool),'--stl',str(path),'--expected-sha256',sha,'--out',str(out)]
            run=subprocess.run(command,capture_output=True,timeout=10)
            (a.out/(name+'.stdout')).write_bytes(run.stdout);(a.out/(name+'.stderr')).write_bytes(run.stderr)
            require(run.returncode==(0 if passed else 1),'Unexpected exact exit: '+name)
            require(out.exists() is (passed or name=='existing-output'),'Unexpected proof presence: '+name)
            row={'case':name,'input_bytes':len(data),'input_sha256':digest(data),'expected_pass':passed,'returncode':run.returncode,'expectation_verified':True,'stdout_sha256':digest(run.stdout),'stderr_sha256':digest(run.stderr)}
            if not passed:
                last_line=run.stderr.decode('utf-8',errors='strict').strip().splitlines()[-1]
                require(last_line==NEGATIVE_ERRORS[name] and run.stdout==b'', 'Wrong negative-control error: '+name)
                row.update(expected_error=NEGATIVE_ERRORS[name],observed_error=last_line,error_classification_verified=True)
            if name=='existing-output':
                require(out.read_bytes()==protected_output,'Existing output was overwritten')
                retained=a.out/(name+'.preserved-output')
                retained.write_bytes(out.read_bytes())
                row.update(existing_output_unchanged=True,existing_output_sha256=digest(protected_output),
                           preserved_output_file=retained.name)
            if name=='oversized-sparse':
                after=path.stat()
                require(after.st_size==sparse_stat.st_size and after.st_blocks==sparse_stat.st_blocks,
                        'Sparse input changed')
                row.update(input_bytes=sparse_stat.st_size,input_sha256=None,
                           fixture_seed_sha256=digest(data),supplied_expected_sha256=sha,
                           sparse_allocated_bytes=sparse_stat.st_blocks*512,
                           sparse_input_unchanged=True,hash_not_read_by_size_rejection=True)
            if passed:
                require(run.stderr==b'', 'Unexpected positive-control stderr: '+name)
                proof=json.loads(out.read_bytes())
                require(proof['passed'] is True and proof['model_go'] is False,'Acceptance scope changed')
                require(type(proof['optimization_level']) is int and proof['optimization_level']==sys.flags.optimize,'Mode mismatch')
                require(proof['completed'] is True and proof['stl_sha256']==digest(data)
                        and proof['stl_bytes']==len(data) and proof['source_sha256']==digest(source)
                        and proof['original_input_and_source_unchanged'] is True,
                        'Positive input/source binding mismatch')
                require(proof['cpu_affinity']==sorted(os.sched_getaffinity(0)) and len(proof['cpu_affinity'])==1,
                        'Positive CPU binding mismatch')
                face_count=2 if name=='second-face-last-coordinate' else 1
                require(proof['original_faces']==face_count and proof['original_coordinate_values_checked']==9*face_count,'Count mismatch')
                require(proof['maximum_denominator_power']==power and proof['coordinate_denominator_lcm']==str(1<<power),'Wrong lattice')
                require(proof['exact_rational_round_trips']==proof['binary32_byte_round_trips']==9*face_count,'Incomplete roundtrip')
                if face_count==2:
                    w=proof['minimality_witness']
                    require((w['face_index'],w['vertex_index'],w['axis'],w['byte_offset'])==(1,2,'z',178),'Tail coordinate omitted')
                require(proof['negative_zero_signs_preserved_explicitly']==zeros,'Zero sign lost')
                if face_count==2:
                    expected_histogram={'0':15,'1':2,'31':1}
                    expected_high=[0.5,1.0,2.**-31]
                else:
                    expected_histogram={'0':9} if power==0 else {'0':8,str(power):1}
                    value=next(v for n,v,p,z in positives if n==name)
                    expected_high=[value,1.0,0.0]
                require(proof['denominator_power_histogram']==expected_histogram
                        and all(type(v) is int for v in proof['denominator_power_histogram'].values())
                        and sum(proof['denominator_power_histogram'].values())==9*face_count,
                        'Histogram mismatch')
                require(proof['bounds_mm']==[[0.0,0.0,0.0],expected_high]
                        and proof['extents_mm']==expected_high,'Bounds/extents mismatch')
                row.update(histogram_verified=True,bounds_and_extents_verified=True,
                           source_and_input_binding_verified=True)
                raw=out.read_bytes();(a.out/(name+'.proof.json')).write_bytes(raw);row['proof_sha256']=digest(raw)
            rows.append(row)
    require(len(rows)==24 and len({r['case'] for r in rows})==24,'Incomplete or duplicated control roster')
    require(tool.read_bytes()==source and Path(__file__).read_bytes()==test_source,'Tool or test source changed')
    result={'passed':True,'optimization_level':sys.flags.optimize,'cases':rows,'case_count':len(rows),'tool_sha256':digest(source),'test_source_sha256':digest(test_source),'cpu_affinity':sorted(os.sched_getaffinity(0)),'all_sources_unchanged':True,'negative_error_classes_verified':True,'model_go':False,'scope':'Original byte identity, binary32 denominator minimality and exact signed-zero round trips only; no geometry thresholds relaxed.'}
    (a.out/'controls.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':True,'cases':len(rows),'optimization_level':sys.flags.optimize}))

if __name__=='__main__':
    main()
