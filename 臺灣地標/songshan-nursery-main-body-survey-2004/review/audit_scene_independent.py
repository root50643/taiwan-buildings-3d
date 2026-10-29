import bpy, numpy as np, json, pathlib, collections, hashlib, sys

root = pathlib.Path(bpy.data.filepath).parent
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
report_path = pathlib.Path(args[0]) if args else root.parent/'independent-review'/'scene-audit.json'
d = np.load(root/'mesh-data.npz')
parts = json.loads((root/'construction-parts.json').read_text())
palette = json.loads((root/'editable-parts.json').read_text())['palette']
checks = {}
details = {}

def digest(a, dtype):
    return hashlib.sha256(np.asarray(a, dtype=dtype).tobytes()).hexdigest()

def signature(v, f, evidence, material, operation):
    return (digest(v, '<f4'), digest(f, '<u4'), evidence, material, operation)

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
visible = [o for o in meshes if not o.hide_render]
hidden = [o for o in meshes if o.hide_render]
checks['exactly_one_rendered_mesh'] = len(visible) == 1
checks['all_mesh_transforms_identity'] = all(np.array_equal(np.asarray(o.matrix_world), np.eye(4)) for o in meshes)
checks['metric_millimetre_scene_units'] = bpy.context.scene.unit_settings.system == 'METRIC' and abs(bpy.context.scene.unit_settings.scale_length - .001) < 1e-10
checks['no_mesh_modifiers_or_constraints'] = all(len(o.modifiers) == 0 and len(o.constraints) == 0 for o in meshes)
checks['no_shape_keys'] = all(o.data.shape_keys is None for o in meshes)
checks['no_external_libraries'] = len(bpy.data.libraries) == 0
checks['no_text_blocks'] = len(bpy.data.texts) == 0
details['image_datablocks'] = [{'name':i.name,'source':i.source,'filepath':i.filepath,'size':list(i.size),'packed':bool(i.packed_file),'users':i.users} for i in bpy.data.images]
checks['no_external_or_packed_image_assets'] = all(i.source == 'VIEWER' and not i.filepath and not i.packed_file and list(i.size) == [0,0] for i in bpy.data.images)
checks['no_image_texture_nodes'] = all(n.type not in ('TEX_IMAGE','TEX_ENVIRONMENT') for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
checks['no_animation_or_drivers'] = all(o.animation_data is None for o in bpy.data.objects)
if len(visible) == 1:
    o = visible[0]
    v = np.asarray([tuple(x.co) for x in o.data.vertices], dtype='<f4')
    f = np.asarray([tuple(x.vertices) for x in o.data.polygons], dtype='<u4')
    mi = np.asarray([x.material_index for x in o.data.polygons], dtype='<i4')
    checks['visible_vertex_float32_exact'] = np.array_equal(v, d['vertices'].astype('<f4'))
    checks['visible_faces_exact'] = np.array_equal(f, d['faces'])
    checks['visible_material_indices_exact'] = np.array_equal(mi, d['materials'])
    checks['visible_palette_order_exact'] = [m.name for m in o.data.materials] == [p['name'] for p in palette]
    checks['visible_mesh_not_viewport_hidden'] = not o.hide_get() and not o.hide_viewport
    details['visible_vertex_count'] = len(v)
    details['visible_face_count'] = len(f)
    details['visible_vertex_hash_f32'] = digest(v, '<f4')
    details['visible_face_hash'] = digest(f, '<u4')
    details['visible_material_hash'] = digest(mi, '<i4')
    details['visible_scope'] = o.get('scope','')
    details['visible_coordinate_frame'] = o.get('coordinate_frame','')

expected = collections.Counter(signature(p['vertices'],p['faces'],p['evidence'],palette[p['material']]['name'],p.get('operation','union_add')) for p in parts)
observed = collections.Counter()
for o in hidden:
    v = [tuple(x.co) for x in o.data.vertices]
    f = [tuple(x.vertices) for x in o.data.polygons]
    mat = o.data.materials[0].name if len(o.data.materials) == 1 else 'INVALID_MATERIAL_SLOTS'
    observed[signature(v,f,o.get('evidence',''),mat,o.get('construction_operation','union_add'))] += 1
checks['all_hidden_geometry_evidence_materials_match'] = expected == observed
checks['hidden_count_exact'] = len(hidden) == len(parts)
checks['hidden_parts_no_additional_face_materials'] = all(all(p.material_index == 0 for p in o.data.polygons) for o in hidden)
checks['hidden_parts_hidden_in_viewport'] = all(o.hide_get() or o.hide_viewport or all(c.hide_viewport for c in o.users_collection) for o in hidden)
checks['subtractive_cutters_operations_exact'] = collections.Counter(p.get('operation','union_add') for p in parts) == collections.Counter(o.get('construction_operation','union_add') for o in hidden)
details['expected_parts'] = len(parts)
details['actual_hidden_parts'] = len(hidden)
details['construction_operation_counts'] = dict(collections.Counter(p.get('operation','union_add') for p in parts))
details['unmatched_expected_parts'] = sum((expected-observed).values())
details['unmatched_actual_parts'] = sum((observed-expected).values())
material_checks = []
for p in palette:
    m = bpy.data.materials.get(p['name'])
    if m is None or not m.use_nodes:
        material_checks.append(False); continue
    c = [int(p['hex'][i:i+2],16)/255 for i in (1,3,5)]
    lin = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in c]
    node = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    material_checks.append(node is not None and np.allclose(node.inputs['Base Color'].default_value, lin+[1], rtol=0,atol=1e-7) and node.inputs['Alpha'].default_value == 1 and m.get('source_evidence','') == p['evidence'])
checks['all_palette_colors_alpha_evidence_exact'] = all(material_checks)
checks['all_editable_metadata_nonempty'] = all(bool(p['name']) and bool(p['evidence']) and isinstance(p['material'], int) for p in parts)
report = {'checks':checks, 'details':details, 'passed':all(checks.values()), 'scope':'Independent scene object transforms, millimetre unit convention, full visible geometry/material comparison, and full hidden per-part geometry/material/evidence multiset comparison. No builder QA is trusted as evidence.'}
report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
assert report['passed']
