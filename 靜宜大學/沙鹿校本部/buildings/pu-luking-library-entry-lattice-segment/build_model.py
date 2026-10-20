"""PU Luking old library bounded entry lattice corner. Relative display mm, front -Y.
Grid counts read from official two-angle photos, no measured dimensional survey.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def beam(a,b,width,depth):
 # Front XZ diagonal rectangle, with overlap embedded into grid intersections.
 a=np.array(a,float);b=np.array(b,float);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
 pts=[a-n,b-n,b+n,a+n]
 return CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((0,-18+depth/2,0))
# Neutral display base; approach terrace and deliberately simplified 9-step apron.
parts.append(box(0,0,0,96,92,3))
parts.append(box(0,9,2.8,79,54,10.2))
for i in range(9):parts.append(box(0,-40+i*2.8,2.8,40,3.0,1.2*(i+1)))
# Slightly projecting landing joins the stairs to source-visible raised entrance.
parts.append(box(0,-18,11.8,48,6,1.4))
# Bounding structural lattice: six front bays, five right-return bays; six rows.
X=np.linspace(-24,24,7);Y=np.linspace(-18,22,6);Z=np.linspace(37,109,7)
for x in X:parts.append(box(x,-18,36.5,1.7,2.8,73.5))
for y in Y:parts.append(box(24,y,36.5,2.8,1.7,73.5))
for z in Z:
 parts.append(box(0,-18,z,50.8,2.8,1.7))
 parts.append(box(24,2,z,2.8,42.8,1.7))
# Deeper edge frame and tall open pilotis; no fake dark panels in the screen voids.
for x,y in [(-24,-18),(24,-18),(24,22)]:parts.append(box(x,y,12.7,3.4,3.4,98.3))
parts.append(box(0,-18,109,51.4,3.4,4.0));parts.append(box(24,2,109,3.4,43.4,4.0))
# Source front chevron rises from second lower grid row to upper-middle apex.
parts.extend([beam((-24,61),(0,85),2.2,3.0),beam((0,85),(24,61),2.2,3.0)])
# Setback bounded mass: cut at rear; front glazing is 12mm BEHIND lattice.
parts.append(box(-2,18,12.7,48,8,94.0))
# Upper overhangs behind porous screen, physically attached to short backing.
for z in [37,61,85,105]:parts.append(box(-2,5,z,48,25,1.8))
# Setback entrance portal at rear, open ground under main lattice preserved.
parts.append(box(-17,5,12.7,3.2,25,24.8));parts.append(box(13,5,12.7,3.2,25,24.8))
# Truncated left wing stub, not an invented whole building.
parts.append(box(-31,10,36.7,12,22,70.0))
# Window recesses in backing and short left stub, not black patches on the lattice.
back=Manifold.batch_boolean(parts,OpType.Add)
for z in [45,69,93]:
 for x in [-18,-10,-2,6,14]:back=back-box(x,13.9,z,5.4,2.2,9.0)
 for x in [-34,-28]:back=back-box(x,-1,z,3.6,2.2,9.0)
parts=[back]
m=Manifold.batch_boolean(parts,OpType.Add).simplify(0.0001)
# Generator-level boolean sliver simplification (0.0001 display mm); raw export audited independently.
print('STATUS',m.status());assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Canonical surface is raw float32 STL, and all exchanges share these exact triangles.
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center
palette=[('warm_grey_small_tile_concrete','#A69F91'),('recessed_window_shadow','#485251'),('terrace_stair_stone','#B9B2A3'),('display_base_neutral','#D0CDC4')]
colors=np.zeros(len(f),dtype=int)
# Only true planar window-recess back faces receive shadow material.
for z in [45,69,93]:
 for x in [-18,-10,-2,6,14]:
  mask=(np.max(abs(t.triangles[:,:,1]-15.0),axis=1)<1e-4)&(abs(c[:,0]-x)<2.71)&(c[:,2]>z)&(c[:,2]<z+9)
  colors[mask]=1
 for x in [-34,-28]:
  mask=(np.max(abs(t.triangles[:,:,1]-.1),axis=1)<1e-4)&(abs(c[:,0]-x)<1.81)&(c[:,2]>z)&(c[:,2]<z+9)
  colors[mask]=1
colors[c[:,2]<13.21]=2
colors[c[:,2]<3.01]=3
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
