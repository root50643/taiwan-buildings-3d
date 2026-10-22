"""TTCS West School, source-bound exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from TTCS West School source observations.
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

# Source-bound TTCS west school. +X east, +Y north, +Z up; no mirrored PDF axes.
SCALE=5.5
palette=[('display_base','#A6A598',255),('light_gray_washed_stone','#C2C2B9',255),('dark_opaque_miniature_glazing','#344344',255),('dark_brown_window_frames','#44372F',255),('weathered_gray_cement_tiles','#595850',255),('dark_gray_bands','#838780',255),('copper_gutters','#94694A',255),('pale_door_frames','#D6D5C7',255)]
def cube(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def block(a,b,c,d,e,f,col,name):add(cube(a,b,c,d,e,f),col,name)
def arch(u,z0,spring,r,depth):
 p=[(u-r,z0),(u+r,z0),(u+r,spring)]+[(u+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return CrossSection([p]).extrude(depth)
def ax(x0,x1,y,z0,spring,r):return arch(y,z0,spring,r,x1-x0).transform([[0,0,1,x0],[1,0,0,0],[0,1,0,0]])
def ay(y0,y1,x,z0,spring,r):return arch(x,z0,spring,r,y1-y0).transform([[1,0,0,0],[0,0,-1,y1],[0,1,0,0]])
def winx(x,y,z=5.35,r=.64,spring=7.05,label='upper'):
 add(ax(x-.18,x+.18,y,z,spring,r),3,label+'_arched_frame')
 add(ax(x-.19,x+.19,y,z+.12,spring,r-.12),2,label+'_opaque_recessed_pane')
 block(x-.20,x+.20,y-.045,y+.045,z+.08,spring+r-.06,3,label+'_center_mullion')
 for zz in [z+.5,z+1.0,spring]:block(x-.20,x+.20,y-r+.1,y+r-.1,zz-.035,zz+.035,3,label+'_transom')
def winy(y,x):
 add(ay(y-.18,y+.18,x,5.35,7.05,.64),3,'short_end_arch_frame');add(ay(y-.19,y+.19,x,5.47,7.05,.52),2,'short_end_glass')
 block(x-.045,x+.045,y-.20,y+.20,5.45,7.6,3,'short_end_mullion')
 for z in [5.9,6.4,7.05]:block(x-.54,x+.54,y-.20,y+.20,z-.035,z+.035,3,'short_end_transom')
def rectwin(x,y,w=.68,z0=1.2,z1=3.1,label='west_rectangular'):
 block(x-.10,x+.10,y-w/2,y+w/2,z0,z1,3,label+'_frame');block(x-.12,x+.12,y-w/2+.10,y+w/2-.10,z0+.1,z1-.1,2,label+'_pane')
 for z in [z0+.5,z0+1,z1-.2]:block(x-.14,x+.14,y-w/2,y+w/2,z-.03,z+.03,3,label+'_grille')
block(-1.4,10.1,-1.4,35.1,0,.25,0,'thin_display_base_not_terrain')
block(0,8.5,0,31.5,.2,.5,1,'ground_platform')
# Ground offices solid except central cross passage and deep open east gallery.
for a,b in [(0,14.5),(17,31.5)]:
 block(0,6.35,a,b,.45,4.25,1,'simplified_closed_office_volume')
 block(-.045,.08,a,b,.5,1.05,5,'west_base_band')
# Upper volume (interior omitted); authentic openings are recessed opaque proxies.
upper=cube(0,8.5,0,31.5,4.05,8.3)
for y in [1.75+3.5*i for i in range(9)]:upper-=ax(8.13,8.7,y,5.35,7.05,.64)
westys=[1.75+3.5*i for i in range(8)]
for y in westys:upper-=ax(-.2,.37,y,5.35,7.05,.64)
upper-=ay(-.2,.37,4.1,5.35,7.05,.64)
add(upper,1,'upper_storey_with_recessed_arch_windows')
for y in [1.75+3.5*i for i in range(9)]:winx(8.24,y,label='east_W'+str(45-round((y-1.75)/3.5)))
for i,y in enumerate(westys):winx(.26,y,label='west_W'+str(47+i))
winy(.26,4.1)
for y in [28.5,29.65,30.8]:rectwin(-.02,y,.62,6.35,7.25,'north_bathroom_small_rectangular')
for x in [2.3,5.0]:
 block(x-.5,x+.5,31.48,31.62,5.8,7.1,3,'north_short_end_small_frame');block(x-.4,x+.4,31.5,31.64,5.9,7.0,2,'north_short_end_small_pane')
# East 4 arches + central flat/sloping-shoulder passage + 4 arches. Void extends into gallery.
facade=cube(8.1,8.5,0,31.5,.45,4.3)
for i in list(range(4))+list(range(5,9)):
 y=1.75+3.5*i;facade-=ax(7.9,8.7,y,.35,2.65,1.42)
 # shallow pale arch surround, same true aperture
 trim=ax(8.48,8.61,y,.48,2.65,1.58)-ax(8.4,8.75,y,.35,2.65,1.42)
 add(trim,7,'east_open_arch_surround')
facade-=cube(7.9,8.7,14.5,17,.3,3.5)
add(facade,1,'east_arcade_true_open_4_plus_4')
for y in [0,3.5,7,10.5,14,17.5,21,24.5,28,31.5]:block(8.06,8.58,max(0,y-.19),min(31.5,y+.19),.45,1.1,5,'arcade_column_base')
# Central portal shouldered top, projecting shallow canopy, no door obstructing cross passage.
for y in [14.35,17.15]:block(8.48,8.68,y-.20,y+.20,.45,3.35,5,'central_portal_jamb')
block(8.44,8.69,14.3,17.2,3.48,3.66,5,'central_flat_portal_lintel')
block(8.35,9.05,14.05,17.45,3.85,4.02,5,'central_shallow_canopy')
block(-.72,.1,14.2,17.3,3.5,3.67,5,'west_passage_shallow_canopy')
# Southern gallery mouth is a real transverse arch, visible into the long gallery.
south=cube(6.27,8.5,0,.38,.45,4.3)-ay(-.2,.6,7.3,.35,2.65,1.0);add(south,1,'south_open_gallery_end_arch')
# South pair of long rectangular windows and common shallow sunshade.
for x in [1.7,4.2]:
 block(x-.46,x+.46,-.08,.08,1.15,3.1,3,'south_ground_long_window_frame');block(x-.35,x+.35,-.1,.09,1.26,3.0,2,'south_ground_long_window_glass')
 for z in [1.7,2.2,2.7]:block(x-.38,x+.38,-.12,.1,z-.035,z+.035,3,'south_grille')
block(.85,5.1,-.65,.1,3.35,3.49,5,'south_shared_shallow_canopy')
# West lower window locations clustered 8 south / 10 north of central passage.
for y in np.linspace(.8,13.7,8):rectwin(-.03,float(y),.72)
for y in np.linspace(17.7,30.7,10):rectwin(-.03,float(y),.65)
# East gallery rear wall: source p432/436, 3doors+5windows south and 2doors+3windows north.
for ya,yb in [(0,14.5),(17,31.5)]:block(6.34,6.40,ya,yb,.5,1.25,5,'gallery_rear_dark_gray_base_band')
for i,y in enumerate([2.6,8.3,11.7,18.5,28.7]):
 block(6.32,6.48,y-.58,y+.58,.5,3.25,7,'gallery_door_'+str(i)+'_pale_outer_frame')
 block(6.40,6.50,y-.46,y+.46,.52,3.12,3,'gallery_door_'+str(i)+'_dark_leaf')
 for z0,z1 in [(1.65,2.6),(2.78,3.05)]:
  for dy in [-.23,.23]:block(6.48,6.52,y+dy-.16,y+dy+.16,z0,z1,2,'gallery_door_readable_glass_panel')
 block(6.50,6.55,y-.035,y+.035,.6,3.08,7,'gallery_door_central_mullion')
for i,y in enumerate([.9,4.3,6.5,10.2,13.3,20.4,23.8,30.3]):rectwin(6.42,y,.78,1.3,3.15,'gallery_window_'+str(i))
# Source p432/436 D2 and flanking window at the north upper corridor junction.
# Closed miniature doorway proxy into simplified upper interior, not a blank wall.
block(6.84,7.96,31.47,31.65,4.3,7.35,7,'north_upper_D2_pale_door_frame')
block(6.95,7.85,31.53,31.68,4.32,7.22,3,'north_upper_D2_dark_door_leaf')
for x in [7.17,7.62]:block(x-.16,x+.16,31.65,31.71,5.5,7.06,2,'north_upper_D2_door_glass')
block(7.37,7.43,31.66,31.74,4.4,7.2,7,'north_upper_D2_center_mullion')
block(6.31,6.76,31.48,31.66,5.55,7.2,3,'north_upper_junction_flanking_window_frame')
block(6.38,6.69,31.55,31.70,5.65,7.1,2,'north_upper_junction_flanking_window_pane')
# Continuous waist/eave bands above the voids, no extra back arcade.
for x in [-.05,8.55]:block(x-.07,x+.07,0,31.5,4.25,4.6,5,'long_gray_waist_band')
for y in [-.05,31.55]:block(0,8.5,y-.07,y+.07,4.25,4.6,5,'end_gray_waist_band')
block(-.25,8.75,-.25,31.75,8.2,8.45,5,'eave_cornice')
# Single long ridge hipped roof; simple solid roof interior is intentional.
roofpts=[(-.5,-.5,8.42),(9,-.5,8.42),(9,32,8.42),(-.5,32,8.42),(4.25,4.25,10.45),(4.25,27.25,10.45)]
add(Manifold.hull_points(roofpts),4,'single_long_ridge_four_hip_cement_tile_roof')
beam((4.25,4.25,10.45),(4.25,27.25,10.45),.16,4,'single_roof_ridge')
for p,q in [(roofpts[0],roofpts[4]),(roofpts[1],roofpts[4]),(roofpts[2],roofpts[5]),(roofpts[3],roofpts[5])]:beam(p,q,.15,4,'diagonal_hip_ridge')
# Regular restrained roof tile courses; no guessed exact tile count.
for t in np.linspace(.06,.95,18):
 z=8.42+2.03*t;xl=-.5+4.75*t;xr=9-4.75*t;ya=-.5+4.75*t;yb=32-4.75*t
 for a,b in [((xl,ya,z),(xl,yb,z)),((xr,ya,z),(xr,yb,z)),((xl,ya,z),(xr,ya,z)),((xl,yb,z),(xr,yb,z))]:beam(a,b,.055,4,'approximate_tile_course')
# Eight copper downpipes, two long sides x four, attached and thickened for scale.
for x in [-.16,8.66]:
 beam((x,-.25,8.4),(x,31.75,8.4),.15,6,'copper_eave_gutter')
 for y in [.15,10.5,21,31.35]:beam((x,y,.45),(x,y,8.4),.13,6,'copper_downpipe')
# North one-bay short connector to existing main hall: open termination, no false wall.
block(6.22,8.55,31.45,34.1,.2,.5,1,'north_connector_ground_slab')
block(6.22,8.55,31.45,34.1,4.08,4.35,1,'north_connector_upper_floor')
block(6.22,8.55,31.45,34.1,8.0,8.25,1,'north_connector_top_beam')
for x in [6.22,8.32]:
 side=cube(x,x+.23,31.45,34.1,.45,4.3)-ax(x-.1,x+.4,32.78,.35,2.65,1.08)
 add(side,1,'north_connector_lower_open_arch')
 block(x,x+.23,31.45,34.1,4.3,5.05,1,'north_connector_upper_low_guard')
 block(x,x+.23,33.87,34.1,5.0,8.18,1,'north_connector_end_post_cut_at_seam')
# Display cutoff at y34.1 is deliberately OPEN, it is not an invented end wall.
parts=[p.translate((-4.25,-16.35,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'南神神學院西校舍（1957）','version':'2024–2025 completed restoration exterior; 2026 photo only corroborates north seam','scope':'Complete west school and one-bay north connector cut open at main-hall seam; excludes main hall chapel fountain and landscape','coordinate_hand':'right-handed +X east +Y north +Z up; east arcade +X, south end -Y','nominal_proportional_units_to_display_mm':SCALE,'east_upper_arches':9,'west_upper_arches':8,'west_north_small_windows':3,'east_ground_arches':8,'east_gallery_doors':5,'east_gallery_windows':8,'north_upper_D2_and_flanking_window':True,'central_cross_passage':True,'north_connector_open_cutoff':True,'thin_details':{'grille_mm':.06*SCALE,'downpipe_mm':.13*SCALE,'tile_course_mm':.055*SCALE},'supports':'Arcade and connector arches, canopies, eaves require supports. Opaque miniature glazing; no physical print; interiors simplified; not measured as-built.'}
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
