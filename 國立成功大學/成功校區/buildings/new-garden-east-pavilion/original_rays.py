"""Original-triangle Moller-Trumbore rays with R-tree candidate bounds.
No repair or face filtering. Avoids the barycentric dot-product cancellation on very skinny original triangles.
Direction must be normalized. Finite ray extent is set from original mesh bounds; all original positive hits retained.
"""

import sys
sys.dont_write_bytecode=True

def require(value,message):
 if not bool(value):raise RuntimeError(message)
import numpy as np
class OriginalRays:
 def __init__(self,mesh):
  self.tri=np.asarray(mesh.triangles,dtype=np.float64);self.tree=mesh.triangles_tree
  self.e1=self.tri[:,1]-self.tri[:,0];self.e2=self.tri[:,2]-self.tri[:,0]
  self.lo=mesh.bounds[0];self.hi=mesh.bounds[1];self.reach=float(np.linalg.norm(mesh.extents)*4+10)
 def hits(self,origin,direction):
  o=np.asarray(origin,float);d=np.asarray(direction,float);require((abs(np.linalg.norm(d)-1)<1e-7), ('Required check failed'))
  end=o+d*self.reach;lo=np.maximum(np.minimum(o,end)-1e-7,self.lo-1e-7);hi=np.minimum(np.maximum(o,end)+1e-7,self.hi+1e-7)
  if np.any(lo>hi):return []
  ix=np.array(list(self.tree.intersection(tuple(lo)+tuple(hi))),dtype=int)
  if not len(ix):return []
  e1=self.e1[ix];e2=self.e2[ix];p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p)
  # The determinant threshold scales with original triangle area, retaining skinny nonzero faces.
  scale=np.linalg.norm(np.cross(e1,e2),axis=1);ok=np.abs(det)>scale*1e-12
  ix=ix[ok];e1=e1[ok];e2=e2[ok];p=p[ok];det=det[ok]
  if not len(ix):return []
  tv=o-self.tri[ix,0];u=np.einsum('ij,ij->i',tv,p)/det;q=np.cross(tv,e1);v=q@d/det;t=np.einsum('ij,ij->i',e2,q)/det
  ok=(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=0)&(t<=self.reach)
  raw=sorted((float(tt),int(ii))for tt,ii in zip(t[ok],ix[ok]));out=[]
  for x in raw:
   if not out or abs(x[0]-out[-1][0])>1e-7:out.append(x)
  return out
