#!/usr/bin/env python3
"""Independent long-double original-BVH verification of all capsule clearances."""
from check_root_supports import *
def audit(stl=None):
 out=HERE/'root_evidence';report=json.loads((out/'root_support_report.json').read_text());detail=json.load(gzip.open(out/report['detail_file'],'rt'));stl=Path(stl)if stl is not None else HERE/'output/model.stl';_,tri,_=raw_read(stl)
 assert report['stl_sha256']==sha(stl)
 points=[w['point_mm']for p in detail['paths']for w in p['point_distance_witnesses']]
 with tempfile.TemporaryDirectory(prefix='root_clearance_',dir=out)as td:
  d=Path(td);tri.astype('<f8').tofile(d/'root_tri.bin');np.array(points,dtype='<f8').tofile(d/'root_pts.bin');subprocess.run(['g++','-O3','-std=c++17',str(HERE/'root_clearance.cpp'),'-o',str(d/'root_verify')],check=True);subprocess.run([str(d/'root_verify'),str(d/'root_tri.bin'),str(d/'root_pts.bin'),str(d/'root_distance.csv')],check=True);rows=np.loadtxt(d/'root_distance.csv',delimiter=',')
 checks=[];cursor=0;pointrecords=[]
 for path in detail['paths']:
  a=cursor;b=a+len(path['point_distance_witnesses']);dist=rows[a:b,1];cursor=b;lower=float(dist.min()-path['sample_spacing_mm']/2-path['numeric_guard_mm']);diffs=[]
  for i,w in enumerate(path['point_distance_witnesses']):
   row=rows[a+i];diff=float(abs(row[1]-w['candidate_minimum_distance_mm']));diffs.append(diff);pointrecords.append({'path_id':path['path_id'],'sample_index':i,'point_mm':w['point_mm'],'long_double_nearest_original_face_id':int(row[2]),'long_double_distance_mm':float(row[1]),'long_double_nearest_point_mm':row[3:].tolist(),'python_distance_mm':w['candidate_minimum_distance_mm'],'absolute_method_difference_mm':diff})
  checks.append({'path_id':path['path_id'],'root_name':path['root_name'],'name':path['name'],'independent_continuous_clearance_lower_bound_mm':lower,'independent_continuous_diameter_lower_bound_mm':2*lower,'maximum_point_distance_disagreement_mm':max(diffs),'passed':lower>=.4 and max(diffs)<1e-8})
 gzipjson(out/'root_clearance_details.json.gz',{'stl_sha256':report['stl_sha256'],'paths':checks,'point_distance_records':pointrecords})
 r={'passed':all(c['passed']for c in checks),'stl_sha256':sha(stl),'source_support_report_sha256':sha(out/'root_support_report.json'),'source_support_details_sha256':sha(out/'root_support_details.json.gz'),'original_triangles':len(tri),'original_mesh_points_checked':len(rows),'core_paths_checked':len(checks),'minimum_independent_continuous_diameter_lower_bound_mm':min(c['independent_continuous_diameter_lower_bound_mm']for c in checks),'maximum_point_distance_disagreement_mm':max(c['maximum_point_distance_disagreement_mm']for c in checks),'failed_paths':[c for c in checks if not c['passed']],'method':'Independent long-double closest-point-on-triangle calculations through an all-original-triangle BVH. Each node bounding box gives a conservative Euclidean lower bound, with no feature masks or face filtering. Complete path clearances use the same 1-Lipschitz spacing/2 and1e-6mm guard as the primary certificate.','validator_sha256':{'root_clearance.cpp':sha(HERE/'root_clearance.cpp'),'check_root_clearance.py':sha(Path(__file__))},'detail_file':'root_clearance_details.json.gz','detail_sha256':sha(out/'root_clearance_details.json.gz')};writejson(out/'root_clearance_report.json',r);print(json.dumps(r,indent=2));return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--stl',type=Path,default=HERE/'output/model.stl');x=a.parse_args();raise SystemExit(0 if audit(x.stl)['passed']else 1)
