from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-630)/20,(530-y)/20,z])*4
probes=[('central3F_real_room',(630,530,11),True),('west3F_wing',(250,530,11),True),('east3F_wing',(1020,530,11),True),('north3F_wing',(630,230,11),True),('south3F_wing',(630,830,11),True),('east2F_balcony_air',(980,530,7),False),('south2F_balcony_air',(630,795,7),False),('north2F_balcony_air',(630,260,7),False),('west2F_balcony_air',(285,530,7),False),('east2F_recessed_room',(950,530,7),True),('east_entry_air',(955,640,3),False),('east_entry_fullheight_door',(943,640,3),True),('entry_canopy',(280,420,5),True),('entry_canopy_soffit_air',(280,420,4),False),('west_entry_air',(310,420,3),False),('west_entry_door',(322,420,3),True),('partial_B1_east',(700,530,.5),True),('no_fullB1_west',(450,530,.5),False),('west_wall_footing_grounded',(300,530,.5),True),('west_footing_underside_air',(330,530,.5),False),('northeave_slab',(630,180,12.6),True),('northeave_soffit_air',(630,180,12),False),('westeave_slab',(200,530,12.6),True),('no_rooftower',(630,530,14),False),('west_ramp_top_landing',(245,465,1.2),True)]
got=t.contains(np.array([point(p) for n,p,e in probes]));out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,p,g,expected)
 out.append({'feature':name,'point_mm':point(p).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=point(q);d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
rays={}
for name,q,h in [('centralroof',(630,530,15),12.8),('north_eave',(630,180,15),12.8),('west_eave',(200,530,15),12.8),('entrycanopy',(255,420,8),5.18)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-h)*4)<.004,(name,hits);rays[name]={'hits_mm':hits,'expected_first_height_mm':h*4}
steps=[]
for side in ['NW','SE']:
 for i in range(8):
  q=(450,247-i*5+2,2) if side=='NW' else (800,840+i*5-2,2);hits=ray(q,(0,0,-1));height=2-hits[0]/4;expected=1.65-i*.19
  assert abs(height-expected)<.001,(side,i,height,expected);steps.append({'side':side,'step':i,'height_mm':height*4,'expected_approx_mm':expected*4})
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'roof_direct_rays':rays,'two_bent_stairs_direct_rays':steps,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'manufacturing_limits':'Not physically printed or toolpathcertified. Fine windowframes/rails below0.8mm; balcony/roof eaves and porch mayneed support. B1 onlybounded exterior proxy; west underside open between narrow groundfootings, enclosed-room masses solid proxies notsurveyed interiors. Any subsequent hollowing needs resin drainage/venting. No supportfree/globalminimumwallcertificate.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
