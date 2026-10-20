"""NCKU commemorative gate. Original approximate geometry, not survey/scale replica."""
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
# 160 x 128 mm display envelope. No claimed measured architectural scale.
# Two feet genuinely separated below lintel: no invented road joining slab.
for x in [-64.5,64.5]:
 for z,h,w,d in [(0,3,36,27),(3,2.5,34,25),(5.5,2,31,22),(9,2,29,20),(14,2,34,25)]:parts.append(box(x,0,z,w-5,d,h))
 parts.append(taper(x,7.4,9.2,26,22,24,20));parts.append(taper(x,10.8,14.2,24,20,29,25))
 parts.append(box(x,0,15.8,23,18,87.4))
# Main cloud band, plain unseen upper closure. Piers are flush with its broad faces.
parts.append(box(0,0,103,152,18,25))
# Opening above bases 106/1.61 high. Recessed lintel is 3 mm behind both faces.
opening_top=16+106/1.61
parts.append(box(0,0,opening_top,108,12,103.2-opening_top))
# Abstract ruyi cloud silhouette: broad lobed shoulders and central lower lobe.
# Five offset rows. Layout is an approximation, not a measured ornament inventory.
def ellipse(x,z,rx,rz):return translate(scale(Point(0,0).buffer(1,quad_segs=10),rx,rz),x,z)
cloud=unary_union([ellipse(0,0,2.35,1.27),ellipse(-2,0,1.15,.94),ellipse(2,0,1.15,.94),ellipse(0,.83,1.15,.85),ellipse(0,-.82,1.13,.82)])
def relief(x,z,face):
 poly=list(orient(cloud).exterior.coords)[:-1];inner=list(orient(cloud.buffer(-.27)).exterior.coords)[:-1]
 r=CrossSection([poly]).extrude(.65).translate((0,0,-.2)) + CrossSection([inner]).extrude(.6).translate((0,0,.3))
 # Local XY cloud maps onto vertical XZ; extrusion maps toward exterior.
 r=r.rotate((90,0,0))
 if face=='west':r=r.translate((x,-9,z))
 elif face=='east':r=r.rotate((0,0,180)).translate((x,9,z))
 elif face=='north':r=r.rotate((0,0,90)).translate((76,x,z))
 else:r=r.rotate((0,0,-90)).translate((-76,x,z))
 parts.append(r);features.append({'face':face,'horizontal_mm':x,'z_mm':z,'root_overlap_mm':.2,'max_projection_mm':.9})
for row in range(5):
 z=106+row*4.65
 n=19 if row%2==0 else 20
 for x in np.linspace(-(n-1)*3.76,(n-1)*3.76,n):
  for face in ['west','east']:relief(float(x),z,face)
 for x in ([-4,4] if row%2==0 else [0]):
  for face in ['north','south']:relief(x,z,face)
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('warm_white_portal','#DFDFD6'),('charcoal_xumi_pedestals','#303333'),('warm_white_cloud_relief','#E7E6DC')]
colors=np.zeros(len(f),dtype=int);colors[c[:,2]<16.001]=1
colors[(c[:,2]>103.01)&((abs(c[:,1])>9.001)|(abs(c[:,0])>76.001))]=2
(O/'qa/design-features.json').write_text(json.dumps({'cloud_reliefs':features,'count':len(features),'rows':5,'source_total':210,'layout_measured':False,'opening_above_base_width_mm':106,'opening_above_base_height_mm':106/1.61,'overall_width_mm':160,'overall_height_mm':128,'depth_photo_estimated_mm':18},indent=2)+'\n')
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
