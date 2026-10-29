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
# Official pre-repair photographs, capture dates unknown; same original mesh.
palette=[('Unknown court rear roof base','#A7AAA5',.86),('Pale peach sand observed wall family','#B5A48D',.86),('Grey cloud ribbons caps structural family','#8F938B',.87),('Grey green window curtain mixed opaque proxy','#8A9692',.65),('Neutral grey original entry steps','#9B9D95',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
import numpy as np
EPS=.012
levels=[(78,48,3,13),(74,46,15,10),(65,42,25,10),(56,37,35,10),(47,32,45,10),(39,27,55,10),(31,23,65,10)]
def bounded(v,lo,hi):return np.all(v>=np.array(lo)-EPS) and np.all(v<=np.array(hi)+EPS)
def plane(v,axis,value):return np.max(abs(v[:,axis]-value))<EPS
def boxface(v,lo,hi):
 return bounded(v,lo,hi) and any(plane(v,k,t) for k in range(3) for t in [lo[k],hi[k]])
def boxgeom(v,x,y,z,w,d,h):return boxface(v,[x-w/2,y-d/2,z],[x+w/2,y+d/2,z+h])
def inside2(q,poly):
 # Inclusive winding-ray test, with edge tolerance for rounded original mesh.
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=np.array(a);b=np.array(b);u=b-a;t=np.dot(q-a,u)/np.dot(u,u)
  if -EPS<=t<=1+EPS and abs(np.cross(u,q-a))/np.linalg.norm(u)<EPS:return True
  if (a[1]>q[1])!=(b[1]>q[1]) and q[0]<(b[0]-a[0])*(q[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def prismface(v,poly,x0,x1):
 if min(v[:,0])<x0-EPS or max(v[:,0])>x1+EPS:return False
 q=v[:,1:]
 if (plane(v,0,x0) or plane(v,0,x1)) and all(inside2(t,poly) for t in q):return True
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=np.array(a);b=np.array(b);u=b-a;ll=np.linalg.norm(u)
  t=(q-a)@u/(ll*ll)
  if min(t)>=-EPS and max(t)<=1+EPS and max(abs((q[:,0]-a[0])*u[1]-(q[:,1]-a[1])*u[0]))/ll<EPS:return True
 return False
ribbons=[]
for side in [-1,1]:
 for xx,zm in [(side*13,71),(side*28,49)]:
  front=[]
  for k in range(28):
   t=k/27;front.append((-68+13*t+2*math.sin(t*math.pi*2)+(6 if abs(xx)>20 else 0),16+(zm-16)*t))
  ribbons.append((xx-2.75,xx+2.75,front+[(y+12,z) for y,z in front[::-1]]))
sidehole=[(-72,2.9),(-60,2.9),(-60,12),(-61,12.5),(-61,15),(-62.5,16),(-63,18),(-64.8,19.5),(-66,21),(-67.2,19.5),(-69,18),(-69.5,16),(-71,15),(-71,12.5),(-72,12)]
sidehole=[(y-1.3,z) for y,z in sidehole]
for p in mesh.polygons:
 v=np.array([mesh.vertices[j].co[:] for j in p.vertices]);nx,ny,nz=p.normal;i=0
 # True visible front and both photographed side slope planes. Rear court-facing slope neutral.
 if bounded(v,[-39,-61,15],[39,-13,75]):
  if (max(abs(v[:,1]+61-(v[:,2]-15)*25/120))<EPS and ny<-.1) or (max(abs(abs(v[:,0])-39+(v[:,2]-15)*47/120))<EPS and abs(nx)>.1):i=1
 if bounded(v,[-39,-61,3],[39,-13,16]) and ((plane(v,1,-61) and ny<-.8) or (plane(v,0,-39) and nx<-.8) or (plane(v,0,39) and nx>.8)):i=1
 # Source-visible tower upright outside faces. Open slots remain open, never glazed.
 for x in [-40,40]:
  if boxgeom(v,x,-52,3,7,9,33) and abs(nz)<.1:i=1
 for x in [-26,26]:
  if boxgeom(v,x,55,3,11,15,64) and abs(nz)<.1:i=1
 # Exact original window cut back planes, only if final triangle survives union.
 for w,d,z,h in levels:
  for xx in [-w*.33,0,w*.33]:
   yy=-37-d/2+3.5
   if ny<-.8 and plane(v,1,yy) and bounded(v,[xx-w*.11,yy,z+2.1],[xx+w*.11,yy,z+7.1]):i=3
  for side in [-1,1]:
   xx=side*(w/2-3.5)
   for yy in [-37-d*.3,-37,-37+d*.3]:
    if nx*side>.8 and plane(v,0,xx) and bounded(v,[xx,yy-d*.1,z+2.1],[xx,yy+d*.1,z+7.1]):i=3
  if z>15:
   for xx in [-w*.33,0,w*.33]:
    if boxgeom(v,xx,-37-d/2,z+2.1,1.4,3,5):i=2
 # Projecting original horizontal caps. Upward surfaces unverified, kept neutral.
 grey=False
 for w,d,z,h in levels:
  grey|=boxgeom(v,0,-37,z+h-1,w+3,d+2,1.8)
 for k in range(4):grey|=boxgeom(v,0,-37,75+k*1.5,35+k*3.2,26+k*2.8,1.7)
 for x in [-40,40]:
  for k in range(3):grey|=boxgeom(v,x,-52,34+k*1.5,11+k*2.5,12+k*2.3,1.6)
 for x in [-26,26]:
  for zz in [29,66]:
   for k in range(3):grey|=boxgeom(v,x,55,zz+k*1.5,15+k*2.5,19+k*2.5,1.6)
 for zz in [19,25]:grey|=boxgeom(v,0,56,zz,68,21,1.6)
 for x in [-34,34]:
  grey|=boxgeom(v,x,19,22,10,74,3)
  for yy in [-13,0,13,26,39,51]:grey|=boxgeom(v,x,yy,2.8,3.5,4,20)
 grey|=boxgeom(v,0,-66,23,48,14,4)
 for k in range(3):grey|=boxgeom(v,0,-66,26+k*1.5,47+k*2,14+k,1.5)
 if grey:i=2 if nz<.8 else 0
 # Exact ribbon external polygon surfaces, not their bounding volumes.
 if any(prismface(v,poly,x0,x1) for x0,x1,poly in ribbons):i=2
 # Original portico frame: isolated front block plus exact side-wall/hole surfaces.
 if bounded(v,[-23,-75,3],[23,-71,25]):i=2
 for x in [-21,21]:
  if boxgeom(v,x,-66,3,4.2,18,22) or prismface(v,sidehole,x-2.1,x+2.1):i=2
 # Grey actual entry steps only, no blue court emblem or landscaping.
 for k in range(4):
  if boxgeom(v,0,-74+k*1.3,2.8,43,1.5,.5*(k+1)):i=4
 if max(v[:,2])<=3+EPS:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Pre-repair exterior only; photo capture dates unknown; rear court wall and rear crossblock windows neutral. No repairs, courtyard emblem, bells, flags, lettering, grids, vegetation or new trim faces added. Open portico and tower openings are not glass.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-180,-260,160),(0,0,40.6),230),'rear':((180,260,140),(0,0,40.6),230),'elevation':((0,-330,40.6),(0,0,40.6),230),'source-angle':((-200,-230,90),(0,-10,40.6),230),'top':((0,0,350),(0,0,0),230)}
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
