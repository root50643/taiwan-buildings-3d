"""Hongdao Hall entrance/colonnade, source-photo proportion study. Front -Y.
Relative display millimetres; neither measured nor whole-building reconstruction.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Neutral display base and expressly truncated shallow rear wall.
add(0,-11,0,156,70,3)
add(0,14,3,144,4,96)
# Four source-bounded flanking bays: red-brown strips against recessed glazing.
for x in [-55,-33,33,55]:
 add(x,5,3,22,18,94)
 for z,h in [(9,11),(25,20),(49,20),(73,21)]:
  cut(x,-4,z,14,5,h)
# Central opening is open from front to recessed door wall (NOT a through building).
add(0,6,3,44,20,19)
add(0,8,48,44,14,49)
cut(0,1,76,34,6,18)
# Broad roof overhang and six unusually tall narrow external piers.
add(0,-1,97,151,37,3.5)
for x in [-66,-44,-22,22,44,66]:add(x,-9,3,2.8,7,94)
# Lower apron beam and two entrance portal legs; panel and bridge supported behind.
add(0,-7,20,140,8,3)
add(0,-8,46.5,46,8,3.5)
# Upper emblem panel is a blank dark board; no invented text or crest.
add(0,0,52,33,4,20)
# Stairs rise to the entry, no floating stair treads.
for i in range(19):add(0,-40+i*1.45,3,36,1.7,i+1)
add(0,-10,3,36,8,19)
# Stair flanking white solid parapets follow broad stair incline; compressed depth.
def buttress(x):
 # XY cross section (y,z), rotate to world YZ, extrude along X.
 return CrossSection([[(-42,3),(-13,3),(-13,26),(-17,26),(-42,6)]]).extrude(3).rotate((90,0,90)).translate((x-1.5,0,0))
parts.extend([buttress(-20),buttress(20)])
m=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
d=[]
# Backed physical glazing and window frames. Bays are a visible sample, not a count claim.
for x in [-55,-33,33,55]:
 for z,h in [(9,11),(25,20),(49,20),(73,21)]:
  for dx in [-7,0,7]:d.append(box(x+dx,-2.5,z,.9,2.4,h))
  for zz in [z,z+h/2,z+h]:d.append(box(x,-2.5,zz,14.9,2.4,.9))
# Upper central horizontal window and entry transom.
for x in [-17,-8.5,0,8.5,17]:d.append(box(x,2,76,.9,4.4,18))
for z in [76,85,94]:d.append(box(0,2,z,34.9,4.4,.9))
# Central entry retains visible depth; dark backed door and fine frame.
d.append(box(0,11.5,22,34,2,24.5))
for x in [-17,-8.5,0,8.5,17]:d.append(box(x,9.9,22,1.1,2.2,24.5))
for z in [22,39,46]:d.append(box(0,9.9,z,35,2.2,1.1))
m=m+Manifold.batch_boolean(d,OpType.Add)
assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Float32 STL is the canonical delivery surface used by all exchanges and renders.
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center;n=t.face_normals
palette=[('ivory_concrete','#DDD9C9'),('red_brown_wall','#77473D'),('window_frame','#B9B8AD'),('glazing','#485757'),('emblem_board_blank','#4E4144'),('stair_stone','#95938B'),('cut_boundary_neutral','#B8B7AF'),('entry_shadow_glazing','#30393B')]
colors=np.zeros(len(f),dtype=int)
# Red-brown wall uprights behind external pale piers.
for x in [-55,-33,33,55]:
 colors[(abs(c[:,1]+4)<.08)&(c[:,2]>23)&(c[:,2]<97)&(abs(c[:,0]-x)>7.4)&(abs(c[:,0]-x)<11.1)]=1
for x in [-55,-33,33,55]:
 for z,h in [(9,11),(25,20),(49,20),(73,21)]:
  r=(abs(c[:,0]-x)<7.6)&(c[:,2]>=z)&(c[:,2]<=z+h+.91)
  colors[r&(c[:,1]<-1.45)&(c[:,1]>-3.7)]=2
  colors[r&(abs(c[:,1]+1.5)<.08)]=3
r=(abs(c[:,0])<17.6)&(c[:,2]>=76)&(c[:,2]<=95)
colors[r&(c[:,1]<4.1)]=2;colors[r&(abs(c[:,1]-4)<.08)]=3
colors[(abs(c[:,0])<16.51)&(c[:,2]>52)&(c[:,2]<72.01)&(c[:,1]<.01)]=4
colors[(c[:,1]<-14)&(c[:,2]<=22.01)&(abs(c[:,0])<18.1)]=5
colors[(c[:,1]>8.7)&(c[:,1]<10.61)&(c[:,2]>=22)&(c[:,2]<46.6)&(abs(c[:,0])<17.6)]=2
colors[(abs(c[:,1]-10.5)<.08)&(c[:,2]>22)&(c[:,2]<46.5)&(abs(c[:,0])<17)]=7
colors[(c[:,2]<3.01)|((n[:,1]>.9)&(c[:,1]>15.9))|((abs(c[:,0])>71.9)&(c[:,2]<97))]=6
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
