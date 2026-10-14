"""Targeted original-STL caliper rays and root continuity for finials/spire.
Does not claim exhaustive directional minimum-wall or slicer validation.
"""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=True)
def exits(o,d):
 p,_,_=m.ray.intersects_location([o],[d],multiple_hits=True)
 t=np.dot(p-np.array(o),np.array(d));return sorted(float(x) for x in t if x>1e-6)
def calipers(x,y,z):
 out={}
 for axis,d in [('x',[1,0,0]),('y',[0,1,0])]:
  a=exits([x,y,z],d);b=exits([x,y,z],[-v for v in d]);assert a and b
  out[axis+'_width_mm']=a[0]+b[0]
 return out
features=[]
for x in [-49.5,49.5]:
 for y in [-58.1,58.1]:features.append((f'wing_finial_{x}_{y}',x,y,41.9,50.45,1.15))
for x in [-29,29]:features.append((f'hall_finial_{x}',x,-21.95,51.2,59.05,1.15))
features.append(('central_spire_cross',0,-21.95,50.8,66.1,1.2))
checks={};rows=[]
for name,x,y,root,top,width in features:
 # Caliper through the centre, .001 mm below the actual closed top surface.
 z=top-.001;c=calipers(x,y,z)
 roots=exits([x,y,root],[0,0,1]);ok=bool(roots) and abs(roots[0]-(top-root))<1e-4
 checks[name+'_root_to_top_continuous']=ok
 checks[name+'_top_xy_caliper_retained']=min(c.values())>=width-1e-4
 rows.append({'feature':name,'axis_xy_mm':[x,y],'root_test_z_mm':root,'top_z_mm':top,'top_caliper_test_z_mm':z,**c,'first_root_ray_exit_distance_mm':roots[0] if roots else None,'minimum_designed_top_width_mm':width})
# Critical high-loss layer: central cross stem = 1.2 mm backed/connected square.
c=calipers(0,-21.95,63.271);checks['high_loss_square_actual_1_2mm']=all(abs(v-1.2)<1e-4 for v in c.values())
layers=json.loads((R/'layer-component-check.json').read_text());worst=max(layers['layers'],key=lambda r:r['fraction']);worst_c=max(layers['original_component_checks'],key=lambda r:r['opening_loss_fraction'])
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'targeted_features':rows,'high_loss_section':{'z_mm':63.271,**c,'section_shape':'central cross stem square; original section remains one Polygon','reference_opening_mm':.8,'square_corner_opening_loss_explanation':'At this layer the entire section is approximately 1.2 x 1.2 mm. Radius .4 mm opening rounds the four convex corners while retaining the core. No vanishing or splitting.'},'worst_total_layer':worst,'worst_original_polygon':worst_c,'limits':['Calipers at selected vertical ornament tops and axial root rays do not prove minimum thickness in every direction.','Cross arms, eaves and portico overhangs still require slicer support inspection.','Do not scale down; fragile details need physical print testing.']}
(R/'ornament-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
