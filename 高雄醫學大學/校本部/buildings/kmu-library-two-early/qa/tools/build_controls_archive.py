"""Rebuild the deterministic control archive from its validated member inventory.
No member is decoded: intentionally malformed compressed fixtures remain exact bytes.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, lzma, stat, tarfile
FORMAT = 'original-stl-controls-ustar-xz-v1'
def require(ok, message):
    if not ok: raise ValueError(message)
def digest(data): return hashlib.sha256(data).hexdigest()
def safe_path(name):
    require(isinstance(name,str) and name and '\\' not in name and '\x00' not in name, 'Unsafe member path')
    p=PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix()==name and all(x not in ('','..','.') for x in name.split('/')), 'Unsafe member path')
    return p

def make_archive(root, members):
    root=Path(root)
    require(root.is_dir() and not root.is_symlink(), 'Root must be a real directory')
    names=[r['path'] for r in members]
    require(names==sorted(set(names)) and len(names)>0, 'Member names must be unique and sorted')
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as tf:
        for row in members:
            require(set(row)=={'path','bytes','sha256'}, 'Member schema differs')
            path=safe_path(row['path']); p=root
            for part in path.parts:
                p=p/part
                require(not p.is_symlink(), 'Symlink in member source')
            require(stat.S_ISREG(p.stat().st_mode), 'Source is not regular')
            data=p.read_bytes()
            require(type(row['bytes']) is int and len(data)==row['bytes'] and digest(data)==row['sha256'], 'Source member content differs')
            info=tarfile.TarInfo(row['path']); info.size=len(data); info.mode=0o644
            info.uid=info.gid=info.mtime=0; info.uname=info.gname=''; info.type=tarfile.REGTYPE
            tf.addfile(info, io.BytesIO(data))
    raw=stream.getvalue()
    return raw,lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC64,preset=6)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(), 'Refuse existing output')
    index=json.loads(a.index.read_text())
    require(set(index)=={'format','archive_sha256','tar_sha256','members'} and index['format']==FORMAT, 'Index schema differs')
    raw,compressed=make_archive(a.root,index['members'])
    require(digest(raw)==index['tar_sha256'] and digest(compressed)==index['archive_sha256'], 'Rebuilt archive bytes differ')
    with a.out.open('xb') as f:f.write(compressed)
    print(json.dumps({'passed':True,'members':len(index['members']),'archive_sha256':digest(compressed),'tar_sha256':digest(raw),'archive_bytes':len(compressed),'tar_bytes':len(raw)}))
if __name__=='__main__':main()
