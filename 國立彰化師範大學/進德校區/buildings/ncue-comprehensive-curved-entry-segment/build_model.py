"""Historical NCUE Comprehensive Center curved entrance screen segment.
Relative, unmeasured geometry in display mm. Front -Y; excluded building behind.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def prism(poly,z,h):
 if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(h).translate((0,0,z))
def curve(x):return -8-.0028*x*x
def screen(xmax=76):
 xs=np.linspace(-xmax,xmax,39)
 return [(float(x),curve(x)-2) for x in xs]+[(float(x),curve(x)+2) for x in xs[::-1]]
# Curved screen and all fourteen authentic openings are geometry, not painted rectangles.
wall=prism(screen(),10,78)
for x in [-65,-51,-37,-23,23,37,51,65]:wall-=box(x,-15,10,6.5,45,60)
wall-=box(0,-12,10,27,45,54)
for x in [-10,-5,0,5,10]:wall-=box(x,-12,72,2.8,45,3.8)
parts.append(wall)
# Low neutral study base, not a surveyed site outline.
parts.append(box(0,-22,0,170,90,3))
# Broad gently curved stairs: seven rises plus rear platform. Solid overlapping levels.
for i in range(7):
 xs=np.linspace(-80,80,41);front=[(float(x),-34+i*2.5-.0028*x*x) for x in xs]
 poly=front+[(80,10),(-80,10)]
 parts.append(prism(poly,3,1.0*(i+1)))
# Entry bay behind screen. Short return cheeks and upper closure are explicitly truncated.
parts += [box(-17,1,10,3,20,67),box(17,1,10,3,20,67),box(0,7,70,37,5,7)]
# Recessed glass backplane; dark glazing, never a surrogate for screen openings.
parts.append(box(0,8,10,31,2,60))
for x in [-15,-7.5,0,7.5,15]:parts.append(box(x,6.4,10,1.0,2.1,60))
for z in [35,51,69]:parts.append(box(0,6.4,z,31,2.1,1.1))
# Source-visible front side rails, grounded into stair/platform; deliberately simplified.
for side in [-1,1]:
 for x0 in [39,51,63,75]:
  x=side*x0;y=curve(x)-5
  parts.append(box(x,y,9.8,1.3,1.3,9.5))
 for z in [14,18.2]:
  xs=np.linspace(39,75,10)*side
  rail=[(float(x),curve(x)-5.55) for x in xs]+[(float(x),curve(x)-4.45) for x in xs[::-1]]
  parts.append(prism(rail,z,.9))
m=Manifold.batch_boolean(parts,OpType.Add)
assert m.status().name=='NoError'
m=m.simplify(0.0001);me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center;n=t.face_normals
palette=[('warm_grey_mosaic','#B8B5A4'),('dark_stone_steps','#69695D'),('pale_window_frame','#C4C5B7'),('recessed_glazing','#3E504E'),('metal_handrail','#959B97'),('cut_boundary_neutral','#A9AAA4'),('entrance_reveal','#AAA794')]
colors=np.zeros(len(f),dtype=int)
colors[c[:,2]<10.01]=1;colors[c[:,2]<3.01]=5
colors[(abs(c[:,0])<18.6)&(c[:,1]>-6)&(c[:,2]>10)]=6
colors[(abs(c[:,0])<15.6)&(c[:,1]>5.2)&(c[:,2]>10)&(c[:,2]<70.1)]=2
colors[(abs(c[:,1]-7)<.03)&(abs(c[:,0])<15.6)&(c[:,2]>10)&(c[:,2]<70)]=3
colors[(abs(c[:,0])>38)&(c[:,2]>10)&(c[:,2]<19.4)&(c[:,1]<-8-.0028*c[:,0]**2-3.8)]=4
colors[(c[:,1]>9.9)&(c[:,2]>10)]=5
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
