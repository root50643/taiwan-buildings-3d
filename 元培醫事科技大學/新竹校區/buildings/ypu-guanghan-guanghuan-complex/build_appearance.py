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
# Official2022 sustainability PDF45/64; photo dates differ/unknown, only limited source-visible color.
palette=[('Unknown outside roofs base slope','#A7AAA5',.86),('Pale grey beige observed inward walls','#C0BCB0',.85),('Grey green observed inner window proxies','#6A8580',.6),('Dark blue green existing convex entry window proxies','#4B6C70',.55),('Muted pink beige existing pergola','#B6A399',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
import numpy as np
D=json.loads((R/'plan-registration.json').read_text());S=1.07;B=1.6;MPP=.13554824373866425
def xy(p):return np.array([(p[0]-790)*MPP,(640-p[1])*MPP])
def coords(points,k=None):
 p=np.array(points,float)
 if k:p=(np.c_[p,np.ones(len(p))]@np.array(D[k]['matrix']).T)[:,:2]
 return np.array([xy(v) for v in p])
Hfront=coords([[910,500],[790,465],[650,450],[530,460],[410,500],[285,560]],'H')
Lfront=coords([[730,610],[650,570],[520,490]],'L')
Gface=coords([[100,550],[130,640],[210,680],[300,698],[380,680],[450,640]],'L')
rows=[(5.4,8.0),(9.5,12.2),(13.7,16.4),(17.9,20.6),(22.1,24.8)]
def strip(p,a,b,lo,hi,offset=0,tol=.006):
 a=np.asarray(a)*S;b=np.asarray(b)*S;u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]]);length=np.linalg.norm(b-a)
 return all(-tol<=np.dot(np.array(mesh.vertices[v].co[:2])-a,u)<=length+tol and abs(np.dot(np.array(mesh.vertices[v].co[:2])-a,n)-offset*S)<=tol and B+lo*S-tol<=mesh.vertices[v].co.z<=B+hi*S+tol for v in p.vertices)
def band(p,a,b,half,lo,hi):
 a=np.asarray(a)*S;b=np.asarray(b)*S;u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]]);length=np.linalg.norm(b-a)
 return all(-.006<=np.dot(np.array(mesh.vertices[v].co[:2])-a,u)<=length+.006 and abs(np.dot(np.array(mesh.vertices[v].co[:2])-a,n))<=half*S+.006 and B+lo*S-.006<=mesh.vertices[v].co.z<=B+hi*S+.006 for v in p.vertices)
rot=np.array([[math.cos(-.8),-math.sin(-.8)],[math.sin(-.8),math.cos(-.8)]])
center=xy([1152,679]);ovalpoints=[np.array([7*math.cos(k*2*math.pi/48),3.5*math.sin(k*2*math.pi/48)]) for k in range(48)]
for p in mesh.polygons:
 x,y,z=p.center;nx,ny,nz=p.normal;i=0
 # Only exact original inward wall planes, not unobserved outer H or Lrear.
 for chain in [Hfront,Lfront,Gface]:
  for a,b in zip(chain[:-1],chain[1:]):
   if strip(p,a,b,0,26):i=1
 # Actual shallow original recess back planes; both potential offsets are bounded to row intervals.
 for chain,depth,rr,idx in [(Hfront,.34,rows,2),(Lfront,.34,rows,2),(Gface,.15,[(6,8.5),(9.5,12),(13,15.5),(16.5,19),(20,23.3)],3)]:
  for a,b in zip(chain[:-1],chain[1:]):
   for lo,hi in rr:
    if any(strip(p,a,b,lo,hi,off) for off in [-depth,depth]):i=idx
 # Source-visible original upper pergola posts/rails only; no added solar panels or facade bands.
 for chain in [Hfront,Lfront]:
  for a,b in zip(chain[:-1],chain[1:]):
   if band(p,a,b,.55,26.6,27.6) or band(p,a,b,.8,28.3,29.3):i=4
   for t in np.linspace(0,1,max(2,round(np.linalg.norm(b-a)/3))):
    q=(a+(b-a)*t)*S
    if all(abs(mesh.vertices[v].co.x-q[0])<=.7*S+.006 and abs(mesh.vertices[v].co.y-q[1])<=.7*S+.006 and B+26.5*S-.006<=mesh.vertices[v].co.z<=B+28.6*S+.006 for v in p.vertices):i=4
 # Only source-visible positive-local-v half of original48-facet H oval; rim/inner hole neutral.
 local=[rot.T@(np.array(mesh.vertices[v].co[:2])/S-center) for v in p.vertices]
 localnormal=rot.T@np.array([nx,ny]);zz=[(mesh.vertices[v].co.z-B)/S for v in p.vertices]
 if abs(nz)<.01 and all(q[1]>=-.006 and -.04<=h<=29.106 for q,h in zip(local,zz)) and np.dot(localnormal,sum(local)/len(local))>0:
  for k,a in enumerate(ovalpoints):
   b=ovalpoints[(k+1)%48];u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
   if all(abs(np.dot(q-a,n))<.006 for q in local):i=1
 # Original wide horizontal recess backs and original narrow stair-slot backs only.
 if all(abs(q[1]-2.975)<.006 and -4.006<=q[0]<=4.006 for q in local) and localnormal[1]>.8 and any(all(lo-.006<=h<=hi+.006 for h in zz) for lo,hi in rows):i=2
 if all(abs(q[0]-6.35)<.006 and 5.994<=h<=24.406 for q,h in zip(local,zz)) and localnormal[0]>.8 and any(all(t-.356<=q[1]<=t+.356 for q in local) for t in [-.6,.6]):i=2
 if z<=B:i=0
 p.material_index=i;indices.append(i)
assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown rear neutral'
scene=bpy.context.scene;scene['appearance_revision']='color-v1'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown outer L arc windows and H back roofs base slope neutral; no PV or new facade divisions;2022 report images are different epochs not same-day condition','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((20,260,155),(0,0,16.85),200),'rear':((-150,-260,100),(0,0,16.85),200),'elevation':((0,300,16.85),(0,0,16.85),200),'source-angle':((-170,220,170),(0,0,16.85),200),'top':((0,0,330),(0,0,0),200)}
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
