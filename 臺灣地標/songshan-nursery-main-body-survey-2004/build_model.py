#!/usr/bin/env python3
"""Songshan nursery main body: 2004-01 report surveyed-envelope study, not a restored or damage-exact replica."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=6.0
INTERNAL=1000.0
SCALE=MODEL_MM_PER_METRE/INTERNAL
L=22.48
SIDE_DEPTH=12.40
REAR_DEPTH=13.45
FLOOR=.51
EAVE=3.65
RIDGE=5.455  # tile surface;0.075m cap reaches annotated5.53m outer crest
BASE=.50
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('plaster','Foundation and plaster proxy','#BDB8A8','PDF121 reinforced brick and cracked lower plaster; neutral uncalibrated tone, fine damage omitted'),
 ('wood','Weatherboard proxy','#7F8C7A','PDF121 fishscale timber cladding; schematic muted green, not a color-calibrated or restored finish'),
 ('frame','Timber joinery proxy','#5A5140','PDF288–289 timber window rhythms and PDF341 dimensions; illustrative brown, glazing opaque'),
 ('glass','Opaque glazing proxy','#829695','Solid-backed glazing; no optical transparency or interior reconstruction'),
 ('tile','Survey-period tile roof proxy','#55574C','PDF286–289 tile roof geometry and PDF122 tile damage; coarse geometry, damage not replicated'),
 ('base','Authored display base','#C2BFAF','Flat display support, not surveyed terrain; north ground datum adopted'),
 ('sheet','Existing modified roof sheet proxy','#7F837A','PDF286 south central striped roof and PDF124 existing plastic corrugation; not repaired timber'),
 ('dark','Unlit openings and gaps','#373A34','Dark solid-backed apertures or door panels; not fabricated transparent interiors'),
 ('brick','Exposed masonry proxy','#927766','PDF121 reinforced-brick construction and exposed lower masonry; sparse approximate patches'),
 ('fascia','Gallery header and fascia','#A3A48E','PDF288 gallery timber fascia and transom framing, schematic uncalibrated finish')]]
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*INTERNAL);b=np.round(np.array(b)*INTERNAL)
 return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat,evidence):add(name,box(a,b),mat,evidence)
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*INTERNAL).tolist())
def hip(x0,x1,y0,y1,z0,z1):
 d=min((x1-x0)/2,(y1-y0)/2)
 rid=([[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]] if x1-x0>=y1-y0 else [[(x0+x1)/2,y0+d,z1],[(x0+x1)/2,y1-d,z1]])
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]]+rid)
def shed(x0,x1,y0,y1,zlo,zhi,axis='y'):
 zbase=min(zlo,zhi)-.14;pts=[[x0,y0,zbase],[x1,y0,zbase],[x1,y1,zbase],[x0,y1,zbase]]
 pts+=([[x0,y0,zlo],[x1,y0,zlo],[x0,y1,zhi],[x1,y1,zhi]] if axis=='y' else [[x0,y0,zlo],[x0,y1,zlo],[x1,y0,zhi],[x1,y1,zhi]])
 return hull(pts)
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;le=np.linalg.norm(d);z=d/le;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return mf.Manifold.cylinder(le*INTERNAL,r*INTERNAL,r*INTERNAL,12).transform(np.column_stack([x,y,z,a*INTERNAL]))
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('N','S'):
  a,b=(plane-depth,plane+.02)if side=='N'else(plane-.02,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.02)if side=='L'else(plane-.02,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def win(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' surround',side,plane,u-w/2-.055,u+w/2+.055,z-.055,z+h+.055,.075,2,ev)
 panel(name+' opaque glazing',side,plane,u-w/2,u+w/2,z,z+h,.095,3,'Solid-backed opaque glazing; not transparent, not a complete interior')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.025,q+.025,z,z+h,.15,2,ev+'; frame section enlarged for model legibility')
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.025,q+.025,.155,2,ev+'; frame section enlarged for model legibility')
def door(name,side,plane,u,w,z,h,cols,ev):
 panel(name+' frame',side,plane,u-w/2-.06,u+w/2+.06,z,z+h+.06,.09,2,ev)
 panel(name+' panel',side,plane,u-w/2,u+w/2,z+.03,z+h,.055,2,ev+'; door closed for printable envelope')
 win(name+' upper light',side,plane,u,w-.16,z+h*.42,h*.49,cols,2,ev+'; upper glazing schematic')
 for q in [u-w/2+.08,u+w/2-.08]:panel(name+' stile',side,plane,q-.025,q+.025,z+.05,z+h,.18,2,ev)
 panel(name+' lower inset',side,plane,u-w/2+.13,u+w/2-.13,z+.16,z+h*.32,.16,7,'Solid-backed lower door panel, not an opening')
# Coordinate convention: x increases left-to-right in source north elevation, geographically east-to-west.
# y runs from north gallery toward south; source Fig5-68/69 east-west labels conflict with site252.
ev='Official2004-01 report PDF284–289 current measured drawings; construction1954 per PDF121, not1937 original nursery'
bx('Authored flat display base',[-.75,-1.05,-BASE],[25.50,14.60,0],5,'Flat display support; north local GL=0. South drawing GL is0.105m lower and is not reproduced as terrain')
# Continuous raised reinforced-brick base, south central projection distinct from the corner returns.
bx('Main raised plinth',[0,0,0],[L,SIDE_DEPTH,FLOOR],0,ev+';2248cm length;12.40m side wall is raster trace, not1284.3cm projected dimension datum; north GL normalized')
bx('South central projected plinth',[3.30,SIDE_DEPTH,0],[19.18,REAR_DEPTH,FLOOR],0,'PDF284 traced rear wall13.45m versus traced sidewall12.40m; both estimated, not subtraction of1385/1284.3 dimension datums')
# Main room block is solid for printing; front gallery retains its own wall/roof plane.
bx('Main room mass',[0,2.25,FLOOR],[L,8.35,EAVE],1,ev+'; room depth and wall thickness registered approximately to scan, interior omitted')
bx('Drawing-left south corner return',[0,8.30,FLOOR],[3.30,SIDE_DEPTH,EAVE],1,'PDF284/286 left narrow rear return and PDF289 figure5-68; no mirroring of other end')
bx('Drawing-right south corner return',[19.18,8.30,FLOOR],[L,SIDE_DEPTH,EAVE],1,'PDF284/286 right rear toilet/service return; sealed internal openings are not restored')
bx('Existing south central infill',[3.28,8.30,FLOOR],[19.20,REAR_DEPTH,2.74],0,'PDF284/288 current south central modified wall; not1954 conjecture or PDF124 proposed repair')
bx('Hidden roof junction solid backing',[3.28,8.28,2.70],[19.20,8.79,3.70],0,'Authored interior fill under roof intersection for printable solid; not exposed facade or surveyed interior')
# North gallery remains spatially recessed; posts and glazing are separate from room backing.
bx('North gallery floor',[0,0,.44],[L,2.30,.55],0,'PDF284 north gallery floor; wall line not merged with inner room front')
bx('North gallery lower wall',[0,0,.51],[L,.13,1.38],0,'PDF121 gallery photo andPDF288 spalling symbol support continuous opaque lower wall; thickness/sill elevation estimated. Gallery remains2.25m deep behind facade, not a full solid infill.')
bx('North transom opaque board backing',[0,-.015,2.49],[L,.13,3.32],9,'PDF288 vertical timber infill surrounds the six upper transoms; this is solid backing, not additional open ventilation holes')
# Main entrance interrupts the outer gallery window band.
bay=[0,2.98,6.46,9.94,12.44,15.92,19.40,L]
for i,x in enumerate(bay):
 bx(f'North gallery post {i+1}',[x-.075,-.04,.50],[x+.075,.17,3.32],2,'PDF287–288 explicit longitudinal bay chain298/348/348/250/348/348/298cm; post section approximate')
 bx(f'North gallery foot {i+1}',[x-.11,-.08,.45],[x+.11,.21,.73],0,'PDF288 gallery post bases, fine corrosion omitted')
for j,(x0,x1) in enumerate(zip(bay[:-1],bay[1:])):
 if j==3:continue
 u=(x0+x1)/2;w=min(3.30,x1-x0-.20)
 num=j+1 if j<3 else j
 win(f'North gallery window {num}','N',0,u,w,1.43,1.10,4 if w<3 else 5,3,'PDF340/341 Nos1–6:1100x3300mm nominal; edge openings fitted to narrower298cm end bays, discrepancy disclosed')
 win(f'North gallery transom {num}','N',0,u,min(2.10,w-.22),2.64,.60,3,1,'PDF341 type6-1:600x2100mm; repeated upper vents visiblePDF288, placement approximate')
win('North central entry upper light','N',0,11.24,1.80,2.64,.60,3,1,'PDF288 central door upper light within boarded header; approximate dimensions, not an open black void')
for xx in np.arange(.08,L,.20):panel('North header vertical board relief','N',0,float(xx),float(xx)+.03,2.53,3.14,.045,1,'PDF288 vertical boards around transoms; glazing projects farther forward and covers these underlying runs')
# Gallery end closures: explicit door49 at drawing-left,48 at drawing-right.
for side,plane in [('L',0),('R',L)]:
 panel('Gallery end board wall',side,plane,0,2.25,.51,3.26,.06,1,'PDF289 gallery end enclosure distinct from main side wall')
 door('Gallery end door49' if side=='L'else'Gallery end door48',side,plane,1.07,.90,FLOOR,1.95,2,'PDF340/341 No48 wood door1950x900mm; No49 has blank status-table fields and is estimated fromPDF289, not a tabulated dimension')
# Outer paired leaves27/28 and inner door29 are not conflated.
for u,nu in [(11.24-.45,27),(11.24+.45,28)]:door(f'North entry leaf{nu}','N',0,u,.90,FLOOR,1.95,1,'PDF340/341 Nos27/28 wood leaf1950x900mm; surveyed double-leaf entry')
bx('Central entry side return left',[9.94,-.04,.51],[10.34,2.26,3.30],1,'PDF284 central gallery entrance side return, approximate thickness')
bx('Central entry side return right',[12.14,-.04,.51],[12.44,2.26,3.30],1,'PDF284 central gallery entrance side return, approximate thickness')
for i in range(3):
 bx(f'North entry step{i+1}',[10.10,-.83+i*.28,0],[12.30,-.54+i*.28,(i+1)*.17],0,'PDF284/288 central three-step approach,0.51m total rise; tread length approximated')
# Inner-room windows/door represented behind the front gallery, not additional exterior openings.
for j,u in enumerate([1.49,4.72,8.20,14.18,17.66,20.94]):win(f'Inner north sash{12-j}','N',2.25,u,2.50,1.10,1.50,4,3,'PDF340/341 Nos7–12:1500x2500mm; behind north gallery, not an extra storey')
door('Inner north central door29','N',2.25,11.24,1.60,FLOOR,2.10,2,'PDF340/341 No29:2100x1600mm; behind gallery entry')
# Body fascia/roof: one long high hipped roof plus two lower south-return hipped roofs.
# Raw roof depth1377 and plan depth1385 have different/unresolved survey endpoints. Current envelope fit prioritizes wall coverage.
rx0,rx1=-.2175,L+.2175
main_y0,main_y1=2.12,8.76
add('Main long hipped tile roof',hip(rx0,rx1,main_y0,main_y1,EAVE,RIDGE),4,'PDF286 high long hipped main roof and PDF287 ridge502+51cm; roof length2291.5cm; transverse registration estimated')
for name,x0,x1 in [('drawing-left',rx0,3.1625),('drawing-right',19.3175,rx1)]:
 add(f'{name} lower south return hipped roof',hip(x0,x1,5.92,12.74,EAVE,4.545),4,'PDF286 two narrow south returns create lowered secondary ridges; estimated outer cap4.61m, underlying tile plane4.545m')
# Existing south altered sheet roof fills the notch; must not be replaced by a matching tile hip.
add('South existing central single-slope sheet roof',shed(3.1625,19.3175,8.72,13.62,3.72,2.86),6,'PDF286 striped south central roof, PDF287 asymmetric section and PDF124 plastic corrugated replacement recommendation; existing sheet roof retained')
add('North gallery lean-to roof',shed(rx0,rx1,-.15,2.12,3.28,3.71),4,'PDF286 north gallery strip227cm andPDF287 lower pitched cover; eave registration approximated')
bx('Concealed gallery-main roof junction backing',[0,2.09,3.22],[L,2.34,3.72],1,'Authored hidden overlap backing at measured north-gallery/main-roof junction; avoids a model seam, not a new visible roof strip')
# North front fascia and framing, solid relief at printable thickness.
bx('North gallery fascia',[-.18,-.18,3.15],[L+.18,.10,3.34],9,'PDF288 long vertical-board fascia, coarse reduced-height relief')
for x in np.arange(0,L,.24):bx('North fascia board',[float(x),-.205,3.15],[float(x)+.045,-.17,3.34],1,'PDF288 vertical fascia boards; count simplified and relief enlarged')
# Source south facade: two rear windows, end doors, blank center panels; not a mirrored north window grid.
for x in [1.67,20.81]:win('South corner rear window46'if x<5 else'South corner rear window39','S',SIDE_DEPTH,x,.90,1.42,1.40,2,4,'PDF340/341 Nos46/39:1400x900mm, present at unequal corner-return faces')
for x,nu in [(7.10,22),(15.34,21)]:win(f'South central sash{nu}','S',REAR_DEPTH,x,2.80,.83,1.10,4,3,'PDF340/341 Nos21/22:1100x2800mm; south modified wall openings')
for x,nu in [(4.00,36),(18.46,45)]:
 panel(f'South modified door{nu} outline','S',REAR_DEPTH,x-.50,x+.50,.51,2.51,.10,2,'PDF340/341 Nos36/45:2000x1000mm; different changed rear door leaves perPDF288')
 panel(f'South door{nu} plain field','S',REAR_DEPTH,x-.42,x+.42,.56,2.46,.15,0,'PDF288 simple rear door panels; uncalibrated pale finish, not matching north glazed leaves')
 if nu==36:
  panel('South door36 high opaque pane','S',REAR_DEPTH,x-.40,x+.40,1.94,2.43,.18,3,'PDF288 rear door at drawing-right has small high opening and lower vertical boarding; actual color not established')
  for xx in np.linspace(x-.38,x+.38,8):panel('South door36 lower boarding','S',REAR_DEPTH,float(xx)-.023,float(xx)+.023,.56,1.10,.19,2,'PDF288 rear-right lower vertical boards, coarse spaced relief')
 else:
  for zz in [1.17,1.98]:panel('South door45 horizontal division','S',REAR_DEPTH,x-.42,x+.42,zz-.025,zz+.025,.19,2,'PDF288 drawing-left rear door has unequal plain stacked fields, not matching rear-right leaf')
for x in [9.98,12.47]:panel('South central vertical panel division','S',REAR_DEPTH,x-.03,x+.03,.51,2.74,.08,1,'PDF288 central south infill divisions; not fabricated doors')
# Side at localx0 matches sourceFig5-68 and site geographic east.
for y,nu in [(3.82,13),(6.77,14)]:win(f'Figure5-68 main sash{nu}','L',0,y,1.45,1.33,1.50,3,3,'PDF340/341 Nos13/14:1500x1450mm, sourceFig5-68 side')
# SourceFig5-68 has three exterior window groups, no separate floating fourth vent. Upper divisions are represented within those groups; No23 is not independently placed from plan index alone.
win('Figure5-68 rear window47','L',0,9.48,.90,1.52,1.40,2,4,'PDF289/340 No47 side window; status-table47 fields blank,0.90x1.40m is visual estimate, not measured table value')
# Other side matches sourceFig5-69; differences and paired high small windows are retained.
for y,nu in [(3.82,15),(6.77,16)]:win(f'Figure5-69 main sash{nu}','R',L,y,1.45,1.33,1.50,3,3,'PDF340/341 Nos15/16:1500x1450mm; not mirrored rear-corner layout')
# SourceFig5-69 upper divisions remain within the three principal window groups; no additional invented floating No24 opening.
win('Figure5-69 rear window38','R',L,9.55,.90,1.50,1.40,2,4,'PDF340/341 No38:1400x900mm')
for y,nu in [(10.96,41),(11.85,42)]:win(f'Figure5-69 small window{nu}','R',L,y,.70,2.03,.70,2,2,'PDF340/341 Nos41/42:700x700mm; two small rear service windows')
# Small north-corner canopy at source drawing-right, geographical west per site252.
bx('Drawing-right canopy landing',[L-.05,-.35,0],[24.75,3.20,.51],0,'PDF284 small side canopy/landing; sourceFig5-66 right, geographic west per site252; dimensions approximate')
for x in [22.72,24.52]:
 for y in [.13,2.95]:
  bx('Canopy post',[x-.065,y-.065,.49],[x+.065,y+.065,2.84],2,'PDF284 four canopy supports; model cross-section enlarged, layout scan registered')
  bx('Canopy base',[x-.10,y-.10,.45],[x+.10,y+.10,.68],0,'Small canopy support foot, approximate')
add('Drawing-right small canopy roof',shed(L-.10,24.88,-.45,3.35,3.11,2.84,axis='x'),6,'PDF288 small side shed andPDF289 side view; geographic west, not east; eave/height estimated')
for y in [.13,2.95]:add('Canopy outer diagonal brace',beam([24.52,y,2.33],[24.0,y,2.93],.055),2,'PDF288 canopy diagonal braces; coarse geometry')
# Timber weatherboard relief is secondary, uncalibrated and not a damage map.
for side,plane,u0,u1 in [('L',0,2.25,SIDE_DEPTH),('R',L,2.25,SIDE_DEPTH),('S',SIDE_DEPTH,0,3.30),('S',SIDE_DEPTH,19.18,L)]:
 for z in np.arange(1.15,3.59,.21):panel('Coarse horizontal weatherboard',side,plane,u0,u1,float(z),float(z)+.032,.035,1,'PDF121 and289 fishscale/weatherboard courses simplified; no exact decay or individual board-length claim')
# Window hoods seen in side and rear-return elevations.
for side,plane,ys in [('L',0,[3.82,6.77,9.48]),('R',L,[3.82,6.77,9.55])]:
 for y in ys:panel('Side window shallow hood',side,plane,y-.85,y+.85,3.03,3.13,.24,2,'PDF289 shallow projecting lintel/hood; dimensions approximated and thickened')
for x in [1.67,20.81]:panel('South return window hood','S',SIDE_DEPTH,x-.65,x+.65,3.00,3.10,.23,2,'PDF288 small rear return window hood, coarse')
# Sparse masonry patches witness known exposed foundation without inventing exact crack geometry.
for side,plane,u in [('S',SIDE_DEPTH,.68),('S',SIDE_DEPTH,21.95),('L',0,8.4),('R',L,6.7)]:
 for j in range(3):panel('Schematic exposed masonry patch',side,plane,u-.32+j*.06,u+.32-j*.04,.57+j*.08,.63+j*.08,.045,8,'PDF121/288–289 exposed lower masonry; patch location approximate, not a measured damage reconstruction')
add('North first-bay low triangular masonry remnant',hull([[.10,-.02,.50],[1.20,-.02,.50],[.10,-.02,1.35],[.10,.14,.50],[1.20,.14,.50],[.10,.14,1.35]]),8,'PDF288 triangular exposed lower masonry at first gallery bay; coarse envelope only, not detailed breakage')
# Simple ridges and roof courses encode form without full tile reproduction.
add('Main roof ridge cap',beam([3.1025,5.44,RIDGE],[19.3775,5.44,RIDGE],.075),4,'PDF286 main ridge alignment;0.075m coarse cap included inside5.53m annotated outer crest, tile plane5.455m')
for xx in [1.4725,21.0075]:add('Secondary return ridge cap',beam([xx,7.61,4.545],[xx,11.05,4.545],.065),4,'PDF286 lower side return ridges; cap outer crest4.61m estimated from silhouette, tile plane4.545m')
for t in [.15,.30,.45,.60,.75,.90]:
 yi=main_y0+(main_y1-main_y0)/2*t;zz=EAVE+(RIDGE-EAVE)*t+.025;inset=(main_y1-main_y0)/2*t
 add('Main roof north tile course',beam([rx0+inset,yi,zz],[rx1-inset,yi,zz],.028),4,'PDF286 tile roof; sparse relief rows not individual tile replication')
 yi=main_y1-(main_y1-main_y0)/2*t
 add('Main roof south tile course',beam([rx0+inset,yi,zz],[rx1-inset,yi,zz],.028),4,'PDF286 rear main pitch visible above changed sheet roof')
# Corrugation runs with south roof slope; broad coarse ribs, not exact original sheets.
for x in np.arange(3.28,19.25,.43):add('South changed roof corrugation',beam([float(x),8.81,3.72],[float(x),13.58,2.89],.025),6,'PDF286 striped south sheet roofing; coarse ribs, existing modification retained')
# Union every construction part with no unreported component deletion.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Author-only underside access bores connect the three gallery cavities to the exterior.
# They are in the display base/floor, not purported historical features. Keep cutters editable and explicitly subtractive.
cut_items=[];cut_ops=[]
for i,x in enumerate([5.0,11.24,17.5]):
 cut=box([x-.40,.72,-BASE-.05],[x+.40,1.48,1.0]).translate([0,0,BASE*INTERNAL]).as_original()
 ids[int(cut.original_id())]=5;cut_items.append(cut);cut_ops.append({'name':f'Authored underside inspection cutter{i+1}','material':5,'operation':'subtract','evidence':'Author manufacturing/inspection access through display underside into gallery cavity;4.8x4.56mm model aperture, NOT a historic feature'})
s=s-mf.Manifold.batch_boolean(cut_items,mf.OpType.Add)
pre_simplify_components=[{'volume_mm3':q.volume()*SCALE**3,'bounds_internal':q.bounding_box()}for q in s.decompose()]
s=s.set_tolerance(.5).simplify(.5)  #0.5mm at source scale=0.003mm in model; remove numerical near-coincidence below STL precision margin.
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda x:'{'+ns+'}'+x
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan nursery main-body survey-envelope study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'Nursery main body from2004-01 current survey report;1954 added building, not1937 original or later restoration. Includes north gallery, south altered sheet roof and geographic-west small canopy; fine damage and interiors omitted. No trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
