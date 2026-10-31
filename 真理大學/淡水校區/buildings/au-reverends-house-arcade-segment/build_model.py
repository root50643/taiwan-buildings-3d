#!/usr/bin/env python3
"""AU Reverends house long arcade facade segment; dimensions nominal photo proportions, not measured."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('brick','Warm orange-red brick','#A6603E','Official university photograph, uncalibrated'),
 ('cream','Aged cream balustrade','#BEB59A','Visible light bottle balusters and rail'),
 ('shadow','Muted recess backing','#65544A','Author-created recess backing, no interior reconstruction'),
 ('trim','Darker brick cornice','#754C3C','Photo visible brick cornice shadows, approximate'),
 ('base','Authored base','#B7B8AC','Author-created support, not actual terrain'),
 ('cut','Authored cut back','#D1D0C5','Explicit shallow segment cutoff, not real rear facade')]]
SCALE=6.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible photo detail, nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
import math
# Main frontage local x0..22.5m nominal; front y0 and author cutoff y3.1, not actual depth.
# Broad bays normalized to equal nominal widths; perspective correction is inference, not survey.
# Bay order established from official university photo: broad, narrow, broad, narrow, broad, broad.
bays=[(2.6,3.8),(5.8,1.2),(9.0,3.8),(12.2,1.2),(15.4,3.8),(19.9,3.8)]
def opening(cx,w,z0,spring,rise):
 pts=[(cx-w/2,z0),(cx+w/2,z0),(cx+w/2,spring)]
 pts +=[(cx+(w/2)*math.cos(math.pi*i/24),spring+rise*math.sin(math.pi*i/24))for i in range(1,25)]
 return mf.CrossSection([pts]).extrude(1.0).rotate([90,0,0]).translate([0,.7,0])
# Hollow arches form an arcade, with authored blank backing rather than invented rooms.
bx('Authored display plinth',[-.6,-.7,-.6],[23.1,3.7,0],4,'Authored level base, not actual stairs or slope')
bx('Ground terrace',[0,0,0],[22.5,3.1,.22],1,'Porch floor exists; depth estimated and truncated')
bx('Upper corridor floor',[0,0,3.9],[22.5,3.1,4.18],0,'Visible interstorey masonry band; depth is cutoff')
bx('Top cropped deck',[0,0,8.55],[22.5,3.1,8.8],0,'Top edge termination; not reconstructed roof')
bx('Authored neutral backing',[0,3.02,0],[22.5,3.16,8.75],5,'Explicit author cutoff, no actual rear/interior wall openings asserted')
bx('Recess low contrast backing',[.4,2.95,.25],[22.1,3.1,8.48],2,'Author-created shadow backing prevents claim of detailed unseen interior')
wall=box([0,0,0],[22.5,.55,8.8])
for i,(cx,w) in enumerate(bays):
 upper_spring=6.10 if w>2 else 6.55
 upper_rise=w*.5 if w>2 else .6
 wall=wall-opening(cx,w,4.15,upper_spring,upper_rise)
 if w>2:wall=wall-opening(cx,w,.18,2.7,min(w*.18,.75))
 else:wall=wall-box([cx-w*.42,-.4,.2],[cx+w*.42,.8,3.1])
add('Brick arcade wall six upper bays',wall,0,'Official photograph broad/narrow/broad/narrow/broad/broad upper openings; lower broad segmental arches and two narrow rectangular apertures')
# Stone/brick horizontal edges: counts simplified, not claimed exact brick courses.
for z,h,depth in [(3.70,.13,.14),(3.86,.18,.18),(4.05,.13,.12),(8.48,.12,.12),(8.7,.16,.14)]:bx('Continuous masonry cornice'+str(z),[-.05,-depth,z],[22.55,.6,z+h],0,'Visible projecting cornices at floor and roof line, dimensions estimated')
# Corbel rhythm visually supported but exact count not known; generalized blocks are explicit approximation.
for x in [i*.45+.15 for i in range(50)]:
 bx('Roof corbel approximate rhythm'+str(x),[x,-.12,8.22],[x+.19,.08,8.62],3,'Approximate visible projecting brick dentil rhythm, count not surveyed')
 bx('Storey dentil approximate rhythm'+str(x),[x,-.11,3.56],[x+.19,.07,3.75],3,'Approximate brick dentil rhythm under middle cornice')
# Continuous square piers are the remaining wall; add photographed shallow bandings.
for x in [0,4.55,6.45,10.95,12.85,17.35,21.85]:
 for z in [1.8,2.12,5.6,5.88]:bx('Pier shallow belt',[x,-.10,z],[min(x+.65,22.5),.1,z+.12],0,'Visible pier belt details simplified')
def baluster(x,y,z):
 # Robust bottle profile, not exact historic carving, minimum diameter .14 nominal m (.84mm).
 for dz,h,r0,r1 in [(0,.1,.12,.12),(.1,.14,.10,.07),(.24,.26,.07,.14),(.50,.16,.14,.08),(.66,.14,.08,.08),(.8,.08,.12,.12)]:
  add('Bottle baluster',mf.Manifold.cylinder(h+.025,r0,r1,12).translate([x,y,z+dz]),1,'Cream bottle balustrade visible; thickened simplified turned profile, not surveyed')
for level in [0,1]:
 z=level*4.0+.3
 for i,(cx,w) in enumerate(bays):
  # Ground central broad entry bay is an open access, as visible in photograph.
  if level==0 and i==2:continue
  bx('Balustrade sill',[cx-w/2,-.08,z],[cx+w/2,.39,z+.15],1,'Cream/grey balustrade sill visible; plant-obscured bases simplified')
  bx('Balustrade handrail',[cx-w/2,-.09,z+.94],[cx+w/2,.4,z+1.10],1,'Continuous light rail across photographed balcony bays')
  n=max(2,round(w/.43))
  for j in range(n):baluster(cx-w/2+(j+.5)*w/n,.16,z+.12)
# Short supporting side boundary is an explicit cut, not an invented return facade.
bx('Left shallow segment end',[0,.3,0],[.2,3.1,8.7],5,'Author cutoff end behind visible facade')
bx('Right shallow segment end',[22.3,.3,0],[22.5,3.1,8.7],5,'Author cutoff end; side arcade not reconstructed')
# No contemporary roof additions, signage, interior furniture, trees, people or unsupported stairs.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='AU Reverends house six-bay arcade facade segment');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official university photo based six-bay long arcade facade segment. All dimensions estimated; shallow rear cutoff authored; full roof, rear, interior omitted; not trial printed.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
