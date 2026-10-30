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
# Qualified multi-date source-guided material study, no geometry changes.
palette=[('Unknown sides roof interior and base','#AAA79F',.86),('Supported pale grey cream wall and D fascia','#D6D4C8',.86),('True supported window backing mixed appearance','#71817F',.86),('Original entrance window rails grey brown','#8F8D83',.86),('Actual D-end recess backing shadow not glass','#62655E',.86),('Main negative-Y entry stairs pale brick','#B98D82',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x,y,z,w,d,h):
 a=(x-w/2,y-d/2,z);b=(x+w/2,y+d/2,z+h)
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.8) or (plane(k,b[k]) and n[k]>.8) for k in range(3))
def arcside(r,z0,z1):
 if lo[2]<z0-EPS or hi[2]>z1+EPS or abs(n[2])>.001:return False
 v=q[:,:2]-[0,7]
 for k in range(40):
  a=(k+.5)*math.pi/40;nn=np.array([math.cos(a),math.sin(a)]);tt=np.array([-nn[1],nn[0]])
  if np.dot(nn,n[:2])>.9999 and max(abs(v@nn-r*math.cos(math.pi/80)))<EPS and max(abs(v@tt))<=r*math.sin(math.pi/80)+EPS:return True
 return False
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if plane(1,-40.5) and n[1]<-.99 and bounds((-68,-40.5,2.8),(68,-40.5,60)):i=1
 for x in [-67,-53.5,-40.5,-27.5,-14.5,14.5,27.5,40.5,53.5,67]:
  if boxface(x,-40.3,3,1.7,1.6,57.3):i=1
 for z in [14.8,25.6,36.4,47.2,58]:
  if plane(1,-41) and n[1]<-.99 and bounds((-68.5,-41,z),(68.5,-41,z+1.4)):i=1
 if boxface(0,-43,15.2,28,11.5,3):i=1
 for x in [-12,0,12]:
  if boxface(x,-46.5,5,2.5,2.5,10.6):i=1
 for f in range(5):
  z=6+10.8*f
  for x in [-60,-47,-34,-21,-8,8,21,34,47,60]:
   if f==0 and abs(x)<14:continue
   if plane(1,-38.4) and n[1]<-.99 and bounds((x-5.05,-38.4,z),(x+5.05,-38.4,z+6.4)):i=2
   if boxface(x,-39.3,z+4.8,10.2,1.8,1):i=3
 # Old D-end visible fields; long outer wings and unseen court depths untouched.
 if plane(1,.5) and n[1]>.99 and bounds((-30.5,.5,2.8),(30.5,.5,60)):i=1
 for x in [-45,45]:
  if plane(1,43.5) and n[1]>.99 and bounds((x-14.5,43.5,2.8),(x+14.5,43.5,60)):i=1
 for x in [-27.5,27.5]:
  if plane(1,47.5) and n[1]>.99 and bounds((x-5,47.5,2.8),(x+5,47.5,62)):i=1
  for z in [9,20,31,42,53]:
   if plane(1,46.65) and n[1]>.99 and bounds((x-1.15,46.65,z),(x+1.15,46.65,z+6)):i=2
 for x in [-9.6,9.6]:
  if boxface(x,7.7,3,2.3,3.2,57.3):i=1
 for x in [-24.5,-16.5,16.5,24.5]:
  if boxface(x,.5,3,1.7,2.5,57.5):i=1
 for f in range(1,5):
  z=3+10.8*f
  if arcside(9.5,z,z+4.1):i=1
  if bounds((-9.5,-5,z),(9.5,7,z+4.1)) and ((plane(0,-9.5) and n[0]<-.99) or (plane(0,9.5) and n[0]>.99)):i=1
 if arcside(10.2,58.8,60.7):i=1
 for f in range(5):
  z=6+10.8*f
  for x in [-22,-13,13,22]:
   if plane(1,-1.5) and n[1]>.99 and bounds((x-1.3,-1.5,z),(x+1.3,-1.5,z+6)):i=2
  if plane(1,-1.5) and n[1]>.99 and bounds((-6.5,-1.5,z),(6.5,-1.5,z+5.4)):i=4
  for x in [-51,-39,45]:
   w=8.5 if x>0 else 7.3
   if plane(1,42.35) and n[1]>.99 and bounds((x-w/2,42.35,z),(x+w/2,42.35,z+3)):i=2
 for k in range(5):
  y=-51+k*1.35;h=.65*(k+1)
  if bounds((-15,y-.8,2.9),(15,y+.8,2.9+h)) and ((plane(2,2.9+h) and n[2]>.99) or (plane(1,y-.8) and n[1]<-.99)):i=5
 if hi[2]<=3+EPS:i=0
 p.material_index=i;indices.append(i)

assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown surfaces neutral'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing backing only; open courts and balconies remain open','Shi Xi is 時習大樓, not 實習大樓. Official school-history PDF10/printed154 three photographs personally viewed. Upper old D-end and lower newer entry images are different periods, unknown capture dates, not single-date reconstruction or2026condition. -Y entrance cream walls/grey brown original rails/grey blue green true window backs and pale brick stairs. +Y source-visible end fields, true narrow window backs, actual central recess shadow, D outer40facet fascia and paired piers cream. D openings remain open; no glass infill. Minor hidden faces of actual columns/porch continue same material family; long unknown side walls/court depths/D inner faces and tops/roof/base neutral. No letters, tile texture, AC, new rails or2025condition claim. No geometry/face splits or printQA rerun','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((190,-250,150),(0,0,32),220),'rear':((-180,250,145),(0,0,32),220),'elevation':((0,-300,32),(0,0,32),220),'source-angle':((0,280,115),(0,0,32),220),'top':((0,0,400),(0,0,32),220)}
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
