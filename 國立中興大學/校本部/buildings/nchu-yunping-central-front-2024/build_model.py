#!/usr/bin/env python3
"""NCHU Yunping central front cut segment. Dimensions are photo proportions, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('wall','Warm white exterior','#E1E1D6','Official 2024 aerial photo, approximate color'),
('frame','Light panel grid and window frame','#B9BDB8','Visible pale grids, reduced counts'),
('glass','Dark grey glazing screen','#525651','Window/screen shadow, no interior reconstruction'),
('solar','Grey photovoltaic modules','#797C78','Visible roof photovoltaic modules, not electrical design'),
('tower','Brown red tower cladding','#8D513C','Visible tapered central tower front'),
('base','Grey stairs and authored base','#AAA99E','Entry stairs; common base artificial'),
('unused','Pale fascia','#D0CEBE','Reserved'),
('cut','Artificial back closure','#B5B3A8','Unobserved cut back, not actual rear')]]
SCALE=5.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed visible feature; photo normalized, not measured'):add(name,box(a,b),mat,evidence)
def frontcyl(rad,depth,x,y,z,n=24):return mf.Manifold.cylinder(depth,rad,rad,n).rotate([90,0,0]).translate([x,y,z])
# Central front ONLY: left/right wings cut at their junction, no rear or footprint claim.
bx('Authored common cut footing',[-15,-5,-.6],[15,2.2,-.1],5,'Artificial support and cut boundary; not surveyed site')
bx('Central lower facade',[-14.6,-.12,-.2],[14.6,1.8,4.35],0,'Ground-level visible center/right only; left tree-obscured portion is blank authored support, not inferred openings; shallow depth arbitrary')
bx('Upper central tall rectangle',[-14.0,.8,4],[14.0,1.95,13.3],0,'White rectangular upper facade above two lower sloping solar awnings')
bx('Neutral artificial cut rear',[-14.0,1.86,-.18],[14.0,2.05,13.25],7,'Unobserved artificial closure, not real rear')
def slope(name,x0,x1,y0,y1,z0,z1,mat):
 # solid wedge roof slab, top pitches up away from viewer; thickness is authored
 vv=[[x0,y0,z0-.28],[x1,y0,z0-.28],[x1,y1,z1-.28],[x0,y1,z1-.28],[x0,y0,z0],[x1,y0,z0],[x1,y1,z1],[x0,y1,z1]]
 ff=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
 add(name,mf.Manifold(mf.Mesh(np.array(vv,dtype=np.float32),np.array(ff,dtype=np.uint32))),mat,'Visible pitched panel plane; depth and pitch normalized from photo, not measured')
# Pale fascia around photovoltaic covered roofs, two distinct lower strips.
slope('Lower white eave',-15,15,-3.8,.95,4.45,6.5,0)
slope('Lower solar plane',-14.8,14.8,-3.6,.90,4.58,6.55,3)
slope('Upper shallow white eave',-15,15,-1.5,1.1,7.1,8.1,0)
slope('Upper shallow solar plane',-14.8,14.8,-1.4,1.05,7.22,8.17,3)
# Panels: reduced symbolic modules; not exact cell count, and no electrical claim.
for x in range(-14,15,2):
 slope('Lower panel seam',x-.025,x+.025,-3.6,.9,4.60,6.57,1)
 slope('Upper panel seam',x-.025,x+.025,-1.4,1.05,7.24,8.19,1)
for y in [-2.7,-1.8,-.9,0]:
 z=4.58+(y+3.6)/4.5*1.97;bx('Lower panel cross seam',[-14.8,y-.025,z],[14.8,y+.025,z+.06],1,'Reduced PV grid representation; not cell-count reconstruction')
# Tall front screen and white vertical fins. Source has approximately 24 narrow divisions;
# model uses 24 divisions, micro mesh is deliberately abstracted, no invented interior.
bx('Upper screen shadow',[-11.8,.63,8.15],[11.8,.85,12.55],2)
for x in range(25):
 xx=-11.8+x*23.6/24;bx('White vertical screen fin',[xx-.055,.43,8.10],[xx+.055,.86,12.65],0)
for z in [9.15,10.45,11.65]:bx('Screen floor band',[-11.8,.49,z],[11.8,.86,z+.09],1)
# Roof cap solar planes flanking a red-brown open truncated tower.
for x0,x1 in [(-14,-4.2),(4.2,14)]:
 slope('Upper roof white plane',x0,x1,.45,1.95,13.25,13.7,0)
 slope('Upper roof solar plane',x0+.2,x1-.2,.48,1.90,13.32,13.75,3)
 for x in range(int(x0)+1,int(x1)):
  slope('Top panel fine seam',x-.02,x+.02,.48,1.9,13.34,13.77,1)
# Front trapezoid of tower only: depth is cut, not inferred roof enclosure.
vv=[[-4.2,.7,13.20],[4.2,.7,13.20],[3.45,.7,16.7],[-3.45,.7,16.7],[-4.2,2,13.20],[4.2,2,13.20],[3.45,2,16.7],[-3.45,2,16.7]]
ff=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]]
add('Brown tapered tower FRONT SLICE',mf.Manifold(mf.Mesh(np.array(vv,dtype=np.float32),np.array(ff,dtype=np.uint32))),4,'Observed trapezoid face only; real open rooftop machinery behind not reconstructed')
for z in [13.7+i*.25 for i in range(12)]:
 width=4.2-(z-13.20)/3.35*.75
 bx('Tower horizontal cladding seam',[-width,.66,z],[width,.74,z+.035],4,'Visible horizontal cladding, reduced count')
# Glazed ground-floor openings and central entry, no fabricated lettering.
for x0,x1 in [(5.0,8.5),(9.2,12.8),(-2.4,2.4)]:
 bx('Ground opening',[x0,-.25,.75],[x1,-.05,3.5],2)
 for x in [x0,(x0+x1)/2,x1]:bx('Opening frame',[x-.06,-.32,.72],[x+.06,.02,3.58],1)
bx('Blank entry sign',[-3.1,-.36,3.45],[3.1,.05,4.05],0,'Visible pale fascia but text omitted')
for k in range(4):bx('Simplified entry stair',[-2.8,-4.6+k*.5,-.15],[2.8,-.1,.12+k*.16],5,'Entry stair visible; count/depth illustrative, ramp and terrain omitted')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NCHU Yunping central front');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed central front slice ONLY, 2024 source state; side wings and rear excluded, shallow artificial backing, no full-building claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
