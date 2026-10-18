"""Preserve original 580 finite-ray flags; test a piecewise open route only."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'${PYTHON_AUDIT_DEPS}')
import numpy as np,trimesh
R=Path(__file__).resolve().parent
input_report=R/'support-access-and-bridge.json' if len(sys.argv)==1 else Path(sys.argv[1])
d=json.loads(input_report.read_text());p=np.array(d['no_eight_direction_points'])
mesh=trimesh.load_mesh(R.parent/'candidate/parts/main_body-assembly.stl',process=True)
ray=trimesh.ray.ray_triangle.RayMeshIntersector(mesh)
def collision(a,b):
    delta=b-a;l=np.linalg.norm(delta,axis=1);directions=delta/l[:,None]
    loc,ix,tri=ray.intersects_location(a+directions*1e-5,directions,multiple_hits=True)
    fail=np.zeros(len(a),bool)
    if len(ix):
        dist=np.linalg.norm(loc-a[ix],axis=1);use=dist<l[ix]-1e-5
        fail[ix[use]]=True
    return fail
a=p.copy();b=p.copy();b[:,1]=-33
c=b.copy();c[:,0]=np.where(p[:,0]<0,-65,65)
end=c.copy();end[:,1]=-60
legs=[(a,b),(b,c),(c,end)]
blocked=[collision(x,y) for x,y in legs]
inside=mesh.contains(p)
# Shaft corridor samples at z=8.0, y=-33, x=+/-31..65. Orthogonal
# cross-section offsets define a 1.0mm diameter shaft envelope locally.
offsets=np.array([[0,.5*math.cos(t),.5*math.sin(t)] for t in np.linspace(0,2*math.pi,65)])
radius_leg=[]
for sign in [-1,1]:
    origins=np.array([sign*31,-33,8.])+offsets;ends=np.array([sign*65,-33,8.])+offsets
    radius_leg.append({'side':sign,'offset_rays':len(offsets),'radius_mm':.5,'blocked_rays':int(collision(origins,ends).sum())})
out={'original_eight_horizontal_ray_no_clear_count':len(p),'original_flags_preserved':True,'flagged_bbox_mm':[p.min(0).tolist(),p.max(0).tolist()],
     'flagged_sample_points_inside_body_count':int(inside.sum()),'point_route_legs':'Each original point -> same X/Z,Y=-33 -> X=sign*65 -> Y=-60. Geometry-only finite line segments; no support mass, cutter shape or force modeling.',
     'blocked_point_routes_by_leg':[int(x.sum()) for x in blocked],'all_flagged_point_routes_clear':not np.any(blocked),'point_route_example':[a[0].tolist(),b[0].tolist(),c[0].tolist(),end[0].tolist()],
     'shaft_corridor_limited_radius_checks':radius_leg,'known_corridor_between_wall_and_stairs_mm':4.5,'known_corridor_vertical_from_base_to_balcony_mm':9.4,
     'required_operation':'Do not pull these shallow-window supports as one block straight forward. Remove canopy/columns are not assembled yet. Fragment and peel the support from the side of the open 4.5mm corridor using a slender angled pick/fine cutter; a tip must turn into the approximately 1.2mm-deep exterior window relief. The shaft sample does not validate that full bent tool or a gripped support chunk can turn. If physical access/adhesion prevents clean fragmentation, revise support placement/profile or use a compatible soluble-support process, re-slice and inspect.',
     'limitations':['Finite centerline routes and 65 radial shaft rays are evidence of open exterior space, not a continuous swept-tool proof.','No physical print/support removal, fit, adhesive strength or acceptable surface damage test.','Supports themselves may obstruct the corridor and must be fragmented progressively; no whole-block extraction claim.']}
output=R/'support-route-followup.json' if len(sys.argv)<3 else Path(sys.argv[2])
out['source_report']=input_report.name
output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
