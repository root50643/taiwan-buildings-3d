"""Actual fixed STL section measurements for the r2 clerestory/roof edge.
Run from candidate-repo, using the two preceding supplemental scripts.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
from shapely.geometry import box,LineString
from shapely import wkt
P=next(Path('.').glob('*/**/nthu-macronix-building'));OUT=P/'qa/risk-followup-e45f8d6'
script=OUT/'thin_revision_followup.py';ns={'__file__':str(script)}
exec(compile(script.read_text().split('\nreprojections=[]')[0],str(script),'exec'),ns)
section,tri,normals=ns['section'],ns['tri'],ns['normals']

region,closed,keep=section(2,52.)
strip=region.intersection(box(-39,-10.5,-5,-5.5))
assert closed and strip.geom_type=='Polygon' and strip.is_valid
coords=np.asarray(strip.exterior.coords);xs=sorted(set(float(x) for x in coords[:,0]));bands=[]
for lo,hi in zip(xs[:-1],xs[1:]):
    if hi-lo<1e-9:continue
    mid=(lo+hi)/2;active=[]
    for a,b in zip(coords[:-1],coords[1:]):
        if min(a[0],b[0])<mid<max(a[0],b[0]):
            def yy(x,a=a,b=b):return float(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
            active.append((yy(mid),yy(lo),yy(hi)))
    active.sort();assert len(active)%2==0
    intervals=[]
    for lower,upper in zip(active[::2],active[1::2]):
        intervals.append({'lower_Y_at_X_lo_hi_mm':[lower[1],lower[2]],'upper_Y_at_X_lo_hi_mm':[upper[1],upper[2]],'Y_width_at_X_lo_hi_mm':[upper[1]-lower[1],upper[2]-lower[2]],'minimum_Y_width_mm':min(upper[1]-lower[1],upper[2]-lower[2])})
    bands.append({'X_open_interval_mm':[lo,hi],'one_sided_endpoint_material_intervals':intervals})
lines=[]
for x in [-39,-37,-22,-7,-5]:
    hit=strip.intersection(LineString([(x,-20),(x,0)]))
    lines.append({'X_mm':x,'intersection_WKT':wkt.dumps(hit,rounding_precision=12,trim=True),'Y_material_total_length_mm':float(hit.length)})
allmin=min(i['minimum_Y_width_mm'] for b in bands for i in b['one_sided_endpoint_material_intervals'])
slotbands=[b for b in bands if b['X_open_interval_mm'][0]>=-37-1e-6 and b['X_open_interval_mm'][1]<=-7+1e-6]
slotmin=min(i['minimum_Y_width_mm'] for b in slotbands for i in b['one_sided_endpoint_material_intervals'])

r2=json.loads((OUT/'thin_r2_same_rays_and_roof.json').read_text());roof=[]
for row in r2['new_roof_warnings_with_local_evidence']:
    s=row['new_r2_warning_unchanged'];a=row['axis_chords_at_new_ray_midpoint']['Z'];top,bottom=a['plus']['face'],a['minus']['face']
    nt,nb=normals[top],normals[bottom]
    roof.append({'new_source_face':s['face'],'top_face_at_fixed_ray_midpoint':top,'bottom_face_at_fixed_ray_midpoint':bottom,'top_bottom_normal_angle_deg':math.degrees(math.acos(float(np.clip(nt@nb,-1,1)))),'top_bottom_plane_normal_separation_mm':abs(float((tri[top,0]-tri[bottom,0])@nt)),'midpoint_vertical_material_thickness_mm':a['connected_solid_chord_mm'],'local_top_slope_dZ_dY':-float(nt[1]/nt[2])})
first=r2['new_roof_warnings_with_local_evidence'][0];x=first['new_r2_warning_unchanged']['start_mm'][0]
yz,closedyz,_=section(0,x);fullclip=yz.intersection(box(-12,48,-6,56))
# The delivered STL endplane y=-7 is measured on the fixed source-X section;
# no sample is moved to claim a warning disappeared.
endsection=yz.intersection(LineString([(-7,49),(-7,53)]))
# Actual inset-body rear edge at fixed source-X is directly present as a
# vertical contour segment above the roof and below its cap in this section.
edge_candidates=[]
for poly in ([yz] if yz.geom_type=='Polygon' else yz.geoms):
    if poly.geom_type!='Polygon':continue
    c=np.asarray(poly.exterior.coords)
    for a,b in zip(c[:-1],c[1:]):
        if abs(a[0]-b[0])<1e-7 and -10<a[0]<-7 and max(a[1],b[1])>53 and min(a[1],b[1])<53:
            edge_candidates.append({'Y_mm':float(a[0]),'Z_range_mm':sorted([float(a[1]),float(b[1])]),'roof_overhang_to_Y_minus7_mm':float(-7-a[0])})

result={'r2_stl_sha256':ns['SHA'],'fixed_clerestory_XY_section_Z_mm':52.,'section_closed':closed,'strip_section_WKT':wkt.dumps(strip,rounding_precision=12,trim=True),'strip_section_area_mm2':float(strip.area),'method':'The actual r2 STL is sectioned at fixed Z=52. Its strip polygon is clipped only to known strip bounds X[-39,-5], Y[-10.5,-5.5]. Every polygon-vertex X splits the section into intervals on which all contour edges are linear. Upper/lower Y edges are evaluated at both one-sided interval endpoints; the least connected Y material width is taken across all intervals, including both flat truncated ends and both slot steps. This is a full piecewise-linear section minimum, not a shifted or sparse sampling.', 'minimum_continuous_Y_material_width_entire_strip_mm':allmin,'minimum_continuous_Y_material_width_window_slot_X_minus37_to_minus7_mm':slotmin,'explicit_original_STL_fixed_X_lines':lines,'all_piecewise_linear_X_interval_widths':bands,'new_roof_parallel_face_measurements':roof,'minimum_roof_parallel_face_normal_separation_mm':min(r['top_bottom_plane_normal_separation_mm'] for r in roof),'maximum_roof_parallel_face_normal_separation_mm':max(r['top_bottom_plane_normal_separation_mm'] for r in roof),'new_shortest_ray_fixed_X_YZ_section':{'X_mm':x,'closed':closedyz,'clip_YZ_bounds_mm':[-12,48,-6,56],'actual_STL_section_WKT':wkt.dumps(fullclip,rounding_precision=12,trim=True),'Y_minus7_endface_material_intersection_WKT':wkt.dumps(endsection,rounding_precision=12,trim=True),'Y_minus7_endface_full_Z_thickness_mm':float(endsection.length),'inset_body_rear_vertical_contour_edges':edge_candidates},'limitations':['Minimum widths are directions in a fixed section, not a global three-dimensional minimum radius or a guarantee of toolpath width.','Roof corners remain mathematically sharp. This evidence explains why a short normal ray can terminate at a thick plate side while nearby full material is 1.3mm vertically / approximately 0.95037mm normal to the slope; edge loss, extrusion, supports and real strength remain unverified.','No slicing, G-code or physical print was performed.']}
(OUT/'thin_r2_fixed_sections.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(OUT/'thin_fixed_sections_followup.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in result.items() if k.startswith('minimum_') or k.startswith('maximum_')},indent=2));print('endface',endsection.length,'body rear edges',edge_candidates)
