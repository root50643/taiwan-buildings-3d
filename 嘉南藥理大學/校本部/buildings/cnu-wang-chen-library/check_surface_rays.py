"""Dense nominated-family rays against original STL triangles, never a proxy.
First solid chord from exterior avoids summing separated walls. Local probes only.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib,math
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=1.8;B=3.;e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0]
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;t=np.sort(t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]);return t[np.r_[True,np.diff(t)>1e-5]] if len(t) else t
rows=[]
def chord(f,p,d,minw):
 p=np.array([p[0]*S,p[1]*S,B+p[2]*S]);d=np.array(d,float);d/=np.linalg.norm(d)
 forward=hits(p,d);back=hits(p,-d)
 assert len(forward)%2==1 and len(back)%2==1,(f,'probe not inside nominated solid',p)
 # Start immediately outside the nearest original face, then use the first
 # entry/exit pair of this local contiguous solid, not a sum across air gaps.
 o=p-d*(back[0]+.0001);t=hits(o,d);assert len(t)>=2,(f,p,t)
 w=float(t[1]-t[0]);rows.append({'family':f,'inside_probe_mm':p.tolist(),'ray_origin_mm':o.tolist(),'direction':d.tolist(),'first_entry_mm':float(t[0]),'first_solid_chord_mm':w,'required_local_chord_mm':minw});assert w>=minw,(f,p,w,minw)

# Frontmost lower glass panes and both pier overlaps at several heights.
for north in [False,True]:
 for k in range(7 if north else 9):
  a=(23 if north else 183)+20*k;b=a+14
  for z in [1.3,6.1,10.5,14.9,19.3]:
   if not north and ((z==1.3 and k in [3,4,5]) or (z>19 and k in [0,8])):continue
   for dz in [.25,1.2,2.35]:
    for deg in [a-.7,a+1,a+4,a+7,a+10,a+13,b+.7]:
     t=math.radians(deg);rx,ry,cx,cy=(20.8,20.8,-2.5,8) if north else (26.5,28.5,0,0);d=[-math.cos(t)/rx,-math.sin(t)/ry,0]
     if not north and abs(cx+rx*math.cos(t))<12 and -31.5<cy+ry*math.sin(t)<-23.8 and z+dz<6.7:continue
     chord(('north' if north else 'south')+'_pane_and_pier_root',(cx+rx*math.cos(t),cy+ry*math.sin(t),z+dz),d,.8)
# True northern transverse beams: widths away from joins and end engagement.
for z in [27.2,31.6]:
 for x in [-19,-10,-1,8,16]:
  yend=8+math.sqrt(21.3**2-(x+2.5)**2)
  for y in np.linspace(13,yend-.4,7):chord('north_y_grid',(x,y,z+.4),[1,0,0],1.4)
for y in [18,22,26]:
 dx=math.sqrt(21.3**2-(y-8)**2)
 for x in np.linspace(-2.5-dx+.4,-2.5+dx-.4,9):chord('north_x_grid',(x,y,32),[0,1,0],1.2)
# Canopy is a backed inclined slab; face-normal first chord sampled across it.
for x in np.linspace(-11,11,9):
 for y in np.linspace(-35,-29.4,7):
  z=7.7+(y+35.3)/6.3*2.1+.3
  chord('entry_inclined_glass_slab',(x,y,z),[0,-1/3,1],1.0)
# Closed curved glass: dense nominal interior skin probes across height/angle.
for z in np.linspace(23.1,39.3,10):
 f=(z-22.4)/17.6;rx=11.8-1.3*f;ry=12-2*f;cy=-7+5*f
 for t in np.linspace(math.pi+.16,2*math.pi-.16,15):
  chord('central_curved_glass_backing',((rx-.5)*math.cos(t),cy+(ry-.5)*math.sin(t),z),[-math.cos(t)/rx,-math.sin(t)/ry,0],1.0)
roots=[]
def root(label,p,d,minimum):
 p=np.array([p[0]*S,p[1]*S,B+p[2]*S]);d=np.array(d,float);t=hits(p,d)
 assert len(t)%2==1,(label,'origin not inside',p,t)
 path=float(t[0]);assert path>=minimum,(label,p,path,minimum)
 roots.append({'family':label,'inside_origin_mm':p.tolist(),'direction':d.tolist(),'uninterrupted_solid_to_first_original_face_mm':path,'minimum_mm':minimum})
for z in [27.2,31.6]:
 for x in [-19,-10,-1,8,16]:
  for dx in [-.22,0,.22]:root('north_grid_to_retreat_wall',(x+dx,13,z+.4),[0,-1,0],4.0)
for x in [-12.3,12.3]:
 for dx in [-.3,0,.3]:
  for y in [-34.8,-34.2]:root('entry_column_down_to_base',(x+dx,y,6),[0,0,-1],13.7)
for i in range(8):
 for x in [-11,0,11]:root('entry_step_to_base',(x,-43+(i+.5)*.75,.16*(i+1)-.04),[0,0,-1],3.0)
clear=[]
for z in [24.9,29.3]:
 for k in range(7):
  t=math.radians(30+20*k);o=np.array([(-2.5+23*math.cos(t))*S,(8+23*math.sin(t))*S,B+z*S]);d=np.array([-math.cos(t),-math.sin(t),0]);h=hits(o,d);assert len(h)>0
  # The high arc's inner radius is20.5; first hit must be beyond the arc.
  distance=float(h[0]);assert distance>(23-20.4)*S,(z,k,distance)
  clear.append({'z_m_nominal':z,'bay':k,'origin_mm':o.tolist(),'direction':d.tolist(),'air_before_first_original_face_mm':distance})
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':True,'checks':{'nominated_original_surface_first_chords_meet_explicit_local_thresholds':True,'grid_wall_column_step_roots_verified':True,'north_two_upper_rows_genuinely_clear':True},'sample_count':len(rows),'samples':rows,'root_samples':roots,'upper_opening_clear_samples':clear,'limitations':'Nominated local rays, not full all-direction wall thickness. A ray may meet a nearer root/solid at overlapping parts. Does not claim strength, support-free printing or physical test.'}
(R/'surface-ray-check.json').write_text(json.dumps(report,indent=2));print('PASS',len(rows))
