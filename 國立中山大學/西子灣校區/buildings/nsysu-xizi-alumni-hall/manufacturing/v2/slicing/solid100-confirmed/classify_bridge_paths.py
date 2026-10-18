"""Locate actual Bridge infill against previous nominal STL layer footprints.

This distinguishes internal bridge paths above sparse infill from paths outside
the preceding model silhouette. It does not simulate extrusion or validate a
physical bridge span. The original geometric overhang gate remains independent.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
import trimesh
from shapely import build_area
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
LAYER = 0.15


def paths(gcode):
    xyz=[0.,0.,0.];e=0.;relative_e=False;relative_xyz=False;role='';layer=-1
    result=[]; max_motion_z=0.
    for no,raw in enumerate(gcode.read_text(encoding='utf-8-sig').splitlines(),1):
        line=raw.strip()
        if line==';LAYER_CHANGE':layer+=1
        if line.startswith(';TYPE:'):role=line[6:].strip()
        code=line.partition(';')[0].strip()
        if not code:continue
        cmd=code.split()[0].upper()
        vals={m.group(1).upper():float(m.group(2)) for m in re.finditer(r'([XYZEF])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)',code)}
        if cmd=='M82':relative_e=False
        elif cmd=='M83':relative_e=True
        elif cmd=='G90':relative_xyz=False
        elif cmd=='G91':relative_xyz=True
        elif cmd=='G92':
            for i,a in enumerate('XYZ'):
                if a in vals:xyz[i]=vals[a]
            if 'E' in vals:e=vals['E']
        elif cmd in {'G0','G00','G1','G01'}:
            nxt=[xyz[i]+vals.get(a,0.) if relative_xyz else vals.get(a,xyz[i]) for i,a in enumerate('XYZ')]
            de=vals.get('E',0.) if relative_e else vals.get('E',e)-e
            if 'E'in vals:e=e+vals['E'] if relative_e else vals['E']
            max_motion_z=max(max_motion_z,nxt[2])
            if de>1e-7 and math.dist(xyz[:2],nxt[:2])>1e-7:
                result.append({'gcode_line':no,'layer':layer,'z_mm':nxt[2],
                    'xy0_gcode_mm':xyz[:2],'xy1_gcode_mm':nxt[:2],'type':role})
            xyz=nxt
    return result,max_motion_z


def footprint(mesh,z):
    section=mesh.section([0,0,1],[0,0,z])
    if section is None:return None
    # mesh.section uses mesh topology to stitch triangle-plane intersections.
    # build_area preserves nested contours. No mesh/polygon repair is performed.
    lines=MultiLineString([s[:,:2] for s in section.discrete])
    area=build_area(lines)
    if area.is_empty or not area.is_valid:raise RuntimeError('Invalid layer footprint at '+str(z))
    return area


def main():
    rows=[]
    build=json.loads((ROOT/'inputs-build-report.json').read_text())
    parts={p['id']:p for p in build['parts']}
    reference=ROOT.parent/'candidate/國立中山大學/西子灣校區/buildings/nsysu-xizi-alumni-hall/models/v4/model.stl'
    refmesh=trimesh.load_mesh(reference,process=True)
    refcache={}
    for folder in sorted(ROOT.glob('0[1-6]-*')):
        audit=json.loads((folder/'gcode-audit.json').read_text())
        mesh=trimesh.load_mesh(audit['input_stl'],process=True)
        center=mesh.bounds[:,:2].mean(axis=0)
        offset=np.array([110.,110.])-center
        allpaths,max_motion_z=paths(Path(audit['gcode']))
        bridges=[p for p in allpaths if 'bridge' in p['type'].lower()]
        assert len(bridges)==audit['bridge_infill_segments']
        all_by_layer=defaultdict(list)
        for p in allpaths:all_by_layer[p['layer']].append(p)
        sweepcache={}
        cache={}
        layerstats=defaultdict(lambda:{'segments':0,'total_xy_length_mm':0.,
            'outside_previous_nominal_footprint_centerline_mm':0.,
            'outside_current_nominal_footprint_centerline_mm':0.,'max_outside_previous_segment_mm':0.,
            'outside_reference_previous_nominal_centerline_mm':0.,
            'longest_continuous_gap_without_previous_planned_extrusion_mm':0.,
            'total_gap_without_previous_planned_extrusion_mm':0.,'longest_gap_witness':None})
        for b in bridges:
            z=b['z_mm']
            if z not in cache:
                cache[z]=(footprint(mesh,z-LAYER*1.5),footprint(mesh,z-LAYER*.5))
            prev,cur=cache[z]
            a=np.asarray(b['xy0_gcode_mm'])-offset;c=np.asarray(b['xy1_gcode_mm'])-offset
            line=LineString([a,c])
            outside=line.length if prev is None else line.difference(prev).length
            nowoutside=line.length if cur is None else line.difference(cur).length
            assembly=parts[folder.name]['transform_print_to_assembled']
            transform=np.asarray(assembly)
            ap=transform@np.array([*a,z-LAYER*1.5,1.])
            cp=transform@np.array([*c,z-LAYER*1.5,1.])
            ref_z=float(ap[2])
            if ref_z not in refcache:refcache[ref_z]=footprint(refmesh,ref_z)
            refsection=refcache[ref_z]
            refline=LineString([ap[:2],cp[:2]])
            refoutside=refline.length if refsection is None else refline.difference(refsection).length
            layer=b['layer']
            if layer==0:
                gaps=[] # First layer is supported by the build plate.
            else:
                if layer-1 not in sweepcache:
                    prior=all_by_layer[layer-1]
                    priorlines=MultiLineString([[p['xy0_gcode_mm'],p['xy1_gcode_mm']] for p in prior])
                    sweepcache[layer-1]=unary_union(priorlines).buffer(.225,quad_segs=16,cap_style=1,join_style=1)
                gap=LineString([b['xy0_gcode_mm'],b['xy1_gcode_mm']]).difference(sweepcache[layer-1])
                gaps=[] if gap.is_empty else ([gap] if gap.geom_type=='LineString' else [g for g in gap.geoms if g.geom_type=='LineString'])
            maxgap=max((g.length for g in gaps),default=0.)
            witness=None
            if gaps:
                g=max(gaps,key=lambda g:g.length)
                witness={'gcode_line':b['gcode_line'],'continuous_gap_length_mm':g.length,
                    'xy_gcode_mm':list(g.coords),'xy_stl_print_mm':(np.asarray(g.coords)-offset).tolist()}
            b.update({'xy0_stl_print_mm':a.tolist(),'xy1_stl_print_mm':c.tolist(),
                'previous_mesh_sample_z_mm':z-LAYER*1.5,'current_mesh_sample_z_mm':z-LAYER*.5,
                'outside_previous_nominal_footprint_centerline_mm':outside,
                'outside_current_nominal_footprint_centerline_mm':nowoutside,
                'reference_previous_assembled_z_mm':ref_z,
                'outside_reference_previous_nominal_centerline_mm':refoutside,
                'continuous_gap_lengths_without_previous_planned_extrusion_mm':[g.length for g in gaps],
                'longest_gap_witness':witness})
            s=layerstats[b['layer']];s['segments']+=1;s['z_mm']=z
            s['total_xy_length_mm']+=line.length
            s['outside_previous_nominal_footprint_centerline_mm']+=outside
            s['outside_current_nominal_footprint_centerline_mm']+=nowoutside
            s['max_outside_previous_segment_mm']=max(s['max_outside_previous_segment_mm'],outside)
            s['outside_reference_previous_nominal_centerline_mm']+=refoutside
            s['total_gap_without_previous_planned_extrusion_mm']+=sum(g.length for g in gaps)
            if maxgap>s['longest_continuous_gap_without_previous_planned_extrusion_mm']:
                s['longest_continuous_gap_without_previous_planned_extrusion_mm']=maxgap
                s['longest_gap_witness']=witness
        result={'id':folder.name,'input_stl_sha256':audit['input_stl_sha256'],
            'gcode_sha256':audit['gcode_sha256'],'bridge_segments':len(bridges),
            'xy_translation_stl_to_gcode_mm':offset.tolist(),
            'method':'Nominal STL XY cross sections at previous/current layer midplanes; compare actual Bridge infill line centerlines after reversing documented single-object center110,110 placement.',
            'explicit_xy_rounding_allowance_mm':0.,
            'previous_planned_extrusion_sweep_radius_mm':.225,
            'sweep_buffer_quad_segments':16,
            'sweep_polygon_max_radial_approximation_mm':.225*(1-math.cos(math.pi/64)),
            'support_sweep_interpretation':'Planned positive XY G-code extrusion from immediately preceding layer, swept at fixed requested width 0.45mm. Every resulting continuous gap is measured separately, not the full Bridge line. First layer supported by bed. This is a planned-path geometric diagnostic, not observed printed plastic.',
            'max_extruding_z_mm':max(p['z_mm'] for p in allpaths),
            'max_motion_z_mm':max_motion_z,
            'stl_z_max_mm':float(mesh.bounds[1,2]),
            'z_quantization_difference_mm':max(p['z_mm'] for p in allpaths)-float(mesh.bounds[1,2]),
            'layer_height_mm':LAYER,'per_layer':dict(layerstats),'actual_bridge_paths':bridges,
            'limitations':'Nominal interior material includes sparse infill voids. Covered centerlines can bridge across sparse infill; this is not a test of extrusion, adhesion, sagging, machine settings or support-removal force. Does not change any geometry-check result.'}
        (folder/'bridge-location-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        row={k:result[k] for k in ['id','bridge_segments','xy_translation_stl_to_gcode_mm']}
        row.update({'outside_previous_nominal_mm':sum(v['outside_previous_nominal_footprint_centerline_mm'] for v in layerstats.values()),
            'outside_current_nominal_mm':sum(v['outside_current_nominal_footprint_centerline_mm'] for v in layerstats.values()),
            'outside_reference_previous_nominal_mm':sum(v['outside_reference_previous_nominal_centerline_mm'] for v in layerstats.values()),
            'longest_continuous_gap_without_previous_planned_extrusion_mm':max((v['longest_continuous_gap_without_previous_planned_extrusion_mm'] for v in layerstats.values()),default=0.),
            'max_extruding_z_mm':result['max_extruding_z_mm'],'max_motion_z_mm':max_motion_z,
            'stl_z_max_mm':result['stl_z_max_mm'],'z_quantization_difference_mm':result['z_quantization_difference_mm'],
            'actual_xy_bounds_including_brim_mm':audit['all_extrusion_xy_bounds_mm'],
            'per_layer':dict(layerstats)})
        rows.append(row)
        print(json.dumps(row),flush=True)
    (ROOT/'bridge-location-summary.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
