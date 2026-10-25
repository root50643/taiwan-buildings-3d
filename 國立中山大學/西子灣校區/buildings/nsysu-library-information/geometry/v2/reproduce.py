"""Rebuild geometry, 3MF and nine actual previews without network/source-raster inputs.
Run with geometry Python: python reproduce.py --blender blender --lib3mf-python python
Install requirements.txt and requirements-3mf.txt in the relevant Python environments.
"""
from pathlib import Path
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--blender',default='blender');p.add_argument('--lib3mf-python',default=sys.executable);p.add_argument('--skip-renders',action='store_true');a=p.parse_args();src=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(src/'build_model.py'),'--out',str(a.out),'--params',str(src/'params.json')],check=True)
# Renderer and exporter read the same documented parameter file beside their generated mesh arrays.
if a.out.resolve()!=src.resolve():
 import shutil
 shutil.copy2(src/'params.json',a.out/'params.json')
subprocess.run([a.lib3mf_python,str(src/'export_3mf.py'),'--out',str(a.out)],check=True)
cmd=[a.blender,'--background','--factory-startup','--disable-autoexec','-t','4','-P',str(src/'render_model.py'),'--','--out',str(a.out)]
if a.skip_renders:cmd.append('--no-render')
subprocess.run(cmd,check=True)
subprocess.run([sys.executable,str(src/'validate_model.py'),'--out',str(a.out)],check=True)
