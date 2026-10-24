#!/usr/bin/env python3
"""Original CYCU gymnasium whole historical exterior, circa 1989–1991.
All coordinates are normalized display mm, not architectural metric dimensions.
No source pixels or runtime network required. Every Boolean retains face evidence.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_scale_mm'];H=P['hall'];W=P['west_wing'];R=P['west_roof_edge'];M=P['monitor_groups'];E=P['entrance'];T=P['towers'];base=H['base_z'];eave=H['eave_z'];peak=H['roof_top_z'];solids=[];rules=[]
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rule(name,evidence,note,classification='source-supported organization / approximate dimensions'):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unknown closure and manufacturing',[],'Solid interiors, hidden flat roofs, generic model plinth and simplified grade; neutral does not imply a measured finish.','inferred / manufactured')
HALL=rule('Complete north–south high hall',['MPLUS-SLIDES:31–36','MPLUS-NE'],'Includes the smaller northern court/block, separate northern roof pair and break in facade rhythm; no measured scale.')
WING=rule('Unequal stepped west entrance wing',['MPLUS-SLIDES:3–7,10,23,31–36'],'Lower annex steps farther west toward south; asymmetrical, not a symmetric podium. All precise depths approximate.')
ROOF=rule('Four paired east–west monitor groups',['MPLUS-SLIDES:31,32,35,36,7,9,11,12','MPLUS-NE'],'Eight north–south triangular profiles in four groups; high glazed faces south. Pitches and subdivisions simplified; not north-light.')
EDGE=rule('Continuous raised west roof-edge plane',['MPLUS-SLIDES:5,6,7,36'],'High red-brown west plane conceals sawtooth ends in direct west elevation. Hidden joints and exact slope changes unknown.')
ENTRY=rule('Recessed west glass entry and triangular lintel',['MPLUS-SLIDES:3,6,23,33,34,36'],'Two round columns, actual recessed porch, red triangular framing and light glazing grid. Thickened for model.')
TOWER=rule('Rounded stair/transition ends and south attachment interface',['MPLUS-SLIDES:7,10,26–28,33–36'],'South rounded capsule and north west-ended capsule retained. Closed shallow south attachment interface only, no free-ended bridge.')
STAIR=rule('South external stair and design-supported north counterpart',['MPLUS-SLIDES:7,35,36','MPLUS-NE'],'South near east end; north simplified from design sheet. Solid supporting stair enclosures, not detailed engineered stairs.')
FAC=rule('Facade-specific high hall window rhythms',['MPLUS-SLIDES:7,12,15,35,36','MPLUS-NE'],'South broad upper band and largely blank lower wall; east repeated upper/lower groups and north distinct lower layout. North/east design-supported, not photographed as-built.')
LOW=rule('West wing rooftop frames and sunken edge',['MPLUS-SLIDES:3,5,6,7,10,28,31–36'],'Small roof skylight/frame volumes, lower wall bands and visible basement/retaining edge simplified. No exact ground-level reconstruction.')
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
def body(x0,x1,y0,y1,z0,z1,rr):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,1,rr,0,U)
def windows(axis,plane,lo,hi,z0,z1,rr,pitch=4.5,rows=2,outward=1,variation=False):
 # Opaque backing overlaps wall; geometry mullions connect through backing.
 d=outward
 if axis=='x':
  xx=sorted([plane-.18*d,plane+.36*d]);add(box(xx[0],xx[1],lo,hi,z0,z1,5,rr))
  for k,q in enumerate(np.arange(lo,hi-.1,pitch)):
   if variation and k%4==1 and q+pitch-.7<hi:
    xx=sorted([plane+.36*d,plane+.40*d]);add(box(xx[0],xx[1],q+.4,q+pitch-.4,z0+.4,z1-.4,6,rr))
   xx=sorted([plane+.22*d,plane+.65*d]);add(box(xx[0],xx[1],q,min(q+.55,hi),z0,z1,4,rr))
  xx=sorted([plane-.1*d,plane+.66*d])
  for z in np.linspace(z0,z1,rows+1):add(box(xx[0],xx[1],lo,hi,z-.25,z+.3,4,rr))
 else:
  yy=sorted([plane-.18*d,plane+.36*d]);add(box(lo,hi,yy[0],yy[1],z0,z1,5,rr))
  for k,q in enumerate(np.arange(lo,hi-.1,pitch)):
   if variation and k%4==1 and q+pitch-.7<hi:
    yy=sorted([plane+.36*d,plane+.40*d]);add(box(q+.4,q+pitch-.4,yy[0],yy[1],z0+.4,z1-.4,6,rr))
   yy=sorted([plane+.22*d,plane+.65*d]);add(box(q,min(q+.55,hi),yy[0],yy[1],z0,z1,4,rr))
  yy=sorted([plane-.1*d,plane+.66*d])
  for z in np.linspace(z0,z1,rows+1):add(box(lo,hi,yy[0],yy[1],z-.25,z+.3,4,rr))
# Original flat display plinth: whole building attached, no scene fragments.
add(box(-62,97,-100,94,0,base,0,U))
x0,x1=H['x'];y0,y1=H['y'];ny0,ny1=H['north_block_y'];nx=H['north_block_west_x']
add(body(x0,x1,y0,ny0,base-.1,eave,HALL),body(nx,x1,ny0,ny1,base-.1,eave,HALL))
# North block west service face differs from lower annex and main hall.
add(body(-10,nx+.1,ny0,ny1,base-.1,eave,HALL))
windows('x',-10,ny0+4,ny1-4,8,10.6,HALL,pitch=5.5,rows=1,outward=-1)
# Hall east, north, south: distinct observed/design rhythms rather than mirrored fronts.
for b0,b1,count in [(-84,40,8),(49,83,2)]:
 for j in range(count):
  lo=b0+j*(b1-b0)/count;hi=lo+(b1-b0)/count-2.6
  windows('x',x1,lo,hi,21.3,26.5,FAC,pitch=4.0,rows=2,variation=True)
  if b0<0:windows('x',x1,lo,hi,4.0,10.5,FAC,pitch=4.0,rows=2)
  else:windows('x',x1,lo+1,hi-1,4,8.2,FAC,pitch=3.5,rows=1)
add(box(x1-.2,x1+.4,ny0-1,ny0+1,base,eave,1,HALL))
for j in range(7):
 lo=8+j*10.5;windows('y',y1,lo,lo+9.2,21.4,26.8,FAC,pitch=3.1,rows=2)
for j in range(4):
 lo=15+j*12;windows('y',y1,lo,lo+10.8,4.5,11,FAC,pitch=3.5,rows=2)
windows('y',y0,7,87,21.2,26.9,FAC,pitch=4,rows=2,outward=-1,variation=True)
add(box(0,90,y0-.5,y0+.15,27.2,29.1,3,FAC))
# Narrow facade door openings near east-end escape stairs, opaque but geometrically framed.
windows('y',y0,84.5,89,12.5,17.8,STAIR,pitch=2.25,rows=1,outward=-1)
windows('y',y1,84.5,89,12.5,17.8,STAIR,pitch=2.25,rows=1)
# Four groups, two south-facing triangular shed profiles each, not independent towers.
monitor_records=[]
for gi,cy in enumerate(M['centers_y']):
 for pi,off in enumerate(M['paired_offsets_y']):
  c=cy+off;sy=c-M['profile_NS_length']/2;ey=c+M['profile_NS_length']/2;rx0,rx1=M['x']
  add(prism_x([(sy,eave-.12),(sy,peak),(ey,eave-.12)],rx0,rx1,2,ROOF))
  windows('y',sy,rx0+.4,rx1-.4,eave+.4,peak-.6,ROOF,pitch=4.6,rows=2,outward=-1)
  add(box(rx0-.15,rx1+.15,sy-.4,sy+.4,peak-.7,peak+.15,2,ROOF))
  for xx in [rx0,rx1-1.0]:add(box(xx,xx+1,sy-.4,sy+.4,eave,peak,3,ROOF))
  monitor_records.append({'group_north_to_south':gi+1,'profile_in_pair':pi+1,'x':[rx0,rx1],'y':[sy,ey],'high_glazed_side':'south','over_north_block':gi==0})
# Continuous raised west strip: sloped transverse section and nearly unbroken skyline.
rx0,rx1=R['x'];ry0,ry1=R['y'];lo,hi=R['low_z'],R['high_z']
add(prism_y([(rx0,lo-.1),(rx1,hi),(rx1+1.2,hi),(rx1+1.2,eave-.1)],ry0,ry1,2,EDGE))
add(box(rx1-.2,rx1+1.4,ry0,ry1,hi-.5,hi+.2,2,EDGE))
# Asymmetric complete low wing, with real recessed central bay.
sx0,sx1=W['spine_x'];sy0,sy1=W['spine_y'];wt=W['top_z'];add(body(sx0,sx1,sy0,sy1,base-.1,wt,WING))
for j,b in enumerate(W['steps']):
 bx0,bx1=b['x'];by0,by1=b['y'];add(body(bx0,bx1,by0,by1,base-.1,wt,WING))
 if j==2:continue
 add(box(bx0-.25,bx0+.2,by0,by1,wt-2.4,wt-.8,3,WING))
 if j==0:
  for z in [4.3,12.7,21]:windows('x',bx0,by0+1,by1-1,z,z+1.5,WING,pitch=2.9,rows=1,outward=-1)
 else:windows('x',bx0,by0+2,by1-2,5.4,11.3,WING,pitch=3.8,rows=2,outward=-1,variation=True)
 # Step return glazing faces south; visible frontage not copied onto every face.
 if j in [1,3,4]:
  windows('y',by0,bx0+1,-13.4,18.5,23,WING,pitch=3.5,rows=2,outward=-1)
  add(box(bx0,-13,by0-.35,by0+.1,23.8,25.3,3,WING))
# South low wing: full-width upper and lower bands plus exposed basement slits.
windows('y',-87,-54,-15,18.3,23.0,WING,pitch=3.3,rows=2,outward=-1,variation=True)
windows('y',-87,-46,-15,7.2,12.1,WING,pitch=3.3,rows=2,outward=-1)
for xx in np.arange(-52,-17,4.2):windows('y',-87,xx,xx+2.6,3.0,4.8,LOW,pitch=2.6,rows=1,outward=-1)
add(box(-55,-13,-87.4,-86.8,23.8,25.5,3,WING))
# North-facing low-wing return differs and is supported primarily by design elevations.
windows('y',48,-22,-13.2,18.8,23,WING,pitch=3,rows=2)
windows('y',48,-21,-17,5.2,10,WING,pitch=2,rows=1)
# Entry roof/portal: porch remains open between columns and backing glass.
front=E['front_x'];glass=E['glass_x'];ey0,ey1=E['y'];ground=E['porch_ground_z']
add(box(front-2,glass+.5,ey0-1,ey1+1,base-.1,ground,0,U))
for k in range(4):add(box(front-5+k*.9,front-1+k*.9,ey0-1,ey1+1,base-.1,base+(k+1)*(ground-base)/4,1,ENTRY))
windows('x',glass,ey0+.4,ey1-.4,ground,24.4,ENTRY,pitch=3.3,rows=4,outward=-1,variation=True)
for yy in E['column_ys']:add(cylinder(front+2,yy,E['column_radius'],ground-.1,E['column_top_z'],1,ENTRY))
for yy in [ey0,ey1-1.2]:add(box(front,front+2,yy,yy+1.2,ground-.1,26.2,3,ENTRY))
add(box(front,glass+.5,ey0,ey1,25,26.3,3,ENTRY))
for z in [16.3,24.3]:add(box(front,front+2,ey0,ey1,z,z+1.7,3,ENTRY))
points=np.linspace(ey0+1,ey1-1,5)
for j,yy in enumerate(points):add(box(front,front+2,yy-.5,yy+.5,17.5,24.8,3,ENTRY))
for j in range(4):
 a0=[front+1,points[j],24.5 if j%2==0 else 17.2];b0=[front+1,points[j+1],17.2 if j%2==0 else 24.5];add(beam(a0,b0,1.1,1.5,3,ENTRY))
# Rounded south capsule (long side connected to west spine), no detached bridge.
cx,cy=T['south_center'];rad=T['south_radius'];tower=cylinder(cx,cy,rad,base-.1,T['south_top_z'],1,TOWER)
tower=tower+body(cx-rad,cx+rad,cy,-82,base-.1,T['south_top_z'],TOWER)
for z in [14,27]:tower=tower-box(cx-rad-.2,cx-rad+1,-91,-89.7,z,z+5,5,TOWER)
add(tower)
# Attachment closure is flush/short, not a dangling half-bridge.
add(box(cx-3,cx+3,cy-rad-.25,cy-rad+.6,12.5,18.5,5,TOWER),box(cx-5,cx+5,cy-rad-.7,cy-rad+.7,11.8,12.8,3,TOWER))
# North capsule ends west, contrasting with south capsule orientation.
cx,cy=T['north_center'];rad=T['north_radius'];add(cylinder(cx,cy,rad,base-.1,T['north_top_z'],1,TOWER),body(cx,-6,cy-rad,cy+rad,base-.1,T['north_top_z'],TOWER))
windows('x',cx-rad,cy-1,cy+1,23.0,30.7,TOWER,pitch=2,rows=1,outward=-1)
# South edge triangular end frame; vertically repeated diagonal bracing at hall/wing seam.
for xx in [-2.5,5.8]:add(box(xx,xx+1.3,-88.5,-86.3,base,35,3,EDGE))
for z in [6,15,24,33]:add(box(-2.5,7.1,-88.5,-86.3,z,z+1.3,3,EDGE))
for j,z in enumerate([7.3,16.3,25.3]):add(beam([-1.8,-87.7,z if j%2==0 else z+7.4],[6.4,-87.7,z+7.4 if j%2==0 else z],1.0,1.5,3,EDGE))
add(beam([-2,-87.5,34.2],[10.5,-87.5,44],1.5,1.5,3,EDGE),box(9.4,10.8,-88.5,-86.2,33.5,44,3,EDGE),box(-2.5,10.5,-88.5,-86.3,33.5,35,3,EDGE))
# Northern end has a design-supported braced vertical return, not cloned south glazing.
for xx in [-1.5,4.8]:add(box(xx,xx+1,86.2,88.2,base,35,3,EDGE))
for z in [8,17,26,34]:add(box(-1.5,5.8,86.2,88.2,z,z+1,3,EDGE))
for j,z in enumerate([9,18,27]):add(beam([-1,87.2,z],[5.3,87.2,z+7],1.0,1.2,3,EDGE))
# Small wing roof sheds/frames: visible grouping, no interior structural claim.
for xx,yy in [(-17,35),(-18,8),(-17,-18),(-17,-45),(-17,-74),(-38,-44),(-47,-73)]:
 add(prism_x([(yy-4,wt-.1),(yy-4,wt+4),(yy+4,wt-.1)],xx-3.7,xx+3.7,2,LOW))
 add(box(xx-3.4,xx+3.4,yy-4.4,yy-3.8,wt-.1,wt+3.9,5,LOW))
 windows('y',yy-4,xx-3.3,xx+3.3,wt+.2,wt+3.5,LOW,pitch=3.3,rows=1,outward=-1)
 for zz in [wt+.1,wt+3.6]:add(box(xx-4,xx+4,yy-4.5,yy-3.7,zz,zz+.9,3,LOW))
 for xxx in [xx-4,xx+3.1]:add(box(xxx,xxx+.9,yy-4.5,yy-3.7,wt-.1,wt+4.5,3,LOW))
# Two exterior stairs near the east ends; solid supported stepped runs.
for south in [True,False]:
 yy0,yy1=(-91.5,-86.8)if south else(86.8,91.5)
 for i in range(14):
  xx=61+i*1.7;top=base+(i+1)*.78;add(box(xx,xx+1.8,yy0,yy1,base-.1,top,1,STAIR))
 add(box(84.5,90,yy0,yy1,base-.1,base+14*.78,1,STAIR))
 # Diagonal outer parapet overlaps the stair support; thickened model rail.
 out=yy0 if south else yy1-.9
 add(prism_y([(61,base-.2),(84.7,base+10.5),(90,base+10.5),(90,base+13),(84.5,base+13),(61,base+2.1)],out,out+.9,3,STAIR))
# Low retaining edging exposes basement on south/west without invented terrain.
add(box(-59,-57.7,-94,-60,base-.1,6.3,1,LOW),box(-59,-56.8,-94,-92.8,base-.1,6.3,1,LOW))
add(box(-59.2,-57.5,-94,-60,5.2,6.5,3,LOW),box(-59.2,-55.5,-94,-92.5,5.2,6.5,3,LOW))
for by0,by1,bx in [(-85,-59,-55),(-55,-30,-43),(-3,18,-31)]:
 add(box(bx-2.8,bx-1.5,by0,by1,base-.1,4.3,1,LOW),box(bx-3,bx-1.3,by0,by1,3.6,4.5,3,LOW))
# Deterministic authoritative unified model, shared by STL, Blend, color 3MF and renders.
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add).simplify(.0001);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32)*np.float32(S);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32);keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum());faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0;parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.volume,x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original source-face tags through Boolean union/difference; real per-face color, no textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_collapsed_repeated_index_triangles_removed':collapsed,'real_world_metric_scale':'UNESTABLISHED; display dimensions are normalized printing choices','complete_historical_gym_exterior':True,'small_north_block_included':True,'unequal_stepped_west_wing_included':True,'monitor_groups':monitor_records,'continuous_high_west_roof_edge':True,'south_pool_and_bridge_excluded':True,'south_gym_attachment_interface_retained':True,'north_east_design_supported_not_asbuilt_claim':True}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
