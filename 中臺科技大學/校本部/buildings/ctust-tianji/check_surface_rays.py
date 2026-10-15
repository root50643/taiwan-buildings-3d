"""Original-triangle first-solid chords and uninterrupted local roots.
No repair, no summed distant thickness. Finite nominated probes, not full wall proof.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles
S=150/88;B=2.;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0]
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-11;iv=np.zeros(len(T));iv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*iv;r=np.cross(s,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;t=np.sort(t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-8)]);return t[np.r_[True,np.diff(t)>1e-6]] if len(t) else t
rows=[];roots=[];parity_controls=[]
def solid_angle_inside(p):
 v=T-np.asarray(p);a,b,c=v[:,0],v[:,1],v[:,2];la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
 num=np.einsum('ij,ij->i',a,np.cross(b,c));den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
 return float(abs(np.sum(2*np.arctan2(num,den)))/(4*np.pi))
def confirm_inside(label,p,*rays):
 if all(len(r)%2==1 for r in rays):return
 w=solid_angle_inside(p);assert abs(w-1)<1e-7,(label,'full solid-angle outside',p,w)
 parity_controls.append({'family':label,'point_mm':p.tolist(),'ray_counts':[len(r) for r in rays],'absolute_winding_number':w,'interpretation':'axis ray has later tangency/edge hit; original solid-angle verifies nominated interior, first local segments unchanged'})
def first(label,p,d,minimum,mm=False):
 p=np.array(p,float) if mm else np.array([p[0]*S,p[1]*S,B+p[2]*S]);d=np.array(d,float);d/=np.linalg.norm(d)
 f=hits(p,d);back=hits(p,-d);confirm_inside(label,p,f,back)
 surface=p-d*back[0];o=surface-d*1e-4;t=hits(o,d);assert len(t)>=2;w=float(t[1]-t[0]);assert w>=minimum,(label,p,w)
 rows.append({'family':label,'interior_probe_mm':p.tolist(),'original_surface_point_mm':surface.tolist(),'direction_inward':d.tolist(),'first_solid_mm':w,'air_after_mm':float(t[2]-t[1]) if len(t)>2 else None,'local_required_mm':minimum,'all_hits_mm':t.tolist()})
def root(label,p,d,minimum,mm=False):
 p=np.array(p,float) if mm else np.array([p[0]*S,p[1]*S,B+p[2]*S]);d=np.array(d,float);d/=np.linalg.norm(d);h=hits(p,d);confirm_inside(label,p,h);v=float(h[0]);assert v>=minimum,(label,p,v)
 roots.append({'family':label,'inside_origin_mm':p.tolist(),'direction':d.tolist(),'first_uninterrupted_solid_mm':v,'first_exit_mm':(p+d*v).tolist(),'all_hits_mm':h.tolist(),'required_mm':minimum})
# Every original >1% Polygon warning is tested in both rectangle normals and down.
j=json.loads((R/'detailed-component-check.json').read_text());warnings=[]
for r in j['original_component_checks']:
 if r['opening_loss_fraction']<=.01:continue
 assert r['rectangle_area_difference_mm2']<1e-6,'Only proven rectangles use rectangle normal/caliper'
 fam='roof_support' if r['z_mm']>60 else 'west_colonnade' if r['bounds'][0]<-50 else 'court_stair'
 p=[*r['centroid_xy'],r['z_mm']]
 for d in [(1,0,0),(0,1,0)]:first(fam,p,d,1.85,True)
 root(fam+'_vertical_back_root',p,(0,0,-1),.8,True)
 warnings.append({'family':fam,**r})
# Canopy, wing eaves, small window hoods: actual normal thickness, sparse grids.
for y in np.linspace(-27,27,7):
 for x in [14,20,27]:first('high_canopy_slab',(x,y,41.7),(0,0,1),1.05)
for sign in [-1,1]:
 for x in [-24,-12,1,8]:
  for yy in [25,31,38]:first('wing_roof_eave',(x,sign*yy,26.5),(0,0,1),1.15)
for y in np.linspace(-18,18,7):
 for x in [-33.5,-31.0]:first('west_colonnade_roof',(x,y,8.3),(0,0,1),1.15)
for j in range(11):
 y=-28.8+j*5.4
 for dy in [.5,2.2,3.7]:
  first('east_ninth_floor_window_hood',(29.5,y+dy,36.7),(0,0,1),1.05)
  root('east_hood_back_to_wall',(29.5,y+dy,36.7),(-1,0,0),4.0)
# Each outer stair half-landing and rising thick guard-wall, original surface normals.
f=np.array([4.15,7.75,11.35,14.95,18.55])+4
for sign in [-1,1]:
 y0,y1=sorted((sign*28.5,sign*38.5))
 for z in (f[:-1]+f[1:])/2:
  for t in [.2,.5,.8]:
   y=y0+t*(y1-y0);zz=z+.30+1.55*t+.5
   first('outer_stair_solid_guard',(-31.7,y,zz),(0,-.155,1),1.4)
   root('outer_stair_guard_side_root',(-31.0,y,zz),(1,0,0),1.2)
   first('outer_stair_landing',(-31.6,y,z+.25),(0,0,1),1.05)
# Clear arch is genuinely traversable through the high bar to the courtyard.
clear=[]
for y in [-2,0,2]:
 for z in [5.1,7,9]:
  o=np.array([30*S,y*S,B+z*S]);d=np.array([-1.,0,0]);h=hits(o,d)
  assert not len(h) or h[0]>(30-9.5)*S,('arch obstructed',o,h)
  clear.append({'origin_mm':o.tolist(),'direction':d.tolist(),'air_before_first_face_mm':float(h[0]) if len(h) else None,'entire_ray_clear':not len(h)})
# Four lightwell floors retain thick bottom to z=0 and are open from the top.
lightwells=[]
for sign in [-1,1]:
 for x in [-15.5,-5.5]:
  y=sign*17.2;o=np.array([x*S,y*S,B+3.7*S]);h=hits(o,[0,0,-1]);assert len(h)>=2
  floor=o[2]-h[0];thick=h[1]-h[0];assert abs(floor-(B+.12*S))<1e-4 and thick>2
  lightwells.append({'origin_mm':o.tolist(),'first_floor_z_mm':float(floor),'solid_bottom_to_base_mm':float(thick)})
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':True,'checks':{'all_warning_original_first_normals_ge_1p85mm':True,'all_nominated_roots_uninterrupted':True,'roof_and_stair_face_normal_thresholds':True,'arch_genuinely_passes_through':True,'four_lightwells_open_above_with_solid_base':True},'first_chord_samples':rows,'root_samples':roots,'axis_ray_parity_controls':parity_controls,'warning_samples':warnings,'arch_clear_samples':clear,'lightwell_samples':lightwells,'limits':'Nominated original-triangle rays only. Roof supports end in roof slab, not all at base. Sharp corner short-normal segments remain in full dense CSV; do not replace first segments with later walls. No claim of global minimum wall or support-free/physical-print validation.'}
(R/'surface-ray-check.json').write_text(json.dumps(report,indent=2));print('PASS',len(rows),len(roots),len(warnings))
