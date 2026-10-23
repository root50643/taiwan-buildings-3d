"""Blender-side scene readback and material edit/save/reopen check."""
from pathlib import Path
import bpy,json,hashlib,zipfile,xml.etree.ElementTree as E,tempfile,numpy as np
A=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));obs=[o for o in bpy.data.objects if o.type=='MESH'];assert len(obs)==1;ob=obs[0]
with zipfile.ZipFile(A/'hwai-dormitory-m-appearance.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
me=r.find('m:resources/m:object/m:mesh',NS);v=np.array([[float(t.get(k)) for k in 'xyz'] for t in me.findall('m:vertices/m:vertex',NS)]);ts=me.findall('m:triangles/m:triangle',NS);f=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]);colors=[int(t.get('p1')) for t in ts]
def check_mesh(o):
 assert np.array_equal(np.array([list(p.co) for p in o.data.vertices]),v);assert np.array_equal(np.array([list(p.vertices) for p in o.data.polygons]),f);assert [p.material_index for p in o.data.polygons]==colors;assert np.array_equal(np.array(o.matrix_world),np.eye(4))
check_mesh(ob);pal=json.loads((A/'palette.json').read_text())['materials'];assert [m.name for m in ob.data.materials]==[p['id'] for p in pal]
assert set(colors)==set(range(len(pal)))
expected=[]
for m,p in zip(ob.data.materials,pal):
 rgba=[lin(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[1];expected.append(rgba);assert max(abs(a-b) for a,b in zip(m.diffuse_color,rgba))<1e-7;assert max(abs(a-b) for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,rgba))<1e-7
assert all(i.type=='RENDER_RESULT' and not i.filepath and not i.packed_file for i in bpy.data.images);assert not bpy.data.libraries and not bpy.data.texts and not bpy.data.sounds and not bpy.data.movieclips
ob.data.materials[1].diffuse_color=(.1,.2,.3,1);ob.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.1,.2,.3,1)
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p));bpy.ops.wm.open_mainfile(filepath=str(p));o=[x for x in bpy.data.objects if x.type=='MESH'][0];check_mesh(o)
 for i,m in enumerate(o.data.materials):
  rgba=(.1,.2,.3,1) if i==1 else expected[i];assert max(abs(a-b) for a,b in zip(m.diffuse_color,rgba))<1e-7;assert max(abs(a-b) for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,rgba))<1e-7
# Actual vertex edit in an isolated copy, then save/reopen; delivery remains pristine.
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));ob=[x for x in bpy.data.objects if x.type=='MESH'][0];ob.data.vertices[0].co.x+=.125
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'vertex-edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p));bpy.ops.wm.open_mainfile(filepath=str(p));o=[x for x in bpy.data.objects if x.type=='MESH'][0];vv=np.array([list(p.co) for p in o.data.vertices]);want=v.copy();want[0,0]+=.125;assert np.array_equal(vv,want);assert [p.material_index for p in o.data.polygons]==colors
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));check_mesh([x for x in bpy.data.objects if x.type=='MESH'][0])
# Render from saved/reopened delivery scene, strip nondeterministic metadata, compare bytes.
import struct
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'front.png';bpy.context.scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 assert clean==(A/'previews/front.png').read_bytes()
(A/'qa/scene-validation.json').write_text(json.dumps({'scene_sha256':hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest(),'vertices':len(v),'triangles':len(f),'original_triangle_geometry_exact':True,'material_names_and_srgb_verified':True,'material_count':len(pal),'all_palette_materials_used':True,'identity_transform':True,'single_material_edit_save_reopen_verified':True,'single_vertex_edit_save_reopen_verified':True,'reopened_scene_render_matches_front_bytes':True,'other_materials_and_geometry_preserved_on_edit':True,'external_assets_or_embedded_scripts':0,'physical_print_tested':False},indent=2)+'\n')
