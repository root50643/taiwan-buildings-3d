from pathlib import Path
import numpy as np,json,hashlib,math,collections,time
from fractions import Fraction as F
from config import *
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
raw=S.read_bytes();T=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype(float)
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def det(a,b):return a[0]*b[1]-a[1]*b[0]
def clip(subject,clipper):
 orient=1 if det(sub(clipper[1],clipper[0]),sub(clipper[2],clipper[0]))>0 else-1;out=list(subject)
 for a,b in zip(clipper,clipper[1:]+clipper[:1]):
  inp=out;out=[]
  if not inp:break
  prev=inp[-1];dp=orient*det(sub(b,a),sub(prev,a))
  for cur in inp:
   dc=orient*det(sub(b,a),sub(cur,a))
   if (dc>=0)!=(dp>=0):out.append([x+(y-x)*dp/(dp-dc)for x,y in zip(prev,cur)])
   if dc>=0:out.append(cur)
   prev=cur;dp=dc
 return out
start=time.time();groups={};tri=[];planes=[]
for fi,t in enumerate(T):
 a,b,c=[[F(float(x))for x in v]for v in t];n=cross(sub(b,a),sub(c,a));assert any(n);coef=n+[-dot(n,a)];den=math.lcm(*(x.denominator for x in coef));ints=[int(x*den)for x in coef];gcd=math.gcd(*ints);ints=[x//gcd for x in ints]
 orientation=-1 if next(x for x in ints if x)<0 else 1;key=tuple(x*orientation for x in ints);groups.setdefault(key,{1:[],-1:[]})[orientation].append(fi);tri.append([a,b,c]);planes.append(key)
lo=T.min(1);hi=T.max(1);opposite_coplanar_pairs=0;opposite_aabb_pairs=0;records=[];overlaps=[];separated=[]
for key,orient in groups.items():
 opposite_coplanar_pairs+=len(orient[1])*len(orient[-1])
 for i in orient[1]:
  for j in orient[-1]:
   if not(np.all(hi[i]>=lo[j])and np.all(hi[j]>=lo[i])):
    separated.append(dict(faces=[i,j],exact_plane=list(map(str,key)),separating_axes=[k for k in range(3)if hi[i,k]<lo[j,k]or hi[j,k]<lo[i,k]],first_original_aabb_mm=[lo[i].tolist(),hi[i].tolist()],second_original_aabb_mm=[lo[j].tolist(),hi[j].tolist()]));continue
   opposite_aabb_pairs+=1;ax=max(range(3),key=lambda k:abs(key[k]));axes=[k for k in range(3)if k!=ax];a=[[v[k]for k in axes]for v in tri[i]];b=[[v[k]for k in axes]for v in tri[j]];poly=clip(a,b);area=abs(sum(det(poly[k],poly[(k+1)%len(poly)])for k in range(len(poly))))/2 if len(poly)>2 else F(0);row=dict(faces=[i,j],exact_plane=list(map(str,key)),projected_axis=ax,exact_projected_area_mm2=str(area),positive_area=area>0,exact_intersection_vertices_projected_mm=[[str(x)for x in v]for v in poly]);records.append(row)
   if area>0:overlaps.append(row)
summary=dict(stl_sha256=H,original_faces=len(T),exact_plane_groups=len(groups),exact_plane_groups_with_both_windings=sum(bool(q[1])and bool(q[-1])for q in groups.values()),exact_opposing_coplanar_face_pairs=opposite_coplanar_pairs,exact_opposing_coplanar_aabb_face_pairs=opposite_aabb_pairs,exact_positive_area_opposing_overlap_count=len(overlaps),method='Exhaustive exact-rational plane grouping of every original float32 STL triangle. Triangle cross product and plane constant converted to primitive integer coefficient tuple with canonical sign; original cross-product sign retains triangle winding. All opposite-winding pairs on identical planes are checked for original AABB intersection. Any candidate is clipped in dominant-axis projection with exact Fraction Sutherland-Hodgman; exact projected signed polygon area determines positive area, without epsilon. Nothing is repaired, welded, merged, rounded, simplified, or removed.',limits='Exact for opposing coplanar positive-area triangle overlaps in the supplied binary STL coordinates only. This is not a test of every noncoplanar self-intersection, continuous thickness, manifoldness or printability; no exception approval.',source_sha_unchanged=hashlib.sha256(S.read_bytes()).hexdigest()==H,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.time()-start)
Path(W/'ntou-revision-boundary-opposing-exact.json').write_text(json.dumps(dict(summary=summary,candidates=records,overlaps=overlaps,exact_disjoint_opposite_coplanar_pairs=separated),indent=2));print(json.dumps(summary,indent=2))
