"""Clear private default file-browser buffer tails without changing geometry.
Blender may shorten a directory string to // but retain bytes after its NUL.
Only uncompressed BLENDER files are handled; output remains uncompressed.
"""
from pathlib import Path
import re

def sanitize(path):
    path=Path(path);b=path.read_bytes()
    if not b.startswith(b'BLENDER'):raise ValueError('Save with compress=False before sanitizing')
    # No external file paths are used by this scene. The matched fragments are
    # stale default user-directory buffers beyond the current string terminator.
    pattern=rb'(?:[A-Za-z]:[\\/])?(?:Users|home)[\\/][^\\/\x00]{1,128}[\\/][^\x00]{0,1024}'
    matches=list(re.finditer(pattern,b));count=len(matches)
    b=re.sub(pattern,lambda m:b'\x00'*len(m.group(0)),b)
    path.write_bytes(b)
    return count

if __name__=='__main__':
    print(sanitize(Path(__file__).resolve().parent/'scene.blend'))
