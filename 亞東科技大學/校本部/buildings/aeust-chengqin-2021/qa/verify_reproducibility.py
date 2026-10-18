"""Verify exact STL rebuild and saved Blender mesh identity, without re-rendering."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import importlib.util
from collections import Counter

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]


def scene_state(scene, obj):
    """Compare meaningful saved/source display state without rendering or saving."""
    def vec(v):
        return [round(float(x),6) for x in v]
    return {'units':[scene.unit_settings.system,scene.unit_settings.length_unit,scene.unit_settings.scale_length],
        'renderer':[scene.render.engine,scene.cycles.device,scene.cycles.samples,scene.cycles.use_denoising,scene.cycles.seed,
                    scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],
        'camera':[vec(scene.camera.location),vec(scene.camera.rotation_euler),scene.camera.data.type,scene.camera.data.ortho_scale],
        'materials':[(m.name,vec(m.diffuse_color),vec(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value),
                      float(m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value)) for m in obj.data.materials],
        'face_material_indices':[p.material_index for p in obj.data.polygons],
        'lights':sorted((o.name,vec(o.location),vec(o.rotation_euler),o.data.type,float(o.data.energy),float(o.data.size))
                         for o in scene.objects if o.type=='LIGHT'),
        'world':[vec(scene.world.node_tree.nodes['Background'].inputs[0].default_value),float(scene.world.node_tree.nodes['Background'].inputs[1].default_value)],
        'view_transform':[scene.view_settings.view_transform,scene.view_settings.look],
        'objects':sorted((o.name,o.type) for o in scene.objects)}


def triangle_key(points):
    # Cyclic rotation preserves orientation. Binary32 is the exported STL lattice.
    p = [struct.pack('<3f', *v) for v in points]
    return min(b''.join(p[k:]+p[:k]) for k in range(3))


def stl_triangles(path):
    data = path.read_bytes()
    n, = struct.unpack_from('<I', data, 80)
    if len(data) != 84+50*n:
        raise ValueError('Invalid binary STL length')
    faces = Counter()
    for k in range(n):
        p = struct.unpack_from('<9f', data, 84+50*k+12)
        faces[triangle_key([p[:3],p[3:6],p[6:]])] += 1
    return faces


def main():
    stl = ROOT/'models/v1/model.stl'
    original = stl.read_bytes()
    # Keep temporary rebuilds inside this writable package workspace. Some
    # managed Windows environments redirect OS temp to an unwritable container.
    with tempfile.TemporaryDirectory(prefix='chengqin-rebuild-', dir=ROOT/'qa') as temp:
        process = subprocess.run([sys.executable,str(ROOT/'source/build_model.py'),
            '--output-dir',temp],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if process.returncode != 0:
            raise RuntimeError(process.stderr)
        rebuilt = (Path(temp)/'model.stl').read_bytes()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/v1/scene.blend'),load_ui=False)
    obj = bpy.data.objects.get('Chengqin_print_mesh_mm')
    if obj is None or obj.type != 'MESH':
        raise ValueError('Missing print mesh')
    mesh = obj.data
    mesh.calc_loop_triangles()
    scene_faces = Counter(triangle_key([obj.matrix_world @ mesh.vertices[i].co
        for i in face.vertices]) for face in mesh.loop_triangles)
    scene_matches = scene_faces == stl_triangles(stl)
    manifest = json.loads((ROOT/'previews/v1/render-manifest.json').read_text())
    preview_hashes = {v['name']:hashlib.sha256((ROOT/'previews/v1'/
        (v['name']+'.png')).read_bytes()).hexdigest()==v['png_sha256'] for v in manifest['views']}
    scene=bpy.context.scene
    saved_scene_state=scene_state(scene,obj)
    framing=[]
    for v in manifest['views']:
        scene.camera.location=v['position']
        scene.camera.rotation_euler=(Vector(v['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler()
        scene.camera.data.ortho_scale=v['ortho_scale']
        bpy.context.view_layer.update()
        points=[world_to_camera_view(scene,scene.camera,obj.matrix_world @ p.co) for p in obj.data.vertices]
        bounds=[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(2)]
        fits=all(lo>=0 and hi<=1 for lo,hi in bounds)
        framing.append({'view':v['name'],'normalized_projected_xy_bounds':bounds,
                        'entire_print_mesh_fits_frame':fits,'detail_crop_intended':v['name']=='connector'})
    report = {
        'stl_sha256':hashlib.sha256(original).hexdigest(),
        'rebuild_returncode':process.returncode,
        'rebuilt_stl_bytes_identical':original==rebuilt,
        'saved_blend_oriented_triangle_multiset_equals_stl_binary32':scene_matches,
        'scene_triangles':sum(scene_faces.values()),
        'print_object_transform_is_identity':all(abs(obj.matrix_world[i][j]-(1 if i==j else 0))<1e-12 for i in range(4) for j in range(4)),
        'scene_units':'millimetres, scale_length=0.001',
        'render_ground_excluded_from_print_mesh':bpy.data.objects.get('RenderGround_NOT_STL') is not None,
        'reference_image_datablocks':len(bpy.data.images),
        'manifest_scene_hash_matches':hashlib.sha256((ROOT/'models/v1/scene.blend').read_bytes()).hexdigest()==manifest['scene_sha256'],
        'manifest_stl_hash_matches':manifest['stl_sha256']==hashlib.sha256(original).hexdigest(),
        'eight_preview_hashes':preview_hashes,
        'camera_framing':framing,
        'scope':'Mesh identity and existing preview hashes only; does not repeat rendering or prove photographic accuracy',
    }
    spec=importlib.util.spec_from_file_location('chengqin_render_source',ROOT/'source/render_preview.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fresh_scene,fresh_obj=module.create_scene()
    first=manifest['views'][0]
    fresh_scene.camera.location=first['position']
    module.aim(fresh_scene.camera,first['target'])
    fresh_scene.camera.data.ortho_scale=first['ortho_scale']
    source_state=scene_state(fresh_scene,fresh_obj)
    source_state_match=saved_scene_state==source_state
    report['source_create_scene_state_matches_saved_scene']=source_state_match
    report['scene_state_comparison_scope']='Units, renderer, default camera, materials and per-face assignment, lights, world, display transform and object names/types; source create_scene executed without render/save. Mesh triangle identity checked separately.'
    report['render_source_sha256']=hashlib.sha256((ROOT/'source/render_preview.py').read_bytes()).hexdigest()
    report['scope']='Fresh STL rebuild, saved STL/scene mesh identity, source-created scene state, framing and existing preview hashes; does not repeat rendering or prove photographic accuracy'
    ok = report['rebuilt_stl_bytes_identical'] and scene_matches and report['print_object_transform_is_identity'] and report['manifest_scene_hash_matches'] and report['manifest_stl_hash_matches'] and all(preview_hashes.values()) and all(v['entire_print_mesh_fits_frame'] or v['detail_crop_intended'] for v in framing) and source_state_match
    report['pass']=bool(ok)
    (ROOT/'qa/reproducibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
    if not ok:
        raise SystemExit(1)


if __name__=='__main__':
    main()
