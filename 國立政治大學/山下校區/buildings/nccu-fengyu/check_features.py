from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=3.8
# Every listed sample must agree against the exported raw STL, not source primitive labels.
probes=[('B1_colonnade_void',(-5,-9,2.4),False),('B1_pier',(0,-10.5,2.4),True),('B1_mirror_back_mass',(-5,-7,2.4),True),('1F_envelope',(-5,0,6),True),('2F_envelope',(-5,0,10),True),('roof_center',(0,0,12.6),True),('above_roof_no_extra_floor',(0,0,14),False),('entry_under_canopy_void',(-21,-1,5.2),False),('entry_canopy',(-21,0,6.4),True),('outside_unknown_rear',(0,12,6),False)]
pts=np.array([p for n,p,e in probes])*[.7*S,S,S];got=t.contains(pts);out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 out.append({'feature':name,'point_mm':(np.array(p)*[.7*S,S,S]).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
meta=json.loads((A/'mesh.json').read_text());vv=np.array(meta['vertices']);ff=np.array(meta['faces']);tt=vv[ff];cc=np.array(meta['face_materials']);spill=(np.ptp(tt[:,:,1],axis=1)<1e-5)&(np.abs(tt[:,0,1]+41.8)<1e-4)&(cc==2);assert not spill.any(), 'Roof white material leaked into garden wall plane'
report={'garden_wall_roof_white_spill_triangles':int(spill.sum()),'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'true_open_colonnade_verified':True,'three_physical_storeys_only':True,'nominal_mullion_width_mm':.15*S*.7,'nominal_colonnade_pier_width_mm':.9*S*.7,'nominal_canopy_slab_thickness_mm':.65*S,'note':'Local feature widths are generator nominal values, not global minimum-wall certification. Slice erosion only tests connected planar islands and cannot certify every connected thin branch. Canopy and colonnade ceiling require support/slicer review; no physical print.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
