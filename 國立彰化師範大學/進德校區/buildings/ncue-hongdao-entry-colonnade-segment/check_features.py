"""Source-bounded feature audit; digital geometry, not physical print certification."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,LineString,GeometryCollection,box
A=Path(__file__).resolve().parent
m=trimesh.load_mesh(A/'model.stl',process=True)
s=md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def section(z):
 g=GeometryCollection()
 for p in s.slice(z).to_polygons():g=g.symmetric_difference(Polygon(p))
 return g
checks=[]
for z in [23.1,30,38,43,46]:
 g=section(z);clear=g.intersection(LineString([(3,-12),(3,8.6)])).length==0;assert clear
 assert g.intersection(LineString([(3,10.6),(3,15.9)])).length>5
 checks.append({'z_mm':z,'front_to_recess_clear':clear,'backed_door_not_through_portal':True})
# Tall separated pale piers have empty space behind them and ahead of window wall.
for x in [-66,-44,-22,22,44,66]:
 assert section(60).intersection(LineString([(x,-12),(x,-6)])).length>5.9
 assert section(60).intersection(LineString([(x,-5.4),(x,-4.1)])).length==0
# Local erosion measures pier survival independently, not whole-component proxy.
local=[]
for x in [-66,-44,-22,22,44,66]:
 p=section(60).intersection(box(x-2,-13,x+2,-5))
 assert not p.buffer(-.4).is_empty
 local.append({'feature':'external pier','x_mm':x,'width_mm':2.8,'0_8mm_core_survives':True})
# Geometry-defined stair positions, first through nineteenth risers are actually present.
for i in range(19):
 y=-40+i*1.45
 assert section(3+i+.5).intersection(LineString([(-17,y),(17,y)])).length>33
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'entry_recess':checks,'external_column_gap_verified':True,'local_feature_erosion':local,'nineteen_explicit_stair_risers':True,'design_widths_mm':{'external_piers':2.8,'stair_side_buttresses':3,'window_relief_frame':.9,'entry_frame':1.1,'roof_slab':3.5,'base':3},'limitations':['0.9 mm frame relief is fused into backing but may be lost or softened at practical extrusion widths.','Erosion is a digital cross-section test, not nozzle/toolpath simulation.','Roof cantilever, entry beam and column spaces require slicer support/orientation judgment.','Stair depth is deliberately compressed; not a measured stair or accessibility design.','No FFF slicer, machine or physical print tested.']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
