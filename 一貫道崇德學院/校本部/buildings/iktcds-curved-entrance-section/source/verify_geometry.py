"""Reimport native STLs, check topology, assembly contacts and analytic layer screens.
Requires existing trimesh/numpy/manifold3d/shapely. Screens are not an extrusion
planner or a physical print/fit test. They do not establish unsupported bridge length.
"""
from pathlib import Path
import collections,hashlib,itertools,json,struct
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh64
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def planar_faces(v,f):
 groups=collections.defaultdict(list)
 for t in v[f]:
  cross=np.cross(t[1]-t[0],t[2]-t[0]);axis=int(np.argmax(np.abs(cross)))
  if np.ptp(t[:,axis])<1e-8 and np.linalg.norm(cross)>0:
   coords=[j for j in range(3) if j!=axis];key=(axis,round(float(t[:,axis].mean()),5),int(np.sign(cross[axis])));p=Polygon(t[:,coords])
   if p.area>1e-12:groups[key].append(p)
 return {k:unary_union(ps) for k,ps in groups.items()}
def verify_assembly(pairs):
 assert len(pairs)==45
 expected={frozenset([a,b]) for a in ['01-curved-stepped-platform','04-curved-entablature-section'] for b in ['03-curved-glazing-and-three-portals']+['column-'+str(i) for i in range(1,8)]}
 actual={frozenset(p['parts']) for p in pairs if p['opposing_axis_aligned_contact_faces_within_0_0001mm']}
 assert actual==expected and len(actual)==16
 for p in pairs:
  assert abs(p['intersection_volume_mm3'])<.001
  if frozenset(p['parts']) not in expected:assert abs(p['intersection_volume_mm3'])<1e-9 and p['minimum_surface_gap_mm_search_1000']>1
 return {'physical_instances':10,'unique_prototypes':4,'pair_checks':45,'expected_contact_pairs':16,'contact_graph_connected':True,'maximum_pair_intersection_volume_mm3':max(p['intersection_volume_mm3'] for p in pairs),'no_unexpected_intersections_over_1e_9_mm3':True,'expected_contacts_float32_residual_limit_mm3':.001,'physical_adhesive_strength_fit_and_tolerance_validated':False}
def main():
 d=json.loads((R/'geometry.json').read_text());native=[];world=[];planes=[];rows=[];scan=[]
 for p in d['parts']:
  v=np.asarray(p['vertices']);f=np.asarray(p['triangles'],dtype=np.uint64);b=(R/p['stl']).read_bytes();n=struct.unpack_from('<I',b,80)[0];raw=np.array([struct.unpack_from('<9f',b,96+50*i) for i in range(n)]).reshape(n,3,3);assert np.array_equal(v[f],raw)
  tm=trimesh.load(R/p['stl'],force='mesh',process=True);s=Manifold(Mesh64(np.asarray(tm.vertices),np.asarray(tm.faces,dtype=np.uint64)));assert s.status().name=='NoError' and len(s.decompose())==1 and tm.is_watertight and tm.is_winding_consistent and tm.volume>0
  zero=int(np.count_nonzero(np.linalg.norm(np.cross(raw[:,1]-raw[:,0],raw[:,2]-raw[:,0]),axis=1)==0));assert zero==0;native.append(s)
  # Bed footprint is the z=0 analytic cross-section, not G-code contact/extrusion.
  bed=s.slice(0);tm0=trimesh.Trimesh(v,f,process=False);down=tm0.face_normals[:,2]<-np.sqrt(.5)-1e-7
  rows.append({'part':p['id'],'sha256':hashlib.sha256(b).hexdigest(),'STL_float32_values_exact':True,'watertight':bool(tm.is_watertight),'winding_consistent':bool(tm.is_winding_consistent),'connected_components':1,'zero_area_triangles':zero,'volume_mm3':float(tm.volume),'bounds_mm':tm.bounds.tolist(),'bed_section_area_mm2':bed.area(),'downward_facing_area_over_45deg_mm2_including_bed':float(tm0.area_faces[down].sum())})
  flags=[];maxz=float(v[:,2].max());prior=None;num=0
  for z in np.arange(.1,maxz,.2):
   sec=s.slice(float(z));num+=1
   if prior is not None:
    outside=sec-prior.offset(.2);area=outside.area()
    if area>.05:
     points=np.concatenate(outside.to_polygons());bounds=[points.min(axis=0).tolist(),points.max(axis=0).tolist()]
     flags.append({'z_mm':float(z),'beyond_previous_0_2mm_dilation_area_mm2':area,'contours':outside.num_contour(),'flag_native_XY_bounds_mm':bounds})
   prior=sec
  scan.append({'part':p['id'],'layers_sampled':num,'step_mm':.2,'first_plane_mm':.1,'previous_section_radial_dilation_mm':.2,'flag_area_threshold_mm2':.05,'flagged_planes':flags,'max_flagged_area_mm2':max((q['beyond_previous_0_2mm_dilation_area_mm2'] for q in flags),default=0)})
 for inst in d['instances']:
  p=next(p for p in d['parts'] if p['id']==inst['prototype']);v=np.asarray(p['vertices']);f=np.asarray(p['triangles'],dtype=np.uint64);T=np.asarray(inst['transform']);vv=v@T[:3,:3].T+T[:3,3];w=Manifold(Mesh64(vv,f));assert w.status().name=='NoError';world.append(w);planes.append(planar_faces(vv,f))
 pairs=[]
 for i,j in itertools.combinations(range(len(d['instances'])),2):
  contacts=[]
  for (ax,coord,sign),a in planes[i].items():
   for (bx,c2,s2),b in planes[j].items():
    if ax==bx and sign==-s2 and abs(coord-c2)<1e-4:
     area=a.intersection(b).area
     if area>1e-5:contacts.append({'axis':'xyz'[ax],'plane_coordinate_mm':coord,'opposing_plane_gap_mm':abs(coord-c2),'overlapping_planar_area_mm2':area})
  inter=world[i]^world[j];assert inter.status().name=='NoError';vol=inter.volume()
  pairs.append({'parts':[d['instances'][i]['id'],d['instances'][j]['id']],'minimum_surface_gap_mm_search_1000':world[i].min_gap(world[j],1000),'intersection_volume_mm3':vol,'opposing_axis_aligned_contact_faces_within_0_0001mm':contacts})
 report={'geometry_file_sha256':hashlib.sha256((R/'geometry.json').read_bytes()).hexdigest(),'parts':rows,'assembly_pairs':pairs,'analytic_layer_screen':scan,'contact_tolerance_mm':.0001,'contact_limits':'Coplanar axis-aligned geometric contact area only; no adhesive, tolerance, press-fit or physical verification. Tiny float32 gaps/overlaps retained and quantified.','screen_limits':'Analytic section changes after 0.2 mm dilation are risk flags, not unsupported bridge lengths, extrusion paths, a slicer simulation or a support-free verdict. Sub-0.2 mm features can be missed.','physical_print_or_fit_verified':False,'actual_slicing_status':'DEFERRED_PER_USER_PRIORITY_FFF_UNVERIFIED'}
 report['assembly_check']=verify_assembly(pairs)
 (R/'qa/geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'parts':len(rows),'pair_contacts':[{k:p[k] for k in ['parts','minimum_surface_gap_mm_search_1000','intersection_volume_mm3','opposing_axis_aligned_contact_faces_within_0_0001mm']} for p in pairs],'layer_flag_counts':[(p['part'],len(p['flagged_planes']),p['max_flagged_area_mm2']) for p in scan]},ensure_ascii=False))
if __name__=='__main__':main()
