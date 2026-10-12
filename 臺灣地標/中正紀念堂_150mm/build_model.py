"""Photo-interpreted CKS main hall; millimeters, 150 mm maximum footprint.
Run with numpy, trimesh and manifold3d. Not a measured replica.
"""
from pathlib import Path
import numpy as np
import manifold3d as m
import trimesh
import math
OUT=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def oct_loft(rings,cy=14):
 # Each ring: circumradius, height at edge center, added corner lift.
 N=8*12; vs=[]
 for r,z,lift in rings:
  for i in range(N):
   seg=i//12;t=(i%12)/12;a=math.pi/8+seg*math.pi/4;b=a+math.pi/4
   x=r*((1-t)*math.cos(a)+t*math.cos(b));y=r*((1-t)*math.sin(a)+t*math.sin(b))
   vs.append([x,y+cy,z+lift*abs(2*t-1)**4])
 faces=[]
 for k in range(len(rings)-1):
  for i in range(N):
   j=(i+1)%N; faces.extend([[k*N+i,k*N+j,(k+1)*N+j],[k*N+i,(k+1)*N+j,(k+1)*N+i]])
 for i in range(1,N-1):faces.append([0,i+1,i]);faces.append([(len(rings)-1)*N,(len(rings)-1)*N+i,(len(rings)-1)*N+i+1])
 mesh=trimesh.Trimesh(vs,faces,process=True);mesh.fix_normals()
 return m.Manifold(m.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
def square_frustum(w0,w1,z0,z1,cy=14):
 return m.Manifold.hull_points([[x*w/2,y*w/2+cy,z] for w,z in [(w0,z0),(w1,z1)] for x in [-1,1] for y in [-1,1]])
def arch(w,h,depth,x=0,y=-25,z=23):
 r=w/2; return box(x,y,z+(h-r)/2,w,depth,h-r)+m.Manifold.cylinder(depth,r,r,64).rotate((90,0,0)).translate((x,y+depth/2,z+h-r))
# Flat common foundation, three broad terraced platforms.
parts=[box(0,0,1,150,142,2)]
for w,d,z,h in [(140,118,5.5,7),(127,107,12.5,7),(114,96,19.5,7)]:
 parts += [box(0,11,z,w,d,h),box(0,11,z+h/2-.25,w+1.2,d+1.2,.9)]
# Remove the front terrace mass so the twin stairs and central ramp read clearly.
base=m.Manifold.batch_boolean(parts,m.OpType.Add)-box(0,-47,13,93,48,23)
base += box(0,0,1,150,142,2)
parts=[base]
# Thirty robust tread bands represent 89 actual steps. Flat landing every ten.
for i in range(30):
 y0=-67+i*1.34;top=2+(i+1)*.7
 for x in [-29,29]:parts.append(box(x,y0+.67,(top+1.4)/2,28,1.36,top-1.4))
# Central sloping stone ramp and four continuous thickened parapets.
def slope_strip(x,w,y0,y1,z0,z1,thick):
 pts=[[x+dx,y,z] for dx in [-w/2,w/2] for y,z in [(y0,1.7),(y1,1.7),(y0,z0+thick),(y1,z1+thick)]]
 return m.Manifold.hull_points(pts)
parts.append(slope_strip(0,20,-67,-26,2.2,23,.8))
for x in [-45,-12,12,45]:
 parts.append(slope_strip(x,1.8,-67,-26,3.5,24,1.1))
 for i in range(8):
  t=i/7;parts.append(box(x,-67+41*t,4+21*t,2.2,2.2,4))
# Terrace balustrades kept continuous instead of very fragile open rails.
for y,w,z in [(-47.5,140,9.4),(-42.5,127,16.4),(-36.5,114,23.4)]:
 for s in [-1,1]:
  span=w/2-47
  parts.append(box(s*(47+span/2),y,z+1.0,span,1.6,2.8))
  for x in np.arange(48,w/2,7):parts.append(box(float(s*x),y,z+1.7,2,2,4.2))
for x in [-56,56]:
 parts.append(box(x,15,24.6,1.6,100,3))
 for y in np.arange(-32,62,8):parts.append(box(x,float(y),25.2,2,2,4.2))
parts.append(box(0,62,24.6,112,1.6,3))
# Tapered hall and central flat entrance bay. Recessed arch retains a closed back.
hall=square_frustum(80,65,22.7,57)
hall += box(0,-22.5,40,31,9,34)
hall -= arch(19,25,8,y=-28,z=23)
# Molded arch surround fused into the entrance bay.
frame=arch(23,27,2.4,y=-27.1,z=23)-arch(19,25,5,y=-27.1,z=23)
hall += frame
parts.append(hall)
parts += [box(0,14,57,69,69,2),box(0,-27.4,54.8,6,1.4,8)]
# Octagonal lower roof: substantial white edge, curved blue surface and rising corners.
parts += [oct_loft([(35,56.8,0),(48,60,2),(48,61.3,2),(35,67,0)]),oct_loft([(35,65.5,0),(35,72.2,0)])]
# Upper roof rises steeply to the golden crown. Closed solid geometry beneath both eaves.
parts += [oct_loft([(35,70.5,0),(43,74,2.6),(43,75.3,2.6),(35,76.3,.9),(24,80.2,.3),(13,87.5,0),(4.5,95.4,0)])]
# Simplified repeated dougong blocks along eight octagonal faces, fused inward.
for z,r in [(57.8,37.2),(70.9,33.8)]:
 for face in range(8):
  a=math.pi/8+face*math.pi/4;b=a+math.pi/4
  for t in [.16,.39,.61,.84]:
   x=r*((1-t)*math.cos(a)+t*math.cos(b));y=14+r*((1-t)*math.sin(a)+t*math.sin(b))
   parts.append(box(x,y,z,3,3,4.5).rotate((0,0,0)))
# Crown: no needle, minimum terminal diameter 2 mm.
parts += [m.Manifold.cylinder(1.8,5,4.2,48).translate((0,14,94.8)),m.Manifold.cylinder(2,3.4,3.4,48).translate((0,14,96.4)),m.Manifold.sphere(4.1,48).scale((1,1,1.2)).translate((0,14,101.8)),m.Manifold.cylinder(1.5,1.2,1,24).translate((0,14,105.8))]
result=m.Manifold.batch_boolean(parts,m.OpType.Add).simplify(.005)
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals();(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm))
print(result.status(),tm.extents,tm.is_watertight,len(tm.faces)); print('degenerate',int((tm.area_faces<1e-9).sum()))
