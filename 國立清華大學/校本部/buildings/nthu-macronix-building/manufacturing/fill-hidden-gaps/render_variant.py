"""Save this optional STL as an mm Blender scene and render one overview.

Reuse the pinned package renderer, restricted to the front overview. It
neither writes the original scene nor renders the original's four views.
Run: python render_variant.py (bpy), or blender -b -P render_variant.py.
"""
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
source=HERE.parents[1]/'render_preview.py'
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='43980e2e9aee5be584997ff68a56f11e4393ee56b9921563617ddeafd3c56b6a'
text=raw.decode('utf-8')
old="views=[('front',(-195,-220,155),(0,0,target_z)),('rear',(195,230,160),(0,0,target_z)),('elevation',(0,-260,39),(0,0,target_z)),('roof',(-100,-180,250),(-10,-5,30))]"
assert text.count(old)==1
text=text.replace(old,"views=[('front',(-195,-220,155),(0,0,target_z))]")
text=text.replace("'model_category']='Single connected printable solid'","'model_category']='Optional manufacturing infill, not sliced or print validated'")
(HERE/'qa').mkdir(exist_ok=True)
exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(HERE/'render_variant.py')})
