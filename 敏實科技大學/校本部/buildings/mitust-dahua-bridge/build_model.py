#!/usr/bin/env python3
"""MITUST Dahua Bridge upper span; photo-normalized complete main form."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('red','Red arch steel','#B84A43','Daylight official image; night red lighting not used'),
('green','Green surface and panel surrogate','#387C71','Daylight approximate green, canopy transparency not simulated'),
('roof','Grey roof skin','#AAB8B9','Daylight opaque canopy zones; corrugation simplified'),
('ochre','Ochre support frames','#A88B45','Daylight yellow ochre canopy rim and support'),
('neutral','Neutral deck underside and rails','#727C7B','Nominal neutral closure and grey rail metal')]]
SCALE=1.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible main-form feature; photo-normalized not surveyed'):add(name,box(a,b),mat,evidence)
def cyl_y(radius,depth,center):return mf.Manifold.cylinder(depth,radius,radius,64,True).rotate([90,0,0]).translate(center)
# Complete upper span only. Nominal dimensions and representative repeated bays.
bx('Nominal bridge deck / neutral underside',[-25,-70,0],[25,70,2],4,'Deck visible; thickness and neutral underside nominal; valley and foundations excluded')
bx('Green walking surface',[-21,-70,1.9],[21,70,2.4],1,'Daylight green walking surface, approximate uncalibrated color')
# Main parabolic side arches: analytic curve is a silhouette approximation, not engineering profile.
y=np.linspace(-70,70,73); z=5+41*(1-(y/70)**2)
profile=list(zip(y,z))+list(zip(y[::-1],(z-3.4)[::-1]))
for side in [-1,1]:
 a=mf.CrossSection([profile[::-1]]).extrude(3.2).rotate([90,0,90]).translate([side*23.4-1.6,0,0])
 add('Red main side arch '+str(side),a,0,'Observed paired longitudinal red arches; parabola and section nominal')
bx('Observed red crown cross tie',[-24,-1.4,42.8],[24,1.4,45.2],0,'One visible transverse crown member; connection details simplified')
# Barrel canopy at open side-post level, with alternating opaque/translucent-looking zones.
# Green panels rendered opaque surrogate: no fabricated optical measurements.
def shell(r0,r1,y0,y1):
 t=np.linspace(0,math.pi,49)
 poly=[(r1*math.cos(a),17+r1*math.sin(a)) for a in t]+[(r0*math.cos(a),17+r0*math.sin(a)) for a in t[::-1]]
 return mf.CrossSection([poly]).extrude(y1-y0).rotate([90,0,0]).translate([0,y1,0])
bounds=[-70,-48,-30,-10,10,30,48,70]
for i,(a,b) in enumerate(zip(bounds,bounds[1:])):
 add('Canopy representative panel zone '+str(i),shell(20.6,21.2,a,b),2 if i%2==0 else 1,'Alternating opaque grey and greenish translucent zones observed; spacing representative, green opaque surrogate')
for j,y0 in enumerate(bounds):
 add('Ochre barrel rib '+str(j),shell(20.25,21.35,y0-.5,y0+.5),3,'Visible curved support ribs, representative spacing')
 for side in [-1,1]:
  bx('Canopy post '+str((j,side)),[side*20.6-.65,y0-.65,2],[side*20.6+.65,y0+.65,17.7],3)
# Longitudinal purlins bonded to underside of roof.
for ang in [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi]:
 x=20.5*math.cos(ang);z=17+20.5*math.sin(ang)
 bx('Longitudinal canopy purlin '+str(ang),[x-.4,-70,z-.4],[x+.4,70,z+.4],3)
for side in [-1,1]:
 x=side*19.4
 for j,y0 in enumerate(np.linspace(-69,69,15)):
  bx('Representative railing post '+str((side,j)),[x-.65,y0-.75,2],[x+.65,y0+.75,10.3],3,'Representative post spacing; bolt holes omitted, not an exact bay count')
 for z in [4,10]:bx('Continuous side rail '+str((side,z)),[x-.45,-70,z-.45],[x+.45,70,z+.45],4)
 # Open railing rather than opaque walls; glazing omitted explicitly.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.001).simplify(.001)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v=np.round(v,4) # 0.0001mm export grid; STL reload verified independently
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='MITUST Dahua Bridge upper span');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete upper bridge span only; foundations and valley excluded. Nominal underside and deck thickness. Representative canopy and railing spacing; glazing, corrugation, bolts and signage omitted. Not an engineering or surveyed reconstruction.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
