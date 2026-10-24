"""NCCU Dayong Hall — source-relative approximate complete main-building exterior."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NCCU source observations.
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(c,s,col,name):add(Manifold.cube(s,True).translate(c),col,name)
def beam(a,b,w,col,name):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);T=np.column_stack([x,y,z,(a+b)/2]);add(Manifold.cube((w,w,L+w*.15),True).transform(T),col,name)
def path(points,w,col,name):
 for a,b in zip(points,points[1:]):beam(a,b,w,col,name)
def ring(x,y,z,s,w,col,name):
 for a,b in [((-s/2,-s/2),(s/2,-s/2)),((s/2,-s/2),(s/2,s/2)),((s/2,s/2),(-s/2,s/2)),((-s/2,s/2),(-s/2,-s/2))]:beam((x+a[0],y+a[1],z),(x+b[0],y+b[1],z),w,col,name)





SCALE=2.5
palette=[('weathered_grey_concrete','#777E7A',255),('light_structural_concrete','#B8BEB5',255),('opaque_grey_glass_proxy','#677A7A',255),('aluminium_frames_braces','#C1CCCC',255),('dark_entry_frame','#394340',255),('stone_steps','#AAA49A',255),('red_arched_canopy','#852C37',255)]
def q(v):return round(v*1024)/1024
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def b(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
F=.5;H=3.3;centres=[-27.8,-10.7,11.4,27.8];cores=[(x-2.12,x+2.12) for x in centres];E=-10.5
b(-30,30,-3.6,3.6,0,F,5,'main_foundation_no_basement')
for a,bb in cores:b(a,bb,3.4,7.25,0,F,5,'projecting_core_foundation')
for k in range(4):
 z=F+k*H;zt=z+H
 b(-30,30,-3.6,3.6,z-.27,z,1,'registered_main_floor_slab')
 # Common cores at every floor, not diagonally shifted according to raster residual.
 for a,bb in cores:
  if k==0:b(a,bb,3.4,7.25,z-.27,z,1,'core_ground_slab')
  for aa,bbb in [(a,a+.20),(bb-.20,bb)]:b(aa,bbb,3.4,7.25,z,zt,0,'core_side_closure_approx')
  b(a,bb,7.05,7.25,z,zt,0,'core_back_closure_approx')
  if k<3:
   mid=(a+bb)/2
   for i in range(9):
    y=3.35+i*.34;h=z+(i+1)*H/18
    b(a+.20,mid-.1,y,y+.37,h-.28,h,5,'core_up_finite_plate')
    yr=6.07-i*.34;h=z+H/2+(i+1)*H/18
    b(mid+.1,bb-.20,yr,yr+.37,h-.28,h,5,'core_return_finite_plate')
   b(a+.20,bb-.20,6.40,7.08,z+H/2-.28,z+H/2,5,'core_midlanding_finite_slab')
   b(mid+.1,bb-.20,3.1,3.76,z+H-.27,z+H,1,'core_upper_landing_to_corridor')
 # Source photographed classroom-side glazed face; one candidate entry, second gap remains.
 wall=cube(-30,30,-3.6,-3.33,z,zt)
 if k==1:
  for ex in [E,11.3]:wall-=cube(ex-1.9,ex+1.9,-3.7,-3.2,z,z+2.6)
 for i in range(24):
  a=-29.7+i*2.5;bb=a+2.05
  if k==1 and any(a<ex+1.95 and bb>ex-1.95 for ex in [E,11.3]):continue
  wall-=cube(a,bb,-3.7,-3.2,z+.70,z+2.83)
  b(a-.01,bb+.01,-3.49,-3.36,z+.69,z+2.84,2,'window_opaque_proxy_not_texture')
  for xx in [a,(a+bb)/2,bb]:b(xx-.045,xx+.045,-3.68,-3.28,z+.68,z+2.85,3,'window_mullion')
  for zz in [z+.70,z+1.85,z+2.83]:b(a,bb,-3.68,-3.28,zz-.045,zz+.045,3,'window_transom')
 add(wall,0,'front_window_wall_two_2F_gap_candidates')
 rear=cube(-30,30,3.35,3.6,z,zt)
 for a,bb in cores:rear-=cube(a+.19,bb-.19,3.2,3.7,z,z+2.6)
 for xx in [-20,0,20]:
  rear-=cube(xx-.7,xx+.7,3.2,3.7,z+1.2,z+2.4)
  b(xx-.71,xx+.71,3.44,3.55,z+1.19,z+2.41,2,'unseen_back_limited_glazing_approx')
 add(rear,0,'upper_corridor_enclosed_back_approx_not_full_open_gallery')
 b(-30,-29.75,-3.6,3.6,z,zt,0,'left_end_wall');b(29.75,30,-3.6,3.6,z,zt,0,'right_end_wall')
 rw=cube(-29.75,29.75,.85,1.10,z,zt)
 for xx in [-27,-21,-15,E,-5,2,7,11.3,17,23,28]:rw-=cube(xx-.6,xx+.6,.7,1.2,z,z+2.4)
 add(rw,0,'shared_long_corridor_room_wall_schematic_openings_no_room_partitions')
for x in [-30+i*2.5 for i in range(25)]:
 for k in range(4):
  z=F+k*H
  if k==1 and any(abs(x-ex)<2 for ex in [E,11.3]):continue
  b(x-.12,x+.12,-3.82,-3.4,z, z+H,1,'visible_facade_pier')
# Only source-visible entry-neighbouring fields. Opposing slopes connect actual piers.
for xa,xb,rising in [(-22.5,-20,False),(-20,-17.5,True),(-5,-2.5,False)]:
 for k in range(4):
  z=F+k*H
  za,zb=(z+.06,z+3.23) if rising else (z+3.23,z+.06)
  beam((xa,-3.77,za),(xb,-3.77,zb),.16,3,'source_bounded_entry_brace_to_actual_piers')
b(-30.15,30.15,-3.75,3.75,13.67,13.95,1,'low_main_roof_closure_no_RF_approx')
for a,bb in cores:b(a-.1,bb+.1,3.4,7.35,13.67,13.95,1,'low_core_closure_no_towers_approx')
# One left candidate red canopy. Both photos show this same entrance.
z=F+H;G=1.85
b(E-2.15,E+2.15,-5.30,-3.35,z-.30,z,5,'entry_upper_landing')
b(E-2.35,E+2.35,-5.60,-3.20,z+2.60,z+2.84,6,'single_red_canopy')
for yy in [-5.45,-3.4]:
 points=[(E+2.1*math.cos(t),yy,z+2.82+.65*math.sin(t)) for t in np.linspace(0,math.pi,19)]
 path(points,.12,6,'single_canopy_arch_rib')
for xx in [E-1.9,E+1.9]:b(xx-.08,xx+.08,-3.69,-3.28,z,z+2.6,4,'open_entry_frame')
b(E-1.9,E+1.9,-3.69,-3.28,z+2.49,z+2.61,4,'open_entry_header')
b(E-2.25,E+2.25,-10.2,-5.15,0,G,5,'finite_local_grade_full_stair_foot_landing')
for i in range(12):
 y=-5.30-(i+1)*.33;h=z-(i+1)*(z-G)/12
 b(E-1.9,E+1.9,y,y+.36,G-.10,max(G+.02,h),5,'complete_external_treads')
 for a,bb in [(E-2.13,E-1.9),(E+1.9,E+2.13)]:b(a,bb,y,y+.36,G-.10,max(G+.02,h)+.80,0,'entry_solid_stair_sidewall')
# Finite left-side ramp: original photo does not establish its measured pitch/length.
RX=-28.5;UX=q(E-2.15);L=1.88
points=[[q(x),q(y),q(h)] for x,top in [(RX,L),(UX,z)] for y in [-5.18,-3.94] for h in [top-.30,top]]
ramp=trimesh.convex.convex_hull(np.array(points));add(Manifold(Mesh(np.array(ramp.vertices,dtype=np.float32),np.array(ramp.faces,dtype=np.uint32))),5,'finite_left_ramp_top')
b(RX-.7,RX+.5,-5.3,-3.4,0,L,5,'ramp_lower_landing_local_grade')
for i in range(10):
 x=RX+(UX-RX)*i/9;zz=L+(z-L)*i/9
 b(x-.055,x+.055,-5.24,-5.12,zz-.1,zz+.8,3,'ramp_railing_post')
rail_y0,rail_y1=q(-5.24),q(-5.12)
rail_y=(rail_y0+rail_y1)/2;rail_width=rail_y1-rail_y0
beam((q(RX),rail_y,q(L+.75)),(q(UX),rail_y,q(z+.75)),rail_width,3,'ramp_sloping_rail_shared_post_y_planes')
# Exterior feet meet bounded surrounding grade, not isolated high podium cliffs.
# Upper plateaus remain outside full stair/ramp landings; four finite slope faces
# blend to the same model datum. This is not measured terrain or a whole site.
def local_grade(upper,lower,top,name):
 ux0,ux1,uy0,uy1=upper;lx0,lx1,ly0,ly1=lower
 pp=[[x,y,top] for x in [ux0,ux1] for y in [uy0,uy1]]
 pp += [[x,y,zg] for x in [lx0,lx1] for y in [ly0,ly1] for zg in [0,.18]]
 pp=[[q(value) for value in point] for point in pp]
 tm=trimesh.convex.convex_hull(np.array(pp));add(Manifold(Mesh(np.array(tm.vertices,dtype=np.float32),np.array(tm.faces,dtype=np.uint32))),5,name)
local_grade((E-2.9,E+2.9,-10.9,-8.9),(E-5.1,E+5.1,-15.2,-7.8),G,'foot_outside_apron_and_bounded_grade_slope_to_datum')
local_grade((-29.55,-28.1,-5.6,-3.8),(-33.5,-27.4,-8.2,-3.65),L,'ramp_foot_outside_apron_and_bounded_grade_to_datum')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學大勇樓','inventory':'60-21 / A26(21)','revision':'v5','scope':'4F noB long rectangular main body, upper-side corridor and four projecting shared cores; two 2F entry gaps, left candidate single redarched canopy and complete stair/left ramp and finite exterior grade slopes','coordinate_transform':'CCW diagram common60x7.2 frame; endanchors145/780; middle shared centres normalized from2-4F340/593;1F320/571 residual about20px disclosed, no floor drift;2.5mm/unit not survey','limits':['Official fire diagram not as-built','Source dates not photo capture, not verified2026','693/694 same entry candidates, left2Fgap selected not proven exact location','Low roof closure/coretops approximate noRF no towers','Unseen back limited closed wall approximate not whole open gallery','Room partitions omitted; windows structural modules colors stairs grade ramp dimensions approximate','No sourcepixels logos or equipment counts','No physical print or code compliance certification']}
# Coalesce same-material construction primitives before final material Boolean. This removes
# artificial coplanar construction seams without nearest recolouring across material boundaries.
grouped=[];group_material_ids={}
for col in range(len(palette)):
 same=[part for part,record in zip(parts,part_records) if record['material']==col]
 g=Manifold.batch_boolean(same,OpType.Add).as_original()
 group_material_ids[g.original_id()]=col;grouped.append(g)
parts=grouped;material_for_id=group_material_ids
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Preserve Boolean run provenance through simplification: never nearest-surface paint broad triangles.
m=m.set_tolerance(0.000001).simplify(0.000001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
colors=np.empty(len(fs),dtype=int);maxdist=0
for i,rid in enumerate(me.run_original_id):colors[me.run_index[i]//3:me.run_index[i+1]//3]=material_for_id[rid]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),('float32 export degeneracy: repair generator, not QA',tri[np.linalg.norm(cr,axis=1)==0].tolist());nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_assignment_method="Boolean original-run provenance retained through simplification; no nearest recolouring",parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
