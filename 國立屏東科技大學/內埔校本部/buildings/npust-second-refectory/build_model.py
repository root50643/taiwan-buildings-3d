"""NPUST Second Refectory, source-bound exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NPUST Second Refectory source observations.
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

# Image u-right -> world +X (east), image v-down -> world -Y (south).
# All coordinates are drawing-proportioned metre-like units, not a field survey.
SCALE=3.5
palette=[('display_plinth','#9A9A89',255),('cream_tiled_concrete','#C9BE9D',255),('dark_window_glass_opaque_miniature','#293A3D',255),('window_metal','#555D59',255),('red_brown_roof_tile','#AC5141',255),('terracotta_steps','#AB7863',255),('gray_green_rooflight_opaque_miniature','#76948D',255),('gray_service_roof','#959991',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,col,name):add(cube(x0,x1,y0,y1,z0,z1),col,name)
def poly(p,z,h,col,name):add(CrossSection([p]).extrude(h).translate((0,0,z)),col,name)
def slab(points,t,col,name):add(Manifold.hull_points(points+[(x,y,z-t) for x,y,z in points]),col,name)
def chamfer(a,b,c,d,k):return [(a+k,c),(b-k,c),(b,c+k),(b,d-k),(b-k,d),(a+k,d),(a,d-k),(a,c+k)]
def pane_x(x,a,b,z0,z1,name):
 block(x-.18,x+.18,a,b,z0,z1,2,name+'_glazing')
 for y in np.linspace(a,b,max(2,round((b-a)/1.25)+1)):block(x-.2,x+.2,y-.08,y+.08,z0-.1,z1+.1,3,name+'_mullion')
 for z in [z0,z0+(z1-z0)*.65,z1]:block(x-.2,x+.2,a-.06,b+.06,z-.08,z+.08,3,name+'_transom')
def pane_y(a,b,y,z0,z1,name):
 block(a,b,y-.18,y+.18,z0,z1,2,name+'_glazing')
 for x in np.linspace(a,b,max(2,round((b-a)/1.25)+1)):block(x-.08,x+.08,y-.2,y+.2,z0-.1,z1+.1,3,name+'_mullion')
 for z in [z0,z0+(z1-z0)*.65,z1]:block(a-.06,b+.06,y-.2,y+.2,z-.08,z+.08,3,name+'_transom')
def stair(a,b,width,name):
 # flight follows centerline from low to high, complete real air below slab
 a=np.array(a);b=np.array(b);d=b-a;n=10;h=d[2]/n;direction=d[:2]/np.linalg.norm(d[:2]);cross=np.array([-direction[1],direction[0]])
 pts=[(*(p[:2]+cross*side*width/2),p[2]) for p in [a,b] for side in [-1,1]];slab(pts,.32,1,name+'_sloping_slab')
 for i in range(n):
  p=a+d*i/n;q=a+d*(i+1)/n;z=q[2]
  corners=[(*(r[:2]+cross*side*width/2),z) for r in [p,q] for side in [-1,1]];slab(corners,.4,5,name+'_tread')
 for side in [-1,1]:
  aa=a.copy();bb=b.copy();aa[:2]+=cross*side*(width/2+.1);bb[:2]+=cross*side*(width/2+.1)
  pts=[(*(p[:2]+cross*w),p[2]+zz) for p in [aa,bb] for w in [-.16,.16] for zz in [-.3,.85]]
  add(Manifold.hull_points(pts),1,name+'_solid_slope_guard')
 # Short toe grounded in local display base; upper end meets porch slab.
 block(a[0]-.3,a[0]+.3,a[1]-.3,a[1]+.3,1.1,a[2]+.1,1,name+'_toe_support')
block(-8,64,-6,46,0,1.2,0,'bounded_display_base_not_surveyed_terrain')
# Raised east grade stops at main hall edge; exposed basement is west, north, south.
block(39.6,62,-1,40.7,1.1,2.95,0,'east_higher_grade_approximation')
# Lower envelope: window recesses are real cuts, not decals on an unbroken face.
base=CrossSection([chamfer(0,39.7,0,39.7,3.5)]).extrude(1.9).translate((0,0,1.15))
for y0,y1 in [(4,15),(24.5,35.7)]:base-=cube(-.2,1.0,y0,y1,1.35,2.05)
for y in [0,39.7]:
 for x0,x1 in [(4,8.2),(13.5,25)]:base-=cube(x0,x1,y-.6,y+.6,1.35,2.05)
add(base,1,'partly_exposed_basement_closed_inner_volume')
for y0,y1 in [(4,15),(24.5,35.7)]:pane_x(.85,y0,y1,1.34,2.08,'west_basement_recessed_vent')
for y in [.45,39.25]:
 for x0,x1 in [(4,8.2),(13.5,25)]:pane_y(x0,x1,y,1.34,2.08,'side_basement_recessed_vent')
poly(chamfer(-.1,39.8,-.1,39.8,3.5),2.85,.45,1,'main_hall_floor_and_open_perimeter_porch')
# High single storey: recessed closed interior, one high window row, not two floors.
poly(chamfer(3.4,36.3,3.4,36.3,1.6),3.2,4.25,1,'single_storey_hall_inner_enclosure')
# West is recessed behind real open front porch; windows physically project slightly from envelope.
for y0,y1 in [(5.4,13),(13.3,26.4),(26.7,34.3)]:pane_x(3.31,y0,y1,3.5,7.15,'west_recessed_hall_glazing')
for y in [3.31,36.39]:
 for x0,x1 in [(11.4,18.3),(18.6,26.3),(26.6,34.3)]:pane_y(x0,x1,y,3.65,7.15,'north_south_hall_glazing')
for y0,y1 in [(5.4,13.5),(26.2,34.3)]:pane_x(36.39,y0,y1,3.65,7.15,'east_recessed_hall_glazing')
# Real entrance door proxies meet the platform. South doorway is offset west.
pane_x(3.25,16,23.7,3.25,5.9,'west_entrance_doors_to_platform')
pane_y(9.4,13.2,3.25,3.25,5.9,'south_offset_entrance_doors_to_platform')
pane_y(18.2,22.1,36.45,3.25,5.9,'north_entrance_doors_to_platform')
# Perimeter concrete columns and low solid guards; entry gaps stay open.
for x,y in [(0,7),(0,14),(0,25),(0,32),(7,0),(14,0),(25,0),(32,0),(39.7,7),(39.7,14),(39.7,25),(39.7,32),(7,39.7),(14,39.7),(25,39.7),(32,39.7)]:
 block(x-.25,x+.25,y-.25,y+.25,3.15,7.6,1,'outer_porch_column')
for p,q in zip(chamfer(0,39.7,0,39.7,3.5),chamfer(0,39.7,0,39.7,3.5)[1:]+[chamfer(0,39.7,0,39.7,3.5)[0]]):beam((*p,7.35),(*q,7.35),.5,1,'perimeter_fascia_beam')
for y0,y1 in [(3.5,15.7),(24,36.2)]:block(-.15,.22,y0,y1,3.25,4.1,1,'west_porch_solid_guard')
for y in [0,39.7]:
 for x0,x1 in ([(3.5,9.2),(13.4,36.2)] if y==0 else [(3.5,18),(22.2,36.2)]):block(x0,x1,y-.18,y+.18,3.25,4.05,1,'north_south_porch_solid_guard')
# Eave is square while wall corners are chamfered.
ring(19.85,19.85,7.5,40.2,.35,1,'square_low_eave')
outer=[(-.25,-.25,7.62),(39.95,-.25,7.62),(39.95,39.95,7.62),(-.25,39.95,7.62)]
inner=[(16.65,16.65,11.52),(23.05,16.65,11.52),(23.05,23.05,11.52),(16.65,23.05,11.52)]
for i in range(4):
 j=(i+1)%4;slab([outer[i],outer[j],inner[i],inner[j]],.3,4,'main_four_slope_tile_roof_'+str(i));beam(outer[i],inner[i],.19,4,'diagonal_hip_ridge')
# Central square assembly: low hip silhouette from orthophoto, not 16 invented domes or PV.
for z in [11.48,12.05]:ring(19.85,19.85,z,6.5,.3,1,'square_rooflight_curb')
block(16.6,23.1,16.6,23.1,11.45,12.05,6,'raised_square_rooflight_side')
rooflightbase=[(16.5,16.5,12.08),(23.2,16.5,12.08),(23.2,23.2,12.08),(16.5,23.2,12.08)]
for i in range(4):slab([rooflightbase[i],rooflightbase[(i+1)%4],(19.85,19.85,12.55)],.24,6,'rooflight_low_hip_panel')
# Entrance landings and actual external stair flights: north at x20, south x11 (not mirrored).
block(-1.6,3.5,15.7,24,2.85,3.3,1,'west_entrance_landing')
stair((-5.5,19.85,1.35),(-1.3,19.85,3.3),7.8,'west_main_stairs')
block(9.1,13.5,-1.5,3.5,2.85,3.3,1,'south_entry_landing');stair((11.3,-5.3,1.35),(11.3,-1.3,3.3),3.8,'south_offset_stairs')
block(17.9,22.3,36.2,41.3,2.85,3.3,1,'north_entry_landing');stair((20.1,45,1.35),(20.1,41,3.3),3.8,'north_central_stairs')
# Low east connector and service wing. Solid kitchen roof, not an outdoor courtyard.
block(36,43,14,25.7,3.0,3.35,1,'east_connection_floor')
block(36,43,14,25.7,5.55,5.9,7,'east_connection_low_flat_roof')
for y in [14,25.7]:block(36,43,y-.2,y+.2,3.25,5.9,1,'connector_side_wall')
block(42.65,60.4,7,32.7,2.9,6.5,1,'east_service_rooms')
# Central lower roof covers all of the central zone and physically joins wing walls.
block(42.65,52.25,14.55,25.15,6.4,6.75,7,'kitchen_central_covered_gray_flat_roof')
# Outer wall openings approximate drawing; not surveyed partition count.
for y in [6.92,32.78]:pane_y(43.3,51.7,y,5.3,6.35,'service_north_south_strip_windows')
# East elevation A3-1: two ground-level doors, upper slit segments and local low slots.
for a,b in [(14.6,16.4),(23.4,25.2)]:pane_x(60.48,a,b,3.0,5.15,'service_east_ground_door')
for a,b in [(7.5,14.2),(25.6,28.8),(29.2,32.1)]:pane_x(60.48,a,b,5.0,5.6,'service_east_discontinuous_upper_window')
for a,b in [(25.7,28.7),(29.4,32.0)]:pane_x(60.48,a,b,3.4,3.85,'service_east_local_low_window')
# Three distinct roof slopes. The central sides have high clerestory walls.
for y0,y1,zin,zout,label in [(25.15,32.7,8.65,7.1,'north'),(7,14.55,7.1,8.65,'south')]:
 slab([(42.5,y0,zin),(52.35,y0,zin),(52.35,y1,zout),(42.5,y1,zout)],.3,4,'service_'+label+'_single_outward_slope')
 for x in [42.65,52.15]:
  slab([(x,y0,zin-.12),(x+.25,y0,zin-.12),(x+.25,y1,zout-.12),(x,y1,zout-.12)],2.35,1,'service_slope_closed_side_wall')
 # High inner face above the lower solid kitchen cap.
 y=25.15 if label=='north' else 14.55
 block(42.65,52.25,y-.15,y+.15,6.4,8.4,1,'service_inner_high_wall')
 pane_y(43,51.9,y+(-.17 if label=='north' else .17),7.1,7.85,'service_'+label+'_clerestory')
# East slope has high western inner edge and low east eave.
slab([(52.15,6.9,8.7),(60.55,6.9,6.6),(60.55,32.8,6.6),(52.15,32.8,8.7)],.3,4,'service_east_outward_slope')
block(52.1,52.4,7,32.7,6.4,8.5,1,'service_east_inner_high_wall')
pane_x(52.02,14.9,24.8,7.1,7.9,'service_east_inner_clerestory')
# Small gaps beneath lateral sloping end fascia are closed by side walls, not free roofs.
for y in [7,32.4]:slab([(52.15,y,8.5),(60.4,y,6.5),(60.4,y+.3,6.5),(52.15,y+.3,8.5)],2.1,1,'east_roof_end_wall')
# Hidden enclosed roof/connector volumes are intentionally solid, no trapped inner shells.
block(36.3,42.9,14.15,25.55,3.25,5.75,1,'closed_connector_interior_omitted')
add(Manifold.hull_points([(x,y,z) for x,z in [(52.15,8.5),(60.4,6.5)] for y in [7,32.7]]+[(x,y,6.35) for x in [52.15,60.4] for y in [7,32.7]]),1,'closed_east_roof_interior_omitted')
add(Manifold.hull_points(rooflightbase+[(19.85,19.85,12.55)]+[(x,y,11.9) for x,y,z in rooflightbase]),6,'solid_rooflight_hidden_interior')
# Original north/south service yards retained as local ground, no uncertain later yard objects.
parts=[p.translate((-27,-19.85,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立屏東科技大學第二餐廳','campus':'內埔校本部','scope':'Complete main square hipped hall, raised square low-hip rooflight, connected east three-slope service wing and covered gray central kitchen roof, visible partial basement and asymmetric entry stairs. Excludes neighboring buildings and unconfirmed later yard objects.','basis':'1989/1990 design drawings, 1997 completion history, pre-May-2012 exterior photos and capture-date-unknown official orthophoto; not a 2026 condition or measured as-built.','nominal_proportional_units_to_display_mm':SCALE,'coordinate_hand':'Drawing right=east +X; drawing down=south -Y. North stairs x20.1, south x11.3; west main entrance -X; east service wing +X. No PDF y-axis mirroring.','thin_details':{'window_mullions_mm':.16*SCALE,'roof_panels_vertical_thickness_mm':.3*SCALE,'sloping_stair_slab_vertical_thickness_mm':.32*SCALE,'porch_guard_thickness_mm':.36*SCALE},'supports':'Porch/eaves, open stair undersides and roof overhangs require supports. Glazing opaque miniature solids in all formats; materials editable. Interiors closed/simplified. No physical print or universal minimum-wall claim.'}
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
