"""Strict original STL records, exact ordered float32 corners and bounded face materials."""
from pathlib import Path
import hashlib,json,struct,math,csv,io,sys
if sys.flags.optimize:raise RuntimeError("Optimization disables validation assertions; run without -O")
SHA='d79ad8b995cfafb3c89d01d6a8f7401f3e068c8d7193ce3ac83e64ff0f132f2a'
GLOBAL='750baef9a3dbe4e680bfedfe261342ec7421f39d268227e6d88e4721fdc8cd3d'
ORDERED_SIGNATURES='363f094f2c8bc2fa03ae12655911361b5440b49f0d3d60f4155bdc0e8237026b'
STREAM='adce637da89ba30ea57d9322f4c7825d35da4f485de4ba1706820917c40fa54f'
PARAM_SHA='daa61ad9b42fb96a487d04490df2e7ad48de793cd285aa568ce6a8d3fb4ed56b'
PAL_SHA='4663a762d4d1a7fc9d6df97c8cf89a06f199d138ee316d4dcb7fc08de77603a4'
N=30648
ORDER=['unknown_neutral','roof_pale_yellow_green','white_rim_family','front_glazing_family']
def need(ok,message):
 if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def signature(triangle):
 v=[struct.pack('<3f',*q) for q in triangle]
 return sha(min(v[0]+v[1]+v[2],v[1]+v[2]+v[0],v[2]+v[0]+v[1]))
def digest(sigs):return sha(('\n'.join(sorted(sigs))+'\n').encode())
def vertex_stream(triangles):return b''.join(struct.pack('<3f',*q)for t in triangles for q in t)
def mapping(original_sigs,triangles):
 need(len(triangles)==N and all(len(t)==3 for t in triangles),'Triangle count changed')
 sigs=[signature(t)for t in triangles]
 need(len(set(sigs))==N and digest(sigs)==GLOBAL,'Missing, duplicate or changed oriented original triangle')
 need(sigs==original_sigs and sha(('\n'.join(sigs)+'\n').encode())==ORDERED_SIGNATURES,'Original face order changed')
 need(sha(vertex_stream(triangles))==STREAM,'Exact float32 coordinates or original corner order changed')
 return list(range(N))
def read_stl(path):
 b=Path(path).read_bytes();need(sha(b)==SHA,'Original STL hash changed')
 need(len(b)==1532484 and struct.unpack_from('<I',b,80)[0]==N,'Original STL size/count changed')
 tris=[tuple(struct.unpack_from('<3f',b,84+50*i+12+12*j)for j in range(3))for i in range(N)]
 need(all(struct.unpack_from('<H',b,84+50*i+48)[0]==0 for i in range(N)),'Unexpected STL attribute')
 sigs=[signature(t)for t in tris];mapping(sigs,tris);return tris,sigs

def load(stl,params,palette):
 pb=Path(params).read_bytes();cb=Path(palette).read_bytes()
 need(sha(pb)==PARAM_SHA,'Pinned numeric face parameters changed');need(sha(cb)==PAL_SHA,'Pinned fixed palette changed')
 p=json.loads(pb);pal=json.loads(cb);tris,sigs=read_stl(stl)
 need(p['original_stl_sha256']==SHA and p['original_whole_oriented_triangle_multiset_sha256']==GLOBAL and p['original_ordered_triangle_vertex_stream_sha256']==STREAM,'Geometry contract mismatch')
 need(set(pal)==set(ORDER),'Extra or missing material');eps=p['predicate_epsilon_mm'];need(eps==1e-4,'Changed boundary tolerance')
 expected={k:[]for k in ['main_dome','horizontal_roof_rim_lip','observed_front_glazing']};areas=[];above=0.;rear=[];podium=[];cross_roof=cross_glass=0
 for i,t in enumerate(tris):
  z=[q[2]for q in t];y=[q[1]for q in t];r=[math.hypot(q[0],q[1])for q in t]
  roof=min(z)>=37.9-eps and max(z)>37.9+eps;lip=all(abs(q-37.9)<eps for q in z);glass=all(abs(q-60.8)<eps for q in r)and min(z)>=10-eps and max(z)<=33.7+eps
  front=glass and max(y)<=eps;back=glass and min(y)>=-eps
  for k,yes in zip(expected,[roof,lip,front]):
   if yes:expected[k].append(i)
  if back:rear.append(i)
  if all(abs(q-10)<eps for q in z):podium.append(i)
  cross_roof+=int(min(z)<37.9-eps and max(z)>37.9+eps);cross_glass+=int(glass and not front and not back)
  a=[t[1][j]-t[0][j]for j in range(3)];b=[t[2][j]-t[0][j]for j in range(3)];x=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];area=math.sqrt(sum(q*q for q in x))/2;areas.append(area)
  if max(z)>3+eps:above+=area
 materials=[0]*N;regions=['unknown_neutral']*N;seen=set();area=0.
 spec={'main_dome':(22518,'roof_pale_yellow_green'),'horizontal_roof_rim_lip':(384,'white_rim_family'),'observed_front_glazing':(960,'front_glazing_family')}
 need(set(p['regions'])==set(spec),'Extra or missing region')
 for k,(count,material)in spec.items():
  rr=p['regions'][k];ids=rr['original_face_ids'];need(ids==expected[k] and len(ids)==rr['count']==count and rr['material_family']==material,k+': exact face list mismatch')
  need(not seen.intersection(ids),k+': overlapping regions');seen.update(ids)
  need(rr['oriented_vertex_sha256_by_face_id']=={str(i):sigs[i]for i in ids},k+': fingerprint mismatch')
  ar=sum(areas[i]for i in ids);need(abs(ar-rr['area_mm2'])<1e-7,k+': area mismatch');area+=ar
  for i in ids:materials[i]=ORDER.index(material);regions[i]=k
 need(len(seen)==23862 and materials.count(0)==6786 and p['neutral_original_face_ids']==[i for i in range(N)if i not in seen],'Neutral complement changed')
 need(len(rear)==208 and len(podium)==872 and not seen.intersection(rear+podium),'Unverified rear or podium colored')
 need(cross_roof==cross_glass==0,'Boundary-crossing face')
 need(abs(area-p['approved_area_mm2'])<1e-7 and abs(above-p['above_base_area_mm2'])<1e-7,'Area changed')
 vertices=[];faces=[];index={}
 for t in tris:
  f=[]
  for q in t:
   k=struct.pack('<3f',*q)
   if k not in index:index[k]=len(vertices);vertices.append(q)
   f.append(index[k])
  faces.append(f)
 mapping(sigs,[[vertices[v]for v in f]for f in faces])
 return {'triangles':tris,'signatures':sigs,'vertices':vertices,'faces':faces,'materials':materials,'regions':regions,'palette':pal,'parameters':p,'area':area}

def face_csv(D):
 s=io.StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerow(['original_stl_face_id','oriented_vertex_sha256','material_id','region'])
 for i in range(N):w.writerow([i,D['signatures'][i],ORDER[D['materials'][i]],D['regions'][i]])
 return s.getvalue()
def srgb_linear(rgb):return tuple(x/255/12.92 if x/255<=.04045 else((x/255+.055)/1.055)**2.4 for x in rgb)
