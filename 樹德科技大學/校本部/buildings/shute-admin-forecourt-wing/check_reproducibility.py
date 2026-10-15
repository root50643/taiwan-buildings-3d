"""Independent deterministic rebuild, saved/reopened Blend and actual-STL renders."""
from pathlib import Path
import tempfile,subprocess,shutil,json,hashlib,os,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
env={**os.environ,'MALLOC_ARENA_MAX':'2','LP_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
checks={};views=[]
with tempfile.TemporaryDirectory(prefix='shute-repro-') as td:
 T=Path(td);shutil.copy2(R/'build_model.py',T/'build_model.py')
 subprocess.run([sys.executable,str(T/'build_model.py')],check=True,capture_output=True)
 checks['independent_rebuilt_stl_sha_identical']=sha(R/'model.stl')==sha(T/'model.stl')
 assert checks['independent_rebuilt_stl_sha_identical']
 # Reopen the exact saved Blend, not the in-memory source scene.
 probe=T/'probe_blend.py';probe.write_text('''import bpy,struct,json,sys\nfrom pathlib import Path\nr=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(r/'scene.blend'))\nobjs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1\no=objs[0];assert not o.modifiers;o.data.calc_loop_triangles()\nwith (r/'blend_triangles.bin').open('wb') as f:\n for q in o.data.loop_triangles:\n  for i in q.vertices:f.write(struct.pack('<ddd',*(o.matrix_world@o.data.vertices[i].co)))\n(r/'blend_meta.json').write_text(json.dumps({'mesh_count':len(objs),'triangles':len(o.data.loop_triangles),'units':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length,'version':bpy.app.version_string}))\n''')
 shutil.copy2(R/'scene.blend',T/'scene.blend')
 subprocess.run(['/usr/bin/blender','-b','--factory-startup','-t','1','--python-exit-code','1','-P',str(probe),'--',str(T)],check=True,env=env,capture_output=True)
 meta=json.loads((T/'blend_meta.json').read_text());a=np.fromfile(T/'blend_triangles.bin',dtype='<f8').reshape(-1,3,3)
 raw=(R/'model.stl').read_bytes();n=int.from_bytes(raw[80:84],'little');b=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attribute','<u2')]),count=n)['v'].astype(float)
 def canonical(t):
  result=[]
  for tri in t:
   q=[tuple(map(float,p))for p in tri];result.append(min(tuple(q[i:]+q[:i])for i in range(3)))
  return sorted(result)
 checks['saved_reopened_blend_exact_oriented_triangles']=canonical(a)==canonical(b)
 checks['saved_blend_one_mesh_mm_units']=meta['mesh_count']==1 and meta['units']=='METRIC' and abs(meta['scale_length']-.001)<1e-9
 assert all(checks.values())
 shutil.copy2(R/'render_preview.py',T/'render_preview.py')
 subprocess.run(['/usr/bin/blender','-b','--factory-startup','-t','1','--python-exit-code','1','-P',str(T/'render_preview.py')],check=True,env=env,capture_output=True)
 for name in ['front','rear','elevation','top']:
  p=R/'previews'/f'{name}.png';q=T/'previews'/p.name;im=np.asarray(Image.open(p).convert('RGBA'));new=np.asarray(Image.open(q).convert('RGBA'))
  ck={'dimensions_800x640':im.shape==(640,800,4),'nonblank':bool(np.ptp(im[:,:,:3])>20),'independent_render_pixels_identical':bool(np.array_equal(im,new)),'independent_png_bytes_identical':p.read_bytes()==q.read_bytes()}
  views.append({'view':name,'path':str(p.relative_to(R)),'sha256':sha(p),'checks':ck});assert all(ck.values()),(name,ck)
checks['four_actual_stl_renders_reproduce']=len(views)==4 and all(all(v['checks'].values())for v in views)
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'blend_sha256':sha(R/'scene.blend'),'build_script_sha256':sha(R/'build_model.py'),'render_script_sha256':sha(R/'render_preview.py'),'blend_metadata':meta,'views':views,'method':'Independent subprocess STL generation in an empty temporary directory; exact cyclic orientation-preserving triangle comparison after reopening the saved Blend; independently rerendered actual STL, pixel and PNG byte equality.'}
(R/'reproducibility.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['passed']
