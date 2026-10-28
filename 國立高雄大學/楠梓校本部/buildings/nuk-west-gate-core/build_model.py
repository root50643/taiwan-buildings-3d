#!/usr/bin/env python3
"""Original exterior approximation of NUK West Gate pedestrian piers/curved blockers; not background buildings."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'stone','name':'Light speckled granite approximation','hex':'#B4B5AE','evidence':'left stone pier and right cap, untextured'}, {'id':'cap','name':'White translucent cap simplified solid','hex':'#DCDDD6','evidence':'right light box visible pale band'}, {'id':'dark','name':'Dark horizontal louvers','hex':'#555950','evidence':'right square louvered pier'}, {'id':'red','name':'Red paving','hex':'#A47162','evidence':'schematic crop of red grey pavers'}, {'id':'steel','name':'Brushed steel barrier','hex':'#A9B0AF','evidence':'visible tubular vehicle blockers'}, {'id':'yellow','name':'Yellow protective sleeve','hex':'#D4AF2C','evidence':'front low rail sleeve'}, {'id':'base','name':'Concrete paving and display base','hex':'#BFC1B9','evidence':'concrete threshold crop and authored support'}]
SCALE=15.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.2]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-derived approximate proportion; not measured'):add(name,box(a,b),mat,evidence)
def cyl(name,x,y,z0,z1,r0,r1,mat,n=48,evidence='Visible lamp form simplified, dimensions estimated'):
 add(name,mf.Manifold.cylinder(z1-z0,r0,r1,n).translate([x,y,z0]),mat,evidence)
bx('Display base',[-.4,-1.2,-.2],[5.6,4.8,0],6,'Authored connected display plinth, not entire avenue')
bx('Concrete pedestrian threshold',[0,-.6,-.01],[5.2,2.1,.08],6,'Photo3 visible light concrete entrance threshold')
bx('Cropped campus brick approach',[0,2.05,-.01],[5.2,4.5,.08],6,'Cropped campus-side paving, dimensions estimated')
for row in range(6):
 for col in range(13):
  if (row+col)%3!=0:
   bx(f'Schematic paver {row}-{col}',[col*.4+.01,2.1+row*.4+.01,.075],[col*.4+.39,2.1+row*.4+.39,.09],3,'Approximate paving pattern; not exact tile layout')
bx('Left stone pier',[0,.3,.04],[.85,1.05,2.12],0,'Visible rectangular stone pier; back depth estimated')
bx('Left top coping',[-.015,.285,1.91],[.865,1.065,2.15],0,'Visible slightly projecting coping band')
for z in [1.48,1.90]:bx(f'Left stone joint {z}',[-.005,.285,z],[.86,.31,z+.012],2,'Two visible horizontal panel joints simplified')
bx('Right pier inner mass',[4.05,.3,.04],[5.05,1.3,2.14],2,'Louvered square pillar; rear faces neutral core')
# Visible front and left-side louvers, not mirrored unseen faces.
for k in range(17):
 z=.15+k*.098
 bx(f'Front louver {k+1}',[4.02,.25,z],[5.08,.35,z+.038],2,'Photo3 repeated dark horizontal grille; count approximate')
 bx(f'Left side louver {k+1}',[4.00,.28,z],[4.10,1.31,z+.038],2,'Photo3 visible receding louver side; depth estimated')
bx('Right white upper light box',[4.01,.26,1.84],[5.09,1.34,2.20],1,'White light-box band visible; opaque model, not functional luminaire')
bx('Right stone coping',[3.98,.23,2.19],[5.12,1.37,2.43],0,'Visible thick stone upper coping')
# Rounded steel U barriers; curves made from intersecting cylinders and ball joints.
def rod(name,a,b,r,mat):
 a=np.array(a);b=np.array(b);d=b-a;length=float(np.linalg.norm(d))
 if length<1e-7:return
 angle=math.degrees(math.acos(d[2]/length));yaw=math.degrees(math.atan2(d[1],d[0]))
 s=mf.Manifold.cylinder(length,r,r,16).rotate([0,angle,yaw]).translate(a.tolist());add(name,s,mat,'Visible rounded tubular blocker, thickened for scale; dimensions approximate')
def hoop(name,x,y,width,h,r=.032):
 radius=width/2;z0=.055;zc=h-radius
 rod(name+' left leg',[x-width/2,y,z0],[x-width/2,y,zc],r,4)
 rod(name+' right leg',[x+width/2,y,z0],[x+width/2,y,zc],r,4)
 points=[[x+radius*math.cos(t),y,zc+radius*math.sin(t)] for t in np.linspace(0,math.pi,13)]
 for i,(a,b) in enumerate(zip(points[:-1],points[1:])):rod(name+f' arch{i}',a,b,r,4)
 for i,p in enumerate(points):add(name+f' joint{i}',mf.Manifold.sphere(r,12).translate(p),4,'Round rail joints continuous; not separate balls in real object')
# Two compound curved-pipe groups, not four independent U barriers.
# Hidden connection/grounding topology cannot be established; this continuous return is explicitly schematic.
def curved_path(name,pts,r=.032):
 for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):rod(name+f' segment{i}',a,b,r,4)
 for i,p in enumerate(pts):add(name+f' bend joint{i}',mf.Manifold.sphere(r,12).translate(p),4,'Continuous simplified tube; hidden topology not verified')
for side,x in [('left',1.5),('right',3.08)]:
 front=[]
 front.append([x-.20,0,.055]);front.append([x-.20,0,.90])
 front += [[x+.20*math.cos(t),0,.90+.20*math.sin(t)] for t in np.linspace(math.pi,0,15)]
 front.append([x+.20,0,.50])
 # U-shaped lower return projected into depth, connects front to tall narrow rear turn.
 front += [[x+.20,.50+.50*math.cos(t),.50+.26*math.sin(t)] for t in np.linspace(math.pi,2*math.pi,15)]
 front.append([x+.20,1.0,1.12])
 front += [[x+.10+.10*math.cos(t),1.0,1.12+.10*math.sin(t)] for t in np.linspace(0,math.pi,13)]
 front.append([x,1.0,.055])
 curved_path(side+' compound returning blocker',front)
# Low transverse blocker at front right, yellow central sleeve.
rod('Low blocker left leg',[3.51,-.61,.05],[3.51,-.61,.18],.034,4)
rod('Low blocker right leg',[4.75,-.61,.05],[4.75,-.61,.18],.034,4)
rod('Low blocker crossbar',[3.62,-.61,.29],[4.64,-.61,.29],.034,4)
for side,cx,start in [('left',3.62,math.pi/2),('right',4.64,0)]:
 pts=[[cx+.11*math.cos(t),-.61,.18+.11*math.sin(t)] for t in np.linspace(start,start+math.pi/2,9)]
 for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):rod(side+f' low bend{i}',a,b,.034,4)
 for i,pt in enumerate(pts):add(side+f' low joint{i}',mf.Manifold.sphere(.034,12).translate(pt),4,'Simplified continuous rounded bend')
rod('Yellow sleeve',[3.84,-.61,.29],[4.40,-.61,.29],.040,5)
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK west gate pedestrian piers and vehicle blockers core');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo west pedestrian gate core; estimated dimensions; not whole West Gate, building, road or current survey; no trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
