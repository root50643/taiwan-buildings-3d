#!/usr/bin/env python3
"""NUTN Wenhui six-storey courtyard building: official plan/photo bounded exterior.
No source images; main height24.63m recorded, footprint and fine dimensions estimated.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Off-white tile','#D7D3C5','Official courtyard photographs'),('glass','Opaque dark glass','#527875','Photographic uncalibrated approximation'),('frame','Grey window frames','#8B8C81','Photographic simplified detail'),('accent','Muted apricot bands','#AE8A82','Visible corridor bands'),('roof','Neutral roof plane','#B7B9AD','Roof details not documented'),('base','Display support','#BFC5BB','Authored support, not terrain'),('shadow','Recessed doors','#78766A','Simplified visible classroom openings')]]
SCALE=3.2
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.55]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Approximate feature based on official floor plan/photo, not survey'):add(name,box(a,b),mat,evidence)
W,D,H=54.,36.,24.63
F=H/6
bx('Authored display support',[-2,-5,-.55],[W+3,D+2,0],5,'Display slab, not terrain; basement omitted')
def cyl(r,h,x,y,z):return mf.Manifold.cylinder(h,r,r,48).translate([x,y,z])
# Room/corridor perimeter and upper two-storey curved court; plan topology, not measured footprint.
for k in range(6):
 z=k*F
 if k<4: void=box([27,12,z-.1],[41,24,z+F+.1])
 else: void=(box([26,12,z-.1],[41,24,z+F+.1])+cyl(6,F+.2,26,18,z-.1))
 add(f'Level{k+1} complete plan mass',(box([0,0,z],[W,D,z+F])-void)-box([52,14,z+.35],[55,22,z+F-.35]),0,'2025 official floor plans pages41-46; nominal envelope54x36m, not dimensioned source')
 # Main long facades have eight repeating bay groups; balcony pods occur between bay centres on4F.
 for side in [0,D]:
  sg=-1 if side==0 else 1
  ya,yb=sorted([side-.05*sg,side+.19*sg])
  for j in range(8):
   x=8.0625+j*6.125
   bx(f'Long window frame{k}-{side}-{j}',[x-2.45,ya,z+1.12],[x+2.45,yb,z+3.1],2)
   ga,gb=sorted([side+.18*sg,side+.24*sg])
   bx(f'Long glazing{k}-{side}-{j}',[x-2.34,ga,z+1.23],[x+2.34,gb,z+3.0],1)
   for q in range(7):
    xx=x-2.34+q*.78; ma,mb=sorted([side+.21*sg,side+.32*sg])
    bx(f'Mullion{k}-{side}-{j}-{q}',[xx-.045,ma,z+1.18],[xx+.045,mb,z+3.05],0)
   ma,mb=sorted([side+.21*sg,side+.34*sg]);bx(f'Transom{k}-{side}-{j}',[x-2.4,ma,z+2.45],[x+2.4,mb,z+2.55],0)
  a,b=sorted([side-.06*sg,side+.38*sg]);bx(f'Floor fascia{k}-{side}',[5.0,a,z+.08],[54,b,z+.8],0)
  a,b=sorted([side+.34*sg,side+.4*sg]);bx(f'Muted strip{k}-{side}',[5,a,z+.05],[54,b,z+.18],3)
  if k==3:
   for j in range(7):
    x=11.125+j*6.125;cy=side+sg*.35
    outer=cyl(.92,1.15,x,cy,z+.35);inner=cyl(.66,1.2,x,cy,z+.53)
    add(f'4F semicircular pod{side}-{j}',outer-inner,0,'4F plan and photo9: seven small rounded projecting guards')
  if k==4:
   for j in range(8):
    x=8.0625+j*6.125;a,b=sorted([side-.1*sg,side+1.15*sg]);o=box([x-2.15,a,z+.15],[x+2.15,b,z+1.3]);ia,ib=sorted([side-.2*sg,side+.85*sg]);cut=box([x-1.9,ia,z+.4],[x+1.9,ib,z+1.4]);add(f'5F long balcony{side}-{j}',o-cut,0,'5F plan long rounded balconies simplified squared at small corner radius')
 # Short left end openings documented by plan; no invented right blind wall grid.
 for y in [6,11,16,21,26,31]:
  bx(f'Left frame{k}-{y}',[-.13,y-.85,z+1.3],[.05,y+.85,z+3],2)
  bx(f'Left glass{k}-{y}',[-.18,y-.74,z+1.4],[-.12,y+.74,z+2.9],1)
 # Short-end recessed stair bay with curved guards, not an enclosed round tower.
 bx(f'Stair bay glass{k}',[51.98,14.4,z+1.3],[52.14,21.6,z+3.15],1,'Photo5 recessed glazed stair bay; lower levels follow plan, fine detail approximated')
 for yy in [14.5,16.2,18,19.8,21.5]:bx(f'Stair bay mullion{k}-{yy}',[52.12,yy-.06,z+1.25],[52.22,yy+.06,z+3.2],0)
 outer=mf.Manifold.cylinder(1.1,4,4,48).scale([.45,1,1]).translate([54,18,z+.3])
 inner=mf.Manifold.cylinder(1.3,3.7,3.7,48).scale([.45,1,1]).translate([54,18,z+.5])
 clip=box([53.6,13.8,z],[56,22.2,z+2])
 add(f'Curved stair balcony guard{k}',mf.Manifold.batch_boolean([outer-inner,clip],mf.OpType.Intersect),0,'Photo5 stacked curved open balcony guards; 2025 right stair plan')
 slab=mf.Manifold.cylinder(.35,4,4,48).scale([.45,1,1]).translate([54,18,z])
 add(f'Curved stair balcony floor{k}',mf.Manifold.batch_boolean([slab,box([51.8,13.8,z],[56,22.2,z+.4])],mf.OpType.Intersect),0,'Schematic floor slab, joins principal mass')
 for yy in [13.7,21.9]:bx(f'Stair outer frame{k}-{yy}',[53.7,yy,z],[54.4,yy+.4,z+F],0,'Photo5 straight side framing')
 # Court-facing windows on two opposite long walls
 for y,sg in [(12,1),(24,-1)]:
  for x in [29,32.5,36,39.5]:
   a,b=sorted([y-.05*sg,y+.12*sg]);bx(f'Court glazing{k}-{y}-{x}',[x-1.35,a,z+1.25],[x+1.35,b,z+2.95],1)
# Tall left stair glass bands visible at long-facade end
for side in [0,D]:
 sg=-1 if side==0 else 1;a,b=sorted([side-.05*sg,side+.2*sg]);bx(f'Stair glazing{side}',[1,a,.6],[3.8,b,H-.5],1)
 for z in [i*1.05 for i in range(23)]:
  aa,bb=sorted([side+.16*sg,side+.27*sg]);bx(f'Stair transom{side}-{z}',[.98,aa,z],[3.82,bb,z+.07],0)
# front entrance portal is independent of central court, centred around grid7, photo9
# arch is extruded in y from a half-annulus in xz plane
outer=mf.Manifold.cylinder(1.0,3.3,3.3,64).rotate([90,0,0]).translate([34,-1.3,6.4]);inner=mf.Manifold.cylinder(1.4,2.75,2.75,64).rotate([90,0,0]).translate([34,-1.1,6.4]);arch=mf.Manifold.batch_boolean([outer-inner,box([30,-3,6.4],[38,0,10.1])],mf.OpType.Intersect);add('Entrance semicircular arch',arch,0,'Official photo9 entrance arch, dimensions approximated')
for x in [30.7,36.75]:bx(f'Portal support{x}',[x,-2.3,0],[x+.55,-1.3,6.5],0)
# Ground-level glazed entry behind arch: not another elevated classroom window.
bx('Entry glazed doors',[31.4,-.5,.08],[36.6,-.26,3.5],1,'Photo9 and1F plan doorway; glazed door divisions approximated')
for xx in [31.4,33.1,34.9,36.6]:bx(f'Entry jamb{xx}',[xx-.07,-.57,.05],[xx+.07,-.47,3.58],0)
bx('Entry lintel',[31.3,-.57,3.46],[36.7,-.47,3.6],0)
bx('Entry approach',[30,-3.5,0],[38,0,.45],0)
for i in range(5):bx(f'Entry stair{i}',[30,-4.5+i*.23,0],[38,-3.3+i*.23,.09*(i+1)],0)
# Parapet includes central courtyard opening and upper inset curve; no guessed rooftop plant.
bx('Roof front cap',[0,-.15,H],[54,.35,H+.4],0);bx('Roof rear cap',[0,D-.35,H],[54,D+.15,H+.4],0)
bx('Roof left cap',[0,0,H],[.35,D,H+.4],0);bx('Roof right cap',[53.65,0,H],[54,D,H+.4],0)
for side in [0,D]:
 for x in [5.2+i*1.4 for i in range(35)]:
  a,b=sorted([side-.05,side+.4]);bx(f'Upper facade fin{side}-{x}',[x-.07,a,H-3.1],[x+.07,b,H],0,'Visible top-floor narrow vertical reveals')
# Small left stair roof extension observed, no mechanical equipment inferred
bx('Left stair rooftop',[0,0,H],[4.2,5,H+1.0],3,'Photo9 raised left stair termination; height approximate')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUTN Wenhui six-storey courtyard building');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official 1F-6F plan-backed Wenhui mass with upper curved courtyard; historical official-photo exterior, schematic exterior openings; not survey/current-condition/trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
