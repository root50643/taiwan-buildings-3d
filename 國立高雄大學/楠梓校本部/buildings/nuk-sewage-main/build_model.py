#!/usr/bin/env python3
"""Original historical-photo exterior approximation of NUK sewage/reclaimed-water main building.
Not whole treatment works, not as-built/current survey. Obscured long sides are neutral.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'wall','name':'Approximate brown pebble facing','hex':'#9B8C74','evidence':'historical official photos; no color calibration'}, {'id':'glass','name':'Opaque warm grey glazing','hex':'#676E68','evidence':'visible tall glazed facade panels; no interior'}, {'id':'frame','name':'Warm light mullions','hex':'#C8B694','evidence':'visible facade window grid'}, {'id':'vent','name':'Muted green grey rooftop louvers','hex':'#7F9890','evidence':'six square cages in photo3; louver count simplified'}, {'id':'recess','name':'Dark entrance recess','hex':'#353D38','evidence':'observed front central entrance'}, {'id':'roof','name':'Neutral roof plane','hex':'#A5A394','evidence':'unseen roof infill neutral; no machinery or solar reconstruction'}, {'id':'base','name':'Display base','hex':'#B6BAB3','evidence':'authored support, not actual tanks/landscape'}]
SCALE=5.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.5]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Estimated photo proportion; not surveyed dimension'):add(name,box(a,b),mat,evidence)
W,D,H=16.,32.,6.2
bx('Artificial display base',[-1.4,-1.4,-.5],[W+1.4,D+1.4,0],6,'Display support only; whole treatment landscape and tanks excluded')
body=box([0,0,-.02],[W,D,H]);body=body-box([6.1,-.1,0],[9.9,.8,2.85]);add('Closed main building with neutral obscured long sides',body,0,'Historical rectangle estimated; vegetation conceals long side details, no invented window repetition')
bx('Recess entrance back',[6.12,.78,.02],[9.88,.84,2.83],4,'Front entrance shallow dark recess; no interior rooms')
bx('Door left vertical stile',[6.8,.66,.02],[6.93,.81,2.75],2)
bx('Door right vertical stile',[9.1,.66,.02],[9.23,.81,2.75],2)
# Window panels on two known/schematic short ends. Window grid is a colored raised solid relief.
def panel(name,x1,x2,z1,z2,cols,rows,rear=False,evidence='Visible historical photo grid, dimensions estimated'):
 y1,y2=(D-.02,D+.10) if rear else (-.10,.02)
 bx(name+' frame',[x1,y1,z1],[x2,y2,z2],2,evidence)
 y1,y2=(D+.095,D+.14) if rear else (-.14,-.095)
 bx(name+' opaque panes',[x1+.11,y1,z1+.10],[x2-.11,y2,z2-.10],1,evidence)
 y1,y2=(D+.13,D+.20) if rear else (-.20,-.13)
 for i in range(1,cols):
  x=x1+(x2-x1)*i/cols;bx(name+f' mullion {i}',[x-.04,y1,z1+.08],[x+.04,y2,z2-.08],2,evidence)
 for j in range(1,rows):
  z=z1+(z2-z1)*j/rows;bx(name+f' transom {j}',[x1+.08,y1,z-.04],[x2-.08,y2,z+.04],2,evidence)
panel('Front left high glazing',.8,5.2,.45,5.35,4,3,evidence='Left panel partly obscured by plants; same-width visible grid supports approximate matched rhythm')
panel('Front right high glazing',10.8,15.2,.45,5.35,4,3,evidence='Photo1/2 right high panel: 4 columns x 3 rows')
for i in range(3):panel(f'Front upper independent window {i+1}',5.9+i*1.45,7.12+i*1.45,4.25,5.6,1,1,evidence='Three independent windows above central entrance visible')
bx('Entrance header',[5.7,-.12,2.85],[10.3,.05,3.55],0,'Broad header under three upper windows')
for k in range(5):bx(f'Entrance louver simplified {k+1}',[6.0,-.19,2.98+k*.085],[10.0,-.10,3.025+k*.085],2,'Five display slats; actual louver blade count not claimed')
# Perspective suggests photo4 is opposite short end. Only visible panels modeled;
# offset/location and remaining crop are explicitly schematic, not a full rear elevation.
panel('Inferred opposite end wide glazing',8.6,13.4,.45,5.35,4,3,rear=True,evidence='Photo4 visible wide 4x3 panel; inferred opposite short end, x position schematic')
panel('Inferred opposite end narrow glazing',5.9,8.2,.45,5.35,2,3,rear=True,evidence='Photo4 adjacent narrow 2x3 panel; unseen remainder neutral')
# Thick flat cornice. No alleged roof equipment behind visible row.
bx('Continuous top beam',[-.12,-.12,5.8],[W+.12,D+.12,6.3],0,'Flat broad concrete top fascia visible in historical photos')
bx('Neutral roof infill',[.25,.25,6.26],[W-.25,D-.25,6.38],5,'Unseen plane neutral; later orthophoto solar structures not merged with historical reconstruction')
# Six square rooftop vents. Opaque solid body with external rails, not functional ventilation.
for i in range(6):
 y=2.7+i*5.1;cx=W/2;half=1.05
 bx(f'Roof vent {i+1} solid plinth',[cx-1.2,y-1.2,6.3],[cx+1.2,y+1.2,6.85],0,'Six rooftop square elements visible in distant official photo3; equal spacing approximate')
 bx(f'Roof vent {i+1} opaque backing',[cx-half+.07,y-half+.07,6.82],[cx+half-.07,y+half-.07,8.42],1,'Solid display backing for printable approximation; no real interior claim')
 for xx in [cx-half,cx+half-.12]:
  for yy in [y-half,y+half-.12]:bx(f'Roof vent {i+1} corner post {xx} {yy}',[xx,yy,6.8],[xx+.12,yy+.12,8.55],3,'Cage corner posts visible; slightly thickened model features')
 for k in range(7):
  z=6.96+k*.23
  for yy in [y-half-.03,y+half-.08]:bx(f'Roof vent {i+1} horizontal louver Y{k}{yy}',[cx-half-.02,yy,z],[cx+half+.02,yy+.11,z+.07],3,'Seven simplified horizontal rails, not literal blade count')
  for xx in [cx-half-.03,cx+half-.08]:bx(f'Roof vent {i+1} horizontal louver X{k}{xx}',[xx,y-half-.02,z],[xx+.11,y+half+.02,z+.07],3,'Seven simplified horizontal rails, not literal blade count')
 for yy in [y-half-.03,y+half-.09]:bx(f'Roof vent {i+1} top edge Y{yy}',[cx-half-.03,yy,8.43],[cx+half+.03,yy+.12,8.55],3)
 for xx in [cx-half-.03,cx+half-.09]:bx(f'Roof vent {i+1} top edge X{xx}',[xx,y-half-.03,8.43],[xx+.12,y+half+.03,8.55],3)
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK sewage reclaimed water plant main building historical exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo main-building exterior approximation; inferred partial rear, neutral obscured long sides; not whole treatment plant; not current/as-built; not trial printed'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
