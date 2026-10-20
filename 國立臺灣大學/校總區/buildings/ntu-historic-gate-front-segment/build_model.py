"""NTU bounded historical gate front; photo estimates, not surveyed dimensions.
+y campusward. Neutral rear display closure is NOT guardhouse or actual roof.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def hull(points):
 t=trimesh.convex.convex_hull(np.asarray(points,float));return Manifold(Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
W=54.;S=6.5;R=((W/2)**2+S*S)/(2*S)
def curve(x):return R-np.sqrt(R*R-np.asarray(x)**2)
def arcsolid(z,h,offset=0,back=10):
 xs=np.linspace(-27,27,81);poly=[[float(x),float(curve(x)+offset)] for x in xs]+[[27,back],[-27,back]]
 return CrossSection([poly]).extrude(h).translate((0,0,z))
# Thin neutral plinth joins the bounded assembly. Not an actual site pavement plan.
parts.append(box(0,4,0,154,26,3))
wall=arcsolid(3,42)
# Real 2 mm-deep front recesses with opaque bottoms, not interior/window transparency.
windows=[(-15,5.4),(0,8.6),(15,5.4)]
for x,w in windows:wall=wall-box(x,float(curve(x))-.7,17,w,5.4,16)
# Shallow horizontal masonry courses; dimensions and count simplified for print.
# Mortar courses follow the actual bowed front with a 0.18 mm relief depth.
for z in np.arange(7,44,2.6):
 strip=arcsolid(float(z),.24,-.5)-arcsolid(float(z)-.01,.26,.18)
 wall=wall-strip
# Staggered vertical joints: short boxes at bowed surface, shallow, visual simplification.
for row,z in enumerate(np.arange(7.24,44,2.6)):
 for x in np.arange(-25+(row%2)*2.6,27,5.2):
  y=float(curve(x));wall=wall-box(float(x),y-.2,float(z),.22,.9,2.35)
parts.append(wall)
parts.append(arcsolid(44.8,2.2,-.6,10.3)-arcsolid(44.7,2.4,2.0,10.4))
# Pale plaque follows bow, deliberately no text reconstruction.
plaque=arcsolid(38,4.2,-.35,2.8)^box(0,1,38,25,9,4.2);parts.append(plaque)
# Three stepped flag-pedestal blocks. Full flag/pole deliberately omitted.
for w,z,h in [(28,44.8,4.8),(22,49.5,2.5),(12,51.9,2.3)]:parts.append(box(0,5,z,w,8,h))
# Two open adjacent pedestrian portals, with short photographed-depth lintels.
for sign in [-1,1]:
 for x,w in [(34.5,15),(58.5,13)]:
  wing=box(sign*x,6,3,w,7,24)
  for z in np.arange(7,27,2.6):wing=wing-box(sign*x,2.4,float(z),w+.1,.6,.24)
  for row,z in enumerate(np.arange(7.24,27,2.6)):
   for dx in np.arange(-w/2+2+(row%2)*2.6,w/2,5.2):wing=wing-box(sign*x+float(dx),2.4,float(z),.22,.6,2.35)
  parts.append(wing)
 parts.append(box(sign*46,6,26.8,40,8.2,3.3))
 # Eight-sided stone post; stone plinth and shoulder visibly wider than shaft.
 for z,h,r in [(3,2.2,6.4),(5.1,26.8,5.9),(31.7,2.3,6.2)]:
  post=Manifold.cylinder(h,r,r,8).rotate((0,0,22.5)).translate((sign*68,6,z))
  if h>20:
   for zz in np.arange(9.5,31,4.4):
    outer=Manifold.cylinder(.22,6.5,6.5,8).rotate((0,0,22.5)).translate((sign*68,6,float(zz)))
    inner=Manifold.cylinder(.24,5.72,5.72,8).rotate((0,0,22.5)).translate((sign*68,6,float(zz)-.01))
    post=post-(outer-inner)
  parts.append(post)
 # Opaque dark lantern block, with raised frame and low pyramid cap.
 parts.append(box(sign*68,6,33.8,8.1,7.4,5.6))
 for x in [-3.8,3.8]:parts.append(box(sign*68+x,2.15,33.8,.8,1,5.8))
 parts.append(hull([[sign*68+x,6+y,39.2] for x,y in [(-5.5,-4.8),(5.5,-4.8),(5.5,4.8),(-5.5,4.8)]]+[[sign*68,6,41.8]]))
# Neutral back cut plane and low top support: expressly invented display closure.
parts.append(box(0,10.3,3,54,1.4,41.7))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center;n=t.face_normals
palette=[('weathered_brown_masonry','#89684B'),('pale_stone_coping_and_posts','#B1AA8D'),('recessed_opaque_windows','#393D36'),('pale_blank_plaque','#D2CBB4'),('dark_bronze_lantern_frame','#454D43'),('muted_lantern_panels','#72796A'),('neutral_display_cut_support','#9D9E9C')]
colors=np.zeros(len(f),dtype=int)
colors[(c[:,2]<3.01)|((c[:,1]>9.58)&(abs(c[:,0])<27.01))]=6
colors[(c[:,2]>3.01)&(c[:,2]<7.01)]=1
colors[(c[:,2]>=44.79)|(abs(c[:,0])>61.9)|((c[:,2]>26.79)&(c[:,2]<30.11)&(abs(c[:,0])>26))]=1
colors[(abs(c[:,2]-45)<.015)&(c[:,1]>2)&(abs(c[:,0])<27.01)]=6
colors[(c[:,2]>37.99)&(c[:,2]<42.21)&(abs(c[:,0])<12.51)&(c[:,1]<2.81)]=3
for x,w in windows:
 colors[(abs(c[:,0]-x)<w/2+.01)&(c[:,2]>16.99)&(c[:,2]<33.01)&(c[:,1]<float(curve(x))+2.01)]=2
colors[(abs(c[:,0])>62)&(c[:,2]>33.79)]=4
colors[(abs(abs(c[:,0])-68)<3.3)&(c[:,2]>34.1)&(c[:,2]<39.19)&(c[:,1]<2.4)]=5
# Avoid centroid-color wedges on long triangulated wing/base faces.
wing_front=((abs(c[:,1]-2.5)<.015)|(abs(c[:,1]-2.7)<.015))&(abs(c[:,0])>27)&(c[:,2]>7.01)&(c[:,2]<26.79)
colors[wing_front]=0
colors[c[:,2]<3.001]=6
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
