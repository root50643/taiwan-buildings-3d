#!/usr/bin/env python3
"""NTHU Success Lake octagonal pavilion simplified exterior; dimensions nominal photo proportions, not measured."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('roof','Weathered green roof','#315C46','Official university current photograph, uncalibrated'),
('white','White beams and rails','#DFE0D7','Official photograph visible white frame and balustrade'),
('column','Dark brown columns','#443A30','Official photograph shaded dark columns, material uncertain'),
('ridge','Green roof ridges','#52715A','Simplified radial ridges seen in official photograph'),
('base','Grey platform','#898D88','Visible raised grey platform; exact footprint normalized'),
('cut','Authored support underside','#B4B5AD','Author-defined support, not actual foundations')]]
SCALE=18.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible photo detail, nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
import math
angles=[math.radians(22.5+45*i) for i in range(8)]
def pts(rad):return [(rad*math.cos(a),rad*math.sin(a)) for a in angles]
def beam(name,a,b,width,height,mat,evidence):
 a=np.array(a);b=np.array(b);d=b-a;ln=float(np.linalg.norm(d[:2]));ang=math.degrees(math.atan2(d[1],d[0]))
 add(name,mf.Manifold.cube([ln+width,width,height]).translate([-width/2,-width/2,-height/2]).rotate([0,0,ang]).translate(a.tolist()),mat,evidence)
poly('Authored octagonal underside',pts(3.32),-.6,-.32,5,'Author display connection, not surveyed foundation')
poly('Visible grey raised platform',pts(3.25),-.35,.12,4,'Raised grey platform visible; regular octagonal outline inferred from pavilion name and structure')
poly('Platform top',pts(3.18),.10,.20,4,'Approximate platform top, terrain omitted')
for i,(x,y) in enumerate(pts(2.88)):
 bx('Dark column '+str(i),[x-.095,y-.095,.14],[x+.095,y+.095,3.30],2,'Visible dark slender columns; eightfold rear repetition inferred, dimensions approximate')
for z,w,h in [(3.08,.22,.24),(2.65,.18,.18)]:
 ring=mf.CrossSection([pts(2.88+w*.5)])-mf.CrossSection([pts(2.88-w*.5)])
 add('White perimeter beam ring',ring.extrude(h).translate([0,0,z-h/2]),1,'White horizontal beams at two heights visible; hidden continuity inferred')
# Eight-sided curved shell with short solid apex: regular rotational symmetry is an explicit inference.
rings=[.06,.20,.45,.75,1.1,1.5,1.95,2.4,2.8,3.1,3.35,3.55,3.72]
def roofz(rad):
 t=rad/3.72
 return 3.30+2.60*(1-t)**2+.20*t**12
v=[]
for side in [0,1]:
 for rad in rings:
  for a in angles:v.append([rad*math.cos(a),rad*math.sin(a),roofz(rad)-side*.18])
f=[];n=len(rings);off=n*8
for layer in [0,1]:
 for j in range(n-1):
  for i in range(8):
   a=layer*off+j*8+i;b=layer*off+j*8+(i+1)%8;c=layer*off+(j+1)*8+(i+1)%8;d=layer*off+(j+1)*8+i
   f.extend([[a,c,b],[a,d,c]] if layer==0 else [[a,b,c],[a,c,d]])
for j in [0,n-1]:
 for i in range(8):
  a=j*8+i;b=j*8+(i+1)%8;f.extend([[a,b,b+off],[a,b+off,a+off]] if j==0 else [[a,b+off,b],[a,a+off,b+off]])
mesh=trimesh.Trimesh(np.array(v),np.array(f),process=True)
add('Green eight-sector curved roof shell',mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32))),0,'Single pointed green roof with gently upturned eaves; hidden sectors and curvature regularized, not measured')
add('Apex cap',mf.Manifold.cylinder(.22,.13,.07,16).translate([0,0,5.61]),3,'Small apex finish simplified; no invented finial ornament')
# Radial tile ridges: coarse model interpretation, not exact tile count.
def rod(a,b,radius):
 a=np.array(a);b=np.array(b);d=b-a;l=np.linalg.norm(d);yaw=math.degrees(math.atan2(d[1],d[0]));tilt=math.degrees(math.acos(d[2]/l))
 return mf.Manifold.cylinder(l+.035,radius,radius,8).rotate([0,tilt,yaw]).translate(a.tolist())
for i in range(8):
 # Corner ridges, held to polygon shell. Other tile corrugation omitted.
 a=angles[i]
 for j in range(len(rings)-1):
  r0,r1=rings[j:j+2]
  p0=[r0*math.cos(a),r0*math.sin(a),roofz(r0)-.015]
  p1=[r1*math.cos(a),r1*math.sin(a),roofz(r1)-.015]
  add('Rounded corner ridge',rod(p0,p1,.045),3,'Eight corner ridges regularized; exact tile spacing omitted')
# Join canopy to column tops with white eave bearing blocks; source shows projecting white supports.
for i,(x,y) in enumerate(pts(2.88)):
 bx('White canopy bearing',[x-.16,y-.16,3.05],[x+.16,y+.16,3.30],1,'White column/eave connections simplified for continuous support; not carpentry detail')
# Only three lake-facing sides represented. Unseen landward barriers/entry not invented.
P=pts(3.04)
for i in [4,5,6]:
 a=np.array(P[i]);b=np.array(P[(i+1)%8]);
 for z in [.42,.83]:beam('Lake-side white rail',(*a,z),(*b,z),.105,.105,1,'Visible lake-facing horizontal rails; only supported front sectors included')
 for t in [0,.5,1]:
  x,y=(1-t)*a+t*b;bx('White rail post',[x-.065,y-.065,.18],[x+.065,y+.065,1.03 if t in [0,1] else .85],1,'Simplified white rail upright, count and section approximate')
# No stairs/roof inscription/interior furnishing: insufficient verified detail.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.01).simplify(.01)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v=np.round(v,2) # 0.01mm export grid prevents float32 STL sliver collapse
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTHU Success Lake octagonal pavilion');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official university photograph-informed simplified open octagonal pavilion. Hidden roof sectors and columns symmetric inference; only lake-side rail sectors modeled. All dimensions approximate, not surveyed or trial printed.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
