"""Read-only Blender comparison of the new exchange with the unchanged appearance scene.
Run: blender -b --factory-startup --python appearance/source/verify_exchange_scene.py
Does not save scene.blend or render any image.
"""
from pathlib import Path
import bpy,hashlib,json,struct,zipfile,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def lin(v):
    c=v/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
scene_file=OUT/'scene.blend';before=sha(scene_file)
bpy.ops.wm.open_mainfile(filepath=str(scene_file))
with zipfile.ZipFile(OUT/'a1-appearance-core.3mf') as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
palette=json.loads((OUT/'palette.json').read_text());colors={p['id']:p['srgb'] for p in palette['materials']};records=[]
for o in root.findall('m:resources/m:object',NS):
    mesh=o.find('m:mesh',NS)
    if mesh is None:continue
    name=o.get('name');obj=bpy.data.objects[name]
    vertices=[tuple(f32(v.get(k)) for k in ['x','y','z']) for v in mesh.findall('m:vertices/m:vertex',NS)]
    faces=[tuple(int(t.get(k)) for k in ['v1','v2','v3']) for t in mesh.findall('m:triangles/m:triangle',NS)]
    assert vertices==[tuple(v.co) for v in obj.data.vertices] and faces==[tuple(p.vertices) for p in obj.data.polygons]
    assert not obj.modifiers and tuple(obj.location)==(0,0,0) and tuple(obj.rotation_euler)==(0,0,0) and tuple(obj.scale)==(1,1,1)
    mid=palette['mesh_materials'][name];hexcolor=colors[mid];assert len(obj.data.materials)==1
    mat=obj.data.materials[0];assert mat.name==mid and mat['approximate_srgb_hex']==hexcolor
    values=[int(hexcolor[j:j+2],16) for j in [1,3,5]]
    assert max(abs(a-lin(b)) for a,b in zip(mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3],values))<1e-7
    assert all(p.material_index==0 for p in obj.data.polygons)
    records.append({'mesh':name,'material':mid,'sRGB':hexcolor,'geometry_at_Blender_float32_exact':True})
assert len(records)==8 and len([o for o in bpy.data.objects if o.type=='MESH'])==8 and len(bpy.data.materials)==7
assert abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-9 and not bpy.data.libraries
assert all(i.type=='RENDER_RESULT' and not i.packed_file and not i.filepath for i in bpy.data.images)
assert before==sha(scene_file)
r={'Blender':bpy.app.version_string,'scene_sha256_before_and_after':before,'scene_file_unchanged':True,'mesh_count':8,'material_count':7,'unit':'millimeter','scale_length':.001,'new_3mf_matches_existing_scene_geometry_at_float32':True,'material_identities_sRGB_and_linear_BSDF_match':True,'reference_photo_pixels_embedded':False,'external_image_or_library_dependencies':False,'new_render_performed':False,'parts':records}
(OUT/'qa/scene-exchange-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('Read-only comparison passed: eight meshes, seven colors; scene and previews untouched.')
