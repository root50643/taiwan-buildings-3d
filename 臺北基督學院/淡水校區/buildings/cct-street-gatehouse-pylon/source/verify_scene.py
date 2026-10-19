"""Read-only reopen of the generated scene; arrays, transforms and material checks.
Run with Blender -b --python source/verify_scene.py. Does not save the scene.
"""
from pathlib import Path
import collections,hashlib,json
import bpy
import numpy as np
R=Path(__file__).resolve().parents[1]
def main():
 d=json.loads((R/'geometry.json').read_text());before=hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'));scene=bpy.context.scene
 objects={o.name:o for o in scene.objects if o.type=='MESH' and o.get('print_geometry',False)};assert set(objects)=={p['id'] for p in d['parts']};assert len([o for o in scene.objects if o.type=='MESH'])==5
 assert abs(scene.unit_settings.scale_length-.001)<1e-9 and scene.unit_settings.system=='METRIC';count=collections.Counter();transforms={};world_errors={}
 for p in d['parts']:
  o=objects[p['id']];v=np.array([list(v.co) for v in o.data.vertices]);f=np.array([list(x.vertices) for x in o.data.polygons]);T=np.array([list(row) for row in o.matrix_world]);expectedT=np.array(p['assembly_transform'])
  assert np.array_equal(v,np.asarray(p['vertices'])) and np.array_equal(f,np.asarray(p['triangles']));assert [x.material_index for x in o.data.polygons]==p['material_indices'];assert not o.modifiers;assert [m.name for m in o.data.materials]==[m['id'] for m in d['materials']]
  transforms[p['id']]=float(np.max(np.abs(T-expectedT)));world_errors[p['id']]=float(np.max(np.abs((v@T[:3,:3].T+T[:3,3])-(v@expectedT[:3,:3].T+expectedT[:3,3]))));assert world_errors[p['id']]<1e-5;count.update(d['materials'][i]['id'] for i in p['material_indices'])
 assert all(count[m['id']]>0 for m in d['materials'])
 for m in d['materials']:
  ob=bpy.data.materials[m['id']];rgb=[]
  for k in [1,3,5]:
   x=int(m['srgb'][k:k+2],16)/255;rgb.append(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)
  actual=ob.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value;assert max(abs(a-b) for a,b in zip(actual,rgb))<1e-7
 assert not bpy.data.libraries and not bpy.data.fonts and not any(i.source=='FILE' or i.packed_file for i in bpy.data.images)
 assert not bpy.data.texts and not bpy.data.sounds and not bpy.data.movieclips
 assert scene.render.filepath=='//previews/front.png';assert hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest()==before
 report={'blender_version':bpy.app.version_string,'scene_sha256':before,'model_meshes':4,'render_only_ground_meshes':1,'palette_materials':9,'canonical_vertices_triangle_indices_and_face_material_indices_exact':True,'assembly_transform_float32_max_mm':transforms,'transformed_vertex_difference_max_mm':world_errors,'all_nine_materials_used':dict(count),'sRGB_to_linear_palette_verified':True,'external_images':0,'packed_photos':0,'external_libraries':0,'font_files':0,'embedded_scripts':0,'read_only_check_scene_SHA_unchanged':True,'scene_not_a_validated_print_layout':True}
 (R/'qa/scene-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
