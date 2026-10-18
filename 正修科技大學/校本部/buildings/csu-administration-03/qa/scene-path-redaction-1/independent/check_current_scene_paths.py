"""Verify the reviewed current BLEND artifacts without Git or private originals."""
from pathlib import Path
import argparse,hashlib,json,re
from independent_blend_field_audit import inspect
from independent_zstd_frames import parse

EXPECTED={
 'models/v1/scene.blend':'fc0c4ac3a4106a8f7c28ec4b526d6cac33ec433297329c69e7dbccea76be99a3',
 'models/v2/scene.blend':'d852f85363988a986e7ed225ebfeb39433e9e8fe6a1d8e48fb8d09f6fec0f01c'}
def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,message):
 if not ok:raise RuntimeError(message)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package-root',type=Path,required=True)
 p.add_argument('--manifest',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 require(not a.output.exists(),'Fresh output report required')
 manifest_path=a.manifest or a.package_root/'qa/scene-path-redaction-1/redaction-manifest.json'
 manifest=json.loads(manifest_path.read_text());records={r['path']:r for r in manifest['files']};rows=[]
 require(set(records)==set(EXPECTED),'Unexpected current scene manifest entries')
 for name,expected in EXPECTED.items():
  raw=(a.package_root/name).read_bytes();record=records[name]
  require(sha(raw)==expected==record['delivered_sha256'] and len(raw)==record['delivered_bytes'],'Current fixed scene hash/size differs')
  data,fields,hits=inspect(raw);frames=parse(raw)
  require(len(fields)==1,'Need one independent SDNA dir array')
  field=fields[0];start,end=field['field_start'],field['field_end_exclusive']
  checks={'actual_SHA256_matches_fixed_review_and_manifest':sha(raw)==expected==record['delivered_sha256'],
   'actual_expanded_SHA256_matches_manifest':sha(data)==record['delivered_expanded_sha256'],
   'independent_SDNA_dir_span_matches_reviewed_manifest':[start,end]==record['field']['expanded_range'],
   'dir_is_relative_double_slash_and_all_remaining_bytes_NUL':data[start:end]==b'//'+b'\0'*(end-start-2),
   'all_decoded_frames_have_no_private_host_path':not hits,
   'raw_compressed_artifact_has_no_private_host_path':not re.search(rb'[A-Za-z]:[\\/](?:Users|Program Files|Windows)[\\/]',raw),
   'manual_frame_count_matches_manifest':len(frames)==record['frame_count_after'],
   'manual_frame_payloads_reconstruct_full_decoded_file':b''.join(f['data'] for f in frames)==data}
  frame_rows=[]
  for i,frame in enumerate(frames):
   saved=record['frames'][i];lo=frame['expanded_start'];hi=lo+len(frame['data'])
   row={'index':i,'kind':frame['kind'],'compressed_bytes':len(frame['raw']),'compressed_sha256':sha(frame['raw']),
        'expanded_range':[lo,hi],'matches_reviewed_frame_SHA256':sha(frame['raw'])==saved['delivered_compressed_sha256'],
        'matches_reviewed_frame_size_and_range':len(frame['raw'])==saved['delivered_compressed_bytes'] and [lo,hi]==saved['expanded_range']}
   frame_rows.append(row)
  checks['all_current_data_and_seek_frames_match_reviewed_manifest']=all(r['matches_reviewed_frame_SHA256'] and r['matches_reviewed_frame_size_and_range'] for r in frame_rows)
  global_data,global_fields,_=inspect(raw,'FileGlobal','filename');require(len(global_fields)==1,'Need one independent GLOB filename')
  global_field=global_fields[0];checks['GLOB_FileGlobal_filename_remains_empty']=global_data[global_field['field_start']:global_field['field_end_exclusive']].split(b'\0',1)[0]==b''
  rows.append({'path':name,'passed':all(checks.values()),'checks':checks,'actual_sha256':sha(raw),
   'decoded_private_hostpath_findings':len(hits),'field':field,'frames':frame_rows})
 result={'passed':all(r['passed'] for r in rows),'files':rows,'manifest_sha256':sha(manifest_path.read_bytes()),
  'source_inventory':{name:sha(Path(__file__).with_name(name).read_bytes()) for name in ['check_current_scene_paths.py','independent_blend_field_audit.py','independent_zstd_frames.py']},
  'requires_Git_or_private_originals':False,'scene_saved_or_rendered':False,
  'scope':'Current-artifact fixed-hash, manual-frame/seek-table, independent SDNA char-array and decompressed privacy checks. Old/new equivalence remains separately supported by the immutable baseline Git review. Original 13-true report remains historical with its compressed-payload blind spot disclosed.'}
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'files':[{'path':r['path'],'passed':r['passed']} for r in rows]}));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
