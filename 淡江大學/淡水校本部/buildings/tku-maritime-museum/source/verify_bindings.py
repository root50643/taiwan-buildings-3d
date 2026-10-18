from pathlib import Path
import json,hashlib,sys
import numpy as np
import trimesh,bpy
P=Path(__file__).resolve().parent.parent
def tri_signature(v):
    values=np.asarray(v,dtype=np.float32)
    return sorted(tuple(sorted(tuple(float(c) for c in xyz) for xyz in tri)) for tri in values)
bpy.ops.wm.open_mainfile(filepath=str(P/'scene.blend'))
meshes=[x for x in bpy.context.scene.objects if x.type=='MESH']
m=trimesh.load_mesh(P/'model.stl',process=False)
assert len(meshes)==1
o=meshes[0];o.data.calc_loop_triangles();v=np.array([list(o.matrix_world@v.co) for v in o.data.vertices]);f=np.array([list(t.vertices) for t in o.data.loop_triangles])
same=tri_signature(m.triangles)==tri_signature(v[f])
bound={'stl_sha256':hashlib.sha256((P/'model.stl').read_bytes()).hexdigest(),'scene_sha256':hashlib.sha256((P/'scene.blend').read_bytes()).hexdigest(),'one_mesh':len(meshes)==1,'scene_matches_stl_float32_triangles':same,'scene_triangles':len(f),'stl_triangles':len(m.faces),'image_datablocks':[x.name for x in bpy.data.images if x.source=='FILE'],'scene_units_scale_length':bpy.context.scene.unit_settings.scale_length,'textures_in_scene':len([x for x in bpy.data.images if x.source=='FILE'])}
# Rebuild to separate temp directory and compare bytes without replacing the candidate.
import subprocess,tempfile
with tempfile.TemporaryDirectory(dir=P/'qa') as d:
    c=subprocess.run([sys.executable,str(P/'source/build_model.py'),'--output',d],capture_output=True,text=True)
    bound['rebuild_returncode']=c.returncode
    bound['rebuild_stdout']=c.stdout
    bound['rebuild_stl_byte_identical']=c.returncode==0 and (Path(d)/'model.stl').read_bytes()==(P/'model.stl').read_bytes()
manifest=json.loads((P/'previews/render-manifest.json').read_text())
bound['preview_manifest_bound_to_current_stl']=manifest['stl_sha256']==bound['stl_sha256']
bound['preview_hash_matches']={x['file']:hashlib.sha256((P/x['file']).read_bytes()).hexdigest()==x['sha256'] for x in manifest['views']}
revision=json.loads((P/'parameters.json').read_text())['revision']
(P/'qa/publication').mkdir(exist_ok=True)
(P/'qa/publication/rebuild-scene-preview-binding.json').write_text(json.dumps(bound,indent=2)+'\n')
print(json.dumps(bound))
assert same and bound['rebuild_stl_byte_identical'] and bound['preview_manifest_bound_to_current_stl'] and all(bound['preview_hash_matches'].values())
