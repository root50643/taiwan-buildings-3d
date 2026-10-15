"""Independent deterministic rebuild and exact saved-Blend / actual-STL render binding."""
from pathlib import Path
import tempfile,subprocess,shutil,json,hashlib,os,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
env={**os.environ,'MALLOC_ARENA_MAX':'2','LP_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
checks={};views=[]
with tempfile.TemporaryDirectory(prefix='nycu-repro-') as td:
 D=Path(td)
 for name in ['build_model.py','parameters.json','render_model.py']:shutil.copy2(R/name,D/name)
 subprocess.run([sys.executable,str(D/'build_model.py')],check=True,capture_output=True)
 checks['independent_rebuilt_stl_sha_identical']=sha(R/'model.stl')==sha(D/'model.stl');assert checks['independent_rebuilt_stl_sha_identical']
 probe=D/'probe_blend.py';probe.write_text('''import bpy,struct,json,sys\nfrom pathlib import Path\nr=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(r/'scene.blend'))\nobjects=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'stl_sha256' in o];assert len(objects)==1\no=objects[0];assert not o.modifiers;o.data.calc_loop_triangles()\nwith (r/'blend_triangles.bin').open('wb') as f:\n for q in o.data.loop_triangles:\n  for i in q.vertices:f.write(struct.pack('<ddd',*(o.matrix_world@o.data.vertices[i].co)))\n(r/'blend_meta.json').write_text(json.dumps({'actual_stl_mesh_count':len(objects),'render_ground_mesh_count':len([x for x in bpy.context.scene.objects if x.type=='MESH' and 'stl_sha256' not in x]),'triangles':len(o.data.loop_triangles),'stl_tag':o['stl_sha256'],'units':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length,'blender':bpy.app.version_string}))\n''')
 shutil.copy2(R/'scene.blend',D/'scene.blend')
 subprocess.run(['/usr/bin/blender','-b','--factory-startup','-t','1','--python-exit-code','1','--python',str(probe),'--',str(D)],check=True,env=env,capture_output=True)
 meta=json.loads((D/'blend_meta.json').read_text());a=np.fromfile(D/'blend_triangles.bin',dtype='<f8').reshape(-1,3,3)
 raw=(R/'model.stl').read_bytes();n=int.from_bytes(raw[80:84],'little');b=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attribute','<u2')]),count=n)['v'].astype(float)
 def canonical(t):
  result=[]
  for tri in t:
   q=[tuple(map(float,p)) for p in tri];result.append(min(tuple(q[i:]+q[:i])for i in range(3)))
  return sorted(result)
 checks['saved_reopened_blend_exact_oriented_triangles']=canonical(a)==canonical(b)
 checks['saved_blend_one_actual_stl_mesh_mm_units']=meta['actual_stl_mesh_count']==1 and meta['units']=='METRIC' and abs(meta['scale_length']-.001)<1e-9 and meta['stl_tag']==sha(R/'model.stl')
 assert all(checks.values())
 subprocess.run(['/usr/bin/blender','-b','--factory-startup','-t','1','--python-exit-code','1','--python',str(D/'render_model.py')],check=True,env=env,capture_output=True)
 for name in ['front','rear','top','elevation','northeast-detail']:
  p=R/(name+'.png');q=D/p.name;im=np.asarray(Image.open(p).convert('RGBA'));new=np.asarray(Image.open(q).convert('RGBA'))
  ck={'dimensions_800x640':im.shape==(640,800,4),'nonblank':bool(np.ptp(im[:,:,:3])>20),'independent_render_pixels_identical':bool(np.array_equal(im,new)),'independent_png_bytes_identical':p.read_bytes()==q.read_bytes()}
  views.append({'view':name,'path':p.name,'sha256':sha(p),'checks':ck});assert all(ck.values()),(name,ck)
checks['five_actual_stl_renders_reproduce']=len(views)==5 and all(all(v['checks'].values())for v in views)
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'blend_sha256':sha(R/'scene.blend'),'build_script_sha256':sha(R/'build_model.py'),'parameters_sha256':sha(R/'parameters.json'),'render_script_sha256':sha(R/'render_model.py'),'blend_metadata':meta,'views':views,'exact_oriented_triangle_sha256':hashlib.sha256(np.array(canonical(b),dtype='<f8').tobytes()).hexdigest(),'method':'Independent subprocess build in empty temporary directory; original exact-coordinate oriented triangles compared with saved/reopened Blend. Separate render ground is explicitly excluded from printable geometry. Independent actual-STL rerender pixels and PNG bytes must both match.'}
(R/'reproducibility.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
