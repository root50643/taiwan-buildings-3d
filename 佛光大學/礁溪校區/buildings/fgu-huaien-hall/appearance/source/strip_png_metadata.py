"""Remove PNG text/EXIF metadata only. Compressed image bytes never change."""
from pathlib import Path
import sys,struct
root=Path(sys.argv[1])
for p in sorted(root.glob('*.png')):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';chunks=[b[:8]];off=8
 while off<len(b):
  n=struct.unpack_from('>I',b,off)[0];kind=b[off+4:off+8];chunk=b[off:off+n+12]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:chunks.append(chunk)
  off+=n+12
 assert off==len(b);p.write_bytes(b''.join(chunks))
