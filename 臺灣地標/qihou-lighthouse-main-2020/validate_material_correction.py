#!/usr/bin/env python3
"""Verify exact geometry-fixed, three-component source-specific material correction.
The baseline contains authored hashes and parameters only, never source pixels.
"""
import argparse,pathlib,json,hashlib
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();r=a.out;(r/'qa').mkdir(parents=True,exist_ok=True);src=pathlib.Path(__file__).resolve().parent
base=json.loads((src/'material-correction-baseline.json').read_text());params=json.loads((src/'parameters.json').read_text())
with np.load(r/'mesh-data.npz')as archive:D={k:archive[k].copy()for k in ['vertices','faces','materials','component_ids']}
parts=json.loads((r/'construction-parts.json').read_text());info=json.loads((r/'editable-parts.json').read_text());palette=info['palette'];ids={q['id']:i for i,q in enumerate(palette)}
h=lambda b:hashlib.sha256(b).hexdigest()
def ah(v):return h(np.ascontiguousarray(v).tobytes())
def geometry_hash(part):return h(np.ascontiguousarray(part['vertices'],dtype=np.float32).tobytes()+np.ascontiguousarray(part['faces'],dtype=np.uint32).tobytes())
assert {k:params[k]for k in base['original_parameters']}==base['original_parameters']
assert set(params)-set(base['original_parameters'])=={'component_material_overrides','material_revision_note'}
changes=base['allowed_component_material_changes'];assert set(changes)=={'Two tier diagonal lantern frame','Dome lower projecting rim','Lantern base cornice 184.4'}
assert params['component_material_overrides']=={n:c['after']for n,c in changes.items()}
assert [{'id':q['id'],'hex':q['hex']}for q in palette]==base['original_palette'],'No palette-wide repaint is allowed'
for k in ['vertices','faces']:
 expected=base['original_mesh_arrays'][k];assert str(D[k].dtype)==expected['dtype']and list(D[k].shape)==expected['shape']and ah(D[k])==expected['sha256'],(k,'geometry changed')
assert h((r/'qihou-lighthouse-main-2020.stl').read_bytes())==base['original_stl_sha256'],'STL bytes changed'
assert len(parts)==len(base['components'])==len(info['features'])==79
before=[];after=[];changed=[]
for j,(old,new,metadata)in enumerate(zip(base['components'],parts,info['features'])):
 assert new['name']==old['name']==metadata['name'];assert geometry_hash(new)==old['geometry_sha256'],(new['name'],'component geometry changed')
 b=old['material_index'];expect=ids[changes[new['name']]['after']]if new['name']in changes else b
 assert new['material']==expect and metadata['material']==palette[expect]['id'],new['name'];before.append(b);after.append(expect)
 if expect!=b:
  assert palette[b]['id']==changes[new['name']]['before']
  assert 'PDF3 lower completed photo 2020-08-03'in metadata['evidence']
  changed.append({'component_index':j,'name':new['name'],'before':palette[b]['id'],'after':palette[expect]['id'],'before_hex':palette[b]['hex'],'after_hex':palette[expect]['hex'],'geometry_unchanged':True})
assert len(changed)==3
owner=D['component_ids'];assert owner.shape==D['materials'].shape and owner.min()>=0 and owner.max()<79
old_face=np.asarray(before,dtype=np.int32)[owner];expected_face=np.asarray(after,dtype=np.int32)[owner]
assert ah(old_face)==base['original_mesh_arrays']['materials']['sha256'],'Ownership must reproduce every predecessor face material exactly'
assert np.array_equal(D['materials'],expected_face),'Unexpected final face material override'
mask=D['materials']!=old_face;allowed_ids={x['component_index']for x in changed};assert set(owner[mask])==allowed_ids
for q in changed:q['changed_final_triangles']=int(np.sum(mask&(owner==q['component_index'])))
assert np.array_equal(D['materials'][~mask],old_face[~mask])
controls=[]
for q in changed:
 bad=D['materials'].copy();idx=int(np.flatnonzero(owner==q['component_index'])[0]);bad[idx]=old_face[idx]
 assert not np.array_equal(bad,expected_face);controls.append({'fixture':'restore_wrong_predecessor_color_on_one_face','component':q['name'],'detected':True})
v=D['vertices'].copy();v[0,0]+=.125;assert ah(v)!=base['original_mesh_arrays']['vertices']['sha256'];controls.append({'fixture':'move_geometry_vertex','detected':True})
report={'all_pass':True,'geometry_byte_fixed':True,'stl_sha256':base['original_stl_sha256'],'vertices_and_faces_exact_predecessor_dtype_shape_and_sha256':True,'all_79_component_geometry_hashes_unchanged':True,'geometry_parameters_unchanged':True,'palette_colors_unchanged':True,'exactly_three_named_component_materials_changed':True,'per_triangle_original_component_ownership_verified_against_predecessor_material_hash':True,'unrelated_final_face_materials_unchanged':True,'final_triangles':len(D['faces']),'changed_final_triangles':int(mask.sum()),'component_changes':changed,'negative_controls':controls,'source':'P01 PDF3 lower completed photograph dated 2020-08-03','source_interpretation':'Pale diagonal lantern lattice and upper/mid rings plus upper projecting rim; dark lower glazing band below, dark dome and railing retained. Exact lower-band width and calibrated color are not claimed.','original_manifest_sha256':base['original_manifest_sha256'],'source_pixels_included':False}
(r/'qa/material-correction-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
