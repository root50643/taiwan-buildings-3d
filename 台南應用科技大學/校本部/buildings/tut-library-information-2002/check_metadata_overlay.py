"""Read-only saved Blend geometry and relative render-path verification."""
from pathlib import Path
import argparse,subprocess,tempfile,json,hashlib,numpy as np,trimesh
O=Path(__file__).parent;p=argparse.ArgumentParser();p.add_argument('--stl',default=str(O/'model.stl'));a=p.parse_args();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geom(t):return hashlib.sha256(json.dumps(sorted(tuple(sorted(tuple(round(float(x),5) for x in v) for v in f)) for f in t),separators=(',',':')).encode()).hexdigest()
with tempfile.TemporaryDirectory() as td:
 f=Path(td)/'mesh.json'
 expr="import bpy,json;from pathlib import Path;o=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(o)==1;o=o[0];Path("+repr(str(f))+").write_text(json.dumps({'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'render_path':bpy.context.scene.render.filepath}))"
 subprocess.run(['blender','-b',str(O/'scene.blend'),'-t','2','--python-expr',expr],check=True,capture_output=True)
 j=json.loads(f.read_text());m=trimesh.load(a.stl,process=False);sg=geom(m.triangles);bg=geom(np.array(j['vertices'])[j['faces']]);checks={'geometry_matches_original_stl':sg==bg,'relative_render_path':j['render_path']=='//previews/west-detail.png'}
 r={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(a.stl),'blend_sha256':sha(O/'scene.blend'),'stl_geometry_sha256':sg,'blend_geometry_sha256':bg,'render_path':j['render_path'],'method':'Original STL process=False; saved Blend mesh only; no geometry changes or repairs'};(O/'metadata-overlay-check.json').write_text(json.dumps(r,indent=2));assert r['passed'];print(r)
