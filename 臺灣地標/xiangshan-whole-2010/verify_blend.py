# blender --background xiangshan-whole-2010.blend --python verify_blend.py
import bpy, pathlib,json,hashlib,numpy as np
deliverable=pathlib.Path(bpy.data.filepath);root=deliverable.parent
original_sha256=hashlib.sha256(deliverable.read_bytes()).hexdigest()
(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');scene=bpy.context.scene
final_id_name='Xiangshan — unified printable material mesh'.encode()[:63].decode('utf-8',errors='ignore')
obj=bpy.data.objects[final_id_name]
v=np.array([tuple(x.co)for x in obj.data.vertices]);f=np.array([tuple(x.vertices)for x in obj.data.polygons]);mi=np.array([x.material_index for x in obj.data.polygons])
assert np.array_equal(v,D['vertices']) and np.array_equal(f,D['faces']) and np.array_equal(mi,D['materials'])
assert all(x.render.filepath.startswith('//') for x in bpy.data.scenes)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:assert space.params.directory==b'//'
external_images=[x.name for x in bpy.data.images if x.source=='FILE' and x.filepath]
assert not external_images
assert not bpy.data.libraries, 'Linked libraries are not self-contained'
assert not bpy.data.sounds and not bpy.data.movieclips, 'Unexpected external media'
assert not bpy.data.texts, 'No embedded text/scripts expected in this native model'
assert all(not x.filepath or x.filepath=='<builtin>' for x in bpy.data.fonts), 'Unexpected external font'
assert not any(x.packed_file for x in bpy.data.images), 'No packed reference pixels expected'
parts=bpy.data.collections['EDITABLE authored components (hidden; overlaps pre-union)'];assert parts.hide_render and parts.hide_viewport
source_parts=json.loads((root/'construction-parts.json').read_text());source_info=json.loads((root/'editable-parts.json').read_text());assert len(parts.objects)==len(source_parts)==len(source_info['features'])
assert scene.unit_settings.system=='METRIC' and abs(scene.unit_settings.scale_length-.001)<1e-9
assert np.array_equal(np.asarray(obj.matrix_world),np.eye(4))
for palette,native_mat in zip(source_info['palette'],obj.data.materials):
 h=palette['hex'].lstrip('#');srgb=[int(h[i:i+2],16)/255 for i in (0,2,4)];linear=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in srgb]+[1.0]
 assert native_mat.name==palette['id']
 assert np.allclose(native_mat.diffuse_color,linear,atol=1e-7,rtol=0)
 assert np.allclose(native_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,linear,atol=1e-7,rtol=0)
expected_names=[x['name'].encode()[:63].decode('utf-8','ignore') for x in source_parts]
assert len(set(expected_names))==len(expected_names),'Authored component names collide after Blender ID truncation'
for authored,metadata in zip(source_parts,source_info['features']):
 expected_name=authored['name'].encode()[:63].decode('utf-8','ignore');native=parts.objects[expected_name];assert native.name==expected_name
 pv=np.array([tuple(x.co)for x in native.data.vertices]);pf=np.array([tuple(x.vertices)for x in native.data.polygons]);assert np.array_equal(pv,np.asarray(authored['vertices'],np.float32)) and np.array_equal(pf,np.asarray(authored['faces']))
 assert len(native.data.materials)==1 and native.data.materials[0].name==source_info['palette'][authored['material']]['id']
 assert native['evidence']==metadata['evidence'] and native.hide_render
 assert native.name==metadata['name'].encode()[:63].decode('utf-8','ignore')
 assert np.array_equal(np.asarray(native.matrix_world),np.eye(4))

report={'blender_version':bpy.app.version_string,'final_vertices':len(v),'final_triangles':len(f),'final_materials':len(obj.data.materials),'editable_construction_objects':len(parts.objects),'construction_hidden':True,'all_editable_components_match_public_geometry_material_and_evidence':True,'final_mesh_matches_generated_arrays':True,'native_palette_diffuse_and_shader_match_public_srgb':True,'native_geometry_transforms_identity':True,'external_image_textures':external_images,'linked_libraries':0,'embedded_text_blocks':0,'packed_image_files':0,'external_sounds_movieclips':0,'relative_output_and_browser_paths':True,'scale_length':scene.unit_settings.scale_length,'unit_system':scene.unit_settings.system}
(root/'qa'/'blend-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

# Render the actual reopened native scene and compare with its corresponding preview.
import tempfile,struct,hashlib
with tempfile.TemporaryDirectory(prefix='native-render-check-') as tmp:
 render=pathlib.Path(tmp)/'front.png';scene.render.filepath=str(render);bpy.ops.render.render(write_still=True)
 raw=render.read_bytes();clean=raw[:8];at=8
 while at<len(raw):
  n=struct.unpack('>I',raw[at:at+4])[0];tag=raw[at+4:at+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):clean+=raw[at:at+n+12]
  at+=n+12
 expected=(root/'previews/front.png').read_bytes();assert clean==expected
 report={'actual_saved_blend_reopened_and_rendered':True,'reference_preview':'previews/front.png','png_bytes_identical_after_metadata_normalization':True,'sha256':hashlib.sha256(clean).hexdigest(),'deliverable_modified':False}
 (root/'qa/saved-scene-render-validation.json').write_text(json.dumps(report,indent=2)+'\n')
scene.render.filepath='//previews/front.png'

# Exercise editable native geometry AND material persistence, without altering the deliverable.
import tempfile,os
final_name=obj.name
vertex_before=tuple(obj.data.vertices[0].co);obj.data.vertices[0].co.x+=0.125
vertex_after=tuple(obj.data.vertices[0].co)
material_name=obj.data.materials[0].name
mat=obj.data.materials[0];color_before=tuple(mat.diffuse_color);color_after=(0.12,0.34,0.56,1.0)
mat.diffuse_color=color_after;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color_after
probe_index=next(i for i,x in enumerate(source_parts)if x['name']=='Administration whole curved concrete roof shell');part=parts.objects[expected_names[probe_index]];part_name=part.name;part_before=tuple(part.data.vertices[0].co);part.data.vertices[0].co.z+=0.2;part_after=tuple(part.data.vertices[0].co)
part_location_before=tuple(part.location);part.location.x+=0.35;part_location_after=tuple(part.location)
part_mat=part.data.materials[0].copy();part_mat.name='Temporary editability colour probe';part.data.materials[0]=part_mat
part_color=(0.64,0.22,0.09,1.0);part_mat.diffuse_color=part_color;part_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=part_color
with tempfile.TemporaryDirectory(prefix='xiangshan-native-edit-') as tmp:
 test=pathlib.Path(tmp)/'native-edit-probe.blend';bpy.ops.wm.save_as_mainfile(filepath=str(test));bpy.ops.wm.open_mainfile(filepath=str(test))
 reopened=bpy.data.objects[final_name];assert tuple(reopened.data.vertices[0].co)==vertex_after
 assert all(abs(x-y)<1e-6 for x,y in zip(bpy.data.materials[material_name].diffuse_color,color_after))
 assert all(abs(x-y)<1e-6 for x,y in zip(bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,color_after))
 reopened_part=bpy.data.objects[part_name];assert tuple(reopened_part.data.vertices[0].co)==part_after
 assert tuple(reopened_part.location)==part_location_after
 assert all(abs(x-y)<1e-6 for x,y in zip(reopened_part.data.materials[0].diffuse_color,part_color))
 assert all(abs(x-y)<1e-6 for x,y in zip(reopened_part.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,part_color))
 native={'native_vertex_changed_and_reopened':True,'native_material_diffuse_and_shader_changed_and_reopened':True,'construction_component_vertex_changed_and_reopened':True,'individual_component_move_and_colour_changed_and_reopened':True,'construction_location_delta_mm':0.35,'tested_building_component':part_name,'final_vertex_delta_mm':0.125,'construction_vertex_delta_mm':0.2,'deliverable_modified':False,'temporary_probe_removed':True}
assert hashlib.sha256(deliverable.read_bytes()).hexdigest()==original_sha256
native['original_deliverable_sha256_before_and_after']=original_sha256
(root/'qa/native-edit-validation.json').write_text(json.dumps(native,indent=2)+'\n');print(json.dumps(native,indent=2))
