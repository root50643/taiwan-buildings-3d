"""DILA Great Vow bridge researcher-defined A/B middle run, NOT whole bridge.
Photo-fit display millimetres, no measured segment scale. X=-70 B / +70 A.
One high outward-inclined box side (+Y), opposite low OPEN balustrade (-Y).
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,Mesh64,OpType
O=Path(__file__).resolve().parent
parts=[]
def center(x):return 5*((x+70)/140)**2
def width(x):return 38-6*((x+70)/140)**1.5
def height(x):return 25-2*((x+70)/140)
def highy(x,z):return center(x)+width(x)/2+(z-5)*.19
def lowy(x,z):return center(x)-width(x)/2-(z-5)*.16
# Closed ruled loft; transverse planes are arbitrary crop boundaries.
def loft(a,b,section,n=None):
 xs=np.linspace(a,b,n or max(2,int((b-a)/2)+1));v=[]
 for x in xs:
  for y,z in section(x):v.append([x,y,z])
 f=[]
 for j in range(len(xs)-1):
  for k in range(4):
   a0=4*j+k;b0=4*j+(k+1)%4;c=b0+4;d=a0+4;f.extend([[a0,b0,c],[a0,c,d]])
 f.extend([[0,2,1],[0,3,2]]);o=4*(len(xs)-1);f.extend([[o,o+1,o+2],[o,o+2,o+3]])
 m=Manifold(Mesh64(np.asarray(v,float),np.asarray(f,np.uint64)));assert m.status().name=='NoError';return m
# Transverse deck slab roots every plank and both rail sides.
parts.append(loft(-70,70,lambda x:[(center(x)-width(x)/2-1,2),(center(x)+width(x)/2+1,2),(center(x)+width(x)/2+1,5),(center(x)-width(x)/2-1,5)]))
# Single solid girder envelope; internal structural voids deliberately unknown/omitted.
parts.append(loft(-70,70,lambda x:[(highy(x,0),0),(highy(x,0)+2.1,0),(highy(x,height(x))+2.1,height(x)),(highy(x,height(x)),height(x))]))
# Wood deck planks, real 0.28 mm grooves over continuous root slab.
for a in np.arange(-70,70,1.8):
 b=min(a+1.52,70)
 parts.append(loft(a,b,lambda x:[(center(x)-width(x)/2,4.8),(center(x)+width(x)/2+.1,4.8),(center(x)+width(x)/2+.1,5.65),(center(x)-width(x)/2,5.65)],2))
# Raised dark vertical timber strips on the interior high girder surface.
for a in np.arange(-69.6,69.6,2.3):
 b=min(a+1.95,69.8)
 parts.append(loft(a,b,lambda x:[(highy(x,6)-.55,6),(highy(x,6)+.12,6),(highy(x,height(x)-1.2)+.12,height(x)-1.2),(highy(x,height(x)-1.2)-.55,height(x)-1.2)],2))
# Low opposite balustrade: thin posts, two real horizontal rails, large OPEN voids.
for a in np.arange(-69.5,70,3.5):
 b=min(a+1.0,70)
 parts.append(loft(a,b,lambda x:[(lowy(x,4.6)-.55,4.6),(lowy(x,4.6)+.55,4.6),(lowy(x,15)+.55,15),(lowy(x,15)-.55,15)],2))
for z,w,h in [(8.5,.9,.9),(14.2,1.6,1.2)]:
 parts.append(loft(-70,70,lambda x,z=z,w=w,h=h:[(lowy(x,z)-w/2,z),(lowy(x,z)+w/2,z),(lowy(x,z+h)+w/2,z+h),(lowy(x,z+h)-w/2,z+h)]))
# Exterior rib run visually counted/registered in qa/source-registration.json.
RIB_X=np.linspace(-65,65,13)
for a in RIB_X:
 parts.append(loft(a-.65,a+.65,lambda x:[(center(x)-width(x)/2-.8,.6),(highy(x,1)+6.0,.6),(highy(x,1)+6.0,2.4),(center(x)-width(x)/2-.8,2.4)],2))
m=Manifold.batch_boolean(parts,OpType.Add).simplify(.00001);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('pale_grey_box_girder','#A9ADA7'),('weathered_timber_transverse_deck','#626463'),('dark_vertical_timber_inner_strips','#514B43'),('low_open_metal_balustrade_and_ribs','#6B7777'),('timber_low_handrail','#77716A')]
colors=np.zeros(len(f),dtype=int)
x,y,z=c.T;cy=center(x);ww=width(x)
colors[(z>=4.9)&(z<=5.66)&(y<cy+ww/2+.15)]=1
colors[(y<highy(x,z)+.08)&(y>highy(x,z)-.7)&(z>5.9)&(z<height(x)-1.15)]=2
colors[(y<cy-ww/2+.8)&(z>5.7)]=3
colors[(y<cy-ww/2+.8)&(z>=14.15)]=4
colors[z<2.41]=3
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
