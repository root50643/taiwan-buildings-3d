"""MKC Sanzhi Common Classroom Building / 馬偕醫護管理專科學校三芝綜合大樓. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_plinth','#89938B',255),('gray_white_structure','#BAC0BD',255),('concrete_and_roof_edge','#8C9291',255),('brown_louvers_frames','#544C45',255),('opaque_glazing','#53666C',255),('orange_red_brick','#AE7457',255),('orange_sunshade','#CE8C52',255),('gray_metal_roof','#7E8789',255)]
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

# Display mm, visual proportions, arbitrary axes: street +Y, lake -Y.
box((0,0,1.5),(258,92,3),0,'display_base_not_surveyed_terrain')
body=Manifold.cube((240,60,96),True).translate((0,0,54))
# Exposed sloping plinth is a bounded approximation, not a basement interior.
box((0,0,5),(240,60,6),2,'exposed_base')
add(Manifold.hull_points([(x,y,z) for x,top in [(-120,5),(120,9.5)] for y in [29.7,31.4] for z in [3,top]]),2,'bounded_sloping_exposed_street_base_approximation')
box((0,0,57),(24,65,102),5,'central_projected_brick_service_core')
windows=[]
def window(x,y,z,w,h,label):
 global body
 sign=1 if y>0 else -1
 body-=Manifold.cube((w,4,h),True).translate((x,y,z))
 box((x,y-sign*1.5,z),(w,2.2,h),4,label+'_opaque_glass')
 windows.append(dict(x=x,y=y,z=z,w=w,h=h,label=label))
# Five floors: larger ground and first-upper glazing, three upper recessed louver rows.
for sign in [-1,1]:
 y=sign*30
 for side in [-1,1]:
  for j in range(8):
   x=side*(19+13*j)
   for level in range(5):
    z=16+18*level
    if sign==1 and side==-1 and j in [0,1] and level==0:continue
    window(x,y,z,9.2,11.5,('street' if sign==1 else 'lake')+'_window')
    box((x,y+sign*.1,z-7.1),(10.5,1.8,3.0),5,'brick_spandrel_band')
    if level>=2:
     for dz in [-3,-1,1,3]:box((x-2,y+sign*.35,z+dz),(4.2,1.8,.95),3,'simplified_upper_louver')
    else:
     box((x,y-sign*.1,z),(1.0,2,11.8),3,'lower_window_mullion')
     box((x,y-sign*.1,z+1),(9.3,2,1.0),3,'lower_window_transom')
   # Grey frame columns and projecting orange fins at intermediate levels, not top row.
   if sign==1 and side==-1 and j==0:
    box((x-6.1,y+.4*sign,64),(2.0,2.8,76),1,'entry_column_terminated_at_first_floor_beam')
   else:box((x-6.1,y+.4*sign,55),(2.0,2.8,94),1,'gray_vertical_structural_grid')
   for level in [1,2,3]:
    z=16+18*level
    box((x-5.7,y+sign*2.4,z),(1.6,6.5,13.5),1,'fin_gray_edge')
    box((x-5.7,y+sign*3.4,z),(1.7,4.7,11.4),6,'orange_vertical_sunshade')
   if j%2==0 and not(sign==1 and side==-1 and j==0):box((x,y+sign*1.3,14),(9.4,3.5,6),3,'ground_brown_privacy_screen')
  for z in [7,25,43,61,79,97]:box((side*66,y+.2*sign,z),(108,2.5,2.7),1,'horizontal_structural_grid')
# Central street: orange brick pier flanked by two narrow full-height glazing bands.
for x in [-8,8]:
 box((x,32.65,48),(4.2,1.6,75),4,'street_core_narrow_glazing')
 for z in range(15,85,9):box((x,33.1,z),(4.4,1.5,.95),3,'street_core_window_transom')
# Lake side central glass is broad, explicitly not a mirror of the street face.
box((0,-32.65,49),(18,1.7,76),4,'lake_core_broad_continuous_glazing')
for x in [-6,0,6]:box((x,-33.1,49),(.95,1.7,76),3,'lake_core_glass_mullion')
for z in range(15,86,9):box((0,-33.1,z),(18,1.7,.95),3,'lake_core_glass_transom')
# Two short ends: brick wall, offset glazed stair strip and narrow gray-wall slots.
for sign in [-1,1]:
 x=sign*120
 box((x,0,53),(1.8,32,94),5,'short_end_large_brick_wall')
 gy=-22 if sign==1 else 22
 box((x+sign*.5,gy,48),(1.8,11.5,83),4,'offset_end_stair_glass')
 for z in range(12,91,9):box((x+sign*1,gy,z),(1.7,12,.95),3,'end_glazing_transom')
 for y in [gy-3,gy+3]:box((x+sign*1,y,48),(1.7,.95,83),3,'end_glazing_mullion')
 for z in [35,62,88]:
  box((x+sign*.4,-gy,z),(1.8,10,2.1),4,'short_end_gray_wall_narrow_slot')
 if sign==-1:
  for z in [25,43]:
   box((x+sign*1.6,gy,z),(4.2,12,1.3),2,'visible_small_stair_landing')
   box((x+sign*3,gy,z+2),(1.2,12,3.2),3,'simplified_end_landing_guard')
 # End exit steps, distinct from adjacent excluded low green court.
 for k in range(4):box((x+sign*(2+k*1.2),gy,3+(4-k)*.65),(3,11,(4-k)*1.3),2,'end_exit_stair')
window(-23,30,18,20,13.5,'street_entry_recess_meets_stair_landing')
box((-23,29.3,18),(1.0,1.8,13.5),3,'entry_door_center_mullion')
add(body,1,'five_storey_complete_rectangular_closed_envelope')
# Deep eaves, long ridge along X; two wings and a higher short central cap.
def roof(x0,x1,eave,ridge,depth,label):
 # Filled roof wedge under the thin outer roof planes, touching solid body.
 pts=[(x,y,z) for x in [x0+.8,x1-.8] for y,z in [(-29,100),(29,100),(-29,eave),(0,ridge),(29,eave)]]
 add(Manifold.hull_points(pts),1,label+'_gable_fill')
 # Two inclined roof sheets with robust 1.5mm vertical thickness.
 for sign in [-1,1]:
  pts=[(x,y,z+dz) for x in [x0,x1] for y,z in [(0,ridge),(sign*depth,eave)] for dz in [-.8,.8]]
  add(Manifold.hull_points(pts),7,label+'_sloped_sheet')
 box(((x0+x1)/2,0,ridge+.15),(x1-x0,1.4,1.6),7,label+'_printable_flat_ridge_cap')
 # Underside fascia at long eaves, overlapping sheet for single shell.
 for sign in [-1,1]:box(((x0+x1)/2,sign*(depth-.4),eave-.1),(x1-x0,1.6,1.5),2,label+'_thin_eave_edge')
roof(-124,-11,102,110,35,'left_long_roof')
roof(11,124,100.5,108.5,35,'right_long_roof_lower')
roof(-14,14,107,115,37,'central_short_raised_cap')
# Main entrance left of central service core, solid printable risers.
box((-23,31.5,11.3),(20,5,1.6),2,'main_entrance_landing_connected_to_recess')
for k in range(10):
 h=1+(10-k)*.8;box((-23,34+k*1.1,3+h/2),(20,2.4,h),2,'main_entrance_step')
for x in [-33.3,-12.7]:beam((x,44,4),(x,29,13),1.6,2,'entrance_side_wall_slope')
parts=[p.scale((-1,1,1)) for p in parts]
# Reflect design X so street elevation has entrance and small-platform end on photo-left.
FEATURES=dict(name='綜合大樓（共同教室大樓）',school='馬偕醫護管理專科學校',campus='三芝校區',slug='mkc-common-building',aboveground_floors=5,selected_version='Architect exterior photographs without PV; 2019 completion is not photo capture date',roof_sections=3,central_cap_raised=True,roof_PV_excluded=True,orthophoto_capture_date_unknown=True,NLSC2024_not_capture_year=True,front_rear_core_glazing_different=True,underground_interior_excluded=True,adjacent_buildings_and_low_green_court_excluded=True,rear_base_fine_openings_approximate=True,sloping_base_approximate=True,estimated_not_surveyed=True,all_materials_opaque=True,no_actual_print=True,support_free_certified=False,window_records=windows)
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
