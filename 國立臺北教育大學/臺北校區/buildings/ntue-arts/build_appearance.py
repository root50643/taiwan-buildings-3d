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
# Two local official PDF photographs support central entrance components only.
palette=[('Uncertified broad wings roofs stairs neutral', '#AAA79F', 0.86), ('Original curved true window backs mixed bluegray', '#8C9FA4', 0.65), ('Original front-facing curved ribs and floorbands pale', '#C9CDCA', 0.84), ('Original four column lateral family', '#B9BCB5', 0.87), ('Original independent cap front gray', '#90938F', 0.87)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def radial_side(cx,cy,r,z,h,N,frontonly=False):
 if lo[2]<z-EPS or hi[2]>z+h+EPS or (frontonly and n[1]>=-.001):return False
 for k in range(N):
  th=(k+.5)*2*np.pi/N;v=np.array([np.cos(th),np.sin(th)])
  if max(abs((q[:,:2]-[cx,cy])@v-r*np.cos(np.pi/N)))<EPS and np.dot(n[:2],v)>.999:return True
 return False
def rotated_rib(a):
 t=np.radians(a);c=np.cos(t);s=np.sin(t);rot=np.array([[c,-s,0],[s,c,0],[0,0,1]])
 center=np.array([26.1*c,-40+26.1*s,26]);qq=(q-center)@rot;nn=n@rot
 if not (np.all(qq.min(0)>=np.array([-1,-.55,0])-EPS) and np.all(qq.max(0)<=np.array([1,.55,47])+EPS)):return False
 if n[1]>=-.001:return False
 return any(max(abs(qq[:,k]-val))<EPS and nn[k]*sg>.999 for k,vals in enumerate([[-1,1],[-.55,.55],[0,47]]) for val,sg in zip(vals,[-1,1]))
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 for z in [29,40,51,62]:
  if radial_side(0,-40,25.2,z,8.8,80,True):i=1
 for z,h in [(25.5,3.5),(37.8,2.2),(48.8,2.2),(59.8,2.2),(70.8,2.7)]:
  if radial_side(0,-40,28.2,z,h,80,True):i=2
 if any(rotated_rib(a) for a in range(195,346,15)):i=2
 for x,y in [(-20,-48),(-9,-57),(9,-57),(20,-48)]:
  if radial_side(x,y,1.9,3,24,24):i=3
 for x in [-28,28]:
  if plane(1,-57.5) and n[1]<-.999 and bounds((x-7,-57.5,72.5),(x+7,-57.5,77.5)):i=4
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Only existing central entrance components receive source-guided approximate materials; not whole ArtsHall color restoration','Official PDFpage58 two photos personallyread locally, capturedateunknown. Original80facet r25.2 truecutbacks withinfourbands bluegrayopaqueproxy, onlyfrontnynegative. Originalrotatedribs frontfacing sidefaces andfiveannularbands r28.2 outerfrontfaces pale, no newfinegrid. Allbandtop/bottom/inner/back andribunseenfacesneutral. Fouroriginalr1.9 columns lateralsgray, smallhiddencomponentfamilycontinuationdisclosed, capsneutral. Twoexistingraisedcaps fronty-57.5 gray only. Entirebroadfrontbrick/concrete mixedwalls intentionallyneutral, no z62 orcentroidcutoff, no guessedbrick. Alllongouter/courtyard/rearwings/roof/parapet/base/stairs/groundglazing/flankwindows/roundstairheadsneutral. No geometrychange, newtext/AC/rails/tiles orpaintedtextures. Original78layer maximumopeninglossfraction0.00046001705121067444 retained, no newphysicalprint or slicer approval','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-220,-300,165),(0,0,40),225),'rear':((220,300,165),(0,0,40),225),'elevation':((0,-350,40),(0,0,40),225),'source-angle':((180,-300,110),(0,0,40),225),'top':((0,0,380),(0,0,40),225)}
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
