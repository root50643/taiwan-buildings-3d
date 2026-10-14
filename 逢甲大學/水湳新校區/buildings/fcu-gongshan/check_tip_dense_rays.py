from pathlib import Path
import trimesh,numpy as np,json,hashlib
from shapely.geometry import Point,Polygon
P=Path(__file__).parent;F=P/'model.stl';m=trimesh.load(F,process=False)
c=np.array([2.65,-60.55]);poly=Polygon([c+.8*np.array([np.cos(a),np.sin(a)])for a in np.linspace(0,2*np.pi,48,endpoint=False)])
xy=[(x,y)for x in np.arange(1.85,3.451,.025)for y in np.arange(-61.35,-59.749,.025)if poly.contains(Point(x,y))]
verts=np.array(poly.exterior.coords[:-1]);xy.extend([tuple(c+(q-c)*.999875)for q in verts]);xy.extend([tuple(c+((a+b)/2-c)*.999875)for a,b in zip(verts,np.roll(verts,-1,axis=0))])
rows=[]
for x,y in xy:
 hit,_,face=m.ray.intersects_location([[x,y,22]],[[0,0,-1]],multiple_hits=True);i=np.argmax(hit[:,2]);q=hit[i];fi=int(face[i]);n=m.face_normals[fi];o=q+n*.01
 p,_,faces=m.ray.intersects_location([o],[-n],multiple_hits=True);ds=sorted(set(round(float(np.dot(v-o,-n)),8)for v in p if np.dot(v-o,-n)>0))
 rows.append(dict(x=x,y=y,original_top_face=fi,normal=n.tolist(),all_hits_mm=ds,first_solid_normal_chord_mm=ds[1]-ds[0]))
small=min(rows,key=lambda x:x['first_solid_normal_chord_mm']);result=dict(stl_sha256=hashlib.sha256(F.read_bytes()).hexdigest(),scope='Complete rounded-cap footprint sampled on 0.025mm XY grid plus every 48-gon vertex and edge midpoint shifted 0.0001mm inward. Original STL triangles and local normals. The construction is a constant normal-swept slab; adjacent unmodified sharp roof edges are outside this designated cap proof. No claim of mathematical continuous/exhaustive whole-model minimum thickness.',sample_count=len(rows),minimum_sample=small,all_samples_ge_1p5mm=all(r['first_solid_normal_chord_mm']>=1.5 for r in rows),samples=rows)
result['reference_width_mm']=.8;result['checks']={'all_designated_chords_ge_reference_0p8mm':all(r['first_solid_normal_chord_mm']>=.8 for r in rows)};result['passed']=all(result['checks'].values())
(P/'tip-dense-rays.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items()if k!='samples'});assert result['checks']['all_designated_chords_ge_reference_0p8mm']
