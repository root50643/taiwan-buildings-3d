"""Check six delivered print STLs against the saved assembly scene; no render."""
from pathlib import Path
import argparse,hashlib,json,struct
from collections import Counter
import bpy
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return min(tuple(v[i:]+v[:i]) for i in range(3))
def triangles(stl):
    b=stl.read_bytes();n=struct.unpack_from('<I',b,80)[0];result=Counter()
    for i in range(n):
        v=struct.unpack_from('<12fH',b,84+50*i)[3:12]
        result[canonical([tuple(v[j:j+3]) for j in [0,3,6]])]+=1
    return result
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'qa/render-scene-validation.json');a=ap.parse_args()
    report=json.loads((ROOT/'models/build-report.json').read_text(encoding='utf8'))
    manifest=json.loads((ROOT/'previews/render-manifest.json').read_text(encoding='utf8'))
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;parts=[];objects=[]
    for row in report['parts']:
        stl=ROOT/'models'/row['stl'];o=bpy.data.objects[row['id']];objects.append(o)
        actual=Counter()
        for f in o.data.polygons:
            assert len(f.vertices)==3
            actual[canonical([tuple(o.data.vertices[i].co) for i in f.vertices])]+=1
        parts.append({'id':row['id'],'stl_sha256':digest(stl),'sha_matches_build_report':digest(stl)==row['stl_sha256'],
            'local_oriented_triangle_multiset_equals_supplied_print_stl':actual==triangles(stl),
            'scene_assembly_matrix_matches_declared':all(o.matrix_world[i][j]==row['transform_print_to_assembled'][i][j] for i in range(4) for j in range(4)),
            'no_modifiers_or_constraints':not o.modifiers and not o.constraints})
    framing=[]
    for view in manifest['views']:
        name=view['name']
        for i,(o,row) in enumerate(zip(objects,report['parts'])):
            o.matrix_world=Matrix(row['transform_print_to_assembled'])
            if name=='exploded':o.location.z+=12*row['horizontal_band']
            if name=='print-orientations':
                o.matrix_world=Matrix.Identity(4);b=row['print_bounds_mm']
                o.location=((-90,90)[i%2]-(b[0][0]+b[1][0])/2,(140,0,-140)[i//2]-(b[0][1]+b[1][1])/2,0)
        scene.camera.location=view['camera'];scene.camera.data.ortho_scale=view['ortho_scale']
        aim(scene.camera,{'assembled':(0,0,22),'exploded':(0,0,48),'print-orientations':(0,0,0)}[name]);bpy.context.view_layer.update()
        p=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for o in objects for v in o.data.vertices]
        bounds=[[min(getattr(q,k) for q in p),max(getattr(q,k) for q in p)] for k in ['x','y']]
        framing.append({'view':name,'projected_xy_bounds':bounds,'whole_six_part_geometry_inside_frame':all(0<=lo<=hi<=1 for lo,hi in bounds),'png_hash_matches':digest(ROOT/'previews'/(name+'.png'))==view['sha256']})
    result={'parts':parts,'framing':framing,'scene_sha256':digest(ROOT/'scene.blend'),'scene_hash_matches_manifest':digest(ROOT/'scene.blend')==manifest['scene_sha256'],
            'image_datablocks':[x.name for x in bpy.data.images],
            'unit_metadata':{'system':scene.unit_settings.system,'length_unit':scene.unit_settings.length_unit,'scale_length_stored_float32':scene.unit_settings.scale_length,'equals_binary32_of_0p001':scene.unit_settings.scale_length==struct.unpack('<f',struct.pack('<f',.001))[0]},
            'scope':'Scene and image identity/framing only; no slicing or physical print in this checker'}
    result['pass']=all(all(v is True for k,v in p.items() if k not in ['id','stl_sha256']) for p in parts) and all(f['whole_six_part_geometry_inside_frame'] and f['png_hash_matches'] for f in framing) and result['scene_hash_matches_manifest']
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result));raise SystemExit(0 if result['pass'] else 1)
if __name__=='__main__':main()
