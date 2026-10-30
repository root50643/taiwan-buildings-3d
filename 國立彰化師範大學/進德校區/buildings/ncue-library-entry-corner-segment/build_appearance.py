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
# Partial material enrichment only: broad striped walls remain neutral.
palette=[('Unknown or unresolved striped surfaces','#AAA79F',.86),('Supported projecting bay tan fascia','#C7B18E',.86),('Original raised window cross mullions','#D5D8D2',.86),('True backing opaque shadow glazing mixture','#354443',.86),('Original coarse pitched entry canopy','#365954',.86),('Original entry stair treads and risers','#A3A29A',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x,y,z,w,d,h,vertical=False):
 a=(x-w/2,y-d/2,z);b=(x+w/2,y+d/2,z+h)
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.99) or (plane(k,b[k]) and n[k]>.99) for k in range(2 if vertical else 3))
def frontback(x,z,w,h,y):return plane(1,y) and n[1]<-.99 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def rightback(y,z,w,h,x):return plane(0,x) and n[0]>.99 and bounds((x,y-w/2,z),(x,y+w/2,z+h))
def canopy_support():
 # True triangular prism silhouette, including original cutter reveal faces.
 if not bounds((-46,-40.5,22),(-12,-25.5,30)):return False
 if np.any(q[:,2] > 30-(8/17)*abs(q[:,0]+29)+EPS):return False
 for sign in [-1,1]:
  normal=np.array([sign*8/17,0,1]);normal/=np.linalg.norm(normal)
  if max(abs(q@normal-(30+sign*(8/17)*-29)/np.linalg.norm([8/17,0,1])))<EPS and n@normal>.999:return True
 if (plane(1,-40.5) and n[1]<-.99) or (plane(1,-25.5) and n[1]>.99) or (plane(2,22) and n[2]<-.99):return True
 if plane(2,25.5) and n[2]<-.99 and bounds((-42,-40.5,25.5),(-16,-26.5,25.5)):return True
 if plane(1,-26.5) and n[1]<-.99 and bounds((-42,-26.5,22),(-16,-26.5,25.5)):return True
 return False
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 # Original projecting bay outer walls; unresolved broad stripe walls never selected.
 for x,z0,h in [(-34,31,47),(0,31,54),(39,34,57)]:
  if boxface(x,-28,z0,12,8,h,True):i=1
  if boxface(x,-31,z0,13.5,8,2):i=1
  for z in [z0+4,z0+18,z0+32]:
   if frontback(x,z,9,10,-29.85):i=3
   # Cut reveal sides have normals toward the recess; same-family tan proxy.
   if bounds((x-4.5,-32,z),(x+4.5,-29.85,z+10)):
    if (plane(0,x-4.5) and n[0]>.99) or (plane(0,x+4.5) and n[0]<-.99) or (plane(2,z) and n[2]>.99) or (plane(2,z+10) and n[2]<-.99):i=1
   if boxface(x,-32,z,1.1,4,10) or boxface(x,-32,z+5,9,4,1.1):i=2
 for x in [-21,8,38]:
  if frontback(x,22,4,8,-30.5):i=3
 for x in [-25,-11,3,17,31,45]:
  if frontback(x,5,10,13,-14.5):i=3
 for y in [-8,7,22,37]:
  if boxface(67,y,34,7,11,47,True):i=1
  for z in [37,51,65]:
   if rightback(y,z,8,10,68.4):i=3
   if bounds((68.4,y-4,z),(70.5,y+4,z+10)):
    if (plane(1,y-4) and n[1]>.99) or (plane(1,y+4) and n[1]<-.99) or (plane(2,z) and n[2]>.99) or (plane(2,z+10) and n[2]<-.99):i=1
   if boxface(70.2,y,z,3.5,1.1,10) or boxface(70.2,y,z+5,3.5,8,1.1):i=2
 for y in [-6,9,24,38]:
  if rightback(y,6,10,11,59.25):i=3
 if canopy_support():i=4
 for k in range(5):
  y=-46+k*3;h=.8+k*.7
  if bounds((-53,y-1.65,2.8),(71,y+1.65,2.8+h)) and ((plane(2,2.8+h) and n[2]>.99) or (plane(1,y-1.65) and n[1]<-.99)):i=5
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing backing only; true open colonnade and canopy void remain open','One M+ archival completed-building photograph personally viewed; capture date unknown, archive1986-1989 project interval and URL upload timestamp are not capture dates. Only original entry-corner segment, not full building or real rear facade. Three front and four return projecting bay fascia tan, existing cross mullions pale, actual recessed backing planes dark opaque mixed proxy; green original coarse canopy and grey steps. Broad alternating white and tan wall/column bands cannot be represented with full original face boundaries, intentionally omitted: large walls and columns remain neutral, original thin relief courses are not substituted for wide white bands. Unknown roof, artificial rear closure and base neutral. No geometry edits, face splits, letters, tile motifs, bars, transparent roofs or glazing across open colonnade. Original0.2235percent opening-loss warning retained, not new printQA.2016/2018 records not freshly read this pass, no2026 condition claim','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((190,-250,145),(0,0,44),220),'rear':((-180,250,145),(0,0,44),220),'elevation':((0,-300,44),(0,0,44),220),'source-angle':((230,-200,150),(0,0,44),220),'top':((0,0,400),(0,0,44),220)}
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
