"""Targeted thickness, section and support-access probes; never edits STL."""
import argparse, hashlib, io, json
from pathlib import Path
import numpy as np
import trimesh


def section_summary(section):
    if section is None: return {"exists":False,"closed_loop_count":0,"open_component_count":0,"bounds_mm":None}
    neighbors={}
    for entity in section.entities:
        points=list(entity.points)
        for a,b in zip(points[:-1],points[1:]):
            a,b=int(a),int(b)
            neighbors.setdefault(a,set()).add(b);neighbors.setdefault(b,set()).add(a)
    seen=set();closed=0;opened=0
    for first in neighbors:
        if first in seen: continue
        stack=[first];component=[]
        while stack:
            x=stack.pop()
            if x in seen: continue
            seen.add(x);component.append(x);stack.extend(neighbors[x]-seen)
        if all(len(neighbors[x])==2 for x in component):closed+=1
        else:opened+=1
    return {"exists":True,"closed_loop_count":closed,"open_component_count":opened,"bounds_mm":section.bounds.tolist(),"method":"section polyline vertex adjacency, without networkx"}


def line_intervals(mesh, origin, direction):
    origin=np.array(origin,dtype=float); direction=np.array(direction,dtype=float)
    hits, ray, face=mesh.ray.intersects_location([origin],[direction],multiple_hits=True)
    values=sorted(float(np.dot(p-origin,direction)) for p in hits)
    unique=[]
    for x in values:
        if not unique or x-unique[-1]>1e-5: unique.append(x)
    return {"origin_mm":origin.tolist(),"direction":direction.tolist(),"intersection_distances_mm":unique,"solid_intervals_mm":[[unique[i],unique[i+1]] for i in range(0,len(unique)-1,2)]}


def access_probe(mesh, start, end, radius=1.5):
    start=np.array(start,dtype=float); end=np.array(end,dtype=float)
    length=np.linalg.norm(end-start); count=int(np.ceil(length/.25))+1
    points=np.linspace(start,end,count)
    closest, distances, face=trimesh.proximity.closest_point(mesh,points)
    lower_bound=float(min(distances)-length/(count-1)/2)
    return {"start_mm":start.tolist(),"end_mm":end.tolist(),"probe_radius_mm":radius,"sample_count":count,"maximum_step_mm":float(length/(count-1)),"minimum_sampled_distance_to_mesh_mm":float(min(distances)),"continuous_clearance_lower_bound_mm":lower_bound,"collision_free_swept_probe":lower_bound>radius,"method":"nearest-triangle distances on <=0.25 mm path samples; subtract half sample step using distance Lipschitz bound"}


def main():
    p=argparse.ArgumentParser();p.add_argument('stl');p.add_argument('--out',required=True);a=p.parse_args()
    if Path(a.out).exists(): raise FileExistsError(f'Refusing to overwrite preserved report: {a.out}')
    data=Path(a.stl).read_bytes();mesh=trimesh.load_mesh(io.BytesIO(data),file_type='stl',process=True)
    tests={
        "mast_x_at_z126":([-100,41,126],[1,0,0]),
        "lower_crossarm_z_at_x24":([24,41,-1],[0,0,1]),
        "lower_crossarm_y_at_x24_z110":([24,30,110],[0,1,0]),
        "upper_crossarm_z_at_x20":([20,41,-1],[0,0,1]),
        "right_wing_z_at_x50_y44":([50,44,-1],[0,0,1]),
        "right_wing_inner_root_z_at_x40_y44":([40,44,-1],[0,0,1]),
        "right_wing_edge_x_at_z69":([45,44,69],[1,0,0]),
        "green_roof_lip_z_at_x34_5":([34.5,45,-1],[0,0,1]),
        "entry_bridge_z_at_x_minus75":([-75,-4,-1],[0,0,1]),
    }
    paths={
        "right_wing_external_support_tool_access":([48,44,60],[67,44,60]),
        "left_wing_external_support_tool_access":([-48,44,60],[-67,44,60]),
        "entry_bridge_support_tool_access":([-70,-4,12],[-70,-20,12]),
        "lower_crossarm_support_tool_access":([24,41,105],[24,55,105]),
        "between_crossarms_support_tool_access":([20,41,116],[20,55,116]),
    }
    sections={}
    for z in [20.1,44.1,62.5,65,69,80.5,110,121,126]:
        section=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        sections[str(z)]=section_summary(section)
    report={"stl_sha256":hashlib.sha256(data).hexdigest(),"stl_size_bytes":len(data),"targeted_line_intersections":{name:line_intervals(mesh,*probe) for name,probe in tests.items()},"actual_horizontal_mesh_sections":sections,"external_access_probes":{name:access_probe(mesh,*ends) for name,ends in paths.items()},"support_interpretation":"A collision-free swept 3 mm diameter probe shows nominal tool access to these open exterior regions. It does not establish the shape, adhesion or removability of real slicer-generated supports. Shallow window recesses and roof lips remain to be tuned in a slicer. No supports were generated; no slicing or test print was performed."}
    Path(a.out).write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({"out":a.out,"sha256":report['stl_sha256'],"access":{k:v['collision_free_swept_probe'] for k,v in report['external_access_probes'].items()}}))


if __name__=='__main__':main()
