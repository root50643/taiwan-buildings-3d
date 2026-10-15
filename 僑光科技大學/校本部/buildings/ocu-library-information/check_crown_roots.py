"""Specified crown beams and both rings: original normal intervals and continuous roots.
No repair, no remote back-wall substitution; complements all-original-face samples.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);S=1.6552519477888414;ang=np.radians(-2.5);A=np.array([[np.cos(ang),-np.sin(ang),0],[np.sin(ang),np.cos(ang),0],[0,0,1.]])
def pt(p):return (A@(np.asarray(p)+[0,0,1.3]))*S
def interval(p,d):
 p=np.asarray(p);d=np.asarray(d);d/=np.linalg.norm(d);h=ray.hits(p-d*250,d);assert len(h)%2==0
 iv=[(a,b)for a,b in zip(h[::2],h[1::2])if a[0]<250<b[0]];assert len(iv)==1,(p,d,h)
 return dict(first_solid_width_mm=iv[0][1][0]-iv[0][0][0],containing_interval_faces=[iv[0][0][1],iv[0][1][1]],all_original_hits=h)
beams=[]
for t in np.linspace(0,2*np.pi,16,endpoint=False):
 a=np.array([-27+7.5*np.cos(t),-1+7.5*np.sin(t),55.7]);b=np.array([-27+13*np.cos(t),-1+13*np.sin(t),59.7]);v=b-a;L=np.linalg.norm(v);v/=L;xx=np.cross([0,1,0],v)
 if np.linalg.norm(xx)<.1:xx=np.cross([1,0,0],v)
 xx/=np.linalg.norm(xx);yy=np.cross(v,xx);sections=[]
 for f in [.1,.5,.9]:
  p=pt(a+(b-a)*f)
  for n in [xx,yy]:
   q=interval(p,A@n);assert q['first_solid_width_mm']>=1.05*S-1e-5;q.update(surface_station_fraction=f,world_point_mm=p.tolist(),normal=(A@n).tolist());sections.append(q)
 # First interval along complete beam centreline must cover both original endpoints continuously.
 start=pt(b)+(A@v)*5;h=ray.hits(start,-(A@v));assert len(h)>=2 and h[0][0]<5 and h[1][0]>5+L*S
 controls=[interval(pt(a+(b-a)*f),A@v)['first_solid_width_mm']for f in [0,.25,.5,.75,1]]
 beams.append(dict(angle_radians=t,normal_sections=sections,outer_to_inner_all_hits=h,required_cap_to_ring_length_mm=L*S,continuous_first_interval_width_mm=h[1][0]-h[0][0],five_centerline_controls_inside=True))
rings=[]
for ro,ri in [(13.4,12.55),(11.95,11.10)]:
 for t in np.linspace(0,2*np.pi,32,endpoint=False)+np.pi/32:
  p=pt([-27+(ro+ri)/2*np.cos(t),-1+(ro+ri)/2*np.sin(t),59.925]);qs=[]
  for n in [[np.cos(t),np.sin(t),0],[0,0,1]]:
   q=interval(p,A@np.array(n));expected=.85*S*(np.cos(np.pi/96) if n[2]==0 else 1);assert q['first_solid_width_mm']>=expected-1e-5;q['analytic_96gon_or_vertical_lower_bound_mm']=expected;qs.append(q)
  rings.append(dict(radii_m=[ro,ri],angle_radians=t,normal_radial_vertical_sections=qs))
webs=[]
for t in np.linspace(0,2*np.pi,16,endpoint=False):
 samples=[]
 for f in [.05,.25,.5,.75,.95]:
  ri=7.9+.9*f;ro=8.5+3.88*f;z=56.3+3.42*f;r=(ri+ro)/2
  p=pt([-27+r*np.cos(t),-1+r*np.sin(t),z]);q=interval(p,A@np.array([-np.sin(t),np.cos(t),0]));assert q['first_solid_width_mm']>=1.1*S-1e-5
  q.update(profile_fraction=f,world_point_mm=p.tolist());samples.append(q)
 p=pt([-27+12*np.cos(t),-1+12*np.sin(t),59.925]);links=[]
 for n,minimum in [([-np.sin(t),np.cos(t),0],1.1*S),([0,0,1],.85*S),([np.cos(t),np.sin(t),0],2.5*S)]:
  q=interval(p,A@np.array(n));assert q['first_solid_width_mm']>=minimum-1e-5;q['expected_mm']=minimum;links.append(q)
 webs.append(dict(angle_radians=t,backing_web_tangential_sections=samples,ring_link_three_axes=links))
checks=dict(all_sixteen_backing_webs_and_ring_links_pass=len(webs)==16,all_sixteen_beams_normal_sections_ge_nominal=len(beams)==16,all_beam_centerlines_continuous_cap_to_ring=True,both_rings_32_angles_radial_vertical_ge_analytic_96gon_bound=len(rings)==64)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),passed=all(checks.values()),checks=checks,beams=beams,rings=rings,print_only_webs_and_links=webs,limits='Finite designated crown stations and centreline roots. Does not waive short chords elsewhere or guarantee global minimum thickness or actual printing.')
(R/'crown-roots.json').write_text(json.dumps(r,indent=2));print(r['checks'])
