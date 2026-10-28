#!/usr/bin/env python3
"""Former Tainan Weather Observatory; source-supported simplified exterior, NOT measured survey."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('brick','Warm yellow face brick','#BA8B4D','Official city gallery; color uncalibrated'),('stone','Grey stonewashed trim','#96988B','City close photographs; simplified masonry'),('glass','Opaque dark window glass','#334543','Photographic dark window bays; solid printable inlays'),('roof','Dark ceramic roof','#4B504C','Official STSP aerial photo;18radialroofsectors'),('base','Authored display support','#A8ACA3','Not site terrain'),('frame','Grey teal timber and frames','#596D69','Official cityphotos; uncalibrated'),('tower','Plastered white windtower','#E9E7DC','CWA official and STSP tower closeup')]]
SCALE=.1
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,50]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def cyl(r,z0,z1,n=96,r2=None):return mf.Manifold.cylinder((z1-z0)*100,r*100,(r if r2 is None else r2)*100,n).translate([0,0,z0*100])
def poly(pts,z0,z1):return mf.CrossSection([(np.array(pts)*100).tolist()]).extrude((z1-z0)*100).translate([0,0,z0*100])
def facebox(name,a,b,ang,mat,evidence):add(name,box(a,b).rotate([0,0,ang]),mat,evidence)
def arch(width,bottom,spring,rise,y0,y1):
 pts=[(-width/2,bottom),(width/2,bottom),(width/2,spring)]+[(width/2*math.cos(t),spring+rise*math.sin(t))for t in np.linspace(0,math.pi,17)[1:]]
 return mf.CrossSection([(np.array(pts)*100).tolist()]).extrude((y1-y0)*100).rotate([90,0,0]).translate([0,y1*100,0])
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.]) if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);M=np.column_stack([x,y,z,a*100]);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(M)
pts=[(7.5*math.cos(math.radians(100+20*i)),7.5*math.sin(math.radians(100+20*i)))for i in range(18)]
add('Authored eighteen-sided display base',cyl(9.0,-.5,0,72),4,'Authored support, NOT original lot or terrain')
add('Stone foundation plinth',poly(pts,0,.55),1,'City photographs continuous stonebase; height estimated')
add('Eighteen-sided yellowbrick wall body',poly(pts,.5,4.65),0,'Official CWA schematic and heritage text18gon; approximately15m outside diameter from STSP article; no survey')
# Roof an 18-sided shallow frustum, high edge sealed to the cylindrical tower.
roof=mf.Manifold.cylinder(225,815,230,18).rotate([0,0,0]).translate([0,0,455])
add('Eighteen radial roof sectors',roof,3,'Official STSP aerial photograph and culture heritage text18equal roofdivisions; eavesheight4.55m and top6.8m estimated')
add('Central cylindrical wind tower',cyl(2.3,0,11.15),6,'Official approximate12m towerheight, STSP innerdiameter4.6m; cylinder solid to print')
for z,r,h in [(10.9,2.37,.16),(11.06,2.49,.16),(11.22,2.61,.18),(11.40,2.67,.16)]:add('Tower cornice band '+str(z),cyl(r,z,z+h),6,'STSP tower closeup concentric layered cornice; simplified profile')
add('Tower parapet solid lower ring',cyl(2.53,11.5,12.0)-cyl(2.27,11.55,12.05),6,'Tower photographed low circular parapet; not surveyed height')
add('Observation deck',cyl(2.4,11.48,11.62),1,'Tower platform below parapet, hidden floor authored closure')
# Every exterior face is retained. Two opposing entry bays are supported by officialplan.
for i in range(18):
 ang=i*20
 isdoor=i in [0,9]
 bottom=.55 if isdoor else 1.05;spring=3.15 if isdoor else 3.12;rise=.72 if isdoor else .24;width=1.65 if isdoor else 1.12
 add(('Entry arch ' if isdoor else 'Window arched surround ')+str(i),arch(width+.24,bottom-.08,spring,rise+.12,7.30,7.48).rotate([0,0,ang]),1,'City exterior arch profiles; windows repeated according to18face scheme, all aperture dimensions estimated')
 add('Opaque aperture '+str(i),arch(width,bottom,spring,rise,7.45,7.51).rotate([0,0,ang]),2,'Solid dark inlay, NOT open glass; approximate restoration-era window/entry geometry')
 for x in [-width/2,0,width/2]:facebox('Glazing vertical frame '+str((i,x)),[x-.035,7.49,bottom],[x+.035,7.56,spring],ang,5,'Cityphotos visible framed glazing; enlarged print minimum0.7mm')
 for z in ([2.7,3.15] if isdoor else [1.6,2.2,2.8]):facebox('Glazing transom '+str((i,z)),[-width/2,7.49,z-.035],[width/2,7.56,z+.035],ang,5,'Simplified photographed window grid; not exact surveyed muntin rhythm')
 if isdoor:
  for k in range(3):facebox('Entrance step '+str((i,k)),[-1.15,7.2+k*.32,0],[1.15,8.55-k*.32,.18*(k+1)],ang,1,'Opposing approachsteps inferred from officialplan and westernphotograph, risers estimated')
 # Pilasters occur at each polygon corner, photographed alternating stonebands.
 a=math.radians(100+i*20);x,y=7.5*math.cos(a),7.5*math.sin(a)
 add('Corner stone pilaster '+str(i),box([x-.13,y-.13,.5],[x+.13,y+.13,4.6]),1,'Cityclosephotos cornerstone pilasters; simplified square profile')
 # Timber eaves bracket along radial corner line, attached at both ends.
 add('Timber diagonal eaves bracket '+str(i),beam([7.48*math.cos(a),7.48*math.sin(a),3.65],[8.05*math.cos(a),8.05*math.sin(a),4.62],.09),5,'Visible timber triangular eaves brackets; round section robust simplification')
 add('Roof raised radial hip '+str(i),beam([2.25*math.cos(a),2.25*math.sin(a),6.82],[8.12*math.cos(a),8.12*math.sin(a),4.61],.075),3,'18roofridges visible official aerial; coarsened tile ridge, microscopic tiles omitted')
# The four tower windows climb around the shaft; exact heights/angles not surveyed.
for i,z in enumerate([8.05,8.85,9.65,10.10]):
 ang=i*90
 add('Tower small arch surround '+str(i),arch(.70,z,z+.72,.13,2.20,2.38).rotate([0,0,ang]),1,'Official STSP text four arched tower windows, photos staggered at spiralstair heights; chosen elevations approximate')
 add('Tower small dark window '+str(i),arch(.54,z+.08,z+.70,.10,2.35,2.42).rotate([0,0,ang]),2,'Photo-supported tower apertures; solid glazing')
 for x in [0]:facebox('Tower window mullion '+str(i),[x-.035,2.40,z+.05],[x+.035,2.47,z+.78],ang,5,'Simplified cross frame')
 facebox('Tower window transom '+str(i),[-.27,2.40,z+.39],[.27,2.47,z+.46],ang,5,'Simplified cross frame')
# Raised polygonal safety railing visible on platform. Thick printable geometry, no internal access.
for i in range(8):
 a=2*math.pi*i/8;b=2*math.pi*(i+1)/8
 p=[1.45*math.cos(a),1.45*math.sin(a),11.59];q=[p[0],p[1],12.65]
 add('Deck railing post '+str(i),beam(p,q,.065),5,'STSP and firsthand photo raised polygonal platform rail, approximate8sides and print thickening')
 add('Deck railing top '+str(i),beam(q,[1.45*math.cos(b),1.45*math.sin(b),12.65],.065),5,'Simplified observation platform railing')
# One coarse triangular instrument support, not a working or exact scientific apparatus replica.
for x,y in [(1.3,0),(1.8,.45),(1.8,-.45)]:add('Instrument mast leg '+str((x,y)),beam([x,y,11.55],[1.65,0,14.05],.08),1,'STSP photo and2020firsthandphoto instrument support; enlarged simplified representative geometry')
for z in [12.3,13.05,13.65]:add('Instrument horizontal brace '+str(z),beam([1.3,0,z],[1.85,0,z],.075),1,'Coarse instrument mast brace, no precise mechanism claim')
add('Simplified wind indicator',beam([1.1,0,14.0],[2.25,0,14.0],.08),5,'Photographed top wind instrument, coarse nonfunctional indicator')
add('Wind indicator tail',box([2.0,-.07,13.85],[2.28,.07,14.25]),5,'Approximate flat vane tail, enlarged for manufacture')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.05).simplify(.05)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Former Tainan Weather Observatory exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official schematic eighteen-sided plan and dated restoration-era photos; approximate 15m outer diameter,4.6m tower diameter,12m towerheight. Window and roof geometry estimated; apparatus simplified; no trial print; not a measured survey'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
