"""Add source-guided approximate materials; never modify original mesh or locked previews.
Run Blender 4.3.2: blender -b -t 1 --python-exit-code 1 -P build_appearance.py
Requires original scene.blend and model.stl alongside this script. No source photos embedded.
"""
from pathlib import Path
import sys
import bpy,hashlib,json,math,struct,zipfile,xml.etree.ElementTree as ET
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
bpy.context.preferences.filepaths.save_version=0
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mesh=obj.data
verts=[tuple(v.co) for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
assert all(len(f)==3 for f in faces)
def digest(a,fmt):return hashlib.sha256(b''.join(struct.pack(fmt,*r) for r in a)).hexdigest()
before={'vertices':digest(verts,'<3f'),'faces':digest(faces,'<3I')}
# Five official photographs: source-limited western neutral-family calibration.
# Existing four display-contrast materials are NOT a previously all-monochrome model.
palette=[('Unverified rear roof recess and ground neutral','#AAA79F',.86),('Observed western grey white solid bands','#C8C8C2',.86),('Observed slanted column dark grey brown','#55514D',.8),('Observed recessed band mixed opaque appearance not pure glass','#656B6B',.8)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
from collections import defaultdict
S=148/55.2;BASE=2.;N=128;EPS=.00035
# Index true original triangulated loft support planes, not smooth superellipse distance.
# Bounds only prefilter: all vertices must lie in the paired true triangles of one original quad. No geometry is generated in the scene.
records=[];bins=defaultdict(list)
def contour(rx,ry,n=3.15,cx=0,cy=0):
 t=np.arange(N)*2*math.pi/N;c=np.cos(t);s=np.sin(t)
 return np.array([cx+rx*np.sign(c)*abs(c)**(2/n),cy+ry*np.sign(s)*abs(s)**(2/n)]).T
def register(levels,mat,exponent=3.15,zclip=None):
 rings=[]
 for z,rx,ry,cx,cy in levels:
  xy=contour(rx,ry,exponent,cx,cy)
  # Original loft passed mm vertices to float32 Mesh; match that precision.
  r=np.column_stack((xy,np.full(N,z)));r=((r*S+[0,0,BASE]).astype(np.float32).astype(float)-[0,0,BASE])/S;rings.append(r)
 for a,b in zip(rings,rings[1:]):
  for k in range(N):
   j=(k+1)%N
   Q=np.array([a[k],a[j],b[j],b[k]])
   normals=[]
   for t in (Q[[0,1,2]],Q[[0,2,3]]):
    normal=np.cross(t[1]-t[0],t[2]-t[0]);ll=np.linalg.norm(normal)
    if ll<1e-12:break
    normals.append(normal/ll)
   if len(normals)!=2:continue
   lo=Q.min(0);hi=Q.max(0)
   if lo[0]>EPS or min(abs(n[2]) for n in normals)>.95:continue
   if zclip is not None:lo[2]=max(lo[2],zclip[0]);hi[2]=min(hi[2],zclip[1])
   if hi[2]<lo[2]-EPS:continue
   idx=len(records);records.append((Q,normals,lo,hi,mat))
   for zz in range(math.floor(lo[2]*2),math.floor(hi[2]*2)+1):bins[zz].append(idx)
def dims(z):
 t=np.clip((z-13.05)/36.5,0,1);return 16.7*(1-.12*t**3),21.7*(1-.12*t**3)
def shelllevels(a,b,inset=0):return [(z,dims(z)[0]-inset,dims(z)[1]-inset,0,0) for z in np.linspace(a,b,max(2,int((b-a)/.7)+1))]
register(shelllevels(13,50.12),1)
for i in range(10):
 z=13.05+i*3.65;top=z+3.65
 register(shelllevels(z+2.10,top+.02,1.05),3,zclip=(z+2.12,top))
for i,z in enumerate([0,4.35,8.7]):
 rx=[14,14.8,15.4][i];ry=[19.5,20.3,20.8][i]
 register([(z,rx,ry,0,0),(z+1,rx,ry,0,0)],1)
 register([(z,rx-2.4,ry-1.8,0,0),(z+4.55,rx-2.4,ry-1.8,0,0)],3)
 for cy,rry in [(-11.2,8.4),(10,7.2)]:
  if cy>0 and i==2:continue
  register([(z,7.4,rry,-11,cy),(z+1,7.4,rry,-11,cy)],1,2.3)
  # Protected parapet cores are ambiguous glass/solid in the coarse original;
  # preserve neutral rather than claiming every curved guard is glazing.
for y,dy in [(-3.8,-1.7),(4.3,1.7)]:register([(0,.8,.8,-18.1,y),(13.45,.8,.8,-16.38,y+dy)],2,4)
RQ=np.array([r[0] for r in records]);RN=np.array([r[1] for r in records]);RL=np.array([r[2] for r in records]);RH=np.array([r[3] for r in records]);RM=np.array([r[4] for r in records])
bins={k:np.array(v,dtype=np.int32) for k,v in bins.items()}
def in_tri(points,A,B,C):
 u=B-A;w=C-A;normal=np.cross(u,w);normal/=np.linalg.norm(normal,axis=1)[:,None]
 uu=np.sum(u*u,axis=1);ww=np.sum(w*w,axis=1);uw=np.sum(u*w,axis=1);den=uu*ww-uw*uw
 result=[]
 for point in points:
  d=point-A;du=np.sum(d*u,axis=1);dw=np.sum(d*w,axis=1)
  ss=(ww*du-uw*dw)/den;tt=(uu*dw-uw*du)/den
  result.append((abs(np.sum(d*normal,axis=1))<EPS)&(ss>=-.0005)&(tt>=-.0005)&(ss+tt<=1.0005))
 return np.array(result)
indices=[]
for p in mesh.polygons:
 q=(np.array([verts[j] for j in p.vertices])-[0,0,BASE])/S;n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if hi[0]<=EPS and lo[2]>=-EPS and hi[2]<=50.12+EPS:
  candidates=bins.get(math.floor(float((lo[2]+hi[2])*.5)*2))
  if candidates is not None:
   keep=(np.max(RN[candidates]@n,axis=1)>.99995)&np.all(lo>=RL[candidates]-EPS,axis=1)&np.all(hi<=RH[candidates]+EPS,axis=1)
   ids=candidates[keep]
   if len(ids):
    Q=RQ[ids]
    contained=np.all(in_tri(q,Q[:,0],Q[:,1],Q[:,2])|in_tri(q,Q[:,0],Q[:,2],Q[:,3]),axis=0)
    ids=ids[contained]
    if len(ids):
     mats=RM[ids];i=2 if 2 in mats else (3 if 3 in mats else 1)
 p.material_index=int(i);indices.append(int(i))
assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown rear neutral'
scene=bpy.context.scene;scene['appearance_revision']='color-v2'
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.seed=0;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=900;scene.render.resolution_y=800
for attr in dir(scene.render):
 if attr.startswith('use_stamp'):
  try:setattr(scene.render,attr,False)
  except (TypeError,AttributeError):pass
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.85,.89,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
# New appearance lighting only: remove inherited lamps, never change original scene.
for lamp in list(scene.objects):
 if lamp.type=='LIGHT':bpy.data.objects.remove(lamp,do_unlink=True)
for name,energy,ang,rot in [('Key',2.1,.16,(28,-26,-32)),('Fill',.55,.35,(-20,32,140))]:
 light=bpy.data.lights.new(name,'SUN');light.energy=energy;light.angle=ang;o=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(a) for a in rot)

bpy.ops.wm.save_as_mainfile(filepath=str(R/'appearance.blend'))
# Core 3MF base materials per original triangle: no geometry splitting/resampling.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
e=lambda tag,attrs={}:ET.Element('{'+ns+'}'+tag,attrs)
root=e('model',{'unit':'millimeter','xml:lang':'en-US'});res=ET.SubElement(root,'{'+ns+'}resources');bm=ET.SubElement(res,'{'+ns+'}basematerials',{'id':'1'})
for name,col,_ in palette:ET.SubElement(bm,'{'+ns+'}base',{'name':name,'displaycolor':col+'FF'})
o=ET.SubElement(res,'{'+ns+'}object',{'id':'2','type':'model'});m=ET.SubElement(o,'{'+ns+'}mesh');vs=ET.SubElement(m,'{'+ns+'}vertices')
for v in verts:ET.SubElement(vs,'{'+ns+'}vertex',dict(zip(['x','y','z'],[format(c,'.17g') for c in v])))
ts=ET.SubElement(m,'{'+ns+'}triangles')
for f,i in zip(faces,indices):ET.SubElement(ts,'{'+ns+'}triangle',{'v1':str(f[0]),'v2':str(f[1]),'v3':str(f[2]),'pid':'1','p1':str(i),'p2':str(i),'p3':str(i)})
build=ET.SubElement(root,'{'+ns+'}build');ET.SubElement(build,'{'+ns+'}item',{'objectid':'2'})
with zipfile.ZipFile(R/'appearance.3mf','w',zipfile.ZIP_DEFLATED) as out:
 for n,b in {'3D/3dmodel.model':ET.tostring(root,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}.items():
  info=zipfile.ZipInfo(n,date_time=(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;out.writestr(info,b)
from collections import Counter
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v2','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Existing four materials were neutral/display contrasts, not literal monochrome. Five official 2021 article photos support western grey-white bands, dark grey-brown slanted columns and mixed opaque recessed bands. No pure-glass claim; terrace interiors, protected parapet cores, eastern rear, roof cap and unsplit roof panel/grid remain neutral. No lighting tint baked into materials. Original printability QA and short-root limitations preserved, not rerun.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-280,-125,130),(0,0,75),220),'rear':((280,125,135),(0,0,75),220),'elevation':((-320,0,75),(0,0,75),220),'source-angle':((-260,80,125),(0,0,75),220),'top':((0,0,350),(0,0,75),220)}
out=R/'appearance';out.mkdir(exist_ok=True)
for name,(pos,target,scale) in ([] if '--skip-render' in sys.argv else views.items()):
 c=scene.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 inv=c.rotation_euler.to_matrix().transposed();projected=[inv@(obj.matrix_world@Vector(corner)-c.location) for corner in obj.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 c.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 data=(out/(name+'.png')).read_bytes(); cleaned=data[:8]; off=8
 while off<len(data):
  length=struct.unpack_from('>I',data,off)[0];typ=data[off+4:off+8];body=data[off+8:off+8+length];key=body.split(b'\0',1)[0]
  variable=typ in (b'tEXt',b'zTXt',b'iTXt') # no private path/date/timing metadata
  if not variable:cleaned+=data[off:off+length+12]
  off+=length+12
 (out/(name+'.png')).write_bytes(cleaned)
print('APPEARANCE_DONE',before,dict(Counter(indices)))
