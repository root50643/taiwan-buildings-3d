"""Read-only integrity/coverage audit of every original-run dense CSV descriptor.
Recompute the original numerical predicates from each unchanged recorded row and
its original STL face. No reconstructed rays, dropped flags or waivers exist.
"""
from pathlib import Path
from fractions import Fraction
import argparse, csv, gzip, hashlib, io, json, math, re, sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'verification'))
from qa_common import require, sha256, load_stl, open_compressed_csv, write_json
from check_dense_surface import WEIGHTS, MINIMUM_CHORD, ORIGIN_OFFSET

DESCRIPTORS = ['x','y','z','nx','ny','nz','origin_x','origin_y','origin_z','dx','dy','dz']
HEX = re.compile(r'[+-]?0x[0-9a-f]+(?:\.[0-9a-f]*)?p[+-]?\d+\Z')

def exact_hex(value):
    require(isinstance(value, str) and HEX.fullmatch(value.lower()), 'Missing/malformed original-run hex descriptor')
    text=value.lower(); sign=-1 if text.startswith('-') else 1; text=text.lstrip('+-')
    mantissa,power=text[2:].split('p'); whole,_,fraction=mantissa.partition('.')
    coefficient=sign*int(whole+fraction,16); exponent=int(power)-4*len(fraction)
    return Fraction(coefficient*(1<<exponent)) if exponent>=0 else Fraction(coefficient,1<<(-exponent))

def numerical_reasons(row, triangle, normal, sample):
    """Same ordered predicates/tolerances as the unmodified original checker.

    Duplicate samples are rejected by coverage before this function. Geometry is
    compared only to the supplied original STL; no ray is recast or moved.
    """
    reasons=[]
    chord,entry,finish=(float(row[key]) for key in ('first_solid','entry','exit'))
    point=np.array([float(row[key]) for key in ('x','y','z')])
    direction_normal=np.array([float(row[key]) for key in ('nx','ny','nz')])
    if not np.allclose(point,WEIGHTS[sample] @ triangle,atol=1e-9,rtol=1e-12):
        reasons.append('sample_not_on_original_barycentric_point')
    if not np.allclose(direction_normal,normal,atol=1e-10,rtol=1e-12):
        reasons.append('ray_not_original_face_normal')
    if not math.isfinite(entry) or abs(entry-ORIGIN_OFFSET)>1e-8:
        reasons.append('entry_not_at_original_face_offset')
    valid_interval=False
    if not math.isfinite(chord) or not math.isfinite(finish) or chord<=0:
        reasons.append('missing_or_nonpositive_first_original_interval')
    elif abs((finish-entry)-chord)>1e-9:
        reasons.append('inconsistent_original_interval')
    else:
        valid_interval=True
    if int(row['source_face_in_entry'])!=1:
        reasons.append('source_original_face_missing_from_entry')
    if int(row['alternating_crossings'])!=1:
        reasons.append('original_crossings_not_alternating_enter_exit')
    if int(row['ambiguous_events'])!=0:
        reasons.append('near_coincident_or_opposing_original_crossings')
    if [int(row[key]) for key in ('inside_control','outside_control','mid_control','after_exit_control')]!=[1,0,1,0]:
        reasons.append('original_triangle_parity_controls_failed')
    return reasons,chord,valid_interval

def audit(report_path, stl_path=None):
    require(stl_path is not None,'Original STL is required to recompute every numerical flag predicate')
    dense=json.loads(Path(report_path).read_text()); root=Path(report_path).parent
    original,triangles,stored_normals,_=load_stl(stl_path)
    require(hashlib.sha256(original).hexdigest()==dense.get('stl_sha256'),'Dense audit original STL hash differs')
    require(type(dense.get('original_triangles')) is int and dense['original_triangles']==len(triangles)>0, 'Invalid original triangle count')
    n=len(triangles); require(dense.get('samples')==10*n, 'Wrong sample count')
    crosses=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);norms=np.linalg.norm(crosses,axis=1)
    require((norms>0).all(),'Degenerate original triangles cannot define normal rays')
    normals=crosses/norms[:,None]
    normal_agreement=bool(np.all(np.abs(stored_normals-normals)<=1e-5))
    artifact={}
    for field,hashkey in [('csv_file','csv_compressed_sha256'),('short_chords_file','short_chords_sha256'),('flagged_samples_file','flagged_samples_sha256')]:
        name=dense.get(field); require(isinstance(name,str) and Path(name).name==name, 'Artifact path must be a basename')
        path=root/name; require(path.is_file() and sha256(path)==dense.get(hashkey), 'Original dense artifact hash mismatch: '+field); artifact[field]=path
    flags=json.loads(gzip.decompress(artifact['flagged_samples_file'].read_bytes()))
    shorts=json.loads(gzip.decompress(artifact['short_chords_file'].read_bytes()))
    require(type(flags) is list and type(shorts) is list, 'Malformed original flag/short list')
    require(len(flags)==dense.get('flagged_sample_count') and len(shorts)==dense.get('under_0p8mm_count'), 'Recorded flag counts differ')
    keyed=[]
    for records in [flags,shorts]:
        index={}
        for row in records:
            key=(row['original_face_index'],row['sample_index']); require(key not in index, 'Duplicate flagged/short sample'); index[key]=row
        keyed.append(index)
    matched=[set(),set()]; seen=bytearray(n*10); rows=0; shorts_from_csv=set();flags_from_csv={};minimum=math.inf
    with open_compressed_csv(artifact['csv_file'],dense.get('csv_compression')) as stream:
        require(hashlib.file_digest(stream,'sha256').hexdigest()==dense.get('uncompressed_csv_sha256'), 'Decoded CSV hash differs')
    with open_compressed_csv(artifact['csv_file'],dense.get('csv_compression')) as raw:
        reader=csv.DictReader(io.TextIOWrapper(raw,encoding='utf-8',newline=''))
        required={'face','sample','first_solid','entry','exit','source_face_in_entry','alternating_crossings','ambiguous_events','inside_control','outside_control','mid_control','after_exit_control','raw_intersections_t_face_direction','events_t_direction','paired_intervals'} | {x+'_hex' for x in DESCRIPTORS} | set(DESCRIPTORS[:9])
        require(reader.fieldnames is not None and len(reader.fieldnames)==len(set(reader.fieldnames)) and required.issubset(reader.fieldnames), 'Required original CSV columns absent/duplicated')
        for row in reader:
            require(None not in row and all(v is not None for v in row.values()), 'Malformed CSV row')
            face,sample=int(row['face']),int(row['sample']); require(0<=face<n and 0<=sample<10, 'Face/sample outside original range')
            key=(face,sample); k=10*face+sample; require(not seen[k], 'Duplicate original face/sample'); seen[k]=1;rows+=1
            values={name:exact_hex(row[name+'_hex']) for name in DESCRIPTORS}
            require(any(values['d'+axis] for axis in 'xyz'), 'Zero original ray direction')
            for axis in 'xyz': require(values['d'+axis]==-values['n'+axis], 'Original recorded direction is not the recorded inward normal')
            for name in DESCRIPTORS[:9]:
                value=float(row[name]); require(math.isfinite(value) and math.isclose(value,float(values[name]),rel_tol=1e-15,abs_tol=1e-300), 'Decimal/hex descriptors disagree')
            reasons,chord,valid_interval=numerical_reasons(row,triangles[face],normals[face],sample)
            if valid_interval:minimum=min(minimum,chord)
            if reasons:flags_from_csv[key]=reasons
            if math.isfinite(chord) and chord<MINIMUM_CHORD: shorts_from_csv.add(key)
            for i,index in enumerate(keyed):
                if key in index: require(index[key].get('original_cpp_row')==row, 'Flag/short descriptor not identical to full original CSV');matched[i].add(key)
    require(rows==10*n and all(seen), 'Incomplete original face/sample coverage')
    require(all(matched[i]==set(keyed[i]) for i in range(2)), 'Flagged or short row absent from full original CSV')
    require(shorts_from_csv==set(keyed[1]), 'Short-ray evidence omits or adds original samples')
    require(set(flags_from_csv)==set(keyed[0]), 'Numerical flag evidence omits or adds original samples')
    for key,reasons in flags_from_csv.items():
        require(keyed[0][key].get('reasons')==reasons,'Numerical flag reasons differ from recomputed original predicates')
    recomputed_checks={'every_original_face_exactly_ten_samples':True,
        'stored_normals_agree_with_original_directed_faces':normal_agreement,
        'all_original_ray_intervals_and_controls_valid':not flags_from_csv,
        'all_first_original_chords_ge_0p8mm':not shorts_from_csv and math.isfinite(minimum) and minimum>=MINIMUM_CHORD}
    require(type(dense.get('checks')) is dict and set(dense['checks'])==set(recomputed_checks) and all(type(dense['checks'][key]) is bool and dense['checks'][key] is value for key,value in recomputed_checks.items()),'Dense gate checks disagree with recomputed original predicates')
    strict=all(recomputed_checks.values())
    require(dense.get('passed') is strict and dense.get('strict_passed') is strict,'Dense strict result disagrees with recomputed predicates')
    require(dense.get('minimum_first_chord_mm')==(minimum if math.isfinite(minimum) else None),'Dense minimum chord differs from original CSV')
    return {'passed':True,'completed':True,'stl_sha256':dense['stl_sha256'],'dense_report_sha256':sha256(report_path),'source_sha256':sha256(__file__),'csv_rows_verified':rows,'lossless_descriptors_verified':12*rows,'flagged_samples_matched':len(flags),'short_samples_matched':len(shorts),'all_original_numerical_flag_predicates_recomputed':True,'all_expected_flag_indices_and_reasons_match':True,'recomputed_dense_checks':recomputed_checks,'original_numerical_strict_passed':dense['strict_passed'],'scope':'Artifact integrity, original-run descriptor coverage and original numerical predicate audit only; does not waive a numerical flag or establish global thickness.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dense-report',type=Path,required=True);parser.add_argument('--stl',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    require(not args.out.exists(),'Refuse existing audit output')
    try: report=audit(args.dense_report,args.stl)
    except Exception as error: report={'passed':False,'completed':False,'error_type':type(error).__name__,'error':str(error),'source_sha256':sha256(__file__)}
    write_json(args.out,report);print(json.dumps(report));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
