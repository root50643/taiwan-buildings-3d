"""YunTech spirit bell tower. Four concrete columns and rotated steel frame, photo-proportioned display millimetres."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import LineString
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def solid(t):
 if t.volume<0:t.invert()
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def rod(a,b,r):
 a=np.array(a);b=np.array(b);t=trimesh.creation.cylinder(radius=r,height=np.linalg.norm(b-a),sections=24);t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation((a+b)/2);return solid(t)
# Display dimensions in mm, image-proportioned not a measured survey.
def beam(a,b,width,depth):
 a=np.array(a);b=np.array(b);t=trimesh.creation.box((width,depth,np.linalg.norm(b-a)));t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation((a+b)/2);return solid(t)
def ibeam(a,b,width=3.6,depth=2.8,web=1.0,flange=.85,angle=0):
 a=np.array(a);b=np.array(b);L=np.linalg.norm(b-a)
 q=box(0,0,0,web,depth,L)+box(0,-depth/2+flange/2,0,width,flange,L)+box(0,depth/2-flange/2,0,width,flange,L)
 t=q.to_mesh64();t=trimesh.Trimesh(np.array(t.vert_properties)[:,:3],np.array(t.tri_verts),process=False)
 t.apply_transform(trimesh.transformations.rotation_matrix(math.radians(angle),[0,0,1]));t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation(a);return solid(t)
parts=[box(0,0,0,70,70,3),box(0,0,2.7,68,68,1.0)]
corners=[(-15,-15),(15,-15),(15,15),(-15,15)]
for x,y in corners:parts.append(box(x,y,3,5,5,90))
# Four steel posts at edge midpoints: not two frontal projections.
radial=[(15,0),(0,15),(-15,0),(0,-15)]
for x,y in radial:parts.append(ibeam((x,y,3),(x,y,183),angle=math.degrees(math.atan2(y,x))))
for z in [64,91]:
 for i,(x,y) in enumerate(corners):
  u,v=corners[(i+1)%4];parts.append(ibeam((x,y,z),(u,v,z),3.8,3.2))
for i,(x,y) in enumerate(corners):
 u,v=corners[(i+1)%4]
 parts.extend([ibeam((x,y,64),(u,v,91),3.8,2.8),ibeam((u,v,64),(x,y,91),3.8,2.8)])
# Horizontal diamond ring, connected to lower side midpoint vertical posts.
for z in [91,181.5]:
 for i,(x,y) in enumerate(radial):
  u,v=radial[(i+1)%4];parts.append(ibeam((x,y,z),(u,v,z),2.6,2.2,1,.85))
# Suspended square cage aligned to concrete square, 45deg to diamond frame.
cage=[(-7,-7),(7,-7),(7,7),(-7,7)]
for x,y in cage:parts.append(beam((x,y,146),(x,y,178),1.2,1.2))
for z in [146,156,166,176]:
 for i,(x,y) in enumerate(cage):
  u,v=cage[(i+1)%4];parts.append(beam((x,y,z),(u,v,z),1.2,1.2))
 parts.extend([beam((-7,0,z),(7,0,z),1.2,1.2),beam((0,-7,z),(0,7,z),1.2,1.2)])
# Diagonal upper hangers tie cage corners into outer frame, robust fixed substitute.
for x,y in cage:parts.append(beam((x,y,176),(0,0,181.5),1.4,1.4))
parts.extend([beam((-15,0,181.3),(15,0,181.3),1.5,1.5),beam((0,-15,181.3),(0,15,181.3),1.5,1.5)])
# Four mouths on lowest level directly observed; 3x4 inferred, not official count.
for level,z in enumerate([146,156,166]):
 R=[1.9,2.25,2.65][level]
 for x in [-3.5,3.5]:
  for y in [-3.5,3.5]:
   profile=np.array([[0,z+6.8],[R*.4,z+6.8],[R*.48,z+5.8],[R*.6,z+4.5],[R*.8,z+3.2],[R,z+2.3],[R,z+1.5],[0,z+1.5]])
   t=trimesh.creation.revolve(profile,sections=48);t.apply_translation((x,y,0));parts.append(solid(t))
   parts.append(rod((x,y,z+6.3),(x,y,z+10),.6))
   parts.append(beam((x,-7,z+9.6),(x,7,z+9.6),1.2,1.2))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=False);v,inv=np.unique(np.asarray(t.vertices),axis=0,return_inverse=True);f=inv[np.asarray(t.faces)];t=trimesh.Trimesh(v,f,process=False)
palette=[('red_orange_steel','#BA462D'),('pale_gray_concrete','#A7A8A1'),('dark_bronze_bells','#4A4940'),('plaza_stone','#B8B8AC')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center
colors[c[:,2]<=3.701]=3
for x,y in corners:colors[(abs(c[:,0]-x)<=2.501)&(abs(c[:,1]-y)<=2.501)&(c[:,2]>3.701)&(c[:,2]<=93.001)]=1
for level,z in enumerate([146,156,166]):
 R=[1.9,2.25,2.65][level]
 for x in [-3.5,3.5]:
  for y in [-3.5,3.5]:colors[(np.hypot(c[:,0]-x,c[:,1]-y)<=R+.001)&(c[:,2]>=z+1.499)&(c[:,2]<=z+6.801)]=2
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,source_capture_years=[2017,2018,2020],source_appearance_not_claimed_current=True,concrete_columns=4,concrete_top_mm=93,steel_posts=4,steel_post_xy=radial,steel_top_mm=183,upper_square_rotation_deg=45,cage_rotation_relative_concrete_deg=0,cage_levels=3,representative_bells=12,bell_count_inferred_not_official=True,lowest_four_mouths_directly_visible=True,display_base_mm=[70,70,3.7],steel_I_web_mm=1,steel_I_flange_mm=.85,cage_bar_mm=1.2,bell_hanger_diameter_mm=1.2,bells_solid_and_fixed=True,no_actual_print=True,omitted=['adjacent auditorium','full plaza extent and side stairs','trees','thin tension cables','electrical mechanism','lettering'],notes='Complete above-ground tower study from seven official photographs. Small plinth is model support, not surveyed plaza boundary. Three-by-four bell arrangement inferred; bell sizes and hangers simplified. No functional mechanism or hollow casting.'),indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
# Deterministic 3MF, material assigned per triangle. Display materials, not extruder mapping.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b in palette:el(bm,'base',{'name':a,'displaycolor':b+'FF'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
