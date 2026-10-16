"""Exact diagnosis of original-run rounded C++ normal rays.
All exact hexfloat fields must originate in and match the original CSV row.
Hexadecimal long-double descriptors retain their exact dyadic values. The
original dense report, CSV, short rays, and flags are never changed or waived.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,csv,gzip,hashlib,json,math,shutil,struct,subprocess,sys,tempfile,time
from exact_ray_diagnosis import Mesh,load,require,ratio,reduce_point,reduce_vector,sha

def hex_fraction(text):
 s=text.lower();negative=s.startswith('-');s=s.lstrip('+-');require(s.startswith('0x') and 'p' in s,'Not an exact hexfloat descriptor');mant,expo=s[2:].split('p');a,_,b=mant.partition('.')
 value=F(int(a+b,16),16**len(b));power=int(expo);value=value*(2**power) if power>=0 else value/F(2**(-power))
 return -value if negative else value

def point_lattice(values,den):
 r=[x*den for x in values];q=math.lcm(*(x.denominator for x in r));return reduce_point(tuple(x.numerator*(q//x.denominator) for x in r),q)
def direction_lattice(values):
 q=math.lcm(*(x.denominator for x in values));return reduce_vector(tuple(x.numerator*(q//x.denominator) for x in values))
def classify(mesh,desc,original):
 """Classify supplied dyadic descriptors; only main() verifies original-run provenance."""
 names=['x','y','z','nx','ny','nz','origin_x','origin_y','origin_z']
 require(desc is original or all(desc[k]==original[k] for k in names),'Original C++ descriptor differs from original CSV')
 origin=[hex_fraction(desc[k+'_hex']) for k in ['origin_x','origin_y','origin_z']];direction=[hex_fraction(desc[k+'_hex']) for k in ['dx','dy','dz']]
 o,q=point_lattice(origin,mesh.den);d=direction_lattice(direction);hits=mesh.contacts(o,q,d);require(hits,'Original recorded ray has no exact forward contact')
 require(all(h['lo']>0 for h in hits),'Recorded outside origin is on the surface')
 breaks=sorted({F(0)}|{h[k] for h in hits for k in ['lo','hi']});require(len(breaks)>=3,'Recorded ray does not have entry and exit contacts')
 face=int(desc['face']);entry=breaks[1];finish=breaks[2]
 require(any(h['face']==face and h['lo']==entry==h['hi'] and h['direction']==-1 and not h['edge_contact'] for h in hits),'First exact contact is not an interior entry through the original source face')
 intervals=[]
 for index,low in enumerate(breaks):
  high=breaks[index+1] if index+1<len(breaks) else None;mid=(low+high)/2 if high is not None else low+1
  po=tuple(o[k]*mid.denominator+d[k]*q*mid.numerator for k in range(3));po,pq=reduce_point(po,q*mid.denominator)
  state,witness=mesh.status(po,pq);intervals.append({'t0':ratio(low),'t1':ratio(high) if high is not None else None,'state':state,'exact_midpoint_parity_witness':witness})
 require(intervals[0]['state']=='outside' and intervals[1]['state']=='inside','Source origin/first solid interval is not outside then inside')
 require(intervals[-1]['state']=='outside','Recorded ray beyond all surfaces is not outside')
 squared=(finish-entry)**2*dot(d,d)/F(mesh.den*mesh.den)
 return {'original_face_index':face,'sample_index':int(desc['sample']),'exact_classification_completed':True,
  'supplied_lossless_descriptor_line_classified':True,'original_cpp_descriptor':desc,
  'ray_origin_integer_lattice_numerators':list(o),'ray_origin_integer_lattice_denominator':str(q),'ray_direction_integer_lattice':list(d),'coordinate_lattice_denominator':str(mesh.den),
  'all_forward_original_triangle_contacts':[{'face':h['face'],'t0':ratio(h['lo']),'t1':ratio(h['hi']),'coplanar_interval':h['coplanar'],'edge_or_vertex_contact':h['edge_contact'],'directed_crossing':h['direction']} for h in hits],
  'classified_open_intervals':intervals,'first_entry_t':ratio(entry),'conservative_first_exit_t':ratio(finish),
  'conservative_first_solid_chord_squared_mm2_exact':ratio(squared),'conservative_first_solid_chord_mm_approx':math.sqrt(float(squared)),
  'conservative_first_solid_chord_ge_0p8mm':squared>=F(16,25)}
from exact_ray_diagnosis import dot

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stl',type=Path,required=True);ap.add_argument('--flags',type=Path,required=True);ap.add_argument('--dense-report',type=Path,required=True);ap.add_argument('--raw-report',type=Path,required=True);ap.add_argument('--intersections-report',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--limit',type=int);args=ap.parse_args();require(not args.out.exists(),'Evidence output already exists');args.out.mkdir(parents=True)
 core=Path(__file__).with_name('exact_ray_diagnosis.py')
 paths={'stl':args.stl,'flags':args.flags,'dense_report':args.dense_report,'raw_report':args.raw_report,'intersections_report':args.intersections_report,'exact_core_source':core,'diagnostic_source':Path(__file__)};hashes={k:sha(p) for k,p in paths.items()};start=time.time()
 report={'completed':False,'all_selected_rays_exactly_classified':False,'all_selected_first_chords_ge_0p8mm':False,'all_original_inputs_and_sources_unchanged':False,'input_and_tool_sha256':hashes,'optimization_level':sys.flags.optimize,'scope':'Exact rational classification of ORIGINAL-RUN hexfloat C++ point/normal/origin/direction fields, individually matched back to the full lossless original CSV. No reconstructed descriptor can substitute. Original numerical strict failures remain unchanged. Finite rays do not prove global wall thickness.'};rows=[]
 try:
  require(hashes['stl']==args.expected_sha256,'Frozen STL hash mismatch');dense=json.loads(args.dense_report.read_text());require(dense['stl_sha256']==args.expected_sha256,'Original dense report bound to a different STL');require(dense['flagged_samples_sha256']==hashes['flags'],'Original flag file hash mismatch')
  topology=json.loads(args.raw_report.read_text());intersection=json.loads(args.intersections_report.read_text())
  require(topology.get('stl_sha256')==args.expected_sha256 and topology.get('passed') is True and topology.get('strict_passed') is True,'Original raw mesh prerequisite has not passed on this STL')
  required_topology=['binary_length_exact','finite_original_data','all_original_faces_nondegenerate','no_duplicate_original_faces','original_stored_normals_unit','original_stored_normals_agree_with_directed_faces','exact_coordinate_edges_two_faces','exact_coordinate_consistent_winding','exact_coordinate_vertex_links_single_cycles','single_surface_no_internal_shell','positive_signed_volume']
  require(all(topology.get('checks',{}).get(k) is True for k in required_topology),'Missing or failed topology prerequisite flag')
  require(intersection.get('stl_sha256')==args.expected_sha256 and intersection.get('stl_sha256_after_check')==args.expected_sha256 and intersection.get('passed') is True and intersection.get('strict_passed') is True and intersection.get('completed') is True and intersection.get('bad_pair_count')==0 and intersection.get('broad_phase',{}).get('all_bbox_overlapping_pairs_completed') is True,'Exact original self-intersection prerequisite has not completed and passed on this STL')
  inventory=dense.get('checker_sources_sha256');require(isinstance(inventory,dict) and inventory and topology.get('checker_sources_sha256')==inventory,'Original raw and dense checker inventories differ or are missing');require(intersection.get('tools',{}).get('source_sha256')==inventory.get('check_original_intersections.py'),'Exact intersection checker differs from original checker inventory')
  report['original_raw_and_exact_intersection_prerequisites_passed']=True
  raw,triangles,den=load(args.stl);mesh=Mesh(triangles,den);flags=json.load(gzip.open(args.flags));selected=flags if args.limit is None else flags[:args.limit];keys=[(f['original_face_index'],f['sample_index']) for f in selected];require(dense.get('original_triangles')==len(triangles) and dense.get('samples')==10*len(triangles) and dense.get('flagged_sample_count')==len(flags),'Original dense sample/face/flag counts disagree');require(all(0<=f<len(triangles) and 0<=s<10 for f,s in keys),'Out-of-range original face/sample');require(len(keys)==len(set(keys)) and keys,'No samples or duplicate selected samples')
  required_hex=[k+'_hex' for k in ['x','y','z','nx','ny','nz','origin_x','origin_y','origin_z','dx','dy','dz']]
  for flag in selected:require(all(k in flag['original_cpp_row'] for k in required_hex),'Original numerical run lacks lossless hexfloat descriptors; recreated/ideal rays cannot substitute')
  import io,lzma
  require(Path(dense['csv_file']).name==dense['csv_file'],'CSV evidence must be a local basename');csvpath=args.dense_report.parent/dense['csv_file'];require(csvpath.is_file() and sha(csvpath)==dense['csv_compressed_sha256'],'Original compressed CSV hash mismatch');paths['original_csv']=csvpath;hashes['original_csv']=sha(csvpath)
  compression=dense['csv_compression'];require(compression in ('gzip','xz'),'Missing or unsupported CSV compression');require(csvpath.name.endswith('.csv.gz' if compression=='gzip' else '.csv.xz'),'CSV container/extension mismatch')
  opener=gzip.open if compression=='gzip' else lzma.open
  with opener(csvpath,'rb') as handle:require(hashlib.file_digest(handle,'sha256').hexdigest()==dense['uncompressed_csv_sha256'],'Original uncompressed CSV hash mismatch')
  wanted={k:f for k,f in zip(keys,selected)};matches={};all_samples=bytearray(10*len(triangles));csv_rows=0
  with opener(csvpath,'rt',newline='') as handle:
   for row in csv.DictReader(handle):
    key=(int(row['face']),int(row['sample']));face,sample=key;require(0<=face<len(triangles) and 0<=sample<10,'Out-of-range face/sample anywhere in original CSV');index=10*face+sample;require(all_samples[index]==0,'Duplicate face/sample anywhere in original CSV');all_samples[index]=1;csv_rows+=1
    if key in wanted:
     require(key not in matches,'Duplicate original sample in full CSV');require(row==wanted[key]['original_cpp_row'],'Flag descriptor differs from its full original CSV row');matches[key]=True
  require(csv_rows==10*len(triangles) and all(all_samples),'Original CSV does not cover every original face/sample exactly once');require(len(matches)==len(wanted),'Selected flags missing from full original CSV')
  report['full_original_csv_rows_verified']=csv_rows;report['full_original_csv_exact_face_sample_coverage']=True
  for flag in selected:
   face,sample=flag['original_face_index'],flag['sample_index'];desc=flag['original_cpp_row']
   try:row=classify(mesh,desc,desc)
   except Exception as e:row={'original_face_index':face,'sample_index':sample,'exact_classification_completed':False,'error_type':type(e).__name__,'error':str(e),'original_cpp_descriptor':desc}
   row['original_run_lossless_descriptor_used']=True;row['original_numerical_reasons']=flag['reasons'];rows.append(row);print(json.dumps({'done':len(rows),'total':len(selected),'face':face,'sample':sample,'completed':row['exact_classification_completed']}),flush=True)
  details=args.out/'exact-recorded-ray-details.jsonl.gz'
  with details.open('wb') as h:
   with gzip.GzipFile(filename='',fileobj=h,mode='wb',mtime=0) as z:
    for row in rows:z.write((json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode())
  require(all(sha(p)==hashes[k] for k,p in paths.items()),'Original input or diagnostic/checker source changed during analysis')
  report.update(completed=True,total_flagged_samples=len(flags),selected_samples=len(rows),all_flagged_samples_selected=len(rows)==len(flags),all_selected_rays_exactly_classified=all(r['exact_classification_completed'] for r in rows),all_selected_first_chords_ge_0p8mm=all(r.get('conservative_first_solid_chord_ge_0p8mm') is True for r in rows),all_original_inputs_and_sources_unchanged=True,all_selected_descriptors_match_original_full_csv=True,detail_file=details.name,detail_sha256=sha(details),original_numerical_strict_passed=dense['strict_passed'])
 except Exception as e:report.update(completed=False,all_selected_rays_exactly_classified=False,all_selected_first_chords_ge_0p8mm=False,all_original_inputs_and_sources_unchanged=False,error_type=type(e).__name__,error=str(e))
 report['elapsed_seconds']=time.time()-start;(args.out/'exact-recorded-ray-summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 return 0 if report['completed'] and report['all_selected_rays_exactly_classified'] and report['all_selected_first_chords_ge_0p8mm'] and report.get('all_flagged_samples_selected') is True and report['all_original_inputs_and_sources_unchanged'] and 'error' not in report else 1
if __name__=='__main__':raise SystemExit(main())
