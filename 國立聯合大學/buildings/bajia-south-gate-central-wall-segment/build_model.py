"""Estimated NUU Bajia south gate central three masonry wall segments only."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
# Added plinth. Overall wall W140 H70, center W44; not surveyed dimensions.
parts=[box(0,0,0,152,52,3)]
# Two side masonry masses: front -17, back17; upper floors at58.4.
for x in [-46,46]:
 a=box(x,0,2.8,48,34,55.6)
 # Closed thin perimeter coping around a shallow 1.6mm top recess.
 rim=box(x,0,58.2,48,34,1.8)-box(x,0,58.1,44.8,30.8,2.1)
 parts += [a,rim]
# Center projects toward road. Front plain gray borders flank shallow white field.
center=box(0,-2,2.8,36,38,68.6)
# Material boundary is a real shallow backed recess, never a portal.
center-=box(0,-21,4.6,28,1.2,65.2)
parts.append(center)
# Two low brick/terracotta side rims; NO invented red rear crossrim.
for x in [-20,20]:
 parts.append(box(x,-2.3,2.8,4,38.6,70.2))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('gray_masonry_untextured','#929997'),('neutral_added_display_plinth','#727D7D'),('red_brown_brick_piers_simplified','#995D4E'),('blank_white_name_panel','#E4E5DF'),('terracotta_coping','#BC785B'),('gray_recessed_top','#797E79')]
colors=np.zeros(len(f),dtype=int);tri=t.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1);n=t.face_normals
# Face regions use every triangle vertex, not centroid-only color masks.
# Red front piers and exposed long side walls only; neutral unseen rear closure.
for sign in [-1,1]:
 xx=tri[:,:,0]*sign
 pier=(xx.min(axis=1)>=17.999)&(xx.max(axis=1)<=22.001)&(lo[:,2]>=2.999)&(hi[:,1]<17.001)
 colors[pier & (n[:,1]<.5)]=2
# Blank recessed plaque back plane and small recess returns.
white=(lo[:,0]>=-14.001)&(hi[:,0]<=14.001)&(lo[:,2]>=4.599)&(hi[:,2]<=69.801)&(hi[:,1]<=-20.399)
colors[white]=3
# Three actual recessed gray floors.
colors[(n[:,2]>.99)&((abs(c[:,2]-58.4)<.001)|(abs(c[:,2]-71.4)<.001))]=5
# Coping sides and tops above the side floor / center floor, excludes gray rear face.
colors[(lo[:,2]>=58.199)&(hi[:,2]<=60.001)&((hi[:,0]<=-21.999)|(lo[:,0]>=21.999))&~((n[:,2]>.99)&(abs(c[:,2]-58.4)<.001))]=4
colors[(lo[:,2]>=71.199)&(abs(c[:,0])>=17.999)]=4
colors[hi[:,2]<=3.001]=1
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,wall_width_mm=140,central_height_above_plinth_mm=70,side_height_above_plinth_mm=57,central_width_mm=44,side_width_mm=48,central_depth_mm=38,side_depth_mm=34,side_coping_width_mm=1.6,top_recess_depth_mm=1.6,central_side_rim_width_mm=4,white_panel_recess_mm=.6,scope='Only central three masonry walls; no pedestrian arch, gate leaves, retractable gates or guardhouse',unseen_geometry='Neutral rear closure and estimated depth; no invented rear brickwork',added_display_plinth_mm=[152,52,3]),indent=2)+'\n')
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
