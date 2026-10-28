#!/usr/bin/env python3
"""Pingtung Art Hall front lobby and colonnade only; source-limited exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('white','Pale concrete frame','#DEDDD3','Completed official/architect photographs, uncalibrated'),('beige','Beige wall panels','#C5B58C','Front entrance infill, joints coarse'),('glass','Opaque glazing proxy','#576863','Not transparent; internal hall not reconstructed'),('mesh','Silver solid-backed lattice proxy','#B6BFC0','Expanded metal approximated by coarse ribs on solid backing; no microperforations'),('cyan','Cyan frame','#459CAC','Source-visible colored frame; arrangement approximate'),('red','Red frame','#A94735','Source-visible colored frame; arrangement approximate'),('yellow','Yellow frame','#C3A333','Source-visible colored frame; arrangement approximate'),('green','Green frame','#79985A','Source-visible colored frame; arrangement approximate'),('base','Authored support plinth','#AAA79D','Display support, not site'),('cut','Authored cutoff wall','#817F76','Explicit boundary toward excluded auditorium, not reconstructed exterior')]]
SCALE=.05
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
 d=4.25
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(np.column_stack([x,y,z,a*100]))



# Official plan p25, clipped to lobby9 and front colonnade, not whole theatre.
# 84px scale bar = 10m, estimated sidewall width24m, partial depth15.5m.
W=24.;D=15.;floor=.8;roof=12.4
bx('Authored display plinth',[-3,-4,-.6],[W+3,D+1,0],8,'Authored support, no reconstructed site')
bx('Lobby floor and porch platform',[-.5,-.8,0],[W+.5,D,floor],0,'Floorplan lobby/porch only; raised entrance estimated from photograph')
# Floorplan auditorium partition is the cutoff. No claim this is actual exterior rear.
bx('Explicit cutoff toward excluded auditorium',[0,D-.35,floor],[W,D,roof-.4],9,'Authored closed cutoff; auditorium/stage/flytower excluded')
for x in [0,W-.35]:bx('Lobby side wall',[x,3.3,floor],[x+.35,D,roof-.4],1,'Official lobby plan side enclosure, source-visible front portion; depth estimated')
bx('Flat lobby roof slab',[-2.2,-1.7,roof-.5],[W+2.2,D,roof],0,'Official plan/section/front photographs; roof12.4m from architect text, no equipment reconstruction')
# Front glazing is recessed behind the coloured screen; opaque representation.
bx('Recessed front glazing',[.2,3.15,floor],[W-.2,3.35,11.5],2,'Front completed photos; opaque glazing proxy, not internal views')
# Beige first-storey side infill and glazed entrance groups.
for a,b in [(.2,4.4),(19.6,23.8)]:bx('Ground beige infill',[a,3.03,floor],[b,3.36,3.6],1,'Photographed front ground wall panels')
for x in [4.5,5.6,6.7,7.8,8.9,10.,11.,12.,13.,14.,15.1,16.2,17.3,18.4,19.5]:
 bx('Ground glazing vertical frame',[x-.045,2.95,floor],[x+.045,3.36,3.65],0,'Coarse front door and glazing frame, positions photo-estimated')
for z in [floor,2.75,3.6]:bx('Glazing transom',[4.5,2.94,z],[19.5,3.36,z+.085],0,'Photographed door heads/transom; approximate levels')
# Main central double doors: inset contrasting leaves and visible centre stile.
for x in [10.5,12.]:bx('Central entry glass door',[x,2.88,floor+.02],[x+1.45,3.2,2.75],2,'Visible paired central glass doors, not functional opening')
for x in [10.5,12.,13.45]:bx('Central door jamb',[x-.05,2.78,floor],[x+.05,3.2,2.8],0,'Double door frames')
for x in [11.8,12.2]:bx('Door handle',[x-.035,2.70,1.45],[x+.035,2.94,1.85],3,'Coarse paired door handle; not exact hardware')
# Six exposed front piers; central doubled bay has no central vertical column.
for x in [0,4,8,16,20,24]:
 bx('Tall front pier',[x-.24,-.25,floor],[x+.24,.25,10.65],0,'Completed frontal photo six piers and wider central bay; spacing approximate')
 bx('Longitudinal roof beam',[x-.22,1.1,11.5],[x+.22,D,12.05],0,'Visible portico/lobby roof framing, simplified')
# Front-elevation curved transitions: single extruded profile, avoid coplanar hull slivers.
for x in [0,4,8,16,20,24]:
 for sg in [-1,1]:
  pts=[(-.20,10.40),(-.20,11.98),(1.15,11.98),(1.15,11.62)]+[(.85*t*t,10.55+1.12*(2*t-t*t))for t in np.linspace(1,0,13)]
  pts=[((x+sg*a)*100,z*100)for a,z in pts]
  if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0:pts.reverse()
  add('Front curved pier branch',mf.CrossSection([pts]).extrude(48).rotate([90,0,0]).translate([0,24,0]),0,'Visible front column/beam transition, faceted curve approximation')
# Ten roof edge floodlights visible in the completed frontal photograph.
for x in np.linspace(.3,W-.3,10):
 bx('Roof light small base',[x-.09,-.8,roof-.03],[x+.09,-.5,roof+.10],3,'Photo visible lighting; coarse placement, no wiring')
 bx('Roof floodlight box',[x-.14,-.85,roof+.05],[x+.14,-.55,roof+.35],9,'Coarse opaque floodlight housing, approximate tilt omitted')
# Central roof beam exists but no front pier.
bx('Central suspended roof beam',[11.82,-1.6,11.55],[12.18,D,12.05],0,'Frontal photograph shows centre roof beam without centre pier')
# Five stepped rows of colored mesh boxes; each higher row wider and further forward.
# Solid-backed manufacturing proxy, coarse grid instead of microscopic expanded-metal holes.
for row in range(5):
 z=3.55+row*1.31;left=1.6-.28*row;right=W-left;y=2.35-row*.22
 bx('Screen horizontal mounting rail',[left,y,z+1.2],[right,3.33,z+1.29],3,'Approximate supporting rail fused to backing; not measured construction')
 count=24;ww=(right-left)/count
 for j in range(count):
  x=left+j*ww;col=[3,4,3,6,3,7,3,5][(j+row*3)%8]
  bx('Solid-backed expanded metal proxy',[x,y+.06,z],[x+ww,y+.12,z+1.22],3,'Microperforations omitted, opaque coarse lattice backing')
  for xx in [x,x+ww]:bx('Colored vertical screen edge',[xx-.04,y-.05,z],[xx+.04,y+.14,z+1.25],col,'Photographed colored rectangular frames, simplified color sequence')
  for zz in [z,z+1.22]:bx('Colored horizontal screen edge',[x-.04,y-.05,zz-.035],[x+ww+.04,y+.14,zz+.035],col,'Coarse frame')
  for q in [1,2,3]:bx('Coarse metal mesh rib',[x+ww*q/4-.014,y+.025,z+.03],[x+ww*q/4+.014,y+.13,z+1.2],3,'Solid-backed coarse ribs, not real perforation')
# Broad shallow front stair, no imagined site terrain.
for k in range(5):bx('Broad front entry step',[-.9-k*.06,-2.55+k*.35,0],[W+.9+k*.06,-.3,(k+1)*floor/5],0,'Photographed broad front stair, number/rise approximate')
# Side accessibility ramp and coarse metal rail on source-visible left only.
ramp=hull([[-1.7,-2.5,.03],[-.75,-2.5,.03],[-1.7,3.1,.03],[-.75,3.1,.03],[-1.7,3.1,floor],[-.75,3.1,floor]])
add('Left sloped access ramp',ramp,0,'Completed left-corner photograph ramp; route/rise simplified')
for y in [-2,0,2,3]:add('Left ramp rail post',beam([-1.65,y,max(.08,(y+2.5)/5.6*floor)],[-1.65,y,1+(y+2.5)/5.6*floor],.035),3,'Coarse visible accessibility rail')
add('Left ramp handrail',beam([-1.65,-2.1,1.06],[-1.65,3.1,1.8],.04),3,'Simple straight ramp rail, not compliance geometry')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.2).simplify(.2)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if q.volume()<1];s=mf.Manifold.batch_boolean([q for q in chunks if q.volume()>=1],mf.OpType.Add)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Pingtung Art Hall front-lobby exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Front lobby/colonnade only; excludes auditorium, stage, flytower and rear. Plan-scale estimated, opaque glazing/solid-backed mesh; no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
