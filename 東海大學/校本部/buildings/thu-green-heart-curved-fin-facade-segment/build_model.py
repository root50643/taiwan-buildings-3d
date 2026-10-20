"""THU Green Heart: nine registered bays, cropped facade only. Relative display mm.
Front -Y. Twisted curved leaves are photographic fits, not measured developable surfaces.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,Mesh64,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
PITCH=11.;N=9;H=60.;Z0=44.;THICK=1.3
# Curved ruled leaf: facade-aligned upper edge rotates outward at foot.
# Sampled fit, not an asserted construction radius. Root overlaps continuous post.
def leaf(x,zlo=Z0,zhi=Z0+H,thick=THICK):
 ribs=[52,60,68,76,84,92,100]
 zs=sorted(set(np.linspace(zlo,zhi,max(2,int((zhi-zlo)*4.0)+1)).tolist()+[z+d for z in ribs for d in [-.55,-.40,.40,.55] if zlo<z+d<zhi]));v=[]
 for z in zs:
  thick=THICK+.75*max([np.clip((.55-abs(z-r))/.15,0,1) for r in ribs])
  t=np.clip((z-Z0)/H,0,1);a=(1-t)**1.65*np.pi/2
  for u,w in [(0,-thick/2),(10.35,-thick/2),(10.35,thick/2),(0,thick/2)]:
   v.append([x+u*np.cos(a)+w*np.sin(a),-u*np.sin(a)+w*np.cos(a),z])
 f=[]
 for j in range(len(zs)-1):
  for k in range(4):
   a=4*j+k;b=4*j+(k+1)%4;c=b+4;d=a+4;f.extend([[a,b,c],[a,c,d]])
 f.extend([[0,2,1],[0,3,2]]);o=4*(len(zs)-1);f.extend([[o,o+1,o+2],[o,o+2,o+3]])
 return Manifold(Mesh64(np.asarray(v,float),np.asarray(f,np.uint64)))
# Display base and rear/side cut are neutral, not claimed as actual building envelope.
parts.append(box(0,5,0,108,46,3))
parts.append(box(0,21,2.8,100,3.0,89.2))
# Lower recessed entrance backing and its real glazing recesses, 20mm behind slab nose.
parts.append(box(0,10,2.8,99,4,39.2))
parts.append(box(-46.5,12,2.8,7,18,39.2))
parts.append(box(0,4.5,41,101,35,3.6))
# Upper inset glazing backing with shallow real recesses, not opacity filling leaf gaps.
parts.append(box(0,6,44,99,3,61))
for i in range(N+1):parts.append(box(-49.5+i*PITCH,2.8,43.8,1.8,7,61.4))
for i in range(N):
 x=-49.5+i*PITCH
 parts.append(leaf(x,43.9,104.2))
 # Seven simplified horizontal rib bands; count/spacing are visual stand-ins, not surveyed.
 # Ribs are integrated into the leaf solid; no tangent duplicate overlays.
# Top slim dark fascia and lower screen edge tie continuous roots.
parts.append(box(0,2.6,103.7,101,9,2.4))
parts.append(box(0,1.5,43.6,101,6,1.3))
m=Manifold.batch_boolean(parts,OpType.Add)
# Actual lower and upper glazing recesses (back faces are retained as glass proxies).
for i in range(8):
 m=m-box(-36+i*10.7,7.6,6,8.8,2.0,22.5)
 m=m-box(-36+i*10.7,7.6,29.7,8.8,2.0,6.3)
for i in range(N):m=m-box(-44+i*11,4.5,47,8.2,1.3,54)
m=m.simplify(.0001);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('daylight_grey_curved_metal','#999C98'),('pale_concrete_slab_pier','#B7B6AB'),('recessed_dark_glazing','#394C4D'),('slim_metal_fascia_and_frames','#626B69'),('neutral_display_cut_and_base','#D3D0C5')]
colors=np.zeros(len(f),dtype=int)
colors[c[:,2]<44]=1
colors[(c[:,1]>-1)&(c[:,1]<7.6)&(c[:,2]>44)]=3
# Leaf surfaces project toward -Y, retain daylight grey even at upper attachment.
colors[(c[:,1]<.7)&(c[:,2]>44)&(c[:,2]<103.7)]=0
colors[c[:,2]>103.69]=3
for y in [8.6,5.15]:colors[np.max(abs(t.triangles[:,:,1]-y),axis=1)<1e-4]=2
colors[(c[:,1]>19.49)|(c[:,2]<3.01)]=4
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
