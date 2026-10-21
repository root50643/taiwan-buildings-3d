"""THU Alumni bell tower. Two deep wall blades and eleven cross slabs, photo-proportioned display millimetres."""
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
# Photo proportions, not surveyed dimensions. Bounded platform only.
parts=[box(0,0,0,102,34,2),box(0,0,1.8,100,32,.7)]
for x in [-10,10]:parts.append(box(x,0,2.3,5,14,150.2))
photo_y=[519,504,487,467,444,419,390,359,321,281,228]
slabs=[2.5+(603-y)*150/416 for y in photo_y]
for z in slabs:parts.append(box(0,0,z-1.1,16,13.4,2.2))
# Single bell suspended from upper slab: strengthened fixed stem, no invented yoke.
zt=slabs[-1];zb=slabs[-2]
parts.append(rod((0,0,zt-1),(0,0,zt-5),.85))
profile=np.array([[0,zt-4],[2.1,zt-4],[2.6,zt-4.8],[3.0,zt-7],[3.6,zt-11],[4.5,zt-13.0],[4.6,zt-13.7],[3.6,zt-13.7],[3.0,zt-11],[2.1,zt-7],[0,zt-7]])
parts.append(solid(trimesh.creation.revolve(profile,sections=96)))
parts.append(rod((0,0,zt-7),(0,0,zt-14.3),.55))
parts.append(solid(trimesh.creation.icosphere(subdivisions=2,radius=.85).apply_translation((0,0,zt-14))))
# Small visible apparatus on lower bell slab, fixed abstract block; cables omitted.
parts.append(box(0,0,zb+.9,1.4,1.8,3.2))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('exposed_gray_concrete','#B0B0A6'),('weathered_slab_edges','#85877C'),('bronze_bell','#9C8858'),('fixed_iron_hardware','#494A40'),('platform_edge','#9C9786'),('platform_paving','#BDB8A7')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;hi=t.triangles.max(axis=1)
colors[hi[:,2]<=2.501]=5
colors[(hi[:,2]<=2.001)&((np.abs(c[:,0])>50)|(np.abs(c[:,1])>16))]=4
for z in slabs:colors[(np.abs(c[:,0])<7.501)&(np.abs(c[:,2]-z)<1.101)]=1
colors[(np.abs(c[:,0])<4.61)&(np.abs(c[:,1])<4.61)&(c[:,2]>zt-14.9)&(c[:,2]<zt-3.99)]=2
colors[(np.abs(c[:,0])<.86)&(np.abs(c[:,1])<.91)&(((c[:,2]>zt-4)&(c[:,2]<zt-1.09))|((c[:,2]>zb+1.09)&(c[:,2]<zb+4.11)))]=3
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,source_album_date='2019-09-20',independent_photo_date='2022-01-09',source_appearance_not_claimed_current=True,wall_count=2,cross_slab_count=11,between_slab_gaps=10,slab_centers_mm=slabs,slab_thickness_mm=2.2,wall_tip_z_mm=152.5,wall_width_mm=5,wall_depth_mm=14,central_clear_width_mm=15,bottom_passage_height_mm=slabs[0]-1.1-2.5,bell_count=1,display_base_mm=[102,34,2.5],mechanism_fixed_and_strengthened=True,not_functional_bell=True,no_actual_print=True,omitted=['trees','surrounding mall','small finials','wiring','exact mechanisms','surface aggregate','joint hairlines'],notes='Complete photo-approximate tower on bounded platform. Eleven slabs, ten interspaces plus tall lower passage. Heights normalized from perspective photographs, not surveyed. Stem and clapper strengthened; platform depth approximate.'),indent=2)+'\n')
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
