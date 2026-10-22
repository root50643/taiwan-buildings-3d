"""TTCS Barclay Main Hall / 南神本館（巴克禮紀念館）. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_plinth','#92958F',255),('restored_gray_white_washstone','#C5C5BA',255),('dark_brown_timber','#514035',255),('gray_window_surrounds','#777B74',255),('gray_cement_roof_tiles','#656A65',255),('opaque_miniature_glazing','#78878A',255),('gold_circle_cross','#CDB76D',255)]
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

# Display millimetres; X east, Y north. Ratios traced from report p209/p328/p323.
# Eave outline: 240 x 68; outer wings 52x68, center 36x56, links 50x46.
box((0,0,1.5),(250,80,3),0,'bounded_display_base_not_site')
blocks=[(-94,52,66),(94,52,66),(0,36,54),(-43,50,44),(43,50,44)]
outer=Manifold.batch_boolean([Manifold.cube((w,d,40),True).translate((x,0,23)) for x,w,d in blocks],OpType.Add)
inner=Manifold.batch_boolean([Manifold.cube((w-4,d-4,43),True).translate((x,0,25)) for x,w,d in blocks],OpType.Add)
inner=inner+Manifold.cube((234,10,43),True).translate((0,0,25))
shell=outer-inner
# Two actual floor plates; simplified interior, not a room-by-room replica.
for z in [3.5,22.5]:
 floor=Manifold.batch_boolean([Manifold.cube((w,d,1.4),True).translate((x,0,z)) for x,w,d in blocks],OpType.Add)
 if z>20:floor-=Manifold.cube((10,10,4),True).translate((0,0,z))
 add(floor,0,'two_storey_floor_plate_with_abstract_internal_access_void')
# Arched silhouettes in the local horizontal/height plane.
def arch(w,h,pointed=False):
 r=w/2; spring=h-(.95*w if pointed else r)
 if pointed:
  # Two circular ogive segments, approximate small-scale tracery silhouette.
  pts=[(-r,0),(r,0),(r,spring)]
  for t in np.linspace(0,1,13)[1:]:pts.append((r*(1-t),spring+.95*w*(1-(1-t)**1.6)))
  for t in np.linspace(0,1,13)[1:]:pts.append((-r*t,spring+.95*w*(1-t**1.6)))
 else:
  pts=[(-r,0),(r,0),(r,spring)]+[(r*math.cos(a),spring+r*math.sin(a)) for a in np.linspace(0,math.pi,25)[1:]]
 return CrossSection([pts])
def placed(cs,axis,c,pos,z,depth):
 m=cs.extrude(depth).rotate((90,0,0)).translate((c,pos+depth/2,z))
 return m if axis=='y' else m.rotate((0,0,-90))
windows=[]
def opening(axis,c,pos,z,w,h,pointed,name,door=False,open_interface=False):
 global shell
 cs=arch(w,h,pointed);shell-=placed(cs,axis,c,pos,z,6)
 # Thick surround extends outward and overlaps wall, not decorative floating sheet.
 surround=cs.offset(1.0)-cs.offset(-.15)
 add(placed(surround,axis,c,pos,z,3.0),3,name+'_projecting_arch_surround')
 if not open_interface:
  add(placed(cs,axis,c,pos,z,1.05),2 if door else 5,name+('_closed_timber_door' if door else '_opaque_glazing'))
  frame=cs-cs.offset(-.6);add(placed(frame,axis,c,pos,z,1.7),2,name+'_wood_frame')
  # Real small-scale raised muntins, clipped against arch.
  bars=CrossSection.square((.65,h),False).translate((-.325,0))
  for zz in np.arange(3,h-1,3):bars=bars+CrossSection.square((w,.65),False).translate((-w/2,zz))
  add(placed(bars^cs,axis,c,pos,z,1.8),2,name+'_simplified_muntins')
 windows.append(dict(axis=axis,c=c,pos=pos,bottom=z,width=w,height=h,pointed=pointed,door=door,open_interface=open_interface,name=name))
# North and south: three connector bays each level; central two upper / three lower.
for sign,side in [(1,'north'),(-1,'south')]:
 for center in [-43,43]:
  for dx in [-14,0,14]:
   for z in [6,26]:opening('y',center+dx,sign*22,z,6.2,12,False,side+'_link')
 for dx in [-5.8,5.8]:opening('y',dx,sign*27,26,6.5,14,True,side+'_central_upper')
 for dx in [-10,0,10]:opening('y',dx,sign*27,4.2 if dx==0 else 6,6.4,16 if dx==0 else 12.5,True,side+'_central_lower',door=dx==0)
 for center in [-94,94]:
  for dx in [-9,9]:
   opening('y',center+dx,sign*33,6,6.5,14,True,side+'_outer_lower',door=(sign==-1 and dx==(-9 if center==94 else 9)))
   # Southwest upper opening is actual rectangular corridor doorway, not symmetric window.
   if sign==-1 and center==-94 and dx==9:continue
   opening('y',center+dx,sign*33,26,6.5,14,True,side+'_outer_upper')
# East/west short sides: three upper round arches / lower pointed arches.
# placed(x) maps local c to global -Y; symmetric positions retain correct spacing.
for sign,side in [(-1,'west'),(1,'east')]:
 for c in [-21,0,21]:
  opening('x',c,sign*120,6,6.8,14,True,side+'_lower')
  opening('x',c,sign*120,26,6.8,13,False,side+'_upper')
# Actual SW upper corridor interface; no added imaginary closing wall or bridge.
cut=Manifold.cube((8,7,14),True).translate((-85,-33,30))
shell-=cut
for x in [-89.7,-80.3]:box((x,-33,30),(1.4,3.2,15.4),3,'SW_actual_interface_jamb')
box((-85,-33,37.7),(10.8,3.2,1.4),3,'SW_actual_interface_lintel')
# Short existing threshold only; boundary is display truncation, NOT real exterior end wall.
box((-85,-34.5,22.5),(10,5,1.4),0,'SW_interface_threshold_cut_at_display_boundary')
add(shell,1,'H_plan_two_storey_wall_shell_with_actual_openings')
# Horizontal stringcourse follows footprint, not across open recessed corners.
for x,w,d in blocks:
 band=Manifold.cube((w+1.2,d+1.2,1.0),True).translate((x,0,23))-inner
 add(band,3,'floor_stringcourse')
# Roofs are boolean envelope intersections, no internal vertical gable walls exposed.
# Outer longitudinal ridges 56; central 56; connecting transverse ridge 51.5.
def roof_ns(cx,w,d,eave,ridge,bottom):
 return CrossSection([[(cx-w/2,bottom),(cx+w/2,bottom),(cx+w/2,eave),(cx,ridge),(cx-w/2,eave)]]).extrude(d).rotate((90,0,0)).translate((0,d/2,0))
def roof_ew(cx,length,d,eave,ridge,bottom):
 return roof_ns(0,d,length,eave,ridge,bottom).rotate((0,0,90)).translate((cx,0,0))
# Gray-white gable infill inside each longitudinal roof edge.
for cx,w,d in [(-94,52,66),(94,52,66),(0,36,54)]:add(roof_ns(cx,w,d,43,56.2,41.8),1,'longitudinal_gable_infill')
roofparts=[roof_ns(cx,w,d,43.5,57,42.5) for cx,w,d in [(-94,54,69),(94,54,69),(0,38,57)]]
roofparts += [roof_ew(cx,94,47,43.5,52,42.5) for cx in [-43,43]]
roof=Manifold.batch_boolean(roofparts,OpType.Add)
# Cut bottom away only under roof envelope to form a substantial shell over interior.
# Kept filled attic volumes are intentional miniature simplification.
add(roof-roof.translate((0,0,-1.35)),4,'five_intersecting_roof_envelope_four_pairs_of_valleys')
# Roof surface seams modest relief, clipped to continuous roof envelope.
# Repeated grooves are omitted rather than invent exact historic tile counts.
for cx,w,d in [(-94,54,69),(94,54,69),(0,38,57)]:
 beam((cx,-d/2,57.05),(cx,d/2,57.05),1.25,4,'longitudinal_ridge_cap')
 for sign in [-1,1]:
  path([(cx-w/2,sign*d/2,43.5),(cx,sign*d/2,57),(cx+w/2,sign*d/2,43.5)],1.1,3,'gable_bargeboard')
for cx in [-43,43]:beam((cx-44,0,52.05),(cx+44,0,52.05),1.25,4,'transverse_ridge_cap_clipped_by_higher_roofs')
# Gable quatrefoil openings on south center and both ends on both elevations.
def quatrefoil(cx,y,z):
 cs=CrossSection.circle(1.35,24).translate((0,1.2))
 for dx,dz in [(1.2,0),(-1.2,0),(0,-1.2)]:cs=cs+CrossSection.circle(1.35,24).translate((dx,dz))
 add(placed(cs,'y',cx,y,z,1.1),2,'quatrefoil_dark_recess_sealed_in_miniature')
 add(placed(cs.offset(.55)-cs,'y',cx,y,z,1.4),3,'quatrefoil_stone_surround')
quatrefoil(0,-27.1,48.3)
for x in [-94,94]:
 for y in [-33.1,33.1]:quatrefoil(x,y,48.3)
# North gold circle-cross rests on gable, not a free-floating emblem.
cs=CrossSection.circle(3.1,48)-CrossSection.circle(2.45,48)
cs=cs+CrossSection.square((1.1,10)).translate((-.55,-6.2))+CrossSection.square((6.6,1.1)).translate((-3.3,-.55))
add(placed(cs,'y',0,27.55,49.1,1.5),6,'north_gold_circle_cross')
# North-end narrow octagonal spire, blunted .9mm tip for honest miniature robustness.
add(Manifold.cylinder(8,1.7,1.7,8).translate((0,24,56)),1,'north_ridge_octagonal_spire_body')
add(Manifold.cylinder(1,2.1,2.1,8).translate((0,24,63.5)),3,'spire_cap_band')
add(Manifold.cylinder(7,2.0,.5,8).translate((0,24,64)),4,'spire_conical_tip_blunted_not_scale_exact')
FEATURES=dict(name='南神本館（巴克禮紀念館）',school='台灣基督長老教會南神神學院',slug='ttcs-barclay-main-hall',selected_version='2024 restoration completed exterior, checked against March 2026 north photos',estimated_not_surveyed=True,roof_count=5,roof_junction_groups=4,paired_valleys=8,adjacent_west_school_excluded=True,chapel_1957_excluded=True,SW_interface_open_display_boundary_not_real_end_wall=True,all_materials_opaque=True,no_actual_print=True,support_free_certified=False,window_records=windows)
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
