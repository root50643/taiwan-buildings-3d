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
# Official high-angle photograph supports visible original components, not all faces.
palette=[('Unseen rear sides terrain and cropped window neutral', '#AAA79F', 0.86), ('Observed terracotta tower and shallow roof', '#B86C50', 0.87), ('Observed original front gray wall and spandrels', '#777B7B', 0.85), ('Observed independent gray slab roof', '#858788', 0.88), ('Original small light frames and cross', '#C9C9BA', 0.83), ('Opaque mixed clear window and frame backs', '#71807A', 0.68), ('Original right deep back red mixed family', '#985448', 0.7), ('Original right deep back yellow mixed family', '#AD9A4C', 0.7), ('Original right deep back green mixed family', '#527B57', 0.7)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.0012;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def facebox(a,b,k,sg):return bounds(a,b) and plane(k,a[k] if sg<0 else b[k]) and n[k]*sg>.999
def surface(a,b):return any(facebox(a,b,k,sg) for k in range(3) for sg in [-1,1])
def front(a,b):return facebox(a,b,1,-1)
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);q=(q-np.array([0,0,3]))/2.5;n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 # Visible front and right tower faces, never hidden sides/top.
 for a,b in [((-7.6,-24,-.01),(-3,-18,16.7)),((-7.6,-23.6,16.65),(-5.7,-18,17.45)),((-5.9,-21.7,16.65),(-3,-18,18.15))]:
  if front(a,b) or facebox(a,b,0,1):i=1
 # Independent roof slabs, only top and front fascia.
 for a,b in [((-22.5,-22.7,11.65),(-5.5,-7.4,12.35)),((-6.5,-21.7,11.35),(20,-4.3,11.9))]:
  if front(a,b) or facebox(a,b,2,1):i=3
 # Original shallow gable upper facets including the print-flat ridge.
 if bounds((-22.5,-7.6,12),(-5.5,20.4,13.4)) and n[2]>.98:
  if plane(2,13.4) and bounds((-14.25,-7.6,13.4),(-13.75,20.4,13.4)):i=1
  for xa,za,xb,zb in [(-22.5,12,-14.25,13.4),(-13.75,13.4,-5.5,12)]:
   slope=(zb-za)/(xb-xa);normal=np.array([-slope,0,1]);normal/=np.linalg.norm(normal)
   if np.dot(n,normal)>.999 and max(abs(q[:,2]-(za+slope*(q[:,0]-xa))))<EPS and lo[0]>=xa-EPS and hi[0]<=xb+EPS:i=1
 if front((-6,-21,-.01),(19.5,-4.8,11.4)) or front((-22,-22,-.01),(-6,19.8,11.7)):i=2
 for z in [4.35,7.7]:
  if front((-2.8,-21.08,z),(19.45,-20.4,z+.55)):i=2
 # True deep opening backs. Recess returns remain neutral unless explicit support below.
 if plane(1,-21.1) and n[1]<-.999 and bounds((-21.1,-21.1,4.4),(-8.1,-21.1,11.05)):i=5
 if plane(1,-20.9) and n[1]<-.999 and bounds((-20.8,-20.9,1),(-8.2,-20.9,3.8)):i=5
 for z in [2.4,7.1,12.1]:
  for x in [-6.1,-4.8]:
   if plane(1,-23.5) and n[1]<-.999 and bounds((x-.22,-23.5,z),(x+.22,-23.5,z+2.3)):i=5
  for y in [-22.5,-21.2]:
   if plane(0,-3.5) and n[0]>.999 and bounds((-3.5,y-.22,z),(-3.5,y+.22,z+2.3)):i=5
 for x,col in [(-1,6),(2.5,7),(6,8),(9.5,8)]:
  for dx in [-.5,.5]:
   if plane(1,-20.45) and n[1]<-.999 and bounds((x+dx-.34,-20.45,1.7),(x+dx+.34,-20.45,10.75)):i=col if dx>0 else 5
 for a,b,y in [((11.3,-20.45,8.3),(16.8,-20.45,10.75),-20.45),((11,-20.1,.9),(17.2,-20.1,4.5),-20.1)]:
  if plane(1,y) and n[1]<-.999 and bounds(a,b):i=5
 # Actual small grid/door frame components only; hidden sides same-family approximation.
 frames=[]
 for x in np.linspace(-20.8,-8.4,12):frames.append(((x-.16,-21.5,4.4),(x+.16,-21.05,11.05)))
 for z in np.linspace(4.65,10.8,7):frames.append(((-21.1,-21.5,z-.15),(-8.1,-21.05,z+.15)))
 for x in np.linspace(-20.4,-8.6,7):frames.append(((x-.18,-21.25,1),(x+.18,-20.85,3.8)))
 frames.append(((-20.8,-21.25,2.9),(-8.2,-20.85,3.25)))
 for x in [-1,2.5,6,9.5,18]:
  for z in [2.75,6.15,9.55]:frames.append(((x-.86,-20.68,z),(x+.86,-20.4,z+.25)))
 for x in [12.55,14.05,15.55]:frames.append(((x-.16,-20.7,8.3),(x+.16,-20.4,10.75)))
 frames.append(((11.3,-20.7,9.5),(16.8,-20.4,9.8)))
 for x in [11.3,13.3,15.3,17]:frames.append(((x-.18,-20.4,1),(x+.18,-20.05,4.4)))
 frames.extend([((-6.1,-21.1,17.3),(-5.5,-20.5,21)),((-7.15,-21.1,19.6),(-4.45,-20.5,20.2))])
 if any(surface(a,b) for a,b in frames):i=4
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original connected chapel and Aitu geometry preserved including S2.5 and BASE3','Original scene uses three neutral display-contrast materials, not source-guided color and not literally single-material. Official high-angle photo capture date unknown, original2013-2024 geometric synthesis not new2026survey. Front/right tower and visible vertical steppedfascias terracotta; hiddenrear/left/tops neutral. Originalshallow roof upper facets and print-flat ridge terracotta; verticalgable andunderside neutral. Chapel/Aitu slabtop andfrontfascia gray; hiddenedges neutral. Frontchapel/Aitu originalsurvivingwall/spandrelfaces gray. Only actual truecutbacks mixedopaque; firstfour Aitu rightdeepbacks mutedred/yellow/green/green, leftmixedpalegray; croppedlastgroup neutral. Originalcontinuoushalfback includes whiteframe/lowerclear panes: coarse opaque colorfamily proxy, not exact stainedglass or transparency, no newhorizontalcolorseam. Originalgrid/entrybars/cross light withsmallhiddenface familycontinuation disclosed. All side/rearwalls annex, stairs groundbase retainingmasses and unknowns neutral. No newtext/emblem/AC/plants/tiles orgeometry. Original278layer thinfeature warnings including36 cross samples above1percent andmaximum6.140099622784399percent loss preserved; no physicalprint or slicer approval','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((220,-310,180),(0,0,27),225),'rear':((-220,310,180),(0,0,27),225),'elevation':((0,-350,27),(0,0,27),225),'source-angle':((240,-310,220),(0,0,27),225),'top':((0,0,380),(0,0,27),225)}
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
