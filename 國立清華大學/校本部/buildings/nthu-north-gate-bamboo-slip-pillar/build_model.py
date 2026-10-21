"""NTHU north gate bamboo-slip pillar exterior approximation; millimetres."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
# Artificial stabilizing base, NOT the historic foundation. Main equal tops z153.
base=box(0,0,0,49,35,3)
body=box(0,0,2.8,33,15,150.2)
# Two shallow backed grooves on BOTH narrow return faces express 3 equal profiles.
# They do not claim open slots or any hidden structural connector.
for x in [-16.5,16.5]:
 for y in [-2.5,2.5]:body-=box(x,y,3,1.8,1.2,150.1)
parts=[base,body]
band_intervals=[]
for z in [47,96,143]:
 for dz in [0,2.1]:
  parts.append(box(0,0,z+dz,34.6,16.6,1.1));band_intervals.append([z+dz,z+dz+1.1])
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('warm_offwhite_concrete','#E6E2D6'),('added_neutral_display_base','#808A87'),('paired_horizontal_moldings','#D6D1C4')]
colors=np.zeros(len(f),dtype=int);tri=t.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1)
for low,high in band_intervals:colors[(lo[:,2]>=low-.001)&(hi[:,2]<=high+.001)]=2
colors[hi[:,2]<=3.001]=1
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,body_height_mm=150,body_width_mm=33,body_depth_mm=15,equal_profile_top_z_mm=[153,153,153],return_grooves=2,groove_width_mm=1.2,groove_depth_mm=.9,grooves_are_backed_not_through=True,band_groups=3,bands_per_group=2,band_intervals_mm=band_intervals,band_height_mm=1.1,band_projection_mm=.8,band_clear_vertical_gap_mm=1.0,added_display_base_mm=[49,35,3],lettering='Omitted rather than fragile freestanding or false calligraphic reconstruction',unseen_geometry='Plain rear; solid backed mass is print-oriented approximation, not internal reconstruction',scope='Pillar exterior only; excludes guardhouse, corridor, trees, antenna and underground foundations'),indent=2)+'\n')
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
