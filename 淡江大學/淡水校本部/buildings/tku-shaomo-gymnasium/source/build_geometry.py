#!/usr/bin/env python3
"""Original, source-informed whole TKU Shao-mo gym exterior. No source pixels.
Coordinates are normalized display mm; not a survey or engineering design.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_scale_mm'];solids=[];rules=[]
for n,d in [('parameters.json',P),('palette.json',palette)]:(root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rule(name,evidence,note,classification='Source-informed organization / approximate dimensions'):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unobserved closure and manufacture',[],'Rear surfaces and lower ground-contact are neutral plan-constrained approximations, not observed blank walls. Solid interior and display plinth are manufactured.','Unobserved / chosen manufacturing')
LOW=rule('Distinct lower plans and 3F front projection',['S07 physical pp2–5'],'Lower sheets separately traced. Exposed display heights are photographic choices, not floor-to-floor measurements. No B1 reconstruction.')
HALL=rule('Whole high hall and paired front corners',['S07 physical pp5,8','S08','S04 p1-08','S17 image2'],'Front and side organization retained; total exterior height unverified.')
FRONT=rule('Colonnade, recessed glass and overhanging fascia',['S04 p1-08,p2-12,p3-01','S11 image1'],'Six tall columns; recessed field, not a flat painted facade. Fine cladding seams omitted.')
GLASS=rule('Front glass corner volumes',['S08','S04 p1-08','S17 image2'],'Opaque blue-green model interpretation; no image textures or literal reflections.')
LEFT=rule('Opposite flank bands',['S04 p1-08,p2-12','S11 image1'],'Independently parameterized band heights and lower window positions; not a mirror operation.')
RIGHT=rule('Sculpture-side flank bands',['S08','S17 image2'],'Sculpture excluded. Distinct low wall, canopy, glazing and circulation tower.')
TOWER=rule('Rear lateral stair tower masses',['S07 physical pp2–5,8','S08','S04 p1-08'],'Visible lateral and front-facing glazing only. Rear surfaces neutral; stair internals not reconstructed.')
TERRACE=rule('4F terrace and asymmetric exterior stair system',['S07 physical pp4–5','S08','S04 p2-12'],'Separate traced upper terrace, long right flights, left front/rear flights and front access. Tread counts and rail forms simplified.')
PV=rule('Installed PV representative roof',['S10 after half','S11 image1','S12 image4'],'Coarse low arrays with blue access gaps. Not exposed five-strip pre-solar roof; no exact module count, tilt, equipment or electrical design.')
def mesh(v,f,ma,rr):
 v=np.array(v,np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 so=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert so.status()==mf.Error.NoError,so.status();return so

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma,rr):
 assert x1>x0 and y1>y0 and z1>z0,(x0,x1,y0,y1,z0,z1)
 return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def poly(points,z0,z1,ma,rr,topmat=None,toprule=None):
 pp=np.asarray(points,float);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-np.roll(pp[:,0],-1)*pp[:,1]);pp=pp if area>0 else pp[::-1]
 n=len(pp);v=[[x,y,z]for z in [z0,z1]for x,y in pp];cap=np.array(mf.triangulate([pp],allow_convex=False));f=cap[:,::-1].tolist()+(cap+n).tolist();mas=[ma]*len(cap)+[ma if topmat is None else topmat]*len(cap);rs=[rr]*len(cap)+[rr if toprule is None else toprule]*len(cap)
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]];mas += [ma]*2;rs += [rr]*2
 return mesh(v,f,mas,rs)
def prism_x(profile,x0,x1,ma,rr):
 # Make a y,z profile, extrude local z, then cyclic permutation to x,y,z.
 s=poly(profile,x0,x1,ma,rr);m=s.to_mesh();return mesh(m.vert_properties[:,[2,0,1]],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def prism_y(profile,y0,y1,ma,rr):
 s=poly(profile,y0,y1,ma,rr);m=s.to_mesh();return mesh(m.vert_properties[:,[0,2,1]],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def cylinder(cx,cy,r,z0,z1,ma,rr,n=48):return label(mf.Manifold.cylinder(z1-z0,r,r,n).translate((cx,cy,z0)),ma,rr)
def beam(a,b,width,depth,ma,rr):
 aa=np.array(a,float);bb=np.array(b,float);axis=bb-aa;length=np.linalg.norm(axis);axis/=length;reference=np.array([0,0,1.])if abs(axis[2])<.9 else np.array([0,1.,0]);u=np.cross(axis,reference);u/=np.linalg.norm(u);v=np.cross(axis,u)
 verts=[p+sx*u*width/2+sy*v*depth/2 for p in [aa,bb]for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 faces=[[0,3,2],[0,2,1],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
 return mesh(verts,faces,[ma]*12,[rr]*12)
def add(*s):solids.extend(s)

def window(axis,plane,lo,hi,z0,z1,rr,pitch=4.35,zpitch=4.1,outward=1,glass=2,frame=3,width=.44):
 # Supported colored relief over opaque backing, with actual material boundaries.
 d=outward
 def b(a,b,z0,z1,ma,depth):
  q=sorted([plane-.15*d,plane+depth*d])
  return box(q[0],q[1],a,b,z0,z1,ma,rr) if axis=='x' else box(a,b,q[0],q[1],z0,z1,ma,rr)
 add(b(lo,hi,z0,z1,glass,.27))
 for v in np.arange(lo,hi-.01,pitch):add(b(v,min(v+width,hi),z0,z1,frame,.48))
 add(b(hi-width,hi,z0,z1,frame,.48))
 for z in np.arange(z0,z1-1e-5,zpitch):add(b(lo,hi,z,min(z+width,z1),frame,.49))
 add(b(lo,hi,z1-width,z1,frame,.49))
def neutral_poly(points,z0,z1):return poly(points,z0,z1,0,U)
def guard(a,b,z,rr,height=None):
 # Simplified Chinese-style balustrade: open apertures, solid posts and rails.
 T=P['terrace'];height=T['guard_height']if height is None else height;v=np.array(b)-a;L=np.linalg.norm(v);v=v/L
 add(beam([*a,z+.7],[*b,z+.7],T['side_wall_thickness'],.9,6,rr),beam([*a,z+height-.5],[*b,z+height-.5],T['side_wall_thickness'],.85,1,rr))
 for t in np.linspace(0,L,max(2,int(L/T['post_pitch'])+1)):
  x,y=np.array(a)+v*t;w=T['post_width'];add(box(x-w/2,x+w/2,y-w/2,y+w/2,z-.1,z+height+.4,1,rr))
B=P['plinth'];add(neutral_poly(B['polygon'],B['bottom'],B['top']))
L=P['lower'];zs=L['levels_z']
for k,n in enumerate(['floor1_polygon','floor2_polygon','floor3_polygon']):add(neutral_poly(L[n],zs[k]-.12,zs[k+1]))
# Front projecting 3F strip has restrained neutral low facade; visible finish white.
add(box(-24,125,-27.3,-26.9,14.6,21.6,1,LOW))
for x in np.arange(-17,119,15):window('y',-27.3,x,x+9.5,16.0,20.1,LOW,pitch=3.2,zpitch=4.1,outward=-1,glass=7,width=.5)
# No invented lower windows along unseen terrain-contact elevations.
T=P['terrace'];add(poly(T['polygon'],T['slab_bottom'],T['top'],6,TERRACE))
H=P['upper'];W=H['width'];D=H['depth'];Z=H['terrace_z'];R=H['roof_surface_z'];cw=H['corner_width'];cd=H['corner_depth'];F=P['front']
add(box(0,W,H['front_glass_y'],D,Z-.1,R,0,U))
# Light side envelopes, but rear and solid hidden closure stay neutral.
for plane,sgn,rr in [(0,-1,LEFT),(W,1,RIGHT)]:
 xx=sorted([plane-.15*sgn,plane+.25*sgn]);add(box(xx[0],xx[1],cd,65.2,Z-.1,H['roof_z'],1,rr))
# Corner volumes are glass in observed front/lateral directions only.
for x0,x1 in [(0,cw),(W-cw,W)]:
 add(box(x0,x1,0,cd,Z-.1,R,0,U))
 window('y',0,x0,x1,Z,R+.5,GLASS,pitch=F['mullion_pitch_x'],zpitch=F['mullion_pitch_z'],outward=-1,width=F['mullion_width'])
 side=x0 if x0==0 else x1;direction=-1 if x0==0 else 1
 window('x',side,0,cd,Z,R+.5,GLASS,pitch=F['mullion_pitch_x'],zpitch=F['mullion_pitch_z'],outward=direction,width=F['mullion_width'])
 add(box(x0-.2,x1+.2,-.2,.8,R+.4,H['roof_z']+.2,1,GLASS))
 side0,side1=(x0-.2,x0+.8)if x0==0 else(x1-.8,x1+.2);add(box(side0,side1,0,cd,R+.4,H['roof_z']+.2,1,GLASS))
# Recessed front curtain wall, tall deep piers, and massive roof fascia.
window('y',H['front_glass_y'],cw,W-cw,*F['glass_z'],FRONT,pitch=F['mullion_pitch_x'],zpitch=F['mullion_pitch_z'],outward=-1,width=F['mullion_width'])
for x in F['column_x']:add(box(x-F['column_width']/2,x+F['column_width']/2,*F['column_y'],Z-.1,F['fascia_z'][1],1,FRONT))
add(box(cw-1,W-cw+1,*F['fascia_y'],*F['fascia_z'],1,FRONT))
# Thin fascia seam near top is geometric, not text/photo.
add(box(cw,W-cw,F['fascia_y'][0]-.12,F['fascia_y'][0]+.12,H['roof_z']-2.2,H['roof_z']-1.95,3,FRONT))
# Entry canopy projects in front of columns; opaque translucent-color simplification.
cz=F['canopy_z'];add(box(*F['canopy_x'],*F['canopy_y'],cz,cz+F['canopy_thickness'],2,FRONT))
for x in np.arange(F['canopy_x'][0],F['canopy_x'][1]+.1,F['canopy_frame_pitch']):
 add(box(x-.35,x+.35,*F['canopy_y'],cz-.55,cz+.25,3,FRONT))
 add(beam([x,F['canopy_y'][0],cz],[x,3,cz+1.8],.6,.75,3,FRONT))
for y in [-11,-4,3]:add(box(*F['canopy_x'],y-.3,y+.3,cz-.5,cz+.2,3,FRONT))
# Central doors and a plain signboard abstraction; no copied signage or font asset.
window('y',H['front_glass_y']-.3,44.5,75.5,Z,Z+10.6,FRONT,pitch=5.15,zpitch=10.6,outward=-1,glass=7,width=.55)
add(box(44.5,75.5,H['front_glass_y']-.75,H['front_glass_y']+.1,Z+10.6,Z+13.0,1,FRONT))
# Side rhythms: individually parameterized rather than mirrored windows.
for side,plane,sgn,rr in [('left',0,-1,LEFT),('right',W,1,RIGHT)]:
 Q=P['flanks'][side];lo,hi=Q['band_y']
 for z0,z1 in Q['large_bands_z']:
  # Vertical opaque breaks maintain photographed separated bands.
  for aa,bb in [(lo,lo+17),(lo+18.7,hi)]:window('x',plane,aa,bb,z0,z1,rr,pitch=4.6,zpitch=3.1,outward=sgn,width=.43)
 for zz in Q['small_rows_z']:
  for yy in Q['small_window_y']:window('x',plane,yy,yy+2.3,zz,zz+2.25,rr,pitch=2.3,zpitch=2.25,outward=sgn,width=.35)
 # Narrow entry glazing on each seen flank, not a basement facade invention.
 window('x',plane,32,47,Z,Z+9.2,rr,pitch=3.0,zpitch=9.2,outward=sgn,glass=7,width=.5)
 xx=sorted([plane-.2*sgn,plane+6.2*sgn])
 add(box(xx[0],xx[1],*Q['canopy_y'],Q['canopy_z'],Q['canopy_z']+.8,2,rr))
 for yy in np.arange(Q['canopy_y'][0],Q['canopy_y'][1]+.1,4):add(box(xx[0],xx[1],yy-.3,yy+.3,Q['canopy_z']-.45,Q['canopy_z']+.2,3,rr))
# Rear lateral glass stair volumes, with neutral unobserved back faces.
for j,Q in enumerate(P['rear_towers']):
 x0,x1,y0,y1=Q['rect'];top=Q['top'];add(box(x0,x1,y0,y1,2-.1,top,0,U))
 window('y',y0,x0,x1,Z,top-.6,TOWER,pitch=4.3,zpitch=5.2,outward=-1,glass=3,frame=1,width=.5)
 plane=x0 if j==0 else x1;sgn=-1 if j==0 else 1
 window('x',plane,y0,y1,Z,top-.6,TOWER,pitch=4.4,zpitch=5.2,outward=sgn,glass=3,frame=1,width=.5)
 # Sparse dark slabs behind opaque glass suggest circulation, not invented internal stairs.
 for zz in np.arange(Z+5.2,top-1,10.4):
  yy=sorted([y0-.51,y0-.27]);add(box(x0+.5,x1-.5,*yy,zz,zz+.7,2,TOWER))
 add(box(x0-.25,x1+.25,y0-.25,y1+.25,top-.65,top+.2,1,TOWER))
# Terrace guards are open, model-thickened; preserve entrance opening and stair access.
for aa,bb in [([-24,-27],[0,-27]),([14,-27],[139,-27]),([-26,-22],[-26,10]),([-26,13],[-26,62]),([138,-24],[138,63])]:guard(aa,bb,Z,TERRACE)
# Actual asymmetric flight masses; each supported to schematic ground.
for Q in P['stairs']:
 x0,x1=Q['cross'];a0,b0=Q['start'],Q['end'];steps=Q['steps'];z0,z1=Q['bottom'],Q['top'];pitch=(b0-a0)/steps
 landing_length=Q.get('landing_length',0)
 if landing_length:
  flight_steps=Q['landings_every'];nflights=steps//flight_steps;module=(b0-a0)/nflights;run=module-landing_length
  for j in range(nflights):
   for k in range(flight_steps):
    ya=a0+j*module+k*run/flight_steps;yb=ya+run/flight_steps+.04;top=z0+(j*flight_steps+k+1)*(z1-z0)/steps
    add(box(x0,x1,ya,yb,1.9,top,6,TERRACE))
   top=z0+(j+1)*(z1-z0)/nflights;add(box(x0,x1,a0+j*module+run,a0+(j+1)*module+.04,1.9,top,6,TERRACE))
 else:
  for k in range(steps):
   ya=a0+k*pitch;yb=a0+(k+1)*pitch+.04;top=z0+(k+1)*(z1-z0)/steps;add(box(x0,x1,ya,yb,1.9,top,6,TERRACE))
 # Sloped outer cheek is connected; no disembodied rail over air.
 side=x1-.65 if x0>0 else x0
 add(prism_x([(a0,1.9),(b0,1.9),(b0,z1+3),(a0,z0+3)],side,side+1.0,1,TERRACE))
# Small transition landing joins left outward flight to rear stair tower.
add(poly([[-39,94],[-20,94],[-20,87],[-33,87]],20.8,22,6,TERRACE))
# Blue roof basin and light outer fascia. Only roof state modeled is installed PV.
R=P['upper']['roof_surface_z'];Q=P['roof'];add(box(0,W,0,D,R-.2,R+.15,4,PV))
pw=Q['parapet_width']
for x0,x1,y0,y1 in [(0,pw,0,D),(W-pw,W,0,D),(0,W,D-pw,D)]:add(box(x0,x1,y0,y1,R-.1,H['roof_z']+.4,4,PV))
# Front parapet is already the light fascia / corner caps.
for field in Q['fields']:
 x0,x1,y0,y1=field['rect'];z=R+Q['panel_height'];add(box(x0,x1,y0,y1,R-.1,z,5,PV))
 # One 2D-unioned lattice per field avoids coplanar 3D box-intersection
 # slivers when the authoritative delivery is rounded to STL float32.
 strips=[]
 for x in np.arange(x0,x1,Q['grid_x_pitch']):strips.append(mf.CrossSection.square((min(x+Q['grid_width'],x1)-x,y1-y0)).translate((x,y0)))
 for y in np.arange(y0,y1,Q['grid_y_pitch']):strips.append(mf.CrossSection.square((x1-x0,min(y+Q['grid_width'],y1)-y)).translate((x0,y)))
 lattice=mf.CrossSection.batch_boolean(strips,mf.OpType.Add).extrude(.16).translate((0,0,z-.08));add(label(lattice,3,PV))
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add).simplify(.0001);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32)*np.float32(S);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32)
# Re-regularize in the actual float32 delivery coordinate space. Boolean
# provenance can leave sub-micron slivers whose normals invert on STL rounding.
# Three deterministic passes retain face evidence and use only 0.001 mm
# simplification tolerance (well below the smallest 0.26 mm detail).
for _ in range(3):
 rounded=mf.Manifold(mf.Mesh(np.array(vertices,dtype=np.float32,order='C',copy=True),np.array(faces,dtype=np.uint32,order='C',copy=True),face_id=np.array(tags,dtype=np.uint32,order='C',copy=True))).simplify(.001)
 assert rounded.status()==mf.Error.NoError
 mm=rounded.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32)
materials=tags%32;rule_indices=tags//32
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32);keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum());faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0;parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.volume,x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original face-evidence tags preserved through Boolean operations; per-face material colors, no textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_delivery_regularization_passes':3,'float32_regularization_tolerance_mm':.001,'float32_collapsed_repeated_index_triangles_removed':collapsed,'real_world_metric_scale':'UNESTABLISHED; normalized display model','whole_aboveground_exterior':True,'lower_levels_distinct_from_upper_plate':True,'rear_surface_status':'Neutral plan-grounded approximation; exact openings and finish unobserved','installed_pv_period':'2021–2022 publication evidence; exact capture date unknown','not_included':['B1 underground reconstruction','adjacent pool','sculpture','surveyed terrain','interiors']}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
