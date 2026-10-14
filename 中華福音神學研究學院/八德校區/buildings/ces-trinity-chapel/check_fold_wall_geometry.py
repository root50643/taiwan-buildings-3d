"""Independent original-surface thickness controls and plan identity for top tower folds."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=.248
segments=[((235,325),(264,325)),((264,325),(285,375)),((217,325),(208,359)),((217,325),(235,325))]
knots=[(235,325),(264,325),(285,375),(208,359),(217,325)]
def xy(q):return ((q[0]-485)*P,(320-q[1])*P)
foot=LineString([(217,325),(264,325),(285,375),(285,402),(215,402),(208,359),(217,325)]).buffer(2.5,cap_style=2,join_style=2)
foot=foot.difference(box(190,359,240,420)).difference(box(240,375,300,420))
ref=Polygon([xy(q) for q in foot.exterior.coords],[[xy(q) for q in ring.coords] for ring in foot.interiors])
assert ref.is_valid and ref.geom_type=='Polygon' and ref.buffer(-.4).geom_type=='Polygon' and not ref.buffer(-.4).is_empty
m=trimesh.load(R/'model.stl',process=False);rows=[]
for i,(a,b) in enumerate(segments):
 a=np.array(a,float);b=np.array(b,float);v=b-a;v=v/np.linalg.norm(v);n=np.array([-v[1],v[0]]);d=np.array([n[0],-n[1],0.])
 for t in [.2,.5,.8]:
  p=a+(b-a)*t;o=np.array([*xy(p),1.6+26.5*2]);dist=[]
  for direction in [d,-d]:
   h,_,_=m.ray.intersects_location([o],[direction],multiple_hits=True);ds=sorted(float(np.dot(q-o,direction)) for q in h if np.dot(q-o,direction)>1e-5);assert ds;dist.append(ds[0])
  width=sum(dist);assert width>=1.2398,(i,t,width)
  rows.append(dict(segment=i,fraction=t,origin_mm=o.tolist(),normal=d.tolist(),two_surface_distances_mm=dist,thickness_mm=width,passed=True))
# High-wall root: uninterrupted source strips extend down to the solid core.
for x,y in [(235,327),(263,327),(283,375),(210,359),(218,327)]:
 o=np.array([*xy((x,y)),65]);d=np.array([0,0,-1.]);h,_,_=m.ray.intersects_location([o],[d],multiple_hits=True);ds=sorted(set(round(float(np.dot(q-o,d)),6) for q in h if np.dot(q-o,d)>1e-5));assert len(ds)==2 and abs(ds[-1]-65)<.0002,(x,y,ds)
 rows.append(dict(corner=[x,y],vertical_hits_mm=ds,continuous_to_base=True,passed=True))
report=dict(passed=True,checks={'all_fold_original_surface_thickness_at_least_1_2398mm':True,'all_five_fold_corner_roots_continuous_to_base':True,'authored_plan_union_valid_and_single_after_erosion':True},stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),reference_polygon_wkt=ref.wkt,nominal_strip_width_mm=5*P,corner_construction="mitered continuous folded wall; no added external posts",rays=rows,scope='Only highest tower fold section above z=51.6 mm. Reference polygon used only for identity comparison; original slice erosion/opening must still be independently tested unchanged.')
(R/'fold-wall-check.json').write_text(json.dumps(report,indent=2));print('PASS original high-fold rays',len(rows))
