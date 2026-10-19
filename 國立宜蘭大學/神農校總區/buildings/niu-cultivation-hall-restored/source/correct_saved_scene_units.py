"""Apply only explicit mm scene units to an existing scene; keep mesh/object data intact."""
from pathlib import Path
import json,hashlib
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[1];SCENE=ROOT/'models/v1/scene.blend';OUT=ROOT/'qa/unit-correction';OUT.mkdir(parents=True,exist_ok=True)
def snapshot():
    scene=bpy.context.scene;u=scene.unit_settings
    models=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('NIU_Cultivation')]
    assert len(models)==1
    o=models[0];v=np.array([list(q.co) for q in o.data.vertices],dtype='<f4');f=np.array([tuple(p.vertices) for p in o.data.polygons],dtype='<i4')
    return {'scene_units':{'system':u.system,'scale_length':u.scale_length,'length_unit':u.length_unit},'mesh_coordinate_sha256':hashlib.sha256(v.tobytes()).hexdigest(),'mesh_face_indices_sha256':hashlib.sha256(f.tobytes()).hexdigest(),'object_scale':list(o.scale),'object_matrix':[list(r) for r in o.matrix_world],'model_dimensions_coordinate_units':list(o.dimensions),'material_indices':[p.material_index for p in o.data.polygons]}
old_sha=hashlib.sha256(SCENE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SCENE));before=snapshot()
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=0.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE));bpy.ops.wm.open_mainfile(filepath=str(SCENE));after=snapshot()
checks={k:before[k]==after[k] for k in ['mesh_coordinate_sha256','mesh_face_indices_sha256','object_scale','object_matrix','model_dimensions_coordinate_units','material_indices']}
result={'previous_scene_sha256':old_sha,'corrected_scene_sha256':hashlib.sha256(SCENE.read_bytes()).hexdigest(),'before':before,'after':after,'unchanged_checks':checks,'scope':'Only scene unit settings assigned; no mesh or object scaling. Save/reopen verified mesh, transform and material indices; not a claim that every Blender datablock or unused material is byte-identical.','passed':all(checks.values()) and after['scene_units']['system']=='METRIC' and after['scene_units']['length_unit']=='MILLIMETERS' and abs(after['scene_units']['scale_length']-0.001)<1e-9}
(OUT/'saved-scene-unit-correction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['before','after']},indent=2));assert result['passed']
