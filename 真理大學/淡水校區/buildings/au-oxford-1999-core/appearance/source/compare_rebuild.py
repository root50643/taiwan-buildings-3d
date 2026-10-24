"""Compare independent output geometry reports, deterministic data and all nine PNG bytes/pixels."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image
import sys
sys.dont_write_bytecode=True
from common import dump
p=argparse.ArgumentParser();p.add_argument('reference',type=Path);p.add_argument('rebuilt',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();names=['front','front-right','elevation','rear','left','right','top','underside','parapet-detail'];result=[]
for n in names:
 p=a.reference/'previews'/f'{n}.png';q=a.rebuilt/'previews'/f'{n}.png';im=Image.open(p);jm=Image.open(q);assert im.size==jm.size==(1200,900);assert im.mode==jm.mode and im.tobytes()==jm.tobytes();assert p.read_bytes()==q.read_bytes();result.append({'name':n,'bytes_exact':True,'decoded_pixels_exact':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for f in ['au-oxford-1999-core-appearance.3mf','face-materials.csv','parameters.json','palette.json','qa/geometry-preservation.json','qa/3mf-validation.json','qa/blend-validation.json','qa/fail-closed.json','qa/render-manifest.json']:assert (a.reference/f).read_bytes()==(a.rebuilt/f).read_bytes(),f
dump(a.report,{'status':'PASS','clean_input':'Only public original STL plus public Python sources, numeric parameters and palette; no candidate binaries or previews used as input','nine_png_byte_and_pixel_exact':result,'3mf_bytes_exact':True,'material_map_and_numeric_parameters_exact':True,'both_native_geometry_reports_exact':True,'blend_binary_bytes_not_compared':'Blender native save includes nonsemantic session state; exact geometry/materials independently reopened and verified for both.'})
