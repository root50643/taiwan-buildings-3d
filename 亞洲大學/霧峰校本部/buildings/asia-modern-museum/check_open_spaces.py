"""Exact delivered-triangle vertical rays, without repairing input geometry."""
from pathlib import Path
import json,numpy as np,trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False);t=m.triangles
S=2.15;BASE=3.0;CY=29.0
# Barycentric ray/triangle intersection in XY; coplanar vertical facets ignored.
def hits(x,y):
 p=np.array([x*S,(y-CY)*S]);a=t[:,0,:2];u=t[:,1,:2]-a;v=t[:,2,:2]-a;d=p-a
 det=u[:,0]*v[:,1]-u[:,1]*v[:,0];ok=np.abs(det)>1e-9
 b=np.zeros(len(t));c=b.copy();b[ok]=(d[ok,0]*v[ok,1]-d[ok,1]*v[ok,0])/det[ok];c[ok]=(u[ok,0]*d[ok,1]-u[ok,1]*d[ok,0])/det[ok]
 ok&=(b>=-1e-7)&(c>=-1e-7)&(b+c<=1+1e-7)
 z=t[:,0,2]+b*(t[:,1,2]-t[:,0,2])+c*(t[:,2,2]-t[:,0,2])
 return sorted(set(round(float(q),5) for q in z[ok]))
rows=[]
for name,x,y,expected in [('courtyard_rear',0,18,BASE+11.03*S),('courtyard_middle',0,15.5,BASE+11.03*S),('courtyard_front_with_under_eave_void',0,10,BASE+11.03*S),('solid_roof_control',0,35,BASE+17*S),('north_under_cantilever',0,50,BASE+11.03*S),('north_low_pier',0,55,BASE+11.03*S)]:
 zs=hits(x,y);top=max(zs);rows.append({'probe':name,'xy_real_m_approx':[x,y],'z_intersections_mm':zs,'top_hit_mm':top,'expected_top_hit_mm':expected,'clear_air_to_roof_mm':BASE+17*S-top,'pass':abs(top-expected)<.002})
checks={'all_vertical_probe_heights_match':all(r['pass'] for r in rows),'courtyard_not_a_solid_triangular_roof':all(r['clear_air_to_roof_mm']>12 for r in rows[:3]),'rear_court_bottom_is_2F_roof_not_ground':rows[0]['top_hit_mm']>25,'under_eave_void_in_front_of_2F_glazing':len(rows[2]['z_intersections_mm'])==4 and rows[2]['z_intersections_mm'][2]-rows[2]['z_intersections_mm'][1]>11,'solid_roof_control_present':rows[3]['pass'],'north_under_cantilever_is_open':len(rows[4]['z_intersections_mm'])==4 and rows[4]['z_intersections_mm'][2]-rows[4]['z_intersections_mm'][1]>9,'north_pier_connects_ground_to_2F':len(rows[5]['z_intersections_mm'])==2}
report={'passed':all(checks.values()),'checks':checks,'method':'Vertical intersections of original STL triangles; reported courtyard apertures are sampled, not an exhaustive indoor survey. Separate front under-eave portion and rear 2F roof terrace are preserved.','probes':rows};(R/'open-space-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
