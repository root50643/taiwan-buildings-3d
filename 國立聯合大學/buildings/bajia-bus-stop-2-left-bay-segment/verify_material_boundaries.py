"""All vertices, not only centroids, must lie on their intended glazing/roof surfaces."""
from pathlib import Path
import numpy as np,json,hashlib
A=Path(__file__).resolve().parent;j=json.loads((A/'mesh.json').read_text());v=np.array(j['vertices']);f=np.array(j['faces']);c=np.array(j['face_materials']);rows=[]
for i in np.flatnonzero(c==2):
 pts=v[f[i]];x=abs(pts[:,0]);assert np.ptp(x)<1e-4 and min(abs(x[0]-69.2),abs(x[0]-70.8))<1e-4
 assert pts[:,2].min()>=28-1e-4 and pts[:,2].max()<=83+1e-4
 # Real sloped upper edge from y=-22,z=83 to y=20,z=70.
 assert np.all(pts[:,2] <= 83-(pts[:,1]+22)*13/42+1e-4)
 rows.append(dict(face=int(i),x_plane=float(pts[0,0]),z_min=float(pts[:,2].min()),z_max=float(pts[:,2].max())))
assert len(rows)==8 and {round(abs(r['x_plane']),1) for r in rows}=={69.2,70.8}
for i in np.flatnonzero(c==7):
 p=v[f[i]];assert np.max(abs(p[:,2]-(94-(p[:,1]+28)*2/51)))<1e-4
report=dict(mesh_json_sha256=hashlib.sha256((A/'mesh.json').read_bytes()).hexdigest(),stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),glazing_entire_inner_and_outer_planes_verified=True,glazing_faces=rows,plain_roof_top_entire_triangle_planes_verified=True,method='Check every vertex of assigned side glazing and top triangles against actual defining planes, sloped upper pane limit, and both inner/outer thickness planes.')
(A/'qa/material-boundaries.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
