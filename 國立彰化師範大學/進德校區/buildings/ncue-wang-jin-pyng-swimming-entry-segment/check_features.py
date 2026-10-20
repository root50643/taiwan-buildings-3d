"""Localized front-recess and small-feature erosion checks on original STL."""
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
front=geom(m.rotate((90,0,0)).slice(-10));checks=[]
for name,rect in [('upper_glass_panel',(5,-31.5,10,-29.25)),('lower_window_panel',(5,-12.75,7,-12)),('entrance_door_panel',(-9,-9,-5,-4))]:
 aperture=box(*rect);occupied=front.intersection(aperture).area
 assert occupied<1e-6,(name,occupied)
 checks.append({'feature':name,'front_y_mm':-10,'tested_x_minus_z_bounds':rect,'clear_area_mm2':aperture.area,'occupied_area_mm2':occupied,'true_recess_not_building_passthrough':True})
local=[]
# Isolate top ribs and tower crossbars separately from supporting bulk.
for z in [56.26,56.4,56.6,56.624]:
 g=geom(m.slice(z));ps=list(g.geoms) if g.geom_type=='MultiPolygon' else ([g] if not g.is_empty else [])
 lost=[{'area_mm2':p.area,'bounds_mm':list(p.bounds)} for p in ps if p.buffer(-.4).is_empty]
 local.append({'z_mm':z,'components':len(ps),'vanished_components':lost,'morphological_opening_loss_mm2':g.difference(g.buffer(-.4).buffer(.4)).area})
# Frontal feature isolation: crop windows excludes larger facade's survival masking.
front2=geom(m.rotate((90,0,0)).slice(-10.5));detail=front2.intersection(box(2,-48,36,-27.75));opened=detail.buffer(-.4).buffer(.4)
tower=geom(m.rotate((90,0,0)).slice(-20));tower=tower.intersection(box(-35.2,-49,-20.8,-2.25))
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'recess_checks':checks,'normalized_dimensions_not_real_scale':True,'nominal_minimum_features_mm':{'roof_skin_vertical':1.5,'roof_rib_width':1,'roof_rib_height':.375,'upper_horizontal_frames_height':.75,'vertical_frames_width':1,'tower_horizontal_frames_height':.75,'display_base':2.25},'roof_top_local_tests':local,'upper_grid_frontal_area_mm2':detail.area,'upper_grid_0_8mm_opening_loss_mm2':detail.difference(opened).area,'tower_grid_frontal_area_mm2':tower.area,'tower_grid_0_8mm_opening_loss_mm2':tower.difference(tower.buffer(-.4).buffer(.4)).area,'warnings':['0.75 mm horizontal frame bars and 0.375 mm roof rib rise are below the 0.8 mm detail screen, even though every whole horizontal component survives.','Morphological opening removes local corners and thin edges. Not a no-thin-feature or toolpath guarantee.','Roof overhang and recessed entrances need orientation/support planning in a real slicer.','No physical print, survey, engineering, dimensional-restoration or 2026 current-state claim.']}
(A/'qa/features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
