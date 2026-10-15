"""Read-only exact-original-triangle geometry helper for this fixed author evidence."""
from pathlib import Path
import json,hashlib,collections,numpy as np,trimesh
from manifold3d import Manifold,Mesh64
EXPECTED_SHA = 'f7ccaa9bbb042ec8880ad5f63faec349227a22116f6992f12c5f8bc81167c31a'

def cyclic_triangle_key(t):
    return min(tuple(map(tuple,np.roll(t,j,axis=0))) for j in range(3))

class OriginalGeometry:
    def __init__(self, model_path, expected_sha=EXPECTED_SHA):
        self.path=Path(model_path)
        self.sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()
        assert self.sha256==expected_sha, 'Unexpected STL SHA; fail closed.'
        original=trimesh.load(self.path,process=False)
        self.T=original.triangles
        self.V, inverse=np.unique(self.T.reshape(-1,3),axis=0,return_inverse=True)
        self.faces=inverse.reshape(-1,3)
        self.m=trimesh.Trimesh(self.V,self.faces,process=False)
        self.nn=self.m.face_normals; self.fa=self.m.face_adjacency
        self.ee=self.V[self.m.face_adjacency_edges]
        parents=np.arange(len(self.T))
        def root(i):
            while parents[i]!=i:
                parents[i]=parents[parents[i]]; i=parents[i]
            return int(i)
        for a,b in self.fa:
            if self.nn[a]@self.nn[b]>1-1e-8 and np.max(abs((self.T[b]-self.T[a,0])@self.nn[a]))<2e-5:
                parents[root(b)]=root(a)
        self.patch=np.array([root(i)for i in range(len(self.T))])
        self.pairs=collections.defaultdict(list)
        for i,(a,b) in enumerate(self.fa):
            x,y=int(self.patch[a]),int(self.patch[b])
            if x!=y:self.pairs[tuple(sorted([x,y]))].append(i)
        self.solid=Manifold(Mesh64(np.ascontiguousarray(self.V),np.ascontiguousarray(self.faces,dtype=np.uint64)))
        mm=self.solid.to_mesh64()
        tt=np.asarray(mm.vert_properties)[np.asarray(mm.tri_verts)][:,:,:3]
        lookup={cyclic_triangle_key(t):i for i,t in enumerate(self.T)}
        self.remap=[lookup[cyclic_triangle_key(t)] for t in tt]
        assert len(set(self.remap))==len(self.T)==len(tt)
        self.parity_directions=np.array([[.3713906763541037,.5570860145311556,.7427813527082074],[-.681123,.417119,.601003]])
        self.parity_directions/=np.linalg.norm(self.parity_directions,axis=1)[:,None]
    def cast(self,p,d):
        p=np.asarray(p);d=np.asarray(d);out=[]
        for h in sorted(self.solid.ray_cast(p.tolist(),(p+d*1000).tolist()),key=lambda h:h.distance):
            if h.distance<=1e-13:continue
            rec={'distance_mm':float(h.distance*1000),'original_face_id':int(self.remap[h.face_id]),'point_mm':list(h.position),'normal_dot_direction':float(np.array(h.normal)@d)}
            if not out or abs(rec['distance_mm']-out[-1]['distance_mm'])>1e-7:out.append(rec)
        return out
    def inside(self,p):
        return [len(self.cast(np.asarray(p),d))%2==1 for d in self.parity_directions]

def segment_distance(a,b,c,d):
    u=b-a;v=d-c;w=a-c
    def point_distance(p,a,b):
        x=b-a
        return np.linalg.norm(p-a-x*np.clip((p-a)@x/(x@x),0,1))
    ds=[point_distance(a,c,d),point_distance(b,c,d),point_distance(c,a,b),point_distance(d,a,b)]
    mat=np.array([[u@u,-u@v],[-u@v,v@v]])
    if abs(np.linalg.det(mat))>1e-18:
        t,s=np.linalg.solve(mat,[-u@w,v@w])
        if 0<=t<=1 and 0<=s<=1:ds.append(np.linalg.norm(w+t*u-s*v))
    return float(min(ds))

def output_directory(path, evidence_directory):
    out=Path(path).resolve(); evidence=Path(evidence_directory).resolve()
    assert out!=evidence and evidence not in out.parents, 'Replay outputs must not overwrite delivered evidence.'
    out.mkdir(parents=True,exist_ok=True)
    return out
