from pathlib import Path
import trimesh,numpy as np,json,hashlib
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);S=1.5;B=1.6;probes=[]
def add(tag,x,y,z,d,minimum):probes.append((tag,np.array([x*S,-y*S,B+z*S]),np.array([d[0],-d[1],d[2]],float),minimum))
# Coordinates here retain source y-south; saved output and normals are physical Y-north.
for x in [-41,-34,-27,-20,-13,13,20,27,34,41]:
 for z in [1.2,3,5.7]:add('front_pier_width',x-1,-25.2,z,[1,0,0],2.09)
 add('front_pier_down_root',x,-25.2,3,[0,0,-1],5.9)
for x in [-7.45,7.45]:
 for z in [2,6,10.8]:add('entry_pier_width',x-1,-27.5,z,[1,0,0],2.24)
 add('entry_down_root',x,-27.5,6,[0,0,-1],10.5)
for x in [-29,31]:
 for z in [3,11,20,32,41]:add('stair_tower_backing',x,17,z,[0,-1,0],5.5)
 add('stair_tower_down_root',x,13.8,40,[0,0,-1],61)
 for dx in [-1.7,1.7]:
  for z in [11,20,32,41]:add('stair_side_frame_backing',x+dx,17,z,[0,-1,0],5.9)
for x in [-4,13,27]:
 for z in [5.4,10.6,15.8,21,26.2,31.5,36.6]:
  yy=24-.0088*(x+5)**2
  add('south_link_into_core',x,yy-.8,z,[0,-1,0],max(1,(yy-.8-8.5)*S-.05))
for z in [24.5,27.5,31,34.5,37.5]:
 f=(z-23)/16.6;rx=10.5+5*f;ry=11+2.8*f
 for t in np.linspace(.3,np.pi-.3,13):
  x=5+(rx+.8)*np.cos(t);y=-5-(ry+.8)*np.sin(t)
  add('north_bow_backing',x,y,z,[-np.cos(t),np.sin(t),0],10)
for cx,cy,rx,ry,zs in [(7,-3.6,13.8,9.5,[40.7,42.5,44]),(10,-3.8,15.3,15.2,[45.7,47.5,49.5])]:
 for z in zs:
  for t in np.linspace(.3,np.pi-.3,13):add('upper_cap_backing',cx+(rx+.8)*np.cos(t),cy-(ry+.8)*np.sin(t),z,[-np.cos(t),np.sin(t),0],10)
for z in [8.5,13.5,18.5,23.5,29]:
 for x in [-2,4,9.5,14,18,22,26]:add('south_curve_glass_backing',x,25-.0088*(x+5)**2,z,[0,-1,0],5.2)
res=[]
for tag,o,d,minimum in probes:
 hit,idx,faces=m.ray.intersects_location([o],[d],multiple_hits=True);ds=(hit-o)@d;ii=np.argsort(ds);rows=[]
 for j in ii:
  if ds[j]<1e-7:continue
  if rows and abs(ds[j]-rows[-1]['distance_mm'])<1e-6:continue
  rows.append({'distance_mm':float(ds[j]),'point_mm':hit[j].tolist(),'face_id':int(faces[j]),'normal':m.face_normals[faces[j]].tolist(),'dot':float(d@m.face_normals[faces[j]])})
 # If probe begins inside, first hit is exit. Otherwise first pair is the material span.
 inside=bool(m.contains([o])[0]);chord=rows[0]['distance_mm'] if inside and rows else rows[1]['distance_mm']-rows[0]['distance_mm'] if len(rows)>1 else None
 res.append({'label':tag,'origin_mm':o.tolist(),'direction':d.tolist(),'origin_inside':inside,'all_hits':rows,'first_material_span_mm':chord,'source_expected_minimum_mm':minimum,'passes_expected':chord is not None and chord>=minimum})
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'sample_count':len(res),'passed':all(x['passes_expected']for x in res),'method':'Actual unprocessed STL ray, full original hit face IDs. Directed source-root and backing probes, not a whole-object minimum thickness claim. For inside probes first exit measured; outside probes first entry-exit only.','samples':res};(R/'backing-root-check.json').write_text(json.dumps(r,indent=2));print('pass',r['passed'],'failed',[(a['label'],a['origin_mm'],a['first_material_span_mm'],a['source_expected_minimum_mm'])for a in res if not a['passes_expected']])
