#!/usr/bin/env python3
"""NHU green-energy bus shelter from official VR node11 face2, photo-proportional approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('frame','Dark metal frame','#3B403B','Official VR visible dark framing; uncalibrated approximate color'),
('roof','Grey thin roof','#777D77','Official VR thin grey fascia; upper surface nominal, no hidden equipment'),
('board','Blank pale information panel','#C3C6BB','Observed rear information panel; no text/artwork reproduced'),
('display','Blank dark panel','#292E27','Observed dark display/background; no lettering'),
('seat','Dark bench seat','#53594C','Visible benches simplified'),
('base','Authored support base','#ABA99D','Authored continuous support, not pavement reconstruction')]]
SCALE=18.0
P={'width':10.,'depth':2.25,'height':3.35,'front_post_x':[-5.,-2.45,2.1,5.],'nominal_scale_mm_per_unit':18,'glazing':'Omitted, retaining open frame; not replaced with opaque wall','roof':'Thin nominal solid slab; no solar panels or unseen equipment inferred from name'}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.16]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed principal component, nominal photo-proportional dimensions'):add(name,box(a,b),mat,evidence)
bx('Authored display support',[-5.35,-1.5,-.16],[5.35,1.35,0],5,'Authored support not full sidewalk/curb')
for j,x in enumerate(P['front_post_x']):
 bx('Front post '+str(j+1),[x-.055,-1.06,0],[x+.055,-.94,3.28],0,'Four principal front columns visible in photo')
 bx('Rear frame upright '+str(j+1),[x-.045,.94,0],[x+.045,1.04,3.28],0,'Simplified visible rear framing; no hidden subdivisions claimed')
for y in [-1.,1.]:
 bx('Upper longitudinal beam '+str(y),[-5.1,y-.065,3.11],[5.1,y+.065,3.3])
# End return framing stays visually open; no opaque substitute for glass.
for x in [-5.,5.]:
 bx('End upper return '+str(x),[x-.06,-1.02,3.1],[x+.06,1.06,3.29])
 bx('End lower rail '+str(x),[x-.045,-1.02,.38],[x+.045,1.06,.46])
# Right return centre upright and mid-height rail visible in source.
bx('Right return centre upright',[4.95,-.04,0],[5.05,.06,3.23])
bx('Right return mid rail',[4.95,-1.02,2.2],[5.05,1.04,2.28])
bx('Rear lower frame rail',[-5.04,.94,.43],[5.04,1.04,.51])
bx('Rear upper panel rail',[-5.04,.94,2.66],[5.04,1.04,2.74])
bx('Thin plain roof',[-5.22,-1.2,3.26],[5.22,1.2,3.40],1,'Visible flat shallow roof/fascia. Unseen upper details omitted; no inferred photovoltaic equipment')
# Photo includes central pale information board and dark upper display.
bx('Central blank information board',[-2.47,.91,.95],[2.12,1.045,2.19],2,'Visible rear board; all posters/maps/lettering intentionally omitted')
bx('Central blank dark display',[-2.47,.90,2.19],[2.12,1.05,2.66],3,'Observed dark upper display, no content')
bx('Left rear blank dark notice panel',[-5.0,.91,1.88],[-2.43,1.045,2.65],3,'Observed dark left rear panel; no text')
for name,a,b in [('Left',-4.7,-2.75),('Right',2.42,4.7)]:
 bx(name+' bench seat',[a,.20,.47],[b,.83,.56],4,'Visible side bench, nominal seat/leg dimensions')
 for x in [a+.18,b-.18]:
  bx(name+' bench support '+str(x),[x-.055,.27,0],[x+.055,.75,.50],0,'Simplified visible bench support')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NHU green-energy bus shelter');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete principal bus shelter frame, roof, benches and observed blank information boards. Glazing omitted, no invented solar equipment or lettering. Nominal photo proportions.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
