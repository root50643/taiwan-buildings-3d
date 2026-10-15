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
        'relative_saved_render_path':bpy.context.scene.render.filepath=='//previews/front.png'}
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256(raw).hexdigest(),
     'original_oriented_triangle_digest':digest(original),'saved_oriented_triangle_digest':digest(saved),
     'triangles':count,'mesh_objects':len(objects),'blend_sha256':hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest()}
(R/'scene-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));require(out['passed'], 'Required condition failed')
