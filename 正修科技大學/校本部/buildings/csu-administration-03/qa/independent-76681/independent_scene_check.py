from pathlib import Path
import hashlib,json,struct
import bpy

ROOT=Path(__file__).resolve().parent
P=Path('<MODEL_ROOT>')
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(tris):
    return sha(json.dumps(sorted(tuple(sorted(tuple(float(c) for c in p) for p in t)) for t in tris),separators=(',',':')).encode())
def stl_triangles(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
    result=[]
    for i in range(n):
        pts=struct.unpack_from('<9f',raw,84+i*50+12);result.append([pts[j:j+3] for j in (0,3,6)])
    return result
bpy.ops.wm.open_mainfile(filepath=str(P/'models/v2/scene.blend'))
scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
parts={o.name.removeprefix('PrintPart_'):o for o in scene.objects if o.type=='MESH' and o.get('print_part')}
manifest=json.loads((P/'previews/v2/render-manifest.json').read_text(encoding='utf-8'))
result={'bpy_version':bpy.app.version_string,'scene_sha256':sha((P/'models/v2/scene.blend').read_bytes()),'frame':scene.frame_current,'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,'length_unit':scene.unit_settings.length_unit},'print_meshes':len(parts),'excluded_studio_meshes':[o.name for o in scene.objects if o.type=='MESH' and not o.get('print_part')],'parts':{},'linked_libraries':len(bpy.data.libraries),'images':len(bpy.data.images),'external_dependency_paths':list(bpy.utils.blend_paths()),'manifest_scene_SHA_matches':sha((P/'models/v2/scene.blend').read_bytes())==manifest['scene_sha256'],'preview_manifest_hash_checks':[]}
for name,obj in parts.items():
    raw_tri=stl_triangles(P/'models/v2/parts'/f'{name}.stl')
    local_tri=[[tuple(obj.data.vertices[i].co) for i in poly.vertices] for poly in obj.data.polygons]
    result['parts'][name]={'STL_SHA256':sha((P/'models/v2/parts'/f'{name}.stl').read_bytes()),'STL_geometry_SHA256':digest(raw_tri),'scene_local_geometry_SHA256':digest(local_tri),'exact_local_triangle_multiset_identical':digest(raw_tri)==digest(local_tri),'triangles':len(local_tri),'location_mm':list(obj.location),'rotation':list(obj.rotation_euler),'scale':list(obj.scale),'modifiers':len(obj.modifiers),'hide_render':obj.hide_render}
for view in manifest['views']:
    result['preview_manifest_hash_checks'].append({'path':view['path'],'matches':sha((P/view['path']).read_bytes())==view['png_sha256']})
overview=manifest['assembly_overview'];result['preview_manifest_hash_checks'].append({'path':overview['path'],'matches':sha((P/overview['path']).read_bytes())==overview['png_sha256']})
result['render_source_matches_manifest']=sha((P/'source/render_preview.py').read_bytes())==manifest['render_source_sha256']
result['all_part_meshes_identical']=all(r['exact_local_triangle_multiset_identical'] and r['modifiers']==0 and r['scale']==[1,1,1] and r['rotation']==[0,0,0] for r in result['parts'].values())
assert result['all_part_meshes_identical'] and len(parts)==2
assert result['parts']['body']['location_mm']==[0,0,0] and result['parts']['roof']['location_mm']==[0,0,85]
assert all(r['matches'] for r in result['preview_manifest_hash_checks'])
# One review render from the fixed saved scene; change output/render quality in memory only.
scene.camera=bpy.data.objects['View_front-three-quarter'];scene.render.filepath=str(ROOT/'independent-front.png')
scene.render.resolution_x=900;scene.render.resolution_y=638;scene.render.resolution_percentage=100
scene.render.threads_mode='FIXED';scene.render.threads=4;scene.cycles.samples=32;scene.cycles.seed=0
bpy.ops.render.render(write_still=True)
result['independent_render']={'file':'independent-front.png','SHA256':sha((ROOT/'independent-front.png').read_bytes()),'pixels':[900,638],'samples':32,'source':'Saved scene opened read-only; assembled frame1, actual two STL meshes verified exact. Output path and render quality changed only in memory.'}
(ROOT/'independent-scene-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
