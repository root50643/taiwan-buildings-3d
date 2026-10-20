"""OCU as-built folded access pavilion. Arbitrary photographic display units.
+Y = track; -Y = outer path; X is pavilion long axis (not surveyed cardinal).
Basement cut, stair count, shell thickness and hidden closure are display assumptions.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def hull(points):
 t=trimesh.convex.convex_hull(np.asarray(points,float));return Manifold(Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
def prism(tri,lower,upper):return hull([[x,y,z+q] for q in [lower,upper] for x,y,z in tri])
def under(tri):return hull(tri+[[x,y,3] for x,y,z in tri])
# A long asymmetric folded roof: source-mapped e0 path side / e3 track side.
A=(0,22,14);B=(0,8,15.02);C=(25,-20,24.70);D=(62,-20,36.00);E=(95,22,43);F=(113,-18,29);G=(130,-18,27);H=(130,22,34)
# The main long slope is nearly planar; the far-end cap has distinct folds.
tris=[[A,B,C],[A,C,D],[A,D,E],[E,D,F],[E,F,H],[F,G,H]]
roof=Manifold.batch_boolean([prism(t,-2.4,0) for t in tris],OpType.Add)
volume=Manifold.batch_boolean([under(t) for t in tris],OpType.Add)
# Real triangular recesses, opaque glazing 0.9 mm below roof (not clear holes).
def bary(tri,weights):return tuple(sum(w*tri[i][j] for i,w in enumerate(weights)) for j in range(3))
skylights=[]
for tri,weights in [(tris[2],[(.13,.18,.69),(.29,.18,.53),(.16,.48,.36)]),(tris[4],[(.17,.22,.61),(.13,.47,.40),(.42,.23,.35)])]:
 q=[bary(tri,w) for w in weights];skylights.append(q);roof=roof-prism(q,-.9,3)
parts.append(roof)
# Neutral plinth is a display crop, not entire sports complex boundary.
parts.append(box(65,0,0,146,65,3))
# Cropped basement adjacency / upper arrival platform, genuine open pocket.
platform=box(65,-3,3,136,51,7)
platform=platform-box(54,-13,3,47,22,9)
parts.append(platform)
# Long solid track-side wall exactly follows varying roof edge.
parts.append(volume ^ box(65,21,3,130,2.6,44))
# Inset red wall/core on open path-facing side, lower than shell only where visible.
parts.append(volume ^ box(66,-4,3,89,2.8,44))
# Conservative end crop closures, explicitly not measured hidden facade.
for x in [1.1,128.9]:parts.append(volume ^ box(x,9,3,2.2,24,44))
# Partial stair run in cropped well; 4 symbolic treads, not observed count.
for i in range(4):parts.append(box(35+i*5,-13,3,5.2,20,7-i*1.6))
# Arrival landing is above lower basin and attached to side platform.
parts.append(box(86,-18,8,17,19,2))
# Guardrails: rooted 1.2 mm uprights and top rails along actual void edge.
rails=[]
for x in np.arange(30.5,78,4):rails.append(box(float(x),-24.7,9.5,1.2,1.4,9.5))
rails.append(box(54,-24.7,18,49,1.5,1.2))
for y in np.arange(-24,-5,4):rails.append(box(77.5,float(y),9.5,1.4,1.2,9.5))
rails.append(box(77.5,-15,18,1.5,21,1.2))
# Unconfirmed far-end closure; neutral material, not inferred glazing from shadows.
parts.append(volume ^ box(119,-13,10,18,1.5,30))
parts+=rails
m=Manifold.batch_boolean(parts,OpType.Add)
assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center;n=t.face_normals
palette=[('pale_folded_concrete','#D9DAD4'),('recessed_opaque_skylight','#72A6AD'),('red_orange_inset','#BA422B'),('dark_guardrails','#424E50'),('display_crop_base','#B6B5AD'),('unconfirmed_end_closure','#AAAFA9')]
colors=np.zeros(len(f),dtype=int)
colors[c[:,2]<10.01]=4
colors[(abs(c[:,1]+5.4)<.03)&(c[:,0]>21)&(c[:,0]<111)&(c[:,2]>10)]=2
colors[(c[:,0]>109)&(abs(c[:,1]+13.75)<.04)&(c[:,2]>10)]=5
colors[(c[:,2]>10.01)&(c[:,2]<19.21)&(((abs(c[:,1]+24.7)<.76)&(c[:,0]>29)&(c[:,0]<79))|((abs(c[:,0]-77.5)<.76)&(c[:,1]>-26)&(c[:,1]<-4)))]=3
# Recess bottom planes are 0.9 below each source-defined triangular roof plane.
from shapely.geometry import Polygon,Point
for q in skylights:
 q=np.array(q);normal=np.cross(q[1]-q[0],q[2]-q[0]);z=q[0,2]-(normal[0]*(c[:,0]-q[0,0])+normal[1]*(c[:,1]-q[0,1]))/normal[2]-.9
 poly=Polygon(q[:,:2]);mask=np.array([poly.buffer(.001).covers(Point(x,y)) for x,y in c[:,:2]])&(abs(c[:,2]-z)<.003);colors[mask]=1
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-registration.json').write_text(json.dumps({'roof_vertices':{k:list(globals()[k]) for k in 'ABCDEFGH'},'roof_triangles':tris,'skylight_triangles':skylights,'source_views':['e0 opposite path-side','e3 track-side'],'excluded_view':'e1 design model','dimensions_not_measured':True},indent=2)+'\n')
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
