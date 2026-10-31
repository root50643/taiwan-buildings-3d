#!/usr/bin/env python3
"""NKNU demolished historical main gate, official photo constrained approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('pier','Light historic pier','#D8D2C2','Faded official historical photographs; approximate non-calibrated neutral finish'),
('metal','Light gate framing','#D4CDB9','Visible light metal framing; nominal uncalibrated color'),
('plinth','Dark pier plinth','#675356','Visible dark plinth in faded historical photos; nominal color'),
('base','Authored base','#B1A796','Authored display base, not historical road surface')]]
SCALE=12.0
P={'pier_height':6.0,'pier_width':1.9,'pier_depth':.55,'pier_left_edges':[-3.0,3.0],'gate_spans':[[-6.8,-3.0],[-1.1,3.0],[4.9,6.5]],'gate_height':2.65,'gate_low_chevron_height':1.35,'screen_bar_count':9,'nominal_scale_mm_per_unit':12}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.22]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportional nominal dimensions, not measured'):add(name,box(a,b),mat,evidence)
def prism_xz(points,y,depth):
 # An XY polygon extruded +Z then rotated maps input y to world z, extrusion to -y.
 return mf.CrossSection([points]).extrude(depth).rotate([90,0,0]).translate([0,y+depth,0])
def bar(name,a,b,width=.06,depth=.09,mat=1):
 a=np.array(a);b=np.array(b);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)*width/2
 add(name,prism_xz([list(a-n),list(b-n),list(b+n),list(a+n)],-.12,depth),mat,'Visible major gate framing; simplified bar widths and layout, not exact decorative lattice')
bx('Authored continuous display strip',[-7.1,-.78,-.22],[6.8,.78,0],3,'Authored connectivity base; not photographed road or full boundary')
for i,x in enumerate(P['pier_left_edges']):
 bx('Dark pier footing '+str(i+1),[x-.03,-.30,0],[x+1.93,.30,.35],2)
 # Narrow screen framed by a broad solid panel and slender right edge.
 bx('Main solid gate pier '+str(i+1),[x,-.275,.28],[x+1.25,.275,6.0],0,'Visible broad slab; no invented inscription or relief geometry; equal nominal height avoids treating perspective as survey')
 bx('Screen outer stile '+str(i+1),[x+1.76,-.275,.28],[x+1.90,.275,6.0])
 bx('Screen upper lintel '+str(i+1),[x+1.23,-.275,5.55],[x+1.90,.275,6.0])
 bx('Screen lower sill '+str(i+1),[x+1.23,-.275,.28],[x+1.90,.275,.52])
 bx('Screen thin centre vertical '+str(i+1),[x+1.49,-.12,.5],[x+1.54,-.03,5.58],1,'Simplified visible narrow vertical grille, no exact irregular pattern claim')
 for k in range(9):
  z=.72+k*.55
  bx('Screen horizontal '+str(i+1)+'-'+str(k+1),[x+1.23,-.12,z],[x+1.79,-.03,z+.045],1,'Representative reduced grille subdivisions; count nominal')
for i,(a,b) in enumerate(P['gate_spans']):
 # Three entrance spans in the wide official historical photograph; right one narrow.
 bar('Gate top rail '+str(i+1),(a,2.65),(b,2.65),.085,.11)
 bar('Gate bottom rail '+str(i+1),(a,.16),(b,.16),.07,.11)
 bar('Gate left stile '+str(i+1),(a,.0),(a,2.65),.09,.11)
 bar('Gate right stile '+str(i+1),(b,.0),(b,2.65),.09,.11)
 if i<2:
  mid=(a+b)/2
  bar('Chevron left '+str(i+1),(a,2.18),(mid,1.35),.27,.12)
  bar('Chevron right '+str(i+1),(mid,1.35),(b,2.18),.27,.12)
  bar('Central meeting stile '+str(i+1),(mid,0),(mid,2.65),.065,.10)
 else:
  bar('Narrow side gate diagonal',(a,1.35),(b,2.18),.24,.12)
 for j in range(1,9 if i<2 else 4):
  x=a+(b-a)*j/(9 if i<2 else 4)
  bar('Reduced vertical grille '+str(i+1)+'-'+str(j),(x,0),(x,2.65),.045,.09)
 # Preserve only a sparse visible diagonal language, not a speculative copy of irregular decoration.
 for j in range(4 if i<2 else 2):
  x=a+(b-a)*j/(4 if i<2 else 2);xx=a+(b-a)*(j+1)/(4 if i<2 else 2)
  bar('Representative lower grille diagonal '+str(i+1)+'-'+str(j),(x,.42),(xx,1.05),.04,.09)
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.01).simplify(.01)
m=s.to_mesh64();print('raw status',s.status(), 'merge',len(m.merge_from_vert));v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Collapse negligible coplanar material seams before export, preserving the true surface.
# Assign palette deterministically by nearest original triangle centroid after geometric cleanup.

old_centres=v[f].mean(axis=1); old_mi=mi.copy()
s=s.as_original().set_tolerance(.001).simplify(.001)
clean=s.to_mesh64();v=np.asarray(clean.vert_properties)[:,:3]*SCALE;f=np.asarray(clean.tri_verts)
centres=v[f].mean(axis=1); near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
q=mf.Manifold(mf.Mesh(np.round(v,2).astype(np.float32),np.asarray(f,dtype=np.uint32)))
print('grid cleanup',q.status())
qc=q.to_mesh(); v=np.asarray(qc.vert_properties)[:,:3];f=np.asarray(qc.tri_verts)
centres=v[f].mean(axis=1);near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-10;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NKNU historical gate main assembly');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical gate main assembly demolished in 1982; photograph-proportional nominal dimensions, no surrounding walls/buildings or exact decorative replication.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
