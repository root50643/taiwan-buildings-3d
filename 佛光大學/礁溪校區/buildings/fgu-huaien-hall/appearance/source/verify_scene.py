"""Run with Blender opening the delivered scene; exact geometry + edit/reopen QA.
blender -b appearance/scene.blend --python appearance/source/verify_scene.py -- --out appearance
"""
import bpy,sys,argparse,json,tempfile
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);root=a.out.resolve();(root/'qa').mkdir(parents=True,exist_ok=True)
d=np.load(root/'mesh-data.npz');info=json.loads((root/'face-materials.json').read_text())
def check():
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1;o=meshes[0];m=o.data
 v=np.array([tuple(x.co) for x in m.vertices],dtype=np.float32);f=np.array([tuple(p.vertices) for p in m.polygons],dtype=np.int32);mi=np.array([p.material_index for p in m.polygons]);assert np.array_equal(v,d['vertices']);assert np.array_equal(f,d['faces']);assert np.array_equal(mi,d['materials']);assert len(m.materials)==4;assert not o.modifiers;assert not any(im.source!='VIEWER' or im.packed_file for im in bpy.data.images)
 assert [x.value for x in m.attributes['original_stl_face_id'].data]==list(range(len(f)));assert bpy.context.scene.render.filepath.startswith('//')
 for sc in bpy.data.screens:
  for area in sc.areas:
   for sp in area.spaces:
    if sp.type=='FILE_BROWSER' and sp.params:assert sp.params.directory==b'//'
 return o,{'blender_version':bpy.app.version_string,'mesh_objects':1,'vertices':len(v),'triangles':len(f),'vertices_float32_exact':True,'triangle_order_and_winding_exact':True,'face_material_indices_exact':True,'original_face_id_attribute_exact':True,'materials':4,'modifiers':0,'external_or_packed_images':0,'relative_render_and_browser_paths':True}
o,qa=check();old=o.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:]
with tempfile.TemporaryDirectory() as td:
 m=o.data.materials[1];color=list(old);color[0]=max(0,color[0]-.0125);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;temp=Path(td)/'edit.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp));bpy.ops.wm.open_mainfile(filepath=str(temp));o,q2=check();now=o.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:];assert abs(now[0]-color[0])<1e-7;qa['edit_save_reopen']={**q2,'material_edit_persisted':True}
bpy.ops.wm.open_mainfile(filepath=str(root/'scene.blend'));o,_=check();assert abs(o.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[0]-old[0])<1e-7
(root/'qa'/'blend-edit-reopen.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
