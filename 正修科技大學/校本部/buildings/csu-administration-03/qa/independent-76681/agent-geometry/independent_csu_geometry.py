"""Read-only independent CSU raw topology, self-contact and flat joint audit."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
from fractions import Fraction as F
from itertools import product
import hashlib,json,time
import numpy as np

HERE=Path(__file__).resolve().parent
OLD=HERE.parents[1]/'agent-geometry'
P=Path(r'<MODEL_ROOT>')
def module(name,path):
 s=spec_from_file_location(name,path);m=module_from_spec(s);s.loader.exec_module(m);return m
top=module('topology',OLD/'independent_raw_topology.py')
contact=module('contact',OLD/'independent_contact_check.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def det(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def clip(subject,triangle):
 orientation=det(sub(triangle[1],triangle[0]),sub(triangle[2],triangle[0]));sgn=1 if orientation>0 else -1
 polygon=list(subject)
 for a,b in zip(triangle,triangle[1:]+triangle[:1]):
  if not polygon:break
  edge=sub(b,a);out=[];previous=polygon[-1];dp=sgn*det(edge,sub(previous,a))
  for current in polygon:
   dc=sgn*det(edge,sub(current,a))
   if (dp<0<=dc) or (dc<0<=dp):
    t=F(dp,dp-dc);out.append(tuple(previous[k]+t*(current[k]-previous[k]) for k in (0,1)))
   if dc>=0:out.append(current)
   previous,dp=current,dc
  polygon=list(dict.fromkeys(out))
 return polygon
def area(poly):return abs(sum(det(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))))/2 if poly else F(0)
def rawtri(path):
 data,tri,scale=contact.load(path)
 return data,tri,scale,[[tuple(F(v,scale) for v in p) for p in t] for t in tri]
def main():
 start=time.monotonic();controls=contact.controls();results={};triangles={}
 for name in ['body','roof']:
  path=P/f'models/v2/parts/{name}.stl';data,tri,scale,exact=rawtri(path);triangles[name]=exact
  results[name]={'sha256':sha(data),'raw_topology':top.audit(path),'exact_self_contact':contact.full_y_sweep(tri),'integer_units_per_mm':scale}
 body,roof=triangles['body'],triangles['roof'];placement=F(85)
 maxbody=max(p[2] for t in body for p in t);minroof=min(p[2]+placement for t in roof for p in t)
 assert maxbody==minroof==85
 topfaces=[(i,[p[:2] for p in t]) for i,t in enumerate(body) if all(p[2]==maxbody for p in t)]
 bottomfaces=[(i,[p[:2] for p in t]) for i,t in enumerate(roof) if all(p[2]==0 for p in t)]
 contacts=[]
 for (i,a),(j,b) in product(topfaces,bottomfaces):
  poly=clip(a,b);ar=area(poly)
  if ar>0:contacts.append({'body_face':i,'roof_face':j,'exact_area_mm2':str(ar),'area_mm2':float(ar),'exact_xy_polygon':[[str(v) for v in p] for p in poly]})
 bodyarea=sum(area(t) for _,t in topfaces);roofarea=sum(area(t) for _,t in bottomfaces);jointarea=sum(F(r['exact_area_mm2']) for r in contacts)
 bv=sorted(set(p for _,t in topfaces for p in t));rv=sorted(set(p for _,t in bottomfaces for p in t))
 bx=[min(p[k] for p in bv) for k in (0,1)]+[max(p[k] for p in bv) for k in (0,1)]
 rx=[min(p[k] for p in rv) for k in (0,1)]+[max(p[k] for p in rv) for k in (0,1)]
 # Symmetric raw roof: signed-volume first moments, independent of assembly.
 r=np.asarray([[[float(v) for v in p] for p in t] for t in roof]);vol6=np.einsum('ij,ij->i',r[:,0],np.cross(r[:,1],r[:,2]));centroid=(vol6[:,None]*r.sum(axis=1)/4).sum(axis=0)/vol6.sum()
 joint={'placement_translation_mm':[0,0,85],'proof_of_zero_positive_volume_interference':'Every raw body vertex has Z<=85 and every placed roof vertex Z>=85. Each triangle and enclosed solid remains in its corresponding closed Z halfspace, so interiors cannot overlap. Any contact is restricted to Z=85; independent of display assembly union.',
  'body_max_Z_mm':float(maxbody),'placed_roof_min_Z_mm':float(minroof),'positive_volume_interference_mm3':0,
  'body_joint_plane_face_ids':[i for i,_ in topfaces],'roof_bottom_face_ids':[i for i,_ in bottomfaces],
  'body_joint_surface_area_mm2':float(bodyarea),'roof_bottom_area_mm2':float(roofarea),'exact_contact_area_mm2':str(jointarea),'contact_area_mm2':float(jointarea),
  'roof_bottom_area_outside_body_support_mm2':float(roofarea-jointarea),'roof_bottom_supported_area_fraction':float(jointarea/roofarea),
  'body_joint_XY_bounds_mm':[float(x) for x in bx],'roof_bottom_XY_bounds_mm':[float(x) for x in rx],
  'body_joint_unique_vertices_mm':[[float(v) for v in p] for p in bv],'roof_bottom_unique_vertices_mm':[[float(v) for v in p] for p in rv],
  'positive_area_contact_triangle_pairs':contacts,'roof_volume_centroid_local_mm':centroid.tolist(),
  'joint_design':'Plain flat butt contact; no positive XY or yaw location, no pegs/sockets/stops. Nominal centering only; adhesive layer, bonding strength, warp and clearance are not modeled.',
  'nominal_overhang_at_axis_extrema_mm':{'negative_X':float(bx[0]-rx[0]),'negative_Y':float(bx[1]-rx[1]),'positive_X':float(rx[2]-bx[2]),'positive_Y':float(rx[3]-bx[3])}}
 for name,reportpath in [('body',P/'qa/v2/body/exact-contacts.json'),('roof',P/'qa/v1/roof/exact-contacts.json')]:
  prior=json.loads(reportpath.read_text());results[name]['comparison_to_saved_exact']={'report_sha256':sha(reportpath.read_bytes()),'input_sha_matches':prior['stl_sha256']==results[name]['sha256'],'saved_candidate_pairs':prior['broad_phase']['candidate_pairs_checked'],'saved_bad_pairs':len(prior['bad_pairs']),'saved_actual_contact_pairs':prior['actual_intersection_pair_count'],'independent_candidate_pairs_match':prior['broad_phase']['candidate_pairs_checked']==results[name]['exact_self_contact']['aabb_candidate_pairs'],'independent_contact_count_matches':prior['actual_intersection_pair_count']==results[name]['exact_self_contact']['counts'].get('allowed_shared_simplex_contact',0)}
 result={'script_sha256':sha(Path(__file__).read_bytes()),'topology_helper_sha256':sha((OLD/'independent_raw_topology.py').read_bytes()),'exact_helper_sha256':sha((OLD/'independent_contact_check.py').read_bytes()),'controls':controls,'controls_evaluations':sum(r['evaluations'] for r in controls),'parts':results,'assembly_joint':joint,'elapsed_seconds':time.monotonic()-start,'formal_slicer_run':False,'physical_print_test':False,'limitations':['Exact predicates and synthetic controls are not formal verification of the implementation.','Contact area and zero nominal interference do not certify glue strength, assembly accuracy, warp, surface finish or mechanical retention.','Existing raw manufacturing flags and previous failed reports are not rewritten or canceled.','This audit reads printable parts directly; display assembly union is not used for collision or mating-area conclusions.']}
 (HERE/'independent-csu-geometry.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'parts':{k:{'sha256':v['sha256'],'topology_passed':v['raw_topology']['all_listed_checks_passed'],'exact':v['exact_self_contact']} for k,v in results.items()},'joint':{k:v for k,v in joint.items() if k not in ['positive_area_contact_triangle_pairs','body_joint_unique_vertices_mm','roof_bottom_unique_vertices_mm']},'elapsed_seconds':result['elapsed_seconds']},indent=2))
if __name__=='__main__':main()
