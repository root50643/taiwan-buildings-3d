#!/usr/bin/env python3
"""NUTN centenary bell tower: multi-angle photograph-informed, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('frame','Warm white frame','#D9D8CD','Official exterior photos; uncalibrated approximate material color'),
('stairs','Pale stairs and balcony','#C6C8BF','Official exterior photos; nominal finish'),
('bell','Patinated bell','#467567','Visible green patinated bell; detail lettering omitted'),
('base','Authored base','#B1A796','Authored display base, not surveyed terrain')]]
SCALE=12.0
P={'main_height':8.4,'front_post_x':2.0,'front_post_y':-.65,'rear_post_y':2.81,'balcony_z':4.8,'stair_start_deg':-50,'stair_end_deg':165,'stair_steps':28,'stair_inner_r':.45,'stair_outer_r':1.28}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.32]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportional interpretation, not measured'):add(name,box(a,b),mat,evidence)
def prism(points,z,h):return mf.CrossSection([points]).extrude(h).translate([0,0,z])
def beam(a,b,width,z,h):
 a=np.array(a);b=np.array(b);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)*width/2
 return prism([list(a-n),list(b-n),list(b+n),list(a+n)],z,h)
def sector(ri,ro,a,b,z,h):
 aa=np.linspace(math.radians(min(a,b)),math.radians(max(a,b)),max(4,int(abs(b-a)*2)))
 return prism([[ro*math.cos(t),ro*math.sin(t)]for t in aa]+[[ri*math.cos(t),ri*math.sin(t)]for t in aa[::-1]],z,h)
def helix(ri,ro,a,b,z0,z1,h,n=150):
 vs=[]
 for t in np.linspace(0,1,n+1):
  ang=math.radians(a+(b-a)*t);z=z0+(z1-z0)*t
  for r,dz in [(ri,0),(ro,0),(ro,h),(ri,h)]:vs.append([r*math.cos(ang),r*math.sin(ang),z+dz])
 fs=[]
 for i in range(n):
  for j in range(4):
   x=4*i+j;y=4*i+(j+1)%4;u=4*(i+1)+j;v=4*(i+1)+(j+1)%4
   fs.extend([[x,y,v],[x,v,u]])
 fs.extend([[0,2,1],[0,3,2],[4*n,4*n+1,4*n+2],[4*n,4*n+2,4*n+3]])
 tm=trimesh.Trimesh(vs,fs,process=True);trimesh.repair.fix_normals(tm)
 return mf.Manifold(mf.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))
add('Author connected display footing',mf.Manifold.cylinder(.32,3.05,3.05,128).translate([0,0,-.32]),3,'Authored base for print continuity, not real terrain perimeter')
# Three principal uprights inferred from front/reverse photographs. No fourth corner post.
corners=[np.array([-2.,-.65]),np.array([2.,-.65]),np.array([0.,2.81])]
for i,c in enumerate(corners):
 left=corners[(i-1)%3]-c;left=left/np.linalg.norm(left)
 right=corners[(i+1)%3]-c;right=right/np.linalg.norm(right)
 add('Principal corner upright '+str(i+1),prism([list(c),list(c+right*1.02),list(c+left*1.02)],0,8.4),0,'Three main upright positions and orientations inferred from multi-angle photographs; triangular corner section is nominal approximation')
centre=np.mean(corners,axis=0)
frame_path=[]
for i,a in enumerate(corners):
 b=corners[(i+1)%3];mid=(a+b)/2;out=(mid-centre)/np.linalg.norm(mid-centre);mid=mid+out*.35
 frame_path.extend([list(a),list(mid)])
# Continuous mitered perimeter: a plane break is not a V-shaped open notch.
outline=mf.CrossSection([frame_path])
ring=outline.offset(.225,mf.JoinType.Miter,4)-outline.offset(-.225,mf.JoinType.Miter,4)
add('Continuous creased perimeter frame',ring.extrude(1.05).translate([0,0,7.35]),0,'Three-direction frame inferred from multiple official views; continuous mitered plane breaks, angles nominal')
add('Rear bell suspension beam',beam((0,-1.0),(0,2.81),.34,7.35,.34),0,'Visible beam from front junction toward rear upright; nominal depth and joint')
# Platform has a two-segment front and nominal rear closure around landing.
platform=[[-1.56,-.68],[0,-1.20],[1.56,-.68],[1.32,1.20],[0,1.82],[-1.32,1.20]]
add('Bell landing platform',prism(platform,4.78,.26),1,'Front crease visible; rear landing footprint simplified from partial views')
for a,b,label in [((-1.55,-.68),(0,-1.20),'left'),((0,-1.20),(1.55,-.68),'right')]:
 wall=beam(a,b,.18,5.0,1.0);a=np.array(a);b=np.array(b);d=b-a;length=np.linalg.norm(d);yaw=math.degrees(math.atan2(d[1],d[0]))
 for j in range(3):
  c=a+(b-a)*(j+1)/4
  cutter=box([-.12,-.5,5.58],[.12,.5,5.86]).rotate([0,0,yaw]).translate([float(c[0]),float(c[1]),0]);wall=wall-cutter
 add('Perforated balcony parapet '+label,wall,0,'Three representative square apertures per half; reduced count, not survey')
 add('Parapet top cap '+label,beam(a,b,.23,5.97,.09),0,'Visible projecting top coping; nominal section')
# Exposed partial-turn stair, not arbitrary full-turn helix. Tread count authored for readable output.
a,b=P['stair_start_deg'],P['stair_end_deg'];ri,ro=P['stair_inner_r'],P['stair_outer_r'];steps=P['stair_steps']
add('Continuous smooth stair underside',helix(ri,ro,a,b,-.30,4.38,.55),1,'Photo-visible continuous twisted underside; nominal thickness, structurally supports simplified treads')
for j in range(steps):
 aa=a+(b-a)*j/steps;bb=a+(b-a)*(j+1)/steps;z=.04+(4.72-.04)*j/steps
 add('Simplified tread '+str(j+1),sector(ri,ro,aa+.025,bb-.025,z-.12,.32+(4.72-.04)/steps),1,'28 representative treads; actual count not established from photos')
add('Outer rising stair parapet',helix(ro-.14,ro,a,b,.04,4.72,.94),0,'Direction follows front-right low to left/rear high across paired views; nominal partial-turn path')
add('Inner rising stair parapet',helix(ri,ri+.12,a,b,.04,4.72,.83),0,'Visible curved inner edge; nominal section, no invented center column')
# Actual hanging bell, simplified body only. No lettering, portraits or decorative motif recreation.
bell=mf.Manifold.cylinder(1.38,.49,.39,96).translate([0,.02,5.97]);cavity=mf.Manifold.cylinder(1.23,.42,.32,96).translate([0,.02,5.94]);bell=bell-cavity
add('Abstract hollow bell shell',bell,2,'Visible tapered cylindrical hanging bronze bell; relief omitted and thickness authored')
for z,r in [(6.02,.50),(6.42,.47),(6.85,.43),(7.30,.41)]:
 ring=mf.Manifold.cylinder(.055,r,r,96)-mf.Manifold.cylinder(.055,r-.035,r-.035,96)
 add('Simplified bell band '+str(z),ring.translate([0,.02,z]),2,'Representative horizontal bands, not exact engraved register count')
bx('Bell simplified hanger',[-.08,-.06,7.31],[.08,.10,7.57],2,'Plain structurally connected hanger substitutes complex visible hook/crest')
# Tiered semicircular front steps are visible; reduce to three authored nominal levels.
for i,(r,z,h)in enumerate([(2.85,0,.14),(2.52,.12,.14),(2.18,.24,.14)]):
 add('Approximate front curved step '+str(i+1),sector(.01,r,180,360,z,h),1,'Three visible broad forecourt tiers, nominal radii/heights; surrounding planters omitted')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUTN centenary bell tower');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official photograph-informed three-upright bell tower body; nominal stair and framework geometry, not measured replica.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
