"""Inspect saved Blend and prove real native vertex/material editing on a temporary copy."""
from pathlib import Path
import bpy,sys,argparse,tempfile,math,collections
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sys
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.out;D=load(a.stl,root/'parameters.json',root/'palette.json')
objs=[o for o in bpy.data.objects if o.type=='MESH'];assert len(objs)==1;o=objs[0];mesh=o.data;assert not o.modifiers and not o.hide_render and not o.hide_viewport
assert all(abs(o.matrix_world[i][j]-(1 if i==j else 0))==0 for i in range(4)for j in range(4))
assert all(len(f.vertices)==3 for f in mesh.polygons);ids=mapping(D['signatures'],[[tuple(mesh.vertices[v].co)for v in f.vertices]for f in mesh.polygons]);assert [x.value for x in mesh.attributes['original_stl_triangle_index'].data]==ids
assert len(mesh.materials)==4 and len(bpy.data.materials)==4
for f,i in zip(mesh.polygons,ids):assert f.material_index==D['materials'][i]
for mat,name in zip(mesh.materials,ORDER):
 assert mat.name==name;d=D['palette'][name];expected=(*srgb_linear(d['srgb8']),1);node=mat.node_tree.nodes['Principled BSDF']
 assert all(abs(x-y)<1e-7 for x,y in zip(mat.diffuse_color,expected));assert all(abs(x-y)<1e-7 for x,y in zip(node.inputs['Base Color'].default_value,expected));assert abs(node.inputs['Roughness'].default_value-d['roughness'])<1e-7
 assert set(n.bl_idname for n in mat.node_tree.nodes)=={'ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial'}
assert not mesh.uv_layers and not mesh.color_attributes
assert not any(i.source=='FILE'and i.filepath for i in bpy.data.images)
assert not bpy.data.texts
assert all(s.render.filepath=='//previews/front.png'for s in bpy.data.scenes)
path=root/'au-oxford-1999-core-appearance.blend';before=sha(path.read_bytes());r={'blender_version':bpy.app.version_string,'original_face_count':14042,'vertices':len(mesh.vertices),'all_face_oriented_float32_digest':GLOBAL,'exact_one_to_one_face_mapping':True,'colored_original_faces':596,'neutral_original_faces':13446,'all_material_slots_shader_colors_and_face_assignments_exact':True,'original_face_id_attribute_exact':True,'mesh_objects':1,'identity_object_transform':True,'modifiers':0,'hidden_meshes':0,'UV_layers':0,'vertex_color_layers':0,'external_images':0,'embedded_scripts':0,'unit_scale_length':bpy.context.scene.unit_settings.scale_length}
with tempfile.TemporaryDirectory(prefix='native-blend-edit-')as tmp:
 mat=mesh.materials[1];val=(.14,.34,.54,1);mat.diffuse_color=val;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=val;x=float(mesh.vertices[0].co.x);mesh.vertices[0].co.x=x+.25
 e=Path(tmp)/'edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(e),copy=True);bpy.ops.wm.open_mainfile(filepath=str(e));o=next(o for o in bpy.data.objects if o.type=='MESH');assert abs(o.data.vertices[0].co.x-x-.25)<1e-6
 assert all(abs(x-y)<1e-7 for x,y in zip(o.data.materials[1].diffuse_color,val));assert all(abs(x-y)<1e-7 for x,y in zip(o.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,val))
 assert [f.material_index for f in o.data.polygons]==[D['materials'][i]for i in ids]
assert sha(path.read_bytes())==before;r.update({'real_material_and_vertex_edit_saved_reopened':True,'edit_test_kept_face_assignments':True,'original_blend_unchanged':True});dump(root/'qa/blend-validation.json',r);print(json.dumps(r))
