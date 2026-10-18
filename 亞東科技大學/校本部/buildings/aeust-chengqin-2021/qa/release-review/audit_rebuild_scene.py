"""Independently rebuild STL and inspect/evaluate the saved Blender scene.

Never saves candidate source, scene, QA, previews or parameters. The sole render
is written under review-evidence and uses the stored scene/camera/settings.
"""
from pathlib import Path
from collections import Counter
import ast
import importlib.util
import hashlib
import importlib.metadata
import json
import os
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
COPY = Path(os.environ['CHENGQIN_PACKAGE']).resolve()
assert not ROOT.is_relative_to(COPY), 'Copy review tree outside the target package before running'
OUT = ROOT/'scene-evidence'
OUT.mkdir(exist_ok=True)
env = dict(os.environ)
build = subprocess.run([sys.executable, str(COPY/'source/build_model.py'),
                        '--output-dir', str(OUT/'rebuilt')],
                       cwd=ROOT, env=env, capture_output=True)
(OUT/'rebuild.stdout.log').write_bytes(build.stdout)
(OUT/'rebuild.stderr.log').write_bytes(build.stderr)
if build.returncode:
    raise RuntimeError('Rebuild failed; see preserved stdout/stderr')

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(scene, model):
    return dict(
        units=[scene.unit_settings.system,scene.unit_settings.length_unit,float(scene.unit_settings.scale_length)],
        objects=sorted((o.name,o.type,o.hide_render,o.hide_viewport,[list(row) for row in o.matrix_world]) for o in scene.objects),
        camera=[scene.camera.data.type,float(scene.camera.data.ortho_scale),float(scene.camera.data.clip_start),float(scene.camera.data.clip_end)],
        materials=[dict(name=m.name,diffuse=list(m.diffuse_color),base=list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value),roughness=float(m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value)) for m in model.data.materials],
        face_materials=[f.material_index for f in model.data.polygons],
        lights=sorted((o.name,o.data.type,o.data.energy,o.data.size,list(o.data.color)) for o in scene.objects if o.type=='LIGHT'),
        world=[list(scene.world.node_tree.nodes['Background'].inputs[0].default_value),scene.world.node_tree.nodes['Background'].inputs[1].default_value],
        renderer=[scene.render.engine,scene.cycles.device,scene.cycles.samples,scene.cycles.seed,scene.cycles.use_denoising,scene.render.threads,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.view_settings.view_transform,scene.view_settings.look])

def key(points):
    # Canonical cyclic order, without allowing a flipped triangle orientation.
    p = [struct.pack('<3f', *v) for v in points]
    return min(b''.join(p[k:]+p[:k]) for k in range(3))

def stl_keys(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count
    result=Counter()
    for i in range(count):
        xyz=struct.unpack_from('<9f',data,84+50*i+12)
        result[key([xyz[0:3],xyz[3:6],xyz[6:9]])]+=1
    return result

stl = COPY/'models/v1/model.stl'
blend = COPY/'models/v1/scene.blend'
before = {str(p.relative_to(COPY)):sha(p) for p in COPY.rglob('*') if p.is_file()}
bpy.ops.wm.open_mainfile(filepath=str(blend), load_ui=False, use_scripts=False)
scene = bpy.context.scene
depsgraph = bpy.context.evaluated_depsgraph_get()
objects=[]
scene_faces=Counter()
for obj in scene.objects:
    row=dict(name=obj.name, type=obj.type, hide_render=obj.hide_render,
             hide_viewport=obj.hide_viewport, matrix_world=[list(v) for v in obj.matrix_world],
             modifiers=[dict(name=m.name,type=m.type,show_render=m.show_render) for m in obj.modifiers],
             constraints=[c.type for c in obj.constraints])
    if obj.type=='MESH':
        eval_obj=obj.evaluated_get(depsgraph)
        mesh=eval_obj.to_mesh()
        mesh.calc_loop_triangles()
        tris=Counter(key([eval_obj.matrix_world @ mesh.vertices[i].co for i in t.vertices])
                     for t in mesh.loop_triangles)
        row.update(vertices=len(mesh.vertices),polygons=len(mesh.polygons),triangles=sum(tris.values()),
                   materials=[m.name if m else None for m in mesh.materials])
        if obj.name=='Chengqin_print_mesh_mm':
            scene_faces=tris
        eval_obj.to_mesh_clear()
    objects.append(row)

model=bpy.data.objects.get('Chengqin_print_mesh_mm')
assert model and scene.camera
saved_camera=dict(name=scene.camera.name, type=scene.camera.data.type,
                  location=list(scene.camera.location),rotation_euler=list(scene.camera.rotation_euler),
                  ortho_scale=scene.camera.data.ortho_scale)
manifest=json.loads((COPY/'previews/v1/render-manifest.json').read_text('utf8'))
framing={}
for view in manifest['views']:
    scene.camera.location=view['position']
    scene.camera.rotation_euler=(Vector(view['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.ortho_scale=view['ortho_scale']
    bpy.context.view_layer.update()
    pts=[world_to_camera_view(scene,scene.camera,model.matrix_world@v.co) for v in model.data.vertices]
    framing[view['name']]=dict(x_range=[min(p.x for p in pts),max(p.x for p in pts)],
        y_range=[min(p.y for p in pts),max(p.y for p in pts)],
        depth_range=[min(p.z for p in pts),max(p.z for p in pts)],
        all_model_vertices_within_image=all(0<=p.x<=1 and 0<=p.y<=1 and scene.camera.data.clip_start<p.z<scene.camera.data.clip_end for p in pts))

# Restore the saved front camera, then perform one independent visual render.
scene.camera.location=saved_camera['location']
scene.camera.rotation_euler=saved_camera['rotation_euler']
scene.camera.data.ortho_scale=saved_camera['ortho_scale']
bpy.context.view_layer.update()
render_path=OUT/'independent-front.png'
scene.render.filepath=str(render_path)
settings=dict(engine=scene.render.engine,resolution=[scene.render.resolution_x,scene.render.resolution_y],
              percentage=scene.render.resolution_percentage,
              samples=scene.cycles.samples,device=scene.cycles.device,
              denoising=scene.cycles.use_denoising,threads=scene.render.threads,
              film_transparent=scene.render.film_transparent,
              compositor_enabled=bool(getattr(scene,'use_nodes',False)))
saved_snapshot=snapshot(scene,model)
bpy.ops.render.render(write_still=True)
after = {str(p.relative_to(COPY)):sha(p) for p in COPY.rglob('*') if p.is_file()}
report=dict(python=sys.version,bpy=bpy.app.version_string,
    packages={p:importlib.metadata.version(p) for p in ['numpy','trimesh','manifold3d','bpy']},
    stl_sha256=sha(stl),blend_sha256=sha(blend),
    rebuild_returncode=build.returncode,rebuilt_stl_sha256=sha(OUT/'rebuilt/model.stl'),
    rebuilt_stl_bytes_identical=(stl.read_bytes()==(OUT/'rebuilt/model.stl').read_bytes()),
    stl_triangle_count=sum(stl_keys(stl).values()),
    scene_evaluated_triangles=sum(scene_faces.values()),
    evaluated_world_oriented_binary32_triangle_multiset_equals_stl=(scene_faces==stl_keys(stl)),
    units=dict(system=scene.unit_settings.system,length_unit=scene.unit_settings.length_unit,
               scale_length=scene.unit_settings.scale_length),
    objects=objects,saved_camera=saved_camera,framing=framing,render_settings=settings,
    images=[dict(name=i.name,source=i.source,filepath=i.filepath,packed=bool(i.packed_file)) for i in bpy.data.images],
    linked_libraries=[l.filepath for l in bpy.data.libraries],texts=[t.name for t in bpy.data.texts],
    preview_hashes={v['name']:dict(sha256=sha(COPY/'previews/v1'/(v['name']+'.png')),
                                  equals_manifest=sha(COPY/'previews/v1'/(v['name']+'.png'))==v['png_sha256']) for v in manifest['views']},
    manifest_stl_sha_matches=manifest['stl_sha256']==sha(stl),
    manifest_scene_sha_matches=manifest['scene_sha256']==sha(blend),
    independent_front_png_sha256=sha(render_path),
    independent_front_png_bytes_equals_candidate=render_path.read_bytes()==(COPY/'previews/v1/front.png').read_bytes(),
    candidate_package_unchanged=before==after,
    scope='One front render from saved scene; no resave, no repeated full-set renders. Geometry equality includes evaluation and world transforms; not photographic or physical print proof.')

# Independently compare source-created scene and literal view definitions.
source=COPY/'source/render_preview.py'
tree=ast.parse(source.read_text('utf8'))
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
view_node=next(n for n in main.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='views' for t in n.targets))
source_views=ast.literal_eval(view_node.value)
report['source_views_equal_manifest']=all(dict(name=n,position=list(pos),target=list(targ),ortho_scale=scale)=={k:v[k] for k in ['name','position','target','ortho_scale']} for (n,pos,targ,scale),v in zip(source_views,manifest['views'])) and len(source_views)==len(manifest['views'])==8
report['expected_eight_view_names_present']=set(v['name'] for v in manifest['views'])=={'front','rear','long-front','long-rear','end-negative-x','end-positive-x','top','connector'}
report['seven_full_views_framed']=all(v['all_model_vertices_within_image'] for name,v in framing.items() if name!='connector')
report['connector_view_is_declared_detail_crop']=True
spec=importlib.util.spec_from_file_location('reviewed_render_source',source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fresh,fresh_model=module.create_scene()
_,pos,target,scale=source_views[0]
fresh.camera.location=pos
fresh.camera.rotation_euler=(Vector(target)-fresh.camera.location).to_track_quat('-Z','Y').to_euler()
fresh.camera.data.ortho_scale=scale
bpy.context.view_layer.update()
fresh_snapshot=snapshot(fresh,fresh_model)
report['source_created_scene_state_matches_saved']=saved_snapshot==fresh_snapshot
report['source_state_difference_keys']=[k for k in saved_snapshot if saved_snapshot[k]!=fresh_snapshot[k]]
report['source_scene_state_scope']='Actual units, all object world transforms/types/visibility, camera projection, complete face materials and shader colors, lights, world and render/display settings. Source create_scene only, never its save/render main.'
report['render_source_sha256']=sha(source)
(OUT/'saved-scene-state.json').write_text(json.dumps(saved_snapshot,indent=2)+'\n',encoding='utf8')
(OUT/'source-scene-state.json').write_text(json.dumps(fresh_snapshot,indent=2)+'\n',encoding='utf8')

(OUT/'rebuild-scene.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['objects','images','preview_hashes','framing']},ensure_ascii=False,indent=2))
