#!/usr/bin/env python3
"""Original numeric whole-A exterior approximation; no reference images required."""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_mm_per_design_unit'];ZS=P['display_z_translation_design_units'];L=P['levels']
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules=[]
def rule(name,evidence,note):
 rules.append(dict(index=len(rules),name=name,evidence=evidence,note=note));return len(rules)-1
U=rule('Neutral closures and simplification',[],'Opaque interior closure, unverified fine returns, not measured or observed details.')
F1=rule('Distinct first-floor pods',['School PDF p29 lower','School p28 daytime front'],'Three individually projecting polygonal classroom volumes; not extruded into 2F.')
F2=rule('Separately registered second floor',['School PDF p30 upper'],'2F classroom wall y=0 behind 1F pod roofs; left entry wing recessed.')
F3=rule('Third-floor full high wing and attached library',['School PDF p30 lower'],'Whole connected L, not separate packages.')
F4=rule('Fourth-floor high wing',['School PDF p31 upper','School p28 front'],'Low wing is roof; upper front balcony group and rear balcony group differ.')
F5=rule('Fifth-floor high wing',['School PDF p31 lower','School p28 front'],'Asymmetric upper balcony/window groups; not sixth complete storey.')
REAR=rule('Distinct rear high facade',['Architect aerial'],'Long recessed central groups at upper storeys, small core windows, different from plaza.')
LIB=rule('Three-storey library outer and inner faces',['Architect daytime photo 1','ArchDaily photo 4','Architect aerial','School p28 side'],'Wide multistorey grass-side glazing, narrow windows and ground bands; inner face not mirrored.')
STAIR=rule('Own open end stairs',['School PDF p29-p31','Architect aerial'],'Open high free-end switchback flights/landings and library free-end stair. Steps/guards simplified and thickened.')
ROOF=rule('Plain roofs and unequal subdivided cores',['Architect aerial','Architect site plan'],'Plain neutral low roof; plan roof garden omitted due photographic conflict. Two principal unequal roof/core groups, junction subdivided.')
BASE=rule('Limited approach and display base',['School PDF p29','Architect aerial'],'Authored L-shaped display plinth below grade. No campus lawn or shared A/B basement. Local steps approximate.')
BOUND=rule('A-side connection termination',['School p29-p31','ArchDaily photo 3b'],'Stop at A exterior wall; retain recessed local aperture. No chapel bridge, distant portal or floating bridge stump.')

def mesh(v,f,ma,rr):
 v=np.array(v,np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 so=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert so.status()==mf.Error.NoError,so.status();return so

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma=1,rr=U):
 assert x1>x0 and y1>y0 and z1>z0,(x0,x1,y0,y1,z0,z1)
 return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def poly(points,z0,z1,ma=1,rr=U):
 pp=np.asarray(points,float);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-np.roll(pp[:,0],-1)*pp[:,1]);pp=pp if area>0 else pp[::-1];n=len(pp)
 v=[[x,y,z]for z in[z0,z1]for x,y in pp];cap=np.array(mf.triangulate([pp],allow_convex=False));f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def section_yz(points,x0,x1,ma=1,rr=STAIR):
 pp=np.array(points,float);n=len(pp);v=[[x,y,z]for x in[x0,x1]for y,z in pp];cap=np.array(mf.triangulate([pp],allow_convex=False));f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
solids=[]
def add(*s):solids.extend(s)
def union(s):return mf.Manifold.batch_boolean(s,mf.OpType.Add)
def glaze_y(x0,x1,y,z0,z1,sgn,rr,pitch=1.4,transom=True):
 # Nominal glass plane is y; opaque shallow slab joins recessed building back.
 add(box(x0,x1,y-.07,y+.07,z0,z1,3,rr));w=.12
 for x in np.arange(x0,x1-.001,pitch):add(box(x,min(x+w,x1),y-.13,y+.13,z0,z1,4,rr))
 for z in[z0,z1-.12]+([z0+(z1-z0)*.62]if transom else[]):add(box(x0,x1,y-.13,y+.13,z,z+.12,4,rr))
 add(box(x1-.12,x1,y-.13,y+.13,z0,z1,4,rr))
def glaze_x(y0,y1,x,z0,z1,sgn,rr,pitch=1.35,transom=True):
 add(box(x-.07,x+.07,y0,y1,z0,z1,3,rr));w=.12
 for y in np.arange(y0,y1-.001,pitch):add(box(x-.13,x+.13,y,min(y+w,y1),z0,z1,4,rr))
 for z in[z0,z1-.12]+([z0+(z1-z0)*.62]if transom else[]):add(box(x-.13,x+.13,y0,y1,z,z+.12,4,rr))
 add(box(x-.13,x+.13,y1-.12,y1,z0,z1,4,rr))
def win_y(body,x0,x1,y,z0,z1,sgn,rr,depth=.32,pitch=1.4):
 aa,bb=(y-.02,y+depth)if sgn<0 else(y-depth,y+.02);body=body-box(x0,x1,aa,bb,z0,z1,1,rr)
 glaze_y(x0,x1,y-sgn*(depth-.04),z0,z1,sgn,rr,pitch);return body
def win_x(body,y0,y1,x,z0,z1,sgn,rr,depth=.32,pitch=1.35):
 aa,bb=(x-.02,x+depth)if sgn<0 else(x-depth,x+.02);body=body-box(aa,bb,y0,y1,z0,z1,1,rr)
 glaze_x(y0,y1,x-sgn*(depth-.04),z0,z1,sgn,rr,pitch);return body

def rail_y(x0,x1,y,z,rr):
 add(box(x0,x1,y-.08,y+.08,z+.93,z+1.08,4,rr),box(x0,x1,y-.07,y+.07,z+.1,z+.22,4,rr))
 for x in np.arange(x0,x1-.001,.5):add(box(x,min(x+.13,x1),y-.07,y+.07,z-.08,z+1.06,4,rr))
def balcony(body,x0,x1,y,z0,z1,sgn,rr,depth=1.8):
 aa,bb=(y-.02,y+depth)if sgn<0 else(y-depth,y+.02);body=body-box(x0,x1,aa,bb,z0,z1,1,rr)
 # Rear glazed enclosure only: balcony remains a real open recess.
 back=y-sgn*(depth-.04);glaze_y(x0+.18,x1-.18,back,z0+.08,z1-.12,sgn,rr,1.3)
 rail_y(x0-.02,x1+.02,y-sgn*.15,z0,rr);return body

# L plinth follows occupied footprint and own stair toes, leaving the concave court open.
base=[(-4.3,4.5),(-.8,4.5),(-.8,-.9),(7.8,-.9),(7.8,-4.6),(37.3,-4.6),(37.3,-.9),(58.4,-.9),(58.4,40.0),(47.5,40.0),(47.5,37.6),(40.5,37.6),(40.5,19.6),(-4.3,19.6)]
add(poly(base,-.8,0,5,BASE))
# Floorplates/rooms are independently registered. Opaque interiors are deliberate.
for fi,q in enumerate(P['floor_outlines']):
 rr=[F1,F2,F3,F4,F5][fi];z0,z1=L[fi],L[fi+1]
 body=union([box(*rect,z0,z1,1,rr)for rect in q['rectangles']]+[poly(pp,z0,z1,1,rr)for pp in q['pods']])
 # Junction A2 stair has the tall front glazed strip. Free-end two-level
 # entry is already open in the independently traced first/second floor outlines.
 body=win_y(body,37.45,40.8,0,z0+.04,z1-.04,-1,rr,pitch=1.1)
 if fi==0:
  body=win_y(body,.55,7.9,5.5,.5,3.45,-1,F1,pitch=1.25)
  # Small rear windows and pod side glazing visible between projecting solid faces.
  for x0,x1 in[[1,4.6],[5.6,8.1],[9.8,16.8],[18,24.8],[26,29]]:body=win_y(body,x0,x1,18.7,1.05,3.1,1,REAR)
  for x0 in[8.8,18.2,27.6]:
   # Left side wall opening behind the blank projecting classroom face.
   body=win_x(body,-2.9,4.0,x0,.65,3.45,-1,F1,depth=.23,pitch=1.15)
  # Geometric pod roof surface; at 2F these projections are roofs, not enclosed rooms.
  for pp in q['pods']:add(poly(pp,4.02,4.13,2,F1))
 elif fi==1:
  for x0,x1 in P['front_window_groups']['second']:body=win_y(body,x0,x1,0,4.65,6.65,-1,F2)
  body=win_y(body,.7,7.7,5.5,5.2,6.8,-1,BOUND)
  for x0,x1 in[[.8,4.3],[5.3,8.6],[9.8,18.7],[19.8,28.5],[35.5,40.4]]:body=win_y(body,x0,x1,18.7,4.95,6.9,1,REAR)
 elif fi==2:
  for x0,x1 in P['front_window_groups']['third']:body=win_y(body,x0,x1,0,8.8,10.6,-1,F3)
  for x0,x1 in P['rear_window_groups']['small']+P['rear_window_groups']['junction']:body=win_y(body,x0,x1,18.7,8.75,10.55,1,REAR)
  for x0,x1 in P['rear_window_groups']['long_recess']:body=balcony(body,x0,x1,18.7,8.3,10.85,1,REAR,1.7)
 elif fi==3:
  for x0,x1 in P['front_window_groups']['fourth_balconies']:body=balcony(body,x0,x1,0,11.95,14.55,-1,F4)
  body=win_y(body,.7,7.7,0,12.4,14.35,-1,F4)
  for x0,x1 in P['rear_window_groups']['small']+P['rear_window_groups']['junction']:body=win_y(body,x0,x1,18.7,12.4,14.2,1,REAR)
  for x0,x1 in P['rear_window_groups']['long_recess']:body=balcony(body,x0,x1,18.7,11.98,14.55,1,REAR,1.7)
 elif fi==4:
  for x0,x1 in P['front_window_groups']['fifth_balconies']:body=balcony(body,x0,x1,0,15.6,18.15,-1,F5)
  for x0,x1 in P['front_window_groups']['fifth_windows']:body=win_y(body,x0,x1,0,16.0,17.95,-1,F5)
  for x0,x1 in P['rear_window_groups']['small']+P['rear_window_groups']['junction']:body=win_y(body,x0,x1,18.7,16.0,17.8,1,REAR)
  for x0,x1 in P['rear_window_groups']['long_recess']:body=balcony(body,x0,x1,18.7,15.63,18.15,1,REAR,1.7)
 # Narrow rear service windows extend in a distinct group, not front mirrored.
 for x0,x1 in P['rear_window_groups']['core_narrow']:body=win_y(body,x0,x1,18.7,z0+1.2,min(z1-.65,z0+2.65),1,REAR,pitch=2)
 # High end and exposed junction faces, bounded neutral/asymmetric vertical bays.
 if fi>=2:
  for yy in[1.0,3.6]:body=win_x(body,yy,yy+1.4,0,z0+1,z1-.65,-1,REAR,pitch=2)
  for yy in([1.0,4.1,7.3,11.4,15.0] if fi>=3 else []):body=win_x(body,yy,yy+1.4,41.4,z0+1,z1-.65,1,LIB,pitch=2)
 add(body)
# Opaque library shell with three distinct floor levels; complete connected wing.
low=box(41.4,57.5,0,36.7,0,11.6,1,LIB)
for i,(z0,z1) in enumerate(zip(L[:3],L[1:4])):
 if i==0:
  for y0,y1 in P['library_grass_side']['ground_y']:low=win_x(low,y0,y1,57.5,.55,3.4,1,LIB,pitch=1.25)
  low=win_x(low,*P['library_inner_side']['ground_y'],41.4,.6,3.45,-1,LIB,pitch=1.5)
 else:
  for y0,y1 in P['library_grass_side']['narrow_y']:low=win_x(low,y0,y1,57.5,z0+.75,z1-.65,1,LIB,pitch=2)
  for y0,y1 in P['library_inner_side']['narrow_y']:low=win_x(low,y0,y1,41.4,z0+.75,z1-.65,-1,LIB,pitch=2)
 # Library front return and end are their own small groups, not mirrored broad glass.
 for x0,x1 in[[42.4,44.0],[45.3,47],[48.3,49.9],[51.2,52.8],[54.1,56.4]]:low=win_y(low,x0,x1,0,z0+.7,z1-.6,-1,LIB,pitch=2)
 for x0,x1 in[[42.5,47.8],[52.2,56.5]]:low=win_y(low,x0,x1,36.7,z0+.75,z1-.6,1,LIB,pitch=1.4)
# One uninterrupted two-level wide glazing bay, not a through-wing opening.
low=win_x(low,*P['library_grass_side']['central_y'],57.5,4.65,10.95,1,LIB,pitch=1.4)
add(box(57.0,57.28,8.4,14.1,7.75,7.92,4,LIB))
# A-side bridge interface terminates exactly at y=0 wall plane, supported by own floor.
low=low-box(41.7,44.8,-.02,1.25,4.12,7.3,1,BOUND)
low=win_y(low,41.85,44.65,1.25,4.2,7.2,-1,BOUND,pitch=1.35)
add(low)
# Local recessed entry three steps only, not campus terrain or full ramp system.
for i in range(3):add(box(.6,7.9,3.7+i*.55,4.3+i*.55,0,.12*(i+1),5,BASE))
# Two principal high-roof clusters: small free-end and subdivided junction group.
def parapet(rect,z,top,rr=ROOF,th=.28):
 x0,x1,y0,y1=rect
 add(box(x0,x1,y0,y0+th,z-.04,top,1,rr),box(x0,x1,y1-th,y1,z-.04,top,1,rr),box(x0,x0+th,y0,y1,z-.04,top,1,rr),box(x1-th,x1,y0,y1,z-.04,top,1,rr))
add(box(0,41.4,0,18.7,18.79,18.88,2,ROOF),box(41.4,57.5,0,36.7,11.54,11.63,2,ROOF))
# Main parapet stops at the roof-core walls, so it cannot mask the tall glazed stair.
for rect in [[0,36.5,0,.28],[0,31.8,18.42,18.7],[0,.28,0,18.7],[41.12,41.4,5.2,10.2]]:add(box(*rect,18.81,P['high_parapet'],1,ROOF))
parapet([41.4,57.5,0,36.7],11.6,P['low_parapet'])
# Free-end lift extends continuously to its own small overrunning roof.
core=box(-3.0,.5,5.5,10.8,0,21.8,1,ROOF)
for zz in[1.4,5.5,9.3,13.0,16.6,20.0]:core=win_y(core,-2.3,-.7,5.5,zz,zz+1.0,-1,REAR,depth=.3,pitch=2)
for zz in[2.4,6.2,10.0,13.7,17.4]:core=win_x(core,6.1,6.9,-3.0,zz,zz+1.1,-1,REAR,pitch=2)
add(core);add(box(-2.72,.22,5.78,10.52,21.45,21.55,2,ROOF));parapet([-3,.5,5.5,10.8],21.5,21.8)
# Larger rear junction rooftop core contains two unequal recessed roof cells.
cr=box(31.8,41.4,10.2,18.7,18.85,22.6,1,ROOF)
cr=cr-box(32.15,37.55,10.55,18.35,22.0,22.65,1,ROOF)-box(37.9,41.05,10.55,18.35,22.0,22.65,1,ROOF)
for rect in[[32.15,37.55,10.55,18.35],[37.9,41.05,10.55,18.35]]:add(box(*rect,21.96,22.04,2,ROOF))
cr=win_y(cr,32.8,37.2,18.7,19.4,21.6,1,ROOF,pitch=1.1)
cr=win_x(cr,11.0,16.6,31.8,19.5,21.5,-1,ROOF,pitch=1.1);add(cr)
cf=box(36.5,41.4,0,5.2,18.85,21.7,1,ROOF)
cf=cf-box(36.85,41.05,.35,4.85,21.1,21.75,1,ROOF);cf=win_y(cf,37.45,40.8,0,18.85,20.9,-1,ROOF,pitch=1.1);add(cf,box(36.85,41.05,.35,4.85,21.06,21.14,2,ROOF))
# Photographed low roof is left plain; internal lift position does not prove a roof overrun.
# High free-end open switchback stair. Sloping flights, landings, guards remain open.
def flight(y0,y1,z0,z1,x0,x1,n=9):
 add(section_yz([(y0,z0-.2),(y0,z0),(y1,z1),(y1,z1-.2)],x0,x1))
 for i in range(n):
  ya=y0+(y1-y0)*i/n;yb=y0+(y1-y0)*(i+1)/n;zz=z0+(z1-z0)*(i+1)/n
  add(box(x0,x1,min(ya,yb),max(ya,yb)+.01,zz-(z1-z0)/n-.22,zz,1,STAIR))
 # Sloping outer rail is a thin solid ribbon, with foot-attached posts.
 xx=x0+.08
 add(section_yz([(y0,z0+.88),(y0,z0+1.02),(y1,z1+1.02),(y1,z1+.88)],xx,xx+.13,4,STAIR))
 for t in np.linspace(0,1,8):
  yy=y0+(y1-y0)*t;zz=z0+(z1-z0)*t;add(box(xx,xx+.13,yy-.065,yy+.065,zz-.16,zz+1.02,4,STAIR))
for i in range(5):
 z0,z1=L[i],L[i+1];mid=(z0+z1)/2
 add(box(-3.1,.2,17.45,18.7,z0-.18,z0+.08,1,STAIR),box(-3.1,.15,10.8,12.05,mid-.18,mid+.06,1,STAIR))
 flight(17.5,12.0,z0,mid,-3.1,-1.7)
 flight(12.0,17.5,mid,z1,-1.45,.1)
 rail_y(-3.1,-.02,18.55,z0,STAIR)
 # Endwall strip leaves flights visible rather than enclosing a stair box.
add(box(-3.28,-2.96,10.74,11.13,-.02,19.7,1,STAIR),box(-3.28,-3.0,18.4,18.7,0,19.7,1,STAIR))
# Library free-end stair runs across X; transform equivalent Y-flight assembly.
# Local flight solids created in temporary coordinates then rotate/translate together.
start=len(solids)
for i in range(3):
 z0,z1=L[i],L[i+1];mid=(z0+z1)/2
 add(box(-2.7,.12,0,1.0,z0-.18,z0+.06,1,STAIR),box(-2.7,.1,5.4,6.4,mid-.18,mid+.06,1,STAIR))
 flight(.95,5.45,z0,mid,-2.7,-1.45,8);flight(5.45,.95,mid,z1,-1.2,.1,8)
 rail_y(-2.7,.05,.12,z0,STAIR)
# Rotated stairs attach to library end y=36.7; x=49.1..55.5.
for k in range(start,len(solids)):solids[k]=solids[k].rotate((0,0,-90)).translate((49.1,36.7,0))
# Stair outermost narrow supports attach to plinth; no full stair-volume fill.
add(box(49.05,49.32,38.84,39.42,0,11.85,1,STAIR),box(55.2,55.5,38.84,39.42,0,11.85,1,STAIR))
result=union(solids).simplify(.00005);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.array(mm.vert_properties[:,:3],np.float32,copy=True);vertices[:,2]+=np.float32(ZS);vertices*=np.float32(S);vertices=np.round(vertices.astype(np.float64),4).astype(np.float32);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32);keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum());faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
clean=mesh(vertices,faces,materials,rule_indices).simplify(.0004).to_mesh();vertices=np.array(clean.vert_properties[:,:3],np.float32,copy=True);faces=np.array(clean.tri_verts,np.int32,copy=True);tags=np.asarray(clean.face_id,np.int32);materials=tags%32;rule_indices=tags//32
# Repair exactly collinear triangle/edge pairs without shifting actual geometry.
zero_area_retriangulations=0
for attempt in range(200):
 tri=vertices[faces].astype(float);areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;bad=np.where(areas<1e-10)[0]
 if not len(bad):break
 bi=int(bad[0]);f=faces[bi];lengths=[np.linalg.norm(vertices[f[i]]-vertices[f[(i+1)%3]])for i in range(3)];j=int(np.argmax(lengths));u,v,m=int(f[j]),int(f[(j+1)%3]),int(f[(j+2)%3]);adj=np.where(np.sum(np.isin(faces,[u,v]),axis=1)==2)[0];adj=[int(q)for q in adj if q!=bi];assert len(adj)==1
 ai=adj[0];af=faces[ai]
 for k in range(3):
  aa,bb,dd=int(af[k]),int(af[(k+1)%3]),int(af[(k+2)%3])
  if {aa,bb}=={u,v}:break
 newfaces=np.array([[aa,m,dd],[m,bb,dd]],np.int32);ma=int(materials[ai]);rr=int(rule_indices[ai]);keep=np.ones(len(faces),bool);keep[[bi,ai]]=False
 faces=np.concatenate([faces[keep],newfaces]);materials=np.r_[materials[keep],[ma,ma]];rule_indices=np.r_[rule_indices[keep],[rr,rr]];zero_area_retriangulations+=1
else:raise RuntimeError('Unresolved collinear triangles')
vertices[:,1]*=-1;faces=faces[:,::-1].copy()
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original geometry with material/evidence face tags retained through Boolean operations. No image textures.','rules':rules},ensure_ascii=False,indent=2)+'\n');np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_collapsed_repeated_index_triangles_removed':collapsed,'zero_area_triangle_edge_pairs_retessellated':zero_area_retriangulations,'physical_scale_claim':'Coarse envelope-normalized approximation only, not a surveyed scale','whole_connected_five_plus_three_storeys':True,'per_floor_outlines_separately_registered':True,'first_floor_pods_not_extruded_to_second':True,'plain_grey_low_roof':True,'own_end_stairs_open':True,'shared_basement_chapel_and_bridges_excluded':True}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
