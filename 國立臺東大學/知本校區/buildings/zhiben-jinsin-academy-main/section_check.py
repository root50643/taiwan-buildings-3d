"""Compute 0.2 mm horizontal geometric sections of the actual delivered STL.
This is not a slicer, toolpath simulation, support check, or physical print test.
Run: python section_check.py
"""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh
r=Path(__file__).resolve().parent
m=trimesh.load(r/'model.stl',force='mesh',process=True)
solid=Manifold(Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
assert solid.status().name=='NoError'
rows=[];bad=[]
for z in np.arange(.1,float(m.bounds[1,2]),.2):
 cs=solid.slice(float(z));polys=cs.to_polygons();area=float(cs.area())
 finite=all(np.isfinite(p).all() for p in polys)
 valid=bool(polys) and area>0 and finite and all(len(p)>=3 for p in polys)
 if not valid:bad.append(float(z))
 rows.append({'z_mm':round(float(z),4),'area_mm2':round(area,6),'contours':len(polys),'finite_nonempty':valid})
report={'passed':not bad,'stl_sha256':hashlib.sha256((r/'model.stl').read_bytes()).hexdigest(),'method':'Manifold cross-sections reconstructed from the delivered STL, 0.2 mm spacing with 0.1 mm offset. Closed polygon contours are returned by the geometry kernel.','section_count':len(rows),'spacing_mm':.2,'sample_offset_mm':.1,'failed_z_mm':bad,'max_contour_count':max(q['contours'] for q in rows),'min_section_area_mm2':min(q['area_mm2'] for q in rows),'sections':rows,'limitations':['Not slicer or physical print validation.','Does not calculate extrusion paths, bridging, support material, adhesion, or minimum printable thickness.','Multiple contours above the base can be legitimate roofs, columns, or open courtyards; these are not automatically classified as disconnected printable bodies.','Finite sampled sections do not prove every possible inter-layer defect absent.']}
(r/'section_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(r.name,report['passed'],report['section_count']);raise SystemExit(0 if report['passed'] else 1)
