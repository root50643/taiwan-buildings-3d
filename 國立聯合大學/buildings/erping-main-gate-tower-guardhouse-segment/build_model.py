"""NUU Erping Shan gate tower and attached guard booth. Original approximate geometry, not survey/scale replica."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Point
from shapely.affinity import scale,translate
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
parts=[];features=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def taper(x,z0,z1,w0,d0,w1,d1):
 pts=[[x+sx*w/2,sy*d/2,z] for z,w,d in [(z0,w0,d0),(z1,w1,d1)] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 t=trimesh.convex.convex_hull(np.asarray(pts));return Manifold(Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
# 120 mm architectural height on a separate neutral 3 mm display plinth.
# Approximate two-view exterior; unseen rear is plain solid closure.
from shapely.geometry import box as sbox
from shapely.geometry.polygon import orient

def prism(poly,z,h):
 return CrossSection([list(orient(poly).exterior.coords)[:-1]]).extrude(h).translate((0,0,z))
plinth=prism(sbox(-17,-11,22,40).buffer(2,quad_segs=10),0,3)
tower=box(0,0,2.8,24,13,120.2)
# Shallow backed recesses, NOT an invented through-slot or interior.
tower-=box(0,-6.2,18,17,2.6,84)
tower-=box(11.8,0,18,2.8,7,84)
# Small attached booth, rounded outside edge, flat unknown rear closure.
foot=sbox(-7,5,13,31).buffer(3,quad_segs=16)
booth=prism(foot,2.8,40.2)
# Framed backed doorway at front-right junction.
booth-=box(11,3,5,7,4,31)
# Pale frame around actual side bay; flat backed inset glazing, no room.
frame=box(16,20,14,2.4,18,20)
booth+=frame
booth-=box(17,20,15.4,2,15.2,17.2)
# Actual steel divider bars and middle rail intersect backing.
for y in [17.5,22.5]:booth+=box(17, y,15.3,1.6,1,17.4)
booth+=box(17,20,24,1.6,15.4,1.1)
# Door division; no operating detail represented.
booth+=box(11,3.4,21,7.2,1.6,1.1)
fascia=prism(foot.buffer(.35,quad_segs=16),42.8,2.2)
cap=prism(foot.buffer(1.6,quad_segs=16),44.8,2)
parts=[plinth,tower,booth,fascia,cap]
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('warm_white_tower','#E1E0D7'),('light_gray_booth','#C9CBC7'),('pale_window_frames_cap','#DFDFD6'),('desaturated_glazing','#455C5A'),('ochre_fascia','#A37C50'),('neutral_display_plinth','#8D9394'),('recess_backing','#C1C3BC')]
colors=np.zeros(len(f),dtype=int)
# Classify booth surfaces only outside tower footprint; untouched unseen back stays neutral.
boothmask=(c[:,2]<46.81)&((c[:,1]>6.501)|(c[:,0]>12.001))
colors[boothmask]=1
colors[boothmask&(c[:,2]>42.79)&(c[:,2]<44.801)]=4
colors[boothmask&(c[:,2]>=44.8)]=2
# Explicit recessed tower face/backings are shallow and neutral.
colors[(c[:,2]>18)&(c[:,2]<102)&(((abs(c[:,0])<8.51)&(c[:,1]>-5.01)&(c[:,1]<-4.89))|((c[:,0]>10.39)&(c[:,0]<10.41)&(abs(c[:,1])<3.51)))]=6
# Window box and rails, then backed recessed glass faces.
window=(c[:,0]>15.99)&(c[:,1]>10.99)&(c[:,1]<29.01)&(c[:,2]>13.99)&(c[:,2]<34.01)
colors[window]=2
colors[window&(abs(c[:,0]-16)<.01)&(c[:,1]>12.4)&(c[:,1]<27.6)&(c[:,2]>15.4)&(c[:,2]<32.6)]=3
# Exposed doorway back is behind front tower and conservative dark panel.
colors[(c[:,0]>7.5)&(c[:,0]<14.5)&(abs(c[:,1]-5)<.01)&(c[:,2]>5)&(c[:,2]<36)]=3
colors[c[:,2]<3.001]=5
(O/'qa/design-features.json').write_text(json.dumps({'architectural_tower_height_mm':120,'tower_width_mm':24,'tower_depth_mm':13,'booth_cap_top_mm':46.8,'plinth_height_mm':3,'tower_recesses':'shallow solid backed; through topology unknown','cap_thickness_mm':2,'side_window_frame_min_mm':1.4,'mullion_width_mm':1,'estimated_not_surveyed':True},indent=2)+'\n')
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
