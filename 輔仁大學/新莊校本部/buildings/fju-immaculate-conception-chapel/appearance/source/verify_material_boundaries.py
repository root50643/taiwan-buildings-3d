from pathlib import Path
import struct,json,math
p=Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];r=[];eps=.0002
for name,y,xr,zr in [('left_front_pier',-43,[-31.5,-24.5],[3,50]),('right_front_pier',-43,[24.5,31.5],[3,50])]+[(f'cap_{x}',-42.5,[x-3.5,x+3.5],[48,52])for x in [-25,-16,16,25]]:
 ids=[];area=0
 for i in range(n):
  q=struct.unpack_from('<12fH',b,84+i*50);v=[q[3+j*3:6+j*3]for j in range(3)]
  if all(abs(vv[1]-y)<eps and xr[0]-eps<=vv[0]<=xr[1]+eps and zr[0]-eps<=vv[2]<=zr[1]+eps for vv in v):
   ids.append(i);area+=abs((v[1][0]-v[0][0])*(v[2][2]-v[0][2])-(v[2][0]-v[0][0])*(v[1][2]-v[0][2]))/2
 r.append(dict(name=name,y=y,x=xr,z=zr,ids=ids,count=len(ids),area_mm2=area))
for g in r:
 g['triangles']=[{'index':i,'vertices':[struct.unpack_from('<12fH',b,84+i*50)[3+j*3:6+j*3]for j in range(3)]}for i in g['ids']]
m=json.loads((p/'face-materials.json').read_text())['face_material_indices']
ids=[i for g in r for i in g['ids']]
assert len(ids)==len(set(ids))==16 and set(ids)=={i for i,c in enumerate(m) if c==1}
assert n==1678 and abs(sum(g['area_mm2'] for g in r)-702.20000267)<.00001
(p/'qa/material-boundaries.json').write_text(json.dumps({'groups':r,'face_count':n,'colored_faces':16,'neutral_faces':1662,'total_area_mm2':sum(g['area_mm2']for g in r),'all_vertex_plane_and_finite_domain':True,'epsilon_mm':eps,'no_subdivision':True},indent=2)+'\n')
