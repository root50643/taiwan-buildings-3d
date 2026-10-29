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
# Three official undated classroom photographs; actual mesh already scaled1,.64,.75.
palette=[('Unknown sides rear roofs base','#AAA79F',.86),('Muted pink brick observed front portal','#B58A78',.86),('Pale original frames bands arc caps','#C1C3B5',.85),('Grey green front window mixed opaque proxy','#798780',.65),('Visible front shoulder roof terracotta proxy','#B26E55',.86),('Original grey entrance steps','#999B93',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
import numpy as np
EPS=.012
# Coordinates restored for classification only. Original mesh and transforms unchanged.
def bounded(v,lo,hi):return np.all(v>=np.array(lo)-EPS) and np.all(v<=np.array(hi)+EPS)
def plane(v,k,t):return max(abs(v[:,k]-t))<EPS
def boxface(v,n,x,y,z,w,d,h):
 lo=[x-w/2,y-d/2,z];hi=[x+w/2,y+d/2,z+h]
 return bounded(v,lo,hi) and any((plane(v,k,lo[k]) and n[k]<-.8) or (plane(v,k,hi[k]) and n[k]>.8) for k in range(3))
def arcface(v,n,cx):
 if not bounded(v,[cx-7.2,-36.6,50],[cx+7.2,-35.3,52.5]):return False
 q=v[:,[0,2]]-[cx,50]
 poly=[[-7.2,0],[7.2,0]]+[[7.2*math.cos(a),2.5*math.sin(a)] for a in np.linspace(0,math.pi,25)]
 if plane(v,1,-36.6) and n[1]<-.8:return True
 if plane(v,1,-35.3) and n[1]>.8:return True
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=np.array(a);b=np.array(b);u=b-a;ll=np.linalg.norm(u)
  if ll<1e-6:continue
  t=(q-a)@u/(ll*ll)
  if min(t)>=-EPS and max(t)<=1+EPS and max(abs((q[:,0]-a[0])*u[1]-(q[:,1]-a[1])*u[0]))/ll<EPS:return True
 return False
for p in mesh.polygons:
 v=np.array([mesh.vertices[j].co[:] for j in p.vertices])/[1,.64,.75]
 n=np.array(p.normal)*[1,.64,.75];n=n/np.linalg.norm(n);nx,ny,nz=n;i=0
 for x in [-43,43]:
  # Only the actual front bar and frontal gable faces; rear/side walls remain neutral.
  if plane(v,1,-36) and ny<-.8 and bounded(v,[x-27,-36,2.8],[x+27,-36,52]):i=1
  if plane(v,1,-37) and ny<-.8 and bounded(v,[x-28.5,-37,42.4],[x+28.5,-37,56.6]):i=1
  for z in [6,16,26,36]:
   for dx in [-24,-18,-10.5,-3.5,3.5,10.5,18,24]:
    xx=x+dx
    if plane(v,1,-34.8) and ny<-.8 and bounded(v,[xx-2.35,-34.8,z],[xx+2.35,-34.8,z+6.3]):i=3
    if boxface(v,n,xx,-35.25,z,1.2,1.7,6.3) or boxface(v,n,xx,-35.25,z+4.3,4.7,1.7,1.2):i=2
   if boxface(v,n,x,-35.8,z-1.5,54.6,.9,1.15):i=2
  for dx in [-10.5,3.5,10.5]:
   xx=x+dx
   if plane(v,1,-34.85) and ny<-.8 and bounded(v,[xx-2.7,-34.85,44],[xx+2.7,-34.85,50.1]):i=3
   if boxface(v,n,xx,-35.25,44,1.3,1.7,6.1) or boxface(v,n,xx,-35.25,46.5,5.4,1.7,1.2):i=2
  for dx in [-14,0,14]:
   if boxface(v,n,x+dx,-35.5,24.5,2.2,1.4,26.8):i=2
  if boxface(v,n,x,-36.3,42.35,55,1.4,1.1):i=2
  if arcface(v,n,x):i=2
  # Only original shoulder slopes of front bars; no rearbar/high roof/flatroof extrapolation.
  for dx in [-21,21]:
   xx=x+dx
   if bounded(v,[xx-7.5,-37,42.4],[xx+7.5,-17,45.2]) and nz>.2:
    d=abs(v[:,0]-xx)
    slope=42.4+2.8*(7.5-d)/(7.5-.55)
    if (min(d)>=.55-EPS and max(abs(v[:,2]-slope))<EPS) or (max(d)<=.55+EPS and plane(v,2,45.2)):i=4
 # Source-visible brick portal original piers, not fabricated white feet/cap divisions.
 for x in [-13.5,13.5]:
  for y in [-32,-21]:
   if boxface(v,n,x,y,2.8,3.4,3.4,22.6) and abs(nz)<.1:i=1
 if plane(v,1,-34.5) and ny<-.8 and bounded(v,[-16,-34.5,26.2],[16,-34.5,30.3]):i=1
 if plane(v,1,-34) and ny<-.8 and bounded(v,[-15.5,-34,24],[15.5,-34,26.4]):i=1
 for k in range(3):
  if boxface(v,n,0,-42+k*2,2.8,31,2.8,.55*(k+1)):i=5
 # No panel-edge subdivision: fifth-storey solid brown patch omitted, remains brick.
 # Unknown inner/outer side window backs and rear array intentionally not assigned glass.
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Originalscaled above-ground classroom mass unchanged. Unknown inner/outer side windowbacks, rear walls, high/back roofs and flat roofs neutral. Fifth-storey brown solid panel omitted because originalfaces spanpanel andsurround; nofakeglass or new split. No B1, repair-completion claim, letters, landscaping, brick/roof seams or white columnfeet/caps withoutoriginal boundaries.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-160,-230,140),(0,0,21.225),200),'rear':((160,230,140),(0,0,21.225),200),'elevation':((0,-300,21.225),(0,0,21.225),200),'source-angle':((-150,-230,70),(0,-5,21.225),200),'top':((0,0,300),(0,0,0),200)}
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
