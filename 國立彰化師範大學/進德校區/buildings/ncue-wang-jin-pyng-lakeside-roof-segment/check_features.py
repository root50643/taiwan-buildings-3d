"""Localized checks supplement (do not replace) global layer-component survival."""
from pathlib import Path
import json,hashlib
import numpy as np
import manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)))
def geom(s):
 g=GeometryCollection()
 for p in s.to_polygons():
  if len(p)>2:g=g.symmetric_difference(Polygon(p))
 return g
# Rotation maps original x,z onto x,-z; slice uses original y.
front=geom(m.rotate((90,0,0)).slice(-28))
left=[(-60,45),(-32,45),(-21,47),(-13,51),(-13,53),(-60,52)]
right=[(21,57),(64,57),(67,71),(53,68.8),(38,65),(21,60.5)]
checks=[]
for name,p in [('left_tapered_opening',left),('right_sloped_opening',right)]:
 aperture=Polygon([(x,-z) for x,z in p]);occupied=front.intersection(aperture.buffer(-1e-4)).area
 assert occupied<1e-5,(name,occupied)
 checks.append({'feature':name,'front_y_mm':-28,'profile_xz':p,'clear_area_mm2':aperture.area,'solid_inside_aperture_area_mm2':occupied,'true_through_front_skin':True,'building_pass_through':False,'opaque_glazing_backing_y_mm':-20})
# Isolate roof seam components above supporting roof; don't let tower survival mask loss.
roof=[]
for z in np.r_[np.arange(88.55,89.15,.05),89.149]:
 g=geom(m.slice(float(z))).intersection(box(-65,-23.5,65,29.6))
 ps=list(g.geoms) if g.geom_type=='MultiPolygon' else ([g] if not g.is_empty else [])
 lost=[]
 for i,p in enumerate(ps):
  if p.buffer(-.4).is_empty:lost.append({'index':i,'area_mm2':p.area,'bounds_mm':list(p.bounds)})
 roof.append({'z_mm':float(z),'localized_components':len(ps),'vanishes_under_0_8mm_erosion':lost})
# Erosion-opening area loss catches thin ends even when the larger same component survives.
fascia=front.intersection(box(-77,-97,78,-40))
opening=fascia.buffer(-.4).buffer(.4);loss=fascia.difference(opening).area
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'aperture_checks':checks,'minimum_nominal_features_mm':{'fascia_depth':3.2,'roof_rib_width':1.05,'roof_rib_height':.65,'glazing_mullion_width':1.1,'paired_column_width':3.6,'display_plinth':3},'roof_localized_top_checks':roof,'roof_localized_0_8mm_losses_present':any(x['vanishes_under_0_8mm_erosion'] for x in roof),'fascia_front_0_8mm_morphological_opening_area_loss_mm2':loss,'warnings':['Display dimensions are not a surveyed real-world scale.','0.8mm erosion is a geometric screening heuristic, not a slicer/toolpath or printer guarantee.','Local sharp/tapered ends and roof ribs can lose detail even when the whole layer component survives.','Elevated fascia, balcony and roof overhangs require slicer-specific support assessment; no unsupported-print claim.','No physical printing, load-bearing, engineering or full-building reconstruction claim.']}
(A/'qa/features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
