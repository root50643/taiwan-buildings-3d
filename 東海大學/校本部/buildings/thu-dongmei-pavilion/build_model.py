"""Photo-approximate THU Dongmei Pavilion, not measured dimensions. Display millimetres."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,Point,box as rect
from shapely.ops import unary_union
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def solid(t):
 if t.volume<0:t.invert()
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def cross(poly):
 ps=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
 loops=[]
 for p in ps:
  if p.is_empty:continue
  from shapely.geometry.polygon import orient
  p=orient(p,sign=1);loops.append(np.array(p.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in p.interiors)
 return CrossSection(loops)
def yz(poly,x,depth):return cross(poly).extrude(depth).transform([[0,0,1,x-depth/2],[1,0,0,0],[0,1,0,0]])
def profile(y):return 54+25*np.exp(-(np.asarray(y)/19)**2)+4*(abs(np.asarray(y))/43)**8
parts=[]
# Three shallow, broad local red steps: deliberately omit island, shoreline and water.
parts += [box(0,0,0,176,114,2),box(0,0,1.8,166,104,2),box(0,0,3.6,156,94,2.4),box(0,0,5.8,145,83,1)]
floor=6.6
# Rounded stepped tile-panel silhouette; two actual open moon portals.
rough=Polygon([(-27,floor),(-27,39),(-25,43),(-16,43),(-16,51),(-14,53),(14,53),(16,51),(16,43),(25,43),(27,39),(27,floor)])
panel=rough.buffer(1.5,quad_segs=12).buffer(-1.5,quad_segs=12).intersection(rect(-40,floor,40,70))
moon=Point(0,21.2).buffer(17.2,quad_segs=64)
# Circle intersects the floor and is therefore an open portal, not a floating closed ring.
panel_full=panel.difference(moon)
tilearea=panel.buffer(-1.35,quad_segs=12).difference(moon.buffer(1.2,quad_segs=16))
tiles=[]
for y in np.arange(-28,28,3.6):
 for z in np.arange(5.6,54,3.6):
  p=rect(y+.11,z+.11,y+3.49,z+3.49).intersection(tilearea)
  if not p.is_empty and p.area>.025:tiles.append(p)
tilepoly=unary_union(tiles)
ys=np.linspace(-36,36,145);outer=Polygon([(-36,floor),(36,floor)]+[(float(y),float(profile(y)-2.2)) for y in ys[::-1]])
gap=panel.buffer(3.1,quad_segs=16).union(rect(-30.1,-1,30.1,floor+1))
frame=outer.difference(gap).difference(Point(0,66.2).buffer(3.7,quad_segs=48))
for x in [-52,52]:
 parts += [yz(frame,x,5.2),yz(panel_full,x,2.8),yz(tilepoly,x-1.46,.3),yz(tilepoly,x+1.46,.3)]
 # Large softened corner feet integrated into pillars, not separate dark stones.
 for y in [-33,33]:
  foot=Polygon([(y-6.5,floor),(y-5.8,floor+2),(y-3.8,floor+5.3),(y-2.1,floor+6.6),(y+2.1,floor+6.6),(y+3.8,floor+5.3),(y+5.8,floor+2),(y+6.5,floor)])
  parts.append(yz(foot,x,7.4))
# Long sides are completely open: lintels plus stepped end brackets only.
for y in [-33,33]:
 parts.append(box(0,y,50.8,109,5.2,4.8))
 for x in [-48.8,48.8]:
  parts += [box(x,y,47.5,8,5.8,3.6),box(x,y,45.8,5.5,5.2,2)]
# Visible longitudinal underside beams spaced across the curved cross-section.
for y in [-27,-18,-9,0,9,18,27]:parts.append(box(0,y,float(profile(y)-5.2),107,2.2,3.5))
# Curved double-slope orange shell; sampled cross-section is not a straight triangular roof.
ys=np.linspace(-43,43,173);upper=[(float(y),float(profile(y))) for y in ys]
roof=Polygon(upper+[(float(y),float(profile(y)-2.5)) for y in ys[::-1]])
parts.append(yz(roof,0,126))
# White curved gable fascia, both ends. Intentional roof overhang beyond column frames.
cap=Polygon([(float(y),float(profile(y)+1.3)) for y in ys]+[(float(y),float(profile(y)-3.0)) for y in ys[::-1]])
for x in [-63,63]:parts.append(yz(cap,x,2.8))
# Integral rounded tile ribs running from ridge to each eave, regularly simplified count.
def rib(x):
 vertices=[];faces=[];rr=.72; segs=10
 for y in ys:
  z=float(profile(y))-.25
  for k in range(segs):
   th=2*np.pi*k/segs;vertices.append((x+rr*np.cos(th),float(y),z+rr*np.sin(th)))
 for j in range(len(ys)-1):
  for k in range(segs):
   a=j*segs+k;b=j*segs+(k+1)%segs;c=(j+1)*segs+(k+1)%segs;d=(j+1)*segs+k;faces.extend([(a,b,c),(a,c,d)])
 faces.extend((0,k+1,k) for k in range(1,segs-1));q=(len(ys)-1)*segs;faces.extend((q,q+k,q+k+1) for k in range(1,segs-1))
 return solid(trimesh.Trimesh(vertices,faces,process=False))
ribcenters=np.linspace(-59,59,39)
parts.extend(rib(float(x)) for x in ribcenters)
# Tile courses form shallow real overlap lines on the two curved slopes.
for y in [-39,-33,-27,-21,-15,-9,-3,3,9,15,21,27,33,39]:
 strip=Polygon([(y-.22,float(profile(y-.22))-.18),(y+.22,float(profile(y+.22))-.18),(y+.22,float(profile(y+.22))+.20),(y-.22,float(profile(y-.22))+.20)])
 parts.append(yz(strip,0,122))
# Blank long-side hanging plaque. Illegible source inscription intentionally not invented.
for y in [-29.8,29.8]:
 parts += [box(0,y,43,23,1.4,7.8),box(0,y+(.76 if y>0 else -.76),44,20,.22,5.5)]
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('cream_structural_frame','#E8E4D5'),('orange_glazed_roof','#D99430'),('ochre_wall_tiles','#B5672D'),('red_platform_steps','#A75E47'),('gray_inner_floor','#A5A59B'),('blank_plaque','#806640')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;hi=t.triangles.max(axis=1)
colors[hi[:,2]<=6.801]=3
colors[(c[:,2]>5.99)&(hi[:,2]<=6.801)&(abs(c[:,0])<72.51)&(abs(c[:,1])<41.51)]=4
roofmask=(c[:,2]>=profile(c[:,1])-2.51)&(abs(c[:,0])<61.61)&(abs(c[:,1])<=43.01)
colors[roofmask]=1
from shapely import contains_xy
wallmask=(np.abs(np.abs(c[:,0])-52)<1.622)&(np.abs(np.abs(c[:,0])-52)>1.395)&(c[:,2]<54)&contains_xy(tilepoly,c[:,1],c[:,2])
colors[wallmask]=2
colors[(abs(c[:,0])<=11.501)&(abs(abs(c[:,1])-29.8)<.89)&(c[:,2]>=42.99)&(c[:,2]<=50.81)]=5
features=dict(estimated_not_surveyed=True,source_appearance='2017–2019 photographs; official album date not capture date',moon_gate_count=2,corner_support_count=4,open_long_side_count=2,small_gable_oculi=2,far_oculus_symmetric_inference=True,roof_type='curved two-slope gable, not hip or octagon',roof_ribs=39,roof_curve='54+25*exp(-(y/19)^2)+4*(abs(y)/43)^8, display millimetres',frame_end_x=[-52,52],corner_y=[-33,33],floor_z=6.8,moon_center_yz=[0,21.2],moon_radius=17.2,panel_thickness=2.8,frame_depth=5.2,roof_vertical_thickness=2.5,oculus_center_yz=[0,66.2],oculus_radius=3.7,step_count=3,platform_dimensions=[176,114,6.8],plaque='blank; source text too small',no_actual_print=True,support_free_certified=False,omitted=['shoreline','lake','trees','surrounding walk','weathering','unreadable text','exact joinery'],notes='Rounded stepped panel margins and surrounding air gaps preserved. Both moon gates confirmed from photographs. Far tiny oculus and paired plaques symmetrically inferred. Simplified continuous regular ribs/courses, strengthened display thicknesses, estimated local plinth edges and all dimensions.')
(O/'qa/design-features.json').write_text(json.dumps(features,indent=2)+'\n')
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
