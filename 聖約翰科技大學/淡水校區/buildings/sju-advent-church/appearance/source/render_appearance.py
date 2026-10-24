"""Render unchanged original triangles + finite source-backed material assignments.
Run: blender -b -t 4 -P appearance/source/render_appearance.py
"""
import bpy,json,sys,hashlib,struct
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from geometry_io import read_original,triangle_coordinate_sha
OUT=HERE.parent;PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
verts,faces=read_original(OUT.parent/'model.stl')
ann=json.loads((OUT/'face-materials.json').read_text());manifest=json.loads((OUT/'material-manifest.json').read_text())
assert ann['triangle_coordinate_sha256']==triangle_coordinate_sha(verts,faces)

def strip_png(path):
    raw=path.read_bytes();out=raw[:8];i=8
    while i<len(raw):
        n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8]
        if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out+=raw[i:i+12+n]
        i+=12+n
    path.write_bytes(out)

def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for datablock in list(bpy.data.materials):bpy.data.materials.remove(datablock)
mesh=bpy.data.meshes.new('Original STL triangles - no remesh or modifiers');mesh.from_pydata(verts,[],faces);mesh.update()
model=bpy.data.objects.new('SJU_Advent_Church_Original_Faces',mesh);bpy.context.collection.objects.link(model)
bpy.context.view_layer.objects.active=model;model.select_set(True)
for item in manifest['materials']:
    m=bpy.data.materials.new(item['id']);rgb=[linear(v/255) for v in bytes.fromhex(item['hex'][1:])]
    m.diffuse_color=(*rgb,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    m['display_srgb_hex']=item['hex'];m['evidence_status']=item['evidence_status'];mesh.materials.append(m)
original_ids=mesh.attributes.new('original_stl_face_id','INT','FACE')
region_ids=mesh.attributes.new('evidence_region_id','INT','FACE');region_keys=list(manifest['regions'])
for i,p in enumerate(mesh.polygons):
    p.material_index=ann['material_indices'][i];p.use_smooth=False;original_ids.data[i].value=i;region_ids.data[i].value=region_keys.index(ann['region_by_face'][i])
model['original_stl_sha256']=ann['source_stl_sha256'];model['triangle_coordinate_sha256']=ann['triangle_coordinate_sha256'];model['geometry_unchanged']=True
model['source_scope']='Circa-2014 main church; post-2003 entry; not a measured survey or current 2026 paint'
model['appearance_scope']='Bounded original-face annotation. Unknown neutral includes unresolved cross, hidden faces, crown top and unregistered rear door.'
model['evidence_region_keys']=json.dumps(region_keys)
model['units']='mm';model['real_print_tested']=False
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.25;scene.display.shading.curvature_valley_factor=1.1
scene.display.shading.show_specular_highlight=False;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if False else 'None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Appearance_preview_camera';scene.camera=cam;cam.data.type='ORTHO'
target_z=41.54
views=[('front',(-100,-280,105),(0,0,target_z)),('rear',(125,280,105),(0,0,target_z)),('side-minus-x',(-280,-40,100),(0,0,target_z)),('side-plus-x',(280,60,100),(0,0,target_z)),('front-low',(-70,-300,60),(0,0,target_z)),('rear-low',(140,280,60),(0,0,target_z)),('top',(0,0,300),(0,0,0))]
def set_view(loc,aim):
    cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    inv=cam.rotation_euler.to_matrix().transposed();pv=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
    width=max(v.x for v in pv)-min(v.x for v in pv);height=max(v.y for v in pv)-min(v.y for v in pv)
    cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.12
for name,loc,aim in views:
    set_view(loc,aim);scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True);strip_png(PREV/(name+'.png'))
set_view(views[0][1],views[0][2]);scene.render.filepath='//previews/front.png'
bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
actual_vertices=[tuple(v.co) for v in mesh.vertices];actual_faces=[tuple(p.vertices) for p in mesh.polygons]
assert triangle_coordinate_sha(actual_vertices,actual_faces)==ann['triangle_coordinate_sha256']
assert [p.material_index for p in mesh.polygons]==ann['material_indices']
report={'source':'Original STL triangles with per-face material assignments; no proxy meshes','blender_version':bpy.app.version_string,'original_stl_sha256':ann['source_stl_sha256'],'scene_triangle_coordinate_sha256':triangle_coordinate_sha(actual_vertices,actual_faces),'scene_triangle_count':len(mesh.polygons),'scene_vertex_count':len(mesh.vertices),'geometry_exact_float32':True,'material_assignments_exact':True,'mesh_object_count':1,'external_image_paths':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath],'previews':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(PREV.glob('*.png'))}}
(OUT/'render-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
