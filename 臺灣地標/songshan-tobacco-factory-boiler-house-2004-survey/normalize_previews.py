"""Strip PNG ancillary metadata without decoding or changing image samples."""
from pathlib import Path
import struct

def normalize(path):
    raw=path.read_bytes(); assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    out=bytearray(raw[:8]); pos=8
    while pos<len(raw):
        n=struct.unpack('>I',raw[pos:pos+4])[0]; kind=raw[pos+4:pos+8]
        chunk=raw[pos:pos+n+12]; assert len(chunk)==n+12
        if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}: out.extend(chunk)
        pos+=n+12
    path.write_bytes(out)

if __name__=='__main__':
    import sys
    for p in Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).parent/'previews').glob('*.png'):normalize(p)
