#!/usr/bin/env python3
"""Fengyuan Dingjie Police Station, May2013 A-series surveyed exterior; not B restoration."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=10.;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.20
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':'2013 survey photo76 supports red walls; palette uncalibrated display proxy, not original1936 colour/material claim'}for i,(n,c) in enumerate([
('Survey red wall proxy','#A34F43'),('Coping and bands','#D4CFBC'),('Survey roof proxy','#999D95'),('Frames','#3F5146'),('Opaque glazing','#829A99'),('Dark blind backing','#333D3B'),('Survey metal cladding proxy','#8F5A53'),('Accent','#B5B9AC'),('Authored display support','#D1CABB'),('Neutral detail','#858779')])]
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
 if side=='C':add(name,faceprofile(section([[u0,z0],[u1,z0],[u1,z1],[u0,z1]]),'C',plane-.03,depth+.03),mat,ev)
 elif side in ('W','E'):
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


# Localx increases north-to-south, localy west-to-east. North arrow in sourceplan pointsleft.
W=11.44;D=9.19;CH=4.65;BELT=4.23;ROOF=8.33
POLY=[[CH,0],[W,0],[W,D],[0,D],[0,CH]]
def section(pts):
 p=np.array(pts,dtype=float)
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return mf.CrossSection((p*INTERNAL)[None,:,:].tolist())
def prism(poly,z,h):return section(poly).extrude(h*INTERNAL).translate([0,0,z*INTERNAL])
def faceprofile(cs,side,plane,depth):
 if side=='W':M=[[1,0,0,0],[0,0,-1,plane*INTERNAL],[0,1,0,0]]
 elif side=='E':M=[[1,0,0,0],[0,0,1,plane*INTERNAL],[0,1,0,0]]
 elif side=='N':M=[[0,0,-1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 elif side=='S':M=[[0,0,1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 else:
  q=1/math.sqrt(2);M=[[q,0,-q,(CH/2-plane*q)*INTERNAL],[-q,0,-q,(CH/2-plane*q)*INTERNAL],[0,1,0,0]]
 return cs.extrude(depth*INTERNAL).transform(M)
def around(name,z,h,offset,mat):
 cs=section(POLY);add(name,cs.offset(offset*INTERNAL).extrude(h*INTERNAL).translate([0,0,z*INTERNAL]),mat,'PDF200/201/204 mainpentagon continuousband; depth/profilegraphicalproxy')
add('Five-sided two-storey main body',prism(POLY,0,8.20),0,'A2-01PDF200 graphicalscale main11.44x9.19m with45degNWchamfer4.65m,±3%; notrectangularcentralprojection')
around('Textured plinth neutral proxy',0,.62,.035,7)
around('Main intermediate belt lower',4.02,.12,.14,1)
around('Main intermediate belt center',4.14,.18,.20,1)
around('Main intermediate belt upper',4.32,.10,.13,1)
around('Main roof slab and thin cornice',8.20,.13,.29,1)
# Flat roof has no invented continuous high parapet; only diagonal entrance crest rises.
cl=CH*math.sqrt(2)
panel('Raised diagonal entrance parapet','C',-.12,-cl/2,cl/2,8.19,9.25,.27,0,'PDF203/204 raisedentrancecrest9.25m, notall-aroundparapet')
panel('Entrance crest top coping','C',-.18,-cl/2-.15,cl/2+.15,9.14,9.28,.42,1,'PDF203 copingprofile approx; sourcecrest9.25m plusauthoredtrim3cm')
for z in[8.51,8.72,8.93]:
 for sign in[-1,1]:
  u=sign*(cl/2-.40);panel('Entrance crest short horizontal accent','C',.12,u-.38,u+.38,z,z+.055,.08,1,'PDF203 shortlineaccents nearcrestends, notinventedtext')
# East survey addition: full groundfloor but only southern upperpart; retain originalwalls hidden.
def slope_annex(name,x0,x1,y0,y1,zinner,zouter):
 pts=[[x,y,0]for x in[x0,x1]for y in[y0,y1]]+[[x,y0,zinner]for x in[x0,x1]]+[[x,y1,zouter]for x in[x0,x1]]
 add(name,hull(pts),6,'PDF200/201/204/205 latercorrugatedmetal eastannex, differentone/two-storeyportions; slopedcapgraphical')
 roofpts=[[x,y0,zinner-.10]for x in[x0-.08,x1+.08]]+[[x,y1,zouter-.10]for x in[x0-.08,x1+.08]]+[[x,y0,zinner+.03]for x in[x0-.08,x1+.08]]+[[x,y1,zouter+.03]for x in[x0-.08,x1+.08]]
 add(name+' thin sloping roof',hull(roofpts),2,'PDF204/205 annexslopingmetalcap, approximateprofile')
slope_annex('Northern one-storey eastannex',0,4.63,D-.04,D+2.10,3.88,3.54)
slope_annex('Southern two-storey eastannex',4.63,W,D-.04,D+2.10,8.08,7.79)
# Coarse corrugation ribs only; not claimed exact sheet pitch.
for x in np.arange(.1,W,.19):
 h=3.54 if x<4.63 else 7.79
 bx('Eastcladding coarse vertical rib',[x-.018,D+2.08,0],[x+.018,D+2.14,h],6,'PDF205 verticalcorrugation; ribpitch.19m enlargeddisplayproxy')
for x,side in[(0,'N'),(W,'S')]:
 for yy in np.arange(D+.1,D+2.05,.19):
  h=(3.88 if x==0 else 8.08)-(yy-D)/2.10*(.34 if x==0 else .29)
  panel('Annex side corrugation',side,x,yy-.018,yy+.018,0,h,.04,6,'PDF204/205 annexsidecorrugation proxy')
# Small permanent stair enclosure, single slope high atnorthend, not a water tank.
xa,xb=7.08,8.915;ya,yb=D-1.38,D-.25
pts=[[x,y,8.20]for x in[xa,xb]for y in[ya,yb]]+[[xa,y,10.31]for y in[ya,yb]]+[[xb,y,9.16]for y in[ya,yb]]
add('Roof stair enclosure under single slope',hull(pts),6,'PDF201 printed183.5x113cm roofstair,204/205 highnorth10.40/lowsouth9.25m, graphheight±3%')
add('Roof stair sloping cap',hull([[xa-.06,y,10.31]for y in[ya-.06,yb+.06]]+[[xb+.06,y,9.16]for y in[ya-.06,yb+.06]]+[[xa-.06,y,10.40]for y in[ya-.06,yb+.06]]+[[xb+.06,y,9.25]for y in[ya-.06,yb+.06]]),2,'PDF204/205 slopingstaircap, thickness9cmdisplayproxy')
recess('Roof stair north blind door proxy','N',xa,(ya+yb)/2,.68,8.40,1.55,.12,'PDF204 northroofstair door-likeface; neutralblinddoor,nointerior')
# Source roof circles are RC bases, not invented tanks.
for x,y in[(7.89,1.57),(9.30,1.57)]:add('Low circular RC roofbase proxy',cylinder(x,y,8.31,.13,.60,seg=48),7,'PDF201 circularRCbaselabel; low13cmheightproxy, looseequipmentnotreconstructed')
bx('Authored display base',[-1.25,-1.25,-BASE],[W+1.25,D+3.35,0],8,'2mm displaybase,notmeasuredboundary/neighborbuilding/terrain')

def rounded(name,side,plane,u,w,z,h,kind):
 if kind=='halfround':pts=[[u-w/2,z],[u+w/2,z]]+[[u+w/2*math.cos(t),z+h*math.sin(t)]for t in np.linspace(0,math.pi,25)]
 else:pts=[[u+w/2*math.cos(t),z+h/2+h/2*math.sin(t)]for t in np.linspace(0,2*math.pi,49)]
 c=section(pts);start=plane+.025 if side in('W','N')else plane-.025
 add(name+' opaque darkfield',faceprofile(c,side,start,.105),5,'A204/205 round/halfround vent orwindow; opaque blindfield proxy,not fullinterior')
 rim=c.offset(.042*INTERNAL)-c.offset(-.025*INTERNAL)
 add(name+' surround',faceprofile(rim,side,start,.15),1,'A204/205 circularframe relief,thicknessproxy')
 if kind=='halfround':panel(name+' central muntin',side,plane,u-.022,u+.022,z,z+h,.17,1,'A204/205 semicircle centralverticalmuntin')
 if kind=='circle':panel(name+' low horizontal bar',side,plane,u-w/2,u+w/2,z+h*.27-.022,z+h*.27+.022,.17,1,'A204 west lowerroundwindow lowhorizontalbar')
controls=json.loads((ROOT/'opening-positions.json').read_text())
for face,side,plane in[('west','W',0),('north','N',0),('south','S',W),('east','E',D)]:
 c=controls['faces'][face];entries=c['openings']+c.get('cladding_end_windows',[])
 for a in entries:
  name=face+' '+a['name'];u=a['center_host_m'];w=a['width_m'];z=a['bottom_z_m'];h=a['height_m'];kind=a['type']
  ev='A204/205 '+face+' independentlymeasuredcurrentopening;±3%,frame/paneproxy,notBrestoration'
  if kind=='rect':win(name,side,plane,u,w,z,h,a['columns'],a['rows'],ev)
  elif kind=='OPAQUE_INFILL_NOT_OPEN_DOOR':
   panel(name+' infill surround',side,plane,u-w/2-.055,u+w/2+.055,z,z+h+.055,.065,1,ev+'; source laterblockeddoor retainedclosed')
   panel(name+' opaque wall infill',side,plane,u-w/2,u+w/2,z,z+h,.09,0,ev+'; NOT a restoredopenpassage')
  else:rounded(name,side,plane,u,w,z,h,kind)
for a in controls['faces']['east']['cladding_windows']:
 win('eastcladding '+a['name'],'E',D+2.10,a['center_host_m'],a['width_m'],a['bottom_z_m'],a['height_m'],a['columns'],a['rows'],'A205 singleuppermetalwindow onouteradditionface,not hiddenoriginalwall')
# Windowheads and sills are short source bands, not perimeter-storey additions.
for side,plane,u0,u1,zz in[('W',0,4.88,7.91,6.52),('N',0,4.90,7.96,6.52),('S',W,4.04,8.18,6.52),('E',D,1.60,4.58,6.52),('W',0,4.85,6.94,3.32),('N',0,4.87,8.00,3.32)]:
 panel('Survey windowhead projecting band',side,plane,u0,u1,zz,zz+.11,.17,1,'A203–205 windowheadbands,depthprofileproxy')
# Chamfer windows stay on their single diagonal host, not flattened adjacentfacades.
ch=controls['faces']['NW_chamfer']
for a in ch['upper']:
 u=(a['t_from_north_endpoint']-.5)*cl
 win(a['name'],'C',0,u,a['width_m'],a['bottom_z_m'],a['height_m'],a['columns'],a['rows'],'A203 onlymiddlechamfer fourunequalfields; surveyjoinerynotrestoration')
 win(a['name']+' transom','C',0,u,a['width_m'],a['transom_bottom_z_m'],a['transom_height_m'],1,1,'A203 fourindependentuppertransoms')
panel('Chamfer upper mainwindow head','C',0,-2.30,2.30,6.76,6.88,.18,1,'A203 projectedwindowheadband')
panel('Chamfer upper transom head','C',0,-2.30,2.30,7.40,7.51,.20,1,'A203 transomheadband')
# Later shutter CLOSED and opaque noticeboards obscure original diamondwindows.
roller=ch['ground_door'];ww=roller['width_m'];hh=roller['height_m']
panel('Closed iron roller shutter','C',0,-ww/2,ww/2,0,hh,.09,9,'A203 closedrollerdoor,not restoredgreen doubledoor')
for zz in np.arange(.08,hh,.11):panel('Roller shutter coarse slat','C',0,-ww/2,ww/2,zz,zz+.028,.13,3,'A203 rollerslats, count/pitchproxy')
panel('Roller shutter head','C',0,-ww/2-.12,ww/2+.12,hh,hh+.11,.19,1,'A203 shutterhead')
for side in[-1,1]:
 for zz in np.arange(.35,hh,.23):
  u=side*(ww/2+.18);panel('Entrance short side rib','C',0,u-.16,u+.16,zz,zz+.045,.12,1,'A203 doorwayflank shortlineaccents')
for a in ch['noticeboards']:
 u=(a['t']-.5)*cl;w=a['width_m'];z=a['bottom_z_m'];h=a['height_m']
 panel('Noticeboard outerframe covering diamondwindow','C',0,u-w/2-.035,u+w/2+.035,z-.035,z+h+.035,.13,3,'A203 noticeboardobscuresoriginalW1; noexposeddiamondrestoration')
 panel('Blank opaque noticeboard','C',0,u-w/2,u+w/2,z,z+h,.16,1,'A203 blankboardproxy; unreadabletextnotinvented')
# Damaged policeemblem is a neutral disc, never a clock or inventedreadablebadge.
badge=ch['damaged_badge'];rad=badge['diameter_m']/2;uz=(badge['center_t']-.5)*cl;zz=badge['center_z_m'];c=section([[uz+rad*math.cos(t),zz+rad*math.sin(t)]for t in np.linspace(0,2*math.pi,49)])
add('Neutral damaged badge disc',faceprofile(c,'C',.12,.14),3,'A203 damagedpoliceemblem position; fineidentity/textnotreconstructed')
add('Badge pale circular rim',faceprofile(c.offset(.04*INTERNAL)-c.offset(-.03*INTERNAL),'C',.12,.19),1,'A203 damagedemblem rimproxy')
# Two low entrytreads are authored coarse footprintproxies alignedtochamfer.
for j in range(2):
 q=1/math.sqrt(2);u0,u1=-1.2,1.2;d0,d1=.0,.55-j*.18
 poly=[[(CH/2+u*q-d*q),(CH/2-u*q-d*q)]for u,d in[(u0,d0),(u1,d0),(u1,d1),(u0,d1)]]
 add('Entrance step '+str(j+1),prism(poly,0,.10+j*.10),1,'A203 twoentrancelevelchanges,dimensionsproxy notaccessibilitydesign')

# EXPORT_FINAL

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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Fengyuan Dingjie Police Station surveyed exterior2013-05');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'May2013 A-series surveyed two-storey pentagonal exterior with later one/two-storey eastcladding annex. Graphical dimensions±3%; roof RCbases are low proxies not tanks. No B restoration, hidden originaldiamondwindows, fullinteriors, sourceimagery, trialprint or safetyclaim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
