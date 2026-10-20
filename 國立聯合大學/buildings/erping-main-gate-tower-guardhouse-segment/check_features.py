"""Actual local STL sections, including connected small features hidden by global slices."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def g(contours):
 out=GeometryCollection()
 for p in contours:
  if len(p)>2:out=out.symmetric_difference(Polygon(p))
 return out

def audit(solid,levels):
 rows=[]
 for z in levels:
  shape=g(solid.slice(float(z)).to_polygons());parts=list(shape.geoms) if shape.geom_type=='MultiPolygon' else ([] if shape.is_empty else [shape])
  rows.append({'plane_mm':float(z),'components':len(parts),'valid':shape.is_valid,'lost_under_0_4mm_erosion':sum(p.buffer(-.4).is_empty for p in parts),'area_mm2':shape.area})
 return rows
# Side window protrusions in front of backing x=16, rotate x outward into z.
win=m ^ md.Manifold.cube((5,19,21)).translate((16.001,10.5,13.5))
window=audit(win.rotate((0,-90,0)),[16.1,16.7,17.1,17.7])
# Actual cap outer edge cropped beyond the booth wall x=16 (no central mass).
cap=m ^ md.Manifold.cube((4,42,2.2)).translate((16.001,0,44.7))
caprows=audit(cap,np.arange(44.9,46.8,.2))
# Tower wall ribs and solid backing remain separately testable using normal sections.
tower=m ^ md.Manifold.cube((24,13,50)).translate((-12,-6.5,50))
ribs=audit(tower,np.arange(50.1,100,.5))
mullions={}
for y in [17.5,22.5]:
 local=m ^ md.Manifold.cube((1.799,1.01,6)).translate((16.001,y-.505,16))
 mullions[str(y)]=audit(local,[16.1,18,21.9])
# Central rail clipped away from posts so the rail is independently measured.
rail=m ^ md.Manifold.cube((1.799,3,1.11)).translate((16.001,18.5,23.995))
railrows=audit(rail.rotate((0,-90,0)),[16.1,17,17.7])
rows=window+caprows+ribs+railrows+[r for values in mullions.values() for r in values]
result={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'method':'Delivered raw STL exact-weld. Local window outward-normal slices isolate projections beyond backing; cap outer edge clipped beyond booth wall; tower rib horizontal sections. No repairs or exemptions.','isolated_mullion_sections':mullions,'isolated_rail_normal_sections':railrows,'window_projection_slices':window,'cap_edge_layers':caprows,'tower_rib_sections':ribs,'local_failed_sections':sum(r['lost_under_0_4mm_erosion']>0 for r in rows),'all_tested_local_components_survive_0_8mm':all(r['lost_under_0_4mm_erosion']==0 for r in rows),'warning':'Section erosion is not a complete wall-thickness or support analysis. Rounded ends, tower aspect ratio, cap overhangs and orientation need slicer review. No physical print tested.'}
assert all(r['valid'] for r in rows)
(A/'qa/local-features.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['tower_rib_sections','cap_edge_layers']},indent=2))
