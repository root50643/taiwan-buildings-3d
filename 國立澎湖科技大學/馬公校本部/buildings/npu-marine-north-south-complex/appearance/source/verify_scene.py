"""Reopen original and appearance scenes; compare complete mesh arrays and materials.
blender -b --python appearance/source/verify_scene.py
"""
from pathlib import Path
import collections,hashlib,json,math
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
def snapshot():
    return {o.name:{'vertices':[tuple(v.co) for v in o.data.vertices],'triangles':[tuple(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world],'materials':[p.material_index for p in o.data.polygons]} for o in bpy.context.scene.objects if o.type=='MESH'}
def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene.blend'));original=snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'scene.blend'));current=snapshot();assert set(original)==set(current) and len(current)==10
    for name in current:
        for field in ['vertices','triangles','matrix']:assert current[name][field]==original[name][field],(name,field)
        assert [{0:0,1:1,2:1,3:2,4:3}[i] for i in current[name]['materials']]==original[name]['materials'],name
    scene=bpy.context.scene;assert abs(scene.unit_settings.scale_length-.001)<1e-9 and scene.unit_settings.system=='METRIC'
    pal=json.loads((OUT/'palette.json').read_text())['materials'];counts=collections.Counter()
    for ob in scene.objects:
        if ob.type!='MESH':continue
        assert len(ob.modifiers)==0 and [m.name for m in ob.data.materials]==[p['id'] for p in pal]
        counts.update(ob.data.materials[p.material_index].name for p in ob.data.polygons)
    assert len(bpy.data.materials)==5 and all(counts[p['id']]>0 for p in pal)
    for p in pal:
        m=bpy.data.materials[p['id']];expected=[]
        for i in [1,3,5]:
            x=int(p['srgb'][i:i+2],16)/255;expected.append(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)
        for a,b in zip(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,expected):assert abs(a-b)<1e-7
    assert not bpy.data.libraries and not any(i.source=='FILE' or i.packed_file for i in bpy.data.images)
    objects=[o for o in scene.objects if o.type=='MESH'];cam=scene.camera;framing={}
    views={'front':((245,290,190),(60,76,13),270),'rear':((-190,-200,180),(60,76,13),275),'top':((59,79,420),(59,79,0),246),'exploded':((245,290,240),(60,76,35),290)}
    for name,(loc,target,scale) in views.items():
        for ob in objects:ob.location.z=({'02-north-upper':20,'04-hall-roof':12,'05-bridge-tray':8,'06-bridge-lid':22}.get(ob.name,0) if name=='exploded' else 0)
        cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update()
        points=[world_to_camera_view(scene,cam,o.matrix_world@v.co) for o in objects for v in o.data.vertices]
        bounds=[[min(v[k] for v in points) for k in [0,1]],[max(v[k] for v in points) for k in [0,1]]]
        assert all(.02<min(v[k] for v in points)<max(v[k] for v in points)<.98 for k in [0,1]),(name,bounds)
        framing[name]={'normalized_image_bounds':bounds,'all_mesh_vertices_inside_2_percent_margin':True}
    report={'blender_version':bpy.app.version_string,'source_scene_sha256':hashlib.sha256((ROOT/'scene.blend').read_bytes()).hexdigest(),'appearance_scene_sha256':hashlib.sha256((OUT/'scene.blend').read_bytes()).hexdigest(),'mesh_instances':10,'all_vertex_values_triangle_indices_and_transforms_equal_to_original_scene':True,'original_face_material_regions_retained_with_stair_identity_split':True,'material_faces_for_10_instances':dict(counts),'palette_sRGB_to_linear_verified':True,'unit_mm':True,'modifiers':0,'external_image_dependencies':0,'packed_source_photos':0,'external_libraries':0,'preview_framing':framing,'physical_print_or_fit_verified':False}
    (OUT/'qa/scene-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
