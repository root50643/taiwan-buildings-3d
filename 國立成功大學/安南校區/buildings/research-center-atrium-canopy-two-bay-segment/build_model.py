"""NCKU Annan shared atrium canopy: three transverse frames, two bays; estimated section."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def rod(a,b,r):
 a=np.array(a);b=np.array(b);v=b-a;n=np.linalg.norm(v);z=v/n
 x=np.cross(z,[0,0,1] if abs(z[2])<.9 else [0,1,0]);x/=np.linalg.norm(x);y=np.cross(z,x)
 tf=np.column_stack([x,y,z,a-z*.12]);return Manifold.cylinder(n+.24,r,r,16).transform(tf)
def height(x):return 38+24*(1-(x/65)**2)-2.3*(x+65)/130
# BLUE display cut-end bases only, NOT real full-height architecture or ground columns.
parts += [box(-76,0,0,12,62,29),box(76,0,0,12,62,18)]
xs=np.linspace(-65,65,49)
profile=[(x,height(x)+1.6) for x in xs]+[(x,height(x)) for x in xs[::-1]]
parts.append(CrossSection([profile[::-1]]).extrude(60).rotate((90,0,0)).translate((0,30,0)))
# Exactly three frames at y=-28,0,28; longitudinal two-bay scope.
for y in [-28,0,28]:
 # curved chords, constant depth; open zig-zag triangular web (not glazing).
 for a,b in zip(xs[:-1],xs[1:]):
  parts.append(rod((a,y,height(a)-.65),(b,y,height(b)-.65),1.2))
  parts.append(rod((a,y,height(a)-8),(b,y,height(b)-8),1.2))
 nodes=np.linspace(-65,65,13)
 for i,(a,b) in enumerate(zip(nodes[:-1],nodes[1:])):
  za=height(a)-(.65 if i%2==0 else 8);zb=height(b)-(8 if i%2==0 else .65)
  parts.append(rod((a,y,za),(b,y,zb),.9))
 for x in [-65,65]:parts.append(rod((x,y,height(x)-8),(x,y,height(x)-.65),1.2))
 # Left short building-side support, right roof-level fork; hidden anchors not invented.
 parts.append(box(-70,y,28,14,4.4,3.2))
 parts.append(rod((75,y,17),(65,y,28),1.8))
 parts.append(rod((75,y,17),(43.1,y,height(43.1)-7.6),1.8))
# 9 longitudinal purlins visibly lighter than transverse frame; all meet roof.
for x in np.linspace(-65,65,9):parts.append(rod((x,-30,height(x)-.4),(x,30,height(x)-.4),1.0))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
m=m.set_tolerance(.0001).simplify(.001);me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('neutral_dark_gray_steel','#626B70'),('neutral_silver_roof_unknown_material','#C6CBCB'),('blue_DISPLAY_cut_end_bases_NOT_architecture','#668BA6'),('short_building_support_estimated_gray','#A1A4A1')]
colors=np.zeros(len(f),dtype=int)
roofz=38+24*(1-(c[:,0]/65)**2)-2.3*(c[:,0]+65)/130
colors[(c[:,2]>=roofz-.04)&(abs(c[:,0])<=65.01)]=1
colors[(c[:,0]<-69.99)&(c[:,2]<29.001)|(c[:,0]>69.99)&(c[:,2]<18.001)]=2
colors[(c[:,0]<-62.99)&(c[:,0]>-77.01)&(c[:,2]>=28)&(c[:,2]<=31.21)&(colors!=2)]=3
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-features.json').write_text(json.dumps({'estimated_not_surveyed':True,'transverse_frames':3,'longitudinal_bays':2,'span_mm':130,'length_mm':60,'roof_thickness_mm':1.6,'upper_lower_chord_diameter_mm':2.4,'web_diameter_mm':1.8,'purlin_diameter_mm':2,'right_fork_diameter_mm':3.6,'display_bases':'blue side blocks are added display cut ends, not real buildings/columns','source_surface_stripes':'omitted; material and translucency unknown','not_compatible_scale_with_existing_wings':True},indent=2)+'\n')
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
