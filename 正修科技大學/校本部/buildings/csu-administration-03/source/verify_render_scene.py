"""Reopen the delivered v2 scene; verify geometry identity and self-contained data.

Run with the same Blender/bpy runtime as render_preview.py. Evidence uses only
package-relative paths. The current .blend filename is the scene itself, not an
external dependency, and is deliberately omitted from the report.
"""
from pathlib import Path
import hashlib
import json

import bpy
import render_preview as renderer

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'models/v2'
OUT = ROOT/'previews/v2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blend = MODEL/'scene.blend'
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene = bpy.context.scene
    manifest = json.loads((OUT/'render-manifest.json').read_text(encoding='utf8'))
    checks = {'scene_path':'models/v2/scene.blend', 'scene_sha256':sha(blend),
              'renderer':bpy.app.version_string, 'checks':{}, 'parts':{}}
    check = checks['checks']
    check['scene_hash_matches_render_manifest'] = sha(blend) == manifest['scene_sha256']
    parts = [obj for obj in scene.objects if obj.type=='MESH' and obj.get('print_part')]
    check['exactly_two_print_meshes'] = len(parts)==2
    check['exactly_one_excluded_studio_ground'] = len([obj for obj in scene.objects
        if obj.type=='MESH' and not obj.get('print_part')]) == 1
    for obj in parts:
        name = obj.name.removeprefix('PrintPart_')
        triangles = [[tuple(obj.data.vertices[i].co) for i in p.vertices]
                     for p in obj.data.polygons]
        digest = renderer.triangle_digest(triangles)
        expected = manifest['parts'][name]
        checks['parts'][name] = {'triangles':len(triangles),
            'triangle_coordinate_sha256':digest,
            'source_stl_sha256':sha(MODEL/expected['source_path']),
            'geometry_matches_imported_stl':digest==expected['triangle_coordinate_sha256'],
            'source_stl_matches_manifest':sha(MODEL/expected['source_path'])==expected['stl_sha256'],
            'modifiers':len(obj.modifiers), 'scale':list(obj.scale),
            'translation_mm':list(obj.location)}
        check[name+'_geometry_identity'] = (digest==expected['triangle_coordinate_sha256']
            and sha(MODEL/expected['source_path'])==expected['stl_sha256']
            and len(obj.modifiers)==0 and list(obj.scale)==[1,1,1])
    check['saved_in_assembled_frame_one'] = scene.frame_current==1
    check['body_at_original_origin'] = list(bpy.data.objects['PrintPart_body'].location)==[0,0,0]
    check['roof_at_assembly_translation'] = list(bpy.data.objects['PrintPart_roof'].location)==[0,0,85]
    check['front_three_quarter_default_camera'] = scene.camera.name=='View_front-three-quarter'
    check['eight_named_inspection_cameras'] = len([obj for obj in scene.objects if obj.type=='CAMERA'])==8
    render_path = scene.render.filepath.replace('\\', '/')
    checks['render_output_relative_path'] = render_path
    check['render_output_is_package_relative'] = render_path=='//../../previews/v2/front-three-quarter.png'
    check['no_linked_libraries'] = len(bpy.data.libraries)==0
    checks['image_datablocks'] = len(bpy.data.images)
    check['no_images_or_packed_photos'] = len(bpy.data.images)==0
    paths = list(bpy.utils.blend_paths())
    checks['external_dependency_count'] = len(paths)
    check['no_external_dependency_paths'] = len(paths)==0
    check['all_rendered_views_in_frame'] = all(v['geometry_in_frame'] for v in manifest['views'])
    check['renderer_source_matches_manifest'] = sha(ROOT/'source/render_preview.py')==manifest['render_source_sha256']
    for view in manifest['views']:
        check['png_hash_'+view['name']] = sha(ROOT/view['path'])==view['png_sha256']
    overview = manifest['assembly_overview']
    check['assembly_overview_hash'] = sha(ROOT/overview['path'])==overview['png_sha256']
    checks['passed'] = all(check.values())
    (OUT/'scene-check.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
    print(json.dumps(checks,indent=2))
    assert checks['passed'], 'Scene verification failed; inspect scene-check.json'


if __name__=='__main__':
    main()
