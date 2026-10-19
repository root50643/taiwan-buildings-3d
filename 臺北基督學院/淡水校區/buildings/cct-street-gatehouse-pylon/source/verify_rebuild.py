"""Verify source-only clean temporary rebuild in the active installed toolchain.
Run with the Python environment containing numpy/trimesh/manifold3d. No network,
software installation, photo pixels or replacement of delivered model files.
"""
from pathlib import Path
import hashlib,importlib.metadata,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
def main():
 with tempfile.TemporaryDirectory() as td:
  out=Path(td);(out/'source').mkdir()
  for f in ['build_model.py','lettering.scad','build_exchange.py']:shutil.copyfile(R/'source'/f,out/'source'/f)
  for f in ['build_model.py','build_exchange.py']:subprocess.run([sys.executable,str(out/'source'/f)],capture_output=True,text=True,check=True)
  paths=['geometry.json',*[str(p.relative_to(R)) for p in sorted((R/'parts').glob('*.stl'))],*[str(p.relative_to(R)) for p in sorted((R/'appearance').rglob('*.3mf'))]];checks=[]
  for p in paths:
   a=hashlib.sha256((R/p).read_bytes()).hexdigest();b=hashlib.sha256((out/p).read_bytes()).hexdigest();checks.append({'path':p,'sha256':a,'clean_temp_rebuild_identical':a==b})
  assert all(x['clean_temp_rebuild_identical'] for x in checks)
 fontpath=Path(subprocess.check_output(['fc-match','-f','%{file}','Noto Sans CJK TC:style=Bold'],text=True).strip());assert fontpath.is_file()
 versions={k:importlib.metadata.version(k) for k in ['numpy','trimesh','manifold3d']}
 proc=subprocess.run(['openscad','--version'],capture_output=True,text=True,check=True);versions['OpenSCAD']=(proc.stdout+proc.stderr).strip();versions['Python']=sys.version.split()[0]
 report={'clean_temporary_rebuild':True,'files':checks,'source_inputs':['source/build_model.py','source/lettering.scad','source/build_exchange.py'],'source_photo_pixels_required':False,'external_build_dependency_versions':versions,'font_name':'Noto Sans CJK TC Bold','font_file_distributed':False,'font_sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'scope':'Same installed tool versions and font; no claim of cross-version byte identity.'}
 (R/'qa/rebuild-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'files':len(checks),'all_rebuild_SHA_identical':True,'dependencies':versions},ensure_ascii=False))
if __name__=='__main__':main()
