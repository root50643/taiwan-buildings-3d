#!/usr/bin/env python3
"""Tamsui Little White House main body and three arcades only, source-limited exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','White plaster','#E8E5D9','Official completed photo, uncalibrated'),('frame','White shutter and capital trim','#DCDDD5','Photographed shutter leaves and moulding, coarse'),('glass','Dark window proxy','#343F3C','Opaque recessed glazing proxy, not transparent'),('roof','Orange clay roof tiles','#AD5639','Photographed tiled hipped roof, coarse raised ribs'),('metal','Grey gutters','#737D7C','Visible drainage approximate'),('base','Authored display plinth','#B9B5A7','Authored support, not actual site'),('stone','Raised stone footing','#9A917F','Photographed raised foundation, coarse'),('dark','Door wood','#403A30','Photographed dark doors, uncalibrated')]]
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



# Main rectangular body only. Rear ancillary extension deliberately excluded.
# Piecewise x calibration honors interior 4.40/7.00/4.40m dimensions, not a survey.
xp=[255,414,606,695,979,1068,1260,1412];xm=[0,3.69,8.09,10.17,17.17,19.24,23.64,27.17]
def X(p):return float(np.interp(p,xp,xm))
def Y(p):return (928-p)*6.72/284
W=X(1412);D=Y(464);floor=.90;ceiling=floor+3.35;spring=floor+1.85;ridge=6.55
bx('Authored plinth',[-1.5,-2.8,-.6],[W+1.5,D+1.3,0],5,'Display support, no site reconstruction')
bx('Raised main foundation',[0,0,0],[W,D,floor],6,'Official plan rectangular core and photographed raised footing; height estimated')
bx('Arcade floor surface',[0,0,floor-.08],[W,D,floor+.02],1,'Three open verandas from official plan')
# Interior mass is opaque exterior-only proxy; openings are shallow recesses, not full interior.
x0=X(393);x1=X(1280);yf=Y(791)
core=box([x0,yf,floor],[x1,D,ceiling])
# Two full-height longitudinal entry passages read from plan (not interiors).
for a,b in [(606,695),(979,1068)]:core-=box([X(a),yf-.1,floor],[X(b),D+.1,ceiling-.2])
add('Opaque main room volumes with two entrance passages',core,0,'Official floorplan calibrated room widths/depth; no reconstructed room interiors')
# Front arcade: 11 voids from 12 drawn pier centres. Arches cut through, not embossed.
px=[270,414,508,603,695,792,886,979,1073,1167,1261,1397]
front=box([0,.03,floor],[W,.63,ceiling])
for i,(a,b) in enumerate(zip(px[:-1],px[1:])):
 left=X(a)+(1.25 if i==0 else .25);right=X(b)-(1.25 if i==10 else .25);ww=right-left
 front-=arch(ww,floor-.1,spring,ww/2).translate([(left+right)*50,33,0])
add('Eleven open front semicircular arches',front,0,'Official 11-arch count and plan pier locations; rise/photo-estimated')
# Side4 arches each, preserve front/back corner thickness.
yp=[914,795,695,590,478]
for side,x in [('west',.30),('east',W-.30)]:
 wall=box([x-.30,.1,floor],[x+.30,D,ceiling])
 for i,(a,b) in enumerate(zip(yp[:-1],yp[1:])):
  lo=Y(a)+(.48 if i==0 else .24);hi=Y(b)-(.45 if i==3 else .24);ww=hi-lo
  cut=arch(ww,floor-.1,spring,ww/2).rotate([0,0,90]).translate([x*100,(lo+hi)*50,0]);wall-=cut
 add(side+' four open arches',wall,0,'Official side four-arch count and plan positions; estimated arch elevations')
# Square-pier capital/base bands, near visible front spring line.
for i,p in enumerate(px):
 x=X(p);wid=.57
 if i==0:x=.82;wid=1.72
 if i==11:x=W-.82;wid=1.72
 bx('Front pier capital'+str(i),[max(0,x-wid/2),-.04,spring-.09],[min(W,x+wid/2),.70,spring+.08],1,'Photo raised moulded capitals; coarse rectangular bands')
 bx('Front pier foot'+str(i),[max(0,x-wid/2),-.04,floor],[min(W,x+wid/2),.69,floor+.15],1,'Photo column base moulding')
for x in [.3,W-.3]:
 for p in yp[1:-1]:
  y=Y(p);bx('Side capital'+str((x,p)),[x-.38,y-.3,spring-.09],[x+.38,y+.3,spring+.08],1,'Side capitals analogous visible arcade; coarse bands')
# Cornice and four-slope roof. Ceiling335cm does NOT mean ridge height.

roof=hip(-.25,W+.25,-.25,D+.25,ceiling+.02,ridge)
add('Four-slope main tiled roof',roof,3,'Official text confirms four slopes; eaves/ridge elevation and hip run estimated from photo, not survey')
# Shallow tile courses rather than claiming individual historic tiles.
# Roof surface ribs follow front/rear slope; fused with roof using sunk endpoints.
for x in np.arange(.2,W,.43):
 for y0,y1 in [(-.22,D/2),(D+.22,D/2)]:
  ztop=ridge-.05;run=min((x+.25)/4.25,(W+.25-x)/4.25,1)
  yy=y0+(y1-y0)*run;zz=ceiling+.02+(ztop-ceiling-.02)*run
  add('Coarse longitudinal roof tile rib',beam([x,y0,ceiling+.01],[x,yy,zz],.045),3,'Visible claytile channels represented by enlarged coarse ribs; not every tile')
# Front shutter windows, doors at two plan passages. Shallow dark pane overlays are display proxy.
def frontwindow(name,x,w,z,h):
 bx(name+' dark pane',[x-w/2,yf-.045,z],[x+w/2,yf+.05,z+h],2,'Plan openings and photographed dark glazing; depth/height estimated')
 for xx in [x-w/2,x+w/2]:bx(name+' frame',[xx-.05,yf-.1,z-.05],[xx+.05,yf+.05,z+h+.05],1,'Coarse visible frame')
 for zz in [z,z+h]:bx(name+' sill',[x-w/2-.06,yf-.12,zz-.06],[x+w/2+.06,yf+.06,zz+.06],1,'Coarse window sill/head')
 for s in [-1,1]:
  xx=x+s*(w/2+.27);bx(name+' open shutter',[xx-.23,yf-.17,z],[xx+.23,yf+.04,z+h],1,'Photographed opened white louvered shutters; approximate opening angle')
  for zz in np.arange(z+.12,z+h,.16):bx(name+' louvre',[xx-.20,yf-.22,zz],[xx+.20,yf-.1,zz+.045],1,'Coarse louvre slats, no tiny perforations')
for j,p in enumerate([449,510,575,742,836,929,1098,1163,1227]):frontwindow('Front window'+str(j),X(p),.85,floor+.72,1.70)
for j,(a,b) in enumerate([(606,695),(979,1068)]):
 x=(X(a)+X(b))/2;w=X(b)-X(a)-.12
 bx('Recessed passage double door'+str(j),[x-w/2,yf+.48,floor],[x+w/2,yf+.60,floor+2.65],7,'Plan passage entrance and photo doors, recessed opaque proxy')
 for xx in [x-w/2,x,x+w/2]:bx('Door stile',[xx-.045,yf+.41,floor],[xx+.045,yf+.6,floor+2.67],1,'Double leaf coarse frame')
 bx('Door transom',[x-w/2,yf+.4,floor+2.1],[x+w/2,yf+.6,floor+2.18],1,'Visible upper transom; approximate')
 # Two frontal stairs matched plan xpassages.
 for k in range(4):bx('Front stair'+str((j,k)),[x-1.15,-1.45+k*.34,0],[x+1.15,.15,(k+1)*floor/4],6,'Official plan two front stairs, rise/count approximated')
# Rear ends of verandas: photo supports one arched end opening per visible side.
back=box([0,D-.55,floor],[W,D,ceiling])
for x in [X(332),X(1341)]:back-=arch(1.70,floor-.1,spring,.85).translate([x*100,(D-.25)*100,0])
# Only side end panels; central rear plane is an explicit cut at omitted annex.
back=back-box([x0+.04,D-.65,floor-.1],[x1-.04,D+.1,ceiling+.1])
add('Rear end arcade panels',back,0,'Official boch04 shows end arch, photo/plans support arcaded side ends; central annex omitted')
# Side room windows from plan; retain opaque panes with coarse open shutters.
for side,x,sgn in [('west',x0,-1),('east',x1,1)]:
 for pz in [632,691,747]:
  y=Y(pz);z=floor+.72;w=.83;h=1.7
  bx(side+' side darkpane'+str(pz),[x-.05,y-w/2,z],[x+.05,y+w/2,z+h],2,'Side window location from plan and official corridor photo, dimensions approximate')
  for yy in [y-w/2,y+w/2]:bx('Side white frame',[x-.11,yy-.05,z-.04],[x+.11,yy+.05,z+h+.04],1,'Coarse window jamb')
  for v in [-1,1]:
   yy=y+v*(w/2+.24);bx('Side opened shutter',[x-.13,yy-.21,z],[x+.13,yy+.21,z+h],1,'Visible white opened side shutters, approximate angle')
   for zz in np.arange(z+.1,z+h,.17):bx('Side louvre',[x-.17,yy-.18,zz],[x+.17,yy+.18,zz+.04],1,'Coarse louvre no individual perforations')
# White gutters and corner/downpipes, omit utility wiring/cameras/temporary notices.
for y in [-.25,D+.25]:bx('Long gutter',[-.3,y-.075,ceiling+.02],[W+.3,y+.075,ceiling+.14],4,'Official photo visible perimeter gutter coarse profile')
for x in [0,W]:bx('End gutter',[x-.08,-.25,ceiling+.02],[x+.08,D+.25,ceiling+.14],4,'Coarse side gutter')
for x,y in [(0,-.02),(W,-.02),(X(792),-.02),(0,D),(W,D)]:
 bx('Water collector',[x-.13,y-.14,ceiling-.1],[x+.13,y+.14,ceiling+.18],1,'Photographed box hopper, coarse placement')
 add('Downpipe',beam([x,y-.08,.2],[x,y-.08,ceiling+.05],.065),1,'Visible drainpipe, coarse simplified straight path')
# One visible roof chimney; approximate position and height only, not historic flue reconstruction.
cx=W*.52;cy=D*.67;cz=ceiling+(ridge-ceiling)*(D+.25-cy)/(D/2+.25)
bx('Visible rear roof chimney',[cx-.4,cy-.32,cz-.2],[cx+.4,cy+.32,ridge+.32],0,'Official boch04 chimney on far roof, approximate placement/height')
bx('Chimney cap',[cx-.49,cy-.4,ridge+.25],[cx+.49,cy+.4,ridge+.42],6,'Visible rectangular cap coarse profile')
# Raised footing coarse joints and vent grilles from entry photograph.
for z in [.29,.60]:bx('Foundation course',[0,-.015,z],[W,.035,z+.035],6,'Coarse photograph-visible foundation courses, not individual masonry survey')
for x in [X(405),X(580),X(866),X(1125),X(1280)]:
 bx('Foundation vent dark',[x-.23,-.035,.18],[x+.23,.03,.46],2,'Official entryphoto square ground vents, placement approximate')
 for xx in [-.14,0,.14]:bx('Vent grille',[x+xx-.018,-.055,.18],[x+xx+.018,.03,.46],4,'Coarse grille no functional holes')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.2).simplify(.2)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Tamsui Little White House main-body exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Main body and three arcades only. Official room dimensions and photos; overall dimensions/roof height estimated; excludes rear annex and interiors; no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
