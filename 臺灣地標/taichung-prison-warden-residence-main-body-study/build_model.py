#!/usr/bin/env python3
"""Taichung Prison Warden Residence exterior approximation; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('plaster','Light gray rendered base','#C1C0B8','Official restored warden-residence photos; uncalibrated'),('wood','Restored timber siding','#9C784D','Restored photos show natural wood; color varies across dates'),('frame','Wooden sash and doors','#815B34','Door/window survey plus restored photos'),('glass','Opaque glass proxy','#7A9597','Opaque proxy, not interior transparency'),('roof','Gray tiled roofs','#727571','Official restored aerial photo; enlarged coarse tile rhythm'),('base','Authored support','#B8B3A5','Display support only, not reconstructed grounds'),('white','Gable plaster and fascia','#D6D3C7','Restored gable photo'),('dark','Recess and grille backing','#4E493C','Solid-backed shading proxy, no opening through interior'),('brick','Japanese wing brick base','#806354','Restored photographs show exposed brick base; individual mortar omitted')]]
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



# Historic total69shaku controls approximate scaling of proposed reconstruction drawing.
K=(69*10/33)/925
W=925*K;JX=485*K;WX=365*K;BACK=455*K
bx('Authored display support',[-2,-2.7,-.6],[W+2.7,12.6,0],5,'Authored support, not actual site terrain')
# Western wing and Japanese rooms. Lower plinth differs in material.
bx('Western plaster plinth',[0,0,0],[JX,205*K,.65],0,'Restored western facade plaster base; depth from reconstruction-plan tracing')
bx('Western timber main body',[0,0,.65],[JX,205*K,4.0],1,'Western natural timber rainboard facade; height photo-proportioned')
bx('Japanese brick plinth',[415*K,40*K,0],[W,406*K,.72],8,'Japanese brick foundation from restored photos; solid interior proxy')
bx('Japanese timber main body',[415*K,40*K,.72],[W,406*K,3.85],1,'Main rooms from proposed reconstruction plan; hidden interior omitted')
# Porch and side service projections, all independently distinguishable from the two roofs.
bx('Entry back wall',[WX,-.12,.25],[JX,.04,2.9],1,'Main entrance wall and porch from restored front photo')
for x in [WX+.12,JX-.12]:
 bx('Entry pier foot',[x-.15,-1.82,0],[x+.15,-1.46,.55],0,'Rendered foot at main porch column, dimensions estimated')
 bx('Entry porch column',[x-.075,-1.75,.45],[x+.075,-1.57,2.9],2,'Restored main entry has two timber posts')
bx('Entry porch floor',[WX,-1.9,.12],[JX,.08,.35],0,'Main porch platform; not measured terrain')
for j in range(2):bx('Entry front steps',[WX+.2,-2.35+j*.23,0],[JX-.2,-1.8,.12+j*.12],0,'Coarse entry steps')
bx('East service rooms base',[805*K,406*K,0],[W,510*K,.65],8,'Small rear service projection from proposed plan')
bx('East service rooms',[805*K,406*K,.65],[W,510*K,2.7],1,'Small rear service projection, details inferred from drawings')
bx('East projecting kitchen entrance base',[W,240*K,0],[W+80*K,355*K,.55],8,'Side entrance projection traced from proposed plan; photo-supported small gable')
bx('East projecting kitchen entrance',[W,240*K,.55],[W+80*K,355*K,2.7],1,'Side projecting room, simplified external openings')
bx('Western rear washroom foot',[-50*K,205*K,0],[0,305*K,.6],0,'Small rear end projection from official reconstruction drawing')
bx('Western rear washroom',[-50*K,205*K,.6],[0,305*K,2.7],1,'Back end small projection, unseen details inferred')
# Raised veranda floor, with actual empty clearance below and supporting columns.
def veranda(name,x0,x1,y0,y1,h=.72):
 bx(name+' deck',[x0,y0,h-.13],[x1,y1,h],1,'Official restored side/courtyard photographs show raised timber deck, not continuous plaster fill')
 for x in [x0+.12,(x0+x1)/2,x1-.12]:
  for y in [y0+.12,y1-.12]:
   bx(name+' stone foot',[x-.14,y-.14,0],[x+.14,y+.14,.2],0,'Coarse visible stone foundation foot; position estimated')
   bx(name+' support post',[x-.07,y-.07,.15],[x+.07,y+.07,h],2,'Raised corridor timber supports, coarse spacing')
veranda('Western rear veranda',0,WX,205*K,264*K)
veranda('Japanese return veranda',WX,415*K,205*K,455*K)
veranda('Japanese rear veranda',WX,805*K,406*K,455*K)
# Two intersecting hipped roofs, plus lower wraparound eaves and small gable canopies.
def gable(x0,x1,y0,y1,z0,z1,axis='y'):
 pts=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]]
 pts+=([[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]]if axis=='y'else[[(x0+x1)/2,y0,z1],[(x0+x1)/2,y1,z1]])
 return hull(pts)
def shed(x0,x1,y0,y1,zlo,zhi,axis='y'):
 pts=[[x0,y0,min(zlo,zhi)-.13],[x1,y0,min(zlo,zhi)-.13],[x1,y1,min(zlo,zhi)-.13],[x0,y1,min(zlo,zhi)-.13]]
 pts+=([[x0,y0,zlo],[x1,y0,zlo],[x0,y1,zhi],[x1,y1,zhi]]if axis=='y'else[[x0,y0,zlo],[x0,y1,zlo],[x1,y0,zhi],[x1,y1,zhi]])
 return hull(pts)
roofspec=[('Western main hip',-.45,JX+.35,-.45,205*K+.35,3.95,5.57),('Japanese main hip',WX-.15,W+.4,40*K-.35,406*K+.25,3.85,5.65)]
for n,x0,x1,y0,y1,z0,z1 in roofspec:
 add(n,hip(x0,x1,y0,y1,z0,z1),4,'Official roof restoration plan and restored aerial show two joined hipped roofs; heights estimated using truss evidence, not as-built dimensions')
 d=min((y1-y0)/2,(x1-x0)/2)
 add(n+' ridge',beam([x0+d,(y0+y1)/2,z1+.04],[x1-d,(y0+y1)/2,z1+.04],.065),4,'Coarse straight ridge, fine ridge ornaments omitted')
 for x,y in [(x0,y0),(x0,y1),(x1,y0),(x1,y1)]:
  xx=x0+d if x==x0 else x1-d
  add(n+' hip ridge',beam([x,y,z0+.03],[xx,(y0+y1)/2,z1+.03],.045),4,'Hip ridge lines supported by official aerial/roof plan')
add('Western rear lower roof',shed(-.35,WX+.12,205*K-.1,264*K+.35,3.6,3.1),4,'Low veranda roof visible in restored courtyard photo')
add('Japanese rear lower roof',shed(WX-.2,W+.3,406*K-.2,455*K+.35,3.45,3.1),4,'Roof plan and restored aerial show lower rear veranda eaves')
add('Japanese return lower roof',shed(WX-.35,415*K+.1,205*K-.1,455*K+.3,3.1,3.45,'x'),4,'Lower courtyard return eaves, photo-supported outline')
add('Japanese front lower eave',shed(JX-.15,W+.35,40*K-.65,40*K+.15,3.1,3.45),4,'Restored front has lower eave above Japanese lattice windows')
add('Main entry gable canopy',gable(WX-.25,JX+.25,-2.1,.18,2.91,3.7,'x'),4,'Main entry small gable canopy visible in restored front photograph')
add('Side kitchen gable',gable(W-.12,W+80*K+.3,240*K-.25,355*K+.25,2.72,3.4),4,'Restored aerial and roof plan show small projecting gable')
add('Rear east service gable',gable(805*K-.2,W+.25,406*K-.1,510*K+.2,2.72,3.4,'x'),4,'Small outer service roof from roof restoration drawing, partly obscured in current photos')
add('Rear western gable',gable(-50*K-.25,.1,205*K-.1,305*K+.2,2.72,3.3),4,'Rear small roof shape from restoration drawing; not individually current-photo verified')
# Coarse roof courses and timber-faced entry gable, visible defining features.
for n,x0,x1,y0,y1,z0,z1 in roofspec:
 d=min((y1-y0)/2,(x1-x0)/2)
 for z in np.arange(z0+.12,z1-.08,.18):
  q=d*(z-z0)/(z1-z0);xx0,xx1=x0+q,x1-q;yy0,yy1=y0+q,y1-q
  for a,b in [([xx0,yy0,z+.018],[xx1,yy0,z+.018]),([xx0,yy1,z+.018],[xx1,yy1,z+.018]),([xx0,yy0,z+.018],[xx0,yy1,z+.018]),([xx1,yy0,z+.018],[xx1,yy1,z+.018])]:
   add(n+' coarse tile course',beam(a,b,.025),4,'Approximate raised tile-course rhythm, not individual roof tiles or exact profile')
add('Entry timber gable field',gable(WX-.20,JX+.20,-2.135,-2.09,2.92,3.66,'x'),1,'Restored entry triangular timber face, coarse pattern')
for a,b in [([WX-.24,-2.16,2.91],[(WX+JX)/2,-2.16,3.71]),([(WX+JX)/2,-2.16,3.71],[JX+.24,-2.16,2.91]),([WX,-2.16,2.94],[JX,-2.16,2.94]),([(WX+JX)/2,-2.16,2.94],[(WX+JX)/2,-2.16,3.65])]:
 add('Entry gable timber trim',beam(a,b,.055),2,'Restored entry bargeboards and central timber member; joints simplified')
# All facade panels are opaque; no interior transparency is claimed.
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
# Western two long sash windows and shallow shared hood, clearly visible at front.
for x in [5.0,6.8]:
 window('Western front W1','F',0,x,.80,1.35,1.85,3,6,'W1 table185x80cm interpreted as height x width; placement from restored front photo')
add('Western window shared hood',shed(4.43,7.37,-.38,.04,3.38,3.5),2,'Restored front has a shared narrow timber hood above two tall windows')
# Main entrance recessed door between two porch posts.
window('Main entry glass door','F',-.13,(WX+JX)/2,1.45,.4,2.15,4,4,'Restored main entrance timber glazed door; exact leaf dimensions unmeasured')
panel('Main entry lower timber door panels','F',-.13,(WX+JX)/2-.725,(WX+JX)/2+.725,.4,1.35,.17,1,'Front photo lower solid door leaves; coarse panel rhythm')
for offset in [-.725,-.48,-.24,0,.24,.48,.725]:
 q=(WX+JX)/2+offset
 panel('Main entrance lower leaf stile','F',-.13,q-.025,q+.025,.41,1.34,.21,2,'Restored front double door central leaf boundary and narrow lower vertical divisions; coarse simplified pattern')
panel('Main entrance central meeting stile','F',-.13,(WX+JX)/2-.035,(WX+JX)/2+.035,.41,2.53,.22,2,'Visible central separation of double door, not one continuous panel')
window('Main entry transom','F',-.14,(WX+JX)/2,2.2,2.63,.27,4,1,'Front photo upper horizontal glazing above door')
# Japanese facade: grille bays and a broad central glazed group, not western-style sash.
for x,w in [(12.15,1.7),(15.45,3.4),(19.35,1.9)]:
 window('Japanese front sliding group','F',40*K,x,w,1.25,1.3,round(w/.42),3,'Restored front lattice/window pattern; whole-group dimensions photo-proportioned')
 window('Japanese front upper lights','F',40*K,x,w,2.68,.34,max(2,round(w/.42)),1,'Restored front independent upper transom row, photo-proportioned')
 panel('Japanese front lower timber panels','F',40*K,x-w/2,x+w/2,.75,1.2,.14,1,'Restored front lower timber skirt under sliding windows')
 if x!=15.45:shutter('Japanese front grille','F',40*K,x,w,1.25,1.3,round(w/.14),'Restored front dark vertical grille in outer bays')
# Raised L-shaped glazed rear corridors: thin solid-backed wall atop deck; clearance stays open.
for name,side,plane,u0,u1 in [('Western rear','B',264*K,0,WX),('Japanese return','L',WX,264*K,455*K),('Japanese rear','B',455*K,WX,805*K)]:
 panel(name+' lower skirt',side,plane,u0,u1,.70,1.22,.12,1,'Current courtyard photo shows timber lower skirt on raised veranda')
 window(name+' glazed veranda',side,plane,(u0+u1)/2,u1-u0-.15,1.22,1.28,max(2,round((u1-u0)/.55)),3,'Current courtyard photo plus reconstruction-plan opening extent; unseen stretches inferred')
 window(name+' upper lights',side,plane,(u0+u1)/2,u1-u0-.15,2.65,.35,max(2,round((u1-u0)/.55)),1,'Courtyard photo upper horizontal transom row')
 # Coarser structural bays interrupt the fine sash grid, as in courtyard photographs.
 for u in np.arange(u0+.03,u1,.0+1.75):
  panel(name+' veranda main post',side,plane,float(u),float(u)+.09,.69,3.08,.19,2,'Restored courtyard has visible substantial posts separating sash bays; spacing estimated')
 panel(name+' transom separator',side,plane,u0,u1,2.53,2.64,.18,2,'Distinct horizontal member separates main glazing and upper lights')
# Exposed vertical-board waist between Japanese main roof and low eaves.
for side,plane,u0,u1 in [('F',40*K,JX,W),('B',406*K,WX,W),('R',W,40*K,406*K),('L',WX,205*K,406*K)]:
 panel('Japanese upper timber waist',side,plane,u0,u1,3.35,3.85,.06,1,'Restored photos show a clear vertical timber band between main roof and lower eaves; height estimated')
 for u in np.arange(u0+.04,u1-.04,.22):panel('Waist vertical board joint',side,plane,float(u),float(u)+.02,3.36,3.83,.085,2,'Coarse vertical board rhythm on raised eave waist')
# Side/rear openings supported by reconstruction plan; counts/placement approximate where not photographed.
for yy in [1.0,3.2]:window('Western end W1','L',0,yy,.8,1.35,1.85,3,6,'W1 exterior window type from table; end positions inferred from official plan')
for yy,w in [(2.2,2.65),(4.1,1.5)]:window('Japanese side group','R',W,yy,w,1.12,1.43,4,4,'W2 type with side opening extent inferred from proposed plan')
window('Side projecting entrance','R',W+80*K,297.5*K,1.55,.55,1.95,4,4,'Small side entrance from plan and restored aerial; approximate panel pattern')
window('Rear service high window','B',510*K,865*K,1.15,1.6,.61,4,2,'W3 small service ventilation type inferred from official plan; no complete current rear photo')
window('Western rear service window','L',-50*K,250*K,1.0,1.5,.8,3,2,'Small rear projection opening inferred; exact window detail unknown')
# Coarse exterior siding, two construction characters distinguished by vertical battens on Japanese wing.
for side,plane,u0,u1,zmax in [('F',0,0,WX,3.9),('L',0,0,205*K,3.9),('F',40*K,JX,W,3.25),('R',W,40*K,406*K,3.25),('B',406*K,415*K,805*K,3.25)]:
 for zz in np.arange(.86,zmax,.24):panel('Rainboard course',side,plane,u0+.025,u1-.025,float(zz),float(zz)+.022,.027,2,'Coarse timber rainboard lines; not individual measured joints')
for xx in np.arange(JX+.08,W,.42):panel('Japanese vertical siding batten','F',40*K,float(xx),float(xx)+.025,.75,3.25,.038,2,'Japanese wing batten siding differs from western horizontal boards; coarse positions')
# Plinth ventilation slots as dark shallow recess proxies.
for x in [1.4,3.2,5.,6.8]:panel('Western plinth vent','F',0,x-.19,x+.19,.17,.40,.028,7,'Restored facade has low rectangular vents; solid-backed approximation')
for x in [12.0,14.2,16.5,19.1]:panel('Japanese base vent','F',40*K,x-.22,x+.22,.16,.48,.028,7,'Japanese exposed brick base vents, approximate spacing')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Taichung Prison Warden Residence exterior approximation');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Restored warden residence exterior approximation from proposed reconstruction drawings and partial current photos; unseen rear openings inferred, not measured as-built. No interior/garden/trialprint.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
