"""Independent plane/halfspace audit: every colored triangle is a complete primitive boundary."""
from pathlib import Path
import numpy as np,json,struct
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);eps=.002
# A beam is represented independently as six oriented halfspaces, one of which
# must contain the complete triangle. This excludes arbitrary interior planes.
def beam(x0,x1,y0,y1,z0,z1,slope=0):
 ns=np.array([[-1,0,0],[1,0,0],[0,-1,0],[0,1,0],[0,-slope,-1],[0,slope,1]])
 ds=np.array([-x0,x1,-y0,y1,-z0,z1]);val=t@ns.T-ds
 return np.all(val<=eps,axis=(1,2)) & np.any(np.all(abs(val)<=eps,axis=1),axis=1)
r=np.zeros(n,bool)
for cx in range(-57,58,9):r |= beam(cx-.75,cx+.75,-54,-20,80-54*4/34,81.8-54*4/34,4/34)
for cy in [-45,-36,-27]:
 z0=80-(cy+54)*4/34;r |= beam(-60,60,cy-.75,cy+.75,z0,z0+1.8)
r |= beam(-60,60,-55,-53,80,82);r |= beam(-60,60,-21,-19,76,78)
g=np.zeros(n,bool);wins={};normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
for cx in range(-31,32,9):
 for z in [43,54,65]:
  q=np.all(abs(t[:,:,1]+47.6)<eps,axis=1)&np.all((t[:,:,0]>=cx-3.6-eps)&(t[:,:,0]<=cx+3.6+eps)&(t[:,:,2]>=z-eps)&(t[:,:,2]<=z+8+eps),axis=1)&(normal[:,1]<0)
  assert q.sum()==2;wins[f'{cx},{z}']=int(q.sum());g |= q
c=np.array(json.loads((A/'face-materials.json').read_text())['face_material_indices'])
report={'faces':n,'roof_boundary_faces':int(r.sum()),'central_glazing_faces':int(g.sum()),'roof_mismatch':np.flatnonzero(r!=(c==1)).tolist(),'glass_mismatch':np.flatnonzero(g!=(c==2)).tolist(),'overlap':int((r&g).sum()),'windows':wins,'whole_triangle_halfspace_and_surface_plane':True,'neutral_faces':int((c==0).sum())}
(A/'qa/material-boundary-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
assert not report['roof_mismatch'] and not report['glass_mismatch'] and not report['overlap']
