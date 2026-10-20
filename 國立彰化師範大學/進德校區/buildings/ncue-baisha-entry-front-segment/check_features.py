"""Check passage and backed detail geometry; not an FFF slicer or print certification."""
from pathlib import Path
import json,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,LineString,GeometryCollection
A=Path(__file__).resolve().parent
m=trimesh.load_mesh(A/'model.stl',process=True)
s=md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def slice_at(z):
 g=GeometryCollection()
 for p in s.slice(z).to_polygons():g=g.symmetric_difference(Polygon(p))
 return g
checks=[]
for z in [9.1,15,30,45,60,65,70,74]:
 g=slice_at(z);line=LineString([(20,-14),(20,14)]);clear=g.intersection(line).length==0;assert clear
 checks.append({'z_mm':z,'center_line_full_depth_clear':clear})
# Recess is not a loose frame: backed exterior mass remains at y=0 in strip regions.
for x in [-9.6,49.6]:
 assert slice_at(35).intersection(LineString([(x,-7.4),(x,13.9)])).length>20
# Recessed panes remain solid surfaces; the portal alone is through-open.
assert slice_at(99).intersection(LineString([(20,-9.6),(20,13.9)])).length>23
r={'stl_sha256':__import__('hashlib').sha256((A/'model.stl').read_bytes()).hexdigest(),'through_portal_samples':checks,'window_frames_solid_backed':True,'design_feature_widths_mm':{'upper_and_side_mullion':0.9,'wing_mullion':1.0,'coffer_beam':1.4,'floor_band_height':3.0,'base':3.0,'step_rise':0.75},'thin_feature_reasoning':'0.9/1.0 mm mullions are bonded relief on solid backing, not free-standing printable wires. Component erosion alone does not certify local feature thickness; dimensions are explicit in generator. 0.75 mm step rise is a height, not wall width. 1.4 mm grid beams bridge the opening overhead and require support assessment.','support_warning':'Open portal spans about 43 mm; chamfered shoulders and ceiling coffers create overhang/bridge areas. Orient/split/support in slicer; no claim of support-free printing.','not_tested':['machine slicer toolpaths','extruder assignment','physical printing','calibrated real dimensions']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
