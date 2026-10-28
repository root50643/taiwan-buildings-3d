#!/usr/bin/env python3
"""Takao lower consular office, source-based simplified exterior; NOT hilltop residence."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('brick','Exposed redbrick','#8E5142','Official and2019photos; uncalibratedbrickcolor'),('white','White plaster arcades','#E8E5DA','Officialcompletedofficephoto'),('glass','Dark opaque glazing','#435455','Historicalphotos; solidprintinlay'),('roof','Terracotta roof','#B76E4B','Official and2019completedphotos; coarse tile rows'),('base','Authored display support','#AAAFA5','Authorbase NOT true site'),('frame','Off-white shutters','#CCCFC4','Photographed louveredshutters; coarse slats'),('floor','Veranda tile and stone','#AE8B73','2019photographed redtileveranda; uncalibrated')]]
SCALE=.08
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
# Localx west->east, y southfront->north. Physicalrange calibrated to reported facade segments.
W=18.16;D=24.4
bx('Authored display base',[-1.3,-1.4,-.6],[W+1.3,D+1.3,0],4,'Authored rectangular support; garden/prisonarchaeologicaldeck excluded')
bx('L southern plinth',[0,0,0],[W,9.62,.60],1,'Reportfig4-16 frontsegments summed18.16m, shortside9.617m; simplifiedplinth')
bx('L western plinth',[0,9.5,0],[8.1,D,.60],1,'Reportfig4-16 longarcade24.4m; westwingwidth tracedfromfig5-3A')
bx('Southern veranda floor',[.05,.05,.57],[W-.05,9.58,.69],6,'Completedphotographs redtilefloors; authoredsolidplane')
bx('Western veranda floor',[.05,9.5,.57],[8.05,D,.69],6,'L-shapedveranda raisedfloor')
bx('Southern office redbrick enclosure',[2.05,2.15,.64],[W-2.05,9.3,4.66],0,'Officialplan mainofficerooms behindthree-sidedarcade; interioromitted')
bx('Western office wing redbrick enclosure',[2.05,9.15,.64],[7.85,D-.25,4.66],0,'Officialplanpatrolrooms wing; restorationphotocrosscheck')
# Three arcades retain genuinely open holes, not applied dark markings.
front=[1.367,2.276,.595,2.285,1.433,2.260,1.387,2.286,.586,2.281,1.404]
west=list(reversed([.791,1.844,.467,1.832,.467,1.812,.484,2.143,.463,2.149,.464,2.135,.49,2.139,.489,2.321,.494,1.999,1.417]))
east=[1.423,1.879,.583,1.836,.597,1.841,1.458]
def arcade(name,segments,axis,offset,length):
 s=box([0,0,.65],[length,.36,4.65]);pos=0;piers=[]
 for j,w in enumerate(segments):
  mid=pos+w/2
  if j%2==1:s=s-arch(w,.63,3.214,.50).translate([mid*100,0,0])
  else:
   piers.append((pos,w))
   if w>1.2:s=s-box([mid-.10,-.3,.70],[mid+.10,.65,3.47])
  pos+=w
 if axis=='y':s=s.rotate([0,0,90]).translate([offset*100,0,0])
 add(name,s,1,'Reportfig4-16 measuredsegments; shallowsegmentarches confirmedasbuilt2019; openingskeptreal')
 for j,(a,w)in enumerate(piers):
  # Use full-width base; twin shaft slots remain visible above it.
  for z0,z1,extra in [(.65,.92,.035),(2.98,3.08,.055),(3.14,3.23,.085)]:
   q=box([a-extra,-.055,z0],[a+w+extra,.41,z1])
   if w>1.2 and z0>.95:q=q-box([a+w/2-.10,-.3,z0-.01],[a+w/2+.10,.7,z1+.01])
   if axis=='y':q=q.rotate([0,0,90]).translate([offset*100,0,0])
   add(name+' piermoulding'+str((j,z0)),q,1,'Reportp51column2.564m abovefloor, base0.273m andtwoprojectingcapitalbands; coarseprofiles')
arcade('Southfront arcade',front,'x',0,sum(front))
arcade('Westlong arcade',west,'y',.36,sum(west))
arcade('Eastshort arcade',east,'y',W,sum(east))
# Plaster dado below exposed brick remains visible in the open arcades.
bx('Front inner white dado',[2.0,2.10,.65],[W-2.0,2.19,1.65],1,'Photo whiteplasterlowerinnerwall')
bx('West inner white dado',[1.99,2.10,.65],[2.10,D-.2,1.65],1,'Photo whiteplasterbase under redbrick')
bx('East inner white dado',[W-2.10,2.10,.65],[W-1.99,9.3,1.65],1,'Photo innerwall white lowerband')
# Front3 openings and sidebays from officialfloorplan, coarse shutters outside solidglazing.
def window(name,c,ang,width=1.35,door=False):
 x,y=c;bottom=.68 if door else 1.55;top=3.62
 q=box([-width/2,-.04,bottom],[width/2,.08,top]).rotate([0,0,ang]).translate([x*100,y*100,0]);add(name+' darkinlay',q,2,'Officialplan opening and photographedshuttertype; solidglazing dimensionsapproximate')
 for side in [-1,1]:
  a=side*(width/2+.25)
  q=box([a-.23,-.13,bottom],[a+.23,.15,top]).rotate([0,0,ang]).translate([x*100,y*100,0]);add(name+' shutter'+str(side),q,5,'Photographedoffwhiteoutwardshuttersrepresentednearwall; not precisemechanism')
  for z in np.arange(bottom+.12,top-.04,.20):
   q=box([a-.21,-.19,z],[a+.21,-.08,z+.055]).rotate([0,0,ang]).translate([x*100,y*100,0]);add(name+' coarse louver'+str((side,round(z,2))),q,5,'Visible louveredshutters; coarsepitchandenlarged0.44mm relief, not actualslatcount')
 q=box([-.035,-.10,bottom],[.035,.12,top]).rotate([0,0,ang]).translate([x*100,y*100,0]);add(name+' centerframe',q,5,'Simplifiedframedwindow')
window('Southwest window',(5.2,2.06),0)
window('Main entrance',(W/2,2.06),0,1.8,True)
window('Southeast window',(13.1,2.06),0)
for j,y in enumerate([3.5,6.6,10.0,13.1,16.3,19.3,22.1]):window('Westwindow'+str(j),(2.0,y),-90,1.25,j==5)
for j,y in enumerate([3.5,6.7]):window('Eastwindow'+str(j),(W-2.0,y),90,1.25)
# Mainroof and longitudinalwing meet as a hip/gable L, not a single rectangularslab.
add('Southmain hippedroof',hip(-.3,W+.3,-.3,9.75,4.62,7.16),3,'Reportfig4-16 and builtphoto hippedtilemainroof; ridgeheightestimatedfromscaledfront elevation')
add('Westwing gabledroof',hull([[-.3,4.7,4.62],[8.2,4.7,4.62],[8.2,D,4.62],[-.3,D,4.62],[3.95,4.7,7.16],[3.95,D,7.16]]),3,'Officialsideelevation continuouslongroof northgable retained; width/roofintersection tracedapproximate')
# Ridge caps and coarse tile courses on visible roof surfaces.
add('Main ridgecap',beam([3.95,4.725,7.17],[W-3.95,4.725,7.17],.10),3,'Photo tiledridge cap, simplifiedcontinuous')
add('Longwing ridgecap',beam([3.95,4.72,7.17],[3.95,D,7.17],.10),3,'Photo longroof ridgecap')
for j in range(1,12):
 t=j/12;z=4.62+2.54*t;y=-.3+5.025*t;x0=-.3+4.25*t;x1=W+.3-4.25*t
 add('Mainfront coarse tilecourse'+str(j),beam([x0,y,z+.015],[x1,y,z+.015],.045),3,'Photo tiletexture interpreted as coarsecourses, not exactindividualtiles')
for j in range(1,10):
 t=j/10;z=4.62+2.54*t
 for x in [-.3+4.25*t,8.2-4.25*t]:add('Longroof coarse tilecourse'+str((j,x)),beam([x,8.8,z+.015],[x,D,z+.015],.045),3,'Coarse tilecourses, enlarged')
# Low courtyardservicevolumes visible in plan and2019rearphotograph, not rebuiltprison.
bx('Northern small service enclosure',[7.7,18.0,0],[11.3,D,2.8],1,'Officialfig5-3A inner servicecells; dimensionsestimatedtracing, nointeriors')
add('Northern service lean-to roof',hull([[7.6,17.9,2.78],[11.5,17.9,2.78],[11.5,D,2.78],[7.6,D,2.78],[7.6,17.9,4.0],[7.6,D,4.0],[11.5,17.9,3.0],[11.5,D,3.0]]),3,'2019rearphoto lowerleanroof, officialsection; slopeapproximate')
bx('Eastservice enclosure',[11.0,9.0,0],[W,12.6,2.85],1,'Officialplan two small rooms atfrontcourtyardedge; elevationsapproximate')
add('Eastservice leanroof',hull([[10.9,9.0,2.82],[W+.1,9.,2.82],[W+.1,12.8,2.82],[10.9,12.8,2.82],[10.9,9.,4.4],[W+.1,9.,4.4],[10.9,12.8,3.0],[W+.1,12.8,3.0]]),3,'Officialsideelevation lowroomleanroof; simplified')
bx('Courtyard east boundarywall',[W-.2,12.5,0],[W,D,1.8],1,'Officialplan boundarywall, heightestimated, no unverifiedmodernadjoiningbuildings')
bx('Courtyard north boundarywall',[11.2,D-.2,0],[W,D,1.8],1,'Officialplan courtyard northwall; restoredphoto')
# Existing north termination wall with exposed cut brick edge, not new prison rooms.
add('Retained northern gable wall',hull([[0,D-.35,.55],[8.1,D-.35,.55],[8.1,D+.04,.55],[0,D+.04,.55],[0,D-.35,4.8],[8.1,D-.35,4.8],[0,D+.04,4.8],[8.1,D+.04,4.8],[3.95,D-.35,7.42],[3.95,D+.04,7.42]]),1,'2019rearphotograph survivingtallgablewall, no inferredprisonroof')
for k in range(9):bx('North brokenbrick edge'+str(k),[7.88-(k%2)*.10,D-.02,.65+k*.43],[8.12,D+.09,1.02+k*.43],0,'Visible exposedbrick cutedge represented coarsealternatingtooth, not exactdamageprofile')
bx('Historic chimney',[6.1,13.7,5.3],[6.7,14.3,8.0],0,'2019rearphoto shows brickchimney; planlocation andheightestimated')
bx('Chimney cap',[6.02,13.62,7.93],[6.78,14.38,8.12],0,'Photo chimney cap; enlarged')
for k in range(3):bx('Mainentrance step'+str(k),[W/2-1.25,-1.05+k*.3,0],[W/2+1.25,.1,.2*(k+1)],1,'Officialreport3steps, heightsapproximate')
# Crest given a plain small plaque silhouette; no invented coatofarms detail.
bx('Frontcrest plain plaque',[W/2-.25,-.06,3.95],[W/2+.25,.10,4.46],6,'Visible crestlocation; heraldicdetaildeliberatelyomitted, not invented')
# Visible rearthreshold and serviceopenings, coarse solidinlays.
bx('North retained entrance dark aperture',[2.2,D-.03,.65],[6.8,D+.08,3.45],2,'2019rearphoto darkopening underprojectinglintel; widthestimated, solidinlaynotfullinterior')
bx('North short protective lintel canopy',[2.0,D-.1,3.45],[7.0,D+.65,3.61],5,'2019rearphoto slimcanopy over retainedthreshold; projectionestimated')
for j,y in enumerate([19.0,21.25,23.2]):
 bx('Northern service window'+str(j),[11.27,y-.42,1.0],[11.36,y+.42,2.15],2,'2019rearphoto smallwindowrow underleanroof; approximateposition')
 for z in np.arange(1.10,2.12,.20):bx('Servicewindow slat'+str((j,z)),[11.34,y-.43,z],[11.43,y+.43,z+.055],5,'Photographed lightshutters; coarsenedslatcount')
bx('East smallservice door',[W-.02,10.0,.05],[W+.09,11.15,2.35],2,'Officialsideelevation service door; simplifieddarksolidpanel')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.05).simplify(.05)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Takao British consulate lower office exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official2008investigation plans/elevation dimensions with undated official completed-building photo and2019asbuiltphotos. ExistingL-shapedoffice only; demolishednorthernprisonnotreconstructed. Roof/hidden details approximate; no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
