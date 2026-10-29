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
# Four architect-project photographs; original3materials are onlyneutral displaycontrast.
palette=[('Unknown roof court ground end details','#AAA79F',.86),('Photographed muted pink brick family','#B89283',.86),('Grey white corridor slabs stair proxies colonnade','#B8BBB6',.87),('True recessed window opaque grey green','#465F60',.65),('Original separately supported frame green grey','#6A8D83',.72),('Open corridor recessed shadow not glass','#535D5B',.9)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
import numpy as np
S=150/88;BASE=2.;EPS=.012
floors=np.array([.30,4.15,7.75,11.35,14.95,18.55,22.15,25.75,29.35,32.95])+4
# All controls are original source-local geometry units. No geometry transformed.
def bounded(lo,hi):return all(mn[k]>=lo[k]-EPS and mx[k]<=hi[k]+EPS for k in range(3))
def plane(k,t):return abs(mn[k]-t)<EPS and abs(mx[k]-t)<EPS
def boxface(a,b,c,d,e,f):
 return bounded((a,c,e),(b,d,f)) and any((plane(k,lo) and n[k]<-.8) or (plane(k,hi) and n[k]>.8) for k,lo,hi in [(0,a,b),(1,c,d),(2,e,f)])
def edgeplane(q,poly):
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=np.array(a);b=np.array(b);u=b-a;ll=np.linalg.norm(u)
  if ll<1e-8:continue
  t=(q-a)@u/(ll*ll)
  if min(t)>=-EPS and max(t)<=1+EPS and max(abs((q[:,0]-a[0])*u[1]-(q[:,1]-a[1])*u[0]))/ll<EPS:return True
 return False
def inside2(q,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=np.array(a);b=np.array(b);u=b-a;ll=np.dot(u,u)
  if ll<1e-12:continue
  t=np.dot(q-a,u)/ll
  if -EPS<=t<=1+EPS and abs((q[0]-a[0])*u[1]-(q[1]-a[1])*u[0])/math.sqrt(ll)<EPS:return True
  if (a[1]>q[1])!=(b[1]>q[1]) and q[0]<(b[0]-a[0])*(q[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def rounded(x1,x2,y1,y2,r):
 return [(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))) for cx,cy,start in [(x2-r,y2-r,0),(x1+r,y2-r,90),(x1+r,y1+r,180),(x2-r,y1+r,270)] for a in np.linspace(start,start+90,9)]
# Stair proxy source surfaces precomputed; retains original thick walls, not metallic rail reconstruction.
stairs=[]
for sign in [-1,1]:
 ya,yb=sorted((sign*28.,sign*39.));y0,y1=sorted((sign*28.5,sign*38.5))
 for ii,z in enumerate((floors[1:5]+floors[2:6])/2):
  stairs.append(('platform',z,rounded(-33,-27,ya,yb,1.8 if ii==0 else .75)))
  pp=[(y0,z+.30),(y1,min(z+1.85,26.1)),(y1,min(z+1.85,26.1)+1.10),(y0,z+1.40)]
  stairs.append(('wedge',z,(pp,rounded(-33.1,-27,ya,yb,1.0))))
frames=[]
for z in floors[2:8]:
 for j in range(22):
  y=-28.8+j*2.72;frames.append((28.19,28.38,y,y+1.95,z+1.95,z+2.08))
for j in range(11):
 y=-28.8+j*5.4;frames.append((27.89,28.18,y+2.05,y+2.20,34.05,36.35))
for y in [-25,-19,-13,7,13,19,25]:frames.append((27.69,28.,y,y+4.1,7.85,8.45))
for sign in [-1,1]:
 mid=sign*31.9
 for z in floors[6:]:frames.append((5.32,5.52,mid-1.65,mid+1.65,z+1.5,z+1.7))
 for x1,x2,nn in [(-29.7,-21,2),(-21,-11,3),(-11,-1,4),(-1,7,5)]:
  a,b=sorted((sign*20.47,sign*20.68));mid=(x1+x2)/2
  for z in floors[:nn]:frames.append((mid-.1,mid+.1,a,b,z+1.05,z+2.8))
 for z in floors[:6]:
  for x in np.arange(-26,7,5.7):
   a,b=sorted((sign*38.68,sign*38.88));frames.append((x+1.85,x+2.05,a,b,z+.95,z+2.9))
for p in mesh.polygons:
 v=(np.array([mesh.vertices[j].co[:] for j in p.vertices])-[0,0,BASE])/S
 mn=v.min(axis=0);mx=v.max(axis=0);n=np.array(p.normal);nx,ny,nz=n;i=0
 # Actual east opaque facade and source-visible court end-core/stepped pod faces.
 if plane(0,29) and nx>.8 and bounded((29,-29.6,3.9),(29,29.6,40)):i=1
 if plane(0,10) and nx<-.8 and bounded((10,-29.5,4),(10,29.5,40)):i=2
 for sign in [-1,1]:
  a,b=sorted((sign*29.6,sign*40.2));c,d=sorted((sign*26,sign*37.8))
  if boxface(8,30.1,a,b,3.9,42.7) and abs(nz)<.1:
   # Stair-grid end plane and unseen grid grooves excluded, not new curtain wall.
   if not (plane(1,sign*40.2) and mn[0]>=17.99):i=1
  if boxface(4.5,10.3,c,d,4,42.7) and abs(nz)<.1:i=1
  a,b=sorted((sign*26.5,sign*39.5))
  if plane(1,sign*39.5) and ny*sign>.8 and bounded((-29.7,a,3.9),(10.2,b,26.2)):i=1
  if plane(1,sign*24) and ny*sign<-.8 and bounded((-29.7,-40,3.9),(10.2,40,26.2)):i=2
  for x1,x2,nn in [(-29.7,-21,2),(-21,-11,3),(-11,-1,4),(-1,7,5)]:
   a,b=sorted((sign*19.9,sign*24.4));hh=floors[nn]+.75
   if boxface(x1,x2,a,b,3.9,hh) and abs(nz)<.1:i=1
 # Recessed courtyard corridors are shadow proxies, not claims of all-glass curtain walls.
 if plane(0,13.3) and nx<-.8 and bounded((13.3,-29.5,4),(13.3,29.5,39.75)):i=5
 if plane(0,27) and nx>.8 and bounded((27,-29.5,36.95),(27,29.5,40.8)):i=5
 for sign in [-1,1]:
  if plane(1,sign*27.9) and ny*sign<-.8 and bounded((-34,-28,4),(5.6,28,26.2)):i=5
  if plane(1,sign*38.9) and ny*sign>.8 and bounded((11,-39,4),(17.5,39,40)):i=5
 # Actual east window backing planes, never large arch passage.
 if nx>.8:
  if plane(0,28.2):
   for z in floors[2:8]:
    for j in range(22):
     y=-28.8+j*2.72
     if bounded((28.2,y,z+.72),(28.2,y+1.95,z+2.92)):i=3
  if plane(0,27.9) and bounded((27.9,-28.8,34.05),(27.9,29.45,36.35)):i=3
  if plane(0,27.7) and bounded((27.7,-25,5.1),(27.7,29.1,11.1)):i=3
 if nx<-.8:
  for sign in [-1,1]:
   mid=sign*31.9
   if plane(0,5.5):
    for z in floors[6:]:
     if bounded((5.5,mid-1.65,z+.65),(5.5,mid+1.65,z+2.95)):i=3
   if plane(0,5) and bounded((5,mid-3.7,40.6),(5,mid+3.7,41.8)):i=3
 for sign in [-1,1]:
  if plane(1,sign*20.65) and ny*sign<-.8:
   for x1,x2,nn in [(-29.7,-21,2),(-21,-11,3),(-11,-1,4),(-1,7,5)]:
    for z in floors[:nn]:
     if bounded((x1+1.15,min(sign*20.65,sign*20.65),z+1.05),(x2-.95,max(sign*20.65,sign*20.65),z+2.8)):i=3
  if plane(1,sign*38.7) and ny*sign>.8:
   for z in floors[:6]:
    for x in np.arange(-26,7,5.7):
     if bounded((x,sign*38.7,z+.95),(x+3.9,sign*38.7,z+2.9)):i=3
 # Only original narrow frame surface planes. Outward normals prevent shared-plane false colors.
 if (mn[0]>=27.68 or (mn[0]>=5.30 and mx[0]<=5.54) or (mn[0]>=-27 and mx[0]<=7 and (abs(mn[1])>20.45))):
  for f in frames:
   if boxface(*f):i=4;break
 # Existing corridor piers/bars grey; thick walls are not fabricated thin green rails.
 if mn[0]>=9.95 and mx[0]<=13.51:
  for z in floors:
   for y in np.arange(-27,28,5.4):
    if z<12 and abs(y)<5:continue
    if boxface(9.97,13.5,y-.38,y+.38,z+.8,min(z+3.25,40)):i=2
   for y in np.arange(-28,29,5.4):
    if z<9 and abs(y)<5:continue
    if boxface(13.25,13.43,y,y+.34,z+1,min(z+3,39.8)):i=2
 # Known visible roof-edge sides/soffits; all broad upward roof surfaces stay unknown.
 if nz<.8:
  if boxface(9.7,29.5,-29.8,29.8,39.85,40.65) or boxface(12,28,-29,29,41.4,42.05):i=2
  for sign in [-1,1]:
   a,b=sorted((sign*24,sign*40))
   if boxface(-33.8,10.4,a,b,25.95,26.8):i=2
  for j in range(11):
   y=-28.8+j*5.4
   if boxface(26.2,30,y-.2,y+4.45,36.4,37.05):i=2
 # West low arcade and its true supporting box surfaces.
 if mx[0]<=-23.79:
  for f in [(-34,-23.8,-20,20,4.05,4.75),(-34,-29,-20,20,8,8.7),(-34,-33.3,-20,20,8.65,9.35),(-29.7,-29,-20,20,8.65,9.35)]:
   if boxface(*f) and nz<.8:i=2
  for y in np.linspace(-19,19,8):
   if boxface(-33,-31.7,y-.55,y+.55,.55,8.05):i=2
 # Exact original stair-core box, rounded-platform outline and wedge support surfaces.
 if bounded((-33.12,-39.12,3.84),(-27,39.12,26.25)):
  for sign in [-1,1]:
   a,b=sorted((sign*27.75,sign*39.1))
   if boxface(-30.5,-27.2,a,b,3.9,26.2):i=2
  for typ,z,poly in stairs:
   if typ=='platform':
    if mn[2]>=z-EPS and mx[2]<=z+.65+EPS and (((plane(2,z) or plane(2,z+.65)) and all(inside2(q,poly) for q in v[:,:2])) or edgeplane(v[:,:2],poly)):i=2
   else:
    pp,xy=poly
    if mn[0]>=-33.1-EPS and mx[0]<=-29.1+EPS and mn[2]>=z-EPS and mx[2]<=z+4.2+EPS:
     if edgeplane(v[:,1:],pp) or edgeplane(v[:,:2],xy):i=2
     if (plane(0,-33.1) or plane(0,-29.1)) and all(inside2(q,pp) for q in v[:,1:]) and all(inside2(q,xy) for q in v[:,:2]):i=2
  for sign in [-1,1]:
   ya,yb=sorted((sign*28.5,sign*38.5));pp=[(ya,3.85),(ya+1.25,3.85),(yb,9.3),(yb,10.3)]
   if bounded((-32.8,ya,3.85),(-30.2,yb,10.3)) and (edgeplane(v[:,1:],pp) or ((plane(0,-32.8) or plane(0,-30.2)) and all(inside2(q,pp) for q in v[:,1:]))):i=2
   for k in range(7):
    yy=ya+k*1.3
    if boxface(-32.7,-29.65,yy-.02,yy+1.32,3.85,4.2+(k+1)*.60):i=2
 # Base and unverified court texture remain neutral; actual open voids never filled.
 if mx[2]<=.01:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Original3materials were explicitlyneutral/displaycontrast, not photo-derived finishes. Newarchitect-photo broadfamilies only; undated photos and2004projectyear are not2026appearance. Longcorridor recesses shadow notglass, realarch/arcade/roofholes remainopen. Unverifiedendgrid grooves, broadrooftops and courttexture neutral. Thickoriginalstairs greyproxy notgreenmetalrail reconstruction; noletters/railinggeometry/brickjoints/landscape added. OriginalQA preserved, not rerun printcertification.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-235,-205,165),(-5,0,37.4),220),'rear':((235,205,160),(-5,0,37.4),220),'elevation':((-300,0,37.4),(-5,0,37.4),220),'source-angle':((-230,-140,110),(-5,0,37.4),220),'top':((0,0,350),(-5,0,0),220)}
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
