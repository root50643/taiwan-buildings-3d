"""Check actual entry depth,54 open roof-frame cells and closed skylight.
Original STL triangle intersections only; no proxy mesh or repair.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=1.8;BASE=3.
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;hit=t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)];return float(hit.min()) if len(hit) else None
entry=[]
for x in [-3,0,3]:
 o=[x*S,-32.6*S,BASE+2*S];hit=ray(o,[0,1,0]);assert hit is not None
 depth_from_front=hit-.1*S;assert 9.5*S<depth_from_front<10.5*S
 entry.append({'origin_mm':o,'front_plane_y_mm':-32.5*S,'first_back_hit_y_mm':o[1]+hit,'entry_depth_from_front_mm':depth_from_front,'nominal_real_depth_m':depth_from_front/S})
slots=[]
for name,cx,half,yf,yr,top in [('central',0,19.8,-16.6,16.6,36.3),('west',-30.8,6.7,-20.8,18.6,30.),('east',30.8,6.7,-20.8,18.6,30.)]:
 ys=np.linspace(yf+1,yr-1,10)
 for sign in [-1,1]:
  inner=cx+sign*half*.77;outer=cx+sign*(half-.55);x=inner
  for ya,yb in zip(ys[:-1],ys[1:]):
   y=(ya+yb)/2;o=[x*S,y*S,BASE+(top-.8)*S];hit=ray(o,[0,0,1]);assert hit is None,(name,o,hit)
   slots.append({'group':name,'origin_mm':o,'upward_hit':hit})
skylight=[]
for x,y in [(0,0),(-4,3),(4,3)]:
 o=[x*S,y*S,BASE+40*S];hit=ray(o,[0,0,-1]);assert hit is not None;z=o[2]-hit;assert abs(z-(BASE+32.903*S))<.02
 skylight.append({'origin_mm':o,'surface_z_mm':z})
r={'passed':True,'checks':{'three_entry_depth_rays_between_9p5_and_10p5_nominal_metres':True,'all_54_roof_slot_upward_rays_clear':len(slots)==54,'skylight_is_closed_at_expected_height':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'entry_depth_rays':entry,'roof_slot_rays':slots,'skylight_rays':skylight,'limits':'Only nominated spaces/locations tested. Nominal real metres use approximate model scale, not a building measurement. Not a complete visibility/support or slicer analysis.'}
(R/'open-space-check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k not in ['entry_depth_rays','roof_slot_rays','skylight_rays']})
