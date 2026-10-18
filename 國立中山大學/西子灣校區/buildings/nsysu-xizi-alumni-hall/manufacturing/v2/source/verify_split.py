"""Read the fixed outputs; quantify bed orientation, layer support and assembly.

This is a geometric probe. It neither invokes a slicer nor predicts adhesion,
extrusion, fit or physical print success. All geometric tolerances are reported.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon, GeometryCollection
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]

def section(mesh,z):
    path=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    result=GeometryCollection()
    if path is not None:
        for loop in path.discrete:
            polygon=Polygon(loop[:,:2])
            if not polygon.is_valid:raise RuntimeError(f'Invalid cross-section at {z}')
            result=result.symmetric_difference(polygon)
    return result

def count_polygons(g):
    if g.is_empty:return 0
    if g.geom_type=='Polygon':return 1
    return sum(count_polygons(a) for a in getattr(g,'geoms',[]))

def surface_samples(mesh):
    return np.vstack([mesh.vertices,mesh.vertices[mesh.edges_unique].mean(axis=1),mesh.triangles_center])

def sampled_surface_distance(source,target):
    points=surface_samples(source);maximum=0.
    for start in range(0,len(points),128):
        _,dist,_=trimesh.proximity.closest_point_naive(target,points[start:start+128])
        maximum=max(maximum,float(np.max(dist)))
    return {'sample_count':len(points),'maximum_sampled_point_to_triangle_distance_mm':maximum,
            'method':'all vertices, all unique edge midpoints and all triangle centroids; finite samples, not a certified Hausdorff bound'}

def support_probe(mesh):
    height=float(mesh.bounds[1,2]);rows=[]
    for layer_height in [.2,.15]:
        zs=np.arange(layer_height/2,height,layer_height)
        previous=None;flags=[]
        for z in zs:
            current=section(mesh,float(z))
            if previous is not None:
                unsupported=current.difference(previous.buffer(layer_height,join_style='mitre'))
                if unsupported.area>.01:
                    flags.append({'midpoint_z_mm':float(z),'unsupported_area_mm2':unsupported.area})
            previous=current
        rows.append({'layer_height_mm':layer_height,'first_layer_height_mm':layer_height,
                     'midpoint_count':len(zs),'overhang_angle_deg':45.,'area_flag_threshold_mm2':.01,
                     'unsupported_layers':flags})
    transitions=[];events=[]
    for z in np.unique(mesh.vertices[:,2]):
        z=float(z)
        if z<=.0001 or z>=height-.0001:continue
        before=section(mesh,z-.0001);after=section(mesh,z+.0001)
        u=after.difference(before.buffer(.0002,join_style='mitre'))
        events.append(z)
        if u.area>.01:transitions.append({'event_z_mm':z,'unsupported_area_mm2':u.area})
    near_bed=section(mesh,.0001)
    return {'support_screens':rows,'vertex_z_event_count':len(events),
            'event_probe_offset_mm':.0001,'event_reach_mm':.0002,
            'vertex_z_event_unsupported':transitions,
            'near_bed_z_mm':.0001,'near_bed_area_mm2':near_bed.area,
            'near_bed_polygon_components':count_polygons(near_bed),
            'scope':'Adjacent-section 45-degree envelope only; excludes first layer resting on bed. Not generated support or physical evidence.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'qa/design-probe')
    args=ap.parse_args()
    if args.output_dir.exists():raise SystemExit('Refusing overwrite: use a new output directory')
    args.output_dir.mkdir(parents=True)
    report=json.loads((ROOT/'models/build-report.json').read_text(encoding='utf-8'))
    original=trimesh.load_mesh(ROOT/report['reference_stl'],process=True)
    assembled=[];part_reports=[]
    for row in report['parts']:
        path=ROOT/'models'/row['stl']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['stl_sha256']
        m=trimesh.load_mesh(path,process=True)
        r={'id':row['id'],'stl_sha256':row['stl_sha256'],**support_probe(m)}
        part_reports.append(r)
        m.apply_transform(np.array(row['transform_print_to_assembled']))
        assembled.append(m)
    union=trimesh.boolean.union(assembled,engine='manifold')
    union_file=args.output_dir/'assembled-union-verification.stl'
    union_file.write_bytes(trimesh.exchange.stl.export_stl(union))
    union=trimesh.load_mesh(union_file,process=True)
    events=np.unique(np.concatenate([original.vertices[:,2],union.vertices[:,2]]))
    probes=(events[:-1]+events[1:])/2
    sections=[]
    for z in probes:
        a,b=section(original,float(z)),section(union,float(z))
        sections.append({'z_mm':float(z),'symmetric_difference_area_mm2':a.symmetric_difference(b).area,
                         'boundary_hausdorff_distance_mm':a.boundary.hausdorff_distance(b.boundary) if not(a.is_empty or b.is_empty) else None})
    out={'reference_stl_sha256':report['reference_stl_sha256'],
         'physical_part_count':len(part_reports),'parts':part_reports,
         'assembly':{'union_stl_sha256':hashlib.sha256(union_file.read_bytes()).hexdigest(),
                     'watertight':bool(union.is_watertight),'winding_consistent':bool(union.is_winding_consistent),
                     'edge_components':len(union.split(only_watertight=False)),
                     'original_bounds_mm':original.bounds.tolist(),'assembled_bounds_mm':union.bounds.tolist(),
                     'maximum_absolute_AABB_delta_mm':float(np.max(np.abs(original.bounds-union.bounds))),
                     'original_volume_mm3':float(original.volume),'assembled_union_volume_mm3':float(union.volume),
                     'assembled_union_volume_delta_mm3':float(union.volume-original.volume),
                     'original_to_assembled_surface_samples':sampled_surface_distance(original,union),
                     'assembled_to_original_surface_samples':sampled_surface_distance(union,original),
                     'midpoint_section_probe_count':len(sections),
                     'maximum_section_symmetric_difference_area_mm2':max(r['symmetric_difference_area_mm2'] for r in sections),
                     'maximum_section_boundary_hausdorff_distance_mm':max(r['boundary_hausdorff_distance_mm'] or 0 for r in sections),
                     'all_section_results':sections},
         'claim':'Geometric design probe only. Thin 0.15mm first-layer steps, bed adhesion, fit, glue, layer quantization and physical print performance remain process conditions.'}
    target=args.output_dir/'design-probe-results.json'
    target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k!='parts' and k!='assembly'}))
    print(json.dumps({k:v for k,v in out['assembly'].items() if k!='all_section_results'}))
    failures=sum(len(x['vertex_z_event_unsupported'])+sum(len(y['unsupported_layers']) for y in x['support_screens']) for x in part_reports)
    print('support_screen_flags',failures)
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
