#!/usr/bin/env python3
"""NHU principal gate; official front photo and exterior/interior VR constrained approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('pier','Warm ivory piers','#D6CFB7','Official photo ivory finish; uncalibrated approximate color'),
('stone','Brown stone beams and eaves','#8C776C','Official front photograph and VR eaves'),
('lattice','Muted red diamond grille','#824D43','Permanent lattice seen in front and rear official VR'),
('inset','Grey inset panels','#73796F','Front octagonal pier decoration, relief simplified'),
('base','Authored neutral display base','#B3AB9D','Not a reconstruction of roadway'),
('display','Unlettered dark display panel','#3E4441','Visible front LED housing; no text or display content reproduced'),
('inner','Grey inner pier panel','#95998F','Observed grey inset; no relief pattern invented')]]
SCALE=12.0
P={'opening_width':10.,'opening_height':6.,'pier_width':1.0,'pier_depth':1.35,'lower_eave_width':13.4,'lower_eave_depth':2.1,'upper_eave_width':9.0,'upper_eave_depth':1.65,'nominal_scale_mm_per_unit':12,'source':'Official NHU front image plus node50 front-oblique and node44 reverse VR; nominal proportions, not survey'}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.22]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportional nominal dimensions, not measured'):add(name,box(a,b),mat,evidence)
def prism_xz(points,y,depth):return mf.CrossSection([points]).extrude(depth).rotate([90,0,0]).translate([0,y+depth,0])
def bar(name,a,b,y,mat=2,width=.055,depth=.08):
 a=np.array(a);b=np.array(b);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)*width/2
 add(name,prism_xz([list(a-n),list(b-n),list(b+n),list(a+n)],y,depth),mat,'Representative diamond lattice; fine count and widths simplified, not exact copy')
def eave(name,half,yhalf,z):
 # Upturned ends are visible; nominal extruded profile, no invented tiles or hidden trusses.
 xs=[-half,-half+.38,-half+.65,half-.65,half-.38,half]
 zs=[z+.16,z+.03,z,z,z+.03,z+.16]
 pts=list(zip(xs,[a-.13 for a in zs]))+list(zip(xs[::-1],[a+.035 for a in zs[::-1]]))
 add(name,prism_xz(pts,-yhalf,2*yhalf),1,'Visible long eave with upturned ends; depth constrained by oblique official VR, simplified solid surface')
bx('Authored display base',[-6.5,-1.25,-.22],[6.5,1.25,0],4,'Authored connectivity base, not road surface')
for side in [-1,1]:
 x=side*5.5
 bx('Pier footing '+str(side),[x-.57,-.75,0],[x+.57,.75,.16],1)
 bx('Main ivory pier '+str(side),[x-.5,-.675,.1],[x+.5,.675,7.45],0,'Vertical main pier; photographed apparent taper is not treated as measured slant')
 # Slightly raised representative octagonal surround; original recessed detail simplified.
 pts=[[-.36,.45],[-.44,.85],[-.44,2.95],[-.30,3.4],[.30,3.4],[.44,2.95],[.44,.85],[.36,.45]]
 pts=[[a+x,b]for a,b in pts[::-1]]
 add('Front grey octagonal surround '+str(side),prism_xz(pts,-.73,.065),3,'Visible grey elongated octagonal motif; recess depth represented as shallow relief, no inscription')
 pts2=[[x+(a-x)*.72,1.9+(b-1.9)*.80]for a,b in pts]
 add('Front inner grey octagonal panel '+str(side),prism_xz(pts2,-.75,.028),6,'Representative inner panel; no measured relief claim')
bx('Lower spanning stone beam',[-5.55,-.73,6.0],[5.55,.73,6.55],1)
bx('Unlettered front display panel',[-3.95,-.758,6.12],[3.95,-.721,6.43],5,'Plain dark panel records visible fixed housing only; no LED lettering')
bx('Upper spanning stone beam',[-5.8,-.73,7.38],[5.8,.73,7.65],1)
# Open central grille on front and back; avoid an invented solid wall.
for y in [-.71,.63]:
 for i in range(12):
  x=-4.8+i*.8
  bar('Grille rising '+str(y)+'-'+str(i),(x,6.55),(x+.8,7.38),y)
  bar('Grille falling '+str(y)+'-'+str(i),(x,7.38),(x+.8,6.55),y)
 bx('Grille left boundary '+str(y),[-4.85,y,6.52],[-4.78,y+.08,7.4],2)
 bx('Grille right boundary '+str(y),[4.78,y,6.52],[4.85,y+.08,7.4],2)
eave('Lower long upturned eave',6.7,1.05,7.68)
# Raised narrow upper tier seen in all three reference views.
bx('Upper tier shallow stone body',[-4.2,-.61,7.68],[4.2,.61,8.12],1,'Visible raised upper tier; no hidden roof construction')
eave('Upper short upturned eave',4.5,.82,8.14)

for o,i in zip(ops,items):
 assert i.status()==mf.Error.NoError,(o,i.status())
s=items[0]
for o,i in zip(ops[1:],items[1:]):
 s=s+i
 assert s.status()==mf.Error.NoError,(o,s.status())
s=s.set_tolerance(.001).simplify(.001)
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NHU main gate');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete principal gate structure, source-proportional nominal dimensions; no guardhouse, walls, temporary signs or exact decorative replication.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
