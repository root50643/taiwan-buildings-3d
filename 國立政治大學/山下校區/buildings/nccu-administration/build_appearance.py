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
# Two official front/left photographs support original material families; opposite side/court/roof neutral.
palette=[('Unknown opposite court roof surfaces neutral','#AAA79F',.86),('Observed front and left stone family','#B7B7B2',.86),('Opaque mixed actual front left and entry window backs','#525A5C',.66),('Original entry door backing muted mixed','#55504C',.7),('Original coarse doorway supports pale','#AFB0A8',.82),('Observed approximate original stair treads risers','#A2A7A4',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.004;indices=[];original_scale=150/(118*1.7);inverse_scale=np.array([original_scale,original_scale*1.7,original_scale])
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def front(x,y,z,w,h):return plane(1,y) and n[1]<-.999 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def left(x,y,z,d,h):return plane(0,x) and n[0]<-.999 and bounds((x,y-d/2,z),(x,y+d/2,z+h))
def boxsurface(x,y,z,w,d,h):
 aa=np.array([x-w/2,y-d/2,z]);bb=np.array([x+w/2,y+d/2,z+h])
 return bounds(aa,bb) and any((plane(k,aa[k]) and n[k]<-.999) or (plane(k,bb[k]) and n[k]>.999) for k in range(3))
# Disjoint 2D rectangle-union cells support whole original triangles, including connected slots.
rectangles=[]
for x in [-59,-48,-37,37,48,59]:
 for z in [24,38,52,66,85,98]:rectangles.append((x-3.5,x+3.5,z,z+7))
for x in [-25,-12,0,12,25]:
 for z in [85,98]:rectangles.append((x-4,x+4,z,z+7))
 rectangles.append((x-1.35,x+1.35,91,98))
cells=[];zs=sorted(set(v for r in rectangles for v in r[2:]))
for za,zb in zip(zs,zs[1:]):
 ints=sorted((a,b) for a,b,c,d in rectangles if c<zb and d>za);merged=[]
 for a,b in ints:
  if merged and a<=merged[-1][1]+1e-8:merged[-1][1]=max(merged[-1][1],b)
  else:merged.append([a,b])
 cells.extend((a,b,za,zb) for a,b in merged)
def area(v):return abs(sum(np.cross(v[(i+1)%len(v)]-v[0],v[(i+2)%len(v)]-v[0]) for i in range(len(v)-2)))/2 if len(v)>=3 else 0
def clip(poly,k,t,sg):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  va=sg*(a[k]-t);vb=sg*(b[k]-t);ia=va>=-1e-9;ib=vb>=-1e-9
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(va/(va-vb)))
 return out
def in_window_union():
 pts=[v.copy() for v in q[:,[0,2]]];a=area(pts);covered=0
 for x0,x1,z0,z1 in cells:
  if hi[0]<x0-EPS or lo[0]>x1+EPS or hi[2]<z0-EPS or lo[2]>z1+EPS:continue
  p=pts
  for k,t,sg in [(0,x0,1),(0,x1,-1),(1,z0,1),(1,z1,-1)]:
   p=clip(p,k,t,sg)
   if not p:break
  covered+=area(p)
 return covered>=a- max(1e-5,a*1e-5)
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices])/inverse_scale;n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if front(0,-50,2.8,132,104) or left(-66,0,2.8,100,104) or front(0,-31,3,64,78):i=1
 if plane(1,-48) and n[1]<-.999 and in_window_union():i=2
 for y in range(-41,46,7):
  for z in [22,36,50,64,84,98]:
   if left(-61.5,y,z,4.7,8):i=2
 for z in [39,53,67]:
  for x in range(-25,26,10):
   if front(x,-29.4,z,7,7):i=2
 if front(0,-29.5,4,31,27):i=3
 for x in [-26,26]:
  if boxsurface(x,-44,2.8,4.5,5,65):i=1
 for z in [53,67]:
  if boxsurface(0,-44,z,57,6,3):i=1
 for x in [-64,-36,36,64]:
  if boxsurface(x,-49,3,4,5,16):i=1
 for y in [-44,-26,-8,10,28,45]:
  if boxsurface(-64,y,2.8,4,4,15):i=1
 for x in [-13,-6,6,13]:
  if boxsurface(x,-33,2.8,1.5,5.5,30):i=4
 if boxsurface(0,-34,30.8,36,8,3):i=4
 for x in [-18,18]:
  if boxsurface(x,-33,2.8,4,7,31):i=4
 for k in range(7):
  y=-57+k*1.3;h=.5+k*.65
  if front(0,y-.85,2.8,65,h) or (plane(2,2.8+h) and n[2]>.999 and bounds((-32.5,y-.85,2.8+h),(32.5,y+.85,2.8+h))):i=5
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original complete approximate building geometry and Ystretch preserved, no added components','Two actual fullsize official NCCU wiki photographs front and leftside personally read, capturedates unknown. Front and left original outer planes andentrybackwall stone; actual recessed frontrectangles andconnectedslots are opaque coarsewindow proxy, including original unsplit spandrel/curtain/shadow mixture notpuretransparentglass. Leftloggia originalbackplanes similarlymixed, no inventedrails. Trueentrybackwallwindowcuts anddoorback only, neverfill hugeportal/undercroft/courtvoids. Original portal/groundfront/leftarcade supports stone family withsmallhiddenface extrapolation disclosed. Original four doorway reliefbars, two sideposts andoverdoorbeam pale. Existingsevenstep front/top gray approximation notexactphoto count/dimensions. Unseenright/rear/court/roof/returns/undercroftceilings/base neutral. No newletters, solarequipment, fineframes, textures orgeometry. Original geometric andprintQA limits unchanged','No actual trial print; original approximate-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-230,-270,170),(0,0,40),215),'rear':((230,270,170),(0,0,40),215),'elevation':((0,-350,40),(0,0,40),215),'source-angle':((-270,-210,125),(0,0,40),215),'top':((0,0,380),(0,0,40),215)}
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
