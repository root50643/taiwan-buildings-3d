"""Local relief checks on raw delivered STL, not just global component survival."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def geometry(contours):
 g=GeometryCollection()
 for c in contours:
  if len(c)>2:g=g.symmetric_difference(Polygon(c))
 return g
def comps(g):return list(g.geoms) if g.geom_type=='MultiPolygon' else ([] if g.is_empty else [g])
# Rotate each face outward normal to +Z; exact mesh slices at 0.1/0.5/0.8 mm projection.
m=m^md.Manifold.cube((200,100,25)).translate((-100,-50,103))
faces={'west':m.rotate((-90,0,0)), 'east':m.rotate((90,0,0)), 'north':m.rotate((0,-90,0)), 'south':m.rotate((0,90,0))}
result={}
for name,solid in faces.items():
 plane=9 if name in ['west','east'] else 76
 rows=[]
 for depth in [.1,.5,.8]:
  g=geometry(solid.slice(plane+depth).to_polygons());cs=comps(g)
  rows.append({'projection_mm':depth,'components':len(cs),'invalid':not g.is_valid,'components_lost_under_0_4mm_erosion':sum(p.buffer(-.4).is_empty for p in cs),'minimum_component_area_mm2':min((p.area for p in cs),default=0)})
 expected=97 if name in ['west','east'] else 8
 assert all(r['components']==expected and not r['invalid'] for r in rows),(name,rows)
 result[name]=rows
# Exterior-only horizontal layers reveal thin top/bottom tips hidden by the band.
clip=md.Manifold.cube((154,2,26)).translate((-77,-11,103))
clouds=m^clip
rows=[]
for z in np.arange(103.2,128,.2):
 g=geometry(clouds.slice(float(z)).to_polygons());cs=comps(g)
 if cs:rows.append({'z_mm':float(z),'components':len(cs),'lost_under_0_4mm_erosion':sum(p.buffer(-.4).is_empty for p in cs)})
# Negative Y exterior-only clip ends at -9, so no main band included.
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'method':'Raw STL exact weld; actual face-normal slices and exterior-only west cloud horizontal slices; no contour rounding or discarded tips','face_normal_slices':result,'west_exterior_layers':rows,'west_tip_failure_layers':sum(r['lost_under_0_4mm_erosion']>0 for r in rows),'all_west_exterior_components_survive_0_8mm':all(r['lost_under_0_4mm_erosion']==0 for r in rows),'warning':'Global connected-band erosion pass does not certify scalloped cloud tips or 0.27 mm inset shoulders. Local failing tips retained and disclosed; no physical print or slicer support test.','rooting':'Every ornament intersects original band by 0.2 mm in construction; final raw surface is one closed manifold shell; actual face-normal sections preserve all expected ornaments.'}
(A/'qa/local-features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='west_exterior_layers'},indent=2))
