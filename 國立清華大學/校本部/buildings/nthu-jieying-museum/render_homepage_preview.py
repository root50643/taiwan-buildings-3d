"""Render the museum homepage cover without changing the delivered model.
Run from this model directory:
    blender --disable-autoexec --background --factory-startup \
        --python render_homepage_preview.py
Optional: append -- --out /path/to/output to leave the model directory untouched.

Only the camera and square image framing change. The original nine technical
views, native scene, geometry, material indices, lighting and world are preserved.
The source native scene is opened with Python auto-execution disabled.
"""
import bpy, json, pathlib, hashlib, math, struct, argparse, sys
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=pathlib.Path,default=ROOT,help='Directory containing the original native scene and mesh-data.npz')
parser.add_argument('--out',type=pathlib.Path,default=ROOT)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROOT=args.source.resolve()
OUT=args.out.resolve()
(OUT/'previews').mkdir(parents=True,exist_ok=True)
(OUT/'qa').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'nthu-jieying-museum.blend'),load_ui=False,use_scripts=False)
scene = bpy.context.scene
cam = scene.camera
meshes = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
assert len(meshes) == 1, [o.name for o in meshes]
ob = meshes[0]
D = np.load(ROOT/'mesh-data.npz', allow_pickle=False)
vs = np.array([list(v.co) for v in ob.data.vertices], dtype=np.float32)
fs = np.array([list(p.vertices) for p in ob.data.polygons], dtype=np.uint32)
ms = np.array([p.material_index for p in ob.data.polygons], dtype=np.int32)
assert np.array_equal(vs,D['vertices'])
assert np.array_equal(fs,D['faces'])
assert np.array_equal(ms,D['materials'])
before = {'camera': list(cam.location), 'rotation': list(cam.rotation_euler), 'ortho_scale':cam.data.ortho_scale,'resolution':[scene.render.resolution_x,scene.render.resolution_y]}

# NUU canonical delta=(180,-240,130), transformed -90 degrees about Z:
# NUU front -Y -> museum road facade -X; NUU right +X -> museum right -Y.
delta = Vector((-240,-180,130))
target = Vector((78,70,43))
cam.location = target + delta
cam.rotation_euler = (-delta).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
scene.render.resolution_x=1200
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
# Center actual projected delivered vertices. Fit the entire base, not only body.
R=cam.rotation_euler.to_matrix()
right=R@Vector((1,0,0));up=R@Vector((0,1,0))
pts=[ob.matrix_world@v.co for v in ob.data.vertices]
xs=[p.dot(right) for p in pts];ys=[p.dot(up) for p in pts]
move=right*((min(xs)+max(xs))/2-target.dot(right))+up*((min(ys)+max(ys))/2-target.dot(up))
target += move; cam.location = target+delta
cam.data.ortho_scale=max(max(xs)-min(xs),max(ys)-min(ys))/.82
bpy.context.view_layer.update()
q=[world_to_camera_view(scene,cam,p) for p in pts]
assert all(.035<p.x<.965 and .035<p.y<.965 and p.z>0 for p in q)
scene.render.filepath=str(OUT/'previews/homepage-three-quarter.png')
scene.render.use_stamp=False
bpy.ops.render.render(write_still=True)
p=OUT/'previews/homepage-three-quarter.png';raw=p.read_bytes();clean=raw[:8];pos=8
while pos<len(raw):
    n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
    if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME']:clean+=raw[pos:pos+n+12]
    pos+=n+12
p.write_bytes(clean)
report={
 'source_commit':'c8ac293be078b33134be795fae1ac30843cbc7d2',
 'source_blend_blob_sha':'65e5eac5c2290500882360eae60959aeeb712810',
 'source_renderer_blob_sha':'7dad070ad29b9e47ba5afdb104b4e34fbd8eaa83',
 'source_blend_sha256':hashlib.sha256((ROOT/'nthu-jieying-museum.blend').read_bytes()).hexdigest(),
 'source_mesh_sha256':hashlib.sha256((ROOT/'mesh-data.npz').read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,
 'scope':'camera and square framing only; geometry, 9 materials, lighting, world and color management unchanged; original files not saved or overwritten',
 'geometry_exact_match':{'vertices':bool(np.array_equal(vs,D['vertices'])),'faces':bool(np.array_equal(fs,D['faces'])),'material_indices':bool(np.array_equal(ms,D['materials']))},
 'visible_mesh_count':len(meshes),'vertex_count':len(vs),'triangle_count':len(fs),'material_count':len(ob.data.materials),
 'original':before,
 'candidate':{'camera':list(cam.location),'target':list(target),'camera_delta':list(delta),'ortho_scale':cam.data.ortho_scale,'resolution':[1200,1200],'elevation_deg':math.degrees(math.atan2(delta.z,math.hypot(delta.x,delta.y))),'yaw_from_road_facade_deg':math.degrees(math.atan2(abs(delta.y),abs(delta.x))),'screen_bounds':{'min_x':min(p.x for p in q),'max_x':max(p.x for p in q),'min_y':min(p.y for p in q),'max_y':max(p.y for p in q)},'all_vertices_in_frame':True},
 'output':{'file':p.name,'bytes':len(clean),'sha256':hashlib.sha256(clean).hexdigest()}}
(OUT/'qa/homepage-camera-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
