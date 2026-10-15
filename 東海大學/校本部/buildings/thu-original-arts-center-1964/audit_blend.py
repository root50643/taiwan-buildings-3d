"""Load the saved scene, compare its actual mesh triangles to the delivered STL."""
import bpy, json, struct, hashlib, sys
from pathlib import Path
import numpy as np
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if len(objects)!=1:
    (root/'qa-blend.json').write_text(json.dumps({'passed':False,'mesh_objects':len(objects),'failure':'expected_exactly_one_mesh_object'},indent=2)+'\n')
    raise SystemExit(1)
obj=objects[0];me=obj.data;me.calc_loop_triangles()
v=np.array([obj.matrix_world@p.co for p in me.vertices],dtype=np.float32)
f=np.array([t.vertices for t in me.loop_triangles]);tri=v[f]
data=(root/'model.stl').read_bytes();n=struct.unpack('<I',data[80:84])[0];records=np.frombuffer(data,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
def canonical(t):
    t=np.array(t,dtype='<f4',copy=True)
    for i,vs in enumerate(t):
        a=min(range(3),key=lambda j:tuple(vs[j]));t[i]=np.roll(vs,-a,axis=0)
    order=np.lexsort(tuple(t.reshape(-1,9)[:,i] for i in range(8,-1,-1)))
    return t[order].tobytes()
a=canonical(tri);b=canonical(records['v'])
report={'passed':a==b,'mesh_objects':len(objects),'triangles':len(tri),'dimensions_mm':(v.max(axis=0)-v.min(axis=0)).tolist(),'canonical_oriented_triangle_bytes_equal_to_STL':a==b,'mesh_triangle_sha256':hashlib.sha256(a).hexdigest(),'stl_sha256':hashlib.sha256(data).hexdigest(),'render_engine':bpy.context.scene.render.engine,'denoising':bpy.context.scene.cycles.use_denoising,'resolution':list((bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y))}
(root/'qa-blend.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

raise SystemExit(0 if report['passed'] else 1)
