"""Trace original short normal rays to original faces; never changes pass flags."""
from pathlib import Path
import argparse,gzip,json,math
import numpy as np
from qa_common import load_stl,sha256,write_json


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stl',type=Path,required=True)
    p.add_argument('--short-flags',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise RuntimeError('Fresh report required')
    _,triangles,_,_=load_stl(a.stl)
    normal=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
    points=triangles.reshape(-1,3);zmin=float(points[:,2].min())
    planes=[float(np.max((points-triangle[0])@n)) for triangle,n in zip(triangles,normal)]
    globally_convex=max(planes)<=1e-7
    flags=json.load(gzip.open(a.short_flags,'rt'));rows=[];counts={}
    def kind(face):
        t=triangles[face];n=normal[face]
        if np.all(np.abs(t[:,2]-zmin)<=1e-7) and n[2]<-.999:return 'flat_bottom'
        if abs(n[2])<1e-7:return 'vertical_side'
        if n[2]>.001 and n[2]<.999:return 'outward_upward_slope'
        if n[2]>.999:return 'flat_top'
        return 'other'
    for flag in flags:
        face=flag['original_face_index'];sample=flag['sample_index'];point=np.array(flag['surface_point_mm']);direction=-normal[face]
        chord=flag['first_solid_chord_mm'];exits=flag['intersection_events'][1]['faces'];exitpoint=point+direction*chord
        entrykind=kind(face);exitkinds=sorted(set(kind(f) for f in exits));classification=entrykind+' -> '+'|'.join(exitkinds)
        counts[classification]=counts.get(classification,0)+1
        exitdetails=[]
        for exitface in exits:
            n=normal[exitface];t=triangles[exitface];denom=float(n@direction)
            analytic=float(n@(t[0]-point))/denom if abs(denom)>1e-12 else None
            bary=np.linalg.lstsq(np.column_stack([t[1]-t[0],t[2]-t[0]]),exitpoint-t[0],rcond=None)[0]
            exitdetails.append({'original_exit_face_index':exitface,'original_exit_triangle_mm':t.tolist(),
                                'exit_face_kind':kind(exitface),'analytic_line_plane_distance_mm':analytic,
                                'analytic_minus_original_chord_mm':None if analytic is None else analytic-chord,
                                'exit_point_barycentric_weights':[float(1-bary.sum()),float(bary[0]),float(bary[1])],
                                'exit_plane_residual_mm':float(n@(exitpoint-t[0]))})
        rows.append({'original_face_index':face,'sample_index':sample,
                     'original_surface_point_mm':point.tolist(),'original_outward_unit_normal':normal[face].tolist(),
                     'original_first_solid_chord_mm':chord,'derived_exit_point_mm':exitpoint.tolist(),
                     'classification':classification,'entry_height_above_flat_bottom_mm':float(point[2]-zmin),
                     'exit_height_above_flat_bottom_mm':float(exitpoint[2]-zmin),'exit_faces':exitdetails})
    report={'passed':False,'original_screen_passed':False,'purpose':'Supplement original failure locations only; no waiver or pass-state change.',
            'stl_sha256':sha256(a.stl),'original_short_flags_sha256':sha256(a.short_flags),
            'flag_count':len(flags),'classification_counts':counts,
            'all_original_vertices_in_every_outward_halfspace':globally_convex,
            'maximum_outward_halfspace_residual_mm':max(planes),
            'all_analytic_chords_match_original_within_1e_7mm':all(abs(e['analytic_minus_original_chord_mm'])<=1e-7 for r in rows for e in r['exit_faces']),
            'all_original_exit_points_on_original_triangles':all(abs(e['exit_plane_residual_mm'])<=1e-7 and min(e['exit_point_barycentric_weights'])>=-1e-7 for r in rows for e in r['exit_faces']),
            'interpretation':'Convex taper-to-bottom transitions may have arbitrarily short normal chords near a sharp eave. This finite location trace does not establish a global minimum wall width, remove thin flags, validate nozzle extrusion or prove a successful print.',
            'original_flags_with_endpoints':rows}
    write_json(a.out,report);print(json.dumps({k:v for k,v in report.items() if k!='original_flags_with_endpoints'}))


if __name__=='__main__':main()
