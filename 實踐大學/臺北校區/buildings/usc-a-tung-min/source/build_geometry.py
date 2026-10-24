#!/usr/bin/env python3
"""Original whole-A exterior approximation from public evidence; no source pixels.
All coordinates are model millimeters, not a measured physical building scale.
Semantic source-face tags survive Boolean union into real per-face materials.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_scale_mm'];M=P['main'];T=P['tower'];L=P['low_wing'];C=P['repetition_conventions']
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules=[]
def rule(name,evidence,note,classification='observed organization / approximate dimensions'):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unobserved closure / manufacture',[],'Plain hidden west return, capped unknown roof, solid internal fill, model plinth and undersides. Not observed architectural finish.','inferred / manufactured')
B=rule('Upper bridge-like main volume',['02-07','02-08','04-02','08-photo'],'Three front vertical-louver bands over a large unfilled portal; front/back depth is approximate.')
TOW=rule('Higher front tower and blades',['01-09','02-08','04-02'],'Higher cyan-gray metal/glass mass, horizontal joints/window slits, lower recess; no 26.4 m total-height calibration.')
LOW=rule('Diagonal lower horizontal-louver wing',['02-06','02-07','02-08','04-02'],'Approximate diagonal organization, horizontal fins distinct from upper vertical fins. Exact triangle is not surveyed.')
RC=rule('Retained rear classroom grid',['09-photo','13-photo'],'Broad lower classroom block belongs to A; four visible modeled bands are not a verified total floor count. Excludes L.')
RB=rule('Rear long window and balcony bands',['09-photo'],'Two long high bands plus left glazed stack, dark frames/pale curtains; count and rail spacing conventional.')
RE=rule('Higher narrow rear return',['09-photo','13-photo'],'A end before foreground L occlusion. Hidden physical seam is not claimed.')
EN=rule('Entrance columns, open passage and bridges',['02-05','02-06','03-04','03-05'],'Unfilled lower portal, approximate stairs/columns and two inner bridges; not a full interior.')
ST=rule('Rear external return stair',['09-photo'],'Three simplified dogleg flights and landing rhythm. Exact stair geometry/tread count unknown.')
BR=rule('A-side east bridge interface only',['02-12','03-06','03-07'],'Short model stub, not the full surveyed bridge; H excluded.')
NA=rule('Entrance marker position',['02-07','02-08','04-02'],'Plain original narrow gray marker, no sampled calligraphy or logo.')

def mesh(v,f,ma,rr):
 v=np.array(v,dtype=np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 solid=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert solid.status()==mf.Error.NoError,solid.status();return solid

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma,rr):
 assert x1>x0 and y1>y0 and z1>z0,(x0,x1,y0,y1,z0,z1)
 return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def poly(poly,z0,z1,ma,rr,topmat=None,toprule=None):
 pp=np.asarray(poly,float)
 if np.linalg.det(np.array([pp[1]-pp[0],pp[2]-pp[1]]))<0:pp=pp[::-1]
 n=len(pp);v=[[x,y,z]for z in [z0,z1]for x,y in pp];cap=np.array(mf.triangulate([pp],allow_convex=False));f=cap[:,::-1].tolist()+(cap+n).tolist();mas=[ma]*len(cap)+[ma if topmat is None else topmat]*len(cap);rs=[rr]*len(cap)+[rr if toprule is None else toprule]*len(cap)
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]];mas += [ma]*2;rs += [rr]*2
 return mesh(v,f,mas,rs)
def beam_between(a,b,width,depth,ma,rr):
 # General rectangular bar, connected endpoints; useful for stair strings/rails.
 a=np.array(a,float);b=np.array(b,float);d=b-a;d=d/np.linalg.norm(d);q=np.cross(d,[0,0,1])
 if np.linalg.norm(q)<.1:q=np.cross(d,[0,1,0])
 q=q/np.linalg.norm(q)*width/2;r=np.cross(d,q);r=r/np.linalg.norm(r)*depth/2
 v=[p+s*q+t*r for p in [a,b]for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 f=[[0,3,2],[0,2,1],[4,5,6],[4,6,7]]
 for i in range(4):j=(i+1)%4;f += [[i,j,j+4],[i,j+4,i+4]]
 return mesh(v,f,[ma]*12,[rr]*12)
solids=[]
def add(*s):solids.extend(s)
# Original abstract base; no roads, landscape or surveyed foundation inferred.
add(box(-114,110,-67,74,0,2.5,0,U))
# Approximate occupied volume on rear. Use deliberately neutral hidden side/top.
add(box(-90,20,31,65,2.4,78,0,U),box(44,100,17,65,2.4,78,0,U))
# Rear higher narrow end belongs to A; there is no projecting L facade.
add(box(-90,-70,31,65,77.9,133,0,U))
# Long connected upper wing; front lower portal remains physically void.
add(box(-90,100,17,65,78,114,0,U))
# Rear classroom facade frame and true face-color pane patches (opaque, not holes).
# Relief forms frames without pretending to model interior rooms.
def window_group(x0,x1,y,z0,z1,rr,pale=True,pitch=4.3):
 add(box(x0,x1,y-.4,y+.8,z0,z1,3,rr))
 count=max(1,round((x1-x0-1.2)/pitch));step=(x1-x0-1.2)/count
 for i in range(count):
  l=x0+.6+i*step;r=l+step-.65
  ma=6 if pale and i%5!=3 else 4
  add(box(l,r,y+.65,y+1.1,z0+.65,z1-.65,ma,rr))
 # Horizontal transom partly divides glazing; convention not actual exact width.
 add(box(x0,x1,y+.8,y+1.32,z0+3,z0+3.65,3,rr))
# Concrete rear bays and narrow higher end. Whole blocks retained, not a facade fragment.
add(box(-70,20,64.7,65.35,2.4,78,1,RC))
for z0,z1 in C['rear_window_rows']:
 for x0,x1 in [(-67,-26),(-22,17)]:window_group(x0,x1,65.4,z0,z1,RC)
add(box(-90,-70,64.7,65.4,2.4,133,1,RE))
for z0,z1 in C['rear_window_rows']+[[80,94],[100,113],[119,130]]:window_group(-87,-73,65.45,z0,z1,RE,pale=False)
# The left side in the rear photo is right in model coordinates.
add(box(44,100,64.7,65.4,2.4,78,1,RB))
window_group(47,97,65.45,5,37,RB,pale=False)
for z0,z1 in [[42,54],[58,70],[74,86]]:
 # extend third band across stair bay as actual upper link only.
 x0=20 if z0>=74 else 44
 add(box(x0,100,63.8,65.5,z0-.5,z1+.5,1,RB));window_group(x0+2,98,65.6,z0,z1,RB)
# Long two continuous high windows: behind conventional balcony rails.
for z0,z1 in C['upper_rear_rows']:
 add(box(-70,100,64.7,65.6,z0-1.4,z1+.8,1,RB));window_group(-68,98,65.7,z0,z1,RB)
 add(box(-71,102,64.8,69.0,z0-1.9,z0-.8,2,RB))
 for z in [z0+1,z0+3.1]:add(box(-71,102,68.1,69,z,z+.9,2,RB))
 for x in np.arange(-70,102,12):add(box(x,x+.9,68.1,69,z0-1.4,z0+4,2,RB))
# Conventional front vertical fins in three horizontal bands. The dark backing
# is actual glass material and fins are separated solid geometry, not a texture.
add(box(-43,100,16.5,17.2,78,114,3,B))
for z0,z1 in [[79,89.5],[91,101.5],[103,113]]:
 add(box(-42,99,16.12,16.7,z0,z1,4,B))
 for x in np.arange(-42,100,C['front_vertical_fin_pitch']):add(box(x,x+.9,13.7,16.8,z0-.2,z1+.2,2,B))
 for z in [z0-.65,z1]:add(box(-43,100,13.6,17.4,z,z+.9,1,B))
# Wider right support wall, not a mirror copy of slender lower wing columns.
add(box(74,100,14.5,18.5,2.4,79,1,EN))
for z in [14,32,50,68]:add(box(90,98,14.1,14.6,z,z+4,4,EN))
# Concrete coffered soffit for entrance; crossing beams attached to upper block.
for x in np.arange(-39,75,12):add(box(x,x+1.4,17,63,76.7,78.3,1,EN))
for y in np.arange(18,64,10):add(box(-41,76,y,y+1.3,76.7,78.3,1,EN))
# Tower blades. The tall plate at left projects above tower roof in front images.
add(box(-94,-90,-11,41,2.4,T['blade_top'],1,TOW))
add(box(-44,-40,-10,19,2.4,147,1,TOW))
# Only observed front tower envelope. Hidden back and roof neutral.
add(box(-90,-41,-10,28,T['body_bottom'],T['body_top'],0,U))
add(box(-90,-41,-10.6,-9.7,130,173,5,TOW))
for z in np.arange(131,174,3.5):add(box(-90,-41,-10.9,-10.35,z,z+.65,2,TOW))
for z in [138.5,151]:
 add(box(-79,-43,-11.05,-10.5,z,z+2.1,3,TOW))
 add(box(-78.5,-43.5,-11.15,-10.9,z+.3,z+1.75,4,TOW))
 for x in [-67,-55]:add(box(x,x+.55,-11.3,-10.8,z,z+2.1,2,TOW))
# Recessed inner rear wall below tower and undercroft roof do not close the void.
add(box(-90,-44,25,29,78,130.2,1,TOW),box(-90,-41,-10,28,128.7,130.2,1,TOW))
# Approximate diagonal low wing (the 45-degree organization is documented;
# coordinates are a coherent model choice, not an exact footprint).
p0=np.array(L['screen_start'],float);p1=np.array(L['screen_end'],float);d=p1-p0;n=np.array([d[1],-d[0]])/np.linalg.norm(d);inside=-n
triangle=[p0,p1,np.array(L['rear_vertex'],float)];lh=L['screen_top']
add(poly(triangle,27,lh,0,U,0,U))
# Full diagonal glazing panel and horizontal projecting fins, plus open lower arcade.
def strip(a,b,offset0,offset1,z0,z1,ma,rr):return poly([a+n*offset0,b+n*offset0,b+n*offset1,a+n*offset1],z0,z1,ma,rr)
add(strip(p0,p1,-.2,.7,27,lh,4,LOW))
for z in np.arange(27.8,lh,C['horizontal_louver_pitch']):add(strip(p0,p1,.4,3,z,z+.9,2,LOW))
for t in np.linspace(0,1,9):
 c=p0+d*t;add(strip(c-d/np.linalg.norm(d)*.6,c+d/np.linalg.norm(d)*.6,-.1,3.1,3,lh+.7,2,LOW))
# Observed lower screen continues down near the left end, while the right
# portion remains an open lower colonnade; exact division is approximate.
for z in np.arange(4.2,27,C['horizontal_louver_pitch']):add(strip(p0,p0+d*.62,.4,3,z,z+.9,2,LOW))
# Lower solid glazing is inset behind an open front row of concrete columns.
q0=p0+inside*8;q1=p1+inside*8
add(strip(q0,q1,-.2,.4,3,27,3,LOW))
for t in np.linspace(.08,.92,8):
 c=q0+d*t;add(strip(c-d/np.linalg.norm(d)*3.5,c+d/np.linalg.norm(d)*3.5,.3,.7,5,24.5,4,LOW))
for t in [0,.25,.5,.75,1]:
 c=p0+d*t;add(box(c[0]-1.7,c[0]+1.7,c[1]-1.7,c[1]+1.7,2.4,28,1,EN))
# Screen wraps onto a short return without copying uncertain hidden west facade.
add(box(-107,-103,7.5,21,3,lh,3,LOW))
for z in np.arange(4,lh,C['horizontal_louver_pitch']):add(box(-109,-103,7.5,21,z,z+.9,2,LOW))
# The entrance-facing side of the diagonal wing is also visibly screened in
# interior photo 02-06, not a blank triangular wall. Use horizontal geometry
# on this second edge and retain open ground-level arcade columns.
ia=p1;ib=np.array(L['rear_vertex'],float);iv=ib-ia;inu=np.array([iv[1],-iv[0]])/np.linalg.norm(iv)
def inner_strip(off0,off1,z0,z1,ma):
 return poly([ia+inu*off0,ib+inu*off0,ib+inu*off1,ia+inu*off1],z0,z1,ma,LOW)
add(inner_strip(-.2,.55,27,lh,4))
for z in np.arange(27.8,lh,C['horizontal_louver_pitch']):add(inner_strip(.3,2.5,z,z+.9,2))
for t0 in np.linspace(0,1,7):
 cc=ia+iv*t0;dd=iv/np.linalg.norm(iv)*.55
 add(poly([cc-dd,cc+dd,cc+dd+inu*2.6,cc-dd+inu*2.6],27,lh+.7,2,LOW))
for t0 in [0,.25,.5,.75,1]:
 cc=ia+iv*t0;add(box(cc[0]-1.7,cc[0]+1.7,cc[1]-1.7,cc[1]+1.7,2.4,28,1,EN))
# Low wing rear joins the whole A via broad neutral connection, not a separate token facade.
add(box(-90,-47,18,40,3,lh-.2,0,U))
# Open entrance and rear link: inner bridges are narrow, not a filled lower hall.
for z in [30,51]:
 add(box(-27,76,25,31.1,z,z+2.0,1,EN))
 for zz in [z+4,z+7]:add(box(-27,76,24.6,25.5,zz,zz+.9,2,EN))
 for x in np.arange(-26,76,12):add(box(x,x+.9,24.6,25.5,z+1,z+8,2,EN))
add(box(71.5,75,39,49,2.4,78,1,EN))
# Observed-style inner exposed wall and recessed dark apertures are approximate.
add(box(-27,20,30.4,31.2,3,77.8,1,EN))
for z in [12,34,55]:
 add(box(7,17,30.05,30.5,z,z+9,3,EN),box(7.7,16.3,29.9,30.1,z+.7,z+8.3,4,EN))
# Central ground corridor remains open through x20..44 under rear stair.
# Simple flights zigzag in the narrow rear gap; landings connect to both bodies.
for i,(z0,z1) in enumerate([(3,24),(24,45),(45,66)]):
 y=66.3
 xa,xb=(23,41)if i%2==0 else(41,23)
 add(beam_between((xa,y,z0),(xb,y,z1),5.5,1.25,2,ST))
 for k in range(13):
  t=k/12;x=xa+(xb-xa)*t;z=z0+(z1-z0)*t
  add(box(x-1.15,x+1.15,63.5,69.1,z-.15,z+.85,2,ST))
 # Side stringers and simple rail only; no claimed exact treads.
 for yy in [63.55,69.0]:
  add(beam_between((xa,yy,z0),(xb,yy,z1),.9,1.3,2,ST))
  add(beam_between((xa,yy,z0+4),(xb,yy,z1+4),.9,.9,2,ST))
  for t in [0,.33,.66,1]:
   x=xa+(xb-xa)*t;z=z0+(z1-z0)*t;add(box(x-.45,x+.45,yy-.45,yy+.45,z,z+4.5,2,ST))
 add(box(19.7,44.3,62,70,z1-.5,z1+1,2,ST))
# Discreet model-only foot under first flight: removes a print-start island.
add(box(22.2,25.2,62.8,69.7,2.4,4.1,0,U))
# Modest A-side stub only, with no invented full steel span or H building.
add(box(99,108,46,62,40.5,42.3,2,BR))
for yy in [46,61]:
 add(box(99,108,yy,yy+.9,46,46.9,2,BR));add(box(106.5,107.4,yy,yy+.9,41.5,46.9,2,BR))
# Front broad stepped approach, not a surveyed terrain reconstruction.
for i in range(8):add(box(-24,66,-47+3.6*i,22,2.4,3.3+.65*i,1,EN))
# Narrow monument marks observed position; inscriptions deliberately not reproduced.
add(box(-13,-2,-37,-31,2.4,65,1,NA),box(-10,-5,-37.35,-36.9,14,57,3,NA))
# Low platform edge supports louver foot and unifies thin parts for printing.
add(strip(p0,p1,-1,3.5,2.4,4.2,1,LOW))
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add).simplify(0.0001);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32)*np.float32(S);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
assert materials.max()<len(palette) and rule_indices.max()<len(rules)
# Float32 serialization can collapse sub-ULP Boolean edges at stair intersections.
# Weld only bit-identical output coordinates and discard only resulting repeated-index
# triangles, preserving all surviving categorical face tags and exact coordinates.
vertices,inv=np.unique(vertices,axis=0,return_inverse=True);faces=inv[faces].astype(np.int32)
keep=(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,2]!=faces[:,0]);collapsed=int((~keep).sum())
faces=faces[keep];materials=materials[keep];rule_indices=rule_indices[keep]
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
parts=t.split(only_watertight=False);assert len(parts)==1,[(len(x.faces),x.bounds.tolist())for x in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Categorical original source-face tags propagated through Boolean union; actual face materials; no textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'float32_collapsed_repeated_index_triangles_removed':collapsed,'physical_scale_claim':False,'whole_A_exterior_approximation':True,'L_foreground_wing_excluded':True,'maximum_height_record_26_4_m_not_used_as_scale':True,'hidden_west_and_roof_neutral':True,'front_lower_portal_open':True,'exact_floor_count_claim':False}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
