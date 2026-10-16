"""Run in Blender after loading scene.blend: prove actual STL triangles are saved."""

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

from pathlib import Path
import bpy,hashlib,json,struct
R=Path(__file__).resolve().parent
raw=(R/'model.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0]
def canonical(tri):
    pts=[tuple(float(x) for x in p) for p in tri]
    return min(tuple(pts[i:]+pts[:i]) for i in range(3))
def digest(tris):
    return hashlib.sha256(b''.join(struct.pack('<9f',*(v for p in t for v in p)) for t in sorted(tris))).hexdigest()
original=[]
for i in range(count):
    a=struct.unpack_from('<9f',raw,84+i*50+12);original.append(canonical([a[0:3],a[3:6],a[6:9]]))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];saved=[]
for o in objects:
    for f in o.data.polygons:
        require(len(f.vertices)==3, 'Nontriangular saved face')
        saved.append(canonical([o.data.vertices[j].co[:] for j in f.vertices]))
checks={'one_mesh_object':len(objects)==1,'triangle_count_same':len(saved)==count,
        'all_oriented_coordinates_exact':sorted(saved)==sorted(original),
        'no_modifiers':all(len(o.modifiers)==0 for o in objects),
        'identity_transforms':all(tuple(o.location)==(0,0,0) and tuple(o.scale)==(1,1,1) and tuple(o.rotation_euler)==(0,0,0) for o in objects),
        'source_hash_recorded':all(o.get('source_stl_sha256')==hashlib.sha256(raw).hexdigest() for o in objects),
        'no_embedded_text_blocks':len(bpy.data.texts)==0,
        'no_linked_libraries':len(bpy.data.libraries)==0,
        'no_external_images':all(not im.filepath for im in bpy.data.images),
        'no_image_texture_nodes':not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes),
        'relative_saved_render_path':bpy.context.scene.render.filepath=='//previews/front.png',
        'no_other_renderable_object_types':all(o.type in {'MESH','CAMERA','LIGHT'} for o in bpy.data.objects),
        'no_hidden_unlinked_objects':set(bpy.data.objects)==set(bpy.context.scene.objects),
        'no_parent_or_instances':all(o.parent is None and o.instance_type=='NONE' and o.instance_collection is None for o in bpy.data.objects),
        'mesh_world_matrix_identity':all(all(o.matrix_world[i][j]==(1 if i==j else 0) for i in range(4) for j in range(4)) for o in objects),
        'mesh_render_visible':all(not o.hide_render for o in objects),
        'single_scene_no_compositor':len(bpy.data.scenes)==1 and not bpy.context.scene.use_nodes,
        'no_external_blend_resource_paths':not bpy.utils.blend_paths(absolute=False,packed=True,local=False),
        'no_external_media_datablocks':not any(len(getattr(bpy.data,n)) for n in ['sounds','movieclips','volumes','cache_files']),
        'no_linked_datablocks':all(getattr(q,'library',None) is None for name in ['objects','meshes','materials','worlds','scenes','collections','cameras','lights'] for q in getattr(bpy.data,name))}
# Reopened datablock strings, custom properties and file-browser settings.
import re
private_parts=['/'+q+'/' for q in ['workspace','home','Users','tmp']]+['file'+ '://']
def private_string(value):
    if isinstance(value,bytes):value=value.decode('utf8','replace')
    return isinstance(value,str) and (any(q in value for q in private_parts) or re.search(r'(?:^|[^A-Za-z])[A-Za-z]:[\\/]',value) is not None)
def property_private(value):
    if private_string(value):return True
    if hasattr(value,'items'):return any(private_string(str(k)) or property_private(v) for k,v in value.items())
    if isinstance(value,(list,tuple)):return any(property_private(v) for v in value)
    return False
bad_strings=[];packed=[]
for prop in bpy.data.bl_rna.properties:
    if prop.type!='COLLECTION':continue
    for block in getattr(bpy.data,prop.identifier):
        if hasattr(block,'keys') and property_private({k:block[k] for k in block.keys()}):bad_strings.append(prop.identifier+':custom')
        if getattr(block,'packed_file',None) is not None or len(getattr(block,'packed_files',[])):packed.append(prop.identifier)
        if not hasattr(block,'bl_rna'):continue
        for field in block.bl_rna.properties:
            if field.type=='STRING':
                try:
                    if private_string(getattr(block,field.identifier)):bad_strings.append(prop.identifier+':'+field.identifier)
                except (TypeError,AttributeError):pass
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                if private_string(space.params.directory) or private_string(space.params.filename):bad_strings.append('file_browser')
checks['no_private_datablock_or_custom_property_paths']=not bad_strings
checks['no_packed_resources']=not packed
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256(raw).hexdigest(),
     'original_oriented_triangle_digest':digest(original),'saved_oriented_triangle_digest':digest(saved),
     'triangles':count,'mesh_objects':len(objects),'blend_sha256':hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest()}
(R/'scene-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));require(out['passed'], 'Required condition failed')
