"""Actual raw-mesh section counts, not image-only column counting."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md
from shapely.geometry import Polygon
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def centers(z):
 contours=m.slice(z).to_polygons();return sorted([[Polygon(p).centroid.x,Polygon(p).centroid.y] for p in contours])
c=centers(50);assert len(c)==16
corners=[(x,y) for x in [-36,-12,12,36] for y in [-60,60]]+[(x,y) for x in [-36,36] for y in [-36,-12,12,36]]
assert all(min(np.linalg.norm(np.array(p)-q) for q in corners)<.01 for p in c)
assert len(centers(20))==17 # sixteen columns and central memorial, not a seventeenth column
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='unhealed actual raw STL horizontal sections via manifold, no image proxy',z50_columns=16,z50_section_centers=c,z20_components_columns_plus_memorial=17,column_center_grid=[72,120],short_end_columns=4,long_side_columns=6,assumed_not_survey_dimensions=True)
(A/'qa/architecture-sections.json').write_text(json.dumps(r,indent=2)+'\n');print('16 column section centers match intended short4/long6 perimeter; lower section includes distinct memorial.')
