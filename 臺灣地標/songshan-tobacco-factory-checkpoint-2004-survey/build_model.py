#!/usr/bin/env python3
"""Scale-bar-qualified exterior study; all source dimensions approximate ±3%."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=20.;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.15;L=4.76;W=5.62;EAVE=2.77;RIDGE=4.32;OVER=.52
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':e}for i,(n,c,e) in enumerate([
('Clapboard proxy','#B2A58A','PDF114 timber fish-scale/clapboard; monochrome source, uncalibrated display color'),
('Timber trims','#C6BBA3','PDF290–291 raised timber framing; member thickness approximated'),
('Tiled roof','#575B55','PDF114 four-slope tiled roof with repairs; coarse tile courses, not exact tile inventory'),
('Timber joinery','#6D6554','PDF290–291 drawn doors/windows; deformed surveyed condition simplified, not guaranteed intact leaves'),
('Opaque glazing','#81918C','Display glazing proxy, not transparent interior'),
('Recess shadow','#343A36','Authored dark backing when needed, not room reconstruction'),
('Exposed utility proxy','#585B50','East elevation utility line schematic; not a working system'),
('Masonry foundation','#A59C8B','PDF290–291 low foundation plinth; hidden below-ground footings omitted'),
('Authored base','#CFC9B8','Flat display support, not surveyed terrain'),
('Masonry exposure proxy','#8C7C66','Small exposed brick areas visible in291; schematic geometry not calibrated decay map')])]
items=[];ops=[];cut_items=[];cut_ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*INTERNAL);b=np.round(np.array(b)*INTERNAL)
 return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original(); ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':ev})
def bx(name,a,b,mat,ev):add(name,box(a,b),mat,ev)
def cut(name,s,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=5;cut_items.append(s);cut_ops.append({'name':name,'material':5,'operation':'subtract','evidence':ev})
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*INTERNAL).tolist())
def beam(a,b,r,seg=12):
 a=np.array(a);b=np.array(b);d=b-a;le=np.linalg.norm(d);z=d/le;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return mf.Manifold.cylinder(le*INTERNAL,r*INTERNAL,r*INTERNAL,seg).transform(np.column_stack([x,y,z,a*INTERNAL]))
def cylinder(x,y,z,h,r1,r2=None,seg=64):return mf.Manifold.cylinder(h*INTERNAL,r1*INTERNAL,(r1 if r2 is None else r2)*INTERNAL,seg).translate([x*INTERNAL,y*INTERNAL,z*INTERNAL])
def gable(x0,x1,y0,y1,z0,z1):return hull([[x0,y0,z0],[x1,y0,z0],[x0,y1,z0],[x1,y1,z0],[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]])
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('W','E'):
  a,b=(plane-depth,plane+.03)if side=='W'else(plane-.03,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.03)if side=='N'else(plane-.03,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def recess(name,side,plane,u,w,z,h,depth,ev):
 # Real 3D recess with explicit author-added blind backing, never closed leaf.
 if side=='W': aa,bb=[u-w/2,plane-.4,z],[u+w/2,plane+depth,z+h]
 elif side=='E': aa,bb=[u-w/2,plane-depth,z],[u+w/2,plane+.4,z+h]
 elif side=='N': aa,bb=[plane-.4,u-w/2,z],[plane+depth,u+w/2,z+h]
 else: aa,bb=[plane-depth,u-w/2,z],[plane+.4,u+w/2,z+h]
 cut(name+' recess cutter',box(aa,bb),ev+'; depth is authored blind-recess proxy, not measured room depth')
 # backing placed deeper than the cutter, intersecting original mass
 backplane=plane+depth+.01 if side in ('W','N')else plane-depth-.01
 panel(name+' dark back surface',side,backplane,u-w/2+.01,u+w/2-.01,z+.01,z+h-.01,.025,5,'Authored dark blind-recess backing, not a door or complete interior; visible depth '+str(depth)+'m')
def win(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' surround',side,plane,u-w/2-.075,u+w/2+.075,z-.075,z+h+.075,.085,3,ev)
 panel(name+' opaque pane',side,plane,u-w/2,u+w/2,z,z+h,.105,4,'Opaque glazing proxy; not restored transparent glass or full interior')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.034,q+.034,z,z+h,.165,3,ev+'; enlarged member width for legibility')
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.034,q+.034,.17,3,ev+'; enlarged member width for legibility')

ev='Official2004-01 reportPDF290–291 scale-bar raster registration±3%;1940 buildingPDF114, not exact original or current restoration'
bx('Authored flat display base',[-.78,-.78,-BASE],[L+.78,W+.78,0],8,'Authored3mm flat support at1:50; not surveyed ground')
bx('Survey foundation envelope',[0,0,0],[L,W,.39],7,ev+'; approximate above-ground plinth, not underground footing')
bx('Timber exterior envelope',[.025,.025,.37],[L-.025,W-.025,EAVE],0,ev+'; solid-backed exterior study; damaged ceiling/interior omitted')
# Hipped roof has FOUR inclined planes, never four vertical gables.
ra=L/2; y0=(W-L)/2+L/2 # ridge runs east-west, lengthW-L
ridge0=L/2;ridge1=W-L/2
add('Four-slope hipped roof',hull([[-OVER,-OVER,EAVE-.04],[-OVER,W+OVER,EAVE-.04],[L+OVER,-OVER,EAVE-.04],[L+OVER,W+OVER,EAVE-.04],[L/2,ridge0,RIDGE],[L/2,ridge1,RIDGE]]),2,ev+'; four-slope roof explicitly describedPDF114; equal slopes and short ridge inferred from projections')
def rz(x,y):return EAVE+(RIDGE-EAVE)*min((x+OVER)/(L/2+OVER),(L+OVER-x)/(L/2+OVER),(y+OVER)/(L/2+OVER),(W+OVER-y)/(L/2+OVER),1.)
# Continuous stepped horizontal cladding, not an invented brick facade.
for side,plane,end in [('N',0,W),('S',L,W),('W',0,L),('E',W,L)]:
 for z in np.arange(.40,EAVE-.08,.145):panel('Horizontal timber board course',side,plane,0,end,float(z),float(z)+.10,.027,0,'PDF114/291 horizontal clapboard; uniform145mm pitch is scan-derived display approximation, losses/deformation not individually measured')
 panel('Timber eave fascia',side,plane,-OVER,end+OVER,EAVE-.095,EAVE+.015,OVER+.035,1,'PDF290–291 eave fascia/overhang; square profile approximation')
 for u in [.10,end-.10]:panel('Corner timber upright',side,plane,u-.055,u+.055,.38,EAVE,.07,1,'PDF291 corner framing; approximate face width')
# Coarse tile-row overlaps follow each hip plane; thin members enlarged for preview.
for k,d in enumerate(np.arange(.10,L/2+OVER,.23)):
 z=EAVE+(RIDGE-EAVE)*d/(L/2+OVER)+.016
 for x in [-OVER+d,L+OVER-d]:add('North south tile overlap row',beam([x,-OVER+d,z],[x,W+OVER-d,z],.022,8),2,'PDF291 curved tile rows simplified continuous ribs; not individual exact tiles')
 for y in [-OVER+d,W+OVER-d]:
  if L+OVER-d>-OVER+d:add('East west tile overlap row',beam([-OVER+d,y,z],[L+OVER-d,y,z],.022,8),2,'PDF291 hipped roof course at approximate230mm spacing')
# Fall-line raised tile seams subdivide each face and stop at ridge/hips.
for y in np.arange(-OVER+.1,W+OVER,.22):
 stop=min(L/2+OVER,y+OVER,W+OVER-y)
 if stop<.08:continue
 for xedge,sign in [(-OVER,1),(L+OVER,-1)]:
  xend=xedge+sign*stop
  add('Tile fall-line seam',beam([xedge,float(y),EAVE+.025],[xend,float(y),rz(xend,float(y))+.025],.018,8),2,'Approximate raised tile joints; source pattern not exact count')
for x in np.arange(-OVER+.12,L+OVER,.22):
 stop=min(L/2+OVER,x+OVER,L+OVER-x)
 for yedge,sign in [(-OVER,1),(W+OVER,-1)]:
  yend=yedge+sign*stop
  add('Hip-end tile fall-line seam',beam([float(x),yedge,EAVE+.025],[float(x),yend,rz(float(x),yend)+.025],.018,8),2,'Approximate tiled hip face pattern')
for x,y,yr in [(-OVER,-OVER,ridge0),(-OVER,W+OVER,ridge1),(L+OVER,-OVER,ridge0),(L+OVER,W+OVER,ridge1)]:
 add('Raised hip ridge tiles',beam([x,y,EAVE+.035],[L/2,yr,RIDGE+.035],.06,12),2,'PDF291 hip ridge caps, profile simplified')
add('Short horizontal ridge cap',beam([L/2,ridge0-.08,RIDGE+.055],[L/2,ridge1+.08,RIDGE+.055],.085,16),2,'PDF291 short east-west ridge, approximate cap to4.46m overall height')
# Small ridge-end circular silhouette proxy; no unsupported detailed ornament claim.
for y in [ridge0-.07,ridge1+.07]:add('Ridge-end tile ornament proxy',beam([L/2,y-.045,RIDGE+.05],[L/2,y+.045,RIDGE+.05],.09,16),2,'PDF291 small end-on ridge tile silhouette; exact decorative carving omitted')
# North: two 2x4 sashes and narrow central glazed door with2x2 transom.
for u in [1.54,4.20]:win('North side window','N',0,u,1.28,.88,1.24,2,4,'PDF291 north two timber sashes; width/height scan-derived, not nursery table')
panel('North door timber field','N',0,2.40,3.35,.02,2.55,.085,3,'PDF291 north narrow drawn door; survey deformation not represented pointwise')
win('North door lower panel','N',0,2.875,.76,.12,.53,1,1,'North opaque timber inset is a panel not glass')
# Override lower-panel face with timber, rather than pretend glazing.
panel('North opaque lower door inset','N',0,2.50,3.25,.14,.63,.175,3,'PDF291 opaque lower door panel')
win('North door upper glazing','N',0,2.875,.77,.73,1.05,2,3,'PDF291 six upper door panes')
win('North door transom','N',0,2.875,.78,1.92,.53,2,2,'PDF291 four-pane north transom, separated from lower leaf')
# South: four narrow central leaves, side sashes, and full upper transom band.
for u in [.82,4.80]:win('South side window','S',L,u,1.13,.78,1.18,2,3,'PDF291 south side sashes; asymmetric widths simplified from drawing')
for j in range(4):
 u=1.845+j*.65
 panel('South narrow timber leaf','S',L,u-.31,u+.31,.02,2.03,.085,3,'PDF291 central four narrow vertical door leaves; shown closed as drawn, not complete intact condition certification')
 win('South leaf upper glazing','S',L,u,.53,1.04,.90,1,2,'PDF291 each narrow south leaf upper two panes')
 for z in [.12,.57]:
  panel('South leaf opaque lower inset','S',L,u-.25,u+.25,z,z+.35,.125,1,'PDF291 lower door fields, opaque timber proxy')
for u,w in [(.82,1.13),(2.17,1.22),(3.47,1.22),(4.80,1.13)]:win('South high transom','S',L,u,w,2.12,.46,2,1,'PDF291 south upper continuous transom rhythm, approximate opening centers')
# East: door and narrow four-light transom. West: raised sash and transom.
panel('East door timber field','E',W,1.69,3.03,.02,2.59,.09,3,'PDF291 east door shown under four-light transom, approximate')
for u in [2.02,2.70]:panel('East opaque lower door inset','E',W,u-.27,u+.27,.12,.68,.14,1,'PDF291 two opaque bottom fields')
win('East door glazing','E',W,2.36,1.18,.81,1.21,2,3,'PDF291 east door upper six-pane field')
win('East narrow transom','E',W,2.36,1.20,2.16,.32,4,1,'PDF291 east four-light transom')
win('West raised sash','W',0,2.43,1.30,1.12,1.27,2,4,'PDF291 west single eight-pane window, sill higher than north/south')
win('West narrow transom','W',0,2.43,1.30,2.48,.17,4,1,'PDF291 west small upper transom; approximate')
# Paired slightly bending east utility lines; no unsupported functional claim.
for delta in [0,.035]:
 for p,q in [([L-3.36-delta,W+.07,.12],[L-3.30-delta,W+.07,1.22]),([L-3.30-delta,W+.07,1.22],[L-3.39-delta,W+.07,2.69])]:add('East surface utility line',beam(p,q,.02,8),6,'PDF291 east irregular vertical lines, routing schematic; source unclear function')
# Small visibly exposed masonry patches, schematic rather than exact damage facsimile.
for side,plane,u in [('N',0,W-.20-.375),('S',L,.16),('W',0,.65),('E',W,L-.65-.375)]:
 for row in range(3):
  for j in range(3-row):
   panel('Schematic exposed brick at plinth',side,plane,u+j*.13,u+j*.13+.115,.025+row*.09,.10+row*.09,.045,9,'PDF291 exposed brick shapes at foundation; authored coarse indication, not measured crack/loss map')

# All boolean cuts preserve missing apertures; no detailed interior room layout is implied.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
if cut_items:s=s-mf.Manifold.batch_boolean(cut_items,mf.OpType.Add)
pre_simplify_components=[{'volume_mm3':q.volume()*SCALE**3,'bounds_internal':q.bounding_box()}for q in s.decompose()]
s=s.set_tolerance(.5).simplify(.5)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda x:'{'+ns+'}'+x
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan inspection station surveyed-envelope study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.8f}'for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
files={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>','3D/3dmodel.model':ET.tostring(root,encoding='utf-8',xml_declaration=True)}
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED)as z:
 for name,blob in files.items():
  zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,blob)
parts=[]
for op,item in zip(ops+cut_ops,items+cut_items):
 q=item.to_mesh64();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops+cut_ops},indent=2))
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'1940 inspection station as documented in2004-01; approximate scale-bar exterior, hipped tiled roof and asymmetric timber joinery. Later canopy/queue rails and interior excluded; no exact damage replication or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
