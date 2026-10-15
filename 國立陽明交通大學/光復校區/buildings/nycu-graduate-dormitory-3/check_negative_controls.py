"""Prove fail-closed raw and individual/combined invalid-polygon rejection."""
from pathlib import Path
import tempfile,subprocess,sys,shutil,json,hashlib
R=Path(__file__).resolve().parent;checks={};rows=[]
with tempfile.TemporaryDirectory(prefix='nycu-negative-') as td:
 T=Path(td);shutil.copy2(R/'model.stl',T/'model.stl')
 raw=bytearray((T/'model.stl').read_bytes());raw[96:108],raw[108:120]=raw[108:120],raw[96:108];(T/'model.stl').write_bytes(raw)
 shutil.copy2(R/'check_raw_mesh.py',T/'check_raw_mesh.py')
 p=subprocess.run([sys.executable,str(T/'check_raw_mesh.py')],capture_output=True,text=True);checks['flipped_original_triangle_rejected']=p.returncode!=0 and 'AssertionError' in p.stderr
 shutil.copy2(R/'model.stl',T/'model.stl');source=(R/'check_component_detail.py').read_text()
 for name,needle,insert in [('short_original_loop','  assert len(loop)>2,','  loop=loop[:2]\n'),('invalid_individual_polygon','   assert a==seed and p.is_valid,','   p=Polygon([(0,0),(1,1),(1,0),(0,1)])\n'),('invalid_combined_polygon',' assert shape.is_valid,',' shape=Polygon([(0,0),(1,1),(1,0),(0,1)])\n')]:
  assert source.count(needle)==1;test=T/(name+'.py');test.write_text(source.replace(needle,insert+needle));p=subprocess.run([sys.executable,str(test)],capture_output=True,text=True);checks[name+'_rejected']=p.returncode!=0 and 'AssertionError' in p.stderr;rows.append({'case':name,'exit_code':p.returncode,'assertion_seen':'AssertionError' in p.stderr})
checks['no_invalid_polygon_repair_fallback']='buffer(0)' not in source and 'make_valid' not in source
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'component_script_sha256':hashlib.sha256((R/'check_component_detail.py').read_bytes()).hexdigest(),'tests':rows,'method':'Only temporary deliberately damaged copies are executed; final STL and validators remain unchanged.'}
(R/'negative-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(out);assert out['passed']
