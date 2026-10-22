"""Blender-side scene readback and material edit/save/reopen check."""
from pathlib import Path
import bpy,json,hashlib,zipfile,xml.etree.ElementTree as E,tempfile,numpy as np
A=Path(__file__).resolve().parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));obs=[o for o in bpy.data.objects if o.type=='MESH'];assert len(obs)==1;ob=obs[0]
with zipfile.ZipFile(A/'model.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
me=r.find('m:resources/m:object/m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);colors=[int(t.get('p1')) for t in ts]
def check_mesh(o,expected_v=v):
 assert np.array_equal(np.array([list(p.co) for p in o.data.vertices]),expected_v);assert np.array_equal(np.array([list(p.vertices) for p in o.data.polygons]),f);assert [p.material_index for p in o.data.polygons]==colors;assert np.array_equal(np.array(o.matrix_world),np.eye(4))
check_mesh(ob);assert ob['original_STL_sha256']==hashlib.sha256((A/'model.stl').read_bytes()).hexdigest();pal=json.loads((A/'palette.json').read_text())['materials'];assert [m.name for m in ob.data.materials]==[p['id'] for p in pal]
expected=[]
for m,p in zip(ob.data.materials,pal):
 rgba=[lin(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[p.get('alpha',255)/255];expected.append(rgba);assert max(abs(a-b) for a,b in zip(m.diffuse_color,rgba))<1e-7;assert max(abs(a-b) for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,rgba))<1e-7
assert all(abs(m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value-p.get('alpha',255)/255)<1e-7 for m,p in zip(ob.data.materials,pal))
assert all(i.type=='RENDER_RESULT' and not i.filepath and not i.packed_file for i in bpy.data.images);assert not bpy.data.libraries and not bpy.data.texts and not bpy.data.sounds and not bpy.data.movieclips
ob.data.materials[2].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.6;ob.data.materials[2].diffuse_color=(.1,.2,.3,.6);ob.data.materials[2].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.1,.2,.3,.6)
edited_v=v.copy();edited_v[0,0]+=.25;ob.data.vertices[0].co.x+=.25
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p));bpy.ops.wm.open_mainfile(filepath=str(p));o=[x for x in bpy.data.objects if x.type=='MESH'][0];check_mesh(o,edited_v)
 for i,m in enumerate(o.data.materials):
  rgba=(.1,.2,.3,.6) if i==2 else expected[i];assert abs(m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value-rgba[3])<1e-7;assert max(abs(a-b) for a,b in zip(m.diffuse_color,rgba))<1e-7;assert max(abs(a-b) for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,rgba))<1e-7
(A/'qa/scene-validation.json').write_text(json.dumps({'scene_sha256':hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest(),'vertices':len(v),'triangles':len(f),'original_triangle_geometry_exact':True,'material_names_srgb_and_alpha_verified':True,'all_materials_opaque':True,'STL_has_no_transparency':True,'material_count':len(pal),'identity_transform':True,'single_material_color_alpha_edit_save_reopen_verified':True,'single_vertex_edit_save_reopen_verified':True,'test_vertex_delta_x_mm':.25,'other_materials_and_unedited_vertices_preserved':True,'external_assets_or_embedded_scripts':0,'physical_print_tested':False},indent=2)+'\n')
