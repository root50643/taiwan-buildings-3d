#!/usr/bin/env python3
"""Beidou governor residence restored-main-body exterior study; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('plaster','Rendered foundations','#C6C4B9','Restoration elevations and official post-restoration front photograph, uncalibrated'),('wood','Timber siding','#8F704D','Restoration drawing timber panels and official tourism photograph'),('frame','Timber frames','#72563B','Restoration drawing window frames, coarse approximation'),('glass','Opaque glass proxy','#789398','Opaque proxy; no interior visibility'),('roof','Cement roof tiles','#626965','Restoration roof plan and elevation; coarse tile rhythm'),('base','Authored support','#B9B6A9','Author-created display support, not actual terrain'),('white','Rendered infill','#D9D8CC','Restoration drawings and observed entrance plaster infill'),('dark','Recess backing','#3C3932','Solid-backed recess proxy'),('brick','Foundation stone','#99978B','Restoration foundation and porch stone feet simplified')]]
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
# Restored plan axis control dimensions in meters, not eaves-inclusive outline.
W=13.68;D=7.295
bx('Authored display support',[-1.4,-2.9,-.6],[15.2,11.3,0],5,'Display base only; gardens and site terrain excluded')
bx('Main raised foundation',[0,0,0],[W,D,.55],0,'Restoration elevations foundation GL+55cm; floor finishes vary by room')
add('Main timber body',box([0,0,.55],[12.765,D,4.115])-box([3.645,-.1,.45],[6.38,.55,3.0]),1,'Restoration main room envelope; front entrance recessed, axes not entire roof outline')

bx('East service strip',[12.765,0,.55],[13.68,5.47,3.23],1,'Restoration east service-room strip beneath lower eave')
bx('East kitchen projection',[13.68,3.13,0],[14.32,5.47,3.23],0,'Restoration kitchen east projection 64cm, not attached red-brick outbuilding')
# Raised verandas: underfloor voids and stone feet retained, not solid filled plinth.
for name,x0,x1,y0,y1 in [('South veranda',6.38,13.68,-1.82,0),('North veranda',0,12.765,D,D+1.0)]:
 bx(name+' raised floor',[x0,y0,.68],[x1,y1,.83],1,'Restoration floor +83cm, visible undercroft retained')
 outer_y=y0 if name=='South veranda' else y1-.30
 for x in np.linspace(x0+.1,x1-.1,7):
  bx(name+' stone foot',[x-.13,outer_y+.02,0],[x+.13,outer_y+.28,.25],8,'Simplified stone pier/foot, approximate individual placement')
  bx(name+' underfloor support',[x-.07,outer_y+.08,.20],[x+.07,outer_y+.22,.70],2,'Restoration elevated veranda support; no full structural certification')
# Rear sanitary wing distinct lower gabled roof and plaster base.
bx('North toilet base',[10.02,D+1,0],[12.765,D+3.11,.55],0,'Restoration northern sanitary projection from plan,211cm beyond veranda')
bx('North toilet walls',[10.02,D+1,.55],[12.765,D+3.11,2.80],1,'Restoration rear toilet main walls and small exterior window')
# Front projecting bay and entrance tread levels.
bx('West reception window bay',[.4,-.56,.55],[3.32,0,2.92],1,'Restoration front west projecting reception bay, not a flat wall')
for j,z in enumerate([.16,.32,.47]):bx('Front entrance steps',[3.67,-1.1+j*.28,0],[6.35,.55,z],0,'Approximate three-step entrance to drawing+47cm depressed entry')
for x in [3.645,6.38]:bx('Entrance porch upright',[x-.08,-.5,.47],[x+.08,.12,3.40],2,'Recessed entrance timber jambs and outer porch uprights seen in restored official photograph')
window('Recessed front double door','F',.55,5.0125,1.90,.47,2.05,4,4,'Official asset text entrance190cm; restoration/official photograph double door, coarse panes')
panel('Entrance lower timber door panels','F',.55,4.0625,5.9625,.47,1.05,.18,1,'Official restored photograph lower solid double-leaf panels')
panel('Entrance central stile','F',.55,4.99,5.035,.47,2.53,.20,2,'Visible double-leaf center separation')
window('Entrance upper light','F',.55,5.0125,1.90,2.62,.38,4,1,'Separate transom above entrance seen in restored official photograph')
for x0,x1 in [(3.645,4.03),(5.99,6.38)]:panel('Entrance white infill','F',.54,x0,x1,2.1,3.05,.12,6,'White plaster infill flanking door upper portion, official restored photo')
# Veranda transparent areas represented with opaque recessed glass; room interiors omitted.
window('South veranda glazing','F',-1.82,10.03,6.86,1.18,1.60,12,3,'Restoration front elevation and official restored photo; coarse pane rhythm')
panel('South veranda lower board','F',-1.82,6.6,13.46,.83,1.18,.15,1,'Distinct timber lower boards below veranda glass')
for x in np.linspace(6.6,13.46,13):panel('South lower board joint','F',-1.82,x-.015,x+.015,.83,1.18,.18,2,'Coarse timber panel rhythm')
window('North veranda glazing','B',D+1,5.14,9.80,1.18,1.60,16,3,'Restoration rear elevation drawing; no complete current rear photo verified')
panel('North veranda lower board','B',D+1,.24,10.02,.83,1.18,.15,1,'Restoration rear window lower timber panel band')
window('West bay front glazing','F',-.56,1.86,2.70,1.02,1.81,6,4,'Restoration front projecting bay; official post-restoration photograph window family')
for side,u in [('L',.4),('R',3.32)]:window('Reception bay return',side,u,-.28,.44,1.02,1.81,1,4,'Restoration bay return glazing; coarse interpretation')
panel('South veranda white upper band','F',-1.82,6.6,13.46,2.78,3.23,.17,6,'Official post-restoration photograph clear white band over front veranda glazing')
panel('Entrance white upper infill','F',.54,4.04,5.98,3.01,3.23,.14,6,'Visible restored entrance white upper infill above separate transom; not inferred extra storey')
# Other faces based on the lower repair-elevation panels, not old upper panels.
window('West main side window','L',0,1.6,2.6,1.1,1.6,4,4,'Restoration west elevation single principal window; approximate location from plan')
window('East south room window','R',13.68,.88,1.45,1.05,1.55,3,3,'Restoration east elevation foreground room window')
window('East service double door','R',13.68,2.40,1.1,.55,2.0,2,3,'Restoration east access door; reduced coarse sash')
for j in range(3):bx('East doorway steps',[13.67+j*.23,1.8,0],[14.35,3.0,.55-j*.17],0,'Restoration east door level change, simplified treads')
window('East kitchen raised window','R',14.32,4.3,1.35,1.35,1.05,2,2,'Restoration east projecting kitchen window, based on lower elevation')
for z0,z1 in [(2.48,3.15),(.72,1.22)]:
 panel('East kitchen louver dark backing','R',14.32,3.25,5.35,z0,z1,.10,7,'Repair east elevation kitchen louver bands, solid-backed approximation')
 for z in np.arange(z0,z1,.12):panel('East kitchen horizontal louver','R',14.32,3.25,5.35,float(z),float(z)+.045,.17,2,'Coarse horizontal louver blades, not transparent ventilation or exact count')
window('Toilet north window','B',D+3.11,11.7,.85,1.50,.65,2,1,'Restoration rear sanitary small window, drawing-derived')
window('Toilet east window','R',12.765,D+2.1,.75,1.45,.65,2,1,'Restoration side sanitary opening, approximate drawing placement')
# Wall boards and facade horizontal / vertical framing.
for z in np.arange(.75,4.08,.23):
 panel('South main rainboard joint','F',0,0,3.64,float(z),float(z)+.018,.035,2,'Coarse visible horizontal timber siding; no individual construction joints')
 panel('West main rainboard joint','L',0,0,D,float(z),float(z)+.018,.035,2,'Restoration west timber wall siding')
for z in np.arange(.75,2.75,.23):panel('North toilet rainboard joint','B',D+3.11,10.02,12.765,float(z),float(z)+.018,.035,2,'Restoration sanitary-wing siding')
# Main irimoya: lower hipped skirt + upper gable, rather than a plain hip or gable box.
x0,x1,y0,y1=-.50,13.285,-.60,8.815
xb0,xb1=x0+1.50,x1-1.50;yb0,yb1=y0+1.50,y1-1.50
ze,zb,zr=4.115,4.72,6.015
corners=[[x0,y0,ze],[x1,y0,ze],[x1,y1,ze],[x0,y1,ze]]
inner=[[xb0,yb0,zb],[xb1,yb0,zb],[xb1,yb1,zb],[xb0,yb1,zb]]
for i in range(4):
 q=[corners[i],corners[(i+1)%4],inner[(i+1)%4],inner[i]]
 add('Main hipped roof skirt',hull(q+[[x,y,z-.16] for x,y,z in q]),4,'Restoration roof/elevations irimoya lower hipped skirt; slope transition approximated')
add('Main upper gable roof',gable(xb0-.08,xb1+.08,yb0-.03,yb1+.03,zb-.025,zr)-gable(xb0-.2,xb1+.2,yb0-.03,yb1+.03,zb-.185,zr-.16),4,'Restoration two-gable upper roof, overall ridge GL601.5cm; transition approximated')
for x,side in [(xb0,'L'),(xb1,'R')]:
 add('Restored plaster irimoya gable field',gable(x-.045,x+.045,yb0,yb1,zb-.03,zr-.12),6,'Lower repaired side elevations show light rendered gable, unlike old upper-panel timber siding; not swallowed by roof')
 cy=(y0+y1)/2;cz=5.35
 for name,rad,depth,mat in [('Six-sided window frame',.30,.10,6),('Six-sided opaque light',.235,.13,3)]:
  pts=[]
  for off in [-.025,depth]:
   xx=x+(-off if side=='L' else off)
   for t in np.linspace(0,2*math.pi,6,endpoint=False):pts.append([xx,cy+rad*math.sin(t),cz+rad*math.cos(t)])
  add(name,hull(pts),mat,'Official asset text and restoration side elevations show hexagonal gable window; opaque coarse proxy')
 panel('Hexagonal window center bar',side,x,cy-.018,cy+.018,cz-.23,cz+.23,.16,2,'Coarse six-sided window division')
 for sign in [-1,1]:
  xx=x+(-.145 if side=='L' else .145)
  add('Hexagonal window diagonal division',beam([xx,cy-.195,cz-sign*.1125],[xx,cy+.195,cz+sign*.1125],.025),2,'Restoration side elevation hexagonal window three-axis radial division, coarse proxy')
add('Main ridge cap',beam([xb0-.12,(y0+y1)/2,zr+.03],[xb1+.12,(y0+y1)/2,zr+.03],.08),4,'Restoration ridge cap; elaborate decorative carving omitted')
# Coarse ridge end ornaments only; no invented carved emblems.
for x in [xb0-.08,xb1+.08]:
 add('Simplified raised ridge end',beam([x,(y0+y1)/2,zr],[x,(y0+y1)/2,zr+.20],.10),4,'Restoration ridge-end raised silhouette, detailed tile carving simplified')
# Veranda copper/metal lower roofs, supported front canopy columns.
add('South veranda metal roof',shed(6.28,14.0,-2.22,.15,3.25,3.68),4,'Restoration roof plan and observed restored photo lower metal canopy; roof elevation estimated to retain visible white wall band')
add('Entrance shallow canopy',shed(3.48,6.42,-1.02,.20,3.35,3.48),2,'Restoration/official photograph porch canopy above recessed entrance; canopy height estimated, not a transcribed dimension')
add('Reception bay hood',shed(.28,3.48,-.80,.08,2.96,3.17),2,'Restoration front bay independent rain hood')
add('North veranda metal roof',shed(-.25,12.98,D-.1,D+1.3,3.62,3.00),4,'Restoration roof plan rear veranda low metal roof, not modern photo-verified')
add('East low roof',shed(12.55,14.55,-.20,5.8,3.55,3.20,axis='x'),4,'Restoration east service eave lower than main roof')
add('North toilet gable roof',gable(9.78,13.00,D+.88,D+3.4,2.88,3.42,axis='x'),4,'Restoration rear sanitary projection shallow gabled roof')
for x in [6.45,10.0,13.85]:
 bx('South canopy stone foot',[x-.15,-2.02,0],[x+.15,-1.72,.25],8,'Restored photograph canopy column stone base simplified')
 bx('South canopy timber post',[x-.065,-1.93,.22],[x+.065,-1.80,3.27],2,'Visible front canopy posts, not substituted with solid veranda plinth')
# Broad visible wall belt below main eave.
for side,plane,u0,u1 in [('F',0,0,12.765),('B',D,0,12.765)]:
 panel('Main upper timber belt',side,plane,u0,u1,3.25,4.10,.08,1,'Restoration upper timber wall band below high roof')
 for u in np.arange(u0,u1,.91):panel('Upper belt vertical division',side,plane,float(u),float(u)+.035,3.25,4.10,.12,2,'Coarse timber belt panels matching restoration facade rhythm')

# Coarse transverse tile rows on major slopes; not every individual tile shape.
for t in np.linspace(.07,.95,9):
 z=zb-.025+(zr-(zb-.025))*t
 for y in [yb0-.03+((y0+y1)/2-yb0+.03)*t,yb1+.03-((y0+y1)/2-yb0+.03)*t]:
  add('Coarse upper roof tile row',beam([xb0-.065,float(y),float(z)+.005],[xb1+.065,float(y),float(z)+.005],.035),4,'Coarse tile row rhythm; individual concave tile profile omitted')
for t in [.18,.43,.68,.9]:
 z=ze+(zb-ze)*t;xa=x0+(xb0-x0)*t;xx=x1+(xb1-x1)*t
 for y in [y0+(yb0-y0)*t,y1+(yb1-y1)*t]:add('Coarse skirt tile row',beam([xa,float(y),z+.005],[xx,float(y),z+.005],.035),4,'Simplified hipped skirt tile course; not exact tile count')

bx('Concealed roof support core',[1.4,1.0,4.0],[11.4,7.1,4.75],1,'Authored hidden print support connecting roof shell, not reconstructed historic truss or interior')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Beidou governor residence restoration-report main-body exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Restoration-report main residence including veranda and sanitary wing only. Excludes gardens, boundary walls, separate red-brick outbuilding and interiors. Non-photographed faces derived from restoration elevations; no trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
