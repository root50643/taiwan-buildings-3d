"""Review the original body flags in place; no gate outcome is changed."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse,gzip,json,math
import numpy as np
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import unary_union
from qa_common import load_stl,sha256,write_json


def vsub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def fr(v):return tuple(F.from_float(float(x)) for x in v)
def poly_parts(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for item in g.geoms for p in poly_parts(item)]


def coplanar_line_intervals(triangles,point,direction):
    point,direction=fr(point),fr(direction);rows=[]
    for face,triangle in enumerate(triangles):
        t=[fr(x) for x in triangle];n=cross(vsub(t[1],t[0]),vsub(t[2],t[0]))
        if dot(n,direction)!=0 or dot(n,vsub(point,t[0]))!=0:continue
        drop=max(range(3),key=lambda i:abs(n[i]));keep=[i for i in range(3) if i!=drop]
        project=lambda x:tuple(x[i] for i in keep)
        xy=[project(x) for x in t];p=project(point);d=project(direction)
        sign=1 if orient(*xy)>0 else -1;low=F(0);high=None;ok=True
        for i in range(3):
            a,b=xy[i],xy[(i+1)%3]
            c=sign*orient(a,b,p);s=sign*((b[0]-a[0])*d[1]-(b[1]-a[1])*d[0])
            if s==0:
                if c<0:ok=False;break
            elif s>0:low=max(low,-c/s)
            else:high=-c/s if high is None else min(high,-c/s)
        if ok and high is not None and high>low:
            rows.append({'original_face_index':face,'ray_distance_interval_mm':[float(low),float(high)],
                         'exact_fraction_interval':[str(low),str(high)],
                         'original_triangle_mm':triangle.tolist()})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stl',type=Path,required=True)
    p.add_argument('--qa-dir',type=Path,required=True);a=p.parse_args();out=a.qa_dir
    _,triangles,_,_=load_stl(a.stl);digest=sha256(a.stl)
    flags=json.load(gzip.open(out/'manufacturing/normal-chord-flags.json.gz','rt'));rows=[]
    for flag in flags:
        point=flag['surface_point_mm'];direction=-np.array(flag['original_outward_unit_normal'])
        coplanar=coplanar_line_intervals(triangles,point,direction)
        rows.append({'original_face_index':flag['original_face_index'],'sample_index':flag['sample_index'],
                     'original_surface_point_mm':point,'original_outward_unit_normal':flag['original_outward_unit_normal'],
                     'original_reasons':flag['reasons'],'original_first_solid_chord_mm':flag['first_solid_chord_mm'],
                     'exact_coplanar_original_face_intervals':coplanar,
                     'exact_coplanar_nonzero_length_interval_found':bool(coplanar)})
    write_json(out/'body-original-normal-ambiguity-review.json',{'passed':False,'original_screen_passed':False,
        'stl_sha256':digest,'original_flags_sha256':sha256(out/'manufacturing/normal-chord-flags.json.gz'),
        'flag_count':len(flags),'all_flag_rays_have_exact_coplanar_boundary_intervals':bool(rows) and all(r['exact_coplanar_nonzero_length_interval_found'] for r in rows),
        'method':'Exact Fraction arithmetic on original stored flag coordinates and original float32 triangle coordinates. Clip the original unchanged ray to every exactly coplanar original triangle.',
        'interpretation':'A ray lying along a mesh boundary has ambiguous entering/exiting parity for a numerical normal-ray checker. These remain original unresolved flags; no substitute ray or revised pass state.',
        'original_flag_locations':rows})
    sections=json.load(gzip.open(out/'sections/section-failures.json.gz','rt'));srows=[]
    for record in sections:
        original=shape(record['original_polygon']);coords=list(original.exterior.coords)
        box=original.minimum_rotated_rectangle;boxcoords=list(box.exterior.coords)
        dims=sorted(math.dist(boxcoords[i],boxcoords[i+1]) for i in range(4))[::2]
        srows.append({'layer_id':record['layer_id'],'z_mm':record['z_mm'],'original_polygon_index':record['original_polygon_index'],
                      'original_polygon':record['original_polygon'],'original_bounds_mm':record['bounds_mm'],
                      'rectangle_extents_mm':dims,'is_rectangle_to_1e_8mm2':original.symmetric_difference(box).area<1e-8,
                      'original_opening_loss_fraction':record['opening_loss_fraction'],
                      'original_loss_outside_vertex_disks_mm2':record['loss_outside_0p41_vertex_disks_mm2'],
                      'original_checks':record['checks']})
    write_json(out/'body-original-section-flag-review.json',{'passed':False,'original_screen_passed':False,
        'stl_sha256':digest,'original_failures_sha256':sha256(out/'sections/section-failures.json.gz'),
        'failed_original_polygons':len(sections),'all_flagged_sections_survive_without_core_splitting':all(r['original_checks']['survives_erosion'] and r['original_checks']['no_split_after_erosion'] for r in srows),
        'all_reported_losses_inside_original_vertex_disks':all(r['original_loss_outside_vertex_disks_mm2']<=1e-10 for r in srows),
        'interpretation':'Round-corner opening removes corners of approximately0.8x1.8mm rectangular pier sections. They survive erosion, but their core is close to the threshold and the original1%loss gate remains false. No strength or successful-print guarantee.',
        'original_flag_locations':srows})
    downward=json.load(gzip.open(out/'manufacturing/downward-face-flags.json.gz','rt'));groups={}
    for record in downward:
        verts=record['original_triangle_mm'];z=verts[0][2]
        groups.setdefault(z,[]).append(record)
    srows=[]
    for z,records in sorted(groups.items()):
        geom=unary_union([Polygon(np.array(r['original_triangle_mm'])[:,:2]) for r in records])
        prows=[]
        for poly in poly_parts(geom):
            box=list(poly.minimum_rotated_rectangle.exterior.coords)
            widths=sorted(math.dist(box[i],box[i+1]) for i in range(4))[::2]
            prows.append({'original_projection_geometry':mapping(poly),'bounds_mm':list(poly.bounds),
                          'minimum_rotated_bbox_width_mm':min(widths),'area_mm2':poly.area})
        srows.append({'z_mm':z,'original_downward_face_indices':[r['original_face_index'] for r in records],
                      'projected_components':prows})
    write_json(out/'body-original-downward-flag-review.json',{'passed':False,'original_screen_passed':False,
        'stl_sha256':digest,'original_downward_flags_sha256':sha256(out/'manufacturing/downward-face-flags.json.gz'),
        'original_downward_triangles':len(downward),'all_original_downward_faces_horizontal':all(len({v[2] for v in r['original_triangle_mm']})==1 for r in downward),
        'largest_projected_component_minimum_bbox_width_mm':max(p['minimum_rotated_bbox_width_mm'] for r in srows for p in r['projected_components']),
        'interpretation':'Original horizontal downward patches grouped by unchanged Z and unioned only for plan-width measurement. Bbox widths are not a bridge-span certificate. Geometric overhang flags remain failed despite deliberately support-disabled slicing.',
        'original_flag_elevation_groups':srows})
    print(json.dumps({'normal_flags':len(flags),'exact_coplanar_flag_rays':sum(r['exact_coplanar_nonzero_length_interval_found'] for r in rows),
                      'section_flags':len(sections),'downward_triangles':len(downward),
                      'max_downward_bbox_width_mm':max(p['minimum_rotated_bbox_width_mm'] for r in srows for p in r['projected_components'])}))


if __name__=='__main__':main()
