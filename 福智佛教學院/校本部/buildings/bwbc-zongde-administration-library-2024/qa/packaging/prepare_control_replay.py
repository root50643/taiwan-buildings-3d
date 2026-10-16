"""Verify the complete observed control archive, then prepare fresh replay inputs.
The original observed results remain in the archive. Only scripts and baseline
fixtures are materialized beside byte-identical verification/helper sources.
Use a trusted FILES-SHA256.json and controls-index.json; no authentication is implied.
"""
from pathlib import Path
import argparse,hashlib,json,sys
from archive_verify import verify,extract_new,require,safe_path,unique_object

def digest(data):return hashlib.sha256(data).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--qa',type=Path,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 manifest=json.loads((a.qa/'FILES-SHA256.json').read_text(),object_pairs_hook=unique_object)
 require(isinstance(manifest,dict),'Files inventory is not an object')
 sources={}
 def direct(name):
  safe_path(name);p=a.qa
  for part in name.split('/'):
   p=p/part;require(not p.is_symlink(),'Direct source symlink')
  data=p.read_bytes();row=manifest[name]
  require(set(row)=={'bytes','sha256'} and type(row['bytes']) is int and row['bytes']==len(data) and row['sha256']==digest(data),'Direct source integrity differs: '+name)
  sources[name]=row;return data
 direct('controls.tar.xz');direct('controls-index.json')
 validation,tar,records=verify(a.qa/'controls.tar.xz',a.qa/'controls-index.json')
 require(validation['archive_sha256']==sources['controls.tar.xz']['sha256'] and validation['index_sha256']==sources['controls-index.json']['sha256'],'Archive/index changed after package integrity check')
 material={}
 for name,start,end in records:
  if name.endswith('.py') or name.startswith(('audit/generic-controls/','audit/original-hex-box/','audit/original-hex-glide/')):
   material[name]=tar[start:end]
 required_tools={'verification/'+name for name in ['check_controls.py','check_dense_surface.py','check_intersection_controls.py','check_original_intersections.py','check_raw_mesh.py','check_sections.py','dense_original.cpp','qa_common.py','run_qa.py']}
 required_tools.update('independent-tools/'+name for name in ['diagnose_recorded_cpp_rays.py','exact_ray_diagnosis.py','png_exact_compare.py','sanitize_png_previews.py','postflight_acceptance.py'])
 require(required_tools.issubset(manifest),'Missing required replay helper in package inventory')
 for name in sorted(manifest):
  if name.startswith(('verification/','independent-tools/')) and name.endswith(('.py','.cpp')):
   require(name not in material,'Replay source collision');material[name]=direct(name)
 report={'purpose':'Fresh control replay sources and complete positive baselines, excluding prior run output directories. Full observed evidence remains in controls.tar.xz.','archive_validation':validation,'source_files':{name:{'bytes':len(data),'sha256':digest(data)} for name,data in sorted(material.items())},'direct_package_inputs':sources}
 material['REPLAY-INPUTS.json']=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode()
 payload=bytearray();selected=[]
 for name,data in sorted(material.items()):
  start=len(payload);payload.extend(data);selected.append((name,start,len(payload)))
 extract_new(a.out,payload,selected)
 print(json.dumps({'passed':True,'files':len(material),'archive_members_verified':validation['members'],'optimization_level':sys.flags.optimize}))
if __name__=='__main__':main()
