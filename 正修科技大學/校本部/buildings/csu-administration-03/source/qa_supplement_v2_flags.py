"""Trace v2 retained flags at their original coordinates; no waiver."""
from pathlib import Path
import argparse,gzip,json,sys
import numpy as np
from shapely.geometry import Polygon,mapping
from shapely.ops import unary_union

sys.path.insert(0,str(Path(__file__).with_name('qa')))
from qa_common import load_stl,sha256,write_json
from supplement_body_flags import coplanar_line_intervals,poly_parts


def main():
    p=argparse.ArgumentParser();p.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    stl=a.package_root/'models/v2/parts/body.stl';out=a.package_root/'qa/v2/body'
    _,triangles,_,_=load_stl(stl);flagsfile=out/'manufacturing/normal-chord-flags.json.gz'
    flags=json.load(gzip.open(flagsfile,'rt'));rows=[]
    for flag in flags:
        direction=-np.array(flag['original_outward_unit_normal'])
        intervals=coplanar_line_intervals(triangles,flag['surface_point_mm'],direction)
        rows.append({'original_face_index':flag['original_face_index'],'sample_index':flag['sample_index'],
                     'original_surface_point_mm':flag['surface_point_mm'],
                     'original_outward_unit_normal':flag['original_outward_unit_normal'],
                     'original_first_solid_chord_mm':flag['first_solid_chord_mm'],'original_reasons':flag['reasons'],
                     'exact_coplanar_original_face_intervals':intervals})
    dest=out/'body-original-normal-ambiguity-review.json'
    if dest.exists():raise RuntimeError('Refuse to overwrite supplement')
    write_json(dest,{'passed':False,'original_screen_passed':False,'stl_sha256':sha256(stl),
        'original_flags_sha256':sha256(flagsfile),'supplement_source_sha256':sha256(__file__),
        'exact_interval_source_sha256':sha256(Path(__file__).with_name('qa')/'supplement_body_flags.py'),
        'flag_count':len(flags),'all_flag_rays_have_exact_coplanar_boundary_intervals':bool(rows) and all(r['exact_coplanar_original_face_intervals'] for r in rows),
        'method':'Exact Fraction clipping uses the original stored flag point and original triangles without perturbing either.',
        'interpretation':'These unchanged terrace-elevation rays lie along original boundary patches. The six numerical parity flags remain unresolved failures; this trace neither changes the pass state nor asserts global wall thickness.',
        'original_flag_locations':rows})
    source=out/'manufacturing/downward-face-flags.json.gz';down=json.load(gzip.open(source,'rt'));groups={}
    for row in down:groups.setdefault(row['original_triangle_mm'][0][2],[]).append(row)
    records=[]
    for z,items in sorted(groups.items()):
        geom=unary_union([Polygon(np.array(r['original_triangle_mm'])[:,:2]) for r in items]);polys=[]
        for poly in poly_parts(geom):
            verts=list(poly.minimum_rotated_rectangle.exterior.coords)
            widths=[float(np.linalg.norm(np.array(verts[i+1])-verts[i])) for i in range(4)]
            polys.append({'original_projection_geometry':mapping(poly),'bounds_mm':list(poly.bounds),'area_mm2':poly.area,
                          'minimum_rotated_bbox_width_mm':min(widths)})
        records.append({'z_mm':z,'original_downward_face_indices':[r['original_face_index'] for r in items],
                        'projected_components':polys})
    dest=out/'body-original-downward-flag-review.json'
    if dest.exists():raise RuntimeError('Refuse to overwrite supplement')
    write_json(dest,{'passed':False,'original_screen_passed':False,'stl_sha256':sha256(stl),
        'original_downward_flags_sha256':sha256(source),'supplement_source_sha256':sha256(__file__),
        'original_downward_triangles':len(down),
        'all_original_downward_faces_horizontal':all(len({v[2] for v in r['original_triangle_mm']})==1 for r in down),
        'largest_projected_component_minimum_bbox_width_mm':max(p['minimum_rotated_bbox_width_mm'] for r in records for p in r['projected_components']),
        'interpretation':'Horizontal downward patches of shallow solid-backed relief. Grouping at unchanged Z measures plan widths only; it does not prove a bridge span, support-free success, adhesion or a successful print. Original support flags remain failures.',
        'original_flag_elevation_groups':records})
    print(json.dumps({'normal_flags':len(flags),'exact_coplanar_flag_rays':sum(bool(r['exact_coplanar_original_face_intervals']) for r in rows),
                      'downward_triangles':len(down),'max_downward_bbox_width_mm':max(p['minimum_rotated_bbox_width_mm'] for r in records for p in r['projected_components'])}))


if __name__=='__main__':main()
