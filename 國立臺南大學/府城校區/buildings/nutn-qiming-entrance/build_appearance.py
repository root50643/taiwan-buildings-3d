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
# Three official legacy photographs support visible original entrance-end components, not full hall.
palette=[('Unknown rear roof caps and cropped surfaces neutral','#AAA79F',.86),('Observed independent brick tower front and left','#AB5947',.87),('Observed cream hall and original portal components','#CDC7AF',.85),('Opaque mixed original entry and tower window backs','#526361',.65),('Original coarse horizontal entry bars dark','#5A554A',.82)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def front(x,y,z,w,h):return plane(1,y) and n[1]<-.999 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def left(x,y,z,d,h):return plane(0,x) and n[0]<-.999 and bounds((x,y-d/2,z),(x,y+d/2,z+h))
def boxsurface(x,y,z,w,d,h):
 aa=np.array([x-w/2,y-d/2,z]);bb=np.array([x+w/2,y+d/2,z+h])
 return bounds(aa,bb) and any((plane(k,aa[k]) and n[k]<-.999) or (plane(k,bb[k]) and n[k]>.999) for k in range(3))
def underside(x,y,z,w,d):return plane(2,z) and n[2]<-.999 and bounds((x-w/2,y-d/2,z),(x+w/2,y+d/2,z))
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else 0
def clip(poly,v,t):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  va=t-np.dot(a,v);vb=t-np.dot(b,v);ia=va>=-1e-9;ib=vb>=-1e-9
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(va/(va-vb)))
 return out
def circleclip(poly):
 for k in range(40):
  th=(k+.5)*2*np.pi/40;v=np.array([np.cos(th),np.sin(th)]);poly=clip(poly,v,9*np.cos(np.pi/40)+np.dot([-17,-23],v))
  if not poly:break
 return poly
def slabclip(poly):
 for v,t in [([1,0],44),([-1,0],14),([0,1],-14.5),([0,-1],31.5)]:
  poly=clip(poly,np.array(v),t)
  if not poly:break
 return poly
def lower_floor_union():
 if not (plane(2,36) and n[2]<-.999):return False
 pts=[v.copy() for v in q[:,:2]];a=area(pts);cp=circleclip(pts);rp=slabclip(pts);over=slabclip(cp)
 return area(cp)+area(rp)-area(over)>=a-max(1e-4,a*1e-4)
def round_outer():
 if lo[2]<36-EPS or hi[2]>44+EPS or n[1]>=-.001:return False
 for k in range(40):
  th=(k+.5)*2*np.pi/40;v=np.array([np.cos(th),np.sin(th)])
  if max(abs((q[:,:2]-[-17,-23])@v-9*np.cos(np.pi/40)))<EPS and np.dot(n[:2],v)>.999:return True
 return False
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if front(52,-21,2.8,24,81) or left(40,4,2.8,50,81):i=1
 if front(-29,-23,2.8,72,49) or left(-65,9,2.8,64,49) or front(20,-11.5,2.8,55,41):i=2
 for x in [1,19,37]:
  if front(x,-9.5,4,14,30):i=3
 for z in [5,21,37,53,69]:
  if front(61,-19.5,z,5,12):i=3
  if plane(0,61) and n[0]>.999 and bounds((61,0,z),(61,8,z+12)):i=3
 for z in [13,23]:
  if boxsurface(19,-12,z,54,1.1,1.1):i=4
 for x in [-10,39]:
  if boxsurface(x,-29,3,4,6,48):i=2
 if front(15,-33,49,61,3) or underside(15,-21,49,61,24):i=2
 if front(15,-31.5,36,58,2.8) or lower_floor_union():i=2
 if front(15,-32,38,54,4.5):i=2
 if round_outer():i=2
 if front(-29,-25.5,51,78,3) or left(-68,9,51,69,3):i=2
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original partial entrance-end hall geometry retained, not complete auditorium','Three actual official NUTN photographs personally read, capture dates unknown. Legacywebsite updateyear is not photo capture or2026condition. Independenttower front-Y/left-X planes brick; observedhall front/left andentrywall cream. Trueentry threewindowbacks andoriginalsplit towerstrip backs mixedopaqueproxy, no new continuousglassstrip orfinegrid. Original twohorizontalentrybars dark, twoportalpiers cream withsmallcomponenthiddenface familycontinuation disclosed. Originalslab frontfascias/visibleundersides, frontbalustrade, front40facet curvedouterwall/loweredge andoriginalprojectingfloorunderside cream; exact originalcircle+slab union only, no newfacecuts. Hallroofslab front/left verticalfascias cream, allbroadrooftops/capsneutral. Curvedinner/back/top, towercap, clerestory, treeobscuredsideribbon, steps/base, rearcut andunseen broadright/backtower neutral. No newletters/posters/handrails/tiles/equipment orgeometry. OriginalprintQA/support limitations unchanged','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-220,-270,155),(0,0,43),215),'rear':((220,270,155),(0,0,43),215),'elevation':((0,-350,43),(0,0,43),215),'source-angle':((-240,-230,110),(0,0,43),215),'top':((0,0,380),(0,0,43),215)}
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
