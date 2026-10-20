"""Baisha entrance facade segment, historical-photo proportions, not survey geometry.
Millimetres. Front -Y. Truncated rear/left/right are study boundaries.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection
O=Path(__file__).resolve().parent
parts=[];cuts=[];features=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def opening(x=20,z=9,w=43,h=68,shoulder=55):
 return [(x-w/2,z),(x+w/2,z),(x+w/2,z+shoulder),(x+w/2-10,z+h),(x-w/2+10,z+h),(x-w/2,z+shoulder)]
# One study plinth, central high facade body, limited left wing.
add(0,0,0,150,66,3)
add(20,1,3,84,26,115)
add(-47,2,3,50,24,89)
# Broad recessed brown bay behind portal ring and side window strips.
cut(20,-13,9,67,11,81)
# True through portal, no black infill; same opening throughout limited depth.
portal=profile(opening(),1,70)
cuts.append(portal)
# Upper paired ribbon window, set back 2.3 mm from main face.
cut(20,-12,96,65,4.6,13)
# Left wing 4 rows, 3 source-bounded bays, finite cutoff.
for z in [12,32,52,72]:
 for x in [-64,-48,-32]: cut(x,-10.7,z,11.5,5.4,12)
# Union structural mass and real recesses.
m=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
m=m-Manifold.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
d=[]
# Portal face ring only, real chamfer, fuses to recessed body and base.
out=[(-6,8),(46,8),(46,82),(-6,82)]
ring=profile(out,-12.3,4.4)-profile(opening(),-12.3,8)
d.append(ring)
# Grid beams on underside of canopy, supported into ring/back mass.
for x in [-1,6,13,20,27,34,41]: d.append(box(x,1,75.6,1.4,24,3.0))
for y in [-8,-1,6,12]:d.append(box(20,y,75.6,44,1.4,3.0))
# Upper window frame bars, solid backed. 15 lights x2, approximate count.
for x in np.linspace(-12.5,52.5,16):d.append(box(float(x),-11.3,96,0.9,2.3,13))
d.append(box(20,-11.3,102,65,2.3,1.0))
# Thin tall window bays flank portal; backed recess facade remains solid.
# Glass is actual shallow material face, frames protrude but stay fused.
for x in [-9.6,49.6]:
 d.append(box(x,-8.0,13,7.0,1.0,55))
 for dx in [-3.5,0,3.5]:d.append(box(x+dx,-9.0,13,0.9,3.0,55))
 for z in np.linspace(13,68,12):d.append(box(x,-9.0,float(z),7.8,3.0,0.9))
 # small separate top side lights under broad facade beam
 d.append(box(x,-8,79,7,1,7))
 for dx in [-3.5,0,3.5]:d.append(box(x+dx,-9,79,.9,3,7))
 d.append(box(x,-9,82.5,7.8,3,.9))
# Glazed transom above portal, backed by high facade.
d.append(box(20,-8.0,83,48,1,5.7))
for x in [-4,4,12,20,28,36,44]:d.append(box(x,-9,83,1,3,5.7))
# Left wing window mullions and floor projections.
for z in [12,32,52,72]:
 for x in [-64,-48,-32]:
  d.append(box(x,-9.1,z,1,3.0,12));d.append(box(x,-9.1,z+6,11.5,3.0,1))
for z in [28,48,68,88]:d.append(box(-47,-10.8,z,51,5,3.0))
# Main stair. Eight steps ascend from base to entrance floor (z9).
for i in range(8):d.append(box(20,-29+i*1.9,3,62,2.2,.75*(i+1)))
d.append(box(20,-10,3,62,11,6))
# Left lateral approach is a compressed schematic ramp, no unsupported handrail.
ramp=profile([(-69,3),(-23,3),(-23,9),(-40,9)],-23,12)
d.append(ramp)
# Fuse details, then cut portal again to guarantee clear passage below beams.
m=m+Manifold.batch_boolean(d,__import__('manifold3d').OpType.Add)
# Deliberately leave underside coffer beams in the upper 1.4mm of opening.
# Coarse prism clear below z75.5 excludes canopy lattice.
clear=profile([(-1.5,9),(41.5,9),(41.5,64),(31.5,75.5),(8.5,75.5),(-1.5,64)],1,70)
m=m-clear
assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Float32 delivered STL is source of every exchange/render mesh.
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center;n=t.face_normals
palette=[('warm_tile','#C2BDAE'),('recess_brown','#877565'),('window_frame','#E1DFD2'),('glazing','#434F52'),('portal_stone','#AAA697'),('steps','#8F8B80'),('cut_boundary_neutral','#BBBAB5')]
colors=np.zeros(len(f),dtype=int)
# Rear closure is a model boundary, never a surveyed rear facade.
colors[(n[:,1]>.8)&(c[:,1]>12)]=6
colors[(c[:,2]<9.01)&(c[:,1]<-14)]=5
colors[(c[:,2]<3.01)]=6
# Back of broad facade recess.
colors[(np.abs(c[:,1]+7.5)<.06)&(c[:,2]>9)&(c[:,2]<90)&(c[:,0]>-13.6)&(c[:,0]<53.6)]=1
# Portal stone trim at front plane; vertical and chamfer ring faces.
colors[(c[:,1]<-10.05)&(c[:,2]>=8)&(c[:,2]<82.1)&(c[:,0]>=-6.1)&(c[:,0]<=46.1)]=4
# Upper glazing backplane inside main ribbon.
colors[(np.abs(c[:,1]+9.7)<.08)&(c[:,2]>96)&(c[:,2]<109)&(c[:,0]>-12.5)&(c[:,0]<52.5)]=3
colors[(c[:,1]<-10.1)&(c[:,2]>=96)&(c[:,2]<=109)&(c[:,0]>=-13)&(c[:,0]<=53)]=2
# Side strip backing plane and actual mullion geometry.
for x in [-9.6,49.6]:
 region=(abs(c[:,0]-x)<4)&(((c[:,2]>=13)&(c[:,2]<=69))|((c[:,2]>=79)&(c[:,2]<=86)))
 colors[region&(c[:,1]<-7.9)]=2
 colors[region&(abs(c[:,1]+8.5)<.06)]=3
# Transom frame and glazing.
r=(c[:,0]>-4.1)&(c[:,0]<44.1)&(c[:,2]>=83)&(c[:,2]<=88.7)&(c[:,1]<-7.9)
colors[r]=2;colors[r&(abs(c[:,1]+8.5)<.06)]=3
# Wing recessed window backs and mullions.
for z in [12,32,52,72]:
 for x in [-64,-48,-32]:
  r=(abs(c[:,0]-x)<5.8)&(c[:,2]>z)&(c[:,2]<z+12)
  colors[r&(abs(c[:,1]+8)<.08)]=3
  colors[r&(c[:,1]<-9)]=2
# Coffered ceiling underside is pale concrete.
colors[(c[:,2]>75.5)&(c[:,2]<79)&(c[:,0]>-2)&(c[:,0]<42)&(c[:,1]>-10)&(c[:,1]<13)]=2
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=7).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
