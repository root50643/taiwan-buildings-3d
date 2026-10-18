"""Bound tiny >45-degree facet slopes on the unchanged original STL lattice.

The Fraction intervals enclose plane slope run over each triangle's full Z
span. They do not change a support threshold or establish a print process.
"""
import argparse
from fractions import Fraction as F
import hashlib,json,math
from pathlib import Path

from measure_print_risks import read_stl,sub,cross

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--results',type=Path,required=True);ap.add_argument('--json',type=Path,required=True)
a=ap.parse_args();rows=[];precision=10**18
for directory in sorted(p for p in a.results.iterdir() if p.is_dir() and p.name!='inputs'):
    report=directory/'print-risk-measurement.json'
    if not report.exists():continue
    evidence=json.loads(report.read_text(encoding='utf8'))
    stl=a.results/'inputs'/(directory.name+'.stl');data,v,faces=read_stl(stl)
    digest=hashlib.sha256(data).hexdigest()
    if digest!=evidence['stl_sha256']:raise ValueError('STL/report hash mismatch')
    facets=[]
    for entry in evidence['nonbase_downward_facets']:
        if entry['exact_within_45_degrees']:continue
        face_id=entry['stl_record_face_index'];tri=[tuple(F(x) for x in v[i]) for i in faces[face_id]]
        n=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]));xy2=n[0]**2+n[1]**2
        if not xy2 or not n[2]**2>xy2:raise ValueError('Requires an actual sloping, strict over45 facet')
        if [str(x) for x in n]!=entry['unnormalized_normal_exact']:raise ValueError('Stored normal evidence mismatch')
        dz=max(p[2] for p in tri)-min(p[2] for p in tri)
        floor=math.isqrt((xy2.numerator*precision**2)//xy2.denominator)
        root_lo,root_hi=F(floor,precision),F(floor+1,precision)
        if not 0<root_lo or not root_lo**2<=xy2<=root_hi**2:raise ValueError('Exact square-root interval invalid')
        low=dz*(abs(n[2])/root_hi-1);high=dz*(abs(n[2])/root_lo-1)
        facets.append({'face':face_id,'vertices_mm':entry['vertices_mm'],'normal_exact':[str(x) for x in n],
            'z_span_mm_exact':str(dz),'sqrt_xy_normal_interval_exact':[str(root_lo),str(root_hi)],
            'full_z_span_plane_outward_excess_over_45_interval_mm_exact':[str(low),str(high)],
            'full_z_span_plane_outward_excess_over_45_interval_mm':[float(low),float(high)],
            'original_exact_over45_flag_retained':True})
    rows.append({'id':directory.name,'stl_sha256':digest,'source_risk_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
        'strict_over45_facet_count':len(facets),
        'maximum_full_z_plane_excess_upper_bound_mm':max((f['full_z_span_plane_outward_excess_over_45_interval_mm'][1] for f in facets),default=0),
        'facets':facets})
r={'scope':'Supplemental exact Fraction bounds on only the original strict over45 facets. These flags are retained. Fixed 0.01 mm2 sampled support gate and all original exits/reports remain unchanged.',
    'method':'Recompute normals from original binary32 vertices as exact Fractions. Bound sqrt(nx^2+ny^2) by adjacent rational values on a 1e-18 lattice using integer square root; invert interval to enclose abs(nz)/sqrt(nx^2+ny^2), multiply by full triangle Z span, subtract the 45-degree run.',
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'parts':rows,'no_slicer_or_physical_print':True}
a.json.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps({'parts':[{k:v for k,v in p.items() if k!='facets'} for p in rows]},indent=2))
