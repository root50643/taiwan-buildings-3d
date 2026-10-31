#!/usr/bin/env python3
"""THU Mingxian courtyard facade segment, not the whole hall. Nominal photo proportions."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('brick','Red brown brick','#985B48','Municipal PDF courtyard facade, uncalibrated'),
('frame','Weathered concrete','#AAA595','Visible pier strips and eaves, uncalibrated'),
('wood','Dark window lattice','#35382C','Photo dark rectangular grille, fine grid simplified'),
('glass','Recessed dark glazing','#555A4E','Window shadow abstracted, not measured glazing'),
('base','Grey platform','#A8A695','Visible base; simplified extent'),
('roof','Grey brown tile','#797466','Visible front slope, coarse ribs not actual tile count'),
('cut','Authored cut backing','#C0BDB0','Artificial planar rear cut, not actual rear elevation')]]
SCALE=5.5
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed visible feature; photo proportions, not survey'):add(name,box(a,b),mat,evidence)
def section(name,yz,x0,x1,mat,evidence):
 s=mf.CrossSection([yz]).extrude(x1-x0).rotate([90,0,90]).translate([x0,0,0]);add(name,s,mat,evidence)
bx('Simplified platform',[-12.6,-1.4,-.6],[12.6,4.7,-.15],4,'Observed platform edge, depth is authored segment support')
bx('Low wall plinth',[-11.45,-.55,-.2],[11.45,.12,.25],1)
bx('Cut backing',[-8.2,4.3,-.18],[8.2,4.55,6.6],6,'Artificial planar closure; no actual rear wall implied')
# Complete observed five-bay long elevation, two brick/high-window bays on either side.
for k in range(5):
 a=-11.25+k*4.5;b=a+4.5
 if k!=2:bx('Brick wall bay '+str(k+1),[a,-.4,.15],[b,.10,2.50],0)
 else:bx('Central grille shadow',[a,-.25,.2],[b,.12,3.64],3)
 if k!=2:bx('High window shadow bay '+str(k+1),[a,-.25,2.48],[b,.10,3.64],3)
 z0=.24 if k==2 else 2.52
 # Repeated grid is visual abstraction; no measured mullion count claimed.
 for j in range(9):
  x=a+j*4.5/8;bx('Window vertical bar',[x-.045,-.43,z0],[x+.045,-.20,3.67],2)
 for j in range(4 if k!=2 else 9):
  z=z0+(3.62-z0)*j/(3 if k!=2 else 8);bx('Window horizontal bar',[a,-.43,z-.045],[b,-.20,z+.045],2)
for k in range(6):
 x=-11.25+k*4.5;bx('Concrete pier '+str(k+1),[x-.16,-.5,.15],[x+.16,.18,3.84],1)
bx('Continuous eaves beam',[-11.6,-.5,3.59],[11.6,.25,3.86],2)
# Front roof slope only. Ends and far side are cut planes rather than invented gables/back roof.
roofpoints=[]
for dz in [0,.24]:
 for x,y,z in [(-12.4,-1.05,3.78),(12.4,-1.05,3.78),(8.3,4.55,6.64),(-8.3,4.55,6.64)]:roofpoints.append([x,y,z+dz])
add('Trapezoidal front tile roof slope',mf.Manifold.hull_points(roofpoints),5,'Visible front pitch narrows toward shorter ridge; side and opposite roof slopes omitted, section boundaries authored')
# Visible ridge represented at section termination.
bx('Roof ridge band',[-8.32,4.35,6.70],[8.32,4.60,6.94],5,'Visible ridge, coarse rectangular section not surveyed')
bx('Eaves fascia',[-12.45,-1.13,3.72],[12.45,-.93,4.04],1)
# Long narrow raised tile-course ribs follow roof pitch, coarse and explicitly not real count.
for x in np.linspace(-12.15,12.15,66):
 ymax=min(4.40,-1.05+(12.4-abs(x)-.05)*5.60/4.10)
 zmax=4.02+(ymax+1.05)*2.86/5.60
 section('Coarse roof tile rib',[[-1.05,4.01],[ymax,zmax-.01],[ymax,zmax+.07],[-1.05,4.09]],float(x-.035),float(x+.035),5,'Repeated coarse roof rib for legibility; actual tile count and profile unknown')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='THU Mingxian courtyard facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed courtyard long facade and front roof slope ONLY; rear is an artificial cut face. Five bays and central grille observed, dimensions/grid/tiles simplified; no surveyed scale.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
