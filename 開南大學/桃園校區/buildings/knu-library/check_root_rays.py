"""Verify selected original-STL roof/arcade/window roots and local calipers.
Coordinates nominate expected features only; intersections use raw triangles.
Not a global minimum-wall, load-bearing or slicer/physical-print proof.
"""
from pathlib import Path
import numpy as np,trimesh,math,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=1.8;BASE=3.
def p(x,y,z):return np.array([x*S,y*S,BASE+z*S])
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;hit=t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)];assert len(hit);return float(hit.min())
def width(o,d):return ray(o,d)+ray(o,-np.array(d))
rows=[]
for name,cx,half,yf,yr,body,beam,top in [('central',0,19.8,-16.6,16.6,32.1,34.3,36.3),('west',-30.8,6.7,-20.8,18.6,27.6,28.6,30),('east',30.8,6.7,-20.8,18.6,27.6,28.6,30)]:
 for y in [yf,yr]:
  root=22.2 if half<10 and y>10.5 else body-.25;toproot=22.7 if half<10 and y>10.5 else body+.2
  for x in np.linspace(cx-half*.55,cx+half*.55,7):
   o=p(x,y,(toproot+beam)/2);down=o[2]-ray(o,[0,0,-1]);up=o[2]+ray(o,[0,0,1]);wx=width(o,[1,0,0]);wy=width(o,[0,1,0])
   assert down<=BASE+S*(toproot+.02) and up>=BASE+S*(beam+.05) and min(wx,wy)>=1.79,(name,x,y,down,up,wx,wy)
   rows.append({'group':name,'type':'header_post','origin_mm':o.tolist(),'down_exit_z_mm':down,'up_exit_z_mm':up,'x_width_mm':wx,'y_width_mm':wy})
 for sign in [-1,1]:
  outer=cx+sign*(half-.55);inner=cx+sign*(half*.77)
  for y in np.linspace(yf+1,yr-1,10):
   root=22.2 if half<10 and y>10.5 else body-.25;toproot=22.7 if half<10 and y>10.5 else body+.2
   o=p(inner,y,(toproot+top-.6)/2);down=o[2]-ray(o,[0,0,-1]);up=o[2]+ray(o,[0,0,1]);wx=width(o,[1,0,0]);wy=width(o,[0,1,0])
   assert down<=BASE+S*(toproot+.02) and up>=BASE+S*(top-.33) and min(wx,wy)>=1.79,(name,sign,y,down,up,wx,wy)
   # Same rafter traverses to the outer longitudinal beam at a common height.
   q=p(inner,y,top-.75);end=q[0]+sign*ray(q,[sign,0,0]);assert (end-outer*S)*sign>=.4*S
   rows.append({'group':name,'type':'side_frame_post_and_rafter','origin_mm':o.tolist(),'down_exit_z_mm':down,'up_exit_z_mm':up,'x_width_mm':wx,'y_width_mm':wy,'rafter_origin_mm':q.tolist(),'rafter_exit_x_mm':end})
arcade=[]
for xa,xb in [(-37,-8.3),(8.3,37)]:
 for x in np.linspace(xa+.75,xb-.75,7):
  o=p(x,-27.25,3.);down=o[2]-ray(o,[0,0,-1]);up=o[2]+ray(o,[0,0,1]);wx=width(o,[1,0,0]);wy=width(o,[0,1,0]);assert abs(down)<1e-5 and up>=BASE+5.85*S and min(wx,wy)>=1.86
  arcade.append({'origin_mm':o.tolist(),'down_exit_z_mm':down,'up_exit_z_mm':up,'x_width_mm':wx,'y_width_mm':wy})
grilles=[]
for cx in [-20,20]:
 for x,z in [(cx-2.45,13),(cx+2.45,13),(cx,11.7),(cx,15.7)]:
  o=p(x,-26.45,z);end=o[1]+ray(o,[0,1,0]);assert end>=-23.6*S
  grilles.append({'origin_mm':o.tolist(),'backward_exit_y_mm':end})
r={'passed':True,'checks':{'all_102_roof_posts_rooted':len(rows)==102,'all_60_rafters_reach_longitudinal_beams':sum(x['type']=='side_frame_post_and_rafter' for x in rows)==60,'all_14_arcade_piers_rooted':len(arcade)==14,'all_8_window_division_probes_root_into_backing':len(grilles)==8,'roof_selected_x_y_widths_ge_1p79mm':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'roof_roots':rows,'arcade_roots':arcade,'arched_window_roots':grilles,'limits':'Named feature samples only, raw original STL triangles without repair. This is not an exhaustive minimum-wall or strength/support analysis and not a physical print test.'}
(R/'root-ray-check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k not in ['roof_roots','arcade_roots','arched_window_roots']})
