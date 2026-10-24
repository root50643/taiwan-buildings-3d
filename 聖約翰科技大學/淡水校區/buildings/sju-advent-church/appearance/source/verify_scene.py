"""Independently open delivered Blend, verify all coordinates/materials, rerender front."""
import bpy,sys,json,hashlib,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from geometry_io import read_original,triangle_coordinate_sha
OUT=HERE.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'scene.blend'))
objects=[o for o in bpy.data.objects if o.type=='MESH'];assert len(objects)==1
obj=objects[0];assert len(obj.modifiers)==0
assert all(abs(obj.matrix_world[i][j]-(1 if i==j else 0))<1e-12 for i in range(4) for j in range(4))
v=[tuple(x.co) for x in obj.data.vertices];f=[tuple(x.vertices) for x in obj.data.polygons]
ov,of=read_original(OUT.parent/'model.stl');ann=json.loads((OUT/'face-materials.json').read_text());manifest=json.loads((OUT/'material-manifest.json').read_text())
assert v==ov and f==[tuple(x) for x in of]
assert [x.material_index for x in obj.data.polygons]==ann['material_indices']
assert [m.name for m in obj.data.materials]==[m['id'] for m in manifest['materials']]
assert [x.value for x in obj.data.attributes['original_stl_face_id'].data]==list(range(len(f)))
images=[i.name for i in bpy.data.images if i.source=='FILE' and i.filepath];assert not images
assert abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-10
scene=bpy.context.scene;scene.render.filepath=str(OUT/'previews'/'.reopened-front.png');bpy.ops.render.render(write_still=True)
p=OUT/'previews'/'.reopened-front.png';raw=p.read_bytes();clean=raw[:8];i=8
while i<len(raw):
    n=struct.unpack('>I',raw[i:i+4])[0]
    if raw[i+4:i+8] not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:clean+=raw[i:i+12+n]
    i+=12+n
assert clean==(OUT/'previews'/'front.png').read_bytes(),'Reopened Blend front differs from delivered preview'
p.unlink()
report={'pass':True,'opened_delivered_scene':True,'triangle_count':len(f),'vertex_count':len(v),'exact_original_coordinates_and_triangle_order':True,'exact_material_indices':True,'original_face_ids_exact':True,'mesh_objects':1,'modifiers':0,'external_image_paths':images,'scale_length':scene.unit_settings.scale_length,'reopened_front_png_exact':True,'triangle_coordinate_sha256':triangle_coordinate_sha(v,f)}
(OUT/'blend-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
