"""NCCU Fengyu Hall — source-relative approximate complete main-building exterior."""
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


SCALE=3.8
X_RATIO=.7 # v2 photo correction: garden extent28, road width22; not emergency-raster ratio
palette=[('base_concrete','#96978D',255),('warm_tile_proxy','#C7BEA8',255),('pale_window_frames','#DDDCD2',255),('opaque_bluegray_glass','#506B74',255),('stone_cladding','#9B8C76',255),('mirror_wall_proxy','#788C8C',255),('equipment_gray','#969D9C',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0*X_RATIO,x1*X_RATIO,y0,y1,z0,z1),c,n)
# Coordinate frame: road short facade -X; adjacent garden long facade -Y.
# All design lengths proportional approximation, not surveyed metres.
block(-25,21,-12.5,12,0,.65,0,'display_ground')
# Road is higher than garden; small localized apron, not an invented wing.
block(-25,-20,-12,11.5,.6,1.4,0,'raised_road_entrance_apron')
block(-20,20,-7.4,11,.6,4.45,1,'B1_solid_back_mass_recessed_from_colonnade')
block(-20,20,-11,11,4.25,12.5,1,'1F_2F_shared_rectangle_no_setback')
for x in [-19.55,-10,0,10,19.55]:
 block(x-.45,x+.45,-11.08,-10.1,.6,12.5,4,'five_piers_define_four_garden_bays')
# Real void between five piers, ceiling and recessed mirror wall remains open.
block(-19.05,19.05,-7.62,-7.35,1.15,3.75,5,'B1_recessed_mirror_wall_not_fully_open_storey')
for x in [-19,-10,0,10,19]:block(x-.08,x+.08,-7.72,-7.35,1.1,3.85,2,'B1_mirror_vertical_frame')
for z in [1.1,3.2,3.8]:block(-19.1,19.1,-7.72,-7.35,z-.08,z+.08,2,'B1_mirror_transom')
# Upper two rows, four broad main bays; silver frames reflect completed PDF not 1966 grid.
for level,z in enumerate([5.0,9.0]):
 for bay in range(4):
  a=-19.05+bay*9.75;b=a+8.9
  block(a,b,-11.13,-10.8,z,z+2.7,3,'garden_four_bay_glazing_row_'+str(level+1))
  for x in [a,a+2.225,a+4.45,a+6.675,b]:block(x-.075,x+.075,-11.29,-10.8,z-.06,z+2.76,2,'garden_modern_mullion')
  for zz in [z,z+1.9,z+2.7]:block(a-.06,b+.06,-11.29,-10.8,zz-.075,zz+.075,2,'garden_modern_transom')
block(-20,20,-11.12,-10.9,4.25,5,4,'garden_stone_spandrel_lower')
block(-20,20,-11.12,-10.9,7.8,8.55,4,'garden_stone_spandrel_upper')
def entry(x0,x1,y0,y1,z0,z1,c,n):block(x0,x1,y0*.78,y1*.78,z0,z1,c,n)
# Short road wall has central high window, thin flanking vertical slots and attached entry.
block(-20.15,-19.8,-1.4,1.4,7,11.25,3,'road_high_central_window')
for y in [-1.4,-.467,.467,1.4]:block(-20.3,-19.8,y-.075,y+.075,6.95,11.3,2,'road_window_vertical_frame')
for z in [7,7.85,8.7,9.55,10.4,11.25]:block(-20.3,-19.8,-1.47,1.47,z-.07,z+.07,2,'road_window_transom')
for y in [-7.8,7.8]:block(-20.12,-19.8,y-.1,y+.1,5,11.8,3,'road_narrow_vertical_slot')
entry(-20.2,-19.8,-2.5,2.5,3.45,6.35,3,'road_entry_door')
for y in [-2.5,0,2.5]:entry(-20.34,-19.8,y-.08,y+.08,3.4,6.4,2,'road_door_frame')
entry(-22.4,-19.8,-3.35,3.35,6.1,6.75,4,'attached_rectangular_entry_canopy')
for y in [-3.1,3.1]:entry(-22.4,-21.8,y-.25,y+.25,1.35,6.7,4,'entry_canopy_pier')
for i in range(9):entry(-24.5+i*.5,-19.8,-2.8,2.8,1.35,1.6+(i+1)*.3,4,'nine_entry_steps')
# Unseen back/remote facades intentionally neutral; no mirrored glazing claim.
block(-20.04,20.04,-11.04,11.04,12.45,12.8,2,'flat_roof_approximate_closure_RF_not_available')
# Visible circular rooftop equipment is equipment, not occupied tower; approximate coarse outline.
add(Manifold.cylinder(.65,2.15,2.15,32).translate((-16*X_RATIO,5.7,12.7)),6,'equipment_lower_base')
add(Manifold.cylinder(1.35,2.15,2.15,32).translate((-16*X_RATIO,5.7,13.3)),6,'equipment_broad_circular_body')
add(Manifold.cylinder(1.3,1.55,1.55,32).translate((-16*X_RATIO,5.7,14.6)),6,'equipment_upper_cylinder')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學風雩樓','scope':'complete three-storey main rectangle with attached entrance; B1+1F+2F, not four floors','coordinate_transform':'road short facade -X, garden four-bay long facade -Y; unregistered indoor stair handedness omitted','nominal_scale_mm_per_approx_design_m':SCALE,'main_bounds_design':[-14,14,-11,11],'main_aspect':28/22,'photo_correction':'v3 narrow road high window and entry, proud roof/pier interfaces preserve materials; v2: garden width28 / main total height12.15 is about2.30, guided by near-frontal1980s photo; no raster aspect forcing','floor_levels_mm':[.65*SCALE,4.25*SCALE,8.25*SCALE],'roof_mm':12.8*SCALE,'limits':['No RF plan: flat roof is approximate closure','Unknown rear and far-end windows neutral, not mirrored','B1 colonnade open to recessed mirror proxy, no invented interior','No historical garden/window-grid reconstruction','Road apron elevated relative garden; heights approximate','Equipment coarse visible silhouette not occupied floor','Source rights unresolved; private model only; no source pixels','No physical print test or support-free guarantee']}
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
