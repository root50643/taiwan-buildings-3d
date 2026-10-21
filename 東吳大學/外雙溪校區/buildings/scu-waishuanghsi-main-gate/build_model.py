"""SCU Waishuanghsi single-arch gate. Source-photo approximation, not a survey.
Front is negative Y; x left-to-right reads 學 大 [seal] 吳 東.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,FillRule
from shapely.geometry import Polygon,Point,box as rect
from shapely.ops import unary_union
from shapely import contains_xy
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def solid(t):
 if t.volume<0:t.invert()
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def cross(poly):
 ps=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly];loops=[]
 from shapely.geometry.polygon import orient
 for p in ps:
  if p.is_empty:continue
  p=orient(p,sign=1);loops.append(np.array(p.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in p.interiors)
 return CrossSection(loops)
def xz(poly,y,depth):return cross(poly).extrude(depth).transform([[1,0,0,0],[0,0,-1,y+depth/2],[0,1,0,0]])
parts=[];base=3.5
# Low flat connector is an invented printing/display plinth, NOT a surveyed road platform.
parts.append(box(0,0,0,194,40,base))
# Rectangular deep piers have four narrow bevels and sloping/faceted heads.
plan=[(-5,-11),(5,-11),(7,-9),(7,9),(5,11),(-5,11),(-7,9),(-7,-9)]
for x in [-83,83]:
 vs=[(x+a,b,base-.2) for a,b in plan]+[(x+a,b,base+150-max(0,b+5)*.30-max(0,abs(a)-5)*.65) for a,b in plan]
 fs=[];n=len(plan)
 for k in range(1,n-1):fs.extend([(0,k+1,k),(n,n+k,n+k+1)])
 for k in range(n):j=(k+1)%n;fs.extend([(k,j,n+j),(k,n+j,n+k)])
 parts.append(solid(trimesh.Trimesh(vs,fs,process=False)))
# A shallow, rounded-shoulder arch cut leaves long upright legs and a solid spandrel.
def bez(p,a,b,q,t):
 u=1-t;return (u**3*np.array(p)+3*u*u*t*np.array(a)+3*u*t*t*np.array(b)+t**3*np.array(q)).tolist()
left=[bez((-73,97.5),(-73,101.5),(-71,104.1),(-67,105.5),t) for t in np.linspace(0,1,25)]
arc=[(float(x),117.5-12*(float(x)/67)**2) for x in np.linspace(-67,67,161)]
right=[(-x,z) for x,z in left[::-1]]
curve=left[:-1]+arc+right[1:]
opening=Polygon([(-73,base-.6),(73,base-.6)]+curve[::-1])
wall=rect(-80,base-.3,80,139.5).difference(opening)
parts.append(xz(wall,0,11.6))
# Actual continuous lower arch band, modestly protruding both sides.
band=opening.buffer(2.0,quad_segs=20).difference(opening).intersection(rect(-76,92,76,121))
for y in [-5.95,5.95]:parts.append(xz(band,y,.8))
# Continuous fine cap; front plaque interrupts it locally, rear remains blank and continuous.
parts.append(box(0,0,137.7,158,13.6,2.2))
# Front seal backing: full rectangular top, lower/side bevels; no rear duplicate.
p0=[(-12,118.8),(12,118.8),(12,142.2),(-12,142.2)]
p1=[(-10.5,120.3),(10.5,120.3),(10.5,142.2),(-10.5,142.2)]
vs=[(x,-5.5,z) for x,z in p0]+[(x,-9,z) for x,z in p1]
fs=[(0,2,1),(0,3,2),(4,5,6),(4,6,7)]
for k in range(4):j=(k+1)%4;fs.extend([(k,j,j+4),(k,j+4,k+4)])
parts.append(solid(trimesh.Trimesh(vs,fs,process=False)))
seal=Point(0,131.3).buffer(9.0,quad_segs=64)
parts.append(xz(seal,-9.12,.6))
redring=seal.difference(Point(0,131.3).buffer(8.15,quad_segs=64))
innerring=Point(0,131.3).buffer(6.55,quad_segs=64).difference(Point(0,131.3).buffer(6.10,quad_segs=64))
parts.append(xz(redring,-9.47,.35));parts.append(xz(innerring,-9.47,.35))
# Legible school name in a disclosed typeface substitute, not fabricated reproduction of calligraphy.
glyphdata=json.loads((O/'glyphs.json').read_text())['loops'];glyphpolys=[]
for char,x in zip('學大吳東',[-56,-29,29,56]):
 loops=glyphdata[char];q=np.array([p for loop in loops for p in loop]);lo=q.min(axis=0);hi=q.max(axis=0);sc=14.3/max(hi-lo)
 loops=[(np.array(loop)-(lo+hi)/2)*sc+[x,127.1] for loop in loops]
 cs=CrossSection(loops,FillRule.EvenOdd)
 # A tiny contour round/buffer strengthens serif ends but is not a global print guarantee.
 cs=cs.offset(.10, join_type=__import__('manifold3d').JoinType.Round, circular_segments=12)
 parts.append(cs.extrude(1.15).transform([[1,0,0,0],[0,0,-1,-5.65],[0,1,0,0]]))
 g=Polygon()
 for p in cs.to_polygons():g=g.symmetric_difference(Polygon(p))
 glyphpolys.append(g)
glyphs=unary_union(glyphpolys)
# Small seal lettering is intentionally omitted; two red rings are a simplified emblem.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('ivory_white_gate','#EEEDE6'),('charcoal_raised_characters','#242A2B'),('carmine_seal_rings','#AD3038'),('white_seal_field','#ECE9DB'),('gray_printing_plinth','#929A9C')]
c=t.triangles_center;colors=np.zeros(len(f),dtype=int)
colors[t.triangles.max(axis=1)[:,2]<=base+.001]=4
colors[(c[:,1]<-5.80)&contains_xy(glyphs.buffer(.002),c[:,0],c[:,2])]=1
colors[(c[:,1]<-9.0)&contains_xy(seal.buffer(.002),c[:,0],c[:,2])]=3
colors[(c[:,1]<-9.29)&contains_xy(redring.union(innerring).buffer(.002),c[:,0],c[:,2])]=2
features=dict(estimated_not_surveyed=True,school='東吳大學',campus='外雙溪校區',slug='scu-waishuanghsi-main-gate',target_path='東吳大學/外雙溪校區/buildings/scu-waishuanghsi-main-gate',arch_opening_count=1,deep_pier_count=2,pier_center_x=[-83,83],pier_width_mm=14,pier_depth_mm=22,gate_width_mm=180,gate_max_height_above_base_mm=150,plinth_dimensions_mm=[194,40,3.5],plinth_is_printing_addition_not_site_geometry=True,spandrel_depth_mm=11.6,arch_crown_z_mm=117.5,arch_shoulder_z_mm=97.5,front_direction='negative Y',front_character_order_left_to_right='學 大 [seal] 吳 東',rear_characters=0,rear_seal=0,rear_plaque=0,plaque_front_only=True,seal_simplification='two red rings and white field; no illegible tiny seal lettering invented',typeface_substitution='Noto Serif CJK TC Bold contours, not Sun Ke calligraphy',source_date_range='2003–2019 dated photos plus capture-unknown rear photo and 2024-created MOC PDF',no_actual_print=True,support_free_certified=False,excluded=['Suzhou old triple-arch gate','Wangxing Bridge entrance marker','guardhouse','road barriers','movable gate leaves','shops','street context','exact tiny seal lettering'],uncertain=['all dimensions','precise pier cross-section','cap facet geometry','hidden joints','micro mouldings','top drainage'])
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
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
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
