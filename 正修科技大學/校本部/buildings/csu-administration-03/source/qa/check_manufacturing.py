"""Unmodified STL normal chords, downward faces and finite layer support.

Original triangle IDs and coordinates are retained. No repair, rounding, flag
waiver or model-specific exception exists. These are finite numerical screens,
not a global minimum-thickness or physical print certificate.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, math
import numpy as np
from shapely.geometry import MultiPolygon, mapping
from check_sections import original_section
from qa_common import load_stl, write_json, write_gzip_json, sha256, checker_inventory

WEIGHTS = np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],
                    [.495,.495,.01],[.01,.495,.495],[.495,.01,.495],
                    [.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])


def normal_chords(triangles, normals, out, width):
    edge1=triangles[:,1]-triangles[:,0]; edge2=triangles[:,2]-triangles[:,0]
    flags=[]; shorts=[]; count=0; minimum=math.inf; offset=1e-5
    detail=out/'normal-chords.jsonl.gz'
    with detail.open('wb') as raw, gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as g:
        for face,triangle in enumerate(triangles):
            normal=normals[face]; direction=-normal
            h=np.cross(np.broadcast_to(direction,edge2.shape),edge2)
            a=np.einsum('ij,ij->i',edge1,h)
            mask=np.abs(a)>1e-12
            inv=np.divide(1,a,out=np.zeros_like(a),where=mask)
            for sample,weight in enumerate(WEIGHTS):
                point=weight@triangle; origin=point+normal*offset
                s=origin-triangles[:,0]
                u=inv*np.einsum('ij,ij->i',s,h)
                q=np.cross(s,edge1)
                v=inv*(q@direction)
                t=inv*np.einsum('ij,ij->i',edge2,q)
                hits=np.flatnonzero(mask&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(t>=0))
                hits=hits[np.argsort(t[hits],kind='stable')]
                groups=[]
                for hit in hits:
                    if not groups or abs(float(t[hit])-groups[-1]['t_mm'])>1e-6:
                        groups.append({'t_mm':float(t[hit]),'faces':[],'crossings':[]})
                    groups[-1]['faces'].append(int(hit))
                    groups[-1]['crossings'].append(-1 if float(normals[hit]@direction)<0 else 1)
                reasons=[]
                if len(groups)<2: reasons.append('missing_entry_or_exit')
                if groups and (abs(groups[0]['t_mm']-offset)>1e-7 or face not in groups[0]['faces']):
                    reasons.append('entry_not_at_original_face')
                signs=[]
                for group in groups:
                    unique=set(group['crossings'])
                    if len(unique)!=1: reasons.append('opposing_near_coincident_crossings')
                    signs.append(group['crossings'][0])
                if signs != [-1 if i%2==0 else 1 for i in range(len(signs))] or len(signs)%2:
                    reasons.append('crossings_not_alternating_enter_exit')
                chord=groups[1]['t_mm']-groups[0]['t_mm'] if len(groups)>1 else None
                if chord is not None: minimum=min(minimum,chord)
                row={'original_face_index':face,'sample_index':sample,'barycentric_weights':weight.tolist(),
                     'surface_point_mm':point.tolist(),'original_outward_unit_normal':normal.tolist(),
                     'first_solid_chord_mm':chord,'original_triangle_mm':triangle.tolist(),
                     'intersection_events':groups,'reasons':sorted(set(reasons))}
                g.write((json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode())
                if reasons: flags.append(row)
                if chord is not None and chord<width: shorts.append(row)
                count+=1
            if (face+1)%100==0: print(f'normal rays: {face+1}/{len(triangles)} faces',flush=True)
    write_gzip_json(out/'normal-chord-flags.json.gz',flags)
    write_gzip_json(out/'normal-chord-short.json.gz',shorts)
    return {'samples':count,'samples_per_original_face':len(WEIGHTS),'minimum_required_chord_mm':width,
            'minimum_first_solid_chord_mm':minimum if math.isfinite(minimum) else None,
            'flagged_sample_count':len(flags),'short_sample_count':len(shorts),
            'passed':count==len(triangles)*len(WEIGHTS) and not flags and not shorts,
            'detail':detail.name,'detail_sha256':sha256(detail),
            'flags':'normal-chord-flags.json.gz','short_samples':'normal-chord-short.json.gz',
            'ray_origin_outside_offset_mm':offset,'intersection_event_grouping_tolerance_mm':1e-6,
            'limits':'Finite numerical original-normal rays; not global minimum thickness. Shared-face intersections grouped only at stated numerical tolerance. All flags remain failures.'}


def support(triangles,normals,out,layer,angle,area_tolerance):
    zmin,zmax=float(triangles[:,:,2].min()),float(triangles[:,:,2].max())
    reach=layer*math.tan(math.radians(angle)); rows=[]; flags=[]
    for offset in [.031,.071,.137]:
        previous=None; index=0
        while (z:=zmin+offset+layer*index)<zmax:
            row={'offset_mm':offset,'layer_index':index,'z_mm':z};index+=1
            try:
                parts,detail=original_section(triangles,z)
                shape=MultiPolygon(parts)
                row.update({'valid_original_section':True,'area_mm2':shape.area,'material_components':len(parts),
                            'original_section_face_indices':detail['source_face_indices']})
                if previous is not None:
                    unsupported=shape.difference(previous.buffer(reach,quad_segs=32))
                    row['outside_previous_layer_envelope_mm2']=unsupported.area
                    row['passed']=unsupported.area<=area_tolerance
                    if not row['passed']:
                        flags.append({**row,'original_section_geometry':mapping(shape),
                                      'previous_section_geometry':mapping(previous),
                                      'unsupported_geometry':mapping(unsupported)})
                else:
                    row.update({'passed':True,'first_section_assumed_on_build_plate':True})
                previous=shape
            except Exception as error:
                row.update({'valid_original_section':False,'passed':False,'error_type':type(error).__name__,'error':str(error)})
                flags.append(row.copy());previous=None
            rows.append(row)
    downward=[]
    for face in np.flatnonzero(normals[:,2]<-math.cos(math.radians(angle))):
        triangle=triangles[face]
        on_plate=bool(np.all(np.abs(triangle[:,2]-zmin)<=1e-6))
        if not on_plate:
            downward.append({'original_face_index':int(face),'original_triangle_mm':triangle.tolist(),
                             'outward_unit_normal':normals[face].tolist(),
                             'area_mm2':float(np.linalg.norm(np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]))/2)})
    write_gzip_json(out/'support-layer-details.json.gz',rows)
    write_gzip_json(out/'support-layer-flags.json.gz',flags)
    write_gzip_json(out/'downward-face-flags.json.gz',downward)
    return {'passed':bool(rows) and all(row['passed'] for row in rows),
            'sampled_layers':len(rows),'flagged_layers':len(flags),
            'downward_faces_above_plate':len(downward),
            'downward_area_above_plate_mm2':sum(x['area_mm2'] for x in downward),
            'worst_outside_envelope_mm2':max((r.get('outside_previous_layer_envelope_mm2',0) for r in rows),default=0),
            'pitch_mm':layer,'offsets_from_z_min_mm':[.031,.071,.137],
            'angle_from_vertical_deg':angle,'horizontal_reach_per_layer_mm':reach,
            'reporting_tolerance_mm2':area_tolerance,
            'limits':'Three finite layer schedules; first section assumed plate-supported. Geometric envelope cannot simulate extrusion, bridging, cooling, adhesion or arbitrary sublayer details. Downward faces are separately flagged without waiver.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stl',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--layer-height',type=float,default=.2)
    p.add_argument('--angle',type=float,default=45);p.add_argument('--width',type=float,default=.8)
    p.add_argument('--support-area-tolerance',type=float,default=.01);a=p.parse_args()
    if a.out.exists() and any(a.out.iterdir()): raise RuntimeError('Output must be fresh')
    a.out.mkdir(parents=True,exist_ok=True)
    r={'passed':False,'completed':False,'checks':{},'stl_sha256':sha256(a.stl),'checker_sources_sha256':checker_inventory()}
    try:
        if not (a.layer_height>0 and a.width>0 and 0<=a.angle<90): raise ValueError('Invalid screen parameters')
        raw,triangles,stored,_=load_stl(a.stl)
        normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        lengths=np.linalg.norm(normals,axis=1)
        if not np.all(lengths>0): raise ValueError('Degenerate original triangles')
        normals/=lengths[:,None]
        r['normal_chords']=normal_chords(triangles,normals,a.out,a.width)
        r['layer_support']=support(triangles,normals,a.out,a.layer_height,a.angle,a.support_area_tolerance)
        r['checks']={'normal_chords_screen_passed':r['normal_chords']['passed'],
                     'layer_support_screen_passed':r['layer_support']['passed'],
                     'no_downward_faces_above_plate':r['layer_support']['downward_faces_above_plate']==0,
                     'input_unchanged':sha256(a.stl)==hashlib.sha256(raw).hexdigest()}
        r.update(completed=True,passed=all(r['checks'].values()))
    except Exception as error:r.update(error_type=type(error).__name__,error=str(error))
    r['artifacts']={x.name:{'bytes':x.stat().st_size,'sha256':sha256(x)} for x in sorted(a.out.iterdir()) if x.is_file()}
    write_json(a.out/'manufacturing-check.json',r)
    print(json.dumps({'passed':r['passed'],'checks':r['checks'],'error':r.get('error')}),flush=True)
    return 0 if r['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
