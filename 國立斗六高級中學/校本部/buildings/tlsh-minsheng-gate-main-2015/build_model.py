#!/usr/bin/env python3
"""TLSH main gate, bounded photo state stamped 2015-08-15; source-constrained approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('stone','Light stone piers','#B7BAB0','Visible pale grey stone in photo stamped 2015-08-15; uncalibrated'),
('metal','Metal gate','#B1B5B4','Visible dull silver metal gate, approximate finish'),
('plaque','Blank gold plaque','#BEA85A','Visible gold sign plate; text deliberately not reproduced'),
('base','Authored display strip','#9E9C94','Authored connectivity strip, not surveyed pavement')]]
SCALE=18.0
P={'left_pier_height':3.5,'right_pier_height':2.8,'pier_width':.72,'pier_depth':.60,'clear_gate_span':6.5,'gate_height':2.55,'representative_vertical_bars':29,'nominal_scale_mm_per_unit':18}
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
bx('Authored connectivity display strip',[-4.25,-.64,-.22],[4.25,.64,0],3,'Authored display support; not the real pavement')
for name,x,h in [('Left main pier',-3.97,3.5),('Right receiving pier',3.25,2.8)]:
 bx(name,[x,-.3,0],[x+.72,.3,h],0,'Photograph-constrained proportions; unsurveyed nominal depths and height ratio')
 bx(name+' square top cap',[x-.04,-.34,h-.22],[x+.76,.34,h+.04],0,'Visible simple rectangular cap, no older pier-top badge')
# Neutral stone behind blank plate; avoid invented or misspelled calligraphy.
bx('Blank gold school name plate',[-3.90,-.326,.38],[-3.32,-.295,3.23],2,'Photo has gold vertical plaque; school-name text is omitted, not replaced by invented lettering')
bx('Closed gate solid bottom apron',[-3.27,-.11,.10],[3.27,.04,.65],1,'Visible opaque lower metal sheet; closed static representation')
bx('Closed gate top rail',[-3.27,-.11,2.45],[3.27,.04,2.55],1)
bx('Gate left edge stile',[-3.27,-.11,.10],[-3.17,.04,2.55],1)
bx('Gate right edge stile',[3.17,-.11,.10],[3.27,.04,2.55],1)
for k in range(29):
 x=-3.12+k*6.24/28
 bx('Representative vertical gate bar '+str(k+1),[x-.025,-.095,.62],[x+.025,.025,2.47],1,'Regular visible metal bars; representative count and print-safe thickness, not measured exact pattern')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='TLSH Minsheng main gate 2015 photo state');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Two piers and closed main gate only; photo stamped 2015-08-15, not verified present condition. No adjacent name wall, LED, mechanisms, exact inscription or surveyed dimensions.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
