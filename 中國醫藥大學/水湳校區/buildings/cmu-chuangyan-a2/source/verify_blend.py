"""Open the saved Blend and verify geometry, face materials, and real edit/save/reopen."""
import bpy,numpy as np,json,hashlib,tempfile,argparse,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out or Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');obj=next(o for o in bpy.data.objects if o.type=='MESH');meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==1
v=np.array([tuple(x.co)for x in obj.data.vertices]);f=np.array([tuple(x.vertices)for x in obj.data.polygons]);m=np.array([x.material_index for x in obj.data.polygons]);assert np.array_equal(v,D['vertices'])and np.array_equal(f,D['faces'])and np.array_equal(m,D['materials'])
idx=np.array([x.value for x in obj.data.attributes['original_stl_triangle_index'].data]);assert np.array_equal(idx,np.arange(len(f)))
assert not obj.modifiers;assert not any(o.type=='MESH'and(o.hide_render or o.hide_viewport)for o in bpy.data.objects)
assert all(s.render.filepath=='//previews/front.png'for s in bpy.data.scenes)
external=[x.name for x in bpy.data.images if x.source=='FILE'and x.filepath];assert not external
material_count=len(obj.data.materials)
orig=root/'cmu-chuangyan-a2.blend';before=hashlib.sha256(orig.read_bytes()).hexdigest();matname=next(m.name for m in bpy.data.materials if m.name.startswith('C01 '));test=(.14,.34,.54,1)
with tempfile.TemporaryDirectory(prefix='material-edit-')as tmp:
 mat=bpy.data.materials[matname];mat.diffuse_color=test;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=test
 oldx=float(obj.data.vertices[0].co.x);obj.data.vertices[0].co.x=oldx+0.25
 copy=Path(tmp)/'edit-test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(copy),copy=True);bpy.ops.wm.open_mainfile(filepath=str(copy));mat=bpy.data.materials[matname]
 edited=next(o for o in bpy.data.objects if o.type=='MESH');assert abs(edited.data.vertices[0].co.x-(oldx+.25))<1e-5
 assert np.allclose(mat.diffuse_color,test,atol=1e-7)and np.allclose(mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,test,atol=1e-7)
assert hashlib.sha256(orig.read_bytes()).hexdigest()==before
report={'blender_version':bpy.app.version_string,'mesh_objects':1,'vertices':len(v),'triangles':len(f),'materials':material_count,'coordinates_face_order_and_material_assignments_exact':True,'original_stl_triangle_index_attribute_exact':True,'modifiers':0,'hidden_geometry_objects':0,'external_images':external,'real_material_and_vertex_edit_saved_reopened':True,'edited_material':matname,'original_blend_unchanged_after_edit_test':True,'unit':'millimeters','scale_length':.001}
(root/'qa'/'blend-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
