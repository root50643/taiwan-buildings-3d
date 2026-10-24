"""Read pinned STL without a geometry operation; original triangle order is stable."""
import hashlib, math, struct
from pathlib import Path
EXPECTED_STL_SHA256='899833cab3d36540de1455757b2b1119f5d4563a8f0bede4f16286f036f04652'

def read_original(path):
    raw=Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_STL_SHA256, 'Input is not the reviewed original STL'
    n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*n
    vertices=[]; faces=[]; lookup={}
    for i in range(n):
        values=struct.unpack_from('<12fH',raw,84+50*i)
        face=[]
        for j in range(3):
            co=tuple(values[3+3*j:6+3*j])
            assert all(math.isfinite(v) for v in co)
            if co not in lookup: lookup[co]=len(vertices); vertices.append(co)
            face.append(lookup[co])
        faces.append(face)
    return vertices, faces

def triangle_coordinate_sha(vertices,faces):
    h=hashlib.sha256()
    for f in faces:
        for v in f:h.update(struct.pack('<3f',*vertices[v]))
    return h.hexdigest()

def normal(p):
    a=[p[1][k]-p[0][k] for k in range(3)];b=[p[2][k]-p[0][k] for k in range(3)]
    c=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    length=math.sqrt(sum(v*v for v in c));assert length>0
    return [v/length for v in c]

def area(p):
    a=[p[1][k]-p[0][k] for k in range(3)];b=[p[2][k]-p[0][k] for k in range(3)]
    c=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    return math.sqrt(sum(v*v for v in c))/2
