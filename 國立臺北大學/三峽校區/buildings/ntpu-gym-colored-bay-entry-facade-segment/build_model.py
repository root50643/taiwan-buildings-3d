"""NTPU photo-registered colored-bay entry facade CUT, not complete building.
All units arbitrary display millimeters; front is -Y. Back y=8 is invented cut.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(q):parts.append(q)
add(box(93,0,0,198,30,3))
# A shallow rear wall closes the display cut only. It is NOT a surveyed plan.
add(box(93,7,3,186,2,47))
# Upper facade and real recessed narrow glazing on right.
wall=box(102,4,16,168,6,29)
windows=[]
for x in [84,89,94,103,108,117,122,131,136,142,162,172,177]:
 for z in [20,29,37]:
  if 113<x<135 and z==20:continue
  if 142<x<161 and z>=29:continue
  wall=wall-box(x,1,z,2.2,3,5)
  windows.append((x,z))
# Left wing small, deliberately irregular narrow/horizontal windows.
for x,z,w,h in [(22,39,1.2,5),(28,41,1.2,1.2),(34,41,4,1.2),(40,40,1.2,4),(45,39,1.2,1.2),(28,30,1.2,4),(35,31,4,1.2),(44,29,1.2,5),(24,23,1.2,1.2),(33,23,4,1.2),(43,22,1.2,1.2)]:
 wall=wall-box(x,1,z,w,3,h);windows.append((x,z))
add(wall)
# Ground floor glazed recess, piers, continuous canopy.
add(box(93,5,3,184,2,13))
for x in [2,18,39,59,78,96,112,136,158,184]:add(box(x,1.5,3,2.2,9,13))
add(box(93,-.5,15,186,11,1.8))
for x in np.arange(5,184,4):add(box(float(x),3.7,3,0.9,1.2,12))
for z in [7,12]:add(box(93,3.7,z,184,1.2,.9))
# Left three-level recessed balcony stack with open front, not black paint.
add(box(1,2,16,2,12,34))
for z in [17,28,39,48]:add(box(9,2,z,18,12,1.5))
for z in [18.5,29.5,40.5]:
 add(box(9,-3,z,16,1.2,2))
 for x in [4,9,14]:add(box(x,-3,z,1,1.2,3))
# Deep left crown and sky-open right beam. Rear cut must stop below beam slot.
add(box(40,-1,48,80,14,2.2))
add(box(133,3.5,48,106,4,1.6))
for x in [82,98,116,134,152,170,184]:add(box(x,3.5,44,1.8,4,4.5))
# Carve sky slot through the arbitrary back too.
# Colored bays: opaque panels with actual 1.3 mm recessed faces.
bays=[(64,-3,18,30,16,29,68,17,1),(121,-.5,17,20,11,8,121,16,2),(152,-1.5,23,15,13,20,154,7,3)]
for x,y,z,w,d,h,gx,gw,mat in bays:
 b=box(x,y,z,w,d,h);front=y-d/2
 b=b-box(gx,front,z+1.5,gw,2.6,h-3)
 # Blue return is glazed on right, not an opaque frame.
 if mat==1:b=b-box(x+w/2,y-1,z+1.5,2.6,d-4,h-3)
 add(b)
 # Thickened symbolic mullions rooted into recessed glazing surface.
 for xx in np.linspace(gx-gw/2,gx+gw/2,5 if mat==1 else (9 if mat==2 else 4)):add(box(float(xx),front+.9,z+1.5,.75,.9,h-3))
 for zz in np.linspace(z+1.5,z+h-1.5,5 if mat==1 else (2 if mat==2 else 3)):add(box(gx,front+.9,float(zz),gw,.9,.75))
 if mat==1:
  for yy in np.linspace(y-d/2+2,y+d/2-2,4):add(box(x+w/2-.9,float(yy),z+1.5,.9,.75,h-3))
  for zz in np.linspace(z+1.5,z+h-1.5,5):add(box(x+w/2-.9,y-1,float(zz),.9,d-4,.75))
m=Manifold.batch_boolean(parts,OpType.Add)
m=m-box(133,7,45,106,4,3)
assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center;n=t.face_normals
palette=[('pale_concrete','#C7C9C3'),('blue_projecting_bay','#51A9C9'),('red_entry_frame','#D93D48'),('yellow_projecting_bay','#E9B935'),('opaque_glazing','#59747C'),('silver_mullions','#B8C5C6'),('display_cut_base','#A4A79E')]
colors=np.zeros(len(f),dtype=int);colors[c[:,2]<3.01]=6
colors[(c[:,2]>3)&(c[:,2]<15)&(abs(c[:,1]-4)<.02)]=4
for x,z in windows:
 colors[(abs(c[:,0]-x)<2.1)&(c[:,2]>=z)&(c[:,2]<=z+5.01)&(abs(c[:,1]-2.5)<.03)]=4
for x,y,z,w,d,h,gx,gw,mat in bays:
 front=y-d/2
 region=(c[:,0]>=x-w/2-.01)&(c[:,0]<=x+w/2+.01)&(c[:,2]>=z-.01)&(c[:,2]<=z+h+.01)&(c[:,1]<1.01)
 colors[region]=mat
 glass=region&(c[:,0]>=gx-gw/2)&(c[:,0]<=gx+gw/2)&(c[:,2]>z+1.49)&(c[:,2]<z+h-1.49)&(abs(c[:,1]-(front+1.3))<.02)
 colors[glass]=4
 mullion=region&(c[:,0]>=gx-gw/2-.4)&(c[:,0]<=gx+gw/2+.4)&(c[:,2]>z+1.49)&(c[:,2]<z+h-.74)&(c[:,1]>front+.44)&(c[:,1]<front+1.29)
 colors[mullion]=5
 if mat==1:
  side=region&(c[:,1]>y-d/2+1.99)&(c[:,1]<y+d/2-2)&(c[:,2]>z+1.49)&(c[:,2]<z+h-1.49)
  colors[side&(abs(c[:,0]-(x+w/2-1.3))<.02)]=4
  colors[side&(c[:,0]>x+w/2-1.29)&(c[:,0]<x+w/2-.44)]=5
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
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
