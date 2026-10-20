"""CYCU M gate, relocated exterior photo-relative approximation. Front -Y.
No measured scale; source-visible 3 barrel arches, 4 pierced transverse piers/8 feet.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def xz_extrude(points,depth,ycenter=0):
 return CrossSection([points]).extrude(depth).rotate((90,0,0)).translate((0,ycenter+depth/2,0))
def yz_extrude(points,width,x):
 return CrossSection([points]).extrude(width).rotate((90,0,90)).translate((x-width/2,0,0))
def arch_ring(cx,outer,inner,depth,y=0):
 # End-to-end barrel: observed front/rear arch, unobserved upper skin continued smoothly.
 angles=np.unique(np.r_[np.linspace(0,np.pi,97),np.arccos(.6/outer),np.arccos(-.6/outer)])
 # 1.2 mm miniature crown plateau removes unprintable mathematical knife-tip (<0.009 mm lowering).
 cap=np.sqrt(outer*outer-.6*.6)
 outerp=[(cx+outer*np.cos(t),82+min(cap,outer*np.sin(t))) for t in angles]
 innerp=[(cx+inner*np.cos(t),82+inner*np.sin(t)) for t in np.linspace(np.pi,0,97)]
 return xz_extrude(outerp+innerp,depth,y)
parts.append(box(0,0,0,148,52,3))
# Tall piers widen in depth at the curved shoulders, then meet the barrel spring line.
# Outer profile is the concave quarter transition visible at the side end of the gate.
shoulder=[(13+5*(1-np.cos(t)),74+8*np.sin(t)) for t in np.linspace(0,np.pi/2,25)]
profile=[(-13,2.8),(13,2.8),(13,74)]+shoulder[1:]+[(18,82.8),(-18,82.8)]+[(-y,z) for y,z in shoulder[::-1]]+[(-13,2.8)]
for x in [-63,-21,21,63]:
 pier=yz_extrude(profile,5.1,x)
 # Narrow perpendicular arch is a real through-hole in each transverse wall.
 ap=[(-7.2,2.5),(7.2,2.5),(7.2,65)]+[(7.2*np.cos(t),65+7.2*np.sin(t)) for t in np.linspace(0,np.pi,49)][1:]+[(-7.2,2.5)]
 pier=pier-yz_extrude(ap,6.8,x)
 parts.append(pier)
for x in [-42,0,42]:
 parts.append(arch_ring(x,21.6,18.6,36))
 # Slightly thickened arch rims supported by the barrel, not detached stripes.
 for y in [-18,18]:parts.append(arch_ring(x,22.2,18.6,1.6,y))
# Outer end cornice / terminal edge follows source side view, not invented glazing.
for x in [-63,63]:parts.append(box(x,0,81.8,5.2,37.6,1.4))
m=Manifold.batch_boolean(parts,OpType.Add).simplify(0.0001)
# Generator-level boolean sliver simplification (0.0001 display mm); raw export audited independently.
assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Canonical surface is raw float32 STL, and all exchanges share these exact triangles.
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center
palette=[('off_white_concrete','#E5E1D5'),('ivory_thickened_rim','#E9E5DA'),('display_base_neutral','#A7A69E')]
colors=np.zeros(len(f),dtype=int)
colors[(abs(c[:,1])>17.95)&(c[:,2]>81.7)]=1
colors[c[:,2]<3.01]=2
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
# Deterministic 3MF, material assigned per triangle. Display materials, not extruder mapping.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
def el(p,name,attrs={}):return E.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=E.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b in palette:el(bm,'base',{'name':a,'displaycolor':b+'FF'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':E.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
