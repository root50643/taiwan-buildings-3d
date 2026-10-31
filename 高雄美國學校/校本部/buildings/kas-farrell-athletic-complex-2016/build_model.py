#!/usr/bin/env python3
"""KAS Farrell Athletic Complex exterior from 2016 architect-published plans and completion photographs; not an as-built survey."""
from pathlib import Path
import json,math,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent;SCALE=3.3333333333333335
PALETTE=[{'id': 'cladding', 'name': 'Light silver horizontal metal cladding', 'hex': '#C3C8CA', 'evidence': 'Architect-supplied completion photographs'}, {'id': 'concrete', 'name': 'White and pale gray concrete bands', 'hex': '#DDDCD5', 'evidence': 'Architect-supplied completion photographs'}, {'id': 'metal', 'name': 'Pale mullions and diagonal frame', 'hex': '#B8BFC0', 'evidence': 'Architect-supplied elevations and photographs'}, {'id': 'glass', 'name': 'Opaque blue gray glazing backing', 'hex': '#47616C', 'evidence': 'Printable opaque backing; no reconstructed interior'}, {'id': 'base', 'name': 'Authored printing base', 'hex': '#BBB8AA', 'evidence': 'Not survey terrain'}, {'id': 'screen', 'name': 'Dark service screen', 'hex': '#5E6464', 'evidence': 'West and south elevations'}, {'id': 'court', 'name': 'Roof sport surface', 'hex': '#668D8A', 'evidence': '2F plan confirms outdoor sport; color illustrative'}]
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(n,s,mat=1,e='Original architectural drawing, proportional simplified exterior detail'):
 
 if len(items)%50==0: print('construct',len(items),n,flush=True)
 s=s.translate([0,0,.5]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':n,'material':mat,'evidence':e})
def bx(n,a,b,mat=1):add(n,box(a,b),mat)
def polyxz(pts,y,d):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts=list(reversed(pts))
 return mf.CrossSection([pts]).extrude(d).rotate([90,0,0]).translate([0,y+d,0])
def polyyz(pts,x,d):return polyxz(pts,-x-d,d).rotate([0,0,90])
# Coordinate calibration from 2000px architect plans: graphic scale 0=330,10=449 px.
# Local x follows plan's long building axis; front (-y) is field-facing East elevation.
PPM=11.9
X=lambda u:(u-925)/PPM
Y=lambda v:(v-548)/PPM
L=X(495);R=X(1357);G=X(900);B=Y(986);GD=Y(875)
def plan(pts,z,h):
 ps=[[X(x),Y(y)] for x,y in pts]
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]+ps[:1]))<0:ps=ps[::-1]
 return mf.CrossSection([ps]).extrude(h).translate([0,0,z])
outline=[(495,548),(1357,548),(1357,986),(690,986),(690,891),(495,891)]
bx('Authored removable-flat printing support',[L-2,-2,-.5],[R+2,B+2,0],4)
body=plan(outline,0,4.8)
# Field-facing ground glazing and dining hall portal, actual continuous elevation rhythm.
body=body-box([L+.8,-.1,.32],[X(1000),.36,3.15])
body=body-box([X(1000),-.1,-.02],[R+.1,4.72,4.65])
body=body-box([X(1000),4.65,.32],[R-.8,5.05,3.15])
# South end of low wing: four dissimilar openings, not a mirrored front.
for ya,yb,z0,z1 in [(4.8,9,.3,3.1),(15,18,.15,3.3),(21,25.5,.15,3.3),(31.8,34.2,.15,3.3)]:
 body=body-box([R-.30,ya,z0],[R+.1,yb,z1])
# West/back retains broad solid walls with several small high windows.
for xa,xb,yy in [(L+.6,L+3.1,Y(891)),(X(723),X(738),B),(X(978),X(992),B),(X(1015),X(1028),B),(X(1140),X(1156),B),(X(1255),X(1278),B)]:
 z0=.15 if xa<L+4 else 3.8;z1=3.5 if xa<L+4 else 4.25
 body=body-box([xa,yy-.3,z0],[xb,yy+.1,z1])
body=body-box([R-2.8,B-.35,.1],[R-.4,B+.1,4.35])
# North entry/service door shown beside large exterior enclosed stair block.
body=body-box([L-.1,24.6,.1],[L+.32,26.8,3.2])
add('Complete L-plan ground exterior shell including kitchen and dining hall',body)
def frontwin(n,a,b,y,z,h,mat=3,step=1.05):
 bx(n+' opaque glazing',[a,y-.08 if 'West' in n else y,z],[b,y+.08 if 'West' in n else y+.16,z+h],mat)
 for zz in [z,z+h*.55,z+h-.06]:bx(n+' horizontal frame',[a,y-.035,zz],[b,y+.12,zz+.06],2)
 for xx in np.linspace(a,b,max(2,round((b-a)/step)+1)):bx(n+' mullion',[xx-.035,y-.035,z],[xx+.035,y+.12,z+h],2)
def sidewin(n,a,b,x,z,h):
 bx(n+' opaque glazing',[x if 'North' in n else x-.08,a,z],[x+.16 if 'North' in n else x+.08,b,z+h],3)
 for zz in [z,z+h-.06]:bx(n+' horizontal frame',[x-.035,a,zz],[x+.12,b,zz+.06],2)
 for yy in np.linspace(a,b,max(2,round(b-a)+1)):bx(n+' mullion',[x-.035,yy-.035,z],[x+.12,yy+.035,z+h],2)
frontwin('Field-facing pool ground glazing',L+.8,X(1000),.27,.32,2.83)
frontwin('Dining hall recessed portal glazing',X(1000),R-.8,4.95,.32,2.83)
# Explicit white stepped outline: upper low wing is dining hall, not another gym.
bx('Ground front sill',[L,-.18,.10],[R,.32,.40])
bx('Field-facing high fascia under gym',[L,-.18,3.15],[X(1000),.30,4.90])
bx('Dining hall front upper white portal',[X(1000),-.18,4.20],[R,.30,4.90])
bx('Dining hall portal left return',[X(995),-.20,3.15],[X(1005),.30,4.90])
for ya,yb,z0,z1 in [(4.8,9,.3,3.1),(15,18,.15,3.3),(21,25.5,.15,3.3),(31.8,34.2,.15,3.3)]:sidewin('South end distinct opening',ya,yb,R-.32,z0,z1-z0)
for xa,xb,yy in [(L+.6,L+3.1,Y(891)),(X(723),X(738),B),(X(978),X(992),B),(X(1015),X(1028),B),(X(1140),X(1156),B),(X(1255),X(1278),B)]:
 z0=.15 if xa<L+4 else 3.8;z1=3.5 if xa<L+4 else 4.25
 frontwin('West back door or high slit',xa,xb,yy-.29,z0,z1-z0,step=1.6)
frontwin('West far service door',R-2.8,R-.4,B-.29,.1,4.25)
sidewin('North service entry',24.6,26.8,L+.24,.1,3.1)
# Low roof and long field-side open canopy, dimensions estimated from published scale.
bx('Complete low wing roof deck',[G-.25,-.03,4.70],[R+.15,B+.12,5.02])
bx('Kitchen flat roof',[X(690),Y(875),4.70],[G+.15,B+.12,5.02])
bx('Pool field-side shallow canopy',[L-.3,-.65,4.65],[X(1000)+.1,.28,4.92])
bx('Dining hall deep porch canopy',[X(1000)-.1,-.18,4.65],[R+.12,5.05,4.92])
for xx in [X(1000),X(1100),X(1200),X(1300),R-.2]:bx('Dining hall deep porch structural pier',[xx-.27,-.18,0],[xx+.27,.37,4.85])
# Main gym: opaque printable backing at actual window band; no fabricated hidden interior.
gym=box([L,0,4.75],[G,GD,17.4])
gym=gym-box([L+.22,-.1,5.0],[G-.22,.34,7.55])
gym=gym-box([G-.34,4.7,5.0],[G+.1,GD-4.0,9.35])
gym=gym-box([L-.1,.6,5.0],[L+.34,3.8,7.55])
gym=gym-box([L-.1,GD-3.6,5.0],[L+.34,GD-.25,7.55])
# True shallow double-pitched roof, recessed inside parapets; not fully flat roof.
gym=gym-box([L+.30,.30,16.65],[G-.30,GD-.30,17.5])
add('High gym four-sided envelope with recessed windows and parapet',gym,0)
frontwin('East gym ribbon glass',L+.22,G-.22,.26,5.0,2.55)
sidewin('South gym central double-height door glazing',4.7,GD-4.0,G-.32,5.0,4.35)
sidewin('North short ribbon return',.6,3.8,L+.26,5.0,2.55)
sidewin('North rear ribbon return',GD-3.6,GD-.25,L+.26,5.0,2.55)
# V braces seen through field-facing glazing, expressed as exterior relief.
for xa,xb in zip(np.linspace(L+.35,G-.35,5)[:-1],np.linspace(L+.35,G-.35,5)[1:]):
 mid=(xa+xb)/2
 # Only lower ends of full-height V trusses emerge through the ribbon window.
 for p0,p1 in [((mid-.90,7.55),(mid,5.0)),((mid,5.0),(mid+.90,7.55))]:
  add('Window-band V structural relief',polyxz([(p0[0]-.20,p0[1]),(p0[0]+.20,p0[1]),(p1[0]+.20,p1[1]),(p1[0]-.20,p1[1])],.02,.31),1)
# North stair enclosure interrupts low glass; not a transparent symmetric end.
bx('North external stair solid enclosing wall',[L-1.55,4.0,0],[L+.06,GD-3.6,8.05])
bx('North stair lower return',[L-2.1,GD-5.2,0],[L+.05,GD-3.0,3.55])
# Thin canopy below metal gym envelope, clear in completion photos.
bx('High hall field-side projecting eave',[L-.55,-.65,7.50],[G+.5,.45,7.68],1)
bx('High hall south projecting eave',[G-.1,-.65,7.50],[G+.55,GD+.40,7.68],1)
bx('High hall north projecting eave',[L-.55,-.65,7.50],[L+.1,GD+.20,7.68],1)
# Horizontal silver cladding ribs; rear leaves central plain service strip per West drawing.
for z in np.arange(7.9,17.35,.48):
 bx('East silver horizontal rib',[L-.035,-.13,z],[G+.035,.06,z+.105],0)
 bx('North silver horizontal rib',[L-.13,.0,z],[L+.06,GD,z+.105],0)
 
 if z>=9.55:bx('South silver horizontal rib',[G-.06,.0,z],[G+.13,GD,z+.105],0)
 else:
  for ya,yb in [(0,4.7),(GD-4.0,GD)]:bx('South end solid cladding returns',[G-.06,ya,z],[G+.13,yb,z+.105],0)
 for a,b in [(L,X(738)),(X(799),G)]:bx('West silver rib with plain central interruption',[a,GD-.06,z],[b,GD+.13,z+.105],0)
# Gable roof sits behind low parapet and is supported by hidden solid shell.
add('Shallow double pitched high hall roof',polyyz([(.28,16.6),(.28,16.95),(GD/2,17.35),(GD-.28,16.95),(GD-.28,16.6)],L+.28,G-L-.56),0)
# Service/screen block behind hall and stair offices beside the roof court.
bx('Rear mechanical screened enclosure',[X(700),GD-.1,4.8],[X(1000),B-.5,9.6],5)
for z in np.arange(5.1,9.6,.22):bx('Rear screen horizontal rail',[X(700)-.05,B-.60,z],[X(1000)+.05,B-.34,z+.06],2)
for xx in np.linspace(X(700),X(1000),6):bx('Rear screen upright',[xx-.045,B-.62,4.95],[xx+.045,B-.32,9.6],2)
bx('Roof stair headhouse',[X(932),Y(597),4.85],[X(1005),Y(666),8.95],1)
bx('Roof side storage enclosure',[X(932),Y(790),4.85],[X(1005),Y(875),8.0],1)
# Actual roof outdoor court is unroofed; simple opaque surface and perimeter railing.
bx('Outdoor roof sport surface',[X(1063),Y(575),5.005],[X(1310),Y(958),5.045],6)
def railx(a,b,y):
 bx('Roof court rail top',[a,y-.055,6.05],[b,y+.055,6.15],2)
 for xx in np.arange(a,b+.01,1.55):bx('Roof court rail upright',[xx-.055,y-.055,4.98],[xx+.055,y+.055,6.12],2)
def raily(a,b,x):
 bx('Roof court rail top',[x-.055,a,6.05],[x+.055,b,6.15],2)
 for yy in np.arange(a,b+.01,1.55):bx('Roof court rail upright',[x-.055,yy-.055,4.98],[x+.055,yy+.055,6.12],2)
railx(G+.1,R-.1,.05);railx(X(1003),R-.1,B-.12);raily(.05,B-.12,R-.12)
# Sports markings are shallow color strips only, not guessed equipment or tall cages.
ca=X(1120);cb=X(1250);ya=Y(625);yb=Y(905)
for xx in [ca,cb]:bx('Roof sport white boundary',[xx-.025,ya,5.041],[xx+.025,yb,5.057],1)
for yy in [ya,yb,(ya+yb)/2]:bx('Roof sport white boundary',[ca,yy-.025,5.041],[cb,yy+.025,5.057],1)
print('CONSTRUCTION COMPLETE',len(items),flush=True)
for o,i in zip(ops,items):assert i.status()==mf.Error.NoError,(o,i.status())
print('UNION START',flush=True)
# Sequential exact CSG avoids batched coplanar triangulation artifacts on long glazing.
s=items[0]
for part in items[1:]:s=s+part
print('UNION END',flush=True)
assert s.status()==mf.Error.NoError,s.status()
print('SIMPLIFY START',flush=True)
s=s.set_tolerance(.000001)
print('SIMPLIFY END',flush=True)
print('FIRST MESH START',flush=True)
m=s.to_mesh64()
print('FIRST MESH END',len(m.tri_verts),flush=True)
# Quantize into STL's actual float32-mm precision before final topology simplification.
# This removes sub-precision CSG seam slivers rather than shipping a broken float32 STL.
qv=np.ascontiguousarray((np.asarray(m.vert_properties)*SCALE).astype(np.float32).astype(np.float64))
qm=mf.Mesh64(qv,np.array(m.tri_verts,dtype=np.uint64,order="C",copy=True),merge_from_vert=np.array(m.merge_from_vert,dtype=np.uint64,copy=True),merge_to_vert=np.array(m.merge_to_vert,dtype=np.uint64,copy=True),run_index=np.array(m.run_index,dtype=np.uint64,copy=True),run_original_id=np.array(m.run_original_id,dtype=np.uint32,copy=True),tolerance=.002)
print('QUANTIZED SIMPLIFY START',flush=True)
qs=mf.Manifold(qm);print('QUANTIZED SIMPLIFY END',flush=True);assert qs.status()==mf.Error.NoError,qs.status()
# Keep all meaningful components. Only discard numerical face islands after welded
# mesh extraction, using direct signed-volume calculation rather than slow per-part CSG.
print('FINAL MESH START',flush=True)
m=qs.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Weld duplicate material-boundary positions, retaining each surface triangle's real original material.
v,inv=np.unique(np.round(v,9),axis=0,return_inverse=True);f=inv[f]
# Float32 quantization can collapse coincident seam triangles to exact zero area.
# Remove only exact collinear triangles; do not simplify positive-area surfaces.
area2=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
zero=area2==0
print('EXACT ZERO AREA SEAM FACES REMOVED',int(zero.sum()),flush=True)
f=f[~zero];mi=mi[~zero]
parents=np.arange(len(v))
def find(i):
 while parents[i]!=i: parents[i]=parents[parents[i]];i=parents[i]
 return i
for tri in f:
 rr=[find(int(k)) for k in tri];parents[rr[1]]=rr[0];parents[rr[2]]=rr[0]
labels=np.array([find(int(tri[0])) for tri in f]);compids=np.unique(labels)
facevol=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]]))/6
volumes={int(k):float(facevol[labels==k].sum()) for k in compids}
crumb_ids=[k for k,vol in volumes.items() if abs(vol)<.001]
assert sum(abs(volumes[k]) for k in crumb_ids)<.01,volumes
keep=~np.isin(labels,crumb_ids);f=f[keep];mi=mi[keep]
meaningful_components=len(compids)-len(crumb_ids)
print('COMPONENT VOLUMES',volumes,'removed numerical',len(crumb_ids),flush=True)
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape((-1,3))
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='KAS Thomas Farrell Athletic Complex 2016 exterior reconstruction');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':meaningful_components,'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2016 architect-published exterior reconstruction; graphic-scale estimated dimensions, opaque glazing, authored support; not as-built or current-state'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

