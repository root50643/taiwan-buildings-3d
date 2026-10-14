"""宮燈七主棟跨來源有界外形近似。mm；非測繪。東北東軸為+X，北列為+Y。
Roof dimensions are separately digitized eaves, NOT wall-baseline measurements.
Continuous base joins seven visually separate buildings; transverse paths stay open.
"""
from pathlib import Path
import json,math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection,Mesh64
R=Path(__file__).resolve().parent
# Embedded independent roof controls make source-only rebuild reproducible.
BUILDINGS=[{'id': 'N1', 'axis_image_crop_quad_px': [[57, 86], [285, 91], [294, 169], [71, 179]], 'center_px': [176.75, 131.25], 'roof_long_px': 225.63946030636936, 'roof_short_px': 86.28268706311313, 'model_center_mm': [-53.07127804698641, 14.999014133723048], 'roof_mm': [25.303696854286912, 9.675927048637284], 'angle_deg': 0.6351821760496672, 'level': 0, 'front_sign': -1, 'cross_gable': True}, {'id': 'N3', 'axis_image_crop_quad_px': [[681, 68], [910, 73], [908, 151], [682, 158]], 'center_px': [795.25, 112.5], 'roof_long_px': 227.58147987037273, 'roof_short_px': 84.0155960983115, 'model_center_mm': [16.28864899381886, 17.10167966648796], 'roof_mm': [25.521479126350116, 9.421690566966289], 'angle_deg': 0.25184795827246637, 'level': 2, 'front_sign': -1, 'cross_gable': False}, {'id': 'N4', 'axis_image_crop_quad_px': [[987, 52], [1222, 62], [1227, 142], [999, 148]], 'center_px': [1108.75, 101.0], 'roof_long_px': 231.64580171588003, 'roof_short_px': 88.45159534449479, 'model_center_mm': [51.445216701648214, 18.391314526583773], 'roof_mm': [25.977260964142737, 9.919153111943395], 'angle_deg': -0.49498362075731817, 'level': 3, 'front_sign': -1, 'cross_gable': True}, {'id': 'S1', 'axis_image_crop_quad_px': [[75, 362], [302, 358], [302, 443], [70, 452]], 'center_px': [187.25, 403.75], 'roof_long_px': 229.60487144645845, 'roof_short_px': 87.56939094329987, 'model_center_mm': [-51.89378534863806, -15.559724942460358], 'roof_mm': [25.748386631753974, 9.82022080329027], 'angle_deg': 1.6223225874978044, 'level': 0, 'front_sign': 1, 'cross_gable': False}, {'id': 'S2', 'axis_image_crop_quad_px': [[383, 346], [611, 347], [609, 424], [380, 429]], 'center_px': [495.75, 386.5], 'roof_long_px': 228.52838581037747, 'roof_short_px': 80.04008440899565, 'model_center_mm': [-17.29792844954602, -13.625272652316637], 'roof_mm': [25.627667205433756, 8.975868092074105], 'angle_deg': 0.5014819818815615, 'level': 1, 'front_sign': 1, 'cross_gable': False}, {'id': 'S3', 'axis_image_crop_quad_px': [[690, 342], [924, 337], [930, 415], [693, 429]], 'center_px': [809.25, 380.75], 'roof_long_px': 235.7332773597102, 'roof_short_px': 82.64106881685662, 'model_center_mm': [17.85863925828333, -12.98045522226873], 'roof_mm': [26.43563931893195, 9.267548106243076], 'angle_deg': 2.3100422208024227, 'level': 2, 'front_sign': 1, 'cross_gable': False}, {'id': 'S4', 'axis_image_crop_quad_px': [[1003, 331], [1237, 327], [1236, 403], [1007, 415]], 'center_px': [1120.75, 369.0], 'roof_long_px': 231.67419023746658, 'roof_short_px': 80.050881414577, 'model_center_mm': [52.79092264261775, -11.662784821736052], 'roof_mm': [25.980444514322265, 8.977078891620398], 'angle_deg': 1.979196138339196, 'level': 3, 'front_sign': 1, 'cross_gable': False}]
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def polygon(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def place(m,b):return m.rotate((0,0,b['angle_deg'])).translate((*b['model_center_mm'],0))
def roof_skirt(L,W,E):
 # Three-ring closed solid: curved/upturned outer eaves -> raised inner rectangle.
 # Upper gable is added separately; end lower hipped slopes remain exposed.
 a=L/2;c=W/2;p=[(-a,-c),(-a+2,-c),(0,-c),(a-2,-c),(a,-c),(a,0),(a,c),(a-2,c),(0,c),(-a+2,c),(-a,c),(-a,0)];n=len(p)
 verts=[(x,y,E-.85) for x,y in p]
 verts += [(x,y,E+.55*(abs(x)/a)**8*(abs(y)/c)**4) for x,y in p]
 verts += [(x*(L-4)/L,y*(W-3.2)/W,E+.95) for x,y in p]
 verts += [(0,0,E-.85),(0,0,E+.95)];faces=[]
 for i in range(n):
  j=(i+1)%n;faces += [(3*n,j,i),(i,j,n+j),(i,n+j,n+i),(n+i,n+j,2*n+j),(n+i,2*n+j,2*n+i),(3*n+1,2*n+i,2*n+j)]
 out=Manifold(Mesh64(np.array(verts,dtype=np.float64),np.array(faces,dtype=np.uint64)))
 assert not out.is_empty();return out

def upper_gable(L,W,E):
 # Truncated 1mm ridge prevents a vanishing final printed slice.
 pp=[(-W/2,E+.80),(W/2,E+.80),(.5,E+2.65),(-.5,E+2.65)]
 return CrossSection([pp]).extrude(L).rotate((90,0,90)).translate((-L/2,0,0))
# 150mm continuous base, separate stepped garden terraces and continuous rising avenue.
add(0,0,0,150,56,1.5)
levels=[1.70,2.55,3.60,4.60];xb=[-75,-35,0,35,75]
yroad=lambda x:.023*x+1.55
for k in range(4):
 a,b=xb[k:k+2];z=levels[k]
 for side in [-1,1]:
  innera=yroad(a)+side*2.9;innerb=yroad(b)+side*2.9
  pp=[(a,innera),(b,innerb),(b,side*28),(a,side*28)]
  if side<0:pp=pp[::-1]
  parts.append(polygon(pp,1.4,z-1.4))
# Sloping exposed avenue is a solid wedge; there is no roof above it.
vs=[(-75,yroad(-75)-3,1.4),(75,yroad(75)-3,1.4),(75,yroad(75)+3,1.4),(-75,yroad(-75)+3,1.4),(-75,yroad(-75)-3,1.8),(75,yroad(75)-3,4.7),(75,yroad(75)+3,4.7),(-75,yroad(-75)+3,1.8)]
fs=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
parts.append(Manifold(Mesh64(np.array(vs,dtype=np.float64),np.array(fs,dtype=np.uint64))))
for b in BUILDINGS:
 L,W=b['roof_mm'];f=b['front_sign'];k=b['level'];cx,cy=b['model_center_mm'];floor=levels[k]+.55;E=floor+3.6
 wallL=L-3.0;wallW=W-2.0;front=f*wallW/2
 # Low individual platform is integral with stepped land, never a detached shell.
 parts.append(place(box(0,0,levels[k]-.1,L+2,W+2,.65),b))
 body=box(0,0,floor-.1,wallL,wallW,3.0)
 # Open front porch under eaves; rear is an external window wall, not another porch.
 porch=box(0,f*(wallW/2-.75),floor+.10,wallL-2.4,2.5,2.65)
 body-=porch
 parts.append(place(body,b))
 parts.append(place(roof_skirt(L,W,E),b));parts.append(place(upper_gable(L-4,W-3.2,E),b))
 # Ten main porch columns reflect approximately three bays per classroom.
 # Thickness deliberately rationalized at this 150mm group scale.
 for x in np.linspace(-wallL/2+.55,wallL/2-.55,10):
  col=Manifold.cylinder(3.05,.55,.55,circular_segments=24).translate((float(x),front,floor-.10))
  details.append(place(col,b))
 # Nine broad rear window groups; fine muntins and lantern ornament are omitted.
 for i,x in enumerate(np.linspace(-wallL/2+2.2,wallL/2-2.2,9)):
  if not (b['id']=='S3' and i in [1,2]):cuts.append(place(box(float(x),-front,floor+.65,1.55,.8,1.75),b))
  # Front wall is behind porch: recessed windows and three taller door positions.
  back=f*(wallW/2-2.0)
  cuts.append(place(box(float(x),back,floor+(.25 if i in [1,4,7] else .7),1.45,.7,2.05 if i in [1,4,7] else 1.6),b))
 # Short-end upper gable louvers, shallow relief cut into the solid triangle.
 for x in [-L/2+2,L/2-2]:cuts.append(place(box(x,0,E+1.10,.7,1.4,.65),b))
 if b['cross_gable']:
  # Observed only at N1 and N4 facing the avenue, not copied to all seven.
  pp=[(-2.4,E-.30),(2.4,E-.30),(.55,E+2.2),(-.55,E+2.2)]
  cross=CrossSection([pp]).extrude(W/2+1.0).rotate((90,0,0))
  if f>0:cross=cross.rotate((0,0,180))
  parts.append(place(cross,b))
  parts.append(place(box(0,f*(W/2-.6),floor-.1,5.8,6.0,.65),b))
  for x in [-1.95,1.95]:details.append(place(Manifold.cylinder(4.15,.55,.55,circular_segments=24).translate((x,f*(W/2+.2),floor-.1)),b))
 # Open access stair from the avenue to the front platform, never a covered link.
 start=yroad(cx)-f*3;end=cy+f*(W/2+.7);roadz=1.8+(cx+75)/150*2.9
 for j in range(4):
  y0=start+(end-start)*j/4;y1=start+(end-start)*(j+1)/4
  top=max(levels[k]+.05,roadz+(floor-roadz)*(j+1)/4)
  add(cx,(y0+y1)/2,1.4,2.2,abs(y1-y0)+.05,top-1.4)
# Small northern intermediate ancillary building from 2015 plan, not an eighth classroom.
add(-9.3,15.7,2.45,8.5,5.8,2.65);add(-9.3,15.7,4.9,9.0,6.3,.8)
# Southern toilet annex joins S3 rear, excluding neighboring garden roofs.
s3=next(b for b in BUILDINGS if b['id']=='S3');cx,cy=s3['model_center_mm'];W=s3['roof_mm'][1]
add(cx-7,cy-W/2-.4,3.5,4.3,3.4,2.8);add(cx-7,cy-W/2-.4,6.0,4.7,3.8,.65)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
print('components',[(s.volume(),s.bounding_box()) for s in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(R/'model.stl');print('mm',mesh.extents,'watertight',mesh.is_watertight)
