#!/usr/bin/env python3
"""Original complete YZU Building 6 historical exterior from public evidence.
Only approximate published 68 m tower height anchors a nominal 1:400 display.
Other dimensions, repetitions and hidden closures are explicit approximations.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_scale_mm'];T=P['tower'];B=P['teaching_bar'];SP=P['service_spine'];H=P['auditorium'];C=P['repetition_conventions']
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules=[]
def rule(name,evidence,note,classification='observed organization / approximate dimensions'):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unobserved closure / manufacture',[],'Neutral unrecorded north openings and hall east/north faces; roof closure and solid interiors; original display plinth. Not proof of a windowless building.','inferred / manufactured')
TOW=rule('Curved administrative tower',['S003','S009','S032','S039','S040','S041'],'Curved pale concrete with slender vertical windows; repeated layout conventional, no exact count claim. North not mirrored.')
SLIT=rule('Deep tower glazed slit',['S009','S040','S041'],'Real deep SW recess with glass behind floor edges, not painted stripe on a cylinder.')
CROWN=rule('Raised curved crown and projecting cap',['S003','S009','S039','S040','S041'],'Open top with taller curved crown, lower projecting plate and notch; approximate arc/plate, no closed drum.')
SPINE=rule('High attached rectangular service spine',['S009','S040','S041'],'Tall flat slab with horizontal slit rhythm distinct from curved tower. Not independent low Building 1.')
BAR=rule('Full classroom bar and top setback',['S003','S032','S039','S041','S020'],'Two lower glazed bands, top setback glazing and terrace. Solid interior; no current room program claim.')
SHADE=rule('Exterior horizontal metal shades',['S003','S032','S039'],'Horizontal shades and vertical grid, separate from opaque glass; pitch/thickness adjusted for modeling.')
PILOTI=rule('Open ground colonnade',['S032','S039','S041','S083'],'Columns, inset occupied rear and actual open longitudinal covered circulation. No safety model.')
HALL=rule('Eastern adjoining You-Xiang auditorium',['S019','S020','NLSC-2016'],'Complete broader end block, not Building 5 gate. East/north details unknown; volume/topology only.')
TERRACE=rule('Long fourth-level setback terrace',['S003','S020','S039'],'Open terrace with thickened rails; no exact railing/bay counts.')
def mesh(v,f,ma,rr):
 v=np.array(v,dtype=np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
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
def tagged_cylinder(cx,cy,r,z0,z1,n):
 angles=np.linspace(0,2*np.pi,n,endpoint=False);pts=np.c_[cx+r*np.cos(angles),cy+r*np.sin(angles)];v=[[x,y,z]for z in [z0,z1]for x,y in pts];cap=np.array(mf.triangulate([pts]));f=cap[:,::-1].tolist()+(cap+n).tolist();mas=[0]*len(cap)*2;rs=[U]*len(cap)*2
 for i in range(n):
  j=(i+1)%n;observed=not(25<math.degrees(angles[i])<155);f += [[i,j,j+n],[i,j+n,i+n]];mas += [1 if observed else 0]*2;rs += [TOW if observed else U]*2
 return mesh(v,f,mas,rs)
def arc(r0,r1,lo,hi,z0,z1,ma,rr):
 ts=np.radians(np.linspace(lo,hi,max(3,round((hi-lo)/3)+1)));pts=[(cx+r1*np.cos(t),cy+r1*np.sin(t))for t in ts]+[(cx+r0*np.cos(t),cy+r0*np.sin(t))for t in ts[::-1]];return poly(pts,z0,z1,ma,rr)
solids=[]
def add(*s):solids.extend(s)
add(box(-135,152,-39,36,0,2.5,0,U))
cx,cy,rad=T['center_x'],T['center_y'],T['radius'];tower=tagged_cylinder(cx,cy,rad,2.4,T['body_top'],T['circle_segments'])
x0,x1=T['recess_x'];yf,yb=T['recess_front_y'],T['recess_back_y'];tower=tower-box(x0,x1,yf,yb,2.49,T['body_top']+.2,3,SLIT)
# Inset windows only on observed curved sectors; no invented north mirror.
cut=[]
for angle in np.arange(-168,26,C['tower_window_angle_pitch_deg']):
 if -144<angle<-84:continue
 for z in C['tower_window_rows']:
  q=box(rad-1.1,rad+1.0,-.95,.95,z,z+6.6,4,TOW).rotate((0,0,float(angle))).translate((cx,cy,0));cut.append(q)
tower=tower-mf.Manifold.batch_boolean(cut,mf.OpType.Add);add(tower)
add(box(x0+.25,x1-.25,yb-.55,yb+.25,3,160,4,SLIT))
for z in [12,24,36,48,60,72,84,96,108,120,132,144,157]:
 add(box(x0,x1,yb-3.6,yb+.3,z,z+1.0,2,SLIT))
 for x in [x0+3.4,x0+7.2,x0+11]:add(box(x,x+.65,yb-.9,yb+.2,z-8.8,z+.5,3,SLIT))
lo,hi=T['crown_arc_degrees'];add(arc(rad-T['crown_wall'],rad,lo,hi,T['body_top']-.2,T['crown_top'],1,CROWN))
add(box(x0-2.2,x0+.2,-23.4,yb+.4,2.4,T['cap_z']+.8,1,CROWN))
add(box(cx-rad-4,cx+rad+4,-32,5,T['cap_z'],T['cap_z']+T['cap_thickness'],2,CROWN))
# High attached flat spine with distinct horizontal slit rhythm; north neutral.
sx0,sx1=SP['x'];sy0,sy1=SP['y'];sp=box(sx0,sx1,sy0,sy1,2.4,SP['top'],0,U)
add(box(sx0,sx1,sy0-.3,sy0+.3,2.4,SP['top'],5,SPINE))
for z in C['service_window_rows']:
 add(box(sx0+4,sx1-5,sy0-.65,sy0-.25,z,z+2.0,3,SPINE),box(sx0+4.4,sx1-5.4,sy0-.8,sy0-.6,z+.3,z+1.7,4,SPINE))
 for x in np.arange(sx0+7,sx1-4,4):add(box(x,x+.45,sy0-.95,sy0-.55,z,z+2,2,SPINE))
 add(box(sx0-.35,sx0+.1,-8,-2,z,z+2,3,SPINE))
for z in np.arange(8,SP['top'],5.4):add(box(sx0,sx1,sy0-.48,sy0-.25,z,z+.28,2,SPINE))
for x in [sx0+9,sx0+18]:add(box(x,x+.3,sy0-.48,sy0-.25,2.5,SP['top'],2,SPINE))
add(sp)
# Complete bar with actual open south undercroft, two glazed bands and metal grid.
bx0,bx1=B['x'];by0,by1=B['y'];bt=B['terrace_z'];top=B['top']
add(box(bx0,bx1,-7,by1,2.4,B['occupied_bottom']+.1,0,U),box(bx0,bx1,by0,by1,B['occupied_bottom'],bt,0,U))
add(box(bx0,bx1,by0-.25,by0+.25,B['occupied_bottom'],bt,1,BAR))
for z0,z1 in [(17,28),(32,43)]:
 add(box(bx0+1,bx1-1,by0-.6,by0-.2,z0,z1,4,BAR))
 for j,x in enumerate(np.arange(bx0+1.2,bx1-1,C['bar_mullion_pitch'])):
  end=min(x+C['bar_mullion_pitch']-.7,bx1-1.1)
  if end>x:add(box(x,end,by0-.73,by0-.59,z0+.7,z1-.8,6 if j%6 not in [0,5]else 4,BAR))
  add(box(x,x+.65,by0-.98,by0-.5,z0,z1,3,BAR))
 for z in [z0+3.8,z0+7.4]:add(box(bx0,bx1,by0-1.05,by0-.4,z,z+.65,3,BAR))
 for z in [z0+.6,z0+3.2,z0+5.8,z0+8.4,z1+.1]:add(box(bx0,bx1,by0-3.2,by0-.3,z,z+1.,2,SHADE))
for x in np.arange(bx0,bx1+.1,C['bar_bay_pitch']):add(box(x,x+1.15,by0-3.35,by0-.1,15.2,46,2,SHADE))
for z in [14,29.1,44.2,47]:add(box(bx0,bx1,by0-.9,by0+.35,z,z+1.0,1,BAR))
for x in np.arange(bx0+7,bx1-4,C['bar_bay_pitch']):add(box(x-1.9,x+1.9,by0-1.3,by0+2.5,2.4,14.3,1,PILOTI))
add(box(bx0,bx1,-7.45,-6.9,3,13,4,PILOTI))
for x in np.arange(bx0+2,bx1,5):add(box(x,x+.65,-7.8,-7,3,13.7,3,PILOTI))
# Top setback, open terrace and thickened canopy/rails.
setback=B['setback_front_y'];add(box(bx0,bx1,setback,by1,bt-.1,top,0,U),box(bx0,bx1,setback-.55,setback+.2,bt+.5,top-.8,4,BAR))
for x in np.arange(bx0+1,bx1,4.4):add(box(x,x+.7,setback-.95,setback+.2,bt+.3,top-.5,3,BAR))
add(box(bx0-.3,bx1+.5,setback-1.0,by1,top-.8,top+.5,1,BAR),box(bx0,bx1,by0-.4,setback+.3,bt-.5,bt+.3,1,TERRACE))
for z in [bt+1.4,bt+4.2]:add(box(bx0,bx1,by0-.2,by0+.8,z,z+1,2,TERRACE))
for x in np.arange(bx0,bx1,10):add(box(x,x+1,by0-.2,by0+.8,bt,bt+5.2,2,TERRACE))
for x in np.arange(bx0,bx1,4):add(box(x,x+1,setback-5.8,setback+.2,top-2,top-1,2,SHADE))
add(box(bx0,bx1,setback-5.8,setback-4.8,top-2,top-1,2,SHADE))
# Widened attached terminal hall, not Building-5 gate; unobserved openings omitted.
hx0,hx1=H['x'];hy0,hy1=H['y'];ht=H['top'];add(box(hx0,hx1,hy0,hy1,2.4,ht,0,U),box(hx0,hx1,hy0-.25,hy0+.25,2.5,ht,1,HALL),box(hx0-.2,hx1+.2,hy0-.5,hy1+.2,ht-.8,ht+.5,0,U))
add(box(110,128,8,28,ht-.1,top+.8,0,U))
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add).simplify(.0001);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32)*np.float32(S);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32);keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum());faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0;parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original source-face tags through Boolean union/difference; real per-face color, no textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_collapsed_repeated_index_triangles_removed':collapsed,'physical_scale_claim':'Only approximate published 68 m highest tower / nominal 1:400; all other proportions visually approximated','complete_connected_building6_exterior':True,'building1_building5_building7_excluded':True,'north_not_mirrored':True,'newer_large_PV_arrays_not_added':True,'historical_not_guaranteed_solar_free':True,'crown_notch_cap_deep_glass_slot_high_spine_retained':True}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
