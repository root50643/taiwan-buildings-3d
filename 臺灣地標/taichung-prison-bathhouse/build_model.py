#!/usr/bin/env python3
"""Taichung Prison Bathhouse restored exterior study; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('plaster','Light gray rendered base','#C1C0B8','Official restored bathhouse photos; uncalibrated'),('wood','Restored timber siding','#9C784D','Restored photos show natural wood; color varies across dates'),('frame','Wooden sash and doors','#815B34','Door/window survey plus restored photos'),('glass','Opaque glass proxy','#7A9597','Opaque proxy, not interior transparency'),('roof','Gray tiled roofs','#727571','Official restored aerial photo; enlarged coarse tile rhythm'),('base','Authored support','#B8B3A5','Display support only, not reconstructed grounds'),('white','Gable plaster and fascia','#D6D3C7','Restored gable photo'),('dark','Recess and grille backing','#4E493C','Solid-backed shading proxy, no opening through interior')]]
SCALE=.10
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,60]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat,evidence):add(name,box(a,b),mat,evidence)
def arch(w,bottom,spring,rise):
 pts=[(-w/2,bottom),(w/2,bottom),(w/2,spring)]+[(w/2*math.cos(t),spring+rise*math.sin(t))for t in np.linspace(0,math.pi,17)[1:]]
 return mf.CrossSection([(np.array(pts)*100).tolist()]).extrude(120).rotate([90,0,0]).translate([0,60,0])
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*100).tolist())
def hip(x0,x1,y0,y1,z0,z1):
 d=min((y1-y0)/2,(x1-x0)/2)
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(np.column_stack([x,y,z,a*100]))



# Control dimensions from 2014 proposed reconstruction plan, not asbuilt outside envelope.
W=9.232;D=9.226;H=4.4;peak=6.64;bx('Display support',[-3.2,-2,-.6],[W+1.2,D+2,0],5,'Authored support, not site topography')
bx('Main body lower rendered shell',[0,0,0],[W,D,1.5],0,'Proposed-plan control rectangle; solid interior proxy')
bx('Main timber upper shell',[0,0,1.5],[W,D,H],1,'Restored timber siding above rendered base, wall thickness omitted')
# The north and south entrances project beyond main bath walls.
for yy in [-.98,D]:
 bx('Projecting changing-room entry rendered base',[5.462,yy,0],[W,yy+.98,.5],0,'North/south projecting entries in proposed reconstruction plan')
 bx('Entry timber wall',[5.462,yy,.5],[W,yy+.98,3.75],1,'Entry projections; offsets approximate from plan')
# West boiler room retained; no speculative chimney.
bx('Boiler rendered lower wall',[-2.248,1.822,0],[.02,7.404,1.5],0,'224.8 by558.2cm proposed-plan control extent')
bx('Boiler timber upper wall',[-2.248,1.822,1.5],[.02,7.404,3.35],1,'Restored western single-pitch annex')
def gable(x0,x1,y0,y1,z0,z1):return hull([[x0,y0,z0],[x1,y0,z0],[x0,y1,z0],[x1,y1,z0],[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]])
def shed(x0,x1,y0,y1,zlo,zhi,axis='x'):
 pts=[[x0,y0,min(zlo,zhi)-.12],[x1,y0,min(zlo,zhi)-.12],[x1,y1,min(zlo,zhi)-.12],[x0,y1,min(zlo,zhi)-.12]]
 if axis=='x':pts += [[x0,y0,zlo],[x0,y1,zlo],[x1,y0,zhi],[x1,y1,zhi]]
 else:pts += [[x0,y0,zlo],[x1,y0,zlo],[x0,y1,zhi],[x1,y1,zhi]]
 return hull(pts)
add('Main gable roof',gable(-.5,W+.5,-.55,D+.55,H,peak)-gable(-.55,W+.55,-.55,D+.55,H-.30,peak-.16),4,'907cm structural span and224cm rise guide roof; eave overhang/outer height photo-estimated')
add('Boiler single-pitch roof',shed(-2.55,.15,1.52,7.704,3.35,4.08),4,'Restored aerial photograph shows single pitch toward west')
add('North entry canopy',shed(5.3,W+.4,-1.3,.15,3.65,4.02,'y'),4,'North entry roof from plan and south photographic analogue; north exact details inferred')
add('South entry canopy',shed(5.3,W+.4,D-.15,D+1.3,4.02,3.65,'y'),4,'South entry low tiled canopy visible in restored2019photo')
# Plastered end gables with coarse timber grid, visible below main roof slope.
for x in [0,W]:
 add('Pale end gable',gable(x-.015,x+.015,0,D,H-.04,peak-.08),6,'Gable white plaster fields and timber members visible in restored side photo')
 for yy in [1.4,2.9,4.613,6.3,7.8]:
  zz=H+(peak-H)*(1-abs(yy-D/2)/(D/2))-.12
  bx('Gable vertical timber',[x-.04,yy-.05,H-.03],[x+.04,yy+.05,zz],2,'Coarse gable timber grid; precise joints omitted')
# Lantern sits over western bathing rooms, not centred on full roof.
lx0,lx1=1.45,4.55;ly0,ly1=3.60,5.626
bx('Ridge ventilating lantern',[lx0,ly0,5.7],[lx1,ly1,7.05],1,'Lantern position from report roof framing and restored aerial; envelope estimated,121cm is structural post only')
add('Lantern gable roof',gable(lx0-.22,lx1+.22,ly0-.20,ly1+.20,7.05,7.65),4,'Small gable roof on ventilating lantern, height approximate')
# Facade strips attach to solid body; windows are opaque proxies.
def slab(name,side,u0,u1,z0,z1,depth,mat,ev,plane=None):
 if side in ('N','S'):
  y=(0 if side=='N' else D) if plane is None else plane;a,b=(y-depth,y+.02)if side=='N'else(y-.02,y+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  x=(0 if side=='W' else W)if plane is None else plane;a,b=(x-depth,x+.02)if side=='W'else(x-.02,x+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def grid(side,u,w,z,h,cols,rows,plane=None):
 ev='Opening placement from proposed reconstruction plan; lower sash width assembled from leaf table, upper-group width photo-proportioned where dimension reference ambiguous; frame margins estimated'
 slab(side+' outer wood frame',side,u-w/2-.06,u+w/2+.06,z-.06,z+h+.06,.08,2,ev,plane)
 slab(side+' opaque pane',side,u-w/2,u+w/2,z,z+h,.10,3,'Opaque proxy, no interior reconstructed',plane)
 for j in range(cols+1):
  xx=u-w/2+w*j/cols;slab(side+' vertical sash',side,xx-.022,xx+.022,z,z+h,.145,2,ev,plane)
 for j in range(rows+1):
  zz=z+h*j/rows;slab(side+' horizontal sash',side,u-w/2,u+w/2,zz-.022,zz+.022,.17,2,ev,plane)
def louvers(side,u,w,z,h,n,plane=None):
 slab('Vent louver frame',side,u-w/2-.05,u+w/2+.05,z-.05,z+h+.05,.075,2,'Photo-visible slatted ventilation; coarse solid-backed approximation',plane)
 slab('Vent dark backing',side,u-w/2,u+w/2,z,z+h,.09,7,'Solid-backed louver, not full ventilation passage',plane)
 for j in range(n):slab('Coarse louver slat',side,u-w/2+.025,u+w/2-.025,z+j*h/n,z+j*h/n+.035,.13,1,'Slat count simplified, fine bevels omitted',plane)
# Bath windows along north/south: four main leaves plus shorter upper lights.
for side in ['N','S']:
 grid(side,2.73,3.54,1.65,.945,4,3)
 grid(side,2.73,3.30,2.73,.47,4,1)
 louvers(side,2.73,3.9,3.53,.30,4)
 # Source-visible shallow window hood, north geometry inferred from source window arrangement.
 yy=-.40 if side=='N' else D+.04
 add(side+' bath window hood',shed(.78,4.68,yy,yy+.36,3.25,3.39,'y'),2,'Shallow window canopy from restored south photo; northern counterpart approximate')
# East changing-room groups: lower four leaves, upper three leaves per W5 and repair advice for W4.
for yy in [2.28,6.95]:
 grid('E',yy,2.732,1.12,1.35,4,3)
 grid('E',yy,2.732,2.65,.61,3,3) # Upper sash is horizontal in source drawing; whole width photo-proportioned, not 123cm interpreted as height.
# Main doors: each survey dimension is a SINGLE leaf, north D2 differs from south D1.
for side,yy,leafh,leafw,nrows,nlower in [('N',-.98,1.792,.89,3,2),('S',D+.98,1.775,.892,2,3)]:
 u=8.1;w=2*leafw;z=.45
 slab('Entry double-door wood',side,u-w/2-.05,u+w/2+.05,z,z+leafh,.075,2,'D1/D2 single leaf height and width doubled only across opening; placement estimated',yy)
 grid(side,u,w-.10,z+leafh*.48,leafh*.50,4,nrows,yy)
 for j in range(2*nlower+1):slab('Lower door panel rail',side,u-w/2+w*j/(2*nlower)-.022,u-w/2+w*j/(2*nlower)+.022,z+.05,z+leafh*.45,.12,1,'South3/north2 lower panels per leaf, coarse interpretation',yy)
 grid(side,u,1.676,z+leafh+.10,.395,4,1,yy)
 for j in range(2):
  if side=='N':bx('North entry step',[u-1.1,yy-.72+j*.3,0],[u+1.1,yy,.23+j*.22],0,'Coarse entry steps; terrain omitted')
  else:bx('South entry step',[u-1.1,yy,0],[u+1.1,yy+.72-j*.3,.23+j*.22],0,'Coarse entry steps; terrain omitted')
 grid(side,6.30,1.25,2.1,.60,3,1,yy)
# Toilet side high windows on projecting returns.
for yy in [-.48,D+.48]:grid('E',yy,.848,2.05,.6,2,1)
# Boiler doors on north/south, and two timber-grille openings on west.
for side,yy in [('N',1.822),('S',7.404)]:
 slab('Boiler plain plank door',side,-1.65,-.70,.22,2.25,.07,1,'Boiler access shown in proposed plan; plain door detail approximate',yy)
 for j in range(7):slab('Boiler door plank joint',side,-1.65+j*.14,-1.63+j*.14,.22,2.25,.095,2,'Coarse plank divisions',yy)
 if side=='N':bx('Boiler entry step',[-1.70,yy-.45,0],[-.65,yy,.23],0,'Minimal side step')
 else:bx('Boiler entry step',[-1.70,yy,0],[-.65,yy+.45,.23],0,'Minimal side step')
for yy in [2.75,6.4]:
 slab('Boiler grille backing','W',yy-.603,yy+.603,1.55,2.88,.08,7,'W8 two timber-grille leaves,133cm high',-2.248)
 for j in range(9):slab('Boiler vertical grille','W',yy-.603+j*.15,yy-.56+j*.15,1.55,2.88,.13,1,'Coarse W8 vertical wood grille',-2.248)
# Main west bath openings outside the attached boiler-room interval.
for yy in [.95,8.28]:grid('W',yy,1.30,1.65,1.415,2,3)
# Three lantern louver groups on each long side.
for side,yy in [('N',ly0),('S',ly1)]:
 for xx in [1.98,3.0,4.02]:louvers(side,xx,.89,6.25,.60,7,yy)
# Enlarged horizontal rain-board rhythm on all exterior wood surfaces.
for side,a,b,plane,zend in [('N',0,W,0,H),('S',0,W,D,H),('E',0,D,W,H),('W',0,D,0,H),('N',5.462,W,-.98,3.75),('S',5.462,W,D+.98,3.75),('W',1.822,7.404,-2.248,3.35)]:
 for zz in np.arange(1.53,min(zend,3.82) if zend==H else zend,.21):slab('Coarse rainboard course',side,a+.015,b-.015,float(zz),float(zz)+.025,.035,2,'21cm board course from survey; joints simplified behind raised frames',plane)
# Continuous pale plaster band under main eaves, visible in restored photographs.
for side,plane in [('N',0),('S',D)]:
 slab('Pale under-eave plaster band',side,-.03,W+.03,3.86,H-.03,.06,6,'Restored2019 bathhouse photo shows broad pale strip below main eaves; bounds photo-estimated',plane)
# Coarse roof tile rows rather than texture; avoids embedding third-party imagery.
for yy in np.arange(-.42,D/2,.43):
 zz=H+(peak-H)*(yy+.55)/(D/2+.55)+.03
 for y in [yy,D-yy]:add('Main roof tile-course relief',beam([-.48,y,zz],[W+.48,y,zz],.035),4,'Enlarged coarse tile courses, not individual measured tile pieces')
add('Main ridge cap',beam([-.48,D/2,peak+.04],[W+.48,D/2,peak+.04],.07),4,'Simple raised ridge cap, decorative ends coarse')
add('Lantern ridge cap',beam([lx0-.22,D/2,7.68],[lx1+.22,D/2,7.68],.065),4,'Small lantern roof ridge cap')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)
s=s.mirror([0,1,0]).translate([0,922.6,0])
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Taichung Prison Bathhouse restored exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.mirror([0,1,0]).translate([0,922.6,0]).to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Restored bathhouse main-body exterior approximation; north inferred from official proposed plan/window table without full current north photo; no interiors/garden/other buildings, no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
