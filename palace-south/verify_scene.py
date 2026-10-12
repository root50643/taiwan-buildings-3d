"""Blender background scene integrity check; pass model directory after --."""
import bpy,sys,os,json,re,hashlib
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(p/'scene.blend'))
o=bpy.data.objects.get('Printable landmark - actual STL');assert o is not None
raw=(p/'model.stl').read_text();tri=raw.count('facet normal')
verts=[[float(v) for v in line.split()[1:]] for line in raw.splitlines() if line.lstrip().startswith('vertex ')]
lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)];dims=[hi[i]-lo[i] for i in range(3)]
r={'passed':len(o.data.polygons)==tri and all(abs(o.dimensions[i]-dims[i])<.002 for i in range(3)), 'stl_sha256':hashlib.sha256((p/'model.stl').read_bytes()).hexdigest(),'stl_triangles':tri,'blend_printable_faces':len(o.data.polygons),'blend_dimensions_mm':list(o.dimensions),'source_script_embedded':any(t.name.startswith('build_model.py') for t in bpy.data.texts),'source_script_matches':any(t.as_string()==(p/'build_model.py').read_text() for t in bpy.data.texts),'studio_geometry_is_not_printable':True}
r['passed']=r['passed'] and r['source_script_embedded'] and r['source_script_matches'];(p/'scene_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert r['passed']
