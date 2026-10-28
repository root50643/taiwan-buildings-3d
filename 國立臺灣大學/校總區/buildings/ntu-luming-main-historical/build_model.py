#!/usr/bin/env python3
"""Original Lu-Ming Hall historical exterior approximation; all dimensions nominal estimates."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Off-white plaster','#DEDCD3','Historical front/side photographs; not calibrated'),('relief','Cream relief panels','#C8C09B','Historical square pyramidal cladding'),('roof','Grey roof','#91938B','Elevated photograph confirms shallow roof'),('glass','Opaque dark glazing','#35433E','Photographs; opaque manufacturing proxy'),('frame','Pale frames','#B7B8AD','Photographed frames'),('red','Red entrance columns','#A7372C','Photographed front porch'),('base','Display support','#AFB2A7','Authored support, not terrain'),('canopy','Dark side canopy','#655F51','Photographed post-2005 canopy')]]
SCALE=4.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.5]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Historical photograph feature; dimensions estimated'):add(name,box(a,b),mat,evidence)
def pyramid(name,x,y,z,w,h,side=False):
 # Square-based shallow relief, fully backed by enclosing wall; no loose ornaments.
 verts=[[x,y+.03,z],[x+w,y+.03,z],[x+w,y+.03,z+h],[x,y+.03,z+h],[x+w/2,y-.20,z+h/2]]
 if side: verts=[[v[1],v[0],v[2]] for v in verts]
 fs=[[0,2,1],[0,3,2],[0,1,4],[1,2,4],[2,3,4],[3,0,4]]
 if side:fs=[f[::-1] for f in fs]
 add(name,mf.Manifold(mf.Mesh(np.array(verts,np.float32),np.array(fs,np.uint32))),1,'Photographed square-pyramidal facade relief; grid count simplified')
# x front-right, y towards rear. All metre-like source units nominal, not measurement.
W,L,H=24.,40.,14.
bx('Display plinth',[-7,-7,-.5],[31,44,0],6,'Authored rectangular support, not campus terrain')
bx('Main rectangular two-level tall hall',[0,0,0],[W,L,H],0,'Main rectangle: official 2001 plan proportion + historical photos; W24 L40 H14 estimated')
# Roof photograph shows shallow broad cap, not a pitched tile roof.
add('Low-pitch roof with central longitudinal ridge',mf.CrossSection([[[ -1.8,H-.15],[W+1.8,H-.15],[W+1.8,H+.25],[W/2,H+.72],[-1.8,H+.25]]]).extrude(L+3.6).rotate([90,0,0]).translate([0,L+1.8,0]),2,'Elevated historical photograph shows central longitudinal line and two shallow roof planes; pitch estimated')
# End corner uplift is schematic, not a measured roof curve.
for x in [-1.8,24.8]:
 for y in [-1.8,40.8]:
  bx(f'Raised eave corner{x}-{y}',[x,y,H+.2],[x+1,y+1,H+.57],0,'Photo corner eave uplift approximated; carving/curve not measured')
# Fine parapet relief simplified into rails/posts, characteristic front and observed long edge.
for i in range(10):
 x=-1.5+i*3.0
 bx(f'Front eave bracket{i}',[x-.12,-1.9,H-.6],[x+.12,.1,H+.25],0)
 bx(f'Front roof finial{i}',[x-.12,-1.88,H+.2],[x+.12,-1.6,H+1.05],0,'Front photo eave post; carving omitted and thickened')
bx('Front roof rail',[-1.6,-1.8,H+.48],[25.6,-1.63,H+.68],0)
for j,y in enumerate(np.linspace(.1,40,12)):
 bx(f'Left eave bracket{j}',[-1.9,y-.12,H-.6],[.1,y+.12,H+.25],0)
 bx(f'Left roof finial{j}',[-1.88,y-.12,H+.2],[-1.6,y+.12,H+1.05],0)
bx('Left roof rail',[-1.8,-1.7,H+.48],[-1.63,40.2,H+.68],0)
# Front's three large patterned panels; vertical white piers stay visible.
for panel in range(3):
 x0=1.0+panel*7.7
 for row in range(15):
  for col in range(9):
   if row<3 and x0+col*.74+.71>7 and x0+col*.74<17: continue
   pyramid(f'Front relief{panel}-{row}-{col}',x0+col*.74,-.015,2.0+row*.75,.71,.72)
# Observed long-side bays have two window bands alternating with relief cladding.
for bay in range(8):
 y0=1.0+bay*4.75
 for z in [4.0,9.2]:
  bx(f'Left glazing{bay}-{z}',[-.08,y0,z],[.02,y0+3.65,z+1.55],3)
  for k in range(5):bx(f'Left mullion{bay}-{z}-{k}',[-.12,y0+k*.9,z],[-.065,y0+k*.9+.055,z+1.55],4)
 for z0,rows in [(5.7,4),(11.0,3)]:
  for row in range(rows):
   for col in range(5):pyramid(f'Side relief{bay}-{z0}-{row}-{col}',y0+col*.73,-.015,z0+row*.70,.70,.67,True)
 bx(f'Ground side glazing{bay}',[-.06,y0,.35],[.02,y0+3.65,3.5],3)
# First-floor porch with red supports, entry balcony and simplified historic rail.
bx('Front entrance dark glazing',[7,-.08,.15],[17,.02,3.65],3)
for x in [7,12,17]:bx(f'Front doorway stile{x}',[x-.08,-.15,.1],[x+.08,.02,3.7],4)
bx('Front porch slab',[6.0,-4.2,3.7],[18.0,.3,4.13],0)
for x in [6.5,17.5]:
 add(f'Red entry column{x}',mf.Manifold.cylinder(3.65,.23,.23,20).translate([x,-3.7,.15]),5,'Historical photo red cylindrical porch columns; radius estimated')
 bx(f'Column capital{x}',[x-.38,-4.08,3.35],[x+.38,-3.32,3.78],0)
for x in np.linspace(6.15,17.85,9):bx(f'Balcony front post{x}',[x-.10,-4.12,4.08],[x+.10,-3.90,5.05],0)
for z in [4.4,4.8]:bx(f'Balcony front rail{z}',[6.1,-4.1,z],[17.9,-3.91,z+.12],0)
for x in [6.15,17.85]:
 for y in [-3.8,-2.6,-1.4,-.2]:bx(f'Balcony side post{x}-{y}',[x-.1,y-.1,4.08],[x+.1,y+.1,5.05],0)
 for z in [4.4,4.8]:bx(f'Balcony side rail{x}-{z}',[x-.1,-4,z],[x+.1,.1,z+.12],0)
for i in range(3):bx(f'Front approach step{i}',[5.5,-5.7+i*.5,0],[18.5,.1,(i+1)*.12],2)
# Lateral terrace/canopy documented by photos and official 2005 account.
bx('Left terrace solid substructure',[-4.1,7,0],[.15,35,3.6],0,'Plan side corridor and photo balcony; lower storey enclosed for print stability')
bx('Side ground glazing',[-4.18,7.4,.3],[-4.08,34.6,3.3],3)
bx('Left terrace slab',[-4.4,6.7,3.6],[.2,35.3,3.95],0)
for y in np.linspace(7,35,15):bx(f'Left terrace post{y}',[-4.35,y-.1,3.9],[-4.15,y+.1,4.9],0)
for z in [4.25,4.65]:bx(f'Left terrace rail{z}',[-4.33,6.9,z],[-4.14,35.1,z+.12],0)
bx('Side dark canopy',[-5.0,6.5,3.25],[-3.9,35.5,3.45],7,'Photo canopy outboard of balcony, no fabric/vegetation represented')
for y in [7,14,21,28,35]:bx(f'Side canopy post{y}',[-4.75,y-.10,0],[-4.55,y+.1,3.3],7)
# Terrace access is visible as an external stair near the front of observed long side.
for i in range(12):bx(f'Terrace access stair{i}',[-3.8,2+i*.40,0],[-1.8,7.2,(i+1)*.31],0,'Photo exterior stair rising away from front; count/thickness approximate')
# Far side and rear intentionally no invented window grid/ornament. Main footprint retained.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTU Lu-Ming Hall historical massing');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2001 official undimensioned planning footprint and historical and undated photographs; nominal dimensions estimated, rear and far-side details unresolved and neutral; not current/survey/trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
