"""Blender 4.3.2: load exact original binary STL, render five views and save Blend.
Run blender -b -t 1 --python render_model.py -- --out <directory>.
No face repair, simplification, sculpting or generated-reference image is used.
"""
from pathlib import Path
import sys,struct,json,hashlib,argparse,math
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=R);p.add_argument('--views',default='all');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
out=a.out;out.mkdir(parents=True,exist_ok=True)
raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+n*50
verts=[];faces=[];lookup={}
for i in range(n):
 q=struct.unpack_from('<12fH',raw,84+50*i);f=[]
 for j in range(3):
  v=tuple(q[3+3*j:6+3*j])
  if v not in lookup:lookup[v]=len(verts);verts.append(v)
  f.append(lookup[v])
 faces.append(f)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new('Exact original STL triangles');mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new('NYCU grad3 actual STL',mesh);bpy.context.collection.objects.link(ob)
ob['stl_sha256']=hashlib.sha256(raw).hexdigest();ob['scope']='Fresh v2 bounded dual-wing exterior; real 3F connection omitted.'
def mat(name,color,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
ob.data.materials.append(mat('neutral architectural resin',(.62,.67,.69)))
ob.data.materials.append(mat('base neutral gray',(.38,.43,.46)))
ob.data.materials.append(mat('actual recessed glazing faces',(.19,.24,.27)))
ob.data.materials.append(mat('actual louver-box relief faces',(.28,.20,.15)))
P=json.loads((R/'parameters.json').read_text());S=P['scale_mm_per_m'];ox,oy=P['xy_origin_m'];q=P['facade_parameters_m']
for f in mesh.polygons:
 f.material_index=1 if all(mesh.vertices[v].co.z<=2.401 for v in f.vertices) else 0
 if f.material_index==1:continue
 c=f.center;x=c.x/S+ox;y=c.y/S+oy;z=(c.z-(P['base_mm'][2]-.05))/S
 for facade in P['facades']:
  ax,ay=facade['a'];bx,by=facade['b'];L=math.hypot(bx-ax,by-ay);ux=(bx-ax)/L;uy=(by-ay)/L;t=(x-ax)*ux+(y-ay)*uy;depth=-(x-ax)*uy+(y-ay)*ux
  if not -.66<=depth<=.86:continue
  k=round((t-q['end_margin']-q['window_width']/2)/facade['bay_pitch_m']);start=q['end_margin']+k*facade['bay_pitch_m']
  if k<0 or start+q['window_width']>L-q['end_margin']+1e-6 or not start-1e-4<=t<=start+q['window_width']+1e-4:continue
  for row in facade['rows']:
   z0=(row+1)*q['floor_pitch']+q['window_bottom_margin'];z1=min((row+2)*q['floor_pitch']-q['window_top_margin'],(P['north_low_terminal_roof_m'] if facade['mass']=='lower' else P['main_roof_m'])-q['window_top_margin'])
   if facade['mass']=='lower':z0=max(z0,max(x['height'] for x in P['terminal_pilotis'])+q['window_top_margin'])
   if facade['mass']=='upper':z0=max(z0,P['north_upper_terminal_bottom_m']+q['window_top_margin'])
   if any(start<pt1+.7 and start+q['window_width']>pt0-.7 and z0<pz1+.7 and z1>pz0-.7 for pt0,pt1,pz0,pz1 in facade.get('portals',[])):continue
   if z0-1e-4<=z<=z1+1e-4:
    if depth<-.64:f.material_index=2
    elif depth>=-.01 and start+.2-1e-4<=t<=start+.2+q['screen_width']+1e-4 and z<=min(z0+q['screen_height'],z1)+1e-4:f.material_index=3

# Terminal recessed backing is glazing-colored only on existing original STL faces.
for f in mesh.polygons:
 c=f.center;x=c.x/S+ox;y=c.y/S+oy;z=(c.z-(P['base_mm'][2]-.05))/S
 for pf in P.get('terminal_pilotis',[]):
  ax,ay=pf['a'];bx,by=pf['b'];L=math.hypot(bx-ax,by-ay);ux=(bx-ax)/L;uy=(by-ay)/L;t=(x-ax)*ux+(y-ay)*uy;depth=-(x-ax)*uy+(y-ay)*ux
  if pf.get('end_margin_start',pf['end_margin'])<=t<=L-pf.get('end_margin_end',pf['end_margin']) and 0.1<=z<=pf['height']-.1 and abs(depth+pf['depth'])<.01:f.material_index=2
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.1));ground=bpy.context.object;ground.name='Render ground, not printable model';ground.data.materials.append(mat('studio backdrop',(.88,.89,.90)))
world=bpy.data.worlds.new('studio') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25
for name,loc,power,size in [('key',(-120,100,210),45000,140),('fill',(140,-60,160),30000,120)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,18))-o.location).to_track_quat('-Z','Y').to_euler()
sun=bpy.data.lights.new('directional sunlight','SUN');sun.energy=2.0;sun.angle=.12;so=bpy.data.objects.new('directional sunlight',sun);bpy.context.collection.objects.link(so);so.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-25))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.use_denoising=False;scene.cycles.seed=19;scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=800;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
views={'front':((180,220,145),(0,0,18),178),'rear':((-180,-220,140),(0,0,18),178),'top':((0,0,250),(0,0,0),175),'elevation':((0,250,30),(0,0,25),172),'northeast-detail':((150,180,105),(13,5,22),145)}
cameras={}
for name,(pos,target,scale) in views.items():
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras[name]=o
scene.camera=cameras['front'];scene.render.filepath='//front.png'
# No transient private browser directories retained.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='FILE_BROWSER':
   try:area.spaces.active.params.directory=b'//'
   except Exception:pass
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
def strip_text(path):
 data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';res=data[:8];i=8
 while i<len(data):
  length=struct.unpack_from('>I',data,i)[0];chunk=data[i:i+length+12];typ=data[i+4:i+8]
  if typ not in (b'tEXt',b'zTXt',b'iTXt'):res+=chunk
  i+=length+12
 path.write_bytes(res)
selected=list(views) if a.views=='all' else a.views.split(',')
for name in selected:
 scene.camera=cameras[name];scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);strip_text(out/(name+'.png'))
report={'stl_sha256':hashlib.sha256(raw).hexdigest(),'triangles':len(faces),'mesh_vertices':len(verts),'blender':bpy.app.version_string,'render_engine':'CPU Cycles','samples':64,'threads':1,'seed':19,'png_metadata':'Only text chunks stripped; original rendered pixels unchanged','previews':{name:hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest() for name in selected}}
(out/'render-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
