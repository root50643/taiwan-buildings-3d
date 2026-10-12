"""National Taichung Theater exterior interpretation. Units: mm.
Original analytical geometry from cited official photographs; no imported scan.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
import manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,w,d,h): return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def union(parts): return m.Manifold.batch_boolean(parts,m.OpType.Add)
def profiled_window(cx,z0,z1,width,phase=0):
    # Non-circular bottle waist, two unequal bellies and gently drifting center.
    t=np.linspace(0,1,100)
    w=width*(.42+.64*np.exp(-((t-.80-phase)/.16)**2)+.48*np.exp(-((t-.02)/.16)**2))
    c=1.8*np.sin(t*math.pi*2+phase)
    pts=[[float(c[i]+w[i]),float(z0+(z1-z0)*t[i])] for i in range(len(t))]
    pts += [[float(c[i]-w[i]),float(z0+(z1-z0)*t[i])] for i in range(len(t)-1,-1,-1)]
    # An external recess only: closed rear surface and sloping reveal.
    return m.CrossSection([pts]).extrude(5.2,12,scale_top=(1.15,1)).rotate((90,0,0)).translate((cx,-36,0))

base=box(0,0,1.5,150,116,3)
body=box(0,5,26.7,130,90,47.4) # z 3.0 to 50.4
front=[]
for x,w,p in [(-44,12.2,-.04),(-4,12,.03),(38,10.4,-.10)]:front.append(profiled_window(x,2.7,53,w,p))
front_cut=union(front)
body -= front_cut
# Facade glazing ribs are genuinely fused into the rear of the shallow relief.
ribs=[]
for x in np.arange(-61,63,4.1):ribs.append(box(float(x),-36.18,26,.72,.82,48))
for z in np.arange(8,50,5.5):ribs.append(box(0,-36.18,float(z),129,.82,.72))
body+= union(ribs)
# Left elevation has two complementary organic glazing strips.
left_cut=union([profiled_window(-21,2.7,53,11.2,-.03),profiled_window(19,2.7,53,10.5,.06)]).rotate((0,0,-90)).translate((-25,5,0))
body-=left_cut
left_ribs=[]
for y in np.arange(-37,49,4.3):left_ribs.append(box(-61.1,float(y),26,.8,.72,48))
for z in np.arange(8,50,5.5):left_ribs.append(box(-61.1,5,float(z),.8,89,.72))
body+=union(left_ribs)
# Less photographed rear is deliberately simpler, not presented as surveyed.
rear_cut=union([profiled_window(-32,3,52,10.5,.05),profiled_window(29,3,52,12,-.06)]).rotate((0,0,180)).translate((0,10,0))
body-=rear_cut
# Right side: one broad sculptural recessed bowl and low glazed entrance.
right_cut=m.Manifold.sphere(15,72).scale((.38,1,1.05)).translate((66,14,37))
body-=right_cut
body-=box(64.9,-17,9,4,24,12)
# Breathing holes: small external blind dimples, not hidden internal cavities.
pores=[]
for i in range(52):
    x=-61+((i*23.7)%122);z=7+((i*11.31)%39)
    if all(abs(x-c)>w*(.6+.7*math.exp(-((z/50-.8)/.2)**2))+1.5 for c,w in [(-44,12.2),(-4,12),(38,10.4)]):
        pores.append(m.Manifold.sphere(.68,16).scale((1,.7,1)).translate((x,-40.08,z)))
body-=union(pores)
# Rooftop organic landscape, estimated positions, solid bell-mouth volumes.
roof=[]
for x,y,r,h in [(-40,0,11,9),(2,23,12,10),(36,3,9,7),(-7,-14,8,6)]:
    # Profile flares outward at ground and at the mouth, characteristic roof funnels.
    profile=[[0,0],[r,0],[r*.83,1.5],[r*.57,h*.55],[r*.55,h],[0,h]]
    funnel=m.CrossSection([profile]).revolve(64).translate((x,y,49.5))
    # Open-top external bowl ends above roof: no enclosed void.
    bowl=m.Manifold.sphere(r*.52,48).scale((1,1,.75)).translate((x,y,49.5+h+.7))
    roof.append(funnel-bowl)
# Raised rear stagehouse only; uncertain roof equipment intentionally omitted.
roof += [box(37,34,53,42,23,6.3)]
# Shallow curved plaza / pool rim, connected entirely through flat plinth.
plaza=m.Manifold.cylinder(.7,24,24,80).scale((1.5,.43,1)).translate((-19,-45,2.8))
result=union([base,body,plaza]+roof).simplify(.006)
assert result.status()==m.Error.NoError
msh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(msh.vert_properties)[:,:3],np.asarray(msh.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm))
print('dimensions',tm.extents,'watertight',tm.is_watertight,'triangles',len(tm.faces))
