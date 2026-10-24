"""政大研究大樓 — 官方PDF記錄之修繕前瓷磚外觀版，非2026修繕後現況。"""
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


SCALE=3.0
palette=[('ground_concrete','#92958D',255),('historic_pale_tile_proxy','#D0D0C4',255),('gray_roof_coping','#777D78',255),('opaque_recessed_window','#435559',255),('pale_window_frame','#B4B8AF',255),('muted_warm_recess_wall','#B6A48B',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
# Plan X right, Y up. Photograph717 named facade is short end -X; adjacent long face +Y.
# Baseline common 6F end-stair image anchors: x152..714, y253.
# Design units are proportionally chosen, not surveyed metres.
block(-30,30,-16.5,16.5,0,.6,0,'minimal_display_apron_not_basement')
H=3.5; Z=.6
# Lower mass, with actual 1F central entrance recess left open.
base=cube(-28,28,-14.5,14.5,Z,Z+6*H)
base=base-cube(-6.5,6.5,-14.6,-8.8,Z-.01,Z+H-.4)
# 2F central front wall is slightly recessed behind floor edge and columns.
base=base-cube(-12,12,-14.6,-13.2,Z+H+.2,Z+2*H-.35)
add(base,1,'1F_6F_common_rectangular_main_body_with_entry_recess')
block(-6.5,6.5,-8.95,-8.7,Z+.15,Z+H-.55,3,'recessed_entry_door_proxy')
for x in [-6.5,0,6.5]:block(x-.12,x+.12,-9.08,-8.7,Z+.1,Z+H-.5,4,'entry_mullions')
for x in [-12,-4.2,4.2,12]:block(x-.24,x+.24,-14.5,-13.05,Z+H-.1,Z+2*H+.1,5,'2F_plan_front_columns')
# 7/8/9 occupancy polygons follow registered end stair anchors, not raster frames.
# Front central notch begins at7F; rear steps from7 to8, large9F terrace.
for floor,rear in [(7,13.2),(8,10.8),(9,6.9)]:
 z=Z+(floor-1)*H
 if floor<9:
  body=cube(-28,28,-14.5,rear,z-.04,z+H)
  body=body-cube(-12,12,-14.6,-10.8,z-.1,z+H+.1)
 else:
  body=cube(-28,28,-14.5,rear,z-.04,z+H)
  body=body-cube(-12,12,-14.6,-10.8,z-.1,z+H+.1)
  body=body-cube(-12,12,3.2,rear+.1,z-.1,z+H+.1)
 # X-marked upper atrium void: resolved in source review before final freezing.
 # Simplified upper-hall void only, capped by9F; not a certified full interior section.
 if floor in (7,8):
  body=body-cube(-12,12,-1.9,3.5,z-.1,z+H+.1)
  if floor==8:body=body+cube(-5.3,5.3,-1.9,3.5,z-.04,z+H)
 add(body,1,f'{floor}F_registered_occupied_volume')
 # Historic narrow parapet along rear stepped terrace perimeter.
 block(-28.05,28.05,rear-.12,rear+.2,z+H-.03,z+H+.28,2,f'{floor}F_rear_coping')
 for a,b in [(-28,-12),(12,28)]:
  block(a,b,-14.62,-14.35,z+H-.05,z+H+.2,2,f'{floor}F_front_end_coping')
  block(a-.1,a+.15,-14.5,rear,z+H-.05,z+H+.2,2,f'{floor}F_end_roof_edge')
# 7/8 side mids project slightly per plan; small attached local volumes.
for side in [-1,1]:
 x0,x1=(-29.1,-27.9) if side<0 else (27.9,29.1)
 block(x0,x1,.0,6.0,Z+6*H,Z+8*H,1,'7F_8F_local_side_projection')
# 9F balcony: exposed 8F slab, not an extra occupied bar across rear.
block(-28,28,3.2,12.5,Z+8*H-.35,Z+8*H,2,'9F_rear_terrace_floor')
block(-28,28,12.15,12.5,Z+8*H-.05,Z+8*H+.9,1,'9F_rear_terrace_parapet')
for x in [-28,27.65]:block(x,x+.35,6.8,12.5,Z+8*H-.05,Z+8*H+.9,1,'9F_terrace_end_parapet')
# R: only three cores above H-shaped9F roof; broadH is NOT a tenth floor.
for a,b in [(-28,-18.7),(18.7,28)]:
 block(a,b,-6.3,-2.9,Z+9*H-.04,Z+9*H+2.5,1,'R_end_stair_core_only')
 block(a-.15,b+.15,-6.45,-2.75,Z+9*H+2.45,Z+9*H+2.8,2,'R_end_core_cap')
block(-4.7,4.7,-6.4,-.7,Z+9*H-.04,Z+9*H+2.8,1,'R_central_elevator_stair_core_only')
block(-4.85,4.85,-6.55,-.55,Z+9*H+2.75,Z+9*H+3.05,2,'R_central_core_cap')
# Photo717 strongest registration: named SHORT END -X, adjacent +Y long face.
# Fine window/glass-block counts remain opaque proportional surface proxies.
for floor in range(1,10):
 z=Z+(floor-1)*H+.7
 rear=14.5 if floor<=6 else {7:13.2,8:10.8,9:6.9}[floor]
 for yy,w in [(-12,2.4),(-.2,.95),(3.5,.95),(9.7,1.6),(12.1,1.4)]:
  if yy+w/2>rear:continue
  if floor in (7,8) and 0<=yy<=6:continue
  block(-28.14,-27.84,yy-w/2,yy+w/2,z,z+1.9,3,'717_short_named_face_window_proxy')
  block(-28.25,-27.8,yy-w/2-.07,yy+w/2+.07,z-.08,z+.04,4,'717_window_sill')
  if w>1.4:block(-28.26,-27.8,yy-.07,yy+.07,z,z+1.9,4,'717_window_mullion')
 # End stair glass block proxy is a vertical stack at registered stair Y.
 if floor>=2:
  block(-28.15,-27.8,-5.6,-3.5,z-.1,z+2.1,3,'717_stair_glass_block_dark_proxy')
  for yy in [-5.6,-5.075,-4.55,-4.025,-3.5]:block(-28.28,-27.8,yy-.045,yy+.045,z-.1,z+2.1,4,'717_glass_block_grid_vertical')
  for zz in [z-.1,z+.45,z+1,z+1.55,z+2.1]:block(-28.28,-27.8,-5.65,-3.45,zz-.045,zz+.045,4,'717_glass_block_grid_horizontal')
 if floor in (7,8):
  for yy in [1.5,4.5]:
   block(-29.24,-28.95,yy-1.0,yy+1.0,z,z+2.0,3,'717_projected_upper_room_window')
   block(-29.36,-28.9,yy-1.1,yy+1.1,z-.1,z+.04,4,'717_projected_upper_sill')
   block(-29.36,-28.9,yy-.06,yy+.06,z,z+2,4,'717_projected_upper_mullion')
 # Adjacent long+Y face: only broad bay rhythm; no assertion of unseen rear fidelity.
 for xx in [-25,-20,-15,15,20,25]:
  block(xx-1.3,xx+1.3,rear-.15,rear+.13,z,z+1.6,3,'adjacent_long_face_end_window_proxy')
  block(xx-1.4,xx+1.4,rear-.18,rear+.24,z-.08,z+.04,4,'adjacent_long_face_sill')
# 718 coarse central recessed facade, bounded to lower three floors; exact span unmeasured.
# Lower central recesses are cut into facade, never fabricated freestanding annex.
# Cut all shared geometry before colored surface additions so existing 1F entry remains.
for floor in [1,2,3]:
 z=Z+(floor-1)*H
 cutter=cube(-11.8,11.8,13.7,14.7,z+.25,z+H-.4).as_original();material_for_id[cutter.original_id()]=5
 parts=[p-cutter for p in parts]
 # Width is constrained to central plan span; depth/color are local approximate proxy.
 block(-11.8,11.8,13.62,13.8,z+.3,z+H-.45,3,'718_recessed_opaque_back_window_proxy')
 for xx in [-12,-4,4,12]:block(xx-.28,xx+.28,13.65,14.65,z-.02,z+H+.03,5,'718_central_recess_piers')
 block(-12,12,14.35,14.65,z+H-.43,z+H+.02,5,'718_central_warm_spandrel')
# Remaining upper central face glazing is restrained opaque proxy, not copied unseen windows.
for floor in [4,5,6,7,8]:
 z=Z+(floor-1)*H+.75;rear=14.5 if floor<=6 else {7:13.2,8:10.8}[floor]
 for xx in [-8,0,8]:block(xx-2.6,xx+2.6,rear-.12,rear+.1,z,z+1.55,3,'adjacent_long_upper_bay_proxy')
# Short-side foreground named strip is retained pale; lettering omitted at this scale.
block(-28.08,-27.9,-9.1,-7.2,Z+2*H,Z+9*H,1,'717_pale_name_strip_no_invented_lettering')
for zz in [Z+H,Z+3*H,Z+6*H]:
 block(-28.23,-27.8,-14.5,14.5,zz-.12,zz+.06,2,'717_short_face_horizontal_band')
# Coarse R louver on the observed end core; other cores remain neutral geometry.
block(-28.18,-27.8,-5.9,-3.3,Z+9*H+.6,Z+9*H+1.6,3,'R_observed_end_core_louver_proxy')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'政大研究大樓 — 官方PDF記錄之修繕前瓷磚外觀版，非2026修繕後現況','geometry_revision':'v3-short-face-registration','coordinate_transform':'plan right +X, plan upper +Y;717 named short end -X; adjacent long face +Y;718 local same-corner candidate, no opposite facade proof; first-model image comparison corrects earlier source hypothesis','nominal_scale_mm_per_approx_design_m':SCALE,'main_bounds_design':[-28,28,-14.5,14.5],'floor_height_approx_design':H,'ground_Z':Z,'limits':['Unknown exact storey/parapet heights proportional approximation','Fine windows behind occlusion restrained proxies, rear not mirrored','B1 below grade not exposed as extra storey','R only3cores; H shape is9F roof','7/8 X upper hall void proxy only;6F full interior omitted; ceiling interpretation approximate','No copyrighted source pixels embedded','Source rights unresolved/private only/no broad license','No print test or support-free guarantee']}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.00005).simplify(.00005)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<1.2,(dist.max(),centers[start:start+500][dist.argmax()].tolist());maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),'float32 export degeneracy: repair generator, not QA';nn=cr/np.linalg.norm(cr,axis=1)[:,None]
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
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});el(r,'metadata',{'name':'Title'}).text='政大研究大樓 — 官方PDF記錄之修繕前瓷磚外觀版，非2026修繕後現況';res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0,'name':'政大研究大樓 — 官方PDF記錄之修繕前瓷磚外觀版，非2026修繕後現況'});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
