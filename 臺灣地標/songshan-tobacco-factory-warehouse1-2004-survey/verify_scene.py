"""Reopen scene and verify unified mesh plus all editable evidence metadata."""
import bpy,numpy as np,json,pathlib,collections
p=pathlib.Path(bpy.data.filepath).parent
d=np.load(p/'mesh-data.npz');parts=json.loads((p/'construction-parts.json').read_text());edit=json.loads((p/'editable-parts.json').read_text())
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render];o=obs[0]
v=np.array([tuple(x.co) for x in o.data.vertices]);f=np.array([tuple(x.vertices) for x in o.data.polygons])
expected=collections.Counter(x['evidence'] for x in parts)
r={'one_visible_mesh':len(obs)==1,'vertices_equal':bool(np.allclose(v,d['vertices'],rtol=0,atol=2e-5)),'faces_equal':bool(np.array_equal(f,d['faces'])),'no_external_images':not any(i.source != 'VIEWER' for i in bpy.data.images),'no_text_blocks':len(bpy.data.texts)==0,'hidden_editable_components':len([o for o in bpy.context.scene.objects if o.type=='MESH' and o.hide_render]),'scene_evidence_matches_all_parts':expected==collections.Counter(o['evidence'] for o in bpy.data.objects if 'evidence' in o),'editable_evidence_matches_parts':expected==collections.Counter(x['evidence'] for x in edit['features']),'material_evidence_matches_palette':collections.Counter(x['evidence'] for x in edit['palette'])==collections.Counter(m['source_evidence'] for m in bpy.data.materials if 'source_evidence' in m)}
r['subtractive_components_identified']=sum(o.get('construction_operation')=='subtract' for o in bpy.data.objects)==sum(x.get('operation')=='subtract' for x in parts)
r['max_vertex_float32_error_mm']=float(np.max(np.abs(v-d['vertices'])))
r['scope_metadata_correct']='No1 warehouse' in o.get('scope','') and 'workshop' not in o.get('scope','')
r['coordinate_metadata_correct']='PDF268/271/272' in o.get('coordinate_frame','')
r['passed']=all(v for k,v in r.items() if k not in ('hidden_editable_components','max_vertex_float32_error_mm'))
(p/'BLEND-QA.json').write_text(json.dumps(r,indent=2));print(r);assert r['passed']
