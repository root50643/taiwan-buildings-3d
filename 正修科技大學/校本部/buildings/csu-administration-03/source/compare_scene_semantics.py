"""Read-only bpy signatures for original and staged scenes. Never saves a blend."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import bpy


def normalized(value):
    if isinstance(value,(bool,int,float,str)) or value is None:return value
    if isinstance(value,bytes):return value.hex()
    if isinstance(value,set):return sorted(normalized(x) for x in value)
    return [normalized(x) for x in value]


def scalar_properties(value):
    result={}
    ignore={'rna_type','session_uid','users','is_updated','is_updated_data','is_updated_transform'}
    for prop in value.bl_rna.properties:
        if prop.identifier in ignore or prop.type not in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:continue
        try:result[prop.identifier]=normalized(getattr(value,prop.identifier))
        except (AttributeError,TypeError,RuntimeError):continue
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def mesh_record(mesh):
    h=hashlib.sha256()
    for vertex in mesh.vertices:h.update(struct.pack('<3f',*vertex.co))
    for edge in mesh.edges:h.update(struct.pack('<2I',*edge.vertices))
    for loop in mesh.loops:h.update(struct.pack('<2I',loop.vertex_index,loop.edge_index))
    for poly in mesh.polygons:
        h.update(struct.pack('<4I?',poly.loop_start,poly.loop_total,poly.material_index,poly.index,poly.use_smooth))
    return {'vertices':len(mesh.vertices),'edges':len(mesh.edges),'loops':len(mesh.loops),
            'polygons':len(mesh.polygons),'geometry_topology_material_index_sha256':h.hexdigest(),
            'materials':[m.name if m else None for m in mesh.materials]}


def nodes_record(tree):
    if tree is None:return None
    return {'nodes':{n.name:{'type':n.bl_idname,'properties':scalar_properties(n),
        'inputs':[{ 'name':s.name,'value':normalized(s.default_value) if hasattr(s,'default_value') else None}
                  for s in n.inputs]} for n in tree.nodes},
        'links':sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in tree.links)}


def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    scene=bpy.context.scene
    bpy.context.view_layer.update()
    objects={o.name:{'type':o.type,'data_name':o.data.name if o.data else None,
        'parent':o.parent.name if o.parent else None,'properties':scalar_properties(o),
        'custom_properties':{k:normalized(o[k]) for k in o.keys()},
        'modifiers':[(m.name,m.type,scalar_properties(m)) for m in o.modifiers],
        'constraints':[(c.name,c.type,scalar_properties(c)) for c in o.constraints]}
        for o in bpy.data.objects}
    frames={}
    current=scene.frame_current
    for frame in [1,2]:
        scene.frame_set(frame);bpy.context.view_layer.update()
        frames[str(frame)]={o.name:{'matrix_world':normalized(o.matrix_world),
            'location':normalized(o.location),'rotation_euler':normalized(o.rotation_euler),
            'scale':normalized(o.scale)} for o in bpy.data.objects}
    scene.frame_set(current)
    return {'objects':objects,'meshes':{m.name:mesh_record(m) for m in bpy.data.meshes},
        'cameras':{c.name:scalar_properties(c) for c in bpy.data.cameras},
        'lights':{l.name:{'properties':scalar_properties(l),'nodes':nodes_record(l.node_tree)} for l in bpy.data.lights},
        'materials':{m.name:{'properties':scalar_properties(m),'nodes':nodes_record(m.node_tree)} for m in bpy.data.materials},
        'worlds':{w.name:{'properties':scalar_properties(w),'nodes':nodes_record(w.node_tree)} for w in bpy.data.worlds},
        'render_settings':{'render':scalar_properties(scene.render),'cycles':scalar_properties(scene.cycles),
            'view':scalar_properties(scene.view_settings),'display':scalar_properties(scene.display_settings),
            'units':scalar_properties(scene.unit_settings),'camera':scene.camera.name if scene.camera else None,
            'frame_current':current,'frame_start':scene.frame_start,'frame_end':scene.frame_end},
        'frame_transforms':frames,
        'external_references':{'blend_paths':list(bpy.utils.blend_paths()),
            'libraries':[l.filepath for l in bpy.data.libraries],
            'images':[(i.name,i.filepath) for i in bpy.data.images]}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-root',required=True,type=Path)
    p.add_argument('--staging-root',required=True,type=Path)
    p.add_argument('--report-name',default='semantic-comparison-corrected.json')
    args=p.parse_args();root=args.input_root.resolve();stage=args.staging_root.resolve()
    assert Path(args.report_name).name==args.report_name and args.report_name!='semantic-comparison.json'
    assert not stage.is_relative_to(root)
    manifest=json.loads((stage/'manifest.json').read_text(encoding='utf8'))
    result={'tool':'compare_scene_semantics.py','tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'bpy_version':bpy.app.version_string,'operation':'Read-only opens, signature extraction, memory frame evaluation; no Blender saves or renders',
        'expected_exclusion':'File browser directory UI field is the authorized metadata change. Current main-file runtime location is also excluded.',
        'files':[]}
    for record in manifest['files']:
        relative=record['path'];original=root/relative;delivered=stage/relative
        before_original=hashlib.sha256(original.read_bytes()).hexdigest()
        before_delivered=hashlib.sha256(delivered.read_bytes()).hexdigest()
        assert before_original==record['original_sha256'], 'Wrong original scene identity'
        assert before_delivered==record['delivered_sha256'], 'Wrong delivered scene identity'
        assert before_original!=before_delivered
        a=inspect(original);b=inspect(delivered)
        after_original=hashlib.sha256(original.read_bytes()).hexdigest()
        after_delivered=hashlib.sha256(delivered.read_bytes()).hexdigest()
        assert after_original==before_original==record['original_sha256']
        assert after_delivered==before_delivered==record['delivered_sha256']
        checks={category:a[category]==b[category] for category in a}
        hashes={category:{'original_sha256':digest(a[category]),'delivered_sha256':digest(b[category])} for category in a}
        result['files'].append({'path':relative,'original_scene_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'delivered_scene_sha256':hashlib.sha256(delivered.read_bytes()).hexdigest(),
            'source_identity_checks':{'before_original_sha256':before_original,'after_original_sha256':after_original,
                'before_delivered_sha256':before_delivered,'after_delivered_sha256':after_delivered,
                'original_matches_known_old_sha':True,'delivered_matches_known_new_sha':True,
                'old_and_new_hashes_differ':True,'both_input_files_unchanged_during_bpy_comparison':True},
            'category_checks':checks,'category_signatures':hashes,'passed':all(checks.values())})
    result['passed']=all(f['passed'] for f in result['files'])
    (stage/args.report_name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
    assert result['passed'],'Signature mismatch retained in report; no file flags rewritten'


if __name__=='__main__':main()
