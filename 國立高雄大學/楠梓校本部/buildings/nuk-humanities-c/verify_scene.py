#!/usr/bin/env python3
import bpy,pathlib,numpy as np,json,sys
r=pathlib.Path(__file__).resolve().parent;d=np.load(r/'mesh-data.npz');bpy.ops.wm.open_mainfile(filepath=str(r/'scene.blend'),load_ui=False,use_scripts=False)
s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH' and not o.hide_render];assert len(obs)==1;ob=obs[0]
v=np.array([tuple(q.co)for q in ob.data.vertices],dtype=np.float32);f=np.array([tuple(q.vertices)for q in ob.data.polygons]);mi=np.array([q.material_index for q in ob.data.polygons]);assert np.array_equal(v,d['vertices']) and np.array_equal(f,d['faces']) and np.array_equal(mi,d['materials'])
assert len(bpy.data.texts)==0;assert not [x for x in bpy.data.images if x.source=='FILE'];assert len(ob.data.materials)==7;assert abs(s.unit_settings.scale_length-.001)<1e-8
palette=json.loads((r/'editable-parts.json').read_text())['palette'];err=[]
for m,p in zip(ob.data.materials,palette):
 c=[int(p['hex'][i:i+2],16)/255 for i in (1,3,5)];c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c];err.append(float(np.max(np.abs(np.array(m.diffuse_color[:3])-c))))
assert max(err)<1e-6;hidden=[o for o in s.objects if o.type=='MESH' and o.hide_render];assert len(hidden)==len(json.loads((r/'construction-parts.json').read_text()))
report={'visible_mesh_objects':1,'editable_hidden_authored_components':len(hidden),'exact_vertices_faces_materials_vs_npz':True,'palette_materials':7,'max_linear_material_color_error':max(err),'external_file_images':0,'embedded_script_texts':0,'units':'millimetres','separate_pre_union_parts_not_print_mesh':True};(r/'qa/scene-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
