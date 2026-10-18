"""Locate a thin core connection on an exact-STL-coordinate section.

Fractions assemble triangle-plane segments before Shapely's floating-point
erosion. This is supplementary localization and does not change any QA gate.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from shapely.geometry import LineString, Polygon
from shapely.ops import nearest_points, polygonize_full, unary_union

from measure_print_risks import read_stl


def parts(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    return [p for item in g.geoms for p in parts(item)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mesh',type=Path); ap.add_argument('--z',default='15.1')
    ap.add_argument('--json',type=Path,required=True)
    a=ap.parse_args(); data,v,f=read_stl(a.mesh); z=F(a.z)
    rv=[tuple(F(x) for x in p) for p in v]
    segments=[]; rational_segments=[]
    for face in f:
        hits=[]
        for i,j in zip(face,face[1:]+face[:1]):
            p,q=rv[i],rv[j]
            if p[2]==z: hits.append(p[:2])
            if (p[2]<z<q[2]) or (q[2]<z<p[2]):
                t=(z-p[2])/(q[2]-p[2]);hits.append(tuple(p[k]+t*(q[k]-p[k]) for k in (0,1)))
        hits=list(dict.fromkeys(hits))
        if len(hits)==2:
            rational_segments.append(hits)
            segments.append([(float(x),float(y)) for x,y in hits])
    polys,cuts,dangles,invalid=polygonize_full(unary_union([LineString(s) for s in segments]))
    occupied=[]
    for p in polys.geoms:
        x,y=p.representative_point().coords[0];crossings=0
        for (ax,ay),(bx,by) in segments:
            if (ay>y)!=(by>y) and ax+(y-ay)*(bx-ax)/(by-ay)>x:crossings+=1
        if crossings%2:occupied.append(p)
    section=unary_union(occupied);core=section.buffer(-.4,join_style=2);cp=sorted(parts(core),key=lambda p:p.area,reverse=True)
    rows=[]
    for radius in [0,.05,.1,.15,.2,.25,.3,.35,.375,.39,.4]:
        q=section.buffer(-radius,join_style=2); ps=parts(q)
        rows.append({'erosion_radius_mm':radius,'component_count':len(ps),'areas_mm2':[p.area for p in ps]})
    pairs=[]
    for i in range(len(cp)):
        for j in range(i+1,len(cp)):
            p,q=nearest_points(cp[i],cp[j]);mid=((p.x+q.x)/2,(p.y+q.y)/2)
            local=[]
            for exact,segment in zip(rational_segments,segments):
                line=LineString(segment)
                if line.distance(LineString([p,q]))<2:
                    local.append({'endpoints_mm':segment,'exact_endpoints_mm':[[str(x) for x in pt] for pt in exact]})
            pairs.append({'core_pair':[i,j],'nearest_core_points_mm':[list(p.coords[0]),list(q.coords[0])],
                'core_gap_mm':p.distance(q),'midpoint_mm':mid,'section_segments_within_2mm_of_core_gap':local})
    result={'scope':'Supplementary localization; no gate override. Exact rational triangle-plane section endpoints converted to floating Shapely erosion.',
        'stl_sha256':hashlib.sha256(data).hexdigest(),'z_mm_exact':str(z),'section_material_component_count':len(parts(section)),
        'invalid_section_counts':{'cuts':len(cuts.geoms),'dangles':len(dangles.geoms),'invalid':len(invalid.geoms)},
        'core_components_at_fixed_0p4mm_radius':[{'area_mm2':p.area,'bounds_mm':p.bounds,'exterior_mm':list(p.exterior.coords)} for p in cp],
        'erosion_sweep_is_diagnostic_only_fixed_gate_remains_0p4mm':rows,'core_gap_localization':pairs,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('core_components_at_fixed_0p4mm_radius',)},indent=2))
    print(json.dumps({'cores':[{'area_mm2':p.area,'bounds_mm':p.bounds} for p in cp]},indent=2))


if __name__=='__main__':main()
