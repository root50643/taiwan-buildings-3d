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
# Historical listed photograph supports visible upper bell tower components, not all four faces.
palette=[('Unobserved lower and opposite surfaces neutral','#AAA79F',.86),('Observed outer stone upper tower','#93978F',.86),('Visible opposite interior pale','#C0C1B7',.86),('Visible front roof slope tile approximation','#8D6252',.87),('Existing hanging bell dark family','#373C37',.82)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def side(x,z,h):return plane(0,x) and n[0]<-.999 and bounds((x,-27,z),(x,17,z+h))
def gableface(x):
 if not (plane(0,x) and n[0]<-.999):return False
 # Original three-sided gable profile y[-28,18],z134..146.8.
 yz=q[:,[1,2]];return bool(np.all(yz[:,1]>=134-EPS) and np.all(yz[:,1]<=146.8-(12.8/23)*abs(yz[:,0]+5)+EPS))
def front(x,y,z,w,h):return plane(1,y) and n[1]<-.999 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def boxsurface(x,y,z,w,d,h):
 aa=np.array([x-w/2,y-d/2,z]);bb=np.array([x+w/2,y+d/2,z+h])
 return bounds(aa,bb) and any((plane(k,aa[k]) and n[k]<-.999) or (plane(k,bb[k]) and n[k]>.999) for k in range(3))
def cylinder_surface(x,y,z,h,r0,r1,N):
 if lo[2]<z-EPS or hi[2]>z+h+EPS:return False
 qr=q[:,:2]-[x,y]; rr=r0+(r1-r0)*(q[:,2]-z)/h
 for k in range(N):
  theta=(k+.5)*2*np.pi/N;v=np.array([np.cos(theta),np.sin(theta)])
  expected=np.array([v[0],v[1],-(r1-r0)*np.cos(np.pi/N)/h]);expected/=np.linalg.norm(expected)
  if max(abs(qr@v-rr*np.cos(np.pi/N)))<EPS and np.dot(n,expected)>.999:return True
 for zz,rad,sg in [(z,r0,-1),(z+h,r1,1)]:
  if plane(2,zz) and n[2]*sg>.999 and all(max(qr@np.array([np.cos((k+.5)*2*np.pi/N),np.sin((k+.5)*2*np.pi/N)]))<=rad*np.cos(np.pi/N)+EPS for k in range(N)):return True
 return False
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if side(-3.5,78,57.5) or gableface(-3.5):i=1
 for x in [-1.1,42.1]:
  if front(x,-27.1,77,5.2,59.2):i=1
 if front(20.5,-27.7,133,47.6,5):i=1
 if front(20.5,-27,78,47,7):i=1
 if side(39.7,78,57.5) or gableface(39.7):i=2
 # Only outer-upward original front slope, not edge/underside/opposite slope.
 if bounds((-4.1,-32,136.3),(45.1,-5,148.4)) and max(abs(q[:,2]-(136.3+(q[:,1]+32)*(12.1/27))))<EPS and n[2]>.8 and n[1]<-.3:i=3
 if cylinder_surface(20.5,-5,105,14,1.2,1.2,24) or cylinder_surface(20.5,-5,99,6.4,3.6,2.0,32) or boxsurface(20.5,-5,98.5,7.4,6.7,1.3):i=4
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original partial bell-tower section geometry retained, not full teachingbuilding or drumtower','Actual original-listed2017 blog image personally read. Articleyear is not verified capturedate/currentcondition. Opposite view from original preview mapped to-X/-Y via actual originalscene/build and singlephoto. Visible-X original upper screen/gable outer and-Y portalcolumn/beam/balustrade front planes stone; visible+Xscreen interior facing-X pale. Only original-Y roofslab outerupward plane redbrown, no newtilepattern. Original rod/bellcone/flange dark family including smallcomponent unseenrear extrapolation; no alloy/acoustic/currentinstallation claim. Lowergraybrick mixed/tree-obscured box, lowcurvedwing, stairs/base, opposite roof andunseen+Xexterior/rear neutral. Reveals remain neutral conservatively. No added geometry, lettering or texture. Original support/printQA warnings unchanged','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-230,-290,175),(0,0,76),205),'rear':((230,290,175),(0,0,76),205),'elevation':((0,-350,76),(0,0,76),205),'source-angle':((-250,-210,145),(0,0,76),205),'top':((0,0,410),(0,0,76),205)}
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
