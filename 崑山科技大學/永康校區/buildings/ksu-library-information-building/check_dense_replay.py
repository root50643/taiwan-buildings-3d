from pathlib import Path
import json,gzip,hashlib
R=Path(__file__).resolve().parent
expected=(R/'dense-independent-root-evidence.json.gz').read_bytes();a=gzip.decompress(expected);b=(R/'dense-independent-root-evidence.json').read_bytes();ok=a==b
r={'passed':ok,'checks':{'every_dense_flag_and_original_face_root_exact_replay':ok},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'expected_uncompressed_sha256':hashlib.sha256(a).hexdigest(),'recomputed_sha256':hashlib.sha256(b).hexdigest(),'scope':'Exact replay agreement is not approval of retained original diagnostic exceptions.'}
(R/'dense-replay-check.json').write_text(json.dumps(r,indent=2));assert ok
