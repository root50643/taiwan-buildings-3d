"""Reopen, remove UI browser directory metadata, verify exact scene vs STL mesh.
Blender background --python source/verify_scene.py. No geometry is repaired.
"""
from pathlib import Path
import bpy,json,hashlib,struct
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene.blend'))
 bpy.context.preferences.filepaths.save_version=0
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
 scene=bpy.context.scene;scene.render.filepath='//previews/front.png'
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'),compress=False)
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene.blend'))
 scene=bpy.context.scene;data=json.loads((ROOT/'assembly.json').read_text('utf-8'));checks=[]
 for p in data['parts']:
  ob=bpy.data.objects[p['id']];raw=(ROOT/p['stl']).read_bytes();n=struct.unpack_from('<I',raw,80)[0]
  points=[];T=Matrix(p['assembly_transform'])
  for i in range(n):
   vs=struct.unpack_from('<12fH',raw,84+50*i)[3:12]
   for j in range(3):points.append(tuple(T@Vector(vs[j*3:j*3+3])))
  a=sorted(set(tuple(round(x,5) for x in v) for v in points));b=sorted(set(tuple(round(x,5) for x in (ob.matrix_world@v.co)) for v in ob.data.vertices))
  dims=[v*scene.unit_settings.scale_length*1000 for v in ob.dimensions]
  checks.append({'id':p['id'],'stl_sha256':sha(ROOT/p['stl']),'scene_vertex_set_matches_transformed_stl_1e-5mm':a==b,'scene_triangle_count':len(ob.data.polygons),'stl_triangle_count':n,'physical_extent_mm':dims,'stl_extent_mm':p['bounds_print_mm'],'physical_extent_max_error_mm':max(abs(dims[j]-p['bounds_print_mm'][j]) for j in range(3)),'material_face_counts':{m.name:sum(f.material_index==i for f in ob.data.polygons) for i,m in enumerate(ob.data.materials)}})
 passed=all(x['scene_vertex_set_matches_transformed_stl_1e-5mm'] and x['scene_triangle_count']==x['stl_triangle_count'] and x['physical_extent_max_error_mm']<1e-4 for x in checks)
 report={'scene_sha256':sha(ROOT/'scene.blend'),'assembly_manifest_sha256':sha(ROOT/'assembly.json'),'reopened_saved_scene':True,'unit_system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,'unit_formula':'Blender extent BU * .001 m/BU *1000 mm/m = STL mm extent','parts':checks,'pass':passed,'private_UI_file_browser_directory_reset':True,'physical_print_or_fit_tested':False,'four_nozzle_printing_verified':False}
 (ROOT/'qa/scene-independent-report.json').write_text(json.dumps(report,indent=2)+'\n','utf-8');print(json.dumps({'pass':passed,'parts':len(checks),'scene_sha256':report['scene_sha256']}))
if __name__=='__main__':main()
