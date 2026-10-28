#!/usr/bin/env python3
"""Taoran teahouse 2001 survey selected two-wing exterior study, not whole present-day building."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id': 'plaster', 'name': 'Entry landing', 'hex': '#B7B4A6', 'evidence': '2001 survey entrance level; color approximate'}, {'id': 'wood', 'name': 'Timber wall and lower panels', 'hex': '#816544', 'evidence': '2001 monochrome survey timber surfaces; illustrative uncalibrated brown'}, {'id': 'frame', 'name': 'Timber frames', 'hex': '#584832', 'evidence': '2001 survey timber sash rhythm'}, {'id': 'glass', 'name': 'Opaque glazing surrogate', 'hex': '#809291', 'evidence': 'Opaque solid backing, no interior transparency'}, {'id': 'roof', 'name': 'Roof tiles', 'hex': '#68716A', 'evidence': '2001 survey tile roofs; color illustrative not historic color measurement'}, {'id': 'base', 'name': 'Display base', 'hex': '#B9B6A9', 'evidence': 'Author-created support, not garden terrain'}, {'id': 'white', 'name': 'Plaster infill', 'hex': '#D9D8CC', 'evidence': 'Survey plaster panels where drawn; illustrative tone'}, {'id': 'dark', 'name': 'Recess backing', 'hex': '#383A34', 'evidence': 'Solid-backed aperture surrogate'}, {'id': 'brick', 'name': 'Brick pier', 'hex': '#8E7A64', 'evidence': 'Survey195 pier support, approximate color'}, {'id': 'cut', 'name': 'Research cutoff', 'hex': '#9EAAA9', 'evidence': 'Authored boundary to excluded service spaces, not historical wall'}]
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



def gable(x0,x1,y0,y1,z0,z1,axis='y'):
 pts=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]]
 pts+=([[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]]if axis=='y'else[[(x0+x1)/2,y0,z1],[(x0+x1)/2,y1,z1]])
 return hull(pts)
def shed(x0,x1,y0,y1,zlo,zhi,axis='y'):
 pts=[[x0,y0,min(zlo,zhi)-.13],[x1,y0,min(zlo,zhi)-.13],[x1,y1,min(zlo,zhi)-.13],[x0,y1,min(zlo,zhi)-.13]]
 pts+=([[x0,y0,zlo],[x1,y0,zlo],[x0,y1,zhi],[x1,y1,zhi]]if axis=='y'else[[x0,y0,zlo],[x0,y1,zlo],[x1,y0,zhi],[x1,y1,zhi]])
 return hull(pts)
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('F','B'):
  a,b=(plane-depth,plane+.025)if side=='F'else(plane-.025,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.025)if side=='L'else(plane-.025,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def window(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' frame',side,plane,u-w/2-.055,u+w/2+.055,z-.055,z+h+.055,.06,2,ev)
 panel(name+' opaque glass',side,plane,u-w/2,u+w/2,z,z+h,.085,3,'Opaque glass proxy; no interior modeled')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.018,q+.018,z,z+h,.13,2,ev)
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.018,q+.018,.15,2,ev)
def shutter(name,side,plane,u,w,z,h,n,ev):
 panel(name+' dark back',side,plane,u-w/2,u+w/2,z,z+h,.09,7,'Solid-backed security grille, not full opening')
 for i in range(n):
  q=u-w/2+.025+(w-.05)*i/(n-1);panel(name+' bar',side,plane,q-.018,q+.018,z,z+h,.15,2,ev)
# Survey-plan local coordinates; N arrow is oblique to sheet and scene axes are plan-aligned.
ev='2001 survey plan191, south/east elevations193–194 and section195; control dimensions plus explicitly approximate registration'
bx('Authored study base',[-1,-1,-.6],[19,14.3,0],5,'Author-created flat support; not actual hillside/garden')
# Raised main floor blocks, original two staggered room wings; enclosed interiors are solid proxies.
for name,a,b in [('Southwest tea room',[2.73,1.82,.60],[9.405,6.975,4.07]),('Northeast tea room',[10.01,7.885,.60],[17.595,12.74,4.07]),('Northwest 4.5-mat end room',[7.28,9.1,.60],[10.01,12.285,3.75])]:
 bx(name+' solid exterior proxy',a,b,1,ev+'; interior not reconstructed')
 # Foundation piers, rather than filling visible underfloor strip.
 for x in [a[0]+.14,(a[0]+b[0])/2,b[0]-.14]:
  for y in [a[1]+.14,b[1]-.14]:bx(name+' brick pier',[x-.14,y-.14,0],[x+.14,y+.14,.65],8,'Survey section195 brick pier support; individual placement simplified')
# Connecting corridor and entry form part of surveyed selected scope.
for name,x0,x1,y0,y1,h in [('Joining corridor',0,10.01,6.975,7.885,3.30),('Wing junction',7.28,10.01,7.885,9.10,3.40),('Entrance and reception',0,2.73,1.82,6.975,3.03)]:
 bx(name,[x0,y0,.43],[x1,y1,h],1,'Survey191/196 entry and circulation; walls solid-backed; positions estimated from dimensioned plan')
 for x in [x0+.15,x1-.15]:
  bx(name+' foot',[x-.13,y0+.1,0],[x+.13,y0+.35,.48],8,'Author-positioned pier aligned with survey corridor, not individual foundation measurement')
# Low glazed additions explicitly retained as they existed at survey time, not claimed original design.
for name,x0,x1,y0,y1 in [('South glazed addition',2.73,9.405,0,1.82),('East glazed return',9.405,10.525,0,6.975),('North wing low glazed addition',10.01,16.685,6.975,7.885)]:
 bx(name+' floor',[x0,y0,.43],[x1,y1,.62],1,'2001 survey plan191 added glazed veranda footprint and section195 lowered floor; not restored-current state')
 bx(name+' solid glazing backing',[x0,y0,.62],[x1,y1,2.80],3,'Opaque solid-backed glazing surrogate, no interior transparency')
 for x in [x0+.15,(x0+x1)/2,x1-.15]:
  for y in [y0+.12,y1-.12]:bx(name+' pier',[x-.12,y-.12,0],[x+.12,y+.12,.5],8,'Survey undercroft/piers approximated, not all measured')
# Two hipped roofs, roof-wall control inferred from section rather than misusing975.14 as total roof rise.
for name,x0,x1,y0,y1 in [('Southwest main roof',2.73,9.405,1.82,6.975),('Northeast main roof',7.28,17.595,7.885,12.74)]:
 xa,xx,ya,yy=x0-.70,x1+.70,y0-.70,y1+.70
 add(name,hip(xa,xx,ya,yy,3.80,5.04514),4,'Survey193–195 two staggered hipped roofs; ridge section control 5045.14mm excludes decorative crest; eave3.80m and overhang approximate')
 d=min((xx-xa)/2,(yy-ya)/2);cy=(ya+yy)/2
 add(name+' ridge',beam([xa+d,cy,5.045],[xx-d,cy,5.045],.07),4,'Coarse ridge cap, no precise tile/crest carving')
 for x in [xa+d,xx-d]:bx(name+' ridge end finial',[x-.045,cy-.045,5.02],[x+.045,cy+.045,5.18],4,'Elevation193–194 visible ridge-end ornament, coarse upright proxy not exact carving')
 for t in [.10,.25,.40,.55,.70,.85]:
  z=3.80+(5.04514-3.80)*t
  for y in [ya+(cy-ya)*t,yy-(yy-cy)*t]:add(name+' coarse tile course',beam([xa+d*t,y,z+.006],[xx-d*t,y,z+.006],.027),4,'Coarse roof tile courses; not individual concave tile profiles')
# Low hoods/addition roofs preserve tiered silhouette.
for name,bounds,axis in [('South low roof',(2.60,9.54,-.20,1.90,3.40,3.62),'y'),('East return low roof',(9.30,10.72,-.20,7.05,3.62,3.40),'x'),('North wing low roof',(9.95,16.88,6.78,8.0,3.40,3.62),'y')]:add(name,shed(*bounds,axis=axis),4,'Survey193–195 low added veranda roof, approximate slope/end junction')
add('Entrance shallow roof',gable(-.25,2.95,1.57,7.10,3.03,3.70,axis='x'),4,'Survey193 left entrance roof and196 entry heights; simplified roof profile')
add('Connector low roof',shed(-.15,7.40,6.80,8.03,3.30,3.52),4,'Survey selected connector roof approximate; excluded northwest service roofs not invented')
# Facade glazing rows; actual room locations follow plan, fine panes are coarse study proxies.
def glazed(name,side,plane,u0,u1,z=.87,h=1.72,bays=4):
 w=(u1-u0)/bays
 for i in range(bays):
  u=u0+(i+.5)*w;window(name+' bay '+str(i+1),side,plane,u,w-.09,z,h,3,4,'Survey193–194 timber glass grids; coarse pane subdivisions, not every historic sash measured')
  panel(name+' timber bottom',side,plane,u-w/2+.04,u+w/2-.04,.60,z,.17,1,'Survey193–195 wood lower sash panels')
  for q in np.arange(u-w/2+.10,u+w/2-.06,.15):panel(name+' lower board rhythm',side,plane,q,q+.025,.63,z-.02,.19,2,'Coarse vertical wood-board divisions')
# Southwest added outer walls and selected original visible upper bands.
glazed('South addition','F',0,2.73,9.405,bays=5)
glazed('East return','E',10.525,.05,6.85,bays=5)
glazed('Northeast south addition','F',6.975,10.01,16.685,bays=5)
glazed('Northeast east facade','E',17.595,7.99,11.73,bays=3)
# North elevation follows solid cupboard/back walls in plan; unverified openings are not invented.
# Recess-like raised entry double doors, landing and circular front light.
window('Entrance double door','L',0,3.05,1.70,.27,2.02,4,4,'Survey196 entry elevation panel types approximated, recessed threshold not interior')
panel('Door lower timber','L',0,2.20,3.90,.27,.75,.18,1,'Survey entrance lower wood panels')
panel('Door central stile','L',0,3.03,3.07,.27,2.29,.20,2,'Door leaf division retained')
for i in range(3):bx('Entrance step',[-.54+i*.18,2.05,0],[-.34+i*.18,4.05,.10+i*.10],0,'Author-simplified entry level transition, not restored modern ramp')
# Circular window on south entrance wall, per193/196.
cx,cz=.90,2.20;rad=.34
circle=mf.CrossSection.circle(rad*100,32).extrude(26).rotate([90,0,0]).translate([cx*100,1.85*100,cz*100])
add('Entrance circular dark light',circle,7,'Survey193/196 circular entry light, opaque backing')
for t in np.linspace(0,2*math.pi,25)[:-1]:
 a=[cx+rad*math.cos(t),1.61,cz+rad*math.sin(t)];b=[cx+rad*math.cos(t+math.pi/12),1.61,cz+rad*math.sin(t+math.pi/12)];add('Round light frame',beam(a,b,.035),2,'Survey circular frame, coarse segments')
# Rectangular grille surrounding the round entry light (survey193/196), coarse framing.
for x in [.24,.43,1.37,1.56]:
 panel('Round-window surrounding vertical frame','F',1.82,x-.025,x+.025,1.72,2.68,.24,2,'Survey193/196 rectangular grille around circular opening; coarse approximate subdivisions')
for z in [1.72,2.68]:
 panel('Round-window surrounding horizontal frame','F',1.82,.215,1.585,z-.025,z+.025,.24,2,'Survey rectangular outer frame; not measured joinery')
# Coarse horizontal weatherboard relief on unobstructed entrance lower wall.
for z in np.arange(.53,1.64,.16):
 panel('Entrance horizontal weatherboard','F',1.82,.02,2.70,float(z),float(z)+.022,.035,1,'Survey193 horizontal timber weatherboarding; coarse relief only')
# Continuous upper vertical sunshade strips, separate from glass rows.
for side,plane,u0,u1 in [('F',-.05,2.66,9.46),('E',10.57,.05,6.90),('F',6.93,10.0,16.70)]:
 panel('Upper shade backing',side,plane,u0,u1,2.68,3.28,.05,1,'Survey193–194 continuous upper vertical screen band above low glazing')
 for u in np.arange(u0,u1,.105):panel('Upper shade slat',side,plane,float(u),float(u)+.032,2.68,3.28,.09,2,'Coarse solid-backed vertical shade slats')
# Author gray closure marks the omitted service-area interface, not historic facade.
for side,plane,u0,u1,z1 in [('B',7.885,0,7.28,3.25),('L',7.28,9.10,12.285,3.72)]:
 panel('Study cutoff closure',side,plane,u0,u1,.43,z1,.025,9,'Author-created boundary to excluded northwest kitchen/mechanical/preparation and male/female toilets; NOT an existing historical wall')

s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Taoran teahouse 2001 survey selected two-wing exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2001 survey two wings, entry and surveyed glazed additions only. Excludes northwest service rooms and gardens; gray author cutoff is not historic wall. No current restoration or trial-print claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
