# blender --background nqu-roundhouse-entrance-facade.blend --python verify_blend.py
import bpy, pathlib,json,numpy as np, tempfile,hashlib
root=pathlib.Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');scene=bpy.context.scene
obj=bpy.data.objects['NQU central entrance facade — unified printable mesh']
v=np.array([tuple(x.co)for x in obj.data.vertices]);f=np.array([tuple(x.vertices)for x in obj.data.polygons]);mi=np.array([x.material_index for x in obj.data.polygons])
assert np.array_equal(v,D['vertices']) and np.array_equal(f,D['faces']) and np.array_equal(mi,D['materials'])
assert all(x.render.filepath.startswith('//') for x in bpy.data.scenes)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:assert space.params.directory==b'//'
external_images=[x.name for x in bpy.data.images if x.source=='FILE' and x.filepath]
assert not external_images
parts=bpy.data.collections['EDITABLE authored components (hidden; overlaps pre-union)'];assert parts.hide_render and parts.hide_viewport
report={'blender_version':bpy.app.version_string,'final_vertices':len(v),'final_triangles':len(f),'final_materials':len(obj.data.materials),'editable_construction_objects':len(parts.objects),'construction_hidden':True,'final_mesh_matches_generated_arrays':True,'external_image_textures':external_images,'relative_output_and_browser_paths':True,'scale_length':scene.unit_settings.scale_length,'unit_system':scene.unit_settings.system}
# Exercise a real material edit, save a disposable copy, then reopen it.
original=root/'nqu-roundhouse-entrance-facade.blend';before=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='nqu-recolor-') as tmp:
 mat=bpy.data.materials['pale_trim'];test=(.14,.34,.54,1.0)
 mat.diffuse_color=test;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=test
 copy=pathlib.Path(tmp)/'recolor-test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(copy),copy=True)
 bpy.ops.wm.open_mainfile(filepath=str(copy))
 actual=list(bpy.data.materials['pale_trim'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
 assert np.allclose(actual,test,atol=1e-7)
 report['recolor_copy_saved_and_reopened']=True;report['recolor_test_material']='pale_trim'
assert hashlib.sha256(original.read_bytes()).hexdigest()==before
report['original_blend_unchanged_by_edit_test']=True
(root/'qa'/'blend-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
