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
# Official dormitory photo and aerial; original three bars retained unchanged.
palette=[('Unknown tower body rear and ground','#AAA79F',.86),('Observed front wall and original piers warm near white','#CECABF',.86),('Observed separate floor beams pale blue grey','#A8B1B4',.82),('Corridor backing mixed opaque shadow not pure glass','#72716A',.88),('Lantern recessed solid red panels not glass','#A04F37',.85),('Observed pitched roof muted red brown','#A76D60',.85),('Observed gable and front eave grey white','#C6C8C3',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002
indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x0,x1,y0,y1,z0,z1):
 if not bounds((x0,y0,z0),(x1,y1,z1)):return False
 return any((plane(k,a) and n[k]<-.8) or (plane(k,b) and n[k]>.8) for k,a,b in [(0,x0,x1),(1,y0,y1),(2,z0,z1)])
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);lo=q.min(0);hi=q.max(0);n=np.array(p.normal);i=0
 for yc in [-34,0,34]:
  # Primary supported front only: tower body's unsplit blue/cream mosaic is excluded.
  if plane(1,yc-9.5) and n[1]<-.8 and bounds((-62,yc-9.5,2.3),(32,yc-9.5,34.3)):i=1
  for xc in np.arange(-61,34,8):
   if boxface(xc-.55,xc+.55,yc-10.85,yc-9.15,2.3,33.8):i=1
  for z in [9,15.3,21.6,27.9]:
   if boxface(-62,36,yc-11,yc-9,z,z+1.2):i=2
  # Actual flat surviving cut backs; no invented window grids or air conditioning.
  if plane(1,yc-7.8) and n[1]<-.8:
   for xc in np.arange(-57,32,8):
    for z in [4.5,10.8,17.1,23.4,29.7]:
     if bounds((xc-2.9,yc-7.8,z),(xc+2.9,yc-7.8,z+4.1)):i=3
  # Raised lantern: original front panel host and its three true recessed red backs.
  if plane(1,yc-8.5) and n[1]<-.8 and bounds((34,yc-8.5,38),(52,yc-8.5,45)):i=6
  if plane(1,yc-7.8) and n[1]<-.8:
   for xc in [37,42,47]:
    if bounds((xc-1.7,yc-7.8,39.4),(xc+1.7,yc-7.8,43.4)):i=4
  # Exact original roof support planes. Both roof slopes are supported by aerial.
  for xc,w,d,z,rise in [(-6,114,21,34,3.2),(43,21,20,44.6,3.1)]:
   if not bounds((xc-w/2,yc-d/2,z-.2),(xc+w/2,yc+d/2,z+rise)):continue
   if abs(n[0])<.01 and n[2]>.8 and abs(n[1])>.1:
    for side in [-1,1]:
     # Roof face is one true planar slope, never a centroid-limited half patch.
     if np.all((q[:,1]-yc)*side>=-EPS) and max(abs(q[:,2]-(z+rise-side*(2*rise/d)*(q[:,1]-yc))))<EPS:i=5
   # Source-facing positive-X gables, not whole triangular surfaces painted roof red.
   if plane(0,xc+w/2) and n[0]>.8 and np.all(q[:,2]<=z+rise-(2*rise/d)*abs(q[:,1]-yc)+EPS) and lo[2]>=z-EPS:i=6
   # Front eave slab fascia; top/underside and unverified opposite eave stay neutral.
   if plane(1,yc-d/2) and n[1]<-.8 and hi[2]<=z+.55+EPS:i=6
 if hi[2]<=2.4+EPS:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Original scene is single warm display material. Official dormitory and aerial photos support front near-white walls/piers, pale blue-grey original floor beams, mixed opaque corridor cut backs, solid red lantern panels, and red-brown original pitched roof planes. Unsplittable tower-body blue/cream mosaic remains neutral; no fake patches, glass claim, new railing or AC geometry. Unknown rear walls/windows, distant gables and bottom remain neutral. Photograph dates unverified; not a claim of unchanged2026condition. Original geometry/preview/QA remain intact.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-220,155),(0,0,24),220),'rear':((195,230,160),(0,0,24),220),'elevation':((0,-260,24),(0,0,24),220),'source-angle':((190,-230,125),(0,0,24),220),'top':((0,0,350),(0,0,24),220)}
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
