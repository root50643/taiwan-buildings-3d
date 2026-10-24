"""Communication Hall: source-bound complete connected main building, private study."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType,FillRule
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[];SCALE=4.0
palette=[('warm_small_tile_wall','#B6AD99',255),('recessed_wall','#ABA694',255),('dark_stair_glazing','#35464D',255),('opaque_window_proxy','#63777D',255),('light_window_frames','#CDD1CA',255),('approximate_hillside_base','#827F6B',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def CS(p):return CrossSection(p,fillrule=FillRule.EvenOdd)
def poly(p,z0,z1):return CS([p]).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def canon(points,anchor=(478,415)):return [((x-anchor[0])/15,(anchor[1]-y)/15) for x,y in points]
# Front common staircase (478,415); all floors registered to the same stair.
basement=canon([(46,142),(125,86),(230,86),(230,94),(513,94),(513,392),(443,392),(443,374),(185,374),(185,339),(141,339),(141,271),(108,255),(71,255),(46,237)],(478,390))
f1=canon([(46,140),(126,84),(191,84),(191,55),(569,55),(569,90),(655,90),(655,269),(592,269),(592,332),(568,332),(509,354),(509,390),(443,390),(443,354),(185,354),(185,323),(141,323),(141,267),(126,260),(78,260),(46,234)],(478,390))
f2=canon([(121,111),(216,111),(226,119),(401,119),(401,83),(510,83),(510,18),(676,18),(690,28),(690,62),(666,62),(666,341),(592,341),(592,359),(569,359),(528,381),(513,381),(513,415),(443,415),(443,390),(185,390),(185,296),(121,296)])
f3=canon([(121,118),(401,118),(401,83),(510,83),(510,18),(676,18),(690,28),(690,62),(666,62),(666,341),(513,341),(513,415),(443,415),(443,410),(318,410),(318,390),(185,390),(185,296),(121,296)])
f4=canon([(145,290),(505,290),(505,116),(401,116),(401,83),(510,83),(510,16),(690,16),(690,353),(513,353),(513,415),(443,415),(443,408),(145,408)])
lowwest=canon([(121,116),(234,116),(234,251),(363,251),(363,116),(505,116),(505,294),(121,294)])
# Upper L / low western hall caps must not become a ground-level courtyard.
foot=CS([basement])+CS([f1])+CS([f2])+CS([f3])+CS([f4])
add(foot.offset(.5).extrude(.7),5,'outline_following_terrain_base')
add(poly(basement,.65,2.6),0,'B1_wide_left_perimeter_partly_exposed_approx')
add(poly(f1,.65,2.6),5,'terrain_under1F_outside_B1_not_floating')
add(poly(f1,2.55,6.05),0,'1F_broad_halls_and_right_room_strip')
add(poly(f2,6.0,9.55),1,'2F_full_context_halls_not_void')
add(poly(f3,9.5,13.05),1,'3F_full_context_halls_not_void')
add(poly(f4,13.0,16.55),0,'4F_L_rooms_and_front_projection')
# Deep local recess below projecting front row; front lower faces differ by floor.
# Source-plan front4F y408 versus2F y390 gives 1.2 unit cantilever.
# Narrow columns remain structural underneath the overhang, not a filled box.
for x in [-20,-14.3,-8.6]:block(x-.22,x+.22,.55,1.0,2.55,13.05,0,'front_projection_support_column')
# Shared projecting main stair tower; roof access height is bounded approximate.
core=canon([(443,327),(478,327),(478,359),(513,359),(513,410),(507,415),(449,415),(443,410)])
add(poly(core,2.5,19.2),0,'main_attached_stair_tower_all_floors')
# Main tower dark slit plus projecting upper bay visible in both photographs.
block(-.92,-.45,-.08,.10,3.0,16.65,2,'tower_vertical_glazed_slit')
for z in np.arange(3.2,16.6,.9):block(-.95,-.42,-.14,.01,z,z+.065,4,'tower_slit_transom')
block(-1.18,.2,-.45,.1,17.0,18.05,2,'tower_upper_projecting_glazed_bay')
for x in [-1.18,.16]:block(x,x+.07,-.5,-.37,16.95,18.1,4,'upper_bay_side_frame')
for z in [16.95,18.05]:block(-1.2,.24,-.5,-.37,z,z+.07,4,'upper_bay_cap_frame')
# Rear stair is registered to the other shared anchor; no detached R island.
rearcore=canon([(401,83),(510,83),(510,121),(401,121)])
add(poly(rearcore,2.55,17.45),0,'shared_rear_stair_bounded_roof_access')
def roof(p,z,n):
 cs=CS([p]);add(cs.extrude(.18).translate((0,0,z)),0,n+'_deck');add((cs-cs.offset(-.18)).extrude(.48).translate((0,0,z+.1)),0,n+'_low_parapet')
roof(f3,13.02,'3F_lower_body_roof');roof(lowwest,13.04,'3F_west_hall_roof_outlines');roof(f4,16.52,'R_highest_L_roof')
# Front windows: source photograph787 has discrete upper bays and lower continuous bands.
for z,y,xs in [(13.75,.42,[-20.1,-16.9,-13.7,-10.5,-7.3,-4.1]),(10.2,1.61,[-17.8,-14.6,-11.4,-8.2,-5.0]),(6.7,1.61,[-17.8,-14.6,-11.4,-8.2,-5.0])]:
 for x in xs:
  yy=(.3333 if z>9 and z<13 and x>-10.0 else y)
  block(x-1.25,x+1.25,yy-.09,yy+.12,z,z+1.55,3,'left_front_window_proxy')
  for xx in [x-1.25,x,x+1.25]:block(xx-.045,xx+.045,yy-.17,yy+.02,z-.04,z+1.59,4,'left_front_window_mullion')
  for zz in [z,z+1.55]:block(x-1.3,x+1.3,yy-.17,yy+.02,zz-.045,zz+.045,4,'left_front_window_transom')
# Right wing ends behind tower. Front is y4.13 upper and y4.93 lower.
for z,y in [(13.75,4.13),(10.2,4.93),(6.7,4.93)]:
 for x in [4.25,7.7,11.15]:
  block(x-1.5,x+1.5,y-.08,y+.1,z,z+1.55,3,'right_retreat_front_window')
  for xx in [x-1.5,x,x+1.5]:block(xx-.045,xx+.045,y-.16,y+.02,z-.04,z+1.59,4,'right_window_mullion')
  for zz in [z,z+1.55]:block(x-1.52,x+1.52,y-.16,y+.02,zz-.045,zz+.045,4,'right_window_transom')
# Ground rising to the rear/right first occupied level, footprint-bounded approximate hillside.
add(poly(f2,.65,6.03) ^ cube(2,15,8,28,0,6.1),5,'rear_right_upslope_contacts_first_occupied_level')
# Side coarse bands are explicitly approximate: no unseen detailed window survey claim.
for z in [6.8,10.3,13.85]:
 for y in [7,11,15,19,23]:
  xx=14.13 if z>13 else 12.53
  block(xx-.05,xx+.08,y-1.4,y+1.4,z,z+1.3,3,'east_side_approx_window')
# Attached right1F external stair footprint; approximate slope reaches the landing.
# Coordinates from1F right steps, anchored at same main tower.
x0,x1=(592-478)/15,(743-478)/15;y0,y1=(390-372)/15,(390-322)/15
for i in range(9):
 xo=743-i*3.5;yb=372-i*2.6;xi=xo-3.55;yi=yb-2.65
 tread=canon([(592,yb),(xo,yb),(xo,322),(xi,322),(xi,yi),(592,yi)],(478,390))
 add(poly(tread,.6,1.0+(i+1)*1.58/9),0,'right_L_turn_external_stair_tread')
# Inner landing reaches the main1F doorway while preserving the turn in plan.
block(x0, (711.5-478)/15, (390-348.6)/15, (390-322)/15, .6, 2.58, 0,'right_L_stair_inner_landing')
block(x0-.1,x0+.3,y1-.1,6.0,.6,2.6,0,'right_stair_landing_connects_main1F')
# Front main-stair entrance platform is part of the main building, not foreground gate.
block(-2.6,2.5,-1.6,.2,.6,2.55,0,'main_entry_platform_grounded')
for i in range(7):block(-2.3,2.2,-3.7+i*.3,-1.5,.65,.9+(i+1)*1.65/7,0,'main_entry_attached_steps')
# Rear rising grade follows actual main-body boundary, no surrounding campus or portal.
add(((CS([f1])+CS([f2])).extrude(2.1).translate((0,0,.6)) ^ cube(-40,20,16,28,0,3)),5,'rear_rising_grade_proxy')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學傳播學院主樓','revision':'v3','scope':'complete main body B1 and1-4F, highest L roof, attached front tower and right1F steps; excludes foreground portal and adjacent brick building','nominal_scale_mm_per_approx_design_unit':SCALE,'coordinate_transform':'landscape reading X=(pixelX-478)/15,Y=(415-pixelY)/15;1F/B1 anchorY390; no mirror or compass claim','outlines':{'B1':basement,'1F':f1,'2F':f2,'3F':f3,'4F':f4,'lowwest':lowwest,'front_core':core,'rear_core':rearcore},'floor_z_design':[2.55,6.05,9.55,13.05,16.55],'registration':{'B1':[478,390],'1F':[478,390],'2F':[478,415],'3F':[478,415],'4F':[478,415],'R':[478,415]},'limits':['Unmeasured heights/terrain approximate','Lower central blank is3F roof, not open-ground courtyard','Source photos capture dates unknown;not verified2026 state','Unseen small fenestration approximate','R detached stair diagram not positioned as independent wing','Source rights unresolved; no broad license','No physical print or support-free guarantee']}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
# Preserve original surface/material partitions through simplification: no nearest-triangle material spill.
m=Manifold(m.to_mesh()).set_tolerance(.001).simplify(.001)
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
features.update(material_provenance='Original Boolean surface run IDs retained through float32 generation and simplification; no nearest-centroid recoloring',parts=part_records)
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
