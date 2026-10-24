"""Exact, oriented float32 face mapping. No geometric selection or repair."""
from pathlib import Path
import hashlib,json,struct,math,csv,io
SHA='b7966d5a426accfdf6a816a3261748512f564f245a40513f2e55e22754280406'
GLOBAL='f98a2cf7cf528e147fad34c8c457cfc99f0f9b47ba5c28e7564a8a175a005f6a'
PARAM_SHA='2ea947e8240e4b3fcc7c96b2bbc34a2abf639b256145aae2c077cd78bb703a5d'
PAL_SHA='fa29e7d0c6ba5ac918d50839960cfc2d515522316e69e56e7592749e4e42feb3'
ORDER=['unknown_neutral','brick_family','roof_tile_family','parapet_green_family']
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def signature(triangle):
 v=[struct.pack('<3f',*q) for q in triangle]
 return sha(min(v[0]+v[1]+v[2],v[1]+v[2]+v[0],v[2]+v[0]+v[1]))
def digest(sigs):return sha(('\n'.join(sorted(sigs))+'\n').encode())
def read_stl(path):
 b=Path(path).read_bytes();assert sha(b)==SHA,'Original STL hash changed'
 n=struct.unpack_from('<I',b,80)[0];assert n==14042 and len(b)==702184
 tris=[tuple(struct.unpack_from('<3f',b,84+50*i+12+12*j)for j in range(3))for i in range(n)]
 sigs=[signature(t)for t in tris];assert len(set(sigs))==n and digest(sigs)==GLOBAL
 return tris,sigs

def mapping(original_sigs,triangles):
 sigs=[signature(t)for t in triangles];assert len(sigs)==14042 and len(set(sigs))==14042,'Missing or duplicate face'
 assert digest(sigs)==GLOBAL and set(sigs)==set(original_sigs),'Oriented geometry differs'
 bysig={s:i for i,s in enumerate(original_sigs)}
 return [bysig[s]for s in sigs]

def load(stl,params,palette):
 pb=Path(params).read_bytes();cb=Path(palette).read_bytes()
 assert sha(pb)==PARAM_SHA,'Pinned numeric face parameters changed'
 assert sha(cb)==PAL_SHA,'Pinned palette changed'
 p=json.loads(pb);pal=json.loads(cb);tris,sigs=read_stl(stl)
 assert p['original_stl_sha256']==SHA and p['original_whole_oriented_triangle_multiset_sha256']==GLOBAL
 materials=[0]*14042;regions=['unknown_neutral']*14042;seen=set();area=0
 spec={'left_outer_brick_wall':(205,'brick_family',0,-71,5.5,23.1),'front_wing_brick_walls':(150,'brick_family',1,-58,5.5,23.1),'front_hall_recessed_brick_wall':(93,'brick_family',1,-43.2,5.5,28.7),'hall_front_roof':(28,'roof_tile_family'),'front_parapet_infill_plane':(120,'parapet_green_family',1,-58.35,31.4,35)}
 assert set(p['regions'])==set(spec) and set(pal)==set(ORDER)
 for name,r in p['regions'].items():
  ss=spec[name];ids=r['original_face_ids'];assert len(ids)==len(set(ids))==r['count']==ss[0] and r['material_family']==ss[1]
  assert not seen.intersection(ids);seen.update(ids);assert set(r['oriented_vertex_sha256_by_face_id'])==set(map(str,ids))
  for i in ids:
   assert sigs[i]==r['oriented_vertex_sha256_by_face_id'][str(i)];t=tris[i];eps=3e-4
   if name=='hall_front_roof':assert all(abs(z-(51.5-15.5/21.65*(-(y-(-43.2-.7)/2)-.6)))<eps and -29.6-eps<=x<=29.6+eps and y<=-22.85+eps for x,y,z in t)
   else:assert all(abs(q[ss[2]]-ss[3])<eps and ss[4]-eps<=q[2]<=ss[5]+eps for q in t)
   if name=='front_parapet_infill_plane':
    for x in [-27.5,-9.1,9.1,27.5]:assert max(q[0]for q in t)<=x-1+eps or min(q[0]for q in t)>=x+1-eps
   a=[t[1][j]-t[0][j]for j in range(3)];b=[t[2][j]-t[0][j]for j in range(3)]
   cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];area+=math.sqrt(sum(x*x for x in cross))/2
   materials[i]=ORDER.index(r['material_family']);regions[i]=name
 assert len(seen)==596 and materials.count(0)==13446 and abs(area-4852.5755675797)<1e-7
 assert not seen.intersection([11498,11595,13652,13654,13659,13727,13731,13737]+p['explicit_holds']['front_gables']['original_face_ids'])
 vertices=[];faces=[];index={}
 for t in tris:
  face=[]
  for q in t:
   k=struct.pack('<3f',*q)
   if k not in index:index[k]=len(vertices);vertices.append(q)
   face.append(index[k])
  faces.append(face)
 assert mapping(sigs,[[vertices[v]for v in f]for f in faces])==list(range(14042))
 return {'triangles':tris,'signatures':sigs,'vertices':vertices,'faces':faces,'materials':materials,'regions':regions,'palette':pal,'parameters':p,'area':area}

def face_csv(D):
 s=io.StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerow(['original_stl_face_id','oriented_vertex_sha256','material_id','region'])
 for i in range(14042):w.writerow([i,D['signatures'][i],ORDER[D['materials'][i]],D['regions'][i]])
 return s.getvalue()

def srgb_linear(rgb):return tuple(x/255/12.92 if x/255<=.04045 else((x/255+.055)/1.055)**2.4 for x in rgb)
