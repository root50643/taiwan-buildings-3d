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
# Three source photographs support front and rear gate finishes within original boundaries.
palette=[('Unknown or unsegmented mixed surfaces neutral','#AAA79F',.86),('Observed red brick upper wall planes','#A26956',.86),('Original grey stone supports','#A5A79E',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def edges(poly):
 ans=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  e=b-a;v=np.array([e[1],-e[0]],dtype=float);v/=np.linalg.norm(v);ans.append((a,v))
 return ans
def inside(p,ed):return all(max((p-a)@v)<=EPS for a,v in ed)
def area(p):return abs(sum(np.cross(p[k]-p[0],p[k+1]-p[0]) for k in range(1,len(p)-1)))*.5 if len(p)>2 else 0.
def clip(poly,ed):
 out=list(poly)
 for a,v in ed:
  src=out;out=[]
  if not src:break
  for u,w in zip(src,src[1:]+src[:1]):
   du=(u-a)@v;dw=(w-a)@v;iu=du<=1e-8;iw=dw<=1e-8
   if iu:out.append(u)
   if iu!=iw:out.append(u+(w-u)*du/(du-dw))
 return out
def segmentpoly(z,w,h,rise):
 spring=z+h-rise
 return np.array([(-w/2,z),(w/2,z),(w/2,spring)]+[(w/2*np.cos(t),spring+rise*np.sin(t)) for t in np.linspace(0,np.pi,33)[1:]])
def ring(y):
 z,w,h,rise,th=3,62,40,9,2.6
 oe=edges(segmentpoly(z,w+2*th,h+th,rise+th));ie=edges(segmentpoly(z-.2,w,h+.2,rise));qq=q[:,[0,2]]
 if not bounds((-w/2-th,y-1.2,z),(w/2+th,y+1.2,z+h+th)) or not inside(qq,oe):return False
 if ((plane(1,y-1.2) and n[1]<-.99) or (plane(1,y+1.2) and n[1]>.99)) and area(clip(qq,ie))<1e-6:return True
 return any(max(abs((qq-a)@v))<EPS and n@np.array([sg*v[0],0,sg*v[1]])>.999 for ed,sg in [(oe,1),(ie,-1)] for a,v in ed)
def boxsurface(x,y,z,w,d,h):
 aa=np.array([x-w/2,y-d/2,z]);bb=np.array([x+w/2,y+d/2,z+h])
 if not bounds(aa,bb):return False
 return any((plane(k,aa[k]) and n[k]<-.999) or (plane(k,bb[k]) and n[k]>.999) for k in range(3))
def cylinder(x,y):
 z,h,r,N=15,17,2.3,28
 if not bounds((x-r,y-r,z),(x+r,y+r,z+h)):return False
 xy=q[:,:2]-[x,y];theta=(np.arange(N)+.5)*2*np.pi/N;c=np.cos(np.pi/N)
 if (plane(2,z) and n[2]<-.999) or (plane(2,z+h) and n[2]>.999):return all(max(xy@np.array([np.cos(t),np.sin(t)]))<=r*c+EPS for t in theta)
 return any(max(abs(xy@np.array([np.cos(t),np.sin(t)])-r*c))<EPS and n@np.array([np.cos(t),np.sin(t),0])>.999 for t in theta)
for p in mesh.polygons:
 oq=np.array([verts[j] for j in p.vertices]);on=np.array(p.normal);i=0
 for back in [False,True]:
  q=oq.copy();n=on.copy()
  if back:q[:,:2]*=-1;n[:2]*=-1
  lo=q.min(0);hi=q.max(0)
  # Source-observed plane only. Reject entire triangles crossing the mixed lower stone-tooth zone.
  if plane(1,-13) and n[1]<-.999 and bounds((-70,-13,34),(70,-13,57.8)):i=1
  if plane(1,-13) and n[1]<-.999 and bounds((-47,-13,57),(47,-13,70)):i=1
  if ring(-13) or boxsurface(0,-14.2,43,3.5,3,7):i=2
  for z in [37,47,56]:
   for x in [-59,59]:
    if boxsurface(x,-13.4,z,21,1.3,1.3):i=2
  if boxsurface(0,-13.4,68,95,1.4,1.4):i=2
 q=oq;n=on;lo=q.min(0);hi=q.max(0)
 # Supported existing stone components, not new geometry or invented courses.
 for z,w in [(57,142),(69,96),(71,98)]:
  if boxsurface(0,0,z,w,28,2) and ((plane(1,-14) and n[1]<-.999) or (plane(1,14) and n[1]>.999)):i=2
 for x in [-35,35]:
  if boxsurface(x,0,3,14,28,12.5) or boxsurface(x,0,31,15,30,4):i=2
  for dx in [-3.1,3.1]:
   for y in [-8.5,8.5]:
    if cylinder(x+dx,y):i=2
 for x in [-64,64]:
  if boxsurface(x,0,3,13,28,13):i=2
 p.material_index=i;indices.append(i)

assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown or unresolved surfaces neutral'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original three portal openings and paired-column gaps remain genuinely open; no glazing inserted','One official low-angle photograph and two original-listed visitor rear photographs personally read. Dates unverified; Commons image403 not read. Only whole existing triangles on front/rear upper brick planes z>=34 and raised name wall colored. Lower outer mixed brick/stone-tooth walls, unsegmented pedestrian lintels, hidden cut interiors and model base neutral. Grey material on original32segment arch surrounds, keystone, stone courses, front/back vertical cornice fascias only (broad tops neutral), plinths/capitals and eight28facet columns is same-component approximation including unseen portions. No new tooth joints, glyphs, signs, lights or topology. Cross-period illustrative finish, not2026 condition, calibrated RGB or real survey. Original printQA warning unchanged','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-175,-220,125),(0,0,36),210),'rear':((175,220,125),(0,0,36),210),'elevation':((0,-320,36),(0,0,36),210),'source-angle':((-240,-180,85),(0,0,36),210),'top':((0,0,360),(0,0,36),210)}
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
