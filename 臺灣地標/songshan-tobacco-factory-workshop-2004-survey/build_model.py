#!/usr/bin/env python3
"""Source-qualified Songshan workshop exterior study; exact and inferred controls distinguished."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=10/3;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.60;L=83.461;NORTH=18.013;W=12.77;CORRIDOR=2.727;EAVE=4.60;RIDGE=8.10
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':e}for i,(n,c,e) in enumerate([
('Survey wall proxy','#BDB5A3','PDF118 wall surfaces and deterioration; display color uncalibrated, structural descriptions conflict'),
('Bands and frame','#D0C6B2','PDF282–283 visible horizontal courses and external framing; approximate sections'),
('Pitched roof proxy','#62675B','PDF283 roof surface stippling/hatching; coarse finish proxy, not281 structural grid copied outside'),
('Joinery frame','#625C4F','Survey altered door/window formsPDF118/283; not asserted original intact joinery'),
('Opaque glazing','#83948E','Solid display panes; no full interiors'),
('Dark panel or recess','#343934','Dark lower panels and louver backing, opaque simplified condition'),
('Wood corridor supports','#797262','PDF60/71 timber western corridor, posts and braces; sections enlarged at1:300'),
('Low addition roof','#A8A695','PDF281–283 north flat-roof addition; approximate uncalibrated finish'),
('Authored display support','#D1CABB','Flat authored base, not surveyed topography'),
('Roof-cap proxy','#858779','Four externally visible capped roof silhouettes283; uncertain purpose, not claimed smokestacks')])]
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

ev='Official2004-01 surveyPDF281–283; exterior study,1939/1940 source dates conflict; heights approximate±3% graphical20m scale'
bx('Authored flat support',[-3.2,-3.5,-BASE],[L+1.0,W+3.5,0],8,'2mm display base at1:300, not surveyed land or underground footing')
bx('Main long hall solid envelope',[NORTH,0,0],[L,W,EAVE],0,ev+'; solid fill deliberately omits rooms and trusses')
bx('Northern five-bay addition envelope',[0,0,0],[NORTH,W,4.83],0,'PDF281–283 five-bay low north addition, not assumed original phase; wall/roof heights raster-estimated')
bx('North broad flat roof',[-2.3,-2.727,4.80],[NORTH+.13,W+2.6,5.0],7,'PDF281 roof outline and282 north elevation broad flat canopy; cantilever extents estimated, no unsupported engineering claim')
JOIN=NORTH+10.908+34.542
for a,b in [(NORTH,JOIN),(JOIN,L)]:add('Main longitudinal gable roof',gable(a-.08,b+.08,-.30,W+.30,EAVE-.035,RIDGE),2,ev+'; two abutting roof portions, no invented monitor or hipped ends')
for xx in [NORTH,JOIN]:
 add('Raised transverse roof-end separator',gable(xx-.075,xx+.075,-.36,W+.36,EAVE-.04,RIDGE+.22),1,'PDF282–283 raised thin cross-roof separator/end lines; geometry profile inferred from gable roof, not tall freestanding pillar')
# Exterior strips follow actual gable surface, not the roof-framing cross grid in281.
for x in np.arange(NORTH+.35,L,.50):
 for y in [-.30,W+.30]:add('Coarse roof fall-line seam',beam([float(x),y,EAVE+.025],[float(x),W/2,RIDGE+.025],.035,8),2,'PDF283 dense roof texture simplified as coarse surface seams; count not a measured tile inventory')
# Normalize only sub-bay ratios to independently legible group chain, preserving inconsistencies in docs.
groups=[([4.127,3.721,3.060],10.908),([4.248]+[3.721]*7+[4.248],34.542),([2.727,3.636],6.363),([3.409]*4,13.635)]
bounds=[NORTH]
for widths,total in groups:
 for q in widths:bounds.append(bounds[-1]+q*total/sum(widths))
assert len(bounds)==19 and abs(bounds[-1]-L)<1e-7
centers=[(a+b)/2 for a,b in zip(bounds[:-1],bounds[1:])]
# WEST open timber corridor, distinct from main wall, no solid low corridor mass.
add('West open corridor lean-to roof',hull([[NORTH,-CORRIDOR,2.78],[L,-CORRIDOR,2.78],[NORTH,.05,3.53],[L,.05,3.53],[NORTH,-CORRIDOR,2.90],[L,-CORRIDOR,2.90],[NORTH,.05,3.65],[L,.05,3.65]]),2,'PDF60/71 wood corridor,282 south screen-left and283 west braces confirmWEST; inner3.6m/outer2.85m approximate')
bx('West corridor narrow raised walk',[NORTH,-CORRIDOR-.10,0],[L+.08,.08,.10],1,'Low walkway proxy joins open posts, not filled enclosed annex')
bx('West corridor outer longitudinal beam',[NORTH,-CORRIDOR-.10,2.55],[L,-CORRIDOR+.10,2.85],6,'PDF283 western eave beam, member depth enlarged for model')
for i,x in enumerate(bounds):
 bx('West corridor post',[x-.10,-CORRIDOR-.10,.05],[x+.10,-CORRIDOR+.10,2.86],6,'PDF281/283 external post rhythm aligned approximately to bay divisions;200mm proxy section')
 for sign in [-1,1]:
  if x+sign*.68<NORTH or x+sign*.68>L:continue
  add('West corridor diagonal brace',beam([x,-CORRIDOR,1.98],[x+sign*.68,-CORRIDOR,2.65],.085,8),6,'PDF283 paired short timber brackets, enlarged at1:300')
# Main wall course lines and face uprights. Continuous upper sash band remains above corridor.
for side,plane in [('W',0),('E',W)]:
 for z in [.40,1.32,2.52,3.55,4.32]:panel('Long facade course',side,plane,NORTH,L,z,z+.075,.055,1,'PDF283 horizontal facade divisions; heights approximate')
 for x in bounds:panel('Main bay upright',side,plane,x-.085,x+.085,0,EAVE,.095,1,'PDF281/283 main eighteen-bay structural rhythm; sections enlarged')
for side,plane in [('N',NORTH),('S',L)]:
 for z in [.45,1.34,2.52,3.55,4.32]:panel('Main end wall course',side,plane,0,W,z,z+.075,.07,1,'PDF282 gable end facade horizontal divisions')
 # Main gable ends are wall, not roof texture.
 aa,bb=(plane-.09,plane+.02)if side=='N'else(plane-.02,plane+.09)
 add('Main triangular gable wall',hull([[aa,0,EAVE],[aa,W,EAVE],[aa,W/2,RIDGE-.04],[bb,0,EAVE],[bb,W,EAVE],[bb,W/2,RIDGE-.04]]),0,'PDF282 end gables; opaque envelope, not exposed truss reconstruction')
# Generic tall industrial glazed opening: not blanket-labelled a door.
def industrial(name,side,plane,u,w=2.20):
 panel(name+' dark lower panel',side,plane,u-w/2,u+w/2,.20,1.13,.115,5,'PDF283 black lower fields; opaque proxy, not confirmation all are intact door leaves')
 win(name+' upper multi-pane field',side,plane,u,w,1.15,2.0,4,4,'PDF282–283 tall multi-pane industrial joinery; approximate four-by-four glazing, fine damage excluded')
def bandopening(name,side,plane,u,w=2.72):
 panel(name+' dark field',side,plane,u-w/2,u+w/2,.20,3.00,.10,5,'PDF118 later changes;283 wide horizontal-band openings, purpose/operation unconfirmed')
 for z in [.32,1.20,2.02,2.82]:panel(name+' horizontal infill band',side,plane,u-w/2,u+w/2,z,z+.15,.18,1,'283 broad altered horizontal infill bands; not asserted working roller shutter or original window')
for side,plane,altered in [('W',0,{1,4,15}),('E',W,{4,10,15})]:
 for i,u in enumerate(centers):
  if side=='E' and i in [12,13]:
   if i==12:
    panel('East bay12 small offset door','E',W,u-.28,u+.48,.02,2.05,.11,3,'PDF283 east small side-set door in narrow bay12; placement schematic, not north nursery joinery')
    for z in [.55,1.15,1.75]:panel('East small door horizontal field','E',W,u-.22,u+.42,z,z+.09,.18,1,'PDF283 approximate narrow door pattern')
   # bay13 is relatively blank wall, not a mirrored western door pair.
  elif side=='W' and i in [12,13]:
   w=1.20 if i==12 else 1.65
   panel(f'West bay{i} narrow door field',side,plane,u-w/2,u+w/2,.02,3.05,.11,3,'PDF283 west two dissimilar narrow glazed door groups, not mirrored east')
   win(f'West bay{i} narrow door upper',side,plane,u,w-.18,1.03,1.82,2,3,'PDF283 approximate narrow glazed door group')
   for z in [.12,.54]:panel('West narrow door lower inset',side,plane,u-w/2+.09,u+w/2-.09,z,z+.28,.17,1,'Schematic opaque lower field')
  elif i in altered:bandopening(f'{side} main altered bay{i}',side,plane,u)
  else:industrial(f'{side} main tall opening bay{i}',side,plane,u)
  win(f'{side} main high transom bay{i}',side,plane,u,min(2.0,bounds[i+1]-bounds[i]-.45),3.80,.48,4,1,'PDF283 upper small-light strip, approximate four-light units; no original intact glass claim')
# Five bays of north flat addition, offset doors on E/W. North end has three glazed bays.
ann=[NORTH*(i+.5)/5 for i in range(5)]
for side,plane,doorindex in [('W',0,2),('E',W,1)]:
 for i,u in enumerate(ann):
  panel('North addition bay upright',side,plane,i*NORTH/5-.11,i*NORTH/5+.11,0,4.80,.12,1,'PDF281/283 five north addition bays; widths normalized to18.013m overall')
  if i==doorindex:
   panel(f'{side} addition door field',side,plane,u-1.10,u+1.10,.02,2.70,.10,3,'PDF281/283 west middlebay2 and east north-secondbay1 are offset entrances')
   win(f'{side} addition door glazing',side,plane,u,1.95,.55,2.0,2,2,'Approximate addition double glazed entrance')
  else:win(f'{side} addition lower sash bay{i}',side,plane,u,2.85,1.10,1.75,4,2,'PDF283 north addition four-column/two-row lower windows')
  win(f'{side} addition upper transom bay{i}',side,plane,u,2.85,3.35,.85,4,1,'PDF283 north addition upper four-light strip')
for j in range(3):
 u=(j+.5)*W/3
 win(f'North end lower sash{j}','N',0,u,3.55,1.10,1.75,4,2,'PDF282 north addition three glazed bays, four-by-two lower sash')
 win(f'North end upper transom{j}','N',0,u,3.55,3.35,.85,4,1,'PDF282 north end four-light transoms')
for j in range(3):
 industrial(f'South end tall opening{j}','S',L,(j+.5)*W/3,2.10)
 win(f'South end upper transom{j}','S',L,(j+.5)*W/3,3.55,3.8,.48,4,1,'PDF282 south three upper four-light transoms below eave, separate from gable grille')
win('South high rectangular grille','S',L,W/2,2.10,5.25,.82,6,2,'PDF282 south high rectangular ventilation grille, approximately6x2; opaque display grille')
# Two opposed LONG shed-type louver dormers. 281 is framing plan; internal members not shown outside.
def roofz(y):return RIDGE-(RIDGE-EAVE)*abs(y-W/2)/(W/2+.30)
for side,yface,yback in [('W',2.10,4.10),('E',W-2.10,W-4.10)]:
 z0=roofz(yface)-.12; fronttop=roofz(yface)+.45; backtop=roofz(yback)+.08
 add(f'{side} long dormer backing',hull([[x,y,z] for x in [21.90,29.50] for y,zs in [(yface,[z0,fronttop-.08]),(yback,[z0,backtop-.08])] for z in zs]),5,'PDF71/282 shed dormer profile; front rise0.45m and back rise0.08m are approximate, not measured dimensions; x21.9–29.5m raster estimate')
 add(f'{side} long dormer cap',hull([[x,y,z] for x in [21.72,29.68] for y,zs in [(yface,[fronttop-.10,fronttop]),(yback,[backtop-.10,backtop])] for z in zs]),2,'Sloping shed cap rises inward and rejoins main roof; simplified thin profile, not flat monitor cap')
 for x in np.arange(22.0,29.45,.40):panel(f'{side} dormer upright',side,yface,float(x)-.05,float(x)+.05,z0+.12,fronttop-.10,.16,1,'Dormer louver divisions approximate, enlarged for1:300')
 for z in np.arange(z0+.20,fronttop-.10,.22):panel(f'{side} dormer horizontal louver',side,yface,21.97,29.43,float(z),float(z)+.075,.16,3,'PDF71 louver form; no exact slat count')
# Only four caps visible in exterior elevations. Eight framing symbols have unverified exterior meaning and are excluded.
for x in [38.5,50.0,72.0,79.0]:
 bx('Visible roof cap shaft proxy',[x-.25,W/2-.25,RIDGE-.10],[x+.25,W/2+.25,RIDGE+.38],9,'PDF283 four externally visible capped profiles; placement/section approximate, unknown function, not asserted chimney')
 add('Visible roof cap hood proxy',gable(x-.38,x+.38,W/2-.38,W/2+.38,RIDGE+.34,RIDGE+.65),9,'Generic cap silhouette from283;281 eight small framing symbols not asserted to be external devices')
# Broad unidentified low frame above north flat roof; no smokestack claim.
for x in [12.3,15.3]:
 for y in [W/2-2.7,W/2+2.7]:bx('North roof raised frame post',[x-.09,y-.09,4.95],[x+.09,y+.09,6.20],1,'PDF282/283 broad low roof-frame/cover, function unconfirmed; approximately3x5.5m plan')
for y in [W/2-2.78,W/2+2.78]:bx('North roof frame side header',[12.2,y-.08,6.02],[15.4,y+.08,6.20],1,'Schematic header joins roof-frame supports')
for a,b,z0,z1 in [(12.1,13.8,6.28,6.07),(13.8,15.5,6.07,6.28)]:
 add('North roof thin shallow V cover',hull([[a,W/2-2.9,z0],[a,W/2+2.9,z0],[b,W/2-2.9,z1],[b,W/2+2.9,z1],[a,W/2-2.9,z0+.10],[a,W/2+2.9,z0+.10],[b,W/2-2.9,z1+.10],[b,W/2+2.9,z1+.10]]),7,'PDF283 low shallow-curved/V-like top profile, approximate solid cover, not functional classification')

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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan workshop surveyed exterior study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'2004-01 surveyed exterior workshop with north low addition, west open corridor, two louver dormers and four visible roof-cap proxies. Source1939/1940 and structural descriptions conflict; no invented resolution. Interior/framing symbols and fine damage omitted; no trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
