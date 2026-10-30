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
# Exact original folded surface supports, bounded facade segment only.
palette=[('Unknown cut rear roof sides and unresolved boundary','#AAA79F',.86),('Original sunshade structure silver grey','#BFC3BF',.8),('Supported separable tan wall fields','#C8BBA0',.86),('Original true window surfaces opaque mixed glazing','#718987',.8),('Original raised folded-surface ribs','#BEC8C6',.8),('Source-supported platform grey tile','#92928C',.86),('Original canopy mixed translucent/frame proxy','#82918E',.86),('Existing front step treads and risers','#A2A19A',.86)]
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
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.8) or (plane(k,b[k]) and n[k]>.8) for k in range(3))
GLASS_PROFILE=[(17,-12.6),(24,-12.6),(27,-12.3),(30,-11.),(33,-9.1),(36,-8.4),(43,-8.4),(47,-9.),(50,-11.6),(53,-12.6),(56,-12.6),(59,-12.),(62,-10.1),(65,-8.4),(72,-8.4),(79,-8.8),(85,-10.1),(89,-11.)]
HORIZONTAL_RIB_Z=[18,26.5,35,43.5,52,60.5,69,77.5,87.5];rib_x=[30.9,36.3,41.7,47.1]
xs=sorted(set([30.,48.]+[v+d for v in rib_x for d in [-.85,-.55,.55,.85]]));zs=sorted(set([z for z,y in GLASS_PROFILE]+[v+d for v in HORIZONTAL_RIB_Z for d in [-.3,0,1.1,1.4]]));zs=[z for z in zs if 17<=z<=89]
def strength(v,centers):return max(max(0,min(1,(.85-abs(v-c))/.3)) for c in centers)
sv=[];sr=[]
for z in zs:
 for x in xs:
  y=float(np.interp(z,[p[0] for p in GLASS_PROFILE],[p[1] for p in GLASS_PROFILE]));r=max(strength(x,rib_x),strength(z,[v+.55 for v in HORIZONTAL_RIB_Z]));sv.append([x,y-1.4*r,z]);sr.append(r)
sv=np.asarray(sv,dtype=np.float32).astype(float);st=[];sm=[]
for j in range(len(zs)-1):
 for k in range(len(xs)-1):
  a=j*len(xs)+k;b=a+1;c=b+len(xs);d=a+len(xs)
  for tri in [(a,b,c),(a,c,d)]:st.append(sv[list(tri)]);sm.append(4 if max(sr[t] for t in tri)>1e-7 else 3)
st=np.asarray(st);sm=np.asarray(sm);sn=np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);sn/=np.linalg.norm(sn,axis=1)[:,None];slo=st.min(1);shi=st.max(1)
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def area(P):return abs(sum(cross(a,b) for a,b in zip(P,P[1:]+P[:1])))*.5 if len(P)>=3 else 0.
def intersection_area(P,T):
 P=[v.copy() for v in P];T=[v.copy() for v in T]
 if cross(T[1]-T[0],T[2]-T[0])<0:T=T[::-1]
 for a,b in zip(T,T[1:]+T[:1]):
  if not P:return 0.
  O=[];v=b-a
  for c,d in zip(P,P[1:]+P[:1]):
   fc=cross(v,c-a);fd=cross(v,d-a);ic=fc>=-1e-9;idd=fd>=-1e-9
   if ic:O.append(c)
   if ic!=idd:O.append(c+(d-c)*(fc/(fc-fd)))
  P=O
 return area(P)
def surf_material():
 if not bounds((30,-15,17),(48,-7,89)) or n[1]>=-.05:return 0
 cand=np.where(np.all(shi>=lo-EPS,axis=1)&np.all(slo<=hi+EPS,axis=1)&(sn@n>.9999))[0]
 A=area([v[[0,2]] for v in q]);cover={3:0.,4:0.}
 for t in cand:
  if max(abs((q-st[t,0])@sn[t]))>EPS:continue
  cover[int(sm[t])]+=intersection_area(q[:,[0,2]],st[t][:,[0,2]])
 for mat in [3,4]:
  if cover[mat]>=A-max(1e-7,A*2e-5):return mat
 return 0
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if plane(1,-11) and n[1]<-.99 and bounds((-67,-11,19),(33,-11,89)):i=2
 for row,z in enumerate([20,31,42,53,64,75]):
  for col,x in enumerate([-60,-47,-34,-21,-8,5,18]):
   if plane(1,-9) and n[1]<-.99 and bounds((x-5.5,-9,z),(x+5.5,-9,z+8)):i=3
   if boxface(x,-10.5,z,1.1,4.2,8):i=1
   for dx in ([-4,-2.,2.5] if (row+col)%3==0 else [-4,-2.]):
    if boxface(x+dx,-14.5,z,1.1,6,8):i=1
  for x in [-66.5,-53.5,-40.5,-27.5,-14.5,-1.5,11.5,24.5]:
   if boxface(x,-13,z-1,1.5,5.5,10):i=1
  if boxface(-20,-13,z-1.2,96,6,1.4):i=1
 for x in [-57,-44,-31,-18,-5,8,21]:
  if plane(1,-10) and n[1]<-.99 and bounds((x-5,-10,86),(x+5,-10,88.3)):i=3
 for x in range(-63,25,4):
  if boxface(x,-13,83,1.1,4,4):i=1
 if boxface(-19,-13.5,89,102,8,1.6) and abs(n[2])<.8:i=1
 # Ambiguous tower front tan/grey boundary is not invented on unsplit faces.
 for z in [23,35,47,59,71]:
  for x in [49,56]:
   if plane(1,-9.5) and n[1]<-.99 and bounds((x-2.3,-9.5,z),(x+2.3,-9.5,z+7)):i=3
 # Existing short return field only, not synthetic back closure.
 if plane(0,71.5) and n[0]>.99 and bounds((71.5,6,3),(71.5,34,79)):i=2
 for z in [20,31,42,53,64]:
  for y in [14,24]:
   if plane(0,69.75) and n[0]>.99 and bounds((69.75,y-3,z),(69.75,y+3,z+7)):i=3
 if plane(1,-15.5) and n[1]<-.99 and bounds((-68,-15.5,3),(24,-15.5,19)):i=5
 if plane(1,-8.6) and n[1]<-.99 and bounds((28,-8.6,3),(48,-8.6,14)):i=3
 if boxface(39,-17,14,25,12,1.6):i=6
 for x in [29,39,49]:
  if boxface(x,-16,14,1.3,13,1.8):i=1
 for k in range(12):
  x=-58+k*4.4;h=.8+k*1.17
  if bounds((x-2.3,-21.2,2.8),(x+2.3,-13.2,2.8+h)) and ((plane(2,2.8+h) and n[2]>.99) or (plane(0,x-2.3) and n[0]<-.99)):i=7
 j=surf_material()
 if j:i=j
 if hi[2]<=3+EPS:i=0
 p.material_index=i;indices.append(i)

assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown surfaces neutral'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing surface proxy; original through-slot remains open','Original NCUE engineering main front segment only, deliberate28mmdepth and synthetic rear closure, not whole building. Four official/architect photographs personally viewed; university composite lower Teaching Building1 excluded. Dates unknown,2016URL not capturedate,2008-11 originalrecord not freshly reverified. Exact original folded front float32 support triangles regenerated from GLASS_PROFILE/xs/zs; full final triangles tested by coplanar/outnormal and XZ clipped intersection union area by material. Original relief shoulders/rib planes distinct from flatback glass, no new bands or face splits. Source light spandrels unsegmented omitted. Tower planar front mixed tan/grey boundary lacks exact face support so remainsneutral; true windowbacks still supported. Main shade fins/shelves/columns grey, actual tan fields and shortreturn only, platformgrey and small canopy coarse mixed proxy. Minor hidden faces of same shade members continue source-supported family. Broad roofs/cutrear/unknowns neutral; no letters, tiles, PV or newgeometry. Original0.1995percent printQA warning retained, not rerun','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((190,-270,165),(0,0,49),220),'rear':((-170,260,155),(0,0,49),220),'elevation':((0,-300,49),(0,0,49),220),'source-angle':((170,-290,100),(0,0,49),220),'top':((0,0,400),(0,0,49),220)}
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
