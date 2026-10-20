"""Real aperture checks plus local morphological loss, never a printability guarantee."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,LineString
A=Path(__file__).resolve().parent;t=trimesh.load_mesh(A/'model.stl',process=True)
m=md.Manifold(md.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
def section(z):
 g=GeometryCollection()
 for p in m.slice(float(z)).to_polygons():g=g.symmetric_difference(Polygon(p))
 return g
checks=[]
for x in [-65,-51,-37,-23,23,37,51,65]:
 for z in [20,40,65]:
  y=-8-.0028*x*x;clear=section(z).intersection(LineString([(x,y-3),(x,y+3)])).length<1e-7;assert clear;checks.append({'kind':'tall_slit','x':x,'z':z,'screen_clear':clear})
for x in [-10,-5,0,5,10]:
 y=-8-.0028*x*x;clear=section(73).intersection(LineString([(x,y-3),(x,y+3)])).length<1e-7;assert clear;checks.append({'kind':'square_hole','x':x,'z':73,'screen_clear':clear})
for z in [11,30,60]:
 clear=section(z).intersection(LineString([(0,-12),(0,4)])).length<1e-7;assert clear;checks.append({'kind':'central_portal','z':z,'screen_to_recess_clear':clear})
rows=[]
for z in np.r_[np.arange(.2,88,.2),87.999]:
 g=section(z);er=g.buffer(-.4,quad_segs=32);restored=er.buffer(.4,quad_segs=32);lost=g.difference(restored);cores=lost.buffer(-.05,quad_segs=16)
 rows.append({'z_mm':float(z),'lost_area_mm2':float(lost.area),'lost_fraction':float(lost.area/g.area),'loss_core_after_0_05mm_erosion_mm2':float(cores.area),'loss_bounds':list(lost.bounds) if not lost.is_empty else []})
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'aperture_checks':checks,'local_0_8mm_feature_method':'At every 0.2mm layer plus top-0.001: morphological opening buffer(-0.4).buffer(0.4), record ALL loss areas; an extra -0.05mm erosion of lost region identifies loss beyond routine rounded corners. No exemption removes a measured loss. Not FFF toolpath simulation.','local_loss_layers':sum(r['lost_area_mm2']>1e-8 for r in rows),'loss_core_layers':sum(r['loss_core_after_0_05mm_erosion_mm2']>1e-8 for r in rows),'maximum_lost_fraction':max(r['lost_fraction'] for r in rows),'layers':rows,'designed_minimums_mm':{'handrail_horizontal_height':.9,'handrail_width':1.1,'handrail_post':1.3,'glazing_mullion':1.,'screen_depth':4.,'square_aperture_width':2.8,'slit_width':6.5,'stair_rise':1.},'warnings':['Morphological local losses retained even when every whole component survives.','Portal lintel and eight long slit tops bridge open spaces; supports/orientation need actual slicer review.','0.9mm rail height and 1.0mm frames are small display features, not universally printable.','No FFF toolpaths or physical print test.','Recessed glass is solid surface; screen openings alone are through-open.']}
(A/'qa/feature-validation.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['layers','aperture_checks']})
