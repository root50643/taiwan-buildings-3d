"""Optional regeneration of bundled glyph contours. Not needed for geometry rebuild.
Noto Serif CJK TC Bold, SIL Open Font License, stylistic substitute for Sun Ke calligraphy.
No font binary is redistributed. Font outlines are baked in glyphs.json for portability.
"""
from pathlib import Path
import json,hashlib,argparse
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
A=Path(__file__).resolve().parent
class Pen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.loops=[]
 def _moveTo(self,p):self.cur=[p]
 def _lineTo(self,p):self.cur.append(p)
 def _curveToOne(self,a,b,c):
  p=self.cur[-1]
  for i in range(1,13):
   t=i/12;u=1-t;self.cur.append(tuple(u**3*p[k]+3*u*u*t*a[k]+3*u*t*t*b[k]+t**3*c[k] for k in range(2)))
 def _qCurveToOne(self,a,b):
  p=self.cur[-1]
  for i in range(1,13):
   t=i/12;u=1-t;self.cur.append(tuple(u*u*p[k]+2*u*t*a[k]+t*t*b[k] for k in range(2)))
 def _closePath(self):self.loops.append(self.cur)
 def _endPath(self):self.loops.append(self.cur)
p=argparse.ArgumentParser();p.add_argument('--font',default='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc');p.add_argument('--font-number',type=int,default=3);args=p.parse_args()
f=TTFont(args.font,fontNumber=args.font_number);gs=f.getGlyphSet();cmap=f.getBestCmap();r={}
for c in '學大吳東':
 pen=Pen(gs);gs[cmap[ord(c)]].draw(pen);r[c]=pen.loops
(A/'glyphs.json').write_text(json.dumps({'font':'Noto Serif CJK TC Bold','font_license':'SIL OFL 1.1; rendered outlines only, no font binary','source_font_sha256':hashlib.sha256(Path(args.font).read_bytes()).hexdigest(),'substitute_not_original_calligraphy':True,'loops':r},ensure_ascii=False,separators=(',',':'))+'\n')
