"""Rebuild STL and verify saved scene/preview identity without re-rendering.

Run with Python supporting the package requirements and Blender's bpy module:
python -B qa/verify_reproducibility.py --version v4 --json qa/reproducibility.json
Use --stl-only for a separate mesh-only rebuild, without importing bpy.
"""
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def triangle_key(points):
    p=[struct.pack('<3f',*v) for v in points]
    return min(b''.join(p[k:]+p[:k]) for k in range(3))


def stl_triangles(path):
    data=path.read_bytes();n,=struct.unpack_from('<I',data,80)
    if len(data)!=84+50*n:raise ValueError('Invalid binary STL record count')
    result=Counter()
    for k in range(n):
        p=struct.unpack_from('<9f',data,84+50*k+12)
        result[triangle_key([p[:3],p[3:6],p[6:]])]+=1
    return result


def scene_state(scene,obj):
    def vec(x):return [round(float(v),6) for v in x]
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


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version',default='v4');ap.add_argument('--json',type=Path,required=True)
    ap.add_argument('--stl-only',action='store_true');a=ap.parse_args()
    if not a.version.isalnum():ap.error('Version must contain only letters and digits')
    stl=ROOT/'models'/a.version/'model.stl';generator=ROOT/'source/build_model.py';params=ROOT/'parameters.json'
    original=stl.read_bytes();initial={'stl':digest(stl),'source':digest(generator),'parameters':digest(params)}
    qa_root=(ROOT/'qa').resolve()
    # Named temporary rebuilds are created and removed entirely inside qa/.
    with tempfile.TemporaryDirectory(prefix='xizi-rebuild-',dir=qa_root) as temporary:
        temp=Path(temporary).resolve()
        if not temp.is_relative_to(qa_root):raise ValueError('Temporary rebuild escaped qa directory')
        run=subprocess.run([sys.executable,'-B',str(generator),'--output-dir',str(temp)],capture_output=True,text=True,encoding='utf8')
        if run.returncode:raise RuntimeError('Fresh generation failed: '+run.stderr)
        rebuilt=(temp/'model.stl').read_bytes();build=json.loads((temp/'build-report.json').read_text(encoding='utf8'))
    r={'scope':'Fresh generator execution and exact binary STL comparison. No render, slicing or physical print.',
        'model_version':a.version,'stl_sha256':initial['stl'],'source_sha256':initial['source'],'parameters_sha256':initial['parameters'],
        'rebuild_exit_status':run.returncode,'rebuilt_stl_sha256':hashlib.sha256(rebuilt).hexdigest(),
        'rebuilt_stl_bytes_identical':original==rebuilt,'fresh_build_report':build,
        'original_stl_and_source_and_parameters_unchanged':initial=={'stl':digest(stl),'source':digest(generator),'parameters':digest(params)},
        'rebuild_report_source_bindings_match':build['source_sha256']==initial['source'] and build['parameters_sha256']==initial['parameters'],
        'script_sha256':digest(Path(__file__)),'no_slicer_or_physical_print':True}
    passed=r['rebuilt_stl_bytes_identical'] and r['original_stl_and_source_and_parameters_unchanged'] and r['rebuild_report_source_bindings_match']
    if not a.stl_only:
        import bpy
        from mathutils import Vector
        from bpy_extras.object_utils import world_to_camera_view
        blend=ROOT/'models'/a.version/'scene.blend';preview_root=ROOT/'previews'/a.version
        manifest_path=preview_root/'render-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf8'))
        bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False)
        obj=bpy.data.objects.get('Xizi_print_mesh_mm')
        if obj is None or obj.type!='MESH':raise ValueError('Expected Xizi_print_mesh_mm absent from saved scene')
        mesh=obj.data;mesh.calc_loop_triangles()
        faces=Counter(triangle_key([obj.matrix_world@mesh.vertices[i].co for i in face.vertices]) for face in mesh.loop_triangles)
        scene=bpy.context.scene;saved_state=scene_state(scene,obj)
        preview_hashes={v['name']:digest(preview_root/(v['name']+'.png'))==v['png_sha256'] for v in manifest['views']}
        framing=[]
        for view in manifest['views']:
            scene.camera.location=view['position']
            scene.camera.rotation_euler=(Vector(view['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler()
            scene.camera.data.ortho_scale=view['ortho_scale'];bpy.context.view_layer.update()
            points=[world_to_camera_view(scene,scene.camera,obj.matrix_world@p.co) for p in mesh.vertices]
            bounds=[[min(p[k] for p in points),max(p[k] for p in points)] for k in (0,1)]
            framing.append({'view':view['name'],'normalized_projected_xy_bounds':bounds,
                'entire_print_mesh_fits_frame':all(lo>=0 and hi<=1 for lo,hi in bounds)})
        scene_result={
            'blender_version':bpy.app.version_string,'scene_sha256':digest(blend),'preview_manifest_sha256':digest(manifest_path),
            'saved_blend_oriented_triangle_multiset_equals_stl_binary32':faces==stl_triangles(stl),
            'scene_triangles':sum(faces.values()),
            'print_object_transform_is_identity':all(abs(obj.matrix_world[i][j]-(1 if i==j else 0))<1e-12 for i in range(4) for j in range(4)),
            'scene_uses_millimetre_units':scene.unit_settings.system=='METRIC' and scene.unit_settings.length_unit=='MILLIMETERS' and abs(scene.unit_settings.scale_length-.001)<1e-12,
            'render_ground_separate_from_print_object':bpy.data.objects.get('RenderGround_NOT_STL') is not None,
            'image_datablocks':[im.name for im in bpy.data.images],
            'manifest_stl_hash_matches':manifest['stl_sha256']==initial['stl'],
            'manifest_scene_hash_matches':manifest['scene_sha256']==digest(blend),
            'preview_hashes':preview_hashes,'camera_framing':framing,
            'saved_object_stl_hash_matches':obj.get('STL_SHA256')==initial['stl'],
        }
        spec=importlib.util.spec_from_file_location('xizi_render_source',ROOT/'source/render_preview.py')
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        fresh_scene,fresh_obj=source.create_scene()
        first=manifest['views'][0];fresh_scene.camera.location=first['position'];source.aim(fresh_scene.camera,first['target']);fresh_scene.camera.data.ortho_scale=first['ortho_scale']
        scene_result['source_create_scene_state_matches_saved_scene']=scene_state(fresh_scene,fresh_obj)==saved_state
        scene_result['render_source_sha256']=digest(ROOT/'source/render_preview.py')
        scene_result['scope']='Saved scene triangles, units, render settings/materials/lights/camera, source create_scene state, existing preview hashes and whole-mesh framing. No rendering repeated.'
        r['scene_and_previews']=scene_result
        passed=passed and all(scene_result[k] for k in ['saved_blend_oriented_triangle_multiset_equals_stl_binary32',
            'print_object_transform_is_identity','scene_uses_millimetre_units','render_ground_separate_from_print_object',
            'manifest_stl_hash_matches','manifest_scene_hash_matches','saved_object_stl_hash_matches','source_create_scene_state_matches_saved_scene'])
        passed=passed and not scene_result['image_datablocks'] and all(preview_hashes.values()) and len(preview_hashes)==8 and all(v['entire_print_mesh_fits_frame'] for v in framing)
    r['pass']=bool(passed);a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print(json.dumps(r,indent=2));raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()
