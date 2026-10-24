from pathlib import Path
import json,hashlib
import numpy as np,trimesh
A=Path(__file__).resolve().parent;m=trimesh.load(A/'model.stl',process=False);m.merge_vertices(digits_vertex=12)
def world(p):x,y,z=p;return [(x-21.5)*3,(y-10)*3,z*3]
G=1.2;H=3.45;RF=G+7*H
probes={'central_6F_occupied_not_atrium':((22,14,G+5.5*H),True),'continuous_main_roof':((22,14,RF+.15),True),'left_roof_access':((4,12,RF+1),True),'right_roof_access':((40,15,RF+1),True),'under_canopy_air':((10,25,G+H/2),False),'entry_recess_air':((10,20,G+H/2),False),'separate_bridge_span_not_included':((15,30,G+H),False),'central_projecting_room_7F':((20,24,G+6.5*H),True),'rear_3F_deeper_wing':((10,-3,G+2.5*H),True),'rear_5F_terrace_air':((10,-3,G+4.5*H),False)}
results={}
for name,(p,expected) in probes.items():
 actual=bool(m.contains([world(p)])[0]);results[name]={'source_relative_point':p,'expected_solid':expected,'actual_solid':actual};assert actual==expected,name
# Probe local normal thickness by rays started just inside triangle centroids. This is a sampling report, not minimum-wall certification.
ids=np.linspace(0,len(m.faces)-1,min(1800,len(m.faces)),dtype=int);norm=m.face_normals[ids];orig=m.triangles_center[ids]-norm*.0001
loc,ir,it=m.ray.intersects_location(orig,-norm,multiple_hits=True);dist=np.linalg.norm(loc-orig[ir],axis=1);keep=dist>1e-6;mins=np.full(len(ids),np.inf)
for i,d in zip(ir[keep],dist[keep]):mins[i]=min(mins[i],d)
valid=mins[np.isfinite(mins)];thin=[{'face':int(ids[i]),'sampled_thickness_mm':float(t)} for i,t in enumerate(mins) if t<.8]
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'probes':results,'normal_thickness_sampling':{'samples':len(ids),'valid_hits':len(valid),'minimum_sampled_mm':float(valid.min()),'below_0_8mm_count':len(thin),'thin_samples':thin,'method':'triangle-centroid inward normal nearest opposing surface; sampled only, not exhaustive wall certification'},'downward_facing_surface_area_mm2':float(m.area_faces[(m.face_normals[:,2]<-.707)&(m.triangles_center[:,2]>.01)].sum()),'manufacturing':'Overhangs, canopy, red sloped canopy ribs, grille and mullions require slicer review. No slicer-generated toolpath or physical print; not support-free certified.'}
(A/'qa/feature-and-thickness-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='normal_thickness_sampling'}));print('THIN SAMPLES',len(thin))
