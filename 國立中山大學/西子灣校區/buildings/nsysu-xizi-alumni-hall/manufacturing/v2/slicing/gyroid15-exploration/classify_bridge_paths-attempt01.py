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
    result=[]
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
            if de>1e-7 and math.dist(xyz[:2],nxt[:2])>1e-7 and 'bridge' in role.lower():
                result.append({'gcode_line':no,'layer':layer,'z_mm':nxt[2],
                    'xy0_gcode_mm':xyz[:2],'xy1_gcode_mm':nxt[:2],'type':role})
            xyz=nxt
    return result


def footprint(mesh,z):
    segments=trimesh.intersections.mesh_plane(mesh,[0,0,1],[0,0,z])
    if not len(segments):return None
    lines=MultiLineString([s[:,:2] for s in segments])
    # build_area preserves nested contours. No buffer repair is performed.
    area=build_area(unary_union(lines))
    if area.is_empty or not area.is_valid:raise RuntimeError('Invalid layer footprint at '+str(z))
    return area


def main():
    rows=[]
    for folder in sorted(ROOT.glob('0[1-6]-*')):
        audit=json.loads((folder/'gcode-audit.json').read_text())
        mesh=trimesh.load_mesh(audit['input_stl'],process=True)
        center=mesh.bounds[:,:2].mean(axis=0)
        offset=np.array([110.,110.])-center
        bridges=paths(Path(audit['gcode']))
        assert len(bridges)==audit['bridge_infill_segments']
        cache={}
        layerstats=defaultdict(lambda:{'segments':0,'total_xy_length_mm':0.,
            'outside_previous_nominal_footprint_centerline_mm':0.,
            'outside_current_nominal_footprint_centerline_mm':0.,'max_outside_previous_segment_mm':0.})
        for b in bridges:
            z=b['z_mm']
            if z not in cache:
                cache[z]=(footprint(mesh,z-LAYER*1.5),footprint(mesh,z-LAYER*.5))
            prev,cur=cache[z]
            a=np.asarray(b['xy0_gcode_mm'])-offset;c=np.asarray(b['xy1_gcode_mm'])-offset
            line=LineString([a,c])
            # Explicit diagnostic tolerance handles only G-code's 0.001mm XY
            # rounding. It does not alter the independent geometry thresholds.
            eps=.002
            outside=line.length if prev is None else line.difference(prev.buffer(eps)).length
            nowoutside=line.length if cur is None else line.difference(cur.buffer(eps)).length
            b.update({'xy0_stl_print_mm':a.tolist(),'xy1_stl_print_mm':c.tolist(),
                'previous_mesh_sample_z_mm':z-LAYER*1.5,'current_mesh_sample_z_mm':z-LAYER*.5,
                'outside_previous_nominal_footprint_centerline_mm':outside,
                'outside_current_nominal_footprint_centerline_mm':nowoutside})
            s=layerstats[b['layer']];s['segments']+=1;s['z_mm']=z
            s['total_xy_length_mm']+=line.length
            s['outside_previous_nominal_footprint_centerline_mm']+=outside
            s['outside_current_nominal_footprint_centerline_mm']+=nowoutside
            s['max_outside_previous_segment_mm']=max(s['max_outside_previous_segment_mm'],outside)
        result={'id':folder.name,'input_stl_sha256':audit['input_stl_sha256'],
            'gcode_sha256':audit['gcode_sha256'],'bridge_segments':len(bridges),
            'xy_translation_stl_to_gcode_mm':offset.tolist(),
            'method':'Nominal STL XY cross sections at previous/current layer midplanes; compare actual Bridge infill line centerlines after reversing documented single-object center110,110 placement.',
            'explicit_xy_rounding_allowance_mm':.002,
            'layer_height_mm':LAYER,'per_layer':dict(layerstats),'actual_bridge_paths':bridges,
            'limitations':'Nominal interior material includes sparse infill voids. Covered centerlines can bridge across sparse infill; this is not a test of extrusion, adhesion, sagging, machine settings or support-removal force. Does not change any geometry-check result.'}
        (folder/'bridge-location-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        row={k:result[k] for k in ['id','bridge_segments','xy_translation_stl_to_gcode_mm']}
        row.update({'outside_previous_nominal_mm':sum(v['outside_previous_nominal_footprint_centerline_mm'] for v in layerstats.values()),
            'outside_current_nominal_mm':sum(v['outside_current_nominal_footprint_centerline_mm'] for v in layerstats.values()),
            'per_layer':dict(layerstats)})
        rows.append(row)
        print(json.dumps(row),flush=True)
    (ROOT/'bridge-location-summary.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
