from config import *
import numpy as np, hashlib, struct, gzip, csv, json
raw=S.read_bytes()
assert hashlib.sha256(raw).hexdigest()==H
count=struct.unpack_from('<I',raw,80)[0]
assert count==5630 and len(raw)==84+50*count
T=np.frombuffer(raw,offset=84,dtype=[('normal','<f4',3),('vertices','<f4',(3,3)),('attribute','<u2')])['vertices'].astype('<f8')
T.tofile(W/'ntou-revision-dense-triangles.bin')
# The exact C++ deliberately ignores placeholder origin/direction values whenever indices are supplied.
np.zeros((count*15,6),dtype='<f8').tofile(W/'ntou-revision-boundary-queries.bin')
indices=np.array([(face,sample)for sample in range(15)for face in range(count)],dtype='<i4')
indices.tofile(W/'ntou-revision-boundary-indices.bin')
with gzip.open(HERE/'inputs/dense-first-events-raw.csv.gz','rb')as f:(W/'ntou-revision-dense.csv').write_bytes(f.read())
rows=list(csv.DictReader(open(W/'ntou-revision-dense.csv')))
assert [(int(r['face']),int(r['sample']))for r in rows]==[tuple(q)for q in indices]
with gzip.open(HERE/'inputs/raw-flags.json.gz','rb')as f:(W/'ntou-revision-boundary-rawflags.json').write_bytes(f.read())
flags=json.loads((W/'ntou-revision-boundary-rawflags.json').read_text())
assert [int(r['index'])for r in flags]==[i for i,r in enumerate(rows)if any(int(r[k])!=v for k,v in [('inside_control',1),('outside_control',0),('mid_control',1),('after_exit_control',0)])]
print('Original STL geometry and all 84,450 source face/sample indices reconstructed.')
