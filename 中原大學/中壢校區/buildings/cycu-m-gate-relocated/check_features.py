"""Opening/foot/local-loss checks of raw validated STL. Not physical print certification."""
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
for x in [-42,0,42]:
 for z in [10,50,80,95]:
  clear=section(z).intersection(LineString([(x,-21),(x,21)])).length==0;assert clear
  checks.append({'feature':'longitudinal main arch','center_x_mm':x,'z_mm':z,'through_clear':clear})
for x in [-63,-21,21,63]:
 for z in [10,50,65,70]:
  clear=section(z).intersection(LineString([(x-4,0),(x+4,0)])).length==0;assert clear
  checks.append({'feature':'perpendicular small arch','center_x_mm':x,'z_mm':z,'through_clear':clear})
g=section(20);assert g.geom_type=='MultiPolygon' and len(g.geoms)==8
feet=[]
for x in [-63,-21,21,63]:
 for y in [-10.1,10.1]:
  p=g.intersection(box(x-3,y-3.2,x+3,y+3.2));core=p.buffer(-.4);assert not core.is_empty
  feet.append({'x_mm':x,'y_mm':y,'bounds_mm':list(p.bounds),'area_mm2':p.area,'0_8mm_core_survives':True})
# Every slice gets local morphological opening loss; a surviving whole component is NOT zero local loss.
rows=[]
for z in list(np.arange(.2,m.bounds[1,2],.2))+[m.bounds[1,2]-.001]:
 g=section(z);opened=g.buffer(-.4,quad_segs=24).buffer(.4,quad_segs=24);loss=g.difference(opened)
 rows.append({'z_mm':float(z),'slice_area_mm2':g.area,'lost_local_area_mm2':loss.area,'local_area_loss_percent':100*loss.area/g.area,'loss_bounds_mm':list(loss.bounds) if not loss.is_empty else []})
worst=max(rows,key=lambda q:q['local_area_loss_percent'])
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'opening_checks':checks,'eight_separate_feet_above_base':True,'feet':feet,'local_loss_method':'Exact section polygons -> inward0.4mm/outward0.4mm morphological opening, round joins24; records local corner/rim loss even when whole-component erosion passes. Not extrusion path simulation.','all_slice_local_loss':rows,'worst_local_area_loss':worst,'design_widths_mm':{'pier_x':5.1,'foot_y':5.8,'barrel_shell_radial':3.0,'thickened_rim_depth':1.6,'crown_plateau_width':1.2,'base':3},'limitations':['Local corner/edge rounding loss is nonzero: use numerical rows, not a claim that all detail survives.','0.6mm outer rim rise is fused to shell; may soften in printing.','Crown plateau width1.2mm lowers theoretical circle apex by less than0.009mm for miniature robustness; not source detail.','Barrel ceilings/side openings require support or alternative print orientation.','No FFF toolpaths, printer or physical print tested.']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'eight_feet':True,'opening_checks':len(checks),'worst_local_area_loss':worst},ensure_ascii=False))
