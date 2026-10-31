#!/usr/bin/env python3
"""NCHU rebuilt small auditorium main hall, based on 2015 official aerial and rebuilt front photograph; nominal dimensions."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('wall','Pale gray rebuilt facade','#AFB5AF','Official 2015 aerial and alumni issue16p59 photo; approximate'),
 ('canopy','Terracotta porch roof','#A75F43','Official aerial and front photo'),
 ('opening','Dark recess','#293636','Opaque simplified windows/doors; not transparent glass'),
 ('roof','Blue gray main roof','#414F5C','Official 2015 aerial; uncalibrated'),
 ('trim','Light gray trim','#C8CBC1','Observed arch imposts and gable outline'),
 ('base','Authored support','#A3A8A0','Display base not measured actual site'),
 ('unknown','Undocumented side/rear surface','#D5D7D0','Plain closure for unobserved wall details; no claim blank in reality')]]
SCALE=5.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photograph-proportioned visible detail; dimensions estimated'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
import math
# Main auditorium only. The adjoining courtyard, corner towers and wings are excluded.
# x width18, y hall depth32 nominal units; no real-world scale is claimed.
def xzprism(pts,y0,y1):
 return mf.CrossSection([pts]).extrude(y1-y0).rotate([90,0,0]).translate([0,y1,0])
def solid(name,pts,y0,y1,mat,evidence):add(name,xzprism(pts,y0,y1),mat,evidence)
def roundarch(cx,z,w,spring,depth,y0):
 rr=w/2;pts=[(cx-rr,z),(cx+rr,z),(cx+rr,spring)]
 pts +=[(cx+rr*math.cos(math.pi*i/24),spring+rr*math.sin(math.pi*i/24))for i in range(1,25)]
 return xzprism(pts,y0,y0+depth)
bx('Authored display base',[-1,-1.7,-.6],[19,35.6,0],5,'Display base, not surveyed grounds')
bx('Auditorium main block',[0,2.7,0],[18,34.8,8.3],0,'Roof footprint visible in2015aerial; walls mostly hidden; dimensions photo-proportioned')
solid('Main roof supporting volume',[(0,8.25),(18,8.25),(9,14.1)],2.7,34.8,0,'Authored solid roof volume under visible exterior slopes; no interior claim')
solid('Front triangular gable',[(0,8),(18,8),(9,13.7)],2.7,3.4,0,'Triangular front gable fully visible in official rebuilt photo')
solid('Plain rear gable closure',[(0,8),(18,8),(9,13.7)],34.1,34.8,6,'Rear closure follows roof silhouette; actual wall apertures unobserved')
# Side and rear planes explicitly neutral, no invented windows.
bx('Unknown left wall details',[-.04,3.3,0],[.05,34.8,8.3],6,'Vegetation hides wall; plain authored placeholder, not assertion of blank wall')
bx('Unknown right wall details',[17.95,3.3,0],[18.04,34.8,8.3],6,'Adjacent courtyard connection openings unmodeled')
bx('Unknown rear wall',[0,34.72,0],[18,34.83,8.3],6,'Unobserved back wall openings omitted')
# Dark continuous gabled roof visible from both official aerial images.
solid('Main gabled roof',[(-.45,8.2),(9,14.0),(18.45,8.2),(18.45,8.55),(9,14.35),(-.45,8.55)],2.45,35.0,3,'Two long roof slopes and ridge visible; no tile-by-tile detail')
# Front roof fascia / double gable trim.
solid('Front gable sloping fascia',[(-.45,8.12),(9,13.92),(18.45,8.12),(18.45,8.38),(9,14.18),(-.45,8.38)],2.28,2.5,4,'Light sloping border visible around front gable')
# Five semicircular portico arches; real voids into shallow porch, not punched through hall.
wall=box([0,0,0],[18,.8,6.5])
centres=[2.0,5.5,9.0,12.5,16.0]
for cx in centres:wall=wall-roundarch(cx,-.05,2.55,4.85,1.4,-.2)
add('Five arch portico facade',wall,0,'Exactly five semicircular arches in official rebuilt front photograph')
# Small visible square impost blocks and plinths on six intervening piers.
for x in [.35,3.75,7.25,10.75,14.25,17.65]:
 bx('Arch pier foot',[x-.36,-.1,0],[x+.36,.92,.35],4,'Simplified low square column bases visible in source')
 bx('Arch spring impost',[x-.38,-.12,4.7],[x+.38,.95,4.98],4,'Light horizontal impost at round arch spring')
# Front portico lean-to terracotta roof slopes down toward viewer.
# Roof slab is wedge extruded across width via custom mesh.
v=[(x,y,z)for x in[-.15,18.15]for y,z in[(-.35,6.65),(-.35,6.9),(2.9,8.35),(2.9,8.1)]]
f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
add('Sloping terracotta porch roof',mf.Manifold(mf.Mesh(np.array(v,dtype=np.float32),np.array(f,dtype=np.uint32))),1,'Terracotta lean-to roof below gable seen in both official views; slope estimated')
# Recessed dark door/window abstractions: positions behind five visible portico bays, detailed glazing omitted.
for cx in centres:
 add('Recessed opening abstraction',roundarch(cx,.25,1.4,3.7,.18,2.57),2,'Dark recessed front openings visible; detailed door divisions omitted, equal spacing is author simplification')
# Three narrow rectangular attic vents with small shared top/bottom caps.
for cx in [8.0,9.0,10.0]:
 bx('Attic dark vent',[cx-.23,2.53,10.1],[cx+.23,2.8,11.65],2,'Exactly3vertical attic vents visible in rebuilt front photo')
 bx('Attic vent side trim',[cx-.34,2.49,10.0],[cx-.24,2.8,11.75],4,'Simplified narrow light vent frame')
 bx('Attic vent side trim',[cx+.24,2.49,10.0],[cx+.34,2.8,11.75],4,'Simplified narrow light vent frame')
bx('Attic vent common lintel',[7.55,2.43,11.65],[10.45,2.8,11.85],4,'Horizontal attic lintel visible')
bx('Attic vent common sill',[7.55,2.43,9.98],[10.45,2.8,10.15],4,'Horizontal attic sill visible')
# Three front steps visible; tree-obscured side steps omitted.
for j in range(3):bx('Front entry step'+str(j),[0,-1.5+j*.4,0],[18,.2,.12*(j+1)],0,'Broad front steps, count/size simplified from photograph')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v, inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NCHU rebuilt small auditorium main hall');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2015 source-state main auditorium only; adjoining courtyard wings omitted. Roof/front observed; side/rear details omitted as neutral placeholders; all dimensions estimated, no interior or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
