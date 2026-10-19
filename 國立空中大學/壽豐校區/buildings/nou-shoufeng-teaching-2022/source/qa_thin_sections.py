"""Finite-resolution whole-section thin-feature screening of exported STL files.

This does NOT prove a continuous global 3D minimum wall thickness. All X/Y/Z
midplanes are sampled at 0.15 mm; each complete polygonal cross-section receives
a disk morphological opening, and all residual flags remain in the report.
Identical exported SHA geometry is computed once and explicitly reused per part.
"""
from pathlib import Path
import json, math, copy, datetime
from collections import Counter
import numpy as np
import trimesh as tm
from shapely.geometry import LineString, GeometryCollection, Polygon
from qa_geometry import polygons, sha

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa'
SPACING=.15
NOMINAL=1.2
FLOAT_ALLOWANCE=.0002
RADIUS=(NOMINAL-FLOAT_ALLOWANCE)/2
QUAD_SEGS=64
AREA_NOISE=1e-8
LINEAR_TOL=1e-4
COLLINEAR_TOL=1e-6

def section_audited(mesh,axis,value):
    normal=np.eye(3)[axis]
    path=mesh.section(plane_origin=normal*value,plane_normal=normal)
    dims=[a for a in range(3) if a!=axis]
    shape=GeometryCollection()
    audit={'open_or_degenerate_loop_count':0,'invalid_loop_repair_count':0,
           'repair_absolute_area_change_mm2':0.}
    if path is not None:
        for loop in path.discrete:
            if len(loop)<4 or np.linalg.norm(loop[0]-loop[-1])>=LINEAR_TOL:
                audit['open_or_degenerate_loop_count']+=1
                continue
            p=Polygon(loop[:,dims])
            if not p.is_valid:
                repaired=p.buffer(0)
                audit['invalid_loop_repair_count']+=1
                audit['repair_absolute_area_change_mm2']+=abs(repaired.area-p.area)
                p=repaired
            shape=shape.symmetric_difference(p)
    audit['section_valid_before_simplification']=bool(shape.is_valid)
    # Tiny near-collinear vertices from triangle-plane intersections can make
    # almost diameter-wide strips numerically unstable during erosion. Preserve
    # the raw report in history; record the exact changed area in every plane.
    clean=shape.simplify(COLLINEAR_TOL,preserve_topology=True)
    audit['collinear_simplification_symmetric_difference_area_mm2']=float(shape.symmetric_difference(clean).area)
    return clean,audit

def xyz_at(axis, plane, uv):
    out=[0.,0.,0.]
    out[axis]=float(plane)
    dims=[a for a in range(3) if a!=axis]
    out[dims[0]],out[dims[1]]=map(float,uv)
    return out

def bounds3d(axis, plane, g):
    x0,y0,x1,y1=g.bounds
    return [xyz_at(axis,plane,(x0,y0)),xyz_at(axis,plane,(x1,y1))]

def in_bounds(bounds, target, tol=.001):
    return all(bounds[0][i]>=target[0][i]-tol and bounds[1][i]<=target[1][i]+tol for i in range(3))

def residue_class(name, axis, plane, p, wholly_eroded=False):
    b=bounds3d(axis,plane,p)
    # These are narrow horizontal cuts through the ends of a continuously curved
    # 1.6-mm-wide arch relief integral with a >=1.2-mm ceiling base.
    if 'ceiling' in name and any(in_bounds(b,t) for t in [
        [[138.79,-.01,1.19],[149.21,1.61,3.21]],
        [[28.39,-94.41,1.19],[30.01,-84.79,3.21]]]):
        return 'curved_arch_relief_taper_slice'
    # Exact shallow decorative groove top lip: z thickness .5 mm, projection .3
    # mm, while a 1.2 mm core continues immediately behind it.
    if 'lower' in name and not name.startswith('01') and b[0][2]>=3.89 and b[1][2]<=4.51:
        if ((b[0][0]>=31.99 and b[0][1]>=29.69 and b[1][1]<=30.01)
            or (b[0][1]>=31.99 and b[0][0]>=29.69 and b[1][0]<=30.01)):
            return 'decorative_groove_upper_lip'
        if ((b[0][0]>=31.99 and b[0][1]>=29.099 and b[1][1]<=30.01)
            or (b[0][1]>=31.99 and b[0][0]>=29.099 and b[1][0]<=30.01)):
            return 'groove_upper_lip_and_adjacent_disk_rounding'
    if 'lower' in name:
        dz=2 if name.startswith('01') else 0
        if (b[0][1]>=124.39 and b[1][1]<=126.01 and b[0][2]>=2.4+dz and b[1][2]<=7.5+dz
            and ((b[0][0]>=-.01 and b[1][0]<=1.25)
                 or (b[0][0]>=20.7 and b[1][0]<=22.01))):
            return 'blind_window_terminal_border_and_adjacent_corner'
    # A round disk opening replaces a sharp convex corner by a circular arc.
    # A residual confined to a radius-sized box and no larger than the square
    # corner deficit is the expected rounding loss, not a width measurement.
    widths=np.asarray(p.bounds[2:])-np.asarray(p.bounds[:2])
    corner_area=RADIUS*RADIUS*(1-math.pi/4)
    if not wholly_eroded and max(widths)<=RADIUS+.001 and p.area<=corner_area+.002:
        return 'disk_opening_convex_corner_residual'
    return 'unresolved_opening_residual_needs_review'

def lines(g):
    if g.is_empty: return []
    if g.geom_type=='LineString': return [g]
    return [a for b in getattr(g,'geoms',[]) for a in lines(b)]

def z_line_screen(shape, x, name):
    """For this sampled X plane, screen Y event intervals across the whole shape.

    Each polygon vertex Y is an event; both just-inside interval ends and the
    midpoint are sampled. Vertical segment thickness is linear between events
    in a polygonal mesh section. This includes recess lips and arch relief.
    """
    simplified=shape.simplify(1e-6,preserve_topology=True)
    events=[]
    for p in polygons(simplified):
        events.extend(q[0] for q in p.exterior.coords)
        for ring in p.interiors: events.extend(q[0] for q in ring.coords)
    events=sorted(set(round(float(v),7) for v in events))
    probes=[]
    for a,b in zip(events[:-1],events[1:]):
        if b-a<=1e-6: continue
        inset=min(.0001,(b-a)/10)
        probes.extend([a+inset,(a+b)/2,b-inset])
    probes=sorted(set(probes))
    minimum=math.inf
    worst=None
    flags=[]
    count=0
    for y in probes:
        cross=simplified.intersection(LineString([(y,-1.),(y,100.)]))
        for seg in lines(cross):
            z0,z1=seg.bounds[1],seg.bounds[3]
            thickness=z1-z0
            if thickness<1e-6: continue
            count+=1
            if thickness<minimum:
                minimum=thickness;worst={'x_mm':x,'y_mm':y,'z_interval_mm':[z0,z1],
                                         'vertical_solid_segment_length_mm':thickness}
            if thickness<NOMINAL-FLOAT_ALLOWANCE:
                cls='unresolved_short_vertical_segment_needs_review'
                if ('lower' in name and not name.startswith('01')
                    and abs(z0-4.)<.001 and abs(z1-4.5)<.001
                    and ((x>=32 and y>=29.699 and y<=30.001)
                         or (y>=32 and x>=29.699 and x<=30.001))):
                    cls='decorative_groove_upper_lip'
                flags.append({'xyz_start_mm':[x,y,z0],'xyz_end_mm':[x,y,z1],
                    'vertical_solid_segment_length_mm':thickness,'classification':cls})
    return {'y_event_count':len(events),'vertical_line_count':len(probes),
            'nonzero_solid_segment_count':count,
            'minimum_vertical_solid_segment_mm':None if math.isinf(minimum) else minimum,
            'worst_vertical_segment':worst,'short_segment_flags':flags}

def one_geometry(mesh,name,stl_sha):
    out={'representative_stl':name,'stl_sha256':stl_sha,'bounds_mm':mesh.bounds.tolist(),
        'axes':{},'vertical_segment_screening':{'x_planes':[]},
        'interpretation':'Numerical screening requiring manufacturing review; no physical print or continuous global 3D thickness proof.'}
    all_classes=Counter()
    for axis in [2,0,1]:
        lo,hi=mesh.bounds[:,axis]
        planes=np.arange(lo+SPACING/2,hi,SPACING)
        stats={'plane_count':len(planes),'plane_spacing_mm':SPACING,
            'first_plane_mm':float(planes[0]),'last_plane_mm':float(planes[-1]),
            'scanned_shape_area_sum_mm2':0.,'opening_residual_area_sum_mm2':0.,
            'whole_eroded_section_component_count':0,'classification_counts':{},
            'worst_total_residual_plane':None,'worst_residual_component':None,
            'planes':[]}
        class_counts=Counter()
        for n,val in enumerate(planes):
            shape,audit=section_audited(mesh,axis,float(val))
            # Round joins intentionally make every sharp convex corner flag.
            erosion=shape.buffer(-RADIUS,quad_segs=QUAD_SEGS,join_style='round')
            opening=erosion.buffer(RADIUS,quad_segs=QUAD_SEGS,join_style='round')
            lost=shape.difference(opening)
            residuals=[p for p in polygons(lost) if p.area>AREA_NOISE]
            thin=[]
            for p in polygons(shape):
                if p.area>AREA_NOISE and p.buffer(-RADIUS,quad_segs=QUAD_SEGS,join_style='round').is_empty:
                    thin.append({'area_mm2':float(p.area),'bounds_xyz_mm':bounds3d(axis,val,p),
                        'representative_xyz_mm':xyz_at(axis,val,p.representative_point().coords[0]),
                        'classification':residue_class(name,axis,val,p,True)})
            flags=[]
            for p in residuals:
                cls=residue_class(name,axis,val,p)
                flags.append({'area_mm2':float(p.area),'bounds_xyz_mm':bounds3d(axis,val,p),
                    'representative_xyz_mm':xyz_at(axis,val,p.representative_point().coords[0]),
                    'classification':cls})
                class_counts[cls]+=1
            total=float(sum(p.area for p in residuals))
            worst=max(flags,key=lambda r:r['area_mm2']) if flags else None
            row={'plane_mm':float(val),'shape_area_mm2':float(shape.area),'section_integrity':audit,
                'section_component_count':len(polygons(shape)),
                'opening_residual_area_mm2':total,'residual_component_count':len(flags),
                'flag_classification_counts':dict(Counter(r['classification'] for r in flags)),
                'worst_residual_component':worst,
                'all_non_corner_residual_components':[r for r in flags if r['classification']!='disk_opening_convex_corner_residual'],
                'whole_eroded_section_components':thin}
            # Every flagged plane is retained, including all wholly erased islands.
            # Per-corner coordinate lists would only duplicate reproducible data;
            # the worst component, count and classification remain for every plane.
            stats['planes'].append(row)
            stats['scanned_shape_area_sum_mm2']+=float(shape.area)
            stats['opening_residual_area_sum_mm2']+=total
            stats['whole_eroded_section_component_count']+=len(thin)
            if stats['worst_total_residual_plane'] is None or total>stats['worst_total_residual_plane']['area_mm2']:
                stats['worst_total_residual_plane']={'plane_mm':float(val),'area_mm2':total,
                    'worst_residual_component':worst}
            if worst and (stats['worst_residual_component'] is None or worst['area_mm2']>stats['worst_residual_component']['area_mm2']):
                stats['worst_residual_component']={'plane_mm':float(val),**worst}
            if axis==0:
                out['vertical_segment_screening']['x_planes'].append({'x_mm':float(val),
                    **z_line_screen(shape,float(val),name)})
            if (n+1)%250==0: print(name,'axis','xyz'[axis],n+1,'/',len(planes),flush=True)
        stats['classification_counts']=dict(class_counts)
        all_classes.update(class_counts)
        out['axes']['xyz'[axis]]=stats
        print(name,'axis','xyz'[axis],'complete',len(planes),flush=True)
    zr=out['vertical_segment_screening']
    zr['vertical_line_count']=sum(p['vertical_line_count'] for p in zr['x_planes'])
    zr['nonzero_solid_segment_count']=sum(p['nonzero_solid_segment_count'] for p in zr['x_planes'])
    candidates=[p['worst_vertical_segment'] for p in zr['x_planes'] if p['worst_vertical_segment']]
    zr['worst_vertical_segment']=min(candidates,key=lambda r:r['vertical_solid_segment_length_mm']) if candidates else None
    zflags=[f for p in zr['x_planes'] for f in p['short_segment_flags']]
    zr['short_segment_flag_count']=len(zflags)
    zr['short_segment_classification_counts']=dict(Counter(f['classification'] for f in zflags))
    out['summary']={'independently_computed_section_count':sum(a['plane_count'] for a in out['axes'].values()),
        'opening_residual_classification_counts':dict(all_classes),
        'whole_eroded_section_component_count':sum(a['whole_eroded_section_component_count'] for a in out['axes'].values()),
        'short_vertical_segment_flag_count':len(zflags),
        'unresolved_short_vertical_segment_count':sum(f['classification'].startswith('unresolved') for f in zflags)}
    return out

def append_exact_core_proxies(report):
    """Boolean containment of whole expected main cores, with declared inset.

    These rectangular proxy volumes supplement finite planes. They are specific
    slabs, column cores, rail cores and parapets, not an all-directions certificate.
    """
    eps=.0001
    def box(x0,x1,y0,y1,z0,z1):
        m=tm.creation.box([x1-x0,y1-y0,z1-z0])
        m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m
    def combine(items): return tm.boolean.union(items,engine='manifold',check_volume=True)
    result={'face_inset_mm':eps,'missing_proxy_volume_tolerance_mm3':.001,
        'scope':'Entire specified rectangular structural cores only; decorative lips, terminal window borders and curved relief taper are not silently included in this claim.',
        'unique_geometries':{}}
    for s,g in report['geometries'].items():
        name=g['representative_stl'];m=tm.load(ROOT/'models'/name,force='mesh');groups=[]
        inverted='ceiling' in name
        if inverted:
            groups.append(('nominal 1.2 mm complete inverted ceiling base',combine([
                box(eps,156-eps,eps,30-eps,eps,1.2-eps),
                box(eps,30-eps,-96+eps,30-eps,eps,1.2-eps)])))
        else:
            height=3.6 if name.startswith('01') else (1.2 if 'roof' in name else 1.6)
            groups.append((f'nominal {height} mm complete L floor/base slab',combine([
                box(eps,156-eps,eps,30-eps,eps,height-eps),
                box(eps,30-eps,eps,126-eps,eps,height-eps)])))
        if 'lower' in name:
            dz=2 if name.startswith('01') else 0
            cols=[]
            for x in list(np.arange(30,155,12))+[155.2]:
                cols.append(box(x-.8+eps,x+.8-eps,28.4+eps,30-eps,1.6+dz+eps,8.8+dz-eps))
            for y in list(np.arange(30,125,12))+[125.2]:
                cols.append(box(28.4+eps,30-eps,y-.8+eps,y+.8-eps,1.6+dz+eps,8.8+dz-eps))
            groups.append(('all nominal 1.6 by 1.6 mm column cores',combine(cols)))
            if not name.startswith('01'):
                reduced_cols=[]
                for x in list(np.arange(30,155,12))+[155.2]:
                    reduced_cols.append(box(x-.8+eps,x+.8-eps,28.4+eps,29.7-eps,1.6+eps,8.8-eps))
                for y in list(np.arange(30,125,12))+[125.2]:
                    reduced_cols.append(box(28.4+eps,29.7-eps,y-.8+eps,y+.8-eps,1.6+eps,8.8-eps))
                groups.append(('supplement: all continuous column cores 1.6 by 1.3 mm behind front grooves',combine(reduced_cols)))
                groups.append(('whole nominal 1.2 mm uninterrupted grooved railing cores',combine([
                    box(30+eps,156-eps,28.5+eps,29.7-eps,1.6+eps,4.5-eps),
                    box(28.5+eps,29.7-eps,30+eps,126-eps,1.6+eps,4.5-eps)])))
        if 'roof' in name:
            groups.append(('all nominal 1.2 mm parapet straight cores including inner corner',combine([
                box(eps,156-eps,eps,1.2-eps,1.2+eps,3.4-eps),
                box(eps,1.2-eps,eps,126-eps,1.2+eps,3.4-eps),
                box(28.8+eps,156-eps,28.8+eps,30-eps,1.2+eps,3.4-eps),
                box(28.8+eps,30-eps,28.8+eps,126-eps,1.2+eps,3.4-eps),
                box(154.8+eps,156-eps,eps,30-eps,1.2+eps,3.4-eps),
                box(eps,30-eps,124.8+eps,126-eps,1.2+eps,3.4-eps)])))
        checks=[]
        for label,proxy in groups:
            missing=tm.boolean.difference([proxy,m],engine='manifold',check_volume=True)
            vol=float(abs(missing.volume)) if len(missing.faces) else 0.
            checks.append({'specified_core':label,'proxy_volume_mm3':float(proxy.volume),
                'missing_from_exported_stl_volume_mm3':vol,'contained_with_declared_tolerance':vol<=.001,
                'missing_bounds_mm':missing.bounds.tolist() if len(missing.faces) else None})
            if 'lower' in name and not name.startswith('01') and label=='all nominal 1.6 by 1.6 mm column cores':
                checks[-1]['retained_failure_interpretation']='FAIL of uniform nominal 1.6 mm full column envelope: decorative cuts pass across the front 0.3 mm of some columns. Local remaining depth is 1.3 mm, not 1.6 mm everywhere. See separate exact continuous 1.6 by 1.3 mm core supplement; the failure is retained.'
        result['unique_geometries'][s]={'representative_stl':name,'checks':checks}
    result['all_specified_core_proxies_contained']=all(c['contained_with_declared_tolerance'] for g in result['unique_geometries'].values() for c in g['checks'])
    result['all_minimum_core_proxies_contained_excluding_documented_nominal_column_envelope_failure']=all(c['contained_with_declared_tolerance'] for g in result['unique_geometries'].values() for c in g['checks'] if 'retained_failure_interpretation' not in c)
    report['exact_structural_core_proxy_containment']=result
    return report

def main():
    parameters=ROOT/'parameters.json'
    params=json.loads(parameters.read_text(encoding='utf8'))
    report={'schema':'finite-resolution-three-axis-thin-section-screening-v1',
        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'units':'mm','parameters_sha256':sha(parameters),'generator_sha256':sha(ROOT/'source'/'build_model.py'),
        'analysis_script_sha256':sha(Path(__file__)),
        'method':{'all_three_axis_midplane_spacing_mm':SPACING,
            'nominal_thickness_screen_mm':NOMINAL,'floating_point_allowance_mm':FLOAT_ALLOWANCE,
            'morphological_opening_disk_radius_mm':RADIUS,'buffer_quad_segs':QUAD_SEGS,
            'collinear_vertex_simplification_tolerance_mm':COLLINEAR_TOL,
            'disk_chord_radial_error_bound_mm':RADIUS*(1-math.cos(math.pi/(4*QUAD_SEGS))),
            'residual_area_noise_floor_mm2':AREA_NOISE,
            'z_segment_screen':'At every sampled X plane, all section-vertex Y event intervals are sampled at both inset ends (<=0.0001 mm) and midpoint. Every nonzero vertical solid segment is measured.',
            'residual_recording':'Every plane records total residual area, component count, classification counts and worst coordinates; every wholly eroded island and every short vertical segment is retained.',
            'duplicate_geometry':'Exact SHA-identical STL geometry is computed once, then referenced explicitly for every corresponding print part.'},
        'interpretation_legend':{
            'disk_opening_convex_corner_residual':'Expected sharp-corner loss under a round disk opening, bounded by radius-sized box and theoretical quarter-corner area; not proof of a thin structural wall.',
            'curved_arch_relief_taper_slice':'A high horizontal cut intersects the tapering edge of relief integral with the ceiling. Narrow XY section is retained as a flag; full vertical segment and perpendicular sections are used for interpretation.',
            'decorative_groove_upper_lip':'A real 0.5 mm vertical groove lip projecting 0.3 mm in front of the continuous 1.2 mm railing core. Detail needs print verification; not described as a >=1.2 mm feature.',
            'groove_upper_lip_and_adjacent_disk_rounding':'The same 0.5 mm groove lip plus the up-to-radius adjacent rounded-corner deficit created by opening. Original area and bounds remain reported.',
            'blind_window_terminal_border_and_adjacent_corner':'The short-wing last blind window ends at y=125 while the end is y=126, leaving a real 1.0 mm border at the 0.65 mm-deep face recess. The flag includes adjacent disk-rounding loss. The thick classroom mass continues behind the recess; retain as sub-1.2 mm appearance detail, not a separately proven structural wall.',
            'unresolved_opening_residual_needs_review':'Retained numerical flag requiring location/context review. Connected polygon corner/notch/transition loss can exceed the simple corner bound; it is not automatically dismissed.',
            'unresolved_short_vertical_segment_needs_review':'A measured vertical solid segment below threshold outside the explicit decorative lip classification; requires investigation.'},
        'geometries':{},'parts':[],
        'limitations':[
            'This is finite-resolution numerical screening requiring physical validation, not a continuous global minimum 3D thickness proof.',
            'Features between parallel 0.15 mm planes can be missed. The thin end strip after the final midplane is not sampled in that axis.',
            'Axis-aligned sections can overestimate the normal thickness of oblique walls; three directions do not remove that limitation.',
            'Round morphological opening deliberately flags convex corners and relief taper slices. Opening residual area is not the amount of structurally under-thickness material.',
            'Whole-eroded component means a 2D section polygon contains no radius-0.5999 mm disk, not a detached 3D mesh component.',
            'Vertical interval lengths are directional chord lengths, not general local wall-normal thickness. Decorative groove lips remain recorded below 1.2 mm.',
            'No stress analysis, print, support removal, breakage test, extrusion calibration or physical trial fit was performed.']}
    for p in params['parts']:
        path=ROOT/'models'/p['stl'];s=sha(path)
        if s not in report['geometries']:
            mesh=tm.load(path,force='mesh')
            report['geometries'][s]=one_geometry(mesh,p['stl'],s)
        g=report['geometries'][s]
        report['parts'].append({'stl':p['stl'],'sha256':s,'manifest_sha_matches':s==p['sha256'],
            'geometry_result_sha_key':s,'same_geometry_as':g['representative_stl'],
            'planes_by_axis':{a:b['plane_count'] for a,b in g['axes'].items()},
            'opening_residual_area_sum_by_axis_mm2':{a:b['opening_residual_area_sum_mm2'] for a,b in g['axes'].items()},
            'whole_eroded_section_component_count':g['summary']['whole_eroded_section_component_count'],
            'worst_components_by_axis':{a:b['worst_residual_component'] for a,b in g['axes'].items()},
            'worst_vertical_segment':g['vertical_segment_screening']['worst_vertical_segment'],
            'short_vertical_segment_classification_counts':g['vertical_segment_screening']['short_segment_classification_counts']})
        # Recoverable progress if a later unique geometry fails.
        (QA/'thin-section-screening-progress.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    report['final_input_binding']={'parameters_unchanged':sha(parameters)==report['parameters_sha256'],
        'generator_unchanged':sha(ROOT/'source'/'build_model.py')==report['generator_sha256'],
        'all_stls_unchanged':all(sha(ROOT/'models'/p['stl'])==p['sha256'] for p in report['parts']),
        'all_manifest_hashes_match':all(p['manifest_sha_matches'] for p in report['parts'])}
    report['summary']={'unique_sha_geometry_count':len(report['geometries']),
        'independently_computed_section_count':sum(g['summary']['independently_computed_section_count'] for g in report['geometries'].values()),
        'section_count_covered_for_all_nine_parts':sum(sum(p['planes_by_axis'].values()) for p in report['parts']),
        'all_input_binding_checks_pass':all(report['final_input_binding'].values()),
        'unresolved_short_vertical_segment_count_unique_geometry':sum(g['summary']['unresolved_short_vertical_segment_count'] for g in report['geometries'].values()),
        'conclusion':'Finite-resolution flags retained for review. See per-axis coordinates and interpretation; no global 3D minimum thickness certificate.'}
    audits=[p['section_integrity'] for g in report['geometries'].values() for a in g['axes'].values() for p in a['planes']]
    report['summary']['section_integrity']={
        'open_or_degenerate_loop_count':sum(a['open_or_degenerate_loop_count'] for a in audits),
        'invalid_loop_repair_count':sum(a['invalid_loop_repair_count'] for a in audits),
        'invalid_section_count':sum(not a['section_valid_before_simplification'] for a in audits),
        'maximum_simplification_symmetric_difference_area_mm2':max(a['collinear_simplification_symmetric_difference_area_mm2'] for a in audits)}
    append_exact_core_proxies(report)
    report['final_input_binding']['all_stls_still_unchanged_after_proxy_checks']=all(sha(ROOT/'models'/p['stl'])==p['sha256'] for p in report['parts'])
    report['summary']['all_input_binding_checks_pass']=all(report['final_input_binding'].values())
    (QA/'thin-section-screening.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    progress=QA/'thin-section-screening-progress.json'
    if progress.exists():progress.unlink()
    print(json.dumps(report['summary'],indent=2),flush=True)

if __name__=='__main__':main()
