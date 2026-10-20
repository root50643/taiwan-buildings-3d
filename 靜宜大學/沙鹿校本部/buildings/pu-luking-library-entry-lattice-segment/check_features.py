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
# Each grid bay must retain sampled through-air, including bays crossed by chevrons.
for face,n,start,step in [('front',6,-24,8),('right',5,-18,8)]:
 for col in range(n):
  for row in range(6):
   clear=[]
   for u in [.25,.5,.75]:
    for v in [.25,.5,.75]:
     q=start+(col+u)*step;z=37+(row+v)*12
     line=LineString([(q,-20),(q,-16)]) if face=='front' else LineString([(22,q),(26,q)])
     if section(z).intersection(line).length<1e-8:clear.append([q,z])
   assert clear,(face,col,row)
   checks.append({'face':face,'column':col,'row':row,'sampled_through_air_points':clear})
for x in [-12,0,12]:assert section(25).intersection(LineString([(x,-20),(x,-16)])).length==0
# Every slice gets local morphological opening loss; a surviving whole component is NOT zero local loss.
rows=[]
for z in list(np.arange(.2,m.bounds[1,2],.2))+[m.bounds[1,2]-.001]:
 g=section(z);opened=g.buffer(-.4,quad_segs=24).buffer(.4,quad_segs=24);loss=g.difference(opened)
 rows.append({'z_mm':float(z),'slice_area_mm2':g.area,'lost_local_area_mm2':loss.area,'local_area_loss_percent':100*loss.area/g.area,'loss_bounds_mm':list(loss.bounds) if not loss.is_empty else []})
worst=max(rows,key=lambda q:q['local_area_loss_percent'])
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'open_grid_bays':checks,'front_bays':36,'right_bays':30,'open_ground_front_probes':3,'local_loss_method':'Exact section polygons -> inward0.4mm/outward0.4mm morphological opening, round joins24. Local losses are reported even when whole components survive. Not extrusion path simulation.','all_slice_local_loss':rows,'worst_local_area_loss':worst,'design_widths_mm':{'grid_bar':1.7,'grid_depth':2.8,'corner_posts':3.4,'diagonal':2.2,'display_base':3},'limitations':['Corner rounding produces nonzero local loss; no claim of perfect detail survival.','Grid beams, upper slabs and diagonal starts require support or alternative orientation.','No FFF toolpaths or physical print tested.']}
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'grid_bays':len(checks),'worst_local_area_loss':worst}))
