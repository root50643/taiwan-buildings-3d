"""Selected actual G-code support visibility and canopy bridge analysis.

This checks model collisions for point rays, not swept cutters or whole-support
extraction. It cannot certify physical support removal.
"""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'${PYTHON_AUDIT_DEPS}')
import numpy as np,trimesh
from shapely.geometry import LineString
from shapely.ops import unary_union

R=Path(__file__).resolve().parent;C=R.parent/'candidate'

def main():
    input_paths=R/'main_body-selected-paths.npz' if len(sys.argv)==1 else Path(sys.argv[1])
    data=np.load(input_paths);mask=np.char.startswith(data['role'],'Support')
    a=data['a'][mask]-[125,111,0];b=data['b'][mask]-[125,111,0]
    # Up to 1.0mm between tested samples, endpoints included. This does not
    # silently upgrade finite samples to an all-directions removal proof.
    points=[]
    for p,q in zip(a,b):
        steps=max(1,math.ceil(float(np.linalg.norm(q-p))/1.0))
        points.extend(p+(q-p)*t for t in np.linspace(0,1,steps+1))
    points=np.unique(np.round(points,5),axis=0)
    body=trimesh.load_mesh(C/'parts/main_body-assembly.stl',process=True)
    rays=trimesh.ray.ray_triangle.RayMeshIntersector(body)
    directions=np.array([[0,-1,0],[0,1,0],[-1,0,0],[1,0,0],[-1,-1,0],[1,-1,0],[-1,1,0],[1,1,0]],float)
    directions/=np.linalg.norm(directions,axis=1)[:,None]
    clear=[]
    for d in directions:
        blocked=rays.intersects_any(points+d*1e-5,np.tile(d,(len(points),1)))
        clear.append(~blocked)
    clear=np.array(clear).T
    no_y=~np.any(clear[:,:2],axis=1);no_8=~np.any(clear,axis=1)
    result={'scope':'Actual support positive-E XY toolpath points sampled at <=1mm spacing; model-only point-ray tests in eight horizontal directions. Other support, cutter radius, hand access and extraction deformation are not modeled. This is not a full removal or swept-tool guarantee.',
        'actual_support_segment_count':len(a),'unique_points':len(points),'tested_directions':directions.tolist(),'direct_y_exterior_clear_count':int(np.any(clear[:,:2],axis=1).sum()),'not_direct_y_count':int(no_y.sum()),'eight_direction_any_clear_count':int(np.any(clear,axis=1).sum()),'no_eight_direction_clear_count':int(no_8.sum()),'no_y_points':points[no_y].tolist(),'no_eight_direction_points':points[no_8].tolist(),
        'support_min_assembly_xyz':np.minimum(a,b).min(axis=0).tolist(),'support_max_assembly_xyz':np.maximum(a,b).max(axis=0).tolist()}
    # Inspect exact solid cross-section immediately inside previous roof layer,
    # then intersect actual bridge segments with its void. Slots close at Z1.0.
    roof=trimesh.load_mesh(C/'parts/roof-print.stl',process=True)
    path=roof.section(plane_origin=[0,0,.799],plane_normal=[0,0,1]);planar,tf=path.to_2D()
    solid=unary_union(planar.polygons_full)
    inverse=np.linalg.inv(tf)
    d=np.load(R/'roof-selected-paths.npz');idx=(d['role']=='Bridge infill')&np.isclose(d['b'][:,2],1.0)
    bridge=[]
    for p,q,ln in zip(d['a'][idx],d['b'][idx],d['line'][idx]):
        # Gcode -> print STL: min bounds (29,75) at centre (125,105).
        p=p-[29,75,0];q=q-[29,75,0]
        u=(inverse@np.r_[p,1])[:2];v=(inverse@np.r_[q,1])[:2]
        line=LineString([u,v]);void=line.difference(solid)
        pieces=list(void.geoms) if hasattr(void,'geoms') else [void]
        void_lengths=[float(s.length) for s in pieces if s.length>1e-8]
        if void_lengths:bridge.append({'gcode_line':int(ln),'start_print_xyz':p.tolist(),'end_print_xyz':q.tolist(),'unsupported_centerline_spans_mm':void_lengths})
    result['canopy_socket_bridge']={'physical_openings_count':30,'socket_design_xy_mm':[2.6,3.8],'bridge_print_z_mm':1.0,'comparison_previous_solid_section_z_mm':.799,'actual_bridge_segments_at_z':int(idx.sum()),'segments_crossing_openings':len(bridge),'maximum_unbacked_centerline_span_mm':max((max(x['unsupported_centerline_spans_mm']) for x in bridge),default=0),'segments':bridge,'note':'Point/centerline overlap with previous solid section. Bridge-infill elsewhere may be over sparse infill rather than an external void; this does not evaluate cooling, sagging or fit.'}
    output=R/'support-access-and-bridge.json' if len(sys.argv)<3 else Path(sys.argv[2])
    result['source_selected_paths_file']=input_paths.name
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('no_y_points','no_eight_direction_points','canopy_socket_bridge')},indent=2))
    print(json.dumps({k:v for k,v in result['canopy_socket_bridge'].items() if k!='segments'},indent=2))
if __name__=='__main__':main()
