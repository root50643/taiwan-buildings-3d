"""Swimming hall front segment. Primary massing: official aerial, source-era not 2026.
Normalized millimetre display dimensions only; +Y rear is synthetic crop closure.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):
 if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0:poly=list(reversed(poly))
 return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
# Low display foundation, no inferred terrain or site perimeter.
add(0,1,0,184,65,3)
# Closed front-segment backing; rear is a flat invented section cut, not a facade.
add(0,6,3,152,32,65)
# Four upper glazed bays are recessed 2.5mm, lower narrow ribbon similarly recessed.
for a,b in [(-74,-40),(-36,-2),(2,36),(40,74)]:
 cut((a+b)/2,-10,37,b-a,5,27)
 cut((a+b)/2,-10,15,b-a,5,4)
# Recessed actual entrance beside left-central vertical yellow-green tower.
cut(-12,-10,3,20,7,19)
# Major column line rhythm: gray lower piers and yellow upper columns.
for x in [-76,-38,0,38,76]:
 add(x,-11,3,3.6,4,32)
 add(x,-11,35,2.6,4,34)
# Shallow barrel front-edge roof; rear roof beyond crop deliberately omitted.
xs=np.linspace(-85,85,69);zs=68+7*(1-(xs/85)**2)
roof=[(float(x),float(z)) for x,z in zip(xs,zs)]+[(float(x),float(z-2)) for x,z in zip(xs[::-1],zs[::-1])]
parts.append(profile(roof,4,43))
m=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
details=[]
# Real raised mullions over opaque recessed glazing; no transparent cheat.
for a,b in [(-74,-40),(-36,-2),(2,36),(40,74)]:
 for z in [37,43.4,49.8,56.2,62.8]:details.append(box((a+b)/2,-9.4,z,b-a,3.4,1.0))
 for x in np.linspace(a,b,4):details.append(box(float(x),-9.4,37,1.0,3.4,27))
 if a!=-36:
  for x in np.linspace(a,b,7):details.append(box(float(x),-9.4,15,1.0,3.4,4))
  for z in [15,18]:details.append(box((a+b)/2,-9.4,z,b-a,3.4,1))
# Entrance door inset, lintel, split mullion. Door is opaque glazing surface.
details.extend([box(-12,-8.4,3,1.2,4.2,19),box(-12,-9.4,21,20,3.4,1.3)])
# Aerial-version entrance upper cover with vertical fluting; do not copy old red banner.
details.append(box(-12,-12.4,22,21,4.8,11))
for x in np.linspace(-21.5,-2.5,11):details.append(box(float(x),-15,22,1.0,1.4,11))
# Yellow-green tower as opaque glazed display geometry; protruding with framed panels.
details.append(box(-28,-14.5,3,13,10,62))
for x in [-34.5,-28,-21.5]:details.append(box(x,-19.5,3,1.2,1.3,62))
for z in [3,13,23,33,43,53,64]:details.append(box(-28,-19.5,z,14.2,1.3,1.0))
# Side face grid visibly returns, strengthening source-specific entry silhouette.
for z in [3,13,23,33,43,53,64]:details.append(box(-34.65,-14.5,z,1.3,10,1.0))
for y in [-19,-14,-10]:details.append(box(-34.65,y,3,1.3,1.1,62))
# Roof standing seams connected to thin curved skin; no proposed PV arrays.
for y in np.linspace(-16.5,24.5,20):
 rib=[(float(x),float(z+.5)) for x,z in zip(xs,zs)]+[(float(x),float(z-.3)) for x,z in zip(xs[::-1],zs[::-1])]
 details.append(profile(rib,float(y),1.0))
m=m+Manifold.batch_boolean(details,OpType.Add)
# Source-photo proportion calibration, not real-world measurement.
m=m.scale((1,1,.75))
assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center.copy();c[:,2]/=.75;n=t.face_normals
palette=[('gray_facade','#8C9191'),('recessed_blue_gray_glazing','#385057'),('pale_window_frames','#C4CBC7'),('shallow_barrel_roof','#969D9E'),('yellow_upper_columns','#D6B327'),('yellow_green_tower_glazing','#A0B73D'),('display_crop_closure','#B9B8B1'),('green_tower_frames','#CADB65'),('aerial_entry_fluted_cover','#77786A')]
colors=np.zeros(len(f),dtype=int)
colors[(c[:,2]<3.01)|(c[:,1]>21.99)]=6
colors[(abs(c[:,1]+7.5)<.05)&(((c[:,2]>37)&(c[:,2]<64))|((c[:,2]>15)&(c[:,2]<19)))]=1
colors[(abs(c[:,1]+6.5)<.05)&(c[:,0]>-22)&(c[:,0]<-2)&(c[:,2]>3)&(c[:,2]<22)]=1
colors[(c[:,1]<-7.6)&(c[:,1]>-11.2)&(((c[:,2]>=37)&(c[:,2]<=64))|((c[:,2]>=15)&(c[:,2]<=19)))]=2
for x in [-76,-38,0,38,76]:
 colors[(abs(c[:,0]-x)<1.31)&(c[:,1]<-8.9)&(c[:,2]>=35)&(c[:,2]<69)]=4
colors[(c[:,0]>-22.6)&(c[:,0]<-1.4)&(c[:,1]<-10)&(c[:,2]>=22)&(c[:,2]<=33)]=8
colors[(c[:,0]>=-35.11)&(c[:,0]<=-20.89)&(c[:,1]<-9.5)&(c[:,2]>3)&(c[:,2]<=65.01)]=5
colors[(c[:,0]>=-35.11)&(c[:,0]<=-20.89)&(c[:,2]>=3)&(c[:,2]<=65.01)&((c[:,1]<-19.01)|((c[:,0]<-34.51)&(c[:,1]<-9.5)))]=7
# Green grid only; recess central panels remain olive-green on y=-19.5.
colors[(abs(c[:,1]+19.5)<.01)&(c[:,0]>-33.9)&(c[:,0]<-22.1)&(c[:,2]>4)&(c[:,2]<64)]=5
colors[(c[:,2]>=66)&(c[:,1]>=-17.51)&(c[:,1]<=25.51)]=3
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=9).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
