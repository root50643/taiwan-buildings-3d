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
# Two adjacent source-visible clock-tower elevations only.
palette=[('Unknown rear interior roof and base','#AAA79F',.86),('Visible outer wall warm grey cream','#C9C5B5',.86),('Visible column moulding metal appearance','#AEB3B1',.75),('Original front clock opaque dial','#C6C9C7',.8),('Original schematic hands','#59605E',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def cyl_side(cx,cy,r,N,z0,z1):
 if lo[2]<z0-EPS or hi[2]>z1+EPS or abs(n[2])>.001:return False
 v=q[:,:2]-[cx,cy]
 for k in range(N):
  a=(k+.5)*2*math.pi/N;nn=np.array([math.cos(a),math.sin(a)]);tt=np.array([-nn[1],nn[0]])
  if np.dot(nn,n[:2])>.9999 and max(abs(v@nn-r*math.cos(math.pi/N)))<EPS and max(abs(v@tt))<=r*math.sin(math.pi/N)+EPS:return True
 return False
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 # Two actual exterior wall planes, not inner arches or mirrored rear walls.
 if ((plane(1,-27) and n[1]<-.99) or (plane(0,-27) and n[0]<-.99)) and bounds((-27,-27,5.8),(27,27,138)):i=1
 # Original front/left gable faces protrude to 29.5; tops and back stay neutral.
 if ((plane(1,-29.5) and n[1]<-.99 and bounds((-21,-29.5,137),(21,-29.5,143))) or (plane(0,-29.5) and n[0]<-.99 and bounds((-29.5,-21,137),(-29.5,21,143)))):i=1
 for z in [53,62,86,91,129,137]:
  if bounds((-28.5,-28.5,z),(28.5,28.5,z+2.1)) and ((plane(1,-28.5) and n[1]<-.99) or (plane(0,-28.5) and n[0]<-.99)):i=2
 # Only outward source-facing circumference of three visible corners.
 for cx,cy in [(-25,-25),(25,-25),(-25,25)]:
  visible=(cy==-25 and n[1]<-.001) or (cx==-25 and n[0]<-.001)
  if not visible:continue
  if cyl_side(cx,cy,3.6,24,5.6,140.6):i=2
  for z in [54,62,87,130,140]:
   if cyl_side(cx,cy,5,40,z,z+2.2):i=2
  if cyl_side(cx,cy,2.4,24,140.6,145.1):i=2
 # Clock plane is opaque grey-white, not a new dial or copied photo.
 if plane(1,-28.8) and n[1]<-.99 and bounds((-6.8,-28.8,126.2),(6.8,-28.8,139.8)):i=2
 if plane(1,-29.3) and n[1]<-.99 and bounds((-5.6,-29.3,127.4),(5.6,-29.3,138.6)):i=3
 # Original two relief bars only. All bounding planes correspond to actual boxes.
 for x0,x1,z0,z1 in [(-.6,.6,132.4,136.8),(-.05,4.05,132.4,133.6)]:
  if bounds((x0,-29.65,z0),(x1,-28.55,z1)) and any((plane(k,a) and n[k]<-.8) or (plane(k,b) and n[k]>.8) for k,a,b in [(0,x0,x1),(1,-29.65,-28.55),(2,z0,z1)]):i=4
 if hi[2]<=5.8+EPS:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque clock dial only; true openings remain open, no glazing proxies','Original single warm display material. Only source-visible -Y and -X outer planes and outward sectors of three corner columns/caps receive approximate finish. Fourth rear corner, hidden circumference, sphere finials, roof, inner shaft/stair, base and back faces neutral. True arch and baluster openings stay open, no glazing or new geometry. Silver grey is not gold paint or certified alloy. Original schematic hands unchanged; laurel/inscriptions/antenna absent and not invented. EXIF2017-12-13 10:39:01 has no timezone/clock verification, not 2026 condition. Original printQA caveats retained','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-220,-270,190),(0,0,75),220),'rear':((220,270,190),(0,0,75),220),'elevation':((0,-300,75),(0,0,75),220),'source-angle':((-250,-220,100),(0,0,75),220),'top':((0,0,400),(0,0,75),220)}
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
