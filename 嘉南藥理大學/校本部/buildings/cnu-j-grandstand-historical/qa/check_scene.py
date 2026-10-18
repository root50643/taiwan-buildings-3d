"""Validate actual scene mesh against the delivered assembly STL, without rendering."""
from pathlib import Path
import json,hashlib
import bpy,numpy as np,trimesh
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
objects=[o for o in bpy.data.objects if o.type=='MESH']
assert len(objects)==1
o=objects[0]
a=np.array([o.matrix_world@v.co for v in o.data.vertices])
m=trimesh.load(R/'model.stl',force='mesh',process=True)
def nearest(v,w):
    # Keep original floats and the original 1e-5 tolerance. Rounding before
    # sorting changes row correspondence at decimal bin boundaries.
    indices=[];dist=[]
    for start in range(0,len(v),128):
        d=np.linalg.norm(v[start:start+128,None,:]-w[None,:,:],axis=2)
        ix=np.argmin(d,axis=1);indices.extend(ix.tolist())
        dist.extend(d[np.arange(len(ix)),ix].tolist())
    return np.array(indices),max(dist)
ix,forward=nearest(a,m.vertices);_,reverse=nearest(m.vertices,a)
same=len(a)==len(m.vertices) and max(forward,reverse)<=1e-5
scene_faces=np.sort(np.array([[ix[i] for i in f.vertices] for f in o.data.polygons]),axis=1)
stl_faces=np.sort(m.faces,axis=1)
face_set_equal={tuple(f) for f in scene_faces}=={tuple(f) for f in stl_faces}
external_images=[i.name for i in bpy.data.images if i.source=='FILE' and i.filepath]
external_libraries=[lib.name for lib in bpy.data.libraries]
absolute_file_browsers=[]
for s in bpy.data.screens:
    for ar in s.areas:
        for sp in ar.spaces:
            if sp.type=='FILE_BROWSER' and sp.params:
                path=sp.params.directory.decode(errors='replace')
                if not path.startswith('//'):absolute_file_browsers.append(path)
report={'scene_sha256':hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest(),
        'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),
        'mesh_objects':len(objects),'scene_vertices':len(a),'stl_vertices':len(m.vertices),
        'scene_faces':len(o.data.polygons),'stl_faces':len(m.faces),
        'coordinate_tolerance_mm':1e-5,'same_unique_coordinates':bool(same),
        'method':'Bidirectional nearest-coordinate matching in original coordinates; exact mapped triangle index sets',
        'maximum_nearest_error_mm':max(forward,reverse),'mapped_triangle_set_equal':face_set_equal,
        'external_file_images':external_images,'external_libraries':external_libraries,
        'absolute_file_browser_paths':absolute_file_browsers,
        'render_path_is_relative':bpy.context.scene.render.filepath.startswith('//'),
        'pass':bool(same and face_set_equal and len(o.data.polygons)==len(m.faces) and not external_images and not external_libraries and not absolute_file_browsers and bpy.context.scene.render.filepath.startswith('//'))}
(R/'qa/scene-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
assert report['pass'],report
print(json.dumps(report))
