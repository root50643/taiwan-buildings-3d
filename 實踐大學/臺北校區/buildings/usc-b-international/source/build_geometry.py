#!/usr/bin/env python3
"""Original bounded whole 2018 Building B exterior; dimensionless plan ratios.
No source images, measured scale or individual rooflight profiles are embedded.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_main_length_mm']/1000;L=P['levels'];C=P['repetition_conventions'];ZSHIFT=P['display_z_translation_design_units']
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules=[]
def rule(name,evidence,note,classification='observed organization / approximate proportions'):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unverified closure and model simplification',[],'Neutral west closures, opaque room filling and unverified rooflight curb profiles. Not a measured or observed finish.','inferred / model simplification')
TOP=rule('Third-floor overhanging rectangle',['AD01','AD02','AD07','AD18','AD22','AD23'],'Three above-ground levels; upper body overhangs north/south, continuous window bands on north/south/east. No mirrored west glazing.')
F1=rule('First-floor separately traced volumes',['AD20','AD01','AD03','AD18'],'West rooms, small north meeting volume, southern services and separate eastern glazed pod; circulation between pod and core remains open.')
F2=rule('Second-floor separately traced volumes',['AD21','AD01','AD02','AD07'],'West rooms recessed behind north corridor; distinct larger east block, south services and projecting landing; not an extrusion of 1F.')
COL=rule('North colonnade and structural frame',['AD01','AD18','AD20','AD21'],'Actual modeled north entry and longitudinal open colonnade; column repetition is simplified.')
STAIR=rule('North exterior stair and lift',['AD01','AD20','AD21','AD22'],'Separate lift shaft and open stair flights/landings; step count and guard widths simplified. No continuous solid stair-core box.')
SCREEN=rule('South low black canopy and screen',['AD02','AD03','AD17','AD20'],'Low metal fascia and vertical open bars; not a fourth storey or full added solid wall. Fine bars thickened.')
PLAT=rule('Own raised platform and steps',['AD01','AD03','AD07','AD17','AD18','AD20'],'Trace-based platform with northeast rounded corner, north/east stairs, southern strip and limited southwest descending entry edge. No lawn or neighboring ramps.')
ROOF=rule('Four unequal rooflight footprints',['AD19'],'One long western and three shorter eastern strips; shallow neutral planar abstraction only. Individual raised/sloped profiles unverified; unlocated AD23 section is not assigned to a strip.','observed footprints / simplified unverified profiles')
WEST=rule('Bounded west end and small third-floor landing',['AD19','AD20','AD21','AD22','AD06'],'Stop at B west wall; retain only own shallow west platform and small 3F landing/stair. No L block, glass connector or invented long bridge.')

def mesh(v,f,ma,rr):
 v=np.array(v,dtype=np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 so=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert so.status()==mf.Error.NoError,so.status();return so

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma,rr):
 assert x1>x0 and y1>y0 and z1>z0,(x0,x1,y0,y1,z0,z1)
 return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def poly(points,z0,z1,ma,rr):
 pp=np.asarray(points,float);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-np.roll(pp[:,0],-1)*pp[:,1]);pp=pp if area>0 else pp[::-1]
 n=len(pp);v=[[x,y,z]for z in [z0,z1]for x,y in pp];cap=np.array(mf.triangulate([pp],allow_convex=False));f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def section_xz(points,y0,y1,ma,rr):
 # Extrude a profile in XZ along Y; orientation checked by signed mesh volume.
 pp=np.array(points,float);n=len(pp);cap=np.array(mf.triangulate([pp],allow_convex=False));v=[[x,y,z]for y in[y0,y1]for x,z in pp];f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def section_yz(points,x0,x1,ma,rr):
 q=section_xz(points,0,x1-x0,ma,rr);return q.rotate((0,0,90)).translate((x1,0,0))
solids=[]
def add(*s):solids.extend(s)
def glaze_y(x0,x1,y,z0,z1,facing,rr,pitch=None,frame=None):
 # Glass slab intersects the mass; projecting dark mullions remain true geometry.
 pitch=pitch or C['lower_mullion_pitch'];w=frame or C['lower_frame_width'];a,b=(y-1.5,y+2)if facing<0 else(y-2,y+1.5);add(box(x0,x1,a,b,z0,z1,4,rr))
 aa,bb=(y-3,y+.5)if facing<0 else(y-.5,y+3)
 for x in np.arange(x0,x1,pitch):add(box(x,min(x+w,x1),aa,bb,z0-.8,z1+.8,6,rr))
 add(box(x0,x1,aa,bb,z0-1,z0+1.2,6,rr),box(x0,x1,aa,bb,z1-1.2,z1+1,6,rr))
def glaze_x(y0,y1,x,z0,z1,facing,rr,pitch=None,frame=None):
 pitch=pitch or C['lower_mullion_pitch'];w=frame or C['lower_frame_width'];a,b=(x-1.5,x+2)if facing<0 else(x-2,x+1.5);add(box(a,b,y0,y1,z0,z1,4,rr))
 aa,bb=(x-3,x+.5)if facing<0 else(x-.5,x+3)
 for y in np.arange(y0,y1,pitch):add(box(aa,bb,y,min(y+w,y1),z0-.8,z1+.8,6,rr))
 add(box(aa,bb,y0,y1,z0-1,z0+1.2,6,rr),box(aa,bb,y0,y1,z1-1.2,z1+1,6,rr))
# Trace-based platform: not the platform bounding rectangle.
T=P['platform'];cx,cy=T['northeast_corner_center'];rad=T['northeast_corner_radius'];arc=[(cx+rad*math.cos(t),cy+rad*math.sin(t))for t in np.linspace(-math.pi/2,0,T['corner_segments']+1)]
outline=[(-30,0),(355,0),(355,T['north_y'])]+arc+[(T['east_x'],T['flat_south_y']),(140,T['flat_south_y']),(140,430),(-35,430),(-35,345),(-30,345)]
plat=poly(outline,T['bottom_z'],L['first'],2,PLAT)
# Notch step entries before adding treads, rather than covering them with flat fill.
plat=plat-box(740,935,-36,11,-28,1,2,PLAT)-box(990,1051,430,521,-28,1,2,PLAT)
# Circular shallow tree wells are geometric relief only; trees are excluded.
for x,y,rr in [(180,475,14),(315,475,14),(700,470,14)]:
 cut=label(mf.Manifold.cylinder(8,rr,rr,32).translate((x,y,-5)),2,PLAT);plat=plat-cut
add(plat)
for i in range(7):
 add(box(740,935,-35+i*45/7,-35+(i+1)*45/7+.3,-29,-28+(i+1)*4,2,PLAT))
 add(box(990+i*60/7,990+(i+1)*60/7+.3,430,520,-29,-(i)*4,2,PLAT))
# B-side limited southwest descending edge, no underground rooms or deep foundations.
for i in range(7):add(box(-28,125,430+i*15,430+(i+1)*15+.3,-30,-4*i,2,PLAT))
add(box(-35,-28,425,535,-30,10,2,PLAT),box(125,140,425,535,-30,10,2,PLAT))
# Low benches / short parapets visible on own south/east platform; no campus furniture.
add(box(285,545,510,520,-.2,12,2,PLAT),box(1015,1030,260,405,-.2,12,2,PLAT))
# First-floor solids remain independent in plan; interiors are intentionally opaque.
for q in P['floor1_blocks']:
 if q['id']=='east_glazed_pod':continue
 add(poly(q['polygon'],0,L['second']-10,1,F1)if'polygon'in q else box(*q['rect'],0,L['second']-10,1,F1))
# Glazed pod: opaque glass body with real concrete edge frame, connected to platform.
add(box(815,935,65,333,0,L['second']-10,4,F1))
for x in [815,928]:add(box(x,x+7,65,333,0,7,1,F1))
glaze_x(73,325,935,3,94,1,F1);glaze_x(73,325,815,3,94,-1,F1);glaze_y(822,928,65,3,94,-1,F1);glaze_y(822,928,333,3,94,1,F1)
for y in [65,333]:add(box(815,935,y-2,y+2,78,81,6,F1))
for x in [815,935]:add(box(x-2,x+2,65,333,78,81,6,F1))
# 1F observed glazing groups, solid false interiors disclosed.
for x0,x1 in [(13,105),(126,222),(244,340),(362,455),(476,574)]:glaze_y(x0,x1,65,8,94,-1,F1)
glaze_y(15,100,333,35,88,1,F1);glaze_y(245,455,333,6,94,1,F1);glaze_y(120,225,395,42,87,1,F1);glaze_y(480,570,400,55,82,1,F1)
# Second-floor floorplate is not the first-floor footprint.
add(poly(P['floor2_slab_polygon'],L['second']-10,L['second'],1,F2))
for q in P['floor2_blocks']:add(box(*q['rect'],L['second'],L['third']-8,1,F2))
for x0,x1 in [(14,105),(126,222),(244,340),(362,455)]:
 glaze_y(x0,x1,130,145,207,-1,F2);glaze_y(x0,x1,333,145,207,1,F2)
 add(box(x0,x1,126.5,131,175,178,6,F2),box(x0,x1,332,336.5,175,178,6,F2))
for yy,sgn in [(65,-1),(333,1)]:
 glaze_y(829,986,yy,145,207,sgn,F2);add(box(825,988,yy-3,yy+3,175,178,6,F2))
glaze_x(78,320,1000,145,207,1,F2);add(box(998,1003,78,320,175,178,6,F2))
glaze_y(602,686,400,174,190,1,F2);glaze_y(480,568,333,175,195,1,F2)
# North open corridor balustrade, with central gaps; never fill above the guard.
add(box(3,465,61,69,110,143,1,COL),box(815,999,61,69,110,143,1,COL))
for x in [115,232,350]:add(box(x-2,x+2,61,69,142,153,6,COL))
add(box(3,465,61,69,150,153,6,COL))
# Columns and exposed transverse/longitudinal beams connect all levels.
cw=C['column_width']
for x in C['column_x']:
 for y in C['column_y']:
  add(box(max(x-cw/2,0),x+cw/2,y-cw/2,y+cw/2,0,L['third']+2,1,COL))
 add(box(max(x-4,0),x+4,0,400,L['third']-7,L['third']+2,1,COL))
for z in [L['second']-11,L['third']-8]:add(box(0,1000,61,69,z,z+11,1,COL),box(0,1000,329,337,z,z+11,1,COL))
# Unobserved lower west wall faces remain neutral; no mirrored glazing.
add(box(-.4,1.5,65,333,0,L['second']-10,0,U),box(-.4,1.5,130,333,L['second'],L['third']-8,0,U))
# Lift is separate, not a broad solid stair core.
lx0,lx1,ly0,ly1=P['lift']['rect'];add(box(lx0,lx1,ly0,ly1,0,P['lift']['top'],4,STAIR))
for x in [lx0,lx1-5]:add(box(x,x+5,ly0-3,ly1,0,P['lift']['top'],1,STAIR))
for z in [0,40,80,110,150,190,217]:add(box(lx0,lx1,ly0-3,ly0+2,z,z+3,6,STAIR))
add(box(lx0+29,lx0+32,ly0-3,ly0+2,0,220,6,STAIR))
# Open L-return north stair, with sloped undersides and discrete treads.
ST=P['north_stair'];x0,x1=ST['lower_flight_x'];y0,y1=ST['lower_flight_y'];mid=ST['intermediate_z'];n=ST['steps_per_flight'];tw=ST['wall_thickness'];gh=ST['guard_height']
# Lower flight rises to north. Underflight triangular void remains open.
add(section_yz([(y0,mid-8),(y0,mid),(y1,0),(y1,-5)],x0,x1,1,STAIR))
for i in range(n):
 ya=y0+i*(y1-y0)/n;yb=y0+(i+1)*(y1-y0)/n;zz=mid*(1-i/n)
 add(box(x0,x1,ya,yb+.2,max(-1,zz-mid/n-9),zz,1,STAIR))
add(box(x0,x1,-5,65,mid-8,mid,1,STAIR))
# Upper flight rises to west; thickened sloping solid guards, not a solid under-stair box.
ux0,ux1=ST['upper_flight_x'];uy0,uy1=ST['upper_flight_y'];top=L['second'];add(section_xz([(ux0,top-8),(ux0,top),(ux1,mid),(ux1,mid-8)],uy0,uy1,1,STAIR))
for i in range(n):
 xa=ux0+i*(ux1-ux0)/n;xb=ux0+(i+1)*(ux1-ux0)/n;zz=top-(top-mid)*i/n
 add(box(xa,xb+.2,uy0,uy1,zz-(top-mid)/n-9,zz,1,STAIR))
add(box(465,ux0+.5,-5,165,top-9,top,1,STAIR))
add(section_yz([(y0,mid-8),(y0,mid+gh),(y1,gh),(y1,-5)],x1-tw,x1,1,STAIR))
add(section_xz([(ux0,top-8),(ux0,top+gh),(ux1,mid+gh),(ux1,mid-8)],uy0,uy0+tw,1,STAIR))
add(box(465,ux0,-5,1,top-8,top+gh,1,STAIR),box(694,700,-5,65,mid-8,mid+gh,1,STAIR))
# Thin ground rail beside the north landing, anchored only on own platform.
for x in [470,515,560]:add(box(x,x+3,-9,-6,-.2,24,6,STAIR))
add(box(470,563,-9,-6,21,24,6,STAIR))
# Low black south canopy, bar screen and open connection beside the east pod.
K=P['canopy'];kx0,kx1=K['x'];ky0,ky1=K['y'];kz0,kz1=K['z'];add(box(kx0,kx1,ky0,ky1,kz0,kz1,3,SCREEN))
add(box(kx0,760,ky1-5,ky1,kz1-K['fascia_height'],kz1,3,SCREEN))
for x in np.arange(*K['screen_x'],K['bar_pitch']):add(box(x,x+K['bar_width'],K['screen_y']-2,K['screen_y']+2,-.2,kz1,3,SCREEN))
for x in [110,235,465,585,760,807]:add(box(x,x+3,ky1-3,ky1,-.2,kz1,3,SCREEN))
add(box(110,760,K['screen_y']-2,K['screen_y']+2,3,6,3,SCREEN))
# Entire top floor. Recessed observed bands only on north/south/east.
ex0,ex1,ey0,ey1=P['upper_envelope'];body=box(ex0,ex1,ey0,ey1,L['third'],L['roof'],1,TOP)
# The west face is conservatively neutral, without east-facade mirroring.
body=body-box(-1,4,ey0,ey1,L['third'],L['roof']+.1,0,U);add(box(0,4,ey0,ey1,L['third'],L['roof'],0,U))
for y,sgn in [(ey0,-1),(ey1,1)]:
 a,b=(y-1,y+6)if sgn<0 else(y-6,y+1);body=body-box(8,992,a,b,263,299,1,TOP)
 yy=y+4.5 if sgn<0 else y-4.5;glaze_y(8,992,yy,263,299,sgn,TOP,C['upper_mullion_pitch'],C['upper_frame_width'])
 add(box(0,1000,y-3,y+3,259,263,1,TOP))
body=body-box(994,1001,6,394,263,299,1,TOP);glaze_x(6,394,995.5,263,299,1,TOP,C['upper_mullion_pitch'],C['upper_frame_width']);add(box(997,1003,0,400,259,263,1,TOP));add(body)
# Roof parapets and four unequal shallow neutral rooflight abstractions.
add(box(0,1000,0,8,L['roof']-.2,L['parapet'],1,TOP),box(0,1000,392,400,L['roof']-.2,L['parapet'],1,TOP),box(992,1000,0,400,L['roof']-.2,L['parapet'],1,TOP),box(0,8,0,400,L['roof']-.2,L['parapet'],0,U))
R=P['rooflight_simplification']
for rr in P['rooflights']:
 a,b=rr['x'];c,d=rr['y'];w=R['curb_width'];zz=L['roof'];add(box(a,b,c,d,zz-.2,zz+R['light_plane_height'],5,ROOF))
 for bb in [(a,b,c,c+w),(a,b,d-w,d),(a,a+w,c,d),(b-w,b,c,d)]:add(box(*bb,zz-.2,zz+R['curb_height'],0,U))
# Only the trace-confirmed small west 3F landing/stair, not a west bridge.
add(box(-50,10,170,230,L['third']-10,L['third']-8,1,WEST))
for i in range(5):add(box(-50+i*10,-40+i*10+.2,170,230,L['third']-10,L['third']-8+i*2,1,WEST))
# Low western guard rails tie to this landing; unobserved tall west details omitted.
add(box(-50,5,170,174,L['third']-.2,L['third']+18,1,WEST),box(-50,5,226,230,L['third']-.2,L['third']+18,1,WEST))
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add).simplify(.0001);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.array(mm.vert_properties[:,:3],np.float32,copy=True);vertices[:,2]+=np.float32(ZSHIFT);vertices*=np.float32(S);vertices=np.round(vertices.astype(np.float64),3).astype(np.float32);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32);keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum());faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
# Remove numerical zero-area tessellation slivers while preserving the manifold and tags.
clean=mesh(vertices,faces,materials,rule_indices).simplify(.002).to_mesh();vertices=np.array(clean.vert_properties[:,:3],np.float32,copy=True);faces=np.array(clean.tri_verts,np.int32,copy=True);ctags=np.asarray(clean.face_id,np.int32);materials=ctags%32;rule_indices=ctags//32
# Repair exactly collinear triangle/edge pairs without altering any vertex position.
# A zero-area triangle with midpoint M on long edge AB is replaced by splitting
# the adjacent AB-D triangle at M; its actual material/tag is retained.
zero_area_retriangulations=0
for attempt in range(100):
 tri=vertices[faces].astype(float);areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;bad=np.where(areas<1e-10)[0]
 if not len(bad):break
 bi=int(bad[0]);f=faces[bi];lengths=[np.linalg.norm(vertices[f[i]]-vertices[f[(i+1)%3]])for i in range(3)];j=int(np.argmax(lengths));u,v,m=int(f[j]),int(f[(j+1)%3]),int(f[(j+2)%3]);adj=np.where(np.sum(np.isin(faces,[u,v]),axis=1)==2)[0];adj=[int(q)for q in adj if q!=bi];assert len(adj)==1
 ai=adj[0];af=faces[ai]
 for k in range(3):
  aa,bb,dd=int(af[k]),int(af[(k+1)%3]),int(af[(k+2)%3])
  if {aa,bb}=={u,v}:break
 newfaces=np.array([[aa,m,dd],[m,bb,dd]],np.int32);ma=int(materials[ai]);rr=int(rule_indices[ai]);keep=np.ones(len(faces),bool);keep[[bi,ai]]=False
 faces=np.concatenate([faces[keep],newfaces]);materials=np.r_[materials[keep],[ma,ma]];rule_indices=np.r_[rule_indices[keep],[rr,rr]];zero_area_retriangulations+=1
else:raise RuntimeError('Unexpected unresolved collinear tessellation')
# Public source plans use +Y south; delivered right-handed mesh uses +Y north.
vertices[:,1]*=-1;faces=faces[:,::-1].copy()
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0;parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original source-face tags retained through Boolean union/difference. Actual per-face colors, no image textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_collapsed_repeated_index_triangles_removed':collapsed,'numerical_coordinate_grid_display_mm':0.001,'zero_area_triangle_edge_pairs_retessellated':zero_area_retriangulations,'physical_scale_claim':'None: dimensionless approximate W=1 geometry, 240 mm display main length.','complete_bounded_whole_three_storey_B':True,'distinct_first_second_floor_plans':True,'north_open_colonnade_and_east_pod_gap':True,'four_unequal_rooflight_footprints_neutral_shallow_only':True,'western_neighbor_and_glass_connector_excluded':True}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
