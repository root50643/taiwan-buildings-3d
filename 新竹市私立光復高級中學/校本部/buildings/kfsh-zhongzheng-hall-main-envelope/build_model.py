#!/usr/bin/env python3
"""KFSH Zhongzheng hall envelope; official photos plus schematic plan, nominal dimensions."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('wall','Pale warm masonry','#B5AAA0','Opposite facade photo; approximate'),
('roof','White curved roof','#E9E9E2','Both exterior photos'),
('glass','Pale green opaque glazing','#A2B6B0','Front opaque glass approximation, no transparent simulation'),
('steel','Blue grey frames and bands','#718697','Tower bands and open roof rings'),
('dark','Dark door and window panels','#515C5B','Visible entry and masonry-side windows'),
('base','Grey plinth and authored support','#999997','Visible steps; authored base perimeter not surveyed')]]
SCALE=13.0
P={'main_width':10,'main_depth':8,'wall_height':4.5,'roof_rise':1.5,'tower_radius':.88,'tower_centres':[[-5,-4],[5,-4],[-5,4],[5,4]],'nominal_scale_mm_per_unit':13,'surveyed':False}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.2]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Official source photo; nominal proportions, not measured'):add(name,box(a,b),mat,evidence)
def cyl(r,h,x,y,z,n=48):return mf.Manifold.cylinder(h,r,r,n).translate([x,y,z])
def annulus(ro,ri,h,x,y,z):return (mf.Manifold.cylinder(h,ro,ro,48)-mf.Manifold.cylinder(h+.02,ri,ri,48).translate([0,0,-.01])).translate([x,y,z])
# Schematic map identifies four round corner appendages; rounded main outline not surveyed.
pts=[]
for cx,cy,start in [(4.5,3.5,0),(-4.5,3.5,90),(-4.5,-3.5,180),(4.5,-3.5,270)]:
 for a in np.linspace(start,start+90,9):pts.append([cx+.5*math.cos(math.radians(a)),cy+.5*math.sin(math.radians(a))])
bx('Authored continuous display slab',[-6.2,-5.4,-.2],[6.2,5.25,0],5,'Authored connected base, not actual pavement extent')
add('Rounded principal hall body',mf.CrossSection([pts]).extrude(4.5),0,'Official schematic map footprint and both facades; depth nominal')
# Elliptical shallow cap, not a claim of a measured semicylinder or engineered membrane.
dome=mf.Manifold.sphere(1,48).scale([5.25,4.25,1.5]).translate([0,0,4.45])
dome=dome^box([-6,-5,4.43],[6,5,6.1])
add('Nominal shallow elliptic white roof cap',dome,1,'Visible white curved roof; curvature and hidden framing intentionally simplified')
# Four towers have lower glazed cylinders and open circular top frames.
for ti,(x,y) in enumerate(P['tower_centres']):
 add(f'Tower {ti+1} cylindrical envelope',cyl(.88,4.55,x,y,0),2,'Four round appendages corroborated by campus map; cylindrical finish seen in two photos')
 add(f'Tower {ti+1} base plinth',cyl(.91,.25,x,y,0),5,'Grey ground plinth, nominal')
 for z in [1.55,3.12,4.32]:add(f'Tower {ti+1} blue grey belt {z}',cyl(.925,.16,x,y,z),3,'Visible horizontal rings; nominal heights')
 for j in range(10):
  ang=2*math.pi*j/10;xx=x+.885*math.cos(ang);yy=y+.885*math.sin(ang)
  add(f'Tower {ti+1} representative vertical mullion {j}',cyl(.026,4.25,xx,yy,.20,8),3,'Representative regular tower frame divisions, not measured count')
 # Upper louver band simplified as continuous bands, not hidden mechanical detail.
 for z in [1.80,1.92,2.04,2.16,3.48,3.62,3.76,3.90]:add(f'Tower {ti+1} upper louver ring {z}',cyl(.90,.035,x,y,z),0,'Visible louver-belt color and fine lines simplified')
 for j in range(8):
  ang=2*math.pi*j/8;xx=x+.82*math.cos(ang);yy=y+.82*math.sin(ang)
  bx(f'Tower {ti+1} open top upright {j}',[xx-.045,yy-.045,4.44],[xx+.045,yy+.045,5.65],3,'Visible open circular roof frame; representative support spacing')
 add(f'Tower {ti+1} open top ring',annulus(1.02,.83,.14,x,y,5.59),3,'Open top canopy ring visible; no solid roof inserted')
# Front glass curtain wall and visible central entrance.
bx('Front opaque pale glass curtain wall',[-4.25,-4.055,1.55],[4.25,-3.98,4.45],2,'Glass facade photo; opaque panel representation')
for x in np.linspace(-4.2,4.2,11):bx('Front visible curtain wall vertical frame',[x-.018,-4.08,1.55],[x+.018,-4.02,4.45],3,'Simplified photo grid')
for z in [1.55,2.25,2.98,3.71,4.42]:bx('Front curtain wall horizontal frame',[-4.25,-4.08,z-.018],[4.25,-4.02,z+.018],3)
for x in [-2.5,-1.55,-.6,.6,1.55,2.5]:
 bx('Front visible dark entry panel',[x-.4,-4.06,.22],[x+.4,-3.99,1.60],4)
 bx('Front entry door mullion',[x-.018,-4.09,.22],[x+.018,-4.01,1.62],3)
bx('Front shallow entry canopy',[-3.3,-4.55,1.62],[3.3,-3.97,1.73],3,'Visible slender entry canopy, nominal depth and framing')
for j in range(3):bx('Front entry step '+str(j),[-3.5,-4.86+j*.16,0],[3.5,-3.98,.08+j*.07],5,'Visible low entry steps, nominal tread count and rise')
# Two white horizontal grilles flank the lower entrance, directly visible in photo1.
for a,b in [(-4.25,-3.35),(3.35,4.25)]:
 bx('Front grille dark backing',[a,-4.055,.22],[b,-3.99,1.55],4,'Visible lateral grille recess')
 for z in np.linspace(.30,1.50,9):bx('Front white horizontal grille bar',[a,-4.10,z-.025],[b,-4.025,z+.025],1,'Photo1 white horizontal grilles; bar count simplified')
 for x in [a,b]:bx('Front white grille side rail',[x-.025,-4.10,.24],[x+.025,-4.025,1.55],1)
# Rear masonry facade, deliberately different from the glass facade.
bx('Rear horizontal fascia',[-4.3,3.99,3.85],[4.3,4.10,4.42],0,'Masonry facade top band seen in second photo')
for x in np.linspace(-3.9,3.9,9):
 bx('Rear visible vertical masonry pier',[x-.10,3.99,.18],[x+.10,4.14,3.85],0,'Visible vertical bay piers; nominal representative spacing')
for x in [-3.35,-2.5,-1.65,-.8,.8,1.65,2.5,3.35]:bx('Rear high dark window',[x-.16,3.99,2.35],[x+.16,4.075,3.75],4,'Visible narrow window bays, nominal subdivisions')
for x in [-2.4,2.4]:
 bx('Rear visible door group',[x-.6,3.99,.20],[x+.6,4.08,1.78],4)
 bx('Rear door canopy',[x-.75,3.99,1.75],[x+.75,4.48,1.92],0,'Two entry groups visible, nominal shallow canopy')
bx('Rear central darker square panel',[-.85,3.99,1.85],[.85,4.08,3.75],5,'Visible darker central masonry panel, no guessed lettering')
# Unseen short-side elevations remain plain; no fabricated entrances or window repetitions.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.01).simplify(.01)
m=s.to_mesh64();print('raw status',s.status(), 'merge',len(m.merge_from_vert));v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Collapse negligible coplanar material seams before export, preserving the true surface.
# Assign palette deterministically by nearest original triangle centroid after geometric cleanup.

old_centres=v[f].mean(axis=1); old_mi=mi.copy()
s=s.as_original().set_tolerance(.001).simplify(.001)
clean=s.to_mesh64();v=np.asarray(clean.vert_properties)[:,:3]*SCALE;f=np.asarray(clean.tri_verts)
centres=v[f].mean(axis=1); near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
q=mf.Manifold(mf.Mesh(np.round(v,2).astype(np.float32),np.asarray(f,dtype=np.uint32)))
print('grid cleanup',q.status())
qc=q.to_mesh(); v=np.asarray(qc.vert_properties)[:,:3];f=np.asarray(qc.tri_verts)
centres=v[f].mean(axis=1);near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-10;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='KFSH Zhongzheng hall principal envelope');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Principal envelope from official opposing exterior photos and schematic campus map; four corner towers. Nominal roof curvature and depth, unseen short walls simplified without invented fenestration.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
