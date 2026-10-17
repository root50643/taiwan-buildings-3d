"""Read-only Blender projection preflight. No image rendering or saved-scene rewrite."""
from pathlib import Path
import bpy,sys,ast,json,struct,hashlib,itertools
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);revision=args[1];dest=Path(args[2]);assert not dest.exists()
source=root/'source/render_preview.py';tree=ast.parse(source.read_text());views=None
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='views' for t in node.targets):views=ast.literal_eval(node.value)
if views is None:raise RuntimeError('Views literal missing')
raw=(root/'models'/revision/'model.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];points=set()
for i in range(count):
 c=struct.unpack_from('<9f',raw,96+i*50)
 for j in range(3):points.add(tuple(c[j*3:j*3+3]))
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=100
cam=bpy.data.objects.new('Projection preflight camera',bpy.data.cameras.new('Projection preflight camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.clip_end=2000;cam.data.clip_start=.1
focus={'courtyard-gallery':(-71,-61,27,60,15,28),'courtyard-arcade':(-66,64,152,191,28,44)};rows=[]
for name,(pos,target,scale) in views.items():
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP' if name in focus else 'ORTHO';cam.data.lens=20 if name in focus else 50;cam.data.ortho_scale=scale;bpy.context.view_layer.update()
 chosen=points
 if name in focus:
  a,b,c,d,e,f=focus[name];chosen=list(itertools.product((a,b),(c,d),(e,f)))
 coords=[world_to_camera_view(scene,cam,Vector(p)) for p in chosen];bounds=[min(v.x for v in coords),max(v.x for v in coords),min(v.y for v in coords),max(v.y for v in coords)];margin=min(bounds[0],1-bounds[1],bounds[2],1-bounds[3]);ok=margin>=.025 and min(v.z for v in coords)>0
 rows.append({'view':name,'scope':'specified detail focus box' if name in focus else 'every original STL vertex','focus_box_mm':focus.get(name),'normalized_projection_bounds':bounds,'minimum_margin':margin,'passed':ok})
report={'passed':all(r['passed'] for r in rows),'revision':revision,'stl_sha256':hashlib.sha256(raw).hexdigest(),'render_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'resolution':[1000,780,100],'minimum_required_margin':.025,'views':rows};dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));
if not report['passed']:raise RuntimeError('Projection bounds failed')
