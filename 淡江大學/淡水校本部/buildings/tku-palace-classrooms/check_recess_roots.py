"""Read-only feature/root rays on original binary STL, process=False; no repair."""
from pathlib import Path
import ast,json,hashlib,math
import numpy as np
import trimesh
R=Path(__file__).resolve().parent; raw=(R/'model.stl').read_bytes(); m=trimesh.load(R/'model.stl',process=False);rows=[]
a=ast.parse((R/'build_model.py').read_text());buildings=next(ast.literal_eval(n.value) for n in a.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BUILDINGS' for t in n.targets))
def transform(b,p,d=False):
 t=math.radians(b['angle_deg']);x,y,z=p;q=np.array([x*math.cos(t)-y*math.sin(t),x*math.sin(t)+y*math.cos(t),z]);return q if d else q+[*b['model_center_mm'],0]
def hits(p,d):
 h,_,_=m.ray.intersects_location([p],[d],multiple_hits=True);return sorted(set(round(float(np.dot(v-p,d)),5) for v in h if np.dot(v-p,d)>1e-5))
def record(name,b,p,d,test,**extra):
 o=transform(b,p);v=transform(b,d,True);h=hits(o,v);ok=bool(test(h));rows.append(dict(name=b['id']+'_'+name,origin_mm=o.tolist(),direction=v.tolist(),intersections_mm=h,passed=ok,**extra));assert ok,(name,b['id'],h)
for b in buildings:
 L,W=b['roof_mm'];wl=L-3;ww=W-2;f=b['front_sign'];floor=[1.7,2.55,3.6,4.6][b['level']]+.55;E=floor+3.6
 for i,x in enumerate(np.linspace(-wl/2+.55,wl/2-.55,10)):
  record(f'porch_column_{i}_continuous_base_roof',b,(float(x),f*ww/2,30),(0,0,-1),lambda h:len(h)==2 and abs(h[-1]-30)<1e-4,diameter_mm=1.1)
 if b['cross_gable']:
  for x in [-1.95,1.95]:record('cross_gable_post_'+str(x),b,(x,f*(W/2+.2),30),(0,0,-1),lambda h:len(h)==2 and abs(h[-1]-30)<1e-4,diameter_mm=1.1)
 record('porch_end_wall_thickness',b,(-30,f*(ww/2-1.4),floor+1.3),(1,0,0),lambda h:len([v for v in h if 30-L/2<v<30+L/2])==4 and all(abs(v-1.2)<1e-4 for v in np.diff([v for v in h if 30-L/2<v<30+L/2])[::2]),minimum_end_wall_mm=1.2)
 record('front_open_porch_and_recessed_door',b,(0,f*(ww/2+2),floor+1.3),(0,-f,0),lambda h:abs(h[0]-4.35)<1e-4,expected_first_mm=4.35)
 record('rear_recessed_window',b,(0,-f*(ww/2+2),floor+1.3),(0,f,0),lambda h:abs(h[0]-2.4)<1e-4,expected_first_mm=2.4)
 record('upper_gable_vent_side_roots',b,(-L/2+2.15,-20,E+1.74),(0,1,0),lambda h:len([v for v in h if v<40])==4 and min(h[1]-h[0],h[3]-h[2])>=.95,minimum_side_root_mm=.95)
 record('finite_ridge_width',b,(0,-20,E+2.64),(0,1,0),lambda h:len(h)>=2 and h[1]-h[0]>=.999,minimum_width_mm=1.0)
 for x in [-L/2+.2,L/2-.2]:
  record('eave_corner_finite_root_'+str(x),b,(x,-W/2+.2,30),(0,0,-1),lambda h:len(h)>=2 and h[1]-h[0]>.8,minimum_roof_thickness_mm=.8)
# Exposed avenue and transverse gaps: original top hit must remain ground-level.
for x,y in [(-35,0),(0,1.5),(35,2.3),(-9,0),(.2,18),(35.2,18),(-34.8,-15),(.2,-15),(35.2,-15)]:
 h=hits(np.array([x,y,30]),np.array([0,0,-1]));ok=len(h)==2 and 30-h[0]<5.3;rows.append(dict(name=f'open_route_{x}_{y}',origin_mm=[x,y,30],direction=[0,0,-1],intersections_mm=h,passed=ok));assert ok,(x,y,h)
assert (R/'model.stl').read_bytes()==raw
j=dict(passed=True,checks={r['name']:r['passed'] for r in rows},stl_sha256=hashlib.sha256(raw).hexdigest(),method='Original STL process=False; sampled exact ray tests of all 74 columns, front and rear recesses, finite ridges/eaves and open paths. No repair; no universal printability claim.',rays=rows)
(R/'recess-root-check.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print('PASS',len(rows),'rays')
