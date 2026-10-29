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
# One library-hosted aerial freshly viewed; inaccessible Commons image not used.
palette=[('Unknown left outer wall roof plant and artificial rear cut','#AAA79F',.86),('Supported front masonry ribs and right end pale beige','#C8BDA8',.86),('Original left sunshades frames and frontal caps silver grey','#B2B8B6',.8),('True recessed backing mixed opaque grey green','#5E7472',.82)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x0,x1,y0,y1,z0,z1):
 if not bounds((x0,y0,z0),(x1,y1,z1)):return False
 return any((plane(k,a) and n[k]<-.8) or (plane(k,b) and n[k]>.8) for k,a,b in [(0,x0,x1),(1,y0,y1),(2,z0,z1)])
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);lo=q.min(0);hi=q.max(0);n=np.array(p.normal);i=0
 # Long front wall/rib planes and photographed right end, never blanket side symmetry.
 if plane(1,-7) and n[1]<-.8 and bounds((-15,-7,10),(63,-7,64)):i=1
 if plane(1,-3) and n[1]<-.8 and bounds((-15,-3,64.8),(63,-3,76)):i=1
 if plane(0,63) and n[0]>.8 and bounds((63,-7,10),(63,23,76)):i=1
 # Same-family continuation on original visible front supports, partially hidden by trees.
 for xc in [-14,3,20,37,54,65]:
  if boxface(xc-1.1,xc+1.1,-9.1,-5.9,3,13):i=1
 # Left original horizontal and vertical shade supports, exact primitive face bounds.
 for z in range(13,65,4):
  if boxface(-63.5,-24.5,-15.75,-12.65,z,z+1):i=2
 for xc in [-56,-44,-32]:
  if boxface(xc-.55,xc+.55,-15.15,-12.65,11,64):i=2
 # Upper left terrace actual frames and original front-facing lintel host.
 for xc in [-60,-47,-34]:
  if boxface(xc-.7,xc+.7,-11.2,-7.4,72,78.8):i=2
 if plane(1,-8.5) and n[1]<-.8 and bounds((-64.5,-8.5,70),(-25.5,-8.5,80)):i=2
 # Actual front cornice/roof fascia only; roof tops and all plant blocks stay neutral.
 for x0,x1,y,z0,z1 in [(-16.5,64.5,-8.5,63,65.4),(-18,66,-12,75.3,77.1),(-67.5,-22.5,-16.9,79.5,81.2),(-15.5,65.5,-12.1,77,79)]:
  if plane(1,y) and n[1]<-.8 and bounds((x0,y,z0),(x1,y,z1)):i=2
 # True window cut bottoms only, rather than treating every dark gap as glass.
 if plane(1,-12.25) and n[1]<-.8 and bounds((-62.5,-12.25,11),(-25.5,-12.25,64)):i=3
 if plane(1,-6.25) and n[1]<-.8 and bounds((-62.5,-6.25,72),(-27.5,-6.25,78.8)):i=3
 for xc in range(-11,60,3):
  if plane(1,-5.3) and n[1]<-.8 and bounds((xc-.85,-5.3,14),(xc+.85,-5.3,59)):i=3
 for xc in range(-10,61,7):
  if plane(1,-1.4) and n[1]<-.8 and bounds((xc-2.4,-1.4,67),(xc+2.4,-1.4,73.3)):i=3
 # Right end slits are observed; left end slits remain unverified neutral.
 if plane(0,61.8) and n[0]>.8:
  for yy in [0,4,8,12]:
   if bounds((61.8,yy-.8,15),(61.8,yy+.8,55)):i=3
  for yy in [-2,3,8,13]:
   if bounds((61.8,yy-.85,61),(61.8,yy+.85,63.7)):i=3
 if hi[2]<=3+EPS:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Original single warm display material. Only one490x327library-hosted event aerial freshly viewed; Commons2024photo403 was stopped and not used as seen evidence. Limited front ribs/right end warm beige, original left sunshades/frames silvergrey, true window cut backs opaque mixed grey-green. Trees hide lower supports: same-family continuation inference. Purple sign banner is not masonry and omitted. Left outer wall/slits, artificial rear cut, flat roofs and broad plant/penthouse remain neutral. No geometry split/new frames/lettering. Event2020andfilename20160120notverifiedphotodates; no2024or2026restorationclaim. Original partial section and print limitations unchanged.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-220,160),(0,0,45.5),220),'rear':((195,230,160),(0,0,45.5),220),'elevation':((0,-260,45.5),(0,0,45.5),220),'source-angle':((210,-230,150),(0,0,45.5),220),'top':((0,0,350),(0,0,45.5),220)}
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
