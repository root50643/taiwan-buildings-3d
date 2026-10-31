from pathlib import Path
import bpy,numpy as np,json
p=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(p/'scene.blend'));d=np.load(p/'mesh-data.npz');o=bpy.data.objects['NTHU Renxu pavilion'];v=np.array([x.co[:] for x in o.data.vertices]);f=np.array([x.vertices[:] for x in o.data.polygons]);mi=np.array([x.material_index for x in o.data.polygons]);checks={'vertices_equal':bool(np.allclose(v,d['vertices'],rtol=0,atol=1e-5)),'faces_equal':bool(np.array_equal(f,d['faces'])),'materials_equal':bool(np.array_equal(mi,d['materials'])),'no_images_embedded':len([i for i in bpy.data.images if i.type=='IMAGE'])==0};r={'checks':checks,'passed':all(checks.values())};(p/'BLEND-QA.json').write_text(json.dumps(r,indent=2));print(r);assert r['passed']

from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
sc=bpy.context.scene;cam=sc.camera;fr={}
for view in json.loads((p/'render-manifest.json').read_text())['views']:
 cam.location=view['camera'];cam.rotation_euler=(Vector(view['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=view['ortho_scale'];bpy.context.view_layer.update();xy=np.array([world_to_camera_view(sc,cam,o.matrix_world@x.co)[:2]for x in o.data.vertices]);lo=xy.min(0);hi=xy.max(0);full=bool((lo>=.01).all() and (hi<=.99).all());fr[view['name']]={'bounds_normalized':[lo.tolist(),hi.tolist()],'full_mesh_with_1pct_margin':full,'detail_crop_allowed':view['name']=='entry_detail'}
r={'views':fr,'passed':all(d['full_mesh_with_1pct_margin'] or d['detail_crop_allowed']for d in fr.values())};(p/'FRAMING-QA.json').write_text(json.dumps(r,indent=2));print(r);assert r['passed']
