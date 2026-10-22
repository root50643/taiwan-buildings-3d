"""CTU Lugang Pavilion / 建國科技大學綠崗亭. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('stone_base','#77796D',255),('stone_relief','#B2AEA0',255),('gray_columns','#A4A69C',255),('warm_plaster','#D7C9AA',255),('red_tiles','#A64E3D',255),('red_railings','#963B2B',255),('pale_moon_rim','#E8DCC5',255)]
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

# Units are display millimetres, all dimensions photo-proportion estimates.
box((0,0,3),(100,100,6),0,'stone_faced_platform_no_underwater_foundation')
box((0,0,6.2),(101,101,1.8),2,'platform_cap')
# Irregular polygonal stone faces: deliberately non-rectangular, unmeasured joints.
for side in [-1,1]:
 for row in range(2):
  edges=np.linspace(-49.7,49.7,12) if row==0 else np.r_[-49.7,np.linspace(-45,45,11),49.7]
  for j,(left,right) in enumerate(zip(edges[:-1],edges[1:])):
   left+=.25;right-=.25;w=right-left;bottom=.35+row*2.65;top=bottom+2.25
   poly=[(left+.1*w,bottom+.25),(left,bottom+1.15),(left+.19*w,top),(right-.12*w,top-.13*((j%3)+1)),(right,top-.8),(right-.08*w,bottom),(left+.45*w,bottom+.12*(j%2))]
   stone=CrossSection([poly[::-1]]).extrude(.65).rotate((90,0,0)).translate((0,side*50+.325,0))
   add(stone,1,'estimated_irregular_polygon_stone_faces')
   add(stone.rotate((0,0,90)),1,'estimated_irregular_polygon_stone_faces')
for x in [-35,35]:
 for y in [-35,35]:add(Manifold.cylinder(99,3.6,3.6,32).translate((x,y,7)),2,'four_continuous_round_approximation_columns')
box((0,0,55),(74,74,3),3,'upper_floor')
for z in [52,103]:
 for x in [-35,35]:box((x,0,z),(5,76,4),3,'two_storey_beam_frame')
 for y in [-35,35]:box((0,y,z),(76,5,4),3,'two_storey_beam_frame')
def moon(axis,at,lo,hi,half,rad,zc,shift=0):
 wall=Manifold.cube((2.2,2*half,hi-lo),True).translate((at,shift,(lo+hi)/2))
 hole=Manifold.cylinder(8,rad,rad,96,True).rotate((0,90,0)).translate((at,shift,zc))
 frame=wall-hole
 rim=(Manifold.cylinder(2.8,rad+1.1,rad+1.1,96,True)-Manifold.cylinder(4,rad,rad,96,True)).rotate((0,90,0)).translate((at,shift,zc))
 rim=rim ^ Manifold.cube((8,2*half+2,hi-lo),True).translate((at,shift,(lo+hi)/2))
 if axis=='y':frame=frame.rotate((0,0,90));rim=rim.rotate((0,0,90))
 add(frame,3,'lower_moon_gate' if axis=='y' else 'upper_moon_window_panel');add(rim,6,'light_moon_opening_trim')
# Lower gates on +/-Y; upper windows on +/-X: perpendicular, never four copied faces.
for at in [-43,43]:moon('y',at,7,49,22,19.5,25.7)
for at in [-35,35]:moon('x',at,56.5,101,25,18.8,79,-3)
# Only the west upper landing has a walkable side opening y=22..31.5.
for x in [-35,35]:
 for y0,y1 in [(-31.5,-28),(22,31.5)]:
  if x==-35 and y0==22:continue
  for z in [59,65,97,100]:beam((x,y0,z),(x,y1,z),1.2,5,'moon_panel_side_guard_lattice')
  beam((x,(y0+y1)/2,57),(x,(y0+y1)/2,102),1,5,'moon_panel_side_guard_post')
# Open upper faces, red curved balusters.
for y in [-35,35]:
 for z in [58,70]:beam((-32,y,z),(32,y,z),1.6,5,'upper_red_horizontal_rail')
 for x in range(-30,31,3):path([(x+.65*math.sin(t*math.pi*2),y,58+12*t) for t in np.linspace(0,1,9)],1.0,5,'upper_curved_red_baluster')
# Lower gray cap rails, red open X filling. Gate sides stop at the moon frame.
for axis in ['x','y']:
 for side in [-1,1]:
  spans=[(-49,49)] if axis=='x' else [(-49,-22),(22,49)]
  for lo,hi in spans:
   def pt(u,z):return (side*48,u,z) if axis=='x' else (u,side*48,z)
   beam(pt(lo,17),pt(hi,17),2.5,2,'lower_gray_rail_cap');beam(pt(lo,8),pt(hi,8),2,2,'lower_gray_rail_sill')
   count=max(1,round((hi-lo)/7))
   for a,b in zip(np.linspace(lo,hi,count+1)[:-1],np.linspace(lo,hi,count+1)[1:]):
    beam(pt(a,9),pt(b,16),1.05,5,'lower_red_X');beam(pt(a,16),pt(b,9),1.05,5,'lower_red_X');beam(pt(a,9),pt(a,17),1.2,2,'lower_gray_rail_post')
# Single external straight stair, on west side, rising toward north landing.
for i in range(18):
 y=-37+i*3.6;top=7+(i+1)*2.7
 box((-43,y+1.8,top-1.7),(11,3.65,3.4),2,'external_stair_tread_estimated_count')
add(Manifold.cube((10.8,3.8,81.6),True).rotate((-53.1,0,0)).translate((-43,-4.6,30.3)),2,'external_stair_full_width_inclined_slab')
box((-39,29,54.5),(19,10,3),2,'stair_upper_short_landing')
for y,z in [(-37,7),(27.8,55.6)]:beam((-49,y,z),(-49,y,z+14),1.4,5,'external_stair_rail_end')
beam((-49,-37,21),(-49,27.8,69.6),1.5,5,'external_stair_red_handrail')
for i in range(18):
 y=-35+i*3.6;z=7+(y+37)*.75;beam((-49,y,z),(-49,y,z+14),1,5,'external_stair_red_balusters')
beam((-49,34,69.6),(-34,34,69.6),1.5,5,'landing_outer_rail');beam((-49,27.8,69.6),(-49,34,69.6),1.5,5,'landing_rail_return')
# Square hip-roof shell helper, central apex upper roof and annular lower eave.
def frustum(outer,inner,z0,z1,thick):
 poly=CrossSection.square((outer*2,outer*2),True)
 return poly.extrude(z1-z0,1,0,(inner/outer,inner/outer)).translate((0,0,z0)) - poly.extrude(z1-z0,1,0,(inner/outer,inner/outer)).translate((0,0,z0-thick))
notch=Manifold.cube((25,40,20),True).translate((-44,36,55))
low=frustum(54,35,50.5,57,2.4)-Manifold.cube((69.7,69.7,30),True).translate((0,0,55))
add(low-notch,4,'lower_annular_red_hip_eave_with_stair_notch')
# White fascia beneath roof edge, interrupted at the same opening.
for x in [-53,53]:add(Manifold.cube((2,108,2.4),True).translate((x,0,50))-notch,3,'lower_light_fascia')
for y in [-53,53]:add(Manifold.cube((108,2,2.4),True).translate((0,y,50))-notch,3,'lower_light_fascia')
add(frustum(44,0.8,104,124,2.4),4,'single_four_hip_red_roof_shell')
for x in [-43,43]:box((x,0,103),(2,88,3),3,'upper_light_fascia')
for y in [-43,43]:box((0,y,103),(88,2,3),3,'upper_light_fascia')
for sx in [-1,1]:
 for sy in [-1,1]:beam((sx*44,sy*44,104),(sx*.8,sy*.8,124),1.8,4,'four_hip_ridges')
add(Manifold.cylinder(3.2,1.4,.9,24).translate((0,0,123)),4,'apex_finial_narrow_neck');add(Manifold.sphere(1.8,32).translate((0,0,127)),4,'apex_finial_rounded_head')
# Reduced roof tile courses: actual raised geometry; exact count not asserted.
for z in np.arange(105,123,2.6):
 s=44-(z-104)*43.2/20;ring(0,0,z,2*s,0.9,4,'upper_tile_course_simplified')
for u in np.arange(-49,50,5):
 for axis in [0,1]:
  for side in [-1,1]:
   a=(u,side*53.5,51.3);b=(u*.66,side*35.3,57)
   if axis:a=(a[1],a[0],a[2]);b=(b[1],b[0],b[2])
   # Notch kept completely free of tile ribs.
   if axis and side==-1 and max(a[1],b[1])>16:continue
   beam(a,b,1,4,'lower_tile_rib_simplified')
   rib=parts.pop();part_records.pop();rib=rib-notch
   if not rib.is_empty():add(rib,4,'lower_tile_rib_simplified_notch_clipped')
# Geometric red frieze on each level: horizontal bars and stepped rhythm.
for z in [47,98]:
 for y in [-35,35]:
  for zz in [z,z+2.5]:beam((-32,y,zz),(32,y,zz),.96,5,'red_geometric_frieze')
  for x in range(-30,31,6):beam((x,y,z),(x,y,z+2.5),.96,5,'red_frieze_vertical')
 for x in [-35,35]:
  for zz in [z,z+2.5]:beam((x,-32,zz),(x,32,zz),.96,5,'red_geometric_frieze')
  for y in range(-30,31,6):beam((x,y,z),(x,y,z+2.5),.96,5,'red_frieze_vertical')
FEATURES=dict(name='建國科技大學綠崗亭',school='建國科技大學',slug='ctu-lugang-pavilion',selected_version='2013 upload photographs; capture time not independently verified; not 2026 condition',estimated_not_surveyed=True,continuous_corner_columns=4,column_cross_section_approximate=True,lower_upper_moon_openings_rotated_90_degrees=True,single_external_stair=True,lower_eave_has_stair_notch=True,only_one_upper_walkable_side_opening=True,approach_bridges_omitted=True,underwater_foundations_omitted=True,no_actual_print=True,support_free_certified=False,all_materials_opaque=True)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance_nearest_surface_max_distance_mm=maxdist,parts=part_records)
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
