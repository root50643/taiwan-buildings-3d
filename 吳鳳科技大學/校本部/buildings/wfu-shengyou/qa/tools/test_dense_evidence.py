"""Synthetic descriptor and complete original numerical-flag evidence controls."""
from pathlib import Path
import argparse,csv,gzip,hashlib,io,json,lzma,shutil,tempfile
from validate_dense_evidence import audit
from qa_common import sha256,write_json,write_gzip_json,require

def changed_point(rows):
    value=float(rows[0]['x'])+1
    rows[0].update(x=repr(value),x_hex=value.hex())

def changed_normal(rows):
    value=float(rows[0]['nx'])+.5
    rows[0].update(nx=repr(value),nx_hex=value.hex(),dx_hex=(-value).hex())

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);results=[]
    cases=[('missing_hex_column',lambda r:r[0].pop('origin_x_hex')),('non_hex_descriptor',lambda r:r[0].update(origin_x_hex='nan')),('wrong_inward_direction',lambda r:r[0].update(dx_hex='0x1p+0',dy_hex='0x1p+0',dz_hex='0x1p+0')),('decimal_hex_disagreement',lambda r:r[0].update(x_hex='0x1p+30')),('missing_sample',lambda r:r.pop()),('duplicate_sample',lambda r:r.append(dict(r[0]))),('short_ray_omitted_from_evidence',lambda r:r[0].update(first_solid='0.1')),
        ('omitted_flag_bad_entry',lambda r:r[0].update(entry='0.1')),
        ('omitted_flag_nonfinite_entry',lambda r:r[0].update(entry='nan')),
        ('omitted_flag_nonfinite_exit',lambda r:r[0].update(exit='nan')),
        ('omitted_flag_nonfinite_chord',lambda r:r[0].update(first_solid='nan')),
        ('omitted_flag_nonpositive_chord',lambda r:r[0].update(first_solid='0')),
        ('omitted_flag_inconsistent_interval',lambda r:r[0].update(exit=str(float(r[0]['exit'])+1))),
        ('omitted_flag_source_face',lambda r:r[0].update(source_face_in_entry='0')),
        ('omitted_flag_crossing_order',lambda r:r[0].update(alternating_crossings='0')),
        ('omitted_flag_ambiguous_event',lambda r:r[0].update(ambiguous_events='1')),
        ('omitted_flag_inside_parity',lambda r:r[0].update(inside_control='0')),
        ('omitted_flag_outside_parity',lambda r:r[0].update(outside_control='1')),
        ('omitted_flag_midpoint_parity',lambda r:r[0].update(mid_control='0')),
        ('omitted_flag_after_exit_parity',lambda r:r[0].update(after_exit_control='1')),
        ('omitted_flag_original_barycentric_point',changed_point),
        ('omitted_flag_original_face_normal',changed_normal)]
    with tempfile.TemporaryDirectory(dir=a.out,prefix='dense-work-') as temp:
        root=Path(temp)/'dense';shutil.copytree(a.baseline,root);report=root/'dense-check.json';original=report.read_bytes();dense=json.loads(original);path=root/dense['csv_file'];require(dense['csv_compression']=='xz','Synthetic baseline must use xz');compressed=path.read_bytes();data=list(csv.DictReader(io.StringIO(lzma.decompress(compressed).decode())));fields=list(data[0]);flagpath=root/dense['flagged_samples_file'];originalflags=flagpath.read_bytes()
        audit(report,a.stl);results.append({'case':'original_positive_csv','expected_accept':True,'passed':True})
        def restore():path.write_bytes(compressed);report.write_bytes(original);flagpath.write_bytes(originalflags)
        def prepare(name,current,flags=None,recompute_result=False):
            columns=[key for key in fields if key in current[0]]
            if len(columns)!=len(fields):current=[{k:v for k,v in row.items() if k in columns} for row in current]
            buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=columns);writer.writeheader();writer.writerows(current);raw=buf.getvalue().encode();new=lzma.compress(raw,check=lzma.CHECK_CRC64,preset=6);path.write_bytes(new);record=json.loads(original);record.update(csv_compressed_sha256=sha256(path),uncompressed_csv_sha256=hashlib.sha256(raw).hexdigest())
            if flags is not None:
                write_gzip_json(flagpath,flags);record.update(flagged_samples_sha256=sha256(flagpath),flagged_sample_count=len(flags))
                if recompute_result:
                    record['checks']['all_original_ray_intervals_and_controls_valid']=not flags;record['passed']=record['strict_passed']=all(record['checks'].values())
            write_json(report,record);(a.out/(name+'.csv.xz')).write_bytes(new);write_json(a.out/(name+'.report.json'),record)
            if flags is not None:write_gzip_json(a.out/(name+'.flags.json.gz'),flags)
        def rejected(name,stl):
            try:audit(report,stl)
            except Exception as error:results.append({'case':name,'expected_accept':False,'passed':True,'error_type':type(error).__name__,'error':str(error)})
            else:raise RuntimeError('Invalid original evidence accepted: '+name)
        rejected('missing_original_stl',None)
        for name,mutate in cases:
            current=[dict(row) for row in data];mutate(current);prepare(name,current);rejected(name,a.stl);restore()
        bad=[dict(row) for row in data];bad[0]['inside_control']='0'
        key={'original_face_index':int(bad[0]['face']),'sample_index':int(bad[0]['sample'])}
        correct={**key,'reasons':['original_triangle_parity_controls_failed'],'original_cpp_row':bad[0]}
        prepare('correctly_recorded_numerical_flag',bad,[correct],True)
        observed=audit(report,a.stl);require(observed['passed'] is True and observed['original_numerical_strict_passed'] is False,'An honest flag must preserve failed numerical strict state')
        results.append({'case':'correctly_recorded_numerical_flag','expected_accept':True,'numerical_strict_passed':False,'passed':True});restore()
        for name,reasons in [('missing_flag_reason',[]),('wrong_flag_reason',['ray_not_original_face_normal']),('extra_flag_reason',['original_triangle_parity_controls_failed','source_original_face_missing_from_entry'])]:
            prepare(name,bad,[dict(correct,reasons=reasons)],True);rejected(name,a.stl);restore()
        prepare('flag_present_but_strict_falsely_true',bad,[correct],False);rejected('flag_present_but_strict_falsely_true',a.stl);restore()
        fake=dict(correct,original_cpp_row=data[0]);prepare('spurious_flag_on_valid_row',data,[fake],True);rejected('spurious_flag_on_valid_row',a.stl);restore()
    write_json(a.out/'results.json',{'passed':True,'source_sha256':sha256(__file__),'original_stl_sha256':sha256(a.stl),'cases':results,'case_count':len(results)});print(json.dumps({'passed':True,'case_count':len(results)}))
if __name__=='__main__':main()
