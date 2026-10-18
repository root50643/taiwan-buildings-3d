"""Editable scene and actual-STL inspection views for CSU 03 A/B/C.

Run: blender -b --python source/render_preview.py
or:  python source/render_preview.py  (with the bpy Python module installed)

Geometry comes only from parts/body.stl and parts/roof.stl. Materials are
display aids on existing triangles, not additional geometry or print colors.
No photos, textures, vegetation, speculative volumes, modifiers, or bevels.
The original STL triangle-coordinate identity is checked after Blender import.
"""
from pathlib import Path
import hashlib
import json
import struct

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'models/v2'
OUT = ROOT / 'previews/v2'
TOL = 0.0001


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def triangle_digest(triangles):
    # Order-independent triangle geometry, but no approximate geometric edits.
    ordered = sorted(tuple(sorted(tuple(float(c) for c in v) for v in tri))
                     for tri in triangles)
    return hashlib.sha256(json.dumps(ordered, separators=(',', ':')).encode()).hexdigest()


def stl_triangles(path):
    raw = path.read_bytes()
    n = struct.unpack_from('<I', raw, 80)[0]
    assert len(raw) == 84 + 50*n, 'Expected generated binary STL'
    result = []
    for i in range(n):
        coords = struct.unpack_from('<9f', raw, 84 + 50*i + 12)
        result.append([coords[j:j+3] for j in (0, 3, 6)])
    return result


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = 0.78
    return mat


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def in_cut(face, obj, cut):
    cx, cy = cut['center_xy']
    w, d, h = cut['extents']
    z = cut['bottom']
    lo = (cx-w/2-TOL, cy-d/2-TOL, z-TOL)
    hi = (cx+w/2+TOL, cy+d/2+TOL, z+h+TOL)
    return all(all(lo[k] <= obj.data.vertices[i].co[k] <= hi[k] for k in range(3))
               for i in face.vertices)


def import_part(name, record, mats, cuts):
    path = MODEL / record['path']
    assert sha(path) == record['sha256'], 'STL changed since build report: ' + name
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = 'PrintPart_' + name
    obj.data.name = name + '_unaltered_STL_triangles_mm'
    for mat in mats:
        obj.data.materials.append(mat)
    original = stl_triangles(path)
    imported = [[tuple(obj.data.vertices[i].co) for i in p.vertices] for p in obj.data.polygons]
    assert len(original) == len(imported) == record['triangles']
    original_digest = triangle_digest(original)
    imported_digest = triangle_digest(imported)
    assert original_digest == imported_digest, 'Imported geometry differs: ' + name
    obj['source_relative_path'] = record['path']
    obj['source_STL_SHA256'] = sha(path)
    obj['triangle_coordinate_digest'] = original_digest
    obj['print_part'] = True
    obj['units'] = 'mm'
    obj['materials'] = 'Display colors only; material assignment does not modify the STL geometry'
    obj['scope'] = 'One model set: 03 A/B/C, main body plus separate central roof; adjacent 04 excluded'
    counts = [0] * len(mats)
    for face in obj.data.polygons:
        coords = [obj.data.vertices[i].co for i in face.vertices]
        center = sum(coords, Vector()) / len(coords)
        idx = 0
        if name == 'roof':
            idx = 5 if face.normal.z > 0.99 and center.z > 10.9 else 4
        elif max(v.z for v in coords) <= 3 + TOL:
            idx = 3
        elif face.normal.z > 0.99 and abs(center.z-67) < TOL and abs(center.x) > 26:
            idx = 2
        elif any(in_cut(face, obj, cut) for cut in cuts):
            idx = 1
        face.material_index = idx
        face.use_smooth = False
        counts[idx] += 1
    return obj, {'source_path':record['path'], 'stl_sha256':sha(path),
                 'triangles':len(original), 'triangle_coordinate_sha256':original_digest,
                 'blender_import_geometry_identical':True,
                 'material_triangle_counts':dict(zip([m.name for m in mats], counts))}


def create_scene(report):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = 'CSU_03_ABC_one_set_two_print_parts'
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'MILLIMETERS'
    scene.unit_settings.scale_length = 0.001
    scene['coordinate_frame'] = 'Local x left to right facing entrance; -y front; +z up. No north/orientation claim.'
    scene['scale_status'] = 'Relative photograph estimates; not survey scale or a classroom chart measurement.'
    scene['assembly'] = 'Frame 1: body (0,0,0), roof (0,0,85) mm. Frame 2: roof lifted 30 mm for assembly illustration.'
    scene['print_route'] = 'Two separate flat-bottom STLs; one building model set. Assembly STL is display-only.'
    scene['display'] = 'Existing triangle materials only. Pale concrete, subtle recesses, muted terrace deck, orange roof sides and gray flat top.'
    mats = [material('Pale concrete - display only', (0.72, 0.71, 0.66)),
            material('Shallow recess - display only', (0.43, 0.47, 0.46)),
            material('Terrace deck tint - no vegetation', (0.47, 0.53, 0.44)),
            material('Integral 3 mm plinth', (0.60, 0.63, 0.62)),
            material('Central roof orange sides - display only', (0.72, 0.28, 0.105)),
            material('Central roof flat gray top - display only', (0.56, 0.58, 0.55))]
    cuts = [f for f in report['feature_ledger'] if f['kind'] == 'cut']
    body, body_info = import_part('body', report['parts']['body'], mats, cuts)
    roof, roof_info = import_part('roof', report['parts']['roof'], mats, [])
    roof.location.z = 85
    roof.keyframe_insert(data_path='location', frame=1)
    roof.location.z = 115
    roof.keyframe_insert(data_path='location', frame=2)
    scene.frame_start, scene.frame_end = 1, 2
    scene.frame_set(1)
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.15))
    ground = bpy.context.object
    ground.name = 'Studio_ground_NOT_A_PRINT_PART'
    ground['print_part'] = False
    ground['purpose'] = 'Studio render background only; not exported in any STL'
    ground.data.materials.append(material('Studio background', (0.84, 0.85, 0.83)))
    world = bpy.data.worlds.new('Soft neutral studio')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.84, 0.87, 0.89, 1)
    world.node_tree.nodes['Background'].inputs[1].default_value = 0.8
    scene.world = world
    for name, position, energy, size in [('Key', (-130,-180,260), 42000, 170),
                                          ('Fill', (160,70,180), 30000, 180),
                                          ('Rear fill', (-60,180,170), 19000, 160)]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size = energy, 'DISK', size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0,0,45))
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.seed = 0
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x, scene.render.resolution_y = 1200, 850
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium Low Contrast'
    scene.render.use_file_extension = True
    return scene, body, roof, {'body':body_info, 'roof':roof_info}


def make_cameras(scene):
    specs = [
        ('front-three-quarter', (225,-310,215), (0,-1,44), 250, 1),
        ('rear-three-quarter', (-225,310,215), (0,0,44), 250, 1),
        ('front-elevation', (0,-400,48), (0,0,48), 232, 1),
        ('rear-elevation', (0,400,48), (0,0,48), 232, 1),
        ('left-elevation', (-400,0,48), (0,0,48), 170, 1),
        ('right-elevation', (400,0,48), (0,0,48), 170, 1),
        ('top', (0,0,450), (0,0,0), 232, 1),
        ('exploded-two-parts', (225,-310,230), (0,-1,58), 260, 2),
    ]
    views = []
    for name, position, target, scale, frame in specs:
        data = bpy.data.cameras.new(name)
        camera = bpy.data.objects.new('View_' + name, data)
        scene.collection.objects.link(camera)
        data.type = 'ORTHO'
        data.lens = 50
        data.clip_end = 5000
        data.ortho_scale = scale
        camera.location = position
        aim(camera, target)
        camera['inspection_view'] = name
        camera['frame_for_roof_position'] = frame
        views.append((camera, {'name':name, 'position_mm':position, 'target_mm':target,
                               'ortho_scale_mm':scale, 'frame':frame,
                               'roof_translation_mm':[0,0,85 if frame==1 else 115]}))
    return views


def verify_framing(scene, views, objects):
    for camera, record in views:
        scene.frame_set(record['frame'])
        scene.camera = camera
        bpy.context.view_layer.update()
        projected = [world_to_camera_view(scene, camera, obj.matrix_world @ v.co)
                     for obj in objects for v in obj.data.vertices]
        factor = max(max(abs(v.x-.5), abs(v.y-.5))/.46 for v in projected)
        if factor > 1:
            camera.data.ortho_scale *= factor
            bpy.context.view_layer.update()
            projected = [world_to_camera_view(scene, camera, obj.matrix_world @ v.co)
                         for obj in objects for v in obj.data.vertices]
        lo = [min(v[i] for v in projected) for i in (0,1)]
        hi = [max(v[i] for v in projected) for i in (0,1)]
        assert all(.039 < lo[i] <= hi[i] < .961 for i in (0,1)), 'Framing failed'
        record['ortho_scale_mm'] = camera.data.ortho_scale
        record['model_projected_bounds_normalized'] = [lo, hi]
        record['geometry_in_frame'] = True


def assembly_overview():
    from PIL import Image, ImageDraw, ImageFont
    def font(size):
        for name in ['C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf']:
            if Path(name).exists():
                return ImageFont.truetype(name, size)
        return ImageFont.load_default(size=size)
    canvas = Image.new('RGB', (1800,900), '#f4f5f1')
    draw = ImageDraw.Draw(canvas)
    draw.text((60,35), 'CSU | Administration Building 03 A/B/C', font=font(36), fill='#303c3c')
    draw.text((60,88), 'One representative model set  /  Two physical print parts', font=font(24), fill='#596565')
    for x, name, title in [(40,'front-three-quarter','ASSEMBLED'),
                           (920,'exploded-two-parts','ROOF LIFTED 30 mm FOR CLARITY')]:
        image = Image.open(OUT/(name+'.png')).convert('RGB')
        image.thumbnail((840,595), Image.Resampling.LANCZOS)
        canvas.paste(image, (x+(840-image.width)//2,170))
        draw.text((x+20,140),title,font=font(21),fill='#3d4b4b')
    draw.text((60,785),'Body stays at (0, 0, 0) mm. Roof centers at (0, 0, 85) mm for assembly.',font=font(24),fill='#303c3c')
    draw.text((60,826),'Print body.stl and roof.stl flat on their original z = 0 bases. Trial place, then glue the flat joint.',font=font(22),fill='#596565')
    path = OUT/'assembly-overview.png'
    canvas.save(path)
    return {'path':path.relative_to(ROOT).as_posix(), 'png_sha256':sha(path),
            'pixels':list(canvas.size), 'kind':'Labeled composition of two actual-STL renders'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = json.loads((MODEL/'build-report.json').read_text(encoding='utf8'))
    scene, body, roof, parts = create_scene(report)
    views = make_cameras(scene)
    verify_framing(scene, views, [body, roof])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    scene.camera = views[0][0]
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    roof.select_set(True)
    bpy.context.view_layer.objects.active = body
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
    blend = MODEL / 'scene.blend'
    scene.render.filepath = '//../../previews/v2/front-three-quarter.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    manifest = {'renderer':bpy.app.version_string, 'engine':'CYCLES CPU',
                'samples':48, 'denoising':True, 'seed':0, 'threads':4,
                'pixels':[1200,850], 'units':'mm',
                'counting':'One representative 03 A/B/C building model set, two physical print parts',
                'geometry':'Unmodified imported STL triangles; only material indices and roof placement changed',
                'assembly_roof_translation_mm':[0,0,85],
                'exploded_roof_translation_mm':[0,0,115],
                'parts':parts,
                'assembly_stl_sha256':sha(MODEL/'assembly.stl'),
                'parameter_sha256':sha(ROOT/'parameters.json'),
                'build_report_sha256':sha(MODEL/'build-report.json'),
                'render_source_sha256':sha(Path(__file__)),
                'scene_path':'models/v2/scene.blend', 'scene_sha256':sha(blend),
                'ground':'Studio background plane is not part of any STL',
                'photos_or_image_textures_in_scene':False,
                'views':[]}
    for camera, record in views:
        scene.frame_set(record['frame'])
        scene.camera = camera
        path = OUT / (record['name'] + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        record['path'] = path.relative_to(ROOT).as_posix()
        record['png_sha256'] = sha(path)
        manifest['views'].append(record)
    # The saved file remains in assembled frame 1 and the front 3/4 camera.
    manifest['assembly_overview'] = assembly_overview()
    (OUT/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print('CSU 03 A/B/C: eight actual-STL views and editable two-part scene saved')


if __name__ == '__main__':
    main()
