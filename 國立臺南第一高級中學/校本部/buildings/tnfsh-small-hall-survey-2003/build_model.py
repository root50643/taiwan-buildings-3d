#!/usr/bin/env python3
"""TNFSH small hall, 2003 report exterior (A3 elevations dated 2000).
Estimated proportions anchored to readable elevation heights; NOT precise measured survey.
Construction metres, nominal 1:150 millimetres. No interior reconstruction.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent;SCALE=1000/150
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('wall','Approximate red brick','#955C4C','Brick notes; approximate illustrative color, monochrome report'),
('roof','Approximate red metal','#914D4B','A3 labels red corrugated metal; exact hue not established'),
('trim','Pale washed aggregate trim','#D5C9AF','A3 trim annotations; approximate hue'),
('glass','Opaque dark window relief','#384445','Simplified closed backing, not real glass or interior'),
('wood','Timber doors','#675746','Documented timber openings; approximate hue'),
('plinth','Grey masonry plinth','#969187','Illustrative neutral masonry'),
('base','Authored support','#B8B4A7','Not surveyed ground')]]
W=7.2;L=13.4;E=5.8;R=12.8;C=9.7
P={'state':'2003 survey report; A3 elevations dated2000, A2/A4 dated2003','scale_denominator':150,'main_width_estimate_m':2*W,'main_length_estimate_m':2*L,'main_eave_m':E,'gable_peak_m':R,'dimension_policy':'Readable A3 west elevation 420+160+700 cm anchors height; horizontal dimensions proportionally traced, not verified measurements. Prose approx23x14m conflicts with drawing proportions and is NOT silently reinterpreted or used as whole footprint.','approximation':'Footprints, opening placement, trim depths, corrugation spacing, small decorative profiles estimated from drawings. No exact brick count.','terrain':'Flat authored support; no site slope/interior/current-restoration claim','dates':'Do not interpret the 2003 report as current appearance'}
(ROOT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(n,s,mat=0,e='2003 report A2/A3/A4, proportional exterior detail'):
 s=s.translate([0,0,.45]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':n,'material':mat,'evidence':e})
def bx(n,a,b,mat=0,e='Proportional detail from survey drawings'):add(n,box(a,b),mat,e)
def xz(pts,y,d):return mf.CrossSection([pts]).extrude(d).rotate([90,0,0]).translate([0,y+d,0])
def archpoly(u,z,w,h,n=18):
 r=w/2;spring=z+h-r
 return [(u-r,z),(u+r,z),(u+r,spring)]+[(u+r*math.cos(a),spring+r*math.sin(a))for a in np.linspace(0,math.pi,n+1)]+[(u-r,z)]
def face_shape(pts,plane,coord,d):
 s=xz(pts,0,d)
 if plane=='y':return s.translate([0,coord-d/2,0])
 return s.rotate([0,0,90]).translate([coord+d/2,0,0])
def relief(n,plane,coord,u,z,w,h,arched=False,mat=3):
 out=1 if coord>0 else -1
 pts=archpoly(u,z,w,h) if arched else [(u-w/2,z),(u+w/2,z),(u+w/2,z+h),(u-w/2,z+h)]
 add(n+' backing',face_shape(pts,plane,coord+out*.025,.09),mat)
 outer=archpoly(u,z-.06,w+.18,h+.15) if arched else [(u-w/2-.09,z-.06),(u+w/2+.09,z-.06),(u+w/2+.09,z+h+.09),(u-w/2-.09,z+h+.09)]
 inside=[(u+(xx-u)*.965,z+(zz-z)*.98+.015) for xx,zz in pts]
 ring=mf.CrossSection([outer])-mf.CrossSection([inside]);s=ring.extrude(.08).rotate([90,0,0]).translate([0,.04,0])
 if plane=='x':s=s.rotate([0,0,90])
 s=s.translate([coord+out*.09,0,0] if plane=='x' else [0,coord+out*.09,0]);add(n+' frame',s,2)
 # Opaque bars are supported by backing. Heights stay under curved head.
 hh=h-w/2 if arched else h
 for k in [-.25,0,.25]:
  uu=u+k*w
  if plane=='x':bx(n+' mullion'+str(k),[coord-.14,uu-.025,z],[coord+.14,uu+.025,z+hh],2)
  else:bx(n+' mullion'+str(k),[uu-.025,coord-.14,z],[uu+.025,coord+.14,z+hh],2)
 for zz in np.linspace(z+hh*.18,z+hh*.82,5):
  if plane=='x':bx(n+' transom'+str(zz),[coord-.14,u-w/2,zz],[coord+.14,u+w/2,zz+.045],2)
  else:bx(n+' transom'+str(zz),[u-w/2,coord-.14,zz],[u+w/2,coord+.14,zz+.045],2)
bx('Authored flat support',[-8.2,-14.9,-.45],[10.4,20.4,0],6)
add('Main complete gabled hall',xz([(-W,0),(W,0),(W,E),(0,R-.16),(-W,E)],-L,2*L))
bx('Main plinth',[-W-.06,-L-.06,0],[W+.06,L+.06,.50],5)
# Complete low rear preparation rooms and polygonal backstage traced from A2-01/02.
rear=[(-W,L-.15),(W,L-.15),(W,L+3.7),(3.5,L+3.7),(3.5,L+4.9),(1.9,L+6.2),(-1.9,L+6.2),(-3.5,L+4.9),(-3.5,L+3.7),(-W,L+3.7)]
add('East preparation rooms and polygonal backstage',mf.CrossSection([rear]).extrude(4.15))
rearclip=mf.CrossSection([rear]).offset(.10).extrude(6.0)
def rear_wedge(z0,z1):return xz([(L-.2,z0),(L+6.4,z1),(L+6.4,z1+.18),(L-.2,z0+.18)],-W-.2,2*W+.4).rotate([0,0,90])
# YZ slope built by exchanging axes of an xz prism; full footprint clipped to the measured polygon.
sloping_fill=xz([(L-.2,4.10),(L+6.4,4.10),(L+6.4,4.18),(L-.2,5.50)],-W-.2,2*W+.4).rotate([0,0,90])
# Rotating xz maps its longitudinal x coordinate to y and prism depth into x.
add('East sloping upper wall volume',sloping_fill ^ rearclip,0)
add('East descending low roof',rear_wedge(5.48,4.16) ^ rearclip,1)
# Main metal two-plane roof, interpreted representative ribs (not counted actual panels).
for side in [-1,1]:
 a,b=sorted([0,side*(W+.35)])
 def roofz(x):return R-abs(x)*(R-E)/(W+.35)
 add('Main roof slab'+str(side),xz([(a,roofz(a)-.40),(b,roofz(b)-.40),(b,roofz(b)+.06),(a,roofz(a)+.06)],-L-.16,2*L+.32),1)
 for j,y in enumerate(np.linspace(-L+.1,L-.1,70)):
  add('Representative roof rib'+str((side,j)),xz([(a,roofz(a)),(b,roofz(b)),(b,roofz(b)+.09),(a,roofz(a)+.09)],y,.05),1)
# Raised gable rim follows each actual roof slope, and blind Lombard stepped arches.
for end in [-1,1]:
 y=end*L
 for side in [-1,1]:
  a,b=sorted([0,side*(W+.25)])
  add('Gable sloped border'+str((end,side)),xz([(a,roofz(a)-.05),(b,roofz(b)-.05),(b,roofz(b)+.23),(a,roofz(a)+.23)],y-.16,.32),2)
 for j,x in enumerate(np.linspace(-6.8,6.8,25)):
  top=roofz(x)-.50;h=.82;w=.62
  outer=archpoly(x,top-h,w,h);inner=archpoly(x,top-h+.11,w-.17,h-.19)
  # Blind filled recess remains attached to gable, never perforation.
  add('Blind Lombard pale outline'+str((end,j)),face_shape(outer,'y',y+end*.07,.15),2)
  add('Blind Lombard inset'+str((end,j)),face_shape(inner,'y',y+end*.16,.06),0)
# Long main wall openings: north seven arched windows + asymmetrically placed secondary door.
ys=np.linspace(-9.5,9.5,8)
for side in [-1,1]:
 for z in [3.85,5.45]:bx('Side horizontal belt'+str((side,z)),[side*W-.10,-L,z],[side*W+.10,L,z+.10],2)
 for j,y in enumerate(ys):
  if side==-1:
   if j==3:relief('North arched door','x',-W,y,.18,2.6,4.1,True,4)
   else:
    relief('North lower rectangular window'+str(j),'x',-W,y,.85,1.10,2.15,False)
    relief('North separate arched transom'+str(j),'x',-W,y,3.85,1.10,1.0,True)
    for yy in [y-.32,y,y+.32]:
     add('North intermediate bead ornament'+str((j,yy)),mf.Manifold.cylinder(.18,.095,.095,12).rotate([0,90,0]).translate([-W-.14,yy,3.45]),2)
  else:
   # Tall arched transoms remain visible above the low independent south arcade.
   relief('South high arched window'+str(j),'x',W,y,3.85,1.10,1.0,True)
   relief('South lower '+('door' if j in [0,3,6] else 'window')+str(j),'x',W,y,.2 if j in [0,3,6] else .85,1.45 if j in [0,3,6] else 1.05,2.45 if j in [0,3,6] else 1.8,False,4 if j in [0,3,6] else 3)
# North buttresses between opening groups, visible down to plinth in A3-1.
for j,y in enumerate([-L]+[(float(a)+float(b))/2 for a,b in zip(ys[:-1],ys[1:])]+[L]):
 bx('North projecting buttress'+str(j),[-W-.24,y-.12,.45],[-W+.03,y+.12,5.58],0)
 bx('North buttress cap'+str(j),[-W-.30,y-.17,5.48],[-W+.03,y+.17,5.66],2)
# Raised west central brick piers continue the high arched composition to its entrance base.
for x in [-2.10,2.10]:
 bx('West continuous central brick pier'+str(x),[x-.20,-L-.18,.30],[x+.20,-L+.02,5.25],0)
# South arcade: seven tall arches and eighth lower brick arch at rear per prose p109.
# Real arch voids through outer wall; inner hall is solid printable exterior.
bx('South arcade floor',[W-.08,-L,0],[C+.12,L+3.7,.32],5)
wall=box([C-.30,-L,.25],[C+.02,L,4.15])
for j,y in enumerate(ys):wall=wall-face_shape(archpoly(y,.29,2.18,3.05 if j==7 else 3.30),'x',C,1.0)
add('South arcade seven plus eighth facade arch wall',wall,0)
# Source shows eight arches across main length; first seven washed aggregate, final brick.
for j,y in enumerate(ys):
 if j==7:continue
 outer=mf.CrossSection([archpoly(y,.29,2.40,3.52)])-mf.CrossSection([archpoly(y,.29,2.18,3.30)])
 ring=outer.extrude(.12).rotate([90,0,0]).translate([0,.06,0]).rotate([0,0,90]).translate([C+.03,0,0]);add('South washed aggregate arch'+str(j+1),ring,2)
bx('South arcade flat roof',[W-.05,-L-.08,4.12],[C+.18,L+3.78,4.30],2)
# East-most low closed preparation corridor end, retained rather than omitted.
bx('South rear service room',[W-.05,L,0],[C,L+3.7,4.12],0)
for y in [L+1.3,L+3.2]:relief('South rear narrow window'+str(y),'x',C,y,.75,.65,2.45)
# West end of arcade opening and east end service-door relief.
endwall=box([W,-L-.06,.3],[C,-L+.22,4.12])-face_shape(archpoly((W+C)/2,.30,1.70,3.1),'y',-L,1.0)
add('West arcade end arch',endwall)
relief('East service door','y',L+3.7,8.4,.25,1.65,2.8,False,4)
# Polygonal column profiles on south arcade piers: end singles, middle pairs.
for j,y in enumerate([-L]+[(float(a)+float(b))/2 for a,b in zip(ys[:-1],ys[1:])]+[L]):
 for dy in ([0] if j in [0,8] else [-.13,.13]):
  add('South octagonal pier profile'+str((j,dy)),mf.Manifold.cylinder(2.18,.17,.17,8).translate([C-.03,y+dy,.30]),2)
# West rectangular crossed diagonal tile ornament fields, distinct from the three high arched lights.
for side in [-1,1]:
 cx=side*4.65;ww=4.9;z0=4.12;hh=1.25
 panel=[(cx-ww/2,z0),(cx+ww/2,z0),(cx+ww/2,z0+hh),(cx-ww/2,z0+hh)]
 add('West solid tile ornament backing'+str(side),xz(panel,-L-.065,.10),2,'Prose p109-110 crossed diagonal face tiles; NOT glass/opening')
 clip=mf.CrossSection([panel]);bars=[]
 for slope in [-1,1]:
  for off in np.arange(-7,7,.55):
   xx=cx+off
   strip=[(xx-.025,z0),(xx+.025,z0),(xx+slope*hh+.025,z0+hh),(xx+slope*hh-.025,z0+hh)]
   q=mf.CrossSection([strip]) ^ clip
   if not q.is_empty():bars.append(q)
 for j,q in enumerate(bars):add('West diagonal tile relief'+str((side,j)),q.extrude(.07).rotate([90,0,0]).translate([0,-L-.035,0]),5)
 for zz in [z0-.06,z0+hh]:bx('West lattice horizontal frame'+str((side,zz)),[cx-ww/2-.06,-L-.13,zz],[cx+ww/2+.06,-L+.02,zz+.07],2)
# West main gable differs from blind east gable: entrance, triple high arches and circular oculus.
relief('West main arched entrance','y',-L,0,.20,2.05,3.65,True,4)
for x in [-4.15,4.15]:relief('West narrow low window'+str(x),'y',-L,x,.85,.85,2.55)
# Large framed upper arched field, with three observed narrow light openings.
outer=mf.CrossSection([archpoly(0,4.45,4.10,5.15)])-mf.CrossSection([archpoly(0,4.55,3.72,4.85)])
add('West tall central arched border',outer.extrude(.17).rotate([90,0,0]).translate([0,-L+.02,0]),2)
for x in [-1.0,0,1.0]:relief('West triple high arched light'+str(x),'y',-L,x,5.35,.65,2.1 if x==0 else 1.75,True)
for radius,depth,mat in [(.40,.11,2),(.29,.15,3)]:
 circle=mf.CrossSection.circle(radius,32).extrude(depth+.02).rotate([90,0,0]).translate([0,-L+.02,8.20]);add('West oculus '+str(radius),circle,mat)
for x in [-3.7,3.7]:
 add('West diamond ornament'+str(x),xz([(x,6.6),(x-.26,6.2),(x,5.8),(x+.26,6.2)],-L-.14,.17),2)
for k in range(3):bx('Main entrance step'+str(k),[-1.6,-L-1.0+.25*k,0],[1.6,-L+.05,.10+.10*k],5)
# East rear windows follow angular footprint; no invented upper east-gable opening.
for side in [-1,1]:relief('Rear preparation side window'+str(side),'x',side*W,L+2,.75,.80,2.45)
for x in [-5.35,5.35]:relief('East preparation window'+str(x),'y',L+3.7,x,.75,.8,2.45)
for x in [-.9,.9]:relief('East polygon back window'+str(x),'y',L+6.2,x,.75,.75,2.45)
# Angled rear facade lights, accurately oriented rather than projecting beyond polygon face.
for side in [-1,1]:
 pts=archpoly(0,.75,.8,2.45) # source rectangular, use simple slab below instead
 s=box([-.4,-.09,.75],[.4,.09,3.2]).rotate([0,0,-side*39.1]).translate([side*2.70,L+5.55,0]);add('East diagonal opaque window'+str(side),s,3)
for side in [-1,1]:
 for u in [-.41,0,.41]:
  q=box([u-.035,-.14,.72],[u+.035,.14,3.25]).rotate([0,0,-side*39.1]).translate([side*2.70,L+5.55,0]);add('East angled window upright'+str((side,u)),q,2)
 for z in [.72,1.3,1.9,2.5,3.20]:
  q=box([-.44,-.14,z],[.44,.14,z+.06]).rotate([0,0,-side*39.1]).translate([side*2.70,L+5.55,0]);add('East angled window horizontal'+str((side,z)),q,2)
# No surrounding connected campus walkway beyond hall boundary, trees, signs, utilities or hidden interiors.

for o,i in zip(ops,items):assert i.status()==mf.Error.NoError,(o,i.status())
s=items[0]
for o,i in zip(ops[1:],items[1:]):
 s=s+i
 assert s.status()==mf.Error.NoError,(o,s.status())
s=s.set_tolerance(.001).simplify(.001)
m=s.to_mesh64()
# Quantize into STL's actual float32-mm precision before final topology simplification.
# This removes sub-precision CSG seam slivers rather than shipping a broken float32 STL.
qv=np.ascontiguousarray((np.asarray(m.vert_properties)*SCALE).astype(np.float32).astype(np.float64))
qm=mf.Mesh64(qv,np.array(m.tri_verts,dtype=np.uint64,order="C",copy=True),merge_from_vert=np.array(m.merge_from_vert,dtype=np.uint64,copy=True),merge_to_vert=np.array(m.merge_to_vert,dtype=np.uint64,copy=True),run_index=np.array(m.run_index,dtype=np.uint64,copy=True),run_original_id=np.array(m.run_original_id,dtype=np.uint32,copy=True),tolerance=.002)
qs=mf.Manifold(qm).simplify(.01);assert qs.status()==mf.Error.NoError,qs.status()
m=qs.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Weld duplicate material-boundary positions, retaining each surface triangle's real original material.
v,inv=np.unique(np.round(v,9),axis=0,return_inverse=True);f=inv[f]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='TNFSH Small Hall 2003 report exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats-package.relationships/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'.replace('http://schemas.openxmlformats-package.relationships/2006/relationships','http://schemas.openxmlformats.org/package/2006/relationships'))
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete small hall with south arcade and east backstage, 2003 report exterior; estimated horizontal dimensions with explicit prose/drawing conflict; no interior/current-state/terrain claim'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
