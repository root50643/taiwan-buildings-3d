"""Original triangle opposing-coplanar positive-area overlap screening. No repair."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib,argparse
from shapely.geometry import Polygon
p=argparse.ArgumentParser();p.add_argument('--stl',default='model.stl');p.add_argument('--output',default='opposing-faces.json');a=p.parse_args();R=Path(__file__).parent;path=Path(a.stl);path=path if path.is_absolute()else R/path
m=trimesh.load(path,process=False);T=m.triangles;N=m.face_normals;tree=m.triangles_tree;bad=[];tested=0
for i,t in enumerate(T):
 ids=np.array([j for j in tree.intersection(tuple(t.min(0))+tuple(t.max(0)))if j>i],int)
 if not len(ids):continue
 ids=ids[(N[ids]@N[i])< -1+1e-9]
 for j in ids:
  d=np.max(abs((T[j]-t[0])@N[i]))
  if d>1e-6:continue
  tested+=1;axes=[k for k in range(3)if k!=np.argmax(abs(N[i]))];x=Polygon(t[:,axes]).intersection(Polygon(T[j][:,axes]));area=x.area/abs(N[i][np.argmax(abs(N[i]))])
  if area>1e-9:bad.append(dict(first_original_face=i,second_original_face=int(j),coplanarity_distance_mm=float(d),positive_overlap_area_mm2=area,first_triangle=t.tolist(),second_triangle=T[j].tolist()))
report=dict(stl_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_triangles=len(T),opposing_coplanar_candidate_pairs_tested=tested,positive_area_overlap_count=len(bad),checks={'no_opposing_coplanar_positive_area_overlap':not bad},passed=not bad,overlaps=bad,limits='Original AABB candidates; opposite-normal tolerance 1e-9, plane distance 1e-6mm, positive-area threshold 1e-9mm². This is a declared finite precision overlap screen, not an unrestricted global self-intersection theorem.')
out=Path(a.output);out=out if out.is_absolute()else R/out;out.write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='overlaps'});raise SystemExit(0 if not bad else 1)
