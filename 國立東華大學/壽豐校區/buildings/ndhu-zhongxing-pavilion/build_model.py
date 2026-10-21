"""NDHU Zhongxing pavilion: two HALF-oval rising leaves, four curved broad legs.
Original source-observed approximation, not surveyed dimensions or exact glass grid.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def poly(points,h):
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
 if area<0:points=points[::-1]
 cs=CrossSection([points]);return cs.extrude(h)
def roofshape(points,h,z,side):
 # XY half ellipse, reflected for rear leaf, shear upwards from low straight diameter.
 return poly(points,h).transform([[1,0,0,0],[0,side,0,0],[0,.64,1,z]])
angles=np.linspace(0,np.pi,97)
outer=[(59*math.cos(a),49*math.sin(a)) for a in angles]
inner=[(53.5*math.cos(a),43.5*math.sin(a)) for a in angles]
for side in [-1,1]:
 # Half disk ONLY: straight closing edge is shared beam, no second curved half.
 parts.append(roofshape(outer,1.4,49.4,side))
 parts.append(roofshape(outer+inner[::-1],8.1,44.5,side))
 for x in [-46,-34.5,-23,-11.5,0,11.5,23,34.5,46]:
  y=49*math.sqrt(1-(x/59)**2)
  rib=roofshape([(x-.9,0),(x+.9,0),(x+.9,y),(x-.9,y)],5.1,46.0,side)
  parts.append(rib ^ roofshape([(56*math.cos(a),46*math.sin(a)) for a in angles],10,44,side))
 crossout=[(45.0*math.cos(a),29.5*math.sin(a)) for a in angles]
 crossin=[(43.2*math.cos(a),27.7*math.sin(a)) for a in angles]
 parts.append(roofshape(crossout+crossin[::-1],4.9,46.2,side))
# One straight shared diameter beam; no ground floor/base slab.
parts.append(box(0,0,42.8,120,7.5,8.2))
# Four open curved ribbon supports: broad swept profiles, no invented footings.
# Sections in y/z: outer curve splayed and concave; true hidden sections unknown.
ts=np.linspace(0,1,41)
for sx in [-1,1]:
 for sy in [-1,1]:
  edge1=[];edge2=[]
  for t in ts:
   y=sy*(47*(1-t)**.78);z=47*t
   edge1.append((y-sy*(5+5*t),z));edge2.append((y+sy*(5+5*t),z))
  leg=poly(edge1+edge2[::-1],6.2)
  # local (u,v,w) = (y,z,x), slight x splay toward feet.
  leg=leg.transform([[0,-sx*.14,1,sx*61-3.1],[1,0,0,0],[0,1,0,0]])
  parts.append(leg)
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
m=m.set_tolerance(.0001).simplify(.001);me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('gray_wide_pavilion_frame','#A3AAA9'),('gray_blue_roof_panel_material_unconfirmed','#668EAA'),('silver_gray_roof_ribs_approximate_grid','#B9C2C2')]
colors=np.zeros(len(f),dtype=int)
rho=(c[:,0]/53.5)**2+(abs(c[:,1])/43.5)**2
roofz=49.4+.64*abs(c[:,1])
colors[(rho<.998)&(abs(c[:,1])>3.8)&(c[:,2]>44+.64*abs(c[:,1]))]=2
colors[(rho<.998)&(abs(c[:,1])>3.8)&(c[:,2]>roofz-.02)&(c[:,2]<roofz+1.42)]=1
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-features.json').write_text(json.dumps({'estimated_not_surveyed':True,'half_oval_roof_leaves':2,'shared_straight_diameter_beam':1,'broad_curved_legs':4,'open_undercroft':True,'roof_panel_thickness_mm':1.4,'rim_section_height_mm':8.1,'parallel_rib_width_mm':1.8,'rib_count_per_leaf_simplified_not_measured':9,'curved_crossrib_per_leaf_simplified':1,'shared_beam_height_mm':8.2,'legs_section_thickness_mm':6.2,'omitted':'seats, site, lettering, lamps, chains, concealed footings and joints','glass_material_unconfirmed':True,'curvature_slope_and_grid_approximate':True},indent=2)+'\n')
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
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
