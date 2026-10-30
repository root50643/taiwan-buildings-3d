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
# Official document supports front arcade and front roof only.
palette=[('Unknown rear ends backing wall and base','#AAA79F',.86),('Original front arcade red brick','#A46656',.86),('Original stone rings plinths cornice and steps','#AAA99B',.86),('Original front roof grey tile family proxy','#797D79',.86),('Actual door window backing opaque shade proxy','#555A53',.86)]
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
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.99) or (plane(k,b[k]) and n[k]>.99) for k in range(3))
def archpoly(x,z,w,h):
 r=w/2;s=z+h-r
 return np.array([(x-r,z),(x+r,z),(x+r,s)]+[(x+r*np.cos(t),s+r*np.sin(t)) for t in np.linspace(0,np.pi,25)[1:]])
def edges(poly):
 ans=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  e=b-a;v=np.array([e[1],-e[0]]);v/=np.linalg.norm(v);ans.append((a,v))
 return ans
def inside(p,ed):return all(max((p-a)@v)<=EPS for a,v in ed)
def area(p):return abs(sum(np.cross(b-a,c-a) for a,b,c in [(p[0],p[k],p[k+1]) for k in range(1,len(p)-1)]))*.5 if len(p)>2 else 0.
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
xs=[c+dx for c in [-57,-38,-19,0,19,38,57] for dx in [-4.5,4.5]]
rings=[]
for x in xs:
 outer=archpoly(x,4.5,8.5,12.55);inner=archpoly(x,4.3,6.8,11.9);original=archpoly(x,4.5,6.8,11.7)
 rings.append((x,edges(outer),edges(inner),edges(original)))
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0;qq=q[:,[0,2]]
 if plane(1,-21.2) and n[1]<-.99 and bounds((-69,-21.2,3),(69,-21.2,19)):i=1
 for x,oe,ie,ae in rings:
  if bounds((x-4.25,-21.95,4.5),(x+4.25,-20.25,17.05)) and inside(qq,oe):
   if ((plane(1,-21.95) and n[1]<-.99) or (plane(1,-20.25) and n[1]>.99)) and area(clip(qq,ie))<1e-6:i=2
   for a,v in oe:
    if max(abs((qq-a)@v))<EPS and n@np.array([v[0],0,v[1]])>.999:i=2
   for a,v in ie:
    if max(abs((qq-a)@v))<EPS and n@np.array([-v[0],0,-v[1]])>.999:i=2
  # Remaining original cut-reveal behind trim; actual open arcade is not filled.
  if bounds((x-3.4,-21.2,4.5),(x+3.4,-18.8,16.2)) and inside(qq,ae):
   for a,v in ae:
    if max(abs((qq-a)@v))<EPS and n@np.array([-v[0],0,-v[1]])>.999:i=2
 for c in [-57,-38,-19,0,19,38,57]:
  if boxface(c+9.5,-20,3.2,3.8,4.3,2.8):i=2
  for dx in [-4.5,4.5]:
   x=c+dx;z=5 if dx<0 else 9;h=9.4 if dx<0 else 5.4
   if plane(1,-14) and n[1]<-.99 and bounds((x-2.6,-14,z),(x+2.6,-14,z+h)):i=4
 if boxface(0,-20,18,141,3.8,1.6):i=2
 if boxface(0,-16,3,140,11,1.6):i=2
 for z,d in [(3,2.4),(3.6,1.8)]:
  if boxface(0,-24+d/2,z,138,d,.8):i=2
 nn=np.array([0,-17/23.8,1]);nn/=np.linalg.norm(nn)
 if bounds((-70,-22,20),(70,1.8,37)) and max(abs((q-np.array([0,-22,20]))@nn))<EPS and n@nn>.999:i=3
 if boxface(0,1.8,36.1,140,1.5,1.2):i=3
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing backing only; true open arcade remains open; dark material only on actual existing door and window backing faces','Official disaster-plan PDF physical71 two exterior photos and72 plan personally viewed; only exterior color used, no interior reconstruction.2023-10-25 document date and PDF metadata not capture dates. Four Commons pages returned403 stopped, no pixels or2026EXIF freshly verified. Original front arcade wall,14 independent original arch_trim rings, plinths/frontcornice/steps and only front roof slope plus ridge supported. True original24segment arch ring outer-minus-inner polygon and exact supporting planes, no new geometry. Door/window back y=-14 mixed opaque shade, original backing wall y=-15 neutral and open corridor never filled. Rear high windows/wall/roof slope and both gable ends unknownneutral, model-end source mapping unverified. No brick joints tiles signs plants glazing or topology edits; original printQA and geometry limitations retained','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((170,-250,140),(0,0,17),220),'rear':((-180,250,140),(0,0,17),220),'elevation':((0,-300,17),(0,0,17),220),'source-angle':((220,-230,100),(0,0,17),220),'top':((0,0,400),(0,0,17),220)}
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
