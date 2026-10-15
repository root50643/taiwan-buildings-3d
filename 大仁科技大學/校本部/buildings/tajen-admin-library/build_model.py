"""Original bounded Tajen Administration-Library A, metres E/N/up.
2001 official photos, 2024 northwest street image and 2016/2024 roofs.
All heights/photo window group coordinates approximate, not a measured survey.
"""
from pathlib import Path
import numpy as np,json,trimesh
from manifold3d import Manifold,OpType
R=Path(__file__).resolve().parent;S=150/62.;B=2.;parts=[]
def box(x0,x1,y0,y1,z0,z1):return Manifold.cube(((x1-x0)*S,(y1-y0)*S,(z1-z0)*S)).translate((x0*S,y0*S,B+z0*S))
def union(ps):return Manifold.batch_boolean(ps,OpType.Add)
parts.append(Manifold.cube((62*S,50*S,B)).translate((-23*S,-26*S,0)))
# Main south block with a real double-height open portico, not full-height wall.
main=box(-20,18,-23,9.5,0,25.6)
main-=box(-18.5,16.6,-24,-18,0,9.2)
# Ground glazing is recessed behind the front columns, with retained solid backs.
for x0,x1 in [(-17.3,-6.8),(-5.2,5.2),(6.8,16.0)]:
 for z0,z1 in [(.9,3.4),(6.0,8.35)]:main-=box(x0,x1,-18.1,-17.65,z0,z1)
# Four source-seen pink south window rows, narrow groups rather than square grid.
front_centres=[-14.1,-9.8,-8.1,-3.3,-1.6,3.2,4.9,12.0]
for z in [10.4,14.3,18.2,22.1]:
 for x in front_centres:main-=box(x-.38,x+.38,-23.1,-22.40,z,z+2.3)
# East long side: actual narrow vertical rhythm over four main upper rows.
for z in [10.4,14.3,18.2,22.1]:
 for y in [-17.7,-16.3,-14.9,-10.5,-9.1,-7.7,-3.3,-1.9,-.5,3.9,5.3,6.7]:
  if z<13 and -1.4<y<7.9:continue # opaque terrace core covers these locations; no sealed hidden window pockets
  main-=box(17.35,18.1,y-.39,y+.39,z,z+2.35)
# Source-visible horizontal cladding bands: shallow backed relief only.
for z in [12.95,16.85,20.75,24.65]:main-=box(17.86,18.1,-23.1,9.6,z,z+.55)
# West source shows different groups and a deep vertical glazed transition.
for z in [10.4,14.3,18.2,22.1]:
 for y in [-18.8,-14.6,-10.4,-6.2,-2.0,2.2,6.4]:main-=box(-20.1,-19.36,y-.45,y+.45,z,z+2.25)
parts.append(main)
for x in [-18,-6,6,17.2]:parts.append(box(x-.68,x+.68,-23.35,-21.45,0,9.5))
# South vertical dark structural strip grounded, as visible in 2001 photo.
parts.append(box(-18.8,-17.4,-23.55,-22.65,0,29.5))
# South upper glass terrace, set back from the four-row pink facade.
upper=box(-18,18,-19.7,9.5,25.4,31.4)
# Long continuous glazing with only shallow fine backed pane boundaries.
for x in np.arange(-15.8,16.1,1.8):upper-=box(x-.84,x+.84,-19.8,-19.53,26.5,29.6)
for y in np.arange(-17.8,8.1,1.8):upper-=box(17.83,18.1,y-.84,y+.84,26.5,29.6)
parts.append(upper)
# Roof extends only over this lower block; the high northern bar is separate.
parts.append(box(-18.3,18.3,-20,9.7,31.15,31.8))
# Broad terrace ledge/solid low parapet, rooted against main facade.
parts.append(box(-20.3,18.3,-23.3,-19.5,25.35,25.95))
parts.append(box(-20.3,-19.65,-23.3,9.6,25.35,26.55))
parts.append(box(-20.3,18.3,-23.3,-22.7,25.35,26.3))
# Northern high white bar, official 10F existence, not ten equally tall floors.
north=box(-17.5,17.5,9,20.0,0,38.0)
# North end partly obscured: omit conjectural repeated windows. Only the
# photograph-visible upper groups are retained, lower unknown wall simplified.
for z in [26.0,29.8]:
 for x in [-13.0,-8.8,-4.6]:north-=box(x-.38,x+.38,19.35,20.1,z,z+1.85)
# Northern visible band rhythm is independent of uncertain individual windows.
for z in [6.8,10.6,14.4,18.2,22.,25.8,29.6]:north-=box(-17.6,17.6,19.85,20.1,z,z+.32)
# Large east upper glazing and smaller flanking openings visible on admin02/03.
north-=box(16.8,17.6,11.1,17.4,30.7,36.0)
for y in [9.8,18.4]:north-=box(16.85,17.6,y-.32,y+.32,32.3,35.3)
# North high south wall is mostly solid, with small east-end horizontal groups.
for z in [33.,36.1]:north-=box(10.7,15.8,8.9,9.65,z,z+1.1)
# West tall glass transition and surrounding retained white wing.
north-=box(-17.6,-16.7,10.0,15.4,2.3,36.5)
for z in [7.,11.,15.,19.,23.,27.,31.,35.]:parts.append(box(-17.65,-16.55,10.0,15.4,z,z+.42))
parts.append(north);parts.append(box(-17.8,17.8,8.8,20.3,37.8,38.45))
# Roof equipment/raised services, explicitly closed, never a dark courtyard hole.
parts.append(box(-2.5,7.2,-8.8,2.8,31.65,34.4))
parts.append(box(-1.8,6.5,-8.1,2.1,34.3,34.9))
parts.append(box(3,10.5,12,17.5,38.3,39.5))
# East two-storey solid pink wing; west inner edge roots into the main block.
wing=box(17.5,37,-19,10.2,0,7.7)
for y in [-15.5,-11.5,-7.5,-3.5,.5,4.5,8]:
 for z in [1.,4.7]:wing-=box(36.3,37.1,y-.43,y+.43,z,z+2.0)
for x in [21,24,27,31,34]:
 for z in [1,4.7]:wing-=box(x-.4,x+.4,-19.1,-18.4,z,z+1.9)
# Recess/overhang on southeast corner visible beside external stairs.
wing-=box(28.4,35.1,-19.1,-17.5,1.6,6.6)
parts.append(wing);parts.append(box(17.5,37.2,-19.2,10.4,7.5,8.25))
# Thick backed parapet, omit thin source metal rails explicitly.
for p in [box(36.7,37.2,-19.2,10.4,8.1,8.85),box(17.5,37.2,9.9,10.4,8.1,8.85),box(17.5,37.2,-19.2,-18.7,8.1,8.85)]:parts.append(p)
# Source-visible east outer stair: solid steps and substantial side cheeks.
for i in range(24):
 y=-18.0+i*.56;parts.append(box(34.2,37.8,y,y+.59,0,(i+1)*.34))
parts.append(box(37.35,37.85,-18, -4.5,0,1.1))
# Raised core on eastern terrace, anchored to roof and main wall.
core=box(17.7,23.0,-1.0,7.5,7.6,13.0)
for y in [1.,3.5,6]:core-=box(22.35,23.1,y-.4,y+.4,9.0,11.7)
parts.append(core)
print('union',len(parts),flush=True);m=union(parts).to_mesh();t=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=False);t.export(R/'model.stl');print('faces',len(t.faces),'extents',t.extents,'watertight',t.is_watertight,flush=True)
(R/'parameters.json').write_text(json.dumps({'school':'大仁科技大學','building':'行政圖資大樓 A','units':'mm','scale_mm_per_m':S,'base_mm':B,'main_roof_projection_m':[36,29],'north_roof_projection_m':[35,11],'nominal_heights_m':{'south_roof':31.8,'north_roof':38.45,'north_equipment':39.5,'east_wing_roof':8.25},'height_photo_trial_bound_m':[32,42],'source_scope':'2001 completed photos; 2016/2024 roof; 2024 northwest street. Official 10F exists; unequal local floor heights approximate. B2 not fully modeled.','excluded':['activity center C','energy center','construction net','whole underground floors'],'status':'bounded visual approved; author QA complete; independent exceptions pending'},ensure_ascii=False,indent=2))
