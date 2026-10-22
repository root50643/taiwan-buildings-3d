"""HCU Hsuan Fo Hall / 玄奘大學慈恩精舍選佛場. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('stone_platform','#999B96',255),('warm_gray_walls','#C2C3B9',255),('timber_cladding','#AE8960',255),('dark_metal_frames','#303A3B',255),('roof_graphite','#50595B',255),('glass_gray_blue','#839B9C',95)]
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

# Display millimetres, photo-proportion approximation, +X east, +Y north.
box((0,0,1.5),(214,126,3),0,'bounded_display_ground_not_full_site')
box((0,0,5),(174,82,6),0,'hall_floor_platform')
box((0,49,5.5),(174,20,5),0,'north_shared_corridor_floor_cut_at_neighbor_boundary')
box((95,0,5),(24,90,4),0,'east_stone_paved_landing')
for i in range(4):box((104+i*2.5,0,4-i*.6),(5,77,2),0,'broad_east_entrance_steps_approximate')
# Thin hollow hall shell with genuine openings (glazing remains a real solid sheet).
shell=Manifold.cube((170,80,34),True).translate((0,0,25))-Manifold.cube((165,75,40),True).translate((0,0,26))
# East: south large window, central sliding entrance, north gray name-panel pier.
for y,w,z,h in [(-26,23,24,25),(3,29,22,29)]:shell-=Manifold.cube((8,w,h),True).translate((85,y,z))
# South: western long windows and shifted eastward door, not old proposal position.
for x,w,z,h in [(-45,53,24,18),(22,24,22,29)]:shell-=Manifold.cube((w,8,h),True).translate((x,-40,z))
# North entry aligns south at x=22. Remaining elevation has flat cabinet leaves.
shell-=Manifold.cube((24,8,29),True).translate((22,40,22))
add(shell,1,'gray_hollow_wall_shell_with_actual_openings')
def glazed(axis,pos,c,w,z,h,count,name):
 if axis=='x':
  box((pos,c,z),(.9,w,h),5,name+'_glass_sheet')
  for u in np.linspace(c-w/2,c+w/2,count+1):box((pos,u,z),(1.4,1.05,h+1.2),3,name+'_vertical_frame')
  for zz in [z-h/2,z+h/2]:box((pos,c,zz),(1.4,w+1,1.2),3,name+'_horizontal_frame')
 else:
  box((c,pos,z),(w,.9,h),5,name+'_glass_sheet')
  for u in np.linspace(c-w/2,c+w/2,count+1):box((u,pos,z),(1.05,1.4,h+1.2),3,name+'_vertical_frame')
  for zz in [z-h/2,z+h/2]:box((c,pos,zz),(w+1,1.4,1.2),3,name+'_horizontal_frame')
glazed('x',85,-26,23,24,25,4,'east_window');glazed('x',85,3,29,22,29,4,'east_sliding_door')
glazed('y',-40,-45,53,24,18,7,'south_long_window');glazed('y',-40,16,12,22,29,2,'south_shifted_entry_part_open');glazed('y',40,16,12,22,29,2,'north_aligned_entry_part_open')
# Upper wood band, shallow gables on east and west, actual two-slope roof.
for y in [-39,39]:box((0,y,44),(170,2.5,8),2,'wood_upper_long_elevation')
for x in [-84,84]:
 g=CrossSection([[( -40,40),(40,40),(40,48),(0,55),(-40,48)]]).extrude(2.5).rotate((90,0,90)).translate((x-1.25,0,0))
 add(g,2,'east_west_shallow_timber_gable')
# Roof slabs are continuous along X and slope across Y, not a flat lid.
for sign in [-1,1]:
 pts=[(-44*sign,47.3),(0,55.0),(0,57.0),(-44*sign,49.3)]
 poly=CrossSection([pts if sign==1 else pts[::-1]])
 add(poly.extrude(180).rotate((90,0,90)).translate((-90,0,0)),4,'low_dual_pitch_main_roof')
# West two small louver grilles on timber, no invented door.
for y in [-25,25]:
 box((-85.5,y,43),(1,9,7),3,'west_small_louver_dark_recess')
 for z in [40.5,42,43.5,45]:box((-86,y,z),(1.2,8,.9),1,'west_small_louver_blade')
# Flat north cabinet units; narrow vent strip, distinct dark mid-entry break.
for lo,hi in [(-82,9),(35,82)]:
 for a,b in zip(np.linspace(lo,hi,round((hi-lo)/13)+1)[:-1],np.linspace(lo,hi,round((hi-lo)/13)+1)[1:]):
  box(((a+b)/2,40.3,23),(b-a-.55,1.5,26),2,'north_flat_cabinet_leaf')
 box(((lo+hi)/2,40.5,38.3),(hi-lo,1.1,2.8),3,'north_narrow_vent_band')
# Distinct low canopy structures; no west canopy invented.
def canopy(x0,x1,y0,y1,label,nx,ny):
 box(((x0+x1)/2,(y0+y1)/2,40.8),(x1-x0,y1-y0,.9),5,label+'_translucent_roof_sheet')
 for x in np.linspace(x0,x1,nx+1):box((x,(y0+y1)/2,40),(1.2,y1-y0+1,2.6),3,label+'_grid_x')
 for y in np.linspace(y0,y1,ny+1):box(((x0+x1)/2,y,40),(x1-x0+1,1.2,2.6),3,label+'_grid_y')
canopy(83.8,103,-44,44,'east_low_canopy',3,12)
canopy(-86,84,-55,-39,'south_low_canopy',22,3)
canopy(-86,84,39,58,'north_shared_corridor_cut_boundary_no_outer_columns',22,3)
# Attached canopy wall brackets, not ground-standing invented columns.
for x in np.linspace(-80,78,12):
 beam((x,-39,36),(x,-53,39.5),1.3,3,'south_canopy_wall_bracket')
# South west sloped approach slab and open handrail, simplified near-site only.
ramp=CrossSection([[(-84,2.8),(-15,2.8),(-15,9.5),(-84,4.7)]]).extrude(11).rotate((90,0,0)).translate((0,-42,-.5));add(ramp,0,'south_west_ramp')
for x in [-82,-65,-48,-31,-16]:
 z=4.7+(x+84)*4.8/69;beam((x,-52.5,z-.7),(x,-52.5,z+10),1.1,3,'ramp_handrail_post')
beam((-82,-52.5,14.84),(-16,-52.5,19.43),1.25,3,'ramp_open_handrail')
FEATURES=dict(name='玄奘大學慈恩精舍選佛場',school='玄奘大學',slug='hcu-hsuan-fo-hall',selected_version='2025 paper completed exterior; opening 2025-05-07; photo capture unknown',estimated_not_surveyed=True,adjacent_kaishan_hall_excluded=True,north_shared_corridor_cut_boundary=True,no_invented_outer_columns=True,low_dual_pitch_roof=True,west_two_small_louvers=True,south_north_entries_aligned=True,north_flat_cabinets_not_proposal_louvers=True,unknown_plan_not_used=True,no_actual_print=True,support_free_certified=False,all_materials_opaque=False)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.0005).simplify(.0005)
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
