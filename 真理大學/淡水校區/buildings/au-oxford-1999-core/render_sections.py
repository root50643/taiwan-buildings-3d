"""Plot two actual STL ornament sections; do not repair any invalid contours."""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh
from shapely.geometry import Polygon,Point
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=True)
def section(z):
 tri=m.triangles;tri=tri[(tri[:,:,2].min(1)<z)&(tri[:,:,2].max(1)>z)];adj={}
 for f in tri:
  hit=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(tuple(np.round((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2],6)))
  if len(hit)==2 and hit[0]!=hit[1]:
   a,b=hit;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(v)==2 for v in adj.values())
 remaining=set(adj);shape=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a);opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
   if a==seed:break
   assert len(loop)<=len(adj)
  p=Polygon(loop);assert p.is_valid
  if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid
 return [shape] if shape.geom_type=='Polygon' else list(shape.geoms)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
im=Image.new('RGB',(900,510),'white');d=ImageDraw.Draw(im)
d.text((20,12),'actual STL 尖塔／端飾截面：原輪廓、侵蝕與opening',font=font,fill='#15243e')
rows=[]
for i,(z,c,title) in enumerate([(50.271,(-49.5,-58.1),'翼端飾頂部'),(63.071,(0,-21.95),'中央尖塔十字桿')]):
 ps=section(z);p=next(p for p in ps if p.covers(Point(c)));e=p.buffer(-.4);o=e.buffer(.4);assert e.geom_type==o.geom_type=='Polygon' and not e.is_empty
 offset=(225+450*i,246);scale=205
 def pts(poly):return [(offset[0]+(x-c[0])*scale,offset[1]-(y-c[1])*scale) for x,y in poly.exterior.coords]
 d.polygon(pts(p),fill='#e0e7f0',outline='#254469',width=3)
 d.polygon(pts(o),fill='#b9d7c3',outline='#246441',width=3)
 d.polygon(pts(e),fill='#db9b7e',outline='#853817',width=2)
 w=p.bounds[2]-p.bounds[0];h=p.bounds[3]-p.bounds[1]
 d.text((25+450*i,58),f'{title}｜z={z:.3f} mm',font=font,fill='#15243e')
 d.text((25+450*i,383),f'實測 {w:.6f} × {h:.6f} mm',font=small,fill='#15243e')
 d.text((25+450*i,410),f'損失 {p.difference(o).area/p.area*100:.6f}%｜保留單一Polygon',font=small,fill='#15243e')
 rows.append({'z_mm':z,'centre_xy_mm':c,'bounds_mm':p.bounds,'original_area_mm2':p.area,'lost_area_mm2':p.difference(o).area,'lost_fraction':p.difference(o).area/p.area,'eroded_components':1,'opened_components':1})
d.text((20,451),'灰藍：原STL　綠：0.4mm侵蝕再膨脹　橘：0.4mm侵蝕',font=small,fill='#15243e')
d.text((20,478),'此圖只定位指定截面；細件仍脆弱，並非全方向厚度或實體試印保證。',font=small,fill='#15243e')
(R/'qa').mkdir(exist_ok=True);file=R/'qa'/'ornament-sections.png';im.save(file)
(R/'ornament-section-provenance.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'image':'qa/ornament-sections.png','image_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'sections':rows},indent=2))
