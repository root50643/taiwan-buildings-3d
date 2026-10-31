#!/usr/bin/env python3
"""HFU Yunshan pavilion from official 2024 unveiling photographs, photo-proportional approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('timber','Dark brown structural frame','#47372D','Official 2024 images, nominal uncalibrated brown'),
('roof','Pale nominal roof covering','#B7AB88','Observed light fibrous roof surface simplified solid; no invented tile detail'),
('soffit','White underside','#E6E2D6','Visible pale roof underside'),
('sign','Blank orange wood plaque','#AF653F','Observed orange plaque, calligraphy omitted'),
('base','Nominal support slab','#C2BEB1','Nominal support across occluded footprint, not precise terrain')]]
SCALE=30.0
P={'width':4.5,'depth':3.6,'height':3.45,'post_radius':.09,'nominal_scale_mm_per_unit':30,'roof':'Shallow hipped solid nominal approximation from oblique and distant photos; roof covering texture not reproduced','scope':'Complete principal standalone pavilion, no statue/table/stones/fence'}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.12]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible principal framing with nominal photo-proportional dimensions'):add(name,box(a,b),mat,evidence)
bx('Nominal supporting slab',[-1.7,-1.45,-.12],[1.7,1.45,0],4,'Authored base across occluded footings, not exact ground plan')
for x in [-1.3,1.3]:
 for y in [-1.1,1.1]:add('Round column '+str((x,y)),mf.Manifold.cylinder(3.02,.09,.09,32).translate([x,y,0]),0,'Four circular columns visible across source photographs')
for y in [-1.1,1.1]:bx('Long primary beam '+str(y),[-1.48,y-.07,2.84],[1.48,y+.07,3.02])
for x in [-1.3,1.3]:bx('Side primary beam '+str(x),[x-.07,-1.23,2.84],[x+.07,1.23,3.02])
# Continuous nominal roof body over pale soffit. Approximate hipped envelope, not measured roof framing.
bx('Plain pale soffit',[-2.25,-1.8,2.99],[2.25,1.8,3.04],2,'Visible pale underside simplified as a continuous slab')
v=[[-2.25,-1.8,3.03],[2.25,-1.8,3.03],[2.25,1.8,3.03],[-2.25,1.8,3.03],[-.55,0,3.45],[.55,0,3.45]]
h=trimesh.Trimesh(np.array(v),np.array([[0,3,2],[0,2,1],[0,1,5],[0,5,4],[1,2,5],[2,3,4],[2,4,5],[3,0,4]]),process=False);add('Shallow four-slope roof',mf.Manifold(mf.Mesh(np.asarray(h.vertices,dtype=np.float32),np.asarray(h.faces,dtype=np.uint32))),1,'Nominal solid hipped envelope from visible outer silhouette; no fine thatch/tile reconstruction')
for y in [-1.77,1.77]:bx('Roof perimeter dark edge '+str(y),[-2.25,y-.03,2.97],[2.25,y+.03,3.06])
for x in [-2.22,2.22]:bx('Roof side dark edge '+str(x),[x-.03,-1.8,2.97],[x+.03,1.8,3.06])
# Only the front-side eave braces visible in the unveiling photographs.
for side in [-1,1]:
 a=np.array([side*1.3,-1.1,2.95]);b=np.array([side*2.20,-1.75,3.00]);d=b-a;ln=float(np.linalg.norm(d))
 beam=mf.Manifold.cube([.10,.10,ln]).translate([-.05,-.05,0]).rotate([0,math.degrees(math.acos(d[2]/ln)),0]).rotate([0,0,math.degrees(math.atan2(d[1],d[0]))]).translate(a.tolist())
 add('Visible front eave diagonal '+str(side),beam,0,'Visible front underside diagonal simplified; no unseen rear roof truss inferred')
bx('Blank orange front plaque',[-.7,-1.205,2.56],[.7,-1.10,3.00],3,'Visible front plaque; no reproduced lettering or invented reverse plaque')
for o,i in zip(ops,items):
 assert i.status()==mf.Error.NoError,(o,i.status())
s=items[0]
for o,i in zip(ops[1:],items[1:]):
 s=s+i
 assert s.status()==mf.Error.NoError,(o,s.status())
s=s.set_tolerance(.001).simplify(.001)
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='HFU Yunshan pavilion');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete principal pavilion exterior; statue, ritual table, stones, fence and inscription omitted. Nominal photo proportions and support slab, not surveyed reconstruction.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
