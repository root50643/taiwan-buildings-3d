"""Record byte identities/newline facts without normalizing bound artifacts."""
import hashlib,json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=['source/build_model.py','source/render_preview.py','parameters.json','qa/independent_geometry_qa.py','qa/verify_reproducibility.py','qa/verify_reproducibility-attempt-01.py']
rows={}
for name in paths:
    data=(root/name).read_bytes()
    rows[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
        'CRLF_sequences':data.count(b'\r\n'),'lone_LF_sequences':data.count(b'\n')-data.count(b'\r\n')}
build=json.loads((root/'models/v4/build-report.json').read_text(encoding='utf8'))
r={'scope':'Raw bytes and newline facts only. No line endings, JSON, scripts, mesh or flags changed.',
    'files':rows,'stl_sha256':sha(root/'models/v4/model.stl'),
    'source_matches_final_build_report':rows['source/build_model.py']['sha256']==build['source_sha256'],
    'parameters_match_final_build_report':rows['parameters.json']['sha256']==build['parameters_sha256'],
    'geometry_checker_matches_unmodified_baseline':rows['qa/independent_geometry_qa.py']['sha256']=='0c0ca4e69386b2a5d7a531415eb4ca3ca16c599177c8ffdd8cfee37ed657b43c',
    'reproducibility_checker_unchanged_from_first_failed_check':rows['qa/verify_reproducibility.py']['sha256']==rows['qa/verify_reproducibility-attempt-01.py']['sha256'],
    'delivery_requirement':'Preserve raw artifact bytes, including existing CRLF/LF. Git text normalization would change bound SHA-256 and must be disabled for the package; this is an artifact integrity measure, not a QA threshold change.'}
(root/'qa/byte-provenance.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,indent=2))
