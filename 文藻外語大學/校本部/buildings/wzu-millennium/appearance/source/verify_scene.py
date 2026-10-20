"""Run with Blender after rendering. Exact mesh/material and no external assets."""
from pathlib import Path
import bpy,json,hashlib,zipfile,xml.etree.ElementTree as E,numpy as np
A=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def lin(s):return s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'))
obs=[o for o in bpy.data.objects if o.type=='MESH'];assert len(obs)==1;ob=obs[0]
with zipfile.ZipFile(A/'millennium-appearance.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
me=r.find('m:resources/m:object/m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts])
assert np.array_equal(np.array([list(p.co) for p in ob.data.vertices]),v);assert np.array_equal(np.array([list(p.vertices) for p in ob.data.polygons]),f);assert [p.material_index for p in ob.data.polygons]==[int(t.get('p1')) for t in ts]
assert np.array_equal(np.array(ob.matrix_world),np.eye(4))
pal=json.loads((A/'palette.json').read_text())['materials'];assert [m.name for m in ob.data.materials]==[p['id'] for p in pal]
for m,p in zip(ob.data.materials,pal):
 assert max(abs(a-b) for a,b in zip(m.diffuse_color,[lin(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[1]))<1e-7
 assert max(abs(a-b) for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,m.diffuse_color))<1e-7
assert all(im.type=='RENDER_RESULT' and not im.filepath and not im.packed_file for im in bpy.data.images) and not bpy.data.libraries and not bpy.data.texts and not bpy.data.sounds and not bpy.data.movieclips
d={'scene_sha256':hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest(),'mesh_objects':1,'vertices':len(v),'triangles':len(f),'exact_original_STL_geometry_through_3MF':True,'identity_transform':True,'face_material_indices_exact':True,'six_named_srgb_materials_verified':True,'external_textures_libraries_embedded_scripts_sounds_movies':0,'internal_render_result_images':[im.name for im in bpy.data.images],'original_scene_untouched':True,'FFF_or_physical_print_validated':False}
(A/'qa/scene-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
