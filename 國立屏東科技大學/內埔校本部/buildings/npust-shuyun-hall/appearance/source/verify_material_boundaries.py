from pathlib import Path
import struct,json
p=Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];eps=.0002;out=[]
# Complete front upper red band (18 panels) and white bands, independently supported by the fully received historical official photo; all 3 vertices exact plane.
regions=[('upper_front_red',-66.2,[-50*.88,50*.88],[32.3*.88,39*.88]),('white_lintel_front',-67.4,[-50.5*.88,50.5*.88],[29*.88,32.3*.88]),('white_parapet_front',-67.4,[-50.5*.88,50.5*.88],[39*.88,42.2*.88])]
regions += [(f'lower_red_{x}',-64.7,[(x-4)*.88,(x+4)*.88],[19*.88,26.5*.88])for x in [-41.5,-30.5,-19.5,19.5,30.5,41.5]]
for name,y,xr,zr in regions:
 ids=[];tris=[];area=0
 for i in range(n):
  q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
  if all(abs(yy-y)<eps and xr[0]-eps<=x<=xr[1]+eps and zr[0]-eps<=z<=zr[1]+eps for x,yy,z in v):
   ids.append(i);tris.append({'id':i,'vertices':v});area+=abs((v[1][0]-v[0][0])*(v[2][2]-v[0][2])-(v[2][0]-v[0][0])*(v[1][2]-v[0][2]))/2
 out.append(dict(name=name,y=y,x=xr,z=zr,ids=ids,count=len(ids),area_mm2=area,triangles=tris))
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];ids=[i for g in out for i in g['ids']]
assert n==3120 and len(ids)==len(set(ids))==94 and set(ids)=={i for i,c in enumerate(m) if c}
assert all(m[i]==(2 if 'white' in g['name'] else 1) for g in out for i in g['ids'])
assert abs(sum(g['area_mm2'] for g in out)-1232.14024)<.001
r=dict(original_faces=n,regions=out,colored_faces=94,neutral_faces=3026,area_mm2=sum(g['area_mm2']for g in out),all_three_vertices_finite_plane_checked=True,no_subdivision=True,epsilon_mm=eps)
(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n')
