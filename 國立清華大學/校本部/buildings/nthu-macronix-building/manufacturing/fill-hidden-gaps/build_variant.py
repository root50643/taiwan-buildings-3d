"""Optional manufacturing simplification of fixed f15ccb3, millimetres.
Run with the package requirements. Only model.stl / model.obj beside this
script are written; the original package source, STL and scene are retained.
This is not an additional building set, a source accuracy improvement, a
slicer result, or a successful print. See ../PRINT-CONDITIONS.zh-TW.md.
"""
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
source=HERE/'original-source-f15ccb3.py'
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='cff21ed128f2fa72d540e5894dc884f3a25db76c7657645477cf90a18bb5b66b'
text=raw.decode('utf-8')
assert text.count('solid=parts[0]')==1
infill="""
# Manufacturing-only infill, unioned after the original cuts. Four fin backs
# at three window levels; overlap the fin and cut back wall by 0.05 mm.
# The front planes and bay boundaries stay; oblique fin side/rear surfaces
# change deliberately. No bay-wide filling and no roof/rear mass reshaping.
for x in [37,43,49,55]:
 for z in [25,34,43]:
  det(x,-20.0,z,1.0,1.9,7.0)
# Rear sill microgap: local Y -9.8..-9.75, Z z..z+0.1.
# Overlap old sill by 0.01 mm and wall by 0.05 mm; keep local front lip -13.
for x,ang in [(-30,-14),(30,14)]:
 for z in [18,29,40,51]:
  details.append(box(0,-9.755,z,64,0.11,0.1).rotate((0,0,ang)).translate((x,30,0)))
"""
text=text.replace('solid=parts[0]',infill+'\nsolid=parts[0]')
exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(HERE/'build_variant.py')})
