#!/usr/bin/env python3
"""Chiayi Art Museum C warehouse wing only, source-limited exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Weathered buff masonry','#AD9E82','Official2021photos, uncalibrated averagedcolor, not staintexture'),('roof','Dark tiled roof','#575B56','Official C-wing roofphoto'),('glass','Opaque window infill','#344E4A','Solid print proxy, not transparentglass'),('frame','Green painted window frames','#509C87','Officialphotos greenframes'),('timber','Courtyard timber posts','#9A6845','Official corridor detail'),('base','Authored display support','#B8B8AF','Authorednottrueground'),('metal','Dark metalwork','#4C5351','Photographed drains and stairs')]]
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

# Approximate source-plan scale: 10m graphicbar. Coordinates x along C wing, y inward from courtyard.
L=35.6;W=8.8
bx('Authored display base',[-2.0,-4.0,-.6],[L+1.0,W+1.0,0],5,'Rectangular display support not landscapedmuseumsite')
bx('Existing C warehouse',[0,0,0],[L,W,9.2],0,'Officialscaledplan rectangular footprint; eaveheightestimatedfromsection/photo')
# True gable profiles; central roof monitor stops short of both ends.
add('Main gabled tile roof',hull([[-.35,-.45,9.16],[L+.35,-.45,9.16],[-.35,W+.45,9.16],[L+.35,W+.45,9.16],[-.35,W/2,11.45],[L+.35,W/2,11.45]]),1,'Officialroofphoto two slopes and continuous ridge; heightproportionestimated')
bx('Raised central roof monitor',[5.8,3.12,10.50],[L-5.8,5.68,12.0],0,'Officialphoto roof clerestory centralraisedstrip; lengthestimated')
add('Monitor gabled cap',hull([[5.45,2.95,11.94],[L-5.45,2.95,11.94],[5.45,5.85,11.94],[L-5.45,5.85,11.94],[5.45,4.4,12.52],[L-5.45,4.4,12.52]]),1,'Visible narrow double-pitched monitorcap, approximate')
for y in [3.10,5.70]:
 bx('Monitor darklightband'+str(y),[5.95,y-.055,11.15],[L-5.95,y+.055,11.87],2,'Photographed continuous darkclerestory; not exact glazingdivisions')
 for x in np.arange(6.1,L-5.9,1.15):bx('Monitor mullion'+str((x,y)),[x-.035,y-.08,11.12],[x+.035,y+.08,11.92],6,'Coarsened visible mullions')
# Tile courses are coarsened relief; no individual traditional roof tile geometry.
for j in range(1,10):
 t=j/10;y=-.45+(W/2+.45)*t;z=9.16+2.29*t
 for yy in [y,W-y]:add('Roof course'+str((j,yy)),beam([-.32,yy,z+.01],[L+.32,yy,z+.01],.04),1,'Photographed tiledsurface, coarsecourses not exact tilecount')
# Courtyard canopy, exposed timber columns, paired beam details.
add('Courtyard lean canopy',hull([[0,-3.0,3.5],[L,-3.0,3.5],[0,.1,3.5],[L,.1,3.5],[0,.1,4.0],[L,.1,4.0]]),1,'Officialphoto continuous corridor roof sloping toward courtyard')
for x in [1.1,4.5,7.9,11.3,14.7,18.1,21.5,24.9,28.3,31.7,35.0]:
 bx('Timber post'+str(x),[x-.13,-2.7,0],[x+.13,-2.44,3.55],4,'Photo timber canopy posts, positions estimated from plan rhythm')
 bx('Post metalfoot'+str(x),[x-.15,-2.72,0],[x+.15,-2.42,.35],6,'Officialcloseup metalfoot, coarsened')
 bx('Canopy crossbeam'+str(x),[x-.09,-2.8,3.34],[x+.09,.12,3.54],4,'Exposed canopybeam photo')
# Framed windows are solid inlays. Front clear11upperwindows; positions proportionallyestimated.
def frontwin(n,x,z,w=1.0,h=1.15):
 bx(n+' glass',[x-w/2,-.06,z],[x+w/2,.02,z+h],2,'Sourcephotograph opening, solidinfill not interior')
 for a,b in [([x-w/2-.06,-.10,z-.06],[x-w/2+.04,.03,z+h+.06]),([x+w/2-.04,-.10,z-.06],[x+w/2+.06,.03,z+h+.06]),([x-w/2,-.10,z-.06],[x+w/2,.03,z+.04]),([x-w/2,-.10,z+h-.04],[x+w/2,.03,z+h+.06]),([x-.035,-.11,z],[x+.035,.03,z+h]),([x-w/2,-.11,z+h/3-.035],[x+w/2,.03,z+h/3+.035]),([x-w/2,-.11,z+2*h/3-.035],[x+w/2,.03,z+2*h/3+.035])]:bx(n+' frame'+str(a),a,b,3,'Greenframes visible, simplified thickenedcrossbars')
for j,x in enumerate([1.9,5.0,8.1,11.2,14.3,17.4,20.5,23.6,26.7,29.8,32.9]):frontwin('Upper courtyard window'+str(j),x,7.0,.9,1.4)
for j,x in enumerate([2.,8.,11.2,14.3,17.4,20.5,23.6,26.7,29.8,33.]):frontwin('Lower courtyard window'+str(j),x,2.05,.8,1.25)
frontwin('Cafe doorway',5.,.05,1.8,2.85)
frontwin('Second courtyard doorway',28.3,.05,1.8,2.85)
# Visible free gable end: three verticalwindowaxes, center upperdoor onto staircase.
for y in [1.7,4.4]:
 for z in [1.1,6.2]:
  bx('Freeend glazing'+str((y,z)),[-.065,y-.5,z],[.025,y+.5,z+1.25],2,'Officialaerial freeend windows; approximateheight')
  for yy in [y-.54,y,y+.54]:bx('Freeend greenjamb'+str((yy,z)),[-.10,yy-.045,z-.05],[.04,yy+.045,z+1.3],3,'Visible greenframes')
  for zz in [z-.02,z+.42,z+.83,z+1.25]:bx('Freeend greenrail'+str((y,zz)),[-.10,y-.54,zz-.035],[.04,y+.54,zz+.035],3,'Simplifiedframe')
bx('Freeend upper door',[-.08,6.35,4.65],[.02,7.75,6.8],2,'Officialaerial metalstair landing door')
add('Freeend masonry gable',hull([[-.36,0,9.15],[-.31,0,9.15],[-.36,W,9.15],[-.31,W,9.15],[-.36,4.4,11.23],[-.31,4.4,11.23]]),0,'Visible masonry triangle under tile verge, simplified')
bx('Freeend gable darkglass',[-.40,3.98,9.35],[-.30,4.82,10.15],2,'Officialphoto darkglass greenframe gablewindow')
for yy in [3.98,4.40,4.82]:bx('Gable window jamb'+str(yy),[-.44,yy-.035,9.32],[-.29,yy+.035,10.18],3,'Visible greenframe simplified')
for zz in [9.35,9.75,10.15]:bx('Gable window rail'+str(zz),[-.44,3.95,zz-.035],[-.29,4.85,zz+.035],3,'Visible greenframe simplified')
# Stair flights along free end; 24steps approximate, no unsafe claim of exact risercount.
for j in range(24):
 y=-.5+j*.31;bx('External stair step'+str(j),[-1.7,y,0],[.02,y+.33,.2+j*.19],6,'Photographed external stair, authorapproximation')
bx('Stair upper landing',[-1.7,6.7,4.45],[.08,7.5,4.68],6,'Visible landing')
add('Stair outer handrail',beam([-1.68,-.45,1.0],[-1.68,6.85,5.65],.065),6,'Photo slimrail thickened for manufacture')
for j in range(0,24,3):
 y=-.45+j*.31;bx('Stair railpost'+str(j),[-1.75,y-.05,.15+j*.19],[-1.61,y+.05,1.05+j*.19],6,'Simplifiedrailing')
# Courtyard masonry foot and visible basement vents; no invented rear pattern.
bx('Courtyard dark masonry foot',[0,-.015,0],[L,.015,1.15],6,'Official corridor photo darkwallfoot, averaged color')
for x in [8.,11.2,14.3,17.4,20.5,23.6,26.7,33.]:
 bx('Low vent dark inset'+str(x),[x-.34,-.07,.15],[x+.34,.02,.63],2,'Official corridor lowvent row; locations coarsely aligned, not measured')
 for zz in [.23,.35,.47,.59]:bx('Low vent green slat'+str((x,zz)),[x-.31,-.10,zz-.025],[x+.31,.03,zz+.025],3,'Visible green vent louvers coarsened')
# Drainpipes on photographed courtyard face; rear and attachedend intentionally notinvented.
for x in [6.7,18.8,30.8]:bx('Courtyard drainpipe'+str(x),[x-.065,-.14,.1],[x+.065,.015,9.25],6,'Officialphoto dark verticaldrains, approximate positions')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.05).simplify(.05)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Chiayi Art Museum C warehouse exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'C warehouse wing only, official2021scaledplan and completedphotos. Approximateproportions, no A/B buildings, no hiddenrearopenings or interior, no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
