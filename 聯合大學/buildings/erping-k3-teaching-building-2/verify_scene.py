"""Run: blender -b -P verify_scene.py. Checks exact triangle sets at 1e-5 mm."""
from pathlib import Path
import bpy,struct,hashlib,json,collections
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'scene.blend'))
raw=(P/'model.stl').read_bytes();n=struct.unpack('<I',raw[80:84])[0]
def key(vs):return tuple(sorted(tuple(round(float(c),5) for c in v) for v in vs))
stl=collections.Counter()
for i in range(n):
 a=struct.unpack('<12fH',raw[84+i*50:134+i*50]);stl[key([a[3:6],a[6:9],a[9:12]])]+=1
obj=bpy.data.objects['Printable landmark - actual STL'];obj.data.calc_loop_triangles();blend=collections.Counter()
for t in obj.data.loop_triangles:blend[key([obj.matrix_world@obj.data.vertices[v].co for v in t.vertices])]+=1
same=stl==blend
embedded=any(t.as_string()==(P/'build_model.py').read_text() for t in bpy.data.texts)
report={'passed':same and embedded,'scene_geometry_matches_stl_at_1e_5_mm':same,'source_script_embedded_and_matches':embedded,'stl_triangles':n,'blend_triangles':len(obj.data.loop_triangles),'stl_sha256':hashlib.sha256(raw).hexdigest(),'scene_units':'millimeters; scale_length=0.001','nonprinting_objects':[o.name for o in bpy.data.objects if o!=obj]}
(P/'scene_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report));assert report['passed']
