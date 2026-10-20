"""Local fin/open-gap/slice-loss audit; no toolpath or physical-print claim."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,LineString,GeometryCollection
A=Path(__file__).resolve().parent
m=trimesh.load_mesh(A/'model.stl',process=True)
s=md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def section(z):
 g=GeometryCollection()
 for p in s.slice(z).to_polygons():g=g.symmetric_difference(Polygon(p))
 return g
probes=[]
for i in range(9):
 for z in [52,67,82]:
  a=(1-(z-44)/60)**1.65*np.pi/2
  x=-49.5+i*11+(10.35*np.cos(a)+11)/2;line=LineString([(x,-12),(x,-1)])
  overlap=section(z).intersection(line).length;assert overlap<1e-7,(i,z,overlap)
  probes.append({'bay':i+1,'z_mm':z,'x_mm':x,'through_air_length_mm':11})
# Foot, middle, upper leaf mid-width thickness; keep test localized away from backing.
thickness=[]
for i in range(9):
 for z in [48,65,81,95]:
  a=(1-(z-44)/60)**1.65*np.pi/2;c=np.array([-49.5+i*11+5.175*np.cos(a),-5.175*np.sin(a)]);n=np.array([np.sin(a),np.cos(a)])
  line=LineString([c-1.0*n,c+1.0*n]);v=section(z).intersection(line).length
  assert v>1.25,(i,z,v)
  thickness.append({'bay':i+1,'z_mm':z,'local_mid_leaf_chord_mm':v})
# Entrance set back: the space directly under slab nose is real air.
for x in [-25,0,25]:assert section(20).intersection(LineString([(x,-12),(x,6.5)])).length==0
rows=[];previous=None
for z in list(np.arange(.2,m.bounds[1,2],.2))+[m.bounds[1,2]-.001]:
 g=section(z);opened=g.buffer(-.4,quad_segs=24).buffer(.4,quad_segs=24);loss=g.difference(opened)
 unsupported=g.difference(previous.buffer(.2)).area if previous is not None else 0
 rows.append({'z_mm':float(z),'slice_area_mm2':g.area,'lost_local_area_mm2':loss.area,'local_area_loss_percent':100*loss.area/g.area,'loss_bounds_mm':list(loss.bounds) if not loss.is_empty else [],'new_area_outside_previous_plus_0_2mm_mm2':unsupported});previous=g
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'registered_cropped_bays':9,'open_screen_gap_probes':probes,'local_leaf_thickness_probes':thickness,'inset_entrance_air_probes':3,'method':'Exact STL sections; inward/outward0.4mm morphological opening with round joins24. Local loss remains visible even when an entire slice component survives. Consecutive-layer+0.2mm overlap is a diagnostic only, not a slicer/support solver.','all_slice_local_loss':rows,'worst_local_area_loss':max(rows,key=lambda q:q['local_area_loss_percent']),'largest_layer_overlap_deficit':max(rows,key=lambda q:q['new_area_outside_previous_plus_0_2mm_mm2']),'design_widths_mm':{'leaf_skin':1.3,'strengthened_horizontal_ribs':2.05,'root_post_x':1.8,'main_slab':3.6,'base':3},'limitations':['Microperforations omitted: solid printable leaf proxy is not acoustical/daylight reconstruction.','Seven ribs and lower glazing divisions are simplified visual rhythm, not counted construction details.','Curved fin undersides, horizontal ribs, cantilever slab and top closure may require supports, orientation change, or splitting; do not print unsupported upright based on this report.','No FFF toolpaths, mechanical testing, or physical print.']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['worst_local_area_loss','largest_layer_overlap_deficit']}))
