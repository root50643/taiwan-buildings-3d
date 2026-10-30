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
# Source-visible principal front and curved-bay side only.
palette=[('Unknown opposite side roof rear and base','#AAA79F',.86),('Visible main terracotta brick family','#A85E49',.86),('Original portico and curved bay grey stone','#A6A69D',.86),('True window backing opaque mixed appearance','#46524F',.86),('Deep portico backing opaque mixed shadow','#55574F',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x,y,z,w,d,h,vertical=True):
 a=(x-w/2,y-d/2,z);b=(x+w/2,y+d/2,z+h)
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.99) or (plane(k,b[k]) and n[k]>.99) for k in range(2 if vertical else 3))
def frontback(x,z,w,h,y):return plane(1,y) and n[1]<-.99 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def frontrectreveal(x,z,w,h,y0,y1):
 return bounds((x-w/2,y0,z),(x+w/2,y1,z+h)) and ((plane(0,x-w/2) and n[0]>.99) or (plane(0,x+w/2) and n[0]<-.99) or (plane(2,z) and n[2]>.99) or (plane(2,z+h) and n[2]<-.99))
def archsupports(x):
 r=3.75;z=28;spring=43.75
 pts=np.array([(x-r,z),(x+r,z)]+[(x+r*np.cos(t),spring+r*np.sin(t)) for t in np.linspace(0,np.pi,25)])
 # Convex original 24-segment arch footprint, not a smooth circular approximation.
 qq=q[:,[0,2]]
 inside=True;edges=[]
 for a,b in zip(pts,np.roll(pts,-1,axis=0)):
  e=b-a;nn=np.array([e[1],-e[0]]);nn/=np.linalg.norm(nn);dd=(qq-a)@nn
  if max(dd)>EPS:inside=False;break
  edges.append((nn,dd))
 if not inside or not bounds((x-r,-66.5,z),(x+r,-62.8,47.5)):return 0
 if plane(1,-62.8) and n[1]<-.99:return 4
 for nn,dd in edges:
  if max(abs(dd))<EPS and np.dot(n,np.array([-nn[0],0,-nn[1]]))>.999:return 2
 return 0
angles=2*np.pi*(np.arange(64)+.5)/64
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if plane(1,-51) and n[1]<-.99 and bounds((-63,-51,2.9),(63,-51,121.9)):i=1
 if plane(1,-51) and n[1]<-.99 and bounds((-21.5,-51,121),(21.5,-51,132)):i=1
 if plane(0,-63) and n[0]<-.99 and bounds((-63,-51,2.9),(-63,55,121.9)):i=1
 # Original lower portico front/left side: horizontal top remains neutral.
 if plane(1,-66.5) and n[1]<-.99 and bounds((-66,-66.5,2.9),(66,-66.5,51.9)):i=2
 if plane(0,-66) and n[0]<-.99 and bounds((-66,-66.5,2.9),(-66,-47.5,51.9)):i=2
 for x in [-55,-44,-33,-22,-11,0,11,22,33,44,55]:
  if frontback(x,5,7.5,20,-62.8):i=4
  if frontrectreveal(x,5,7.5,20,-66.5,-62.8):i=2
  a=archsupports(x)
  if a:i=a
  for z in [59,71,83,95,107]:
   if frontback(x,z,7.5,6.2,-49.8):i=3
   if frontrectreveal(x,z,7.5,6.2,-51,-49.8):i=1
 for x in [-11,0,11]:
  if frontback(x,120,7.5,5.5,-49.8):i=3
  if frontrectreveal(x,120,7.5,5.5,-51,-49.8):i=1
 # Anisotropically scaled original 64-facet cylinder: exact facet support.
 if bounds((-73.3,-38,25),(-63,4,59)) and n[0]<-.01:
  local=np.column_stack(((q[:,0]+67)/.3,q[:,1]+17))
  for t in angles:
   v=np.array([np.cos(t),np.sin(t)]);nn=np.array([v[0]/.3,v[1],0]);nn/=np.linalg.norm(nn)
   if max(abs(local@v-21*np.cos(np.pi/64)))<EPS and n@nn>.999:i=2;break
 if boxface(-64,-17,25,5,42,34) and n[0]<-.01:i=2
 for y in [-31,-17,-3]:
  xx=-67-6.3*np.sqrt(max(0,1-((y+17)/21)**2))
  for z in [30,41,52]:
   if plane(0,xx+1.75) and n[0]<-.99 and bounds((xx+1.75,y-2.2,z),(xx+1.75,y+2.2,z+6.2)):i=3
   if bounds((xx-1.75,y-2.2,z),(xx+1.75,y+2.2,z+6.2)):
    if (plane(1,y-2.2) and n[1]>.99) or (plane(1,y+2.2) and n[1]<-.99) or (plane(2,z) and n[2]>.99) or (plane(2,z+6.2) and n[2]<-.99):i=2
 if hi[2]<=3+EPS:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing backing only; original portico recess geometry remains unchanged; backing shadow is not added glass','Official3402 and3404 photographs personally viewed.3406 returned503 and was not retried or bypassed; no later photo claimed viewed. Only A005 building, excluding adjacent historical architecture hall C-Hub and extension. Source-visible -Y front and -X curved-bay side brick and stone families. Opposite +X and rear including their windowbacks unknown neutral, broad roofs and base neutral. Curved stone bay one grey family because observed lower/upper variation lacks original face boundary. Original 64-facet ellipse support,24-segment arch outlines and actual planar windowbacks only. Minor pale brick bands AC frames lettering and equipment omitted without splits. True portico backs mixed masonry/glazing/shadow proxy not pure glass. Upload2025path is not capturedate or2026condition. Original geometry and0.01089075percent thin-opening-loss record retained, no new printQA','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-190,-250,185),(0,0,64),220),'rear':((180,250,185),(0,0,64),220),'elevation':((0,-300,64),(0,0,64),220),'source-angle':((-250,-180,170),(0,0,64),220),'top':((0,0,400),(0,0,64),220)}
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
