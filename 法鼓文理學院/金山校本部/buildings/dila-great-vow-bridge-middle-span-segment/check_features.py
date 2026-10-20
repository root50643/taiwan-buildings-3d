"""Bridge open-rail / rooted details / local slice loss checks, not print certification."""
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
def center(x):return 5*((x+70)/140)**2
def width(x):return 38-6*((x+70)/140)**1.5
def highy(x,z):return center(x)+width(x)/2+(z-5)*.19
def lowy(x,z):return center(x)-width(x)/2-(z-5)*.16
probes=[]
for a in np.arange(-69.5,66.5,3.5):
 x=a+2.2
 for z in [7,11,13]:
  y=lowy(x,z);n=section(z).intersection(LineString([(x,y-1.2),(x,y+1.2)])).length
  assert n<1e-7,(x,z,n);probes.append({'x_mm':float(x),'z_mm':z,'air_chord_mm':2.4})
# High girder deliberately solid while opposite rail remains open.
high=[]
for x in [-60,-30,0,30,60]:
 for z in [7,12,20]:
  y=highy(x,z);v=section(z).intersection(LineString([(x,y),(x,y+2.1)])).length
  assert v>2.09;high.append({'x_mm':x,'z_mm':z,'solid_chord_mm':v})
ribs=[]
for x in np.linspace(-65,65,13):
 y=highy(x,1)+4
 chord=section(1).intersection(LineString([(x-1,y),(x+1,y)])).length
 assert chord>1.29;ribs.append({'x_mm':float(x),'rib_projection_chord_mm':chord})
rows=[];previous=None
for z in list(np.arange(.2,m.bounds[1,2],.2))+[m.bounds[1,2]-.001]:
 g=section(z);opened=g.buffer(-.4,quad_segs=24).buffer(.4,quad_segs=24);loss=g.difference(opened)
 unsupported=g.difference(previous.buffer(.2)).area if previous is not None else 0
 rows.append({'z_mm':float(z),'slice_area_mm2':g.area,'lost_local_area_mm2':loss.area,'local_area_loss_percent':100*loss.area/g.area,'loss_bounds_mm':list(loss.bounds) if not loss.is_empty else [],'new_area_outside_previous_plus_0_2mm_mm2':unsupported});previous=g
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'open_low_railing_probes':probes,'single_solid_high_girder_probes':high,'registered_approx13_rib_probes':ribs,'method':'Raw STL slices, local inward/outward0.4 mm opening (24 round-join segments); no loss exemption. Consecutive-layer+0.2mm overlap diagnostic is NOT support simulation.','all_slice_local_loss':rows,'worst_local_area_loss':max(rows,key=lambda q:q['local_area_loss_percent']),'largest_layer_overlap_deficit':max(rows,key=lambda q:q['new_area_outside_previous_plus_0_2mm_mm2']),'design_widths_mm':{'girder_envelope':2.1,'rail_post_x':1,'lower_rail':.9,'handrail':1.6,'rib_x':1.3,'wood_strip_projection':.55,'deck_plank_groove':.28},'limitations':['Top sloped girder terminates in a tiny near-top slice: that component fails 0.8mm erosion, explicitly retained, not exempted.','Wood-strip projection and fine plank grooves are sub0.8mm details and may be lost; component survival does not demonstrate detail reproduction.','Initial low girder edge is not a stable print base; ribs/deck underside/rails require generated support or different orientation. No fictitious real bridge piers added.','13 ribs are approximately image-counted; even spacing and model dimensions are photographic fits.','No FFF toolpath, physical print, load test or measured architectural survey.']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['worst_local_area_loss','largest_layer_overlap_deficit']}))
