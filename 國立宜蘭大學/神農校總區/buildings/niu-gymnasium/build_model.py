"""Original photo-and-plan based NIU gymnasium exterior miniature; millimetres.
Five tall facade window bands plus exposed lower glazing are not five gym floors.
2011 evacuation diagrams are rotated between sheets; all are aligned to this model.
"""
from pathlib import Path
import math,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];late=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cap(x,y,z,w,d,h):
 # Asymmetric arched/sawtooth roof silhouette, five profiles visible in p160.
 pts=[(-w/2,0),(w/2,0),(w/2,h*.16),(w*.22,h)]+[(w*.22-w*.72*t,h*math.sqrt(max(0,1-t*t))) for t in np.linspace(.04,1,25)]
 return CrossSection([pts]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z))
add(0,0,0,145,150,3)
# Main sports volume with a short-end office bar; low administration wing to right.
add(-23,3,2.8,84,124,57.2)
add(41,14,2.8,44,102,43.2)
add(26.5,-47,2.8,15,24,57.2)
# A real roof-to-ground light court in administration wing (no sealed inner shell).
cut(43,31,3,14,21,60)
# Deep stepped corner balconies: the fifth row is higher than the fourth-floor wing.
for z,h in [(33,8),(47,8)]:cut(27,-55,z,17,15,h)
for z in [31.2,45.2,58.5]:add(27,-54,z,18,15,1.8)
for z in [33,47]:add(27,-60,z,17,1.7,2.5)
for x in [19.5,34.5]:add(x,-60,30.5,2.2,2.7,30)
# Photo traced unequal window groups across the field-facing wall.
def fx(pixel):return -65+(pixel-25)/595*84
rows=[(50.0,5.2,[(60,88),(135,163),(173,201),(284,317),(330,359),(443,474),(490,516),(579,597)]),
      (40.0,6.0,[(60,90),(135,160),(285,317),(330,359),(489,517),(571,608)]),
      (28.7,7.4,[(100,163),(250,318),(330,395),(490,555),(572,608)]),
      (18.3,6.7,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)]),
      (9.5,5.4,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)]),
      (3.8,4.5,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)])]
for z,h,groups in rows:
 for a,b in groups:
  x=(fx(a)+fx(b))/2;w=fx(b)-fx(a)
  cut(x,-59,z,w,3.8,h)
  if w>7:late.append(box(x,-58.0,z-.2,1.1,3.2,h+.4))
# The paired mural piers remain broad unfenestrated panels. No photo textures.
for x in [fx(167),fx(322),fx(481)]:add(x,-59.5,3,1.5,1.2,57.5)
for z in [8.2,16.9,27.3,38.4,48.5,58.2]:add(-23,-59.1,z,85,1.6,1.4)
# The far/north tall hall wall: rhythm from plan piers, exact glazing partly unseen.
for floor,z in enumerate([6,19,30,41,51]):
 for x in [-57,-43,-29,-15,-1,13]:cut(x,65,z,10.0,3.2,6.1)
# Long west hall wall: broad lower glazed bays, two separated upper clerestory bands.
for y in [-49,-35,-21,-7,7,21,35,49,59]:
 for z,h in [(5,7),(19,8),(32,7),(45,8)]:cut(-65,y,z,3.6,10.0,h)
for y in [-56,-42,-28,-14,0,14,28,42,56]:add(-65,y,3,1.4,1.8,57)
# East administration face: low rows + alternating wide and narrow recess groups.
for y in [-28,-14,0,14,48,59]:
 for z,h in [(5,6),(16,6),(27,7),(37,5.5)]:cut(63,y,z,3.4,9.3,h)
# North entrance patio: open frame above a two-storey entrance, p161 photograph.
cut(41,60,25,40,24,24)
late.append(box(41,64,35.6,44,3,2.5));late.append(box(41,64,44.5,44,3,2.4))
for x in [20,41,62]:late.append(box(x,64,3,2.8,3,44))
add(41,58,16.5,42,14,2.0)
for x in [23,33,49,59]:cut(x,64,5,7.3,4.0,9.0)
# North entrance p161: broad shallow-segment arch over tall recessed glass doors.
# The arch is a genuine opening in the forward portal; its back wall is recessed.
cut(51.5,62,3,20.1,18,22.2)
r=9.0;rise=3.2;spring=14.2
archpts=[(-r,0),(r,0),(r,spring)]+[(r*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,41)[1:]]
arch=CrossSection([archpts]).extrude(6).rotate((90,0,0)).translate((51.5,68,5.0))
portal=box(51.5,64.0,3,22.5,3.8,22.4)-arch
late.append(portal)
# Back glazing is recessed over 10mm behind the arch, with stout attached mullions.
for xx in [45.4,51.5,57.6]:cut(xx,53.0,5.1,5.0,3.6,15.6)
for xx in [48.3,54.7]:late.append(box(xx,53.0,4.9,1.1,4.2,16.1))
late.append(box(51.5,53.0,10,19,4.2,1.2))
# Broad balcony over the portico with slim rectangular reliefs, not free rods.
late.append(box(41,61,24.5,44,11,2.0))
late.append(box(41,65,26.4,44,2.1,2.8))
for k in range(5):add(51.5,73.1-k*1.45,2.9,26,1.7,(k+1)*.50)
# Front/right glass vestibule is lower than the tall wall, with broad glazed bays.
add(48,-34,14.5,25,13,25)
cut(48,-41,18,21,3.8,18)
for x in [40,48,56]:late.append(box(x,-40,17.8,1.15,3.4,18.5))
late.append(box(48,-40,26.3,22,3.4,1.2))
add(48,-42,14.7,29,6,2)
for k in range(14):add(48,-64+k*1.6,2.9,27,1.9,(k+1)*.87)
# Model the roof silhouette as five connected asymmetric arched skylight strips.
for x in [-40,-28,-16,-4,16]:parts.append(cap(x,3,59.6,12.3,108,6.5))
for x,y,w,d in [(-60,57,6,7),(24,57,6,9),(29,-43,5,6)]:add(x,y,59.7,w,d,4)
# Flat-wing parapets are at z46, not falsely level with the hall at60.
for x in [20,63]:add(x,14,45.7,1.7,102,2.0)
add(41,65,45.7,45,1.7,2.0)
# Light-court wall remains 1.8mm thick above the lower roof.
for x in [35.2,50.8]:add(x,31,45.7,1.8,23,2.1)
for y in [19.8,42.2]:add(43,y,45.7,17.4,1.8,2.1)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in late:solid=solid+p
print([(p.volume(),p.bounding_box()) for p in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
