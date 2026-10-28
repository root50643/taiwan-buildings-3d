#!/usr/bin/env python3
"""Original exterior approximation of NUK East Gate low walls/paving; not background buildings."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'frame','name':'Dark aggregate wall frame','hex':'#62665D','evidence':'visible dark speckled coping/frame, untextured approximation'}, {'id':'panel','name':'Cream inset wall panels','hex':'#D6C6A2','evidence':'visible pale inset panels'}, {'id':'concrete','name':'Grey entrance slab','hex':'#969990','evidence':'visible depressed concrete surface'}, {'id':'red','name':'Muted red paving','hex':'#A26755','evidence':'visible red/grey paving rhythm, layout schematic'}, {'id':'metal','name':'Black lamp metal','hex':'#303A34','evidence':'two visible lantern lamp columns'}, {'id':'glass','name':'Opaque lantern glass','hex':'#CDC9B0','evidence':'simplified frosted lantern panes'}, {'id':'base','name':'Display support','hex':'#B3B6AD','evidence':'authored plinth not full surrounding terrain'}]
SCALE=15.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.2]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-derived approximate proportion; not measured'):add(name,box(a,b),mat,evidence)
def cyl(name,x,y,z0,z1,r0,r1,mat,n=48,evidence='Visible lamp form simplified, dimensions estimated'):
 add(name,mf.Manifold.cylinder(z1-z0,r0,r1,n).translate([x,y,z0]),mat,evidence)
bx('Display plinth',[-.7,-.6,-.2],[10.7,8.5,0],6,'Authored support; road, drainage, landscaping excluded')
bx('Lower entrance slab',[0,0,-.01],[10,4.5,.20],2,'Photo2-4 lower grey central slab')
# Single shallow threshold, not a flight of steps.
bx('Upper tiled approach slab',[0,4.35,-.01],[10,8,.27],2,'Cropped campus-side paved path, not the whole avenue')
# Three separate screen walls and two corner return assemblies, as seen both sides.
for i,(lo,hi,yy) in enumerate([(0,2.65,0),(2.35,4.25,.85),(3.95,6.05,0),(5.75,7.65,.85),(7.35,10,0)]):
 bx(f'Staggered low screen/frame {i+1}',[lo,yy,.17],[hi,yy+.25,1.07],0,'Three road-side wall faces and two staggered campus-side screens; not aligned continuous wall')
 bx(f'Campus pale panel {i+1}',[lo+.13,yy+.245,.30],[hi-.13,yy+.27,.94],1,'Pale inset visible from campus side')
 bx(f'Outside pale panel {i+1}',[lo+.13,yy-.025,.30],[hi-.13,yy+.005,.94],1,'Reverse view photo1 supports cream inset faces')
# Side walls overlap corner frames, extend inward to campus step.
for side,x in [('left',0),('right',9.75)]:
 bx(f'{side} return wall',[x,.15,.17],[x+.25,4.4,1.07],0,'Two long pale side returns seen in photos2-4')
 bx(f'{side} outer cream field',[x-.02,.34,.30],[x+.27,4.27,.94],1,'Two face relief approximation; exact aggregate texture excluded')
 bx(f'{side} top coping',[x-.035,.08,.96],[x+.285,4.44,1.10],0,'Dark top coping observed')
# Schematic running checker brick field, avoid claiming measured paving plan.
for row in range(7):
 for col in range(20):
  if (row+col)%3!=0:
   x=col*.5;y=4.55+row*.49
   bx(f'Red paving tile {row:02d}-{col:02d}',[x+.012,y+.012,.265],[x+.488,min(y+.478,7.99),.28],3,'Schematic cropped red/grey paving, not exact tile count/layout')
# Two lanterns flank campus-side threshold, poles thickened for model; not roadway lights.
for side,x in [('left',.23),('right',9.77)]:
 y=4.62
 cyl(side+' lamp plinth',x,y,.26,.59,.22,.22,4)
 cyl(side+' lamp base bell',x,y,.56,1.0,.17,.085,4)
 cyl(side+' tapered shaft',x,y,.95,3.55,.075,.048,4)
 for z,r in [(1.05,.09),(3.45,.08),(3.62,.13)]:cyl(side+f' collar {z}',x,y,z,z+.06,r,r,4)
 cyl(side+' lantern lower flare',x,y,3.53,3.70,.06,.20,4,n=6)
 cyl(side+' opaque hex lantern glass',x,y,3.67,4.15,.17,.22,5,n=6)
 cyl(side+' top rim',x,y,4.12,4.19,.24,.24,4,n=6)
 cyl(side+' lantern roof',x,y,4.17,4.42,.27,.045,4,n=6)
 cyl(side+' finial',x,y,4.40,4.55,.045,.005,4,n=12)
 # Shallow metal corner ribs on solid glazing, joined at both ends.
 for k in range(6):
  ang=2*math.pi*k/6
  a=np.array([x+.175*math.cos(ang),y+.175*math.sin(ang),3.68]);b=np.array([x+.225*math.cos(ang),y+.225*math.sin(ang),4.16])
  d=b-a;seg=mf.Manifold.cylinder(float(np.linalg.norm(d)),.018,.018,8)
  axis=np.cross([0,0,1],d);angle=math.degrees(math.acos(d[2]/np.linalg.norm(d)))
  # rotate toward radial tilt, then around vertical
  seg=seg.rotate([0,angle,math.degrees(ang)]).translate(a.tolist())
  add(side+f' lantern rib {k+1}',seg,4,'Simplified hexagonal lantern frame; no hollow glazing cavity')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK east gate low walls and paving core historical approximation');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo east entrance structure, not a building; estimated dimensions; outside road, planting, remote background buildings excluded; no current survey or trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
