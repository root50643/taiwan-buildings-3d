"""東華花師教育學院四翼院落與鐸鐘蓮花亭，2011–2021歷史外觀近似。
Original miniature-mm CSG. No external mesh. Known 2026 tower-door works are not
silently added to pre-quake photographic form. Partial unseen details simplified.
"""
from pathlib import Path
import math, numpy as np, trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':[150,136,2.5],'east_main_wall_z':26.0,'side_rear_wall_z':34.0,'floor_rows_z':[4,11.7,19.4,27.1],'pavilion_roof_z':12.5,'bridge_bottom_z':10.6,'tower_top_mm':64.0}
parts=[];cuts=[];after=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def poly(pts,z,h):return CrossSection([pts]).extrude(h).translate((0,0,z))
def cyl(x,y,z,r,h,n=48):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
def gable(x,y,z,w,d,rise,along='x'):
 if along=='x':
  cs=[(-d/2,0),(d/2,0),(d/2,1.2),(.7,rise+1.2),(-.7,rise+1.2),(-d/2,1.2)]
  m=CrossSection([cs]).extrude(w).rotate((90,0,90)).translate((x-w/2,y,z))
 else:
  cs=[(-w/2,0),(w/2,0),(w/2,1.2),(.7,rise+1.2),(-.7,rise+1.2),(-w/2,1.2)]
  m=CrossSection([cs]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z))
 parts.append(m)
def hip(x,y,z,w,d,rise):
 pts=[(x+sx*w/2,y+sy*d/2,z+zz) for sx in [-1,1] for sy in [-1,1] for zz in [0,1.2]]
 if w>=d:pts += [(x+sx*(w-d)/2,y+sy*.7,z+rise+1.2) for sx in [-1,1] for sy in [-1,1]]
 else:pts += [(x+sx*.7,y+sy*(d-w)/2,z+rise+1.2) for sx in [-1,1] for sy in [-1,1]]
 parts.append(Manifold.hull_points(pts))
def beam(a,b,z,w,h):
 dx,dy=b[0]-a[0],b[1]-a[1]
 return box(0,0,z,math.hypot(dx,dy),w,h).rotate((0,0,math.degrees(math.atan2(dy,dx)))).translate(((a[0]+b[0])/2,(a[1]+b[1])/2,0))
def radial(cx,cy,r,ang,z,w,depth,h):
 a=math.radians(ang);return box(0,0,z,w,depth,h).rotate((0,0,ang-90)).translate((cx+r*math.cos(a),cy+r*math.sin(a),0))
add(0,0,0,*P['base_mm'])
# A east: lower three-storey strip with a raised central entrance gable.
add(51,0,2.4,18,96,23.6);gable(51,0,25.6,21,97,4.0,'y')
add(51,0,2.4,23,20,31.5);gable(51,0,33.5,25,23,4.5,'x')
# Two end stair/service cores, narrower glazing than the teaching-window groups.
for sy in [-1,1]:
 add(50,sy*48,2.4,20,12,31.6)
 for z in [4,11.7,19.4,27.1]:
  for off in [-3.3,3.3]:
   if sy>0 and off>0:continue
   cuts.append(box(60.05,sy*48+off,z,1.8,1.55,5.4))
# B/D north/south: two main four-storey blocks separated by a narrow linking gap.
for sy in [-1,1]:
 for x,w in [(-21,43),(28,43)]:
  add(x,sy*47,2.4,w,17,31.6)
  gable(x,sy*47,33.6,w+2,20,4.6,'x')
 # Short connective open-air floors in the split, not a filled full-height block.
 for z in [10.3,18.1,25.9]:
  add(3.5,sy*48,z,8.5,6.0,1.5)
  for side in [-1,1]:add(3.5,sy*48+side*2.5,z+1.3,8.5,1.4,1.7)
 # Two lower court-projecting teaching pods; upper setbacks differ in both XY and z.
 for x in [-12,23]:
  add(x,sy*36,2.4,22,20,16.8)
  gable(x,sy*34,18.9,24,20,2.3,'x')
  add(x,sy*40,19.0,19,12,7.8)
  gable(x,sy*40,26.4,21,13.4,2.2,'x')
  # Distinct two/three lower rows on the outward face of each protruding pod.
  for z in [4.0,11.7]:
   for xx in [x-6,x,x+6]:cuts.append(box(xx,sy*25.95,z,3.8,2.0,5.7))
  for xx in [x-5.6,x,x+5.6]:cuts.append(box(xx,sy*33.95,20.1,3.6,2.0,5.7))
 # Outer B/D elevations are broadly repetitive but omit buried ends and connections.
 for x in [-37,-30,-23,-16,-9,-2,10,17,24,31,38,45]:
  for z in [4,11.7,19.4,27.1]:cuts.append(box(x,sy*55.55,z,4.3,2.0,5.7))
 # Upper court fourth-storey windows stay on the deeper main facade.
 for x in [-36,-29,-22,-15,-8,-1,11,18,25,32,39,46]:cuts.append(box(x,sy*38.45,27.1,3.9,2.0,5.6))
 # End-facing upper gables have three narrow vents, distinct from a full window row.
 for yoff in [-2.4,0,2.4]:cuts.append(box(50.45,sy*47+yoff,35.4,1.6,1.3,2.7))
# C western back is a spine plus two outer pods and an inward middle pod, per 3F plan.
add(-43,0,2.4,12,103,31.6)
for sy in [-1,1]:
 add(-58,sy*23,2.4,29,22,31.6);hip(-58,sy*23,33.6,31,24,3.0)
 add(-45,sy*47,2.4,15,12,37.3);add(-45,sy*47,39.2,17,14,1.4)
 # Clear four-row western rear, not a fifth invented storey below the parapet.
 for y in [sy*23-7.2,sy*23,sy*23+7.2]:
  for z in [4,11.7,19.4,27.1]:cuts.append(box(-72.55,y,z,2.0,4.5,5.7))
 # Windows on upper side returns outside the spine connection.
 for side in [-1,1]:
  for x in [-66,-58,-51]:
   for z in [4,11.7,19.4,27.1]:cuts.append(box(x,sy*23+side*11.05,z,4.5,2.0,5.7))
add(-29,0,2.4,20,38,24.1)
# C courtyard upper boxes are FLAT parapets, separately from the rear outer hip roofs.
# 2017 aerial + 2020 court close-up confirm the open gap between the upper boxes.
for y in [-10,10]:
 add(-29,y,26.3,20,16,7.7);add(-29,y,33.8,20.6,16.6,1.2)
 for x in [-38.5,-19.5]:add(x,y,34.8,1.6,16.6,1.8)
 for yy in [y-7.5,y+7.5]:add(-29,yy,34.8,20.6,1.6,1.8)
# Rear spine faces in the gaps, plus slim slots on service cores.
for y in [-39,-35,-8,0,8,35,39]:
 for z in [4,11.7,19.4,27.1]:cuts.append(box(-49.05,y,z,2.0,3.8,5.7))
for sy in [-1,1]:
 for yoff in [-3.5,3.5]:
  for z in [4,11.7,19.4,27.1,35]:cuts.append(box(-52.55,sy*47+yoff,z,1.9,1.6,3.6))
# C court-facing rows: divided broad windows; plain parapet above, not another row.
for y in [-15,-10,-5,5,10,15]:
 for z in [4,11.7,19.4,27.1]:
  cuts.append(box(-18.95,y,z,2.0,4.0,5.7))
# Rounded courtyard corner staircase drums, supported solid glass relief.
for sy in [-1,1]:
 parts.append(cyl(-38,sy*37,2.4,4.3,31.7,32))
 for a in ([330,0,30] if sy<0 else [330,0,30]):cuts.append(radial(-38,sy*37,4.15,a,4.2,1.8,1.0,26.6))
# A exterior: six main bays per side, three visible rows; center is a raised glass/gable block.
for sy in [-1,1]:
 for y in [12.3,18.2,24.1,30,35.9,41.8]:
  for z in [4,11.7,19.4]:
   cuts.append(box(60.05,sy*y,z,2.0,3.7,5.8))
   after.append(box(60.55,sy*y,z,1.8,4.4,.85))
 # Courtyard has deeper gallery-like bays, with solid parapets and door backing.
 for y in [13,20,27,34]:
  for z in [4.0,11.7,19.4]:cuts.append(box(41.95,sy*y,z,3.8,4.6,5.6))
# Central entrance is genuinely open through A strip below the high gable.
cuts.append(box(51,0,2.5,26,12.4,7.3))
for y in [-6.6,0,6.6]:
 for z in [12.0,20.2,28.0]:cuts.append(box(62.55,y,z,2.0,4.5,5.3))
# Three tiny high gable vents, rendered as thick slots, not hairline cuts.
for y in [-2.5,0,2.5]:cuts.append(box(63.05,y,35.0,1.9,1.3,2.3))
for y in [-6.6,0,6.6]:
 for z in [12.0,20.2]:cuts.append(box(39.45,y,z,2.1,4.5,5.3))
# Lower east portico/pergola, interrupted only by the main canopy; stout round columns.
add(64,0,9.8,7.5,85,1.6)
for y in [-41,-31,-21,-11,11,21,31,41]:parts.append(cyl(66.6,y,2.4,1.25,7.8))
for y in np.arange(-40,42,5.8):add(64,y,11.1,8.5,1.2,1.0)
add(64,0,11.1,10.0,21,1.7);hip(64,0,12.5,11.0,22.0,2.0)
for y in [-9.0,9.0]:parts.append(cyl(67.8,y,2.4,1.5,9.1))
for i in range(3):add(69+i*.9,0,2.4,4.0,24,2.0-i*.5)
# Northeast tower: clipped square shaft, full-height corner glazing and upper glazed belt.
tx,ty=64,57
outline=[(-6,-8.5),(6,-8.5),(8.5,-6),(8.5,6),(6,8.5),(-6,8.5),(-8.5,6),(-8.5,-6)]
parts.append(poly([(tx+x,ty+y) for x,y in outline],2.4,49.0))
for a in [45,135,225,315]:cuts.append(radial(tx,ty,9.95,a,11.2,3.2,2.4,36.7))
for a in [0,90,180,270]:
 # Two inward faces below z34 are partly obscured by connecting galleries, simplify.
 cuts.append(radial(tx,ty,8.55,a,26.0,1.6,1.9,18.0))
 cuts.append(radial(tx,ty,8.55,a,45.7,8.5,1.8,4.4))
 if a in [0,90]:cuts.append(radial(tx,ty,8.55,a,15.0,2.0,1.8,2.4))
for z in [11.0,18.8,26.6,44.9,51.0]:
 ring=poly([(tx+x*1.035,ty+y*1.035) for x,y in outline],z,1.0);parts.append(ring)
# Tower connects by short raised passages at the teaching floors; gaps remain visible.
for z in [10.2,18.0,25.8]:parts.append(beam((54,49),(61,55),z,4.2,1.5))
# Open octagonal viewing pavilion with round posts and broad, blunt roof cap.
parts.append(cyl(tx,ty,51.7,10.1,1.8,8))
for a in np.arange(22.5,360,45):
 ar=math.radians(a);parts.append(cyl(tx+8.0*math.cos(ar),ty+8.0*math.sin(ar),53.3,1.4,5.6,24))
parts.append(cyl(tx,ty,58.5,10.5,1.7,8));parts.append(Manifold.cylinder(4.0,10.5,1.6,8).translate((tx,ty,60.0)))
badge_part_start=len(parts);badge_cut_start=len(cuts)
# Bell/lotus-shaped low restaurant body; twin curved lobes face east, stem extends west.
badge=CrossSection.circle(9.6,48).translate((3,6)) + CrossSection.circle(9.6,48).translate((3,-6))
badge+=CrossSection([[(-19,-6),(-16,-8.5),(4,-8.5),(4,8.5),(-16,8.5),(-19,6)]])
parts.append(badge.extrude(8.8).translate((0,0,2.4)))
parts.append(badge.offset(.55).extrude(1.5).translate((0,0,11.0)))
# Backed glazing pockets around exposed lobes, fine muntins omitted for print scale.
for cy in [-6,6]:
 for a in ([-55,-25,5,35] if cy<0 else [-5,25,55,85]):
  cuts.append(radial(3,cy,9.55,a,3.6,3.1,1.5,6.1))
# Roof terrace low solid guard, cut at bridge junctions for true passage.
guard=badge.offset(.43)-badge.offset(-1.2)
guard3=guard.extrude(1.8).translate((0,0,12.3))
guard3-=box(-9,0,12.2,8.2,42,2.2);parts.append(guard3)
# N-S raised walkway intersects badge stem; outside restaurant it is open beneath.
add(-9,0,10.6,7.6,83,1.9)
for y in [-36,-24,24,36]:
 for x in [-11.4,-6.6]:parts.append(cyl(x,y,2.4,1.2,8.4))
for x in [-12.1,-5.9]:
 for sy in [-1,1]:add(x,sy*28.4,12.3,1.5,27.0,1.8)
# 1F plan confirms the emblem rotates 45 degrees: bell stem southwest, lobes north/east.
# The raised bridge therefore runs northwest-southeast, not due north-south.
parts[badge_part_start:]=[p.rotate((0,0,45)).translate((12,0,0)) for p in parts[badge_part_start:]]
cuts[badge_cut_start:]=[c.rotate((0,0,45)).translate((12,0,0)) for c in cuts[badge_cut_start:]]
# Northwest bend joins the D gallery, as the new 1F source shows.
nwx=12+(-9-41.5)/math.sqrt(2);nwy=(-9+41.5)/math.sqrt(2)
parts.append(beam((nwx,nwy),(nwx,38.5),10.6,7.6,1.9))
for y in [27,35]:
 for x in [nwx-2.4,nwx+2.4]:parts.append(cyl(x,y,2.4,1.2,8.4))
for x in [nwx-3.1,nwx+3.1]:add(x,(nwy+38.5)/2,12.25,1.5,38.5-nwy+1,1.8)
# Integral principal cornices follow the actual different-height wings.
for z in [10.1,17.9,25.7]:add(51,0,z,18.7,96.5,.75)
for sy in [-1,1]:
 for x,w in [(-21,43),(28,43)]:
  for z in [10.1,17.9,25.7,33.5]:add(x,sy*47,z,w+.6,17.6,.75)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in after:solid+=p
assert str(solid.status())=='Error.NoError',solid.status()
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight:
 e,c=np.unique(np.sort(mesh.edges,axis=1),axis=0,return_counts=True);print('BAD',len(mesh.faces),[(mesh.vertices[q].tolist(),int(n)) for q,n in zip(e[c!=2],c[c!=2])][:25])
assert len(mesh.faces)>0 and mesh.is_watertight
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
