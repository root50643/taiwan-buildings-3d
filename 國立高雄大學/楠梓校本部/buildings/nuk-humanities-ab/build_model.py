"""NUK Humanities A/B / 國立高雄大學人文社會科學院 A/B 主樓. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_plinth','#93988F',255),('warm_ochre_wall','#D1B58B',255),('light_gray_concrete_metal_frame','#9CABA9',255),('dark_gray_roof_and_service','#545D61',255),('opaque_glazing_proxy','#55727B',255)]
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

# Approximate display millimetres, 2 mm per design metre; no survey claim.
# A opens -Y, B opens -X; actual first-floor corner connector joins the two.
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(bounds,col,name):add(cube(*bounds),col,name)
# Coordinates retain CAD sheet orientation, then all geometry is centered for rendering.
block((-10,232,-118,138,0,3),0,'bounded_display_base_not_site')
windows=[];terraces=[]
def wing(x0,x1,y0,y1,floors,axis,outer,inner,label):
 top=3+floors*8
 shell=cube(x0,x1,y0,y1,3,top) # solid printable room proxy; courts and colonnades remain open
 # Exterior detailed wall openings, inner gallery set back from court.
 if axis=='x':
  run=np.arange(y0+5,y1-3,7.2)
  for xx,side in [(outer,'outer'),(inner,'court')]:
   for z in range(floors):
    for i,yy in enumerate(run):
     h=3.5 if side=='outer' else 4.5;w=4.4 if side=='outer' else 5.0;zz=5+z*8
     shell-=cube(xx-2,xx+2,yy-w/2,yy+w/2,zz,zz+h)
     block((max(x0-.4,xx-2.15),min(x1+.4,xx+2.15),yy-w/2-.1,yy+w/2+.1,zz-.1,zz+h+.1),4,label+'_'+side+'_window')
     windows.append([xx,yy,zz,w,h])
 elif axis=='y':
  run=np.arange(x0+5,x1-3,7.2)
  for yy,side in [(outer,'outer'),(inner,'court')]:
   for z in range(floors):
    for xx in run:
     h=3.5 if side=='outer' else 4.5;zz=5+z*8
     shell-=cube(xx-2.4,xx+2.4,yy-2,yy+2,zz,zz+h)
     block((xx-2.5,xx+2.5,max(y0-.4,yy-2.15),min(y1+.4,yy+2.15),zz-.1,zz+h+.1),4,label+'_'+side+'_window')
     windows.append([xx,yy,zz,4.8,h])
 add(shell,1,label+'_walls')
 for j in range(floors+1):block((x0,x1,y0,y1,3+j*8,4+j*8),1,label+'_floor')
 # Slender gallery outside inner facade, with real open gaps and parapet bands.
 for j in range(1,floors):
  z=3+j*8
  if axis=='x':
   sign=1 if inner>outer else -1; a,b=sorted([inner,inner+sign*4.5])
   block((a,b,y0,y1,z,z+1),2,label+'_gallery_slab');xx=inner+sign*4
   block((xx-.5,xx+.5,y0,y1,z+1,z+2.6),1,label+'_gallery_parapet')
  else:
   sign=1 if inner>outer else -1;a,b=sorted([inner,inner+sign*4.5])
   block((x0,x1,a,b,z,z+1),2,label+'_gallery_slab');yy=inner+sign*4
   block((x0,x1,yy-.5,yy+.5,z+1,z+2.6),1,label+'_gallery_parapet')
# Three-floor A and two-floor B. Split non-overlapping wings.
wing(0,25,0,110,3,'x',0,25,'A_west')
wing(115,140,0,110,3,'x',140,115,'A_east')
wing(25,115,85,110,3,'y',110,85,'A_back')
wing(146,224,-26,0,2,'y',0,-26,'B_north')
wing(146,224,-110,-84,2,'y',-110,-84,'B_south')
wing(198,224,-84,-26,2,'x',224,198,'B_back')
# Continuous inward-falling mitered U roof: outer polygon high, court edge low.
def roofpoly(points,heights,thick=1.15):
 # Convex planar polygon prism, triangulated fan; vertical sides.
 n=len(points);v=[[x,y,z] for (x,y),z in zip(points,heights)]+[[x,y,z-thick] for (x,y),z in zip(points,heights)]
 f=[]
 for i in range(1,n-1):f += [[0,i,i+1],[n,n+i+1,n+i]]
 for i in range(n):j=(i+1)%n;f += [[i,n+i,n+j],[i,n+j,j]]
 t=trimesh.Trimesh(v,f,process=True);t.fix_normals();return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def roofs(label,polys,holes):
 roof=Manifold.batch_boolean([roofpoly(p,h) for p,h in polys],OpType.Add)
 for hi,(x0,x1,y0,y1,z) in enumerate(holes):
  roof-=cube(x0,x1,y0,y1,z,50)
  block((x0,x1,y0,y1,z-1,z+.05),2,label+'_recessed_accessible_roof_platform')
  # Adjacent low water service box at the inner end of platform, not skylight.
  if hi==(2 if label=='A' else 0):block((x0+.5,x0+4.5,y0+.5,y0+4.5,z,z+2),3,label+'_daily_water_tank_service')
  terraces.append(dict(block=label,bounds=[x0,x1,y0,y1],floor_z=z))
 add(roof,3,label+'_continuous_inward_sloping_mitered_roof')
 # Warm wedge infill immediately under roof slopes, supported by wall/floor below.
 for p,h in polys:
  wedge=roofpoly(p,h,7)
  for x0,x1,y0,y1,z in holes:wedge-=cube(x0,x1,y0,y1,z-1,50)
  # Only retain outer edge envelope, do not fill/roof court.
  perimeter=CrossSection([p]).extrude(45)-CrossSection([p]).offset(-1.3).extrude(46)
  add(wedge^perimeter,1,label+'_sloping_wall_end_infill')
roofs('A',[
 ([(0,0),(25,0),(25,85),(0,110)],[34,27,27,34]),
 ([(0,110),(25,85),(115,85),(140,110)],[34,27,27,34]),
 ([(115,0),(140,0),(140,110),(115,85)],[27,34,34,27])
],[(1,11,34,58,28.2),(129,139,34,58,28.2),(34,57,99,109,28.2)])
roofs('B',[
 ([(146,0),(146,-26),(198,-26),(224,0)],[26,19,19,26]),
 ([(224,0),(198,-26),(198,-84),(224,-110)],[26,19,19,26]),
 ([(146,-84),(146,-110),(224,-110),(198,-84)],[19,26,26,19])
],[(154,173,-10,-1,20.2),(214,223,-58,-36,20.2),(154,173,-109,-100,20.2)])
# Thickened high roof-edge fascia preserves a printable cap rather than knife edge.
for b in [(-.5,.5,0,110,33,34),(139.5,140.5,0,110,33,34),(-.5,140.5,109.5,110.5,33,34),(145.5,224.5,-.5,.5,25,26),(223.5,224.5,-110,0,25,26),(145.5,224.5,-110.5,-109.5,25,26)]:block(b,3,'thickened_high_roof_edge_fascia')
# High open gray frames at A front / side, low at B; genuine colonnades not walls.
def frame(a,b,height,bays,name):
 beam((*a,height),(*b,height),1.8,2,name+'_lintel')
 for t in np.linspace(0,1,bays+1):
  x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
  beam((x,y,3),(x,y,height),1.2,2,name+'_column')
frame((0,-10),(140,-10),22,9,'A_front_high_frame')
frame((-7,0),(-7,110),33,8,'A_outer_west_frame')
frame((147,0),(147,84),33,6,'A_outer_east_frame')
frame((140,117),(0,117),33,9,'A_rear_frame')
frame((138,-110),(138,-3),14,7,'B_open_low_frame')
frame((146,-117),(224,-117),25,5,'B_south_frame')
frame((231,-110),(231,0),25,7,'B_east_frame')
frame((151,7),(224,7),25,5,'B_north_frame')
# Frame cross-ties and gallery support columns overlap floor slabs.
for y in np.arange(0,111,14):
 for x,xx in [(-7,0),(140,147)]:beam((x,y,19),(xx,y,19),1.2,2,'A_frame_tie')
 for x in [29,111]:beam((x,y,3),(x,y,26),1.0,2,'A_court_colonnade')
for x in np.arange(26,115,14):beam((x,81,3),(x,81,26),1.0,2,'A_back_court_columns')
for y in np.arange(-84,-25,14):beam((194,y,3),(194,y,18),1.0,2,'B_court_columns')
for x in np.arange(146,199,14):
 for y in [-30,-80]:beam((x,y,3),(x,y,18),1,2,'B_court_columns')
# Roofed open front walkways, not filled courts.
block((0,140,-10,0,21.2,22.5),2,'A_single_high_open_front_walkway_canopy')
block((138,146,-110,0,13.2,14.5),2,'B_single_low_open_side_walkway_canopy')
# Glazed corner connection with nontransparent small-scale glass proxy.
block((133,156,-17,5,3,4),2,'AB_connected_corner_floor')
block((133,156,-17,5,15,16.2),2,'AB_connected_corner_roof')
for yy in [-17,5]:
 block((133,156,yy-.5,yy+.5,4,15),4,'AB_glazed_connection')
 for xx in np.arange(133,157,3):beam((xx,yy,3),(xx,yy,16),1,2,'AB_gray_connection_mullion')
for xx in [133,156]:block((xx-.5,xx+.5,-17,5,4,15),4,'AB_end_glazing')
block((133,156,-17,5,3.8,15.2),4,'AB_glazed_solid_interior_proxy')
# Actual right rear stepped lecture room: sloping roof rises outward.
block((114,140,110,136,3,12),1,'A_actual_rear_stepped_lecture_room')
lecture_poly=[(114,110),(140,110),(140,136),(114,136)]
lecture_h=[13,13,19,19]
add(roofpoly(lecture_poly,lecture_h,9)^cube(114,140,110,136,11.8,20),1,'A_rear_lecture_sloped_upper_volume')
add(roofpoly([(113.5,109.5),(140.5,109.5),(140.5,136.5),(113.5,136.5)],[13,13,19.15,19.15],1.1),2,'A_rear_lecture_sloping_roof')
block((113.5,140.5,135.9,136.9,18.15,19.15),2,'A_lecture_roof_thickened_high_edge')
for xx in np.arange(117,139,5):block((xx-1.3,xx+1.3,135.8,136.6,6.2,9),4,'A_low_room_back_window')
block((140,152,16,31,3,12),1,'A_actual_side_low_projection')
block((139.5,152.5,15.5,31.5,12,13.1),2,'A_side_projection_roof')
# 1F drawing text identifies the left rear striped projection as underground
# parking vehicle ramp, NOT a classroom or upward external stair.
# Only its short visible descending mouth is shown inside the display plinth.
ramp_cut=cube(29,38,108,136,.8,3.3).as_original();material_for_id[ramp_cut.original_id()]=0
parts=[m-ramp_cut for m in parts]
ramp_poly=[(29,110),(38,110),(38,136),(29,136)]
add(roofpoly(ramp_poly,[1,1,3,3],3)^cube(29,38,110,136,.3,3.1),2,'A_rear_parking_ramp_visible_descending_mouth')
for x0,x1 in [(28,29.2),(37.8,39)]:block((x0,x1,110,136,2.8,4.2),2,'A_parking_ramp_side_wall')
# The short above-ground entrance steps are independent of that parking ramp.
for k in range(10):
 z=3+(k+1)*.8
 block((140,148,-10-k*.8,-9-k*.8,3,z),2,'AB_entrance_external_stair_steps')
# Selective exterior sun-screen fins, not mirror copied court glazing.
for x in np.arange(48,111,2.2):block((x,x+.85,116.2,117.8,12,33.2),2,'A_rear_vertical_shading_fins')
for y in np.arange(-79,-30,2.8):block((230.2,231.8,y,y+.85,11,25.2),2,'B_back_vertical_shading_fins')
# Center independent miniature; all geometry including base shifted equally.
parts=[m.translate((-111,-10,0)) for m in parts]
FEATURES=dict(identity='National University of Kaohsiung humanities and social sciences A/B connected main building',scope='A three floors and B two floors; C excluded; tender-design and early official-photo approximation, not 2026 survey',courtyards=2,roof_platforms=terraces,window_count=len(windows),roof_type='three mitered planes each U; falling inward',minimum_nominal_detail_mm=.85,physical_print_tested=False,supports_required=True,source_cad_version='formal tender design; not as-built',rear_ramp='CAD label underground parking vehicle ramp; short visible descending mouth, underground continuation omitted',reviewer_v2_corrections=['left rear ramp not staircase/classroom','right rear lecture room sloping roof','single wide high A canopy and single wide low B canopy'],model_coordinates='CAD sheet axes, centered by (-111,-10); nominal 2 mm per design metre')
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
