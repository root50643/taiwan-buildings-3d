#!/usr/bin/env python3
"""Independent format geometry and horizontal section/overhang screen.
Uses numpy, trimesh, shapely; no external slicer, printer profile or G-code.
Polygonizes explicit mesh-plane segments (does not need networkx/rtree).
"""
from pathlib import Path
import argparse,json,collections
import numpy as np,trimesh
from shapely.geometry import LineString,Polygon,GeometryCollection
from shapely.ops import polygonize,unary_union
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path(__file__).parent);args=ap.parse_args();root=args.input;out=root/'qa';out.mkdir(exist_ok=True)
def stats(m):
 return {'vertices':len(m.vertices),'triangles':len(m.faces),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'shells':len(m.split(only_watertight=False)),'euler_number':int(m.euler_number),'degenerate_triangles_below_1e-8_mm2':int(sum(m.area_faces<1e-8)),'non_two_face_edges':int(sum(np.bincount(m.edges_unique_inverse)!=2)),'volume_mm3':float(m.volume)}
rows={};meshes={}
for name in ['mesh.json','qa/3mf-readback-mesh.json','qa/3mf-edited-readback-mesh.json']:
 d=json.loads((root/name).read_text());m=trimesh.Trimesh(d['vertices'],d['faces'],process=False);rows[name]=stats(m);meshes[name]=m
m=trimesh.load(root/'model.stl',process=True);rows['model.stl']=stats(m);meshes['model.stl']=m
for name,row in rows.items():assert row['watertight'] and row['winding_consistent'] and row['shells']==1 and row['euler_number']==2 and row['degenerate_triangles_below_1e-8_mm2']==0 and row['non_two_face_edges']==0,(name,row)
# All format roundtrips must remain the same triangle-coordinate surface.
base=meshes['mesh.json'];
from scipy.spatial import cKDTree
for name,m in meshes.items():
 dist,remap=cKDTree(base.vertices).query(m.vertices)
 def canonical_faces(f):return sorted(tuple(sorted(t))for t in f)
 rows[name]['vertex_to_master_max_delta_mm']=float(dist.max())
 rows[name]['triangle_coordinate_surface_equal_within_0_00001_mm']=bool(dist.max()<1e-5 and canonical_faces(remap[m.faces])==canonical_faces(base.faces))
 assert rows[name]['triangle_coordinate_surface_equal_within_0_00001_mm'],(name,rows[name])
(out/'format-geometry-qa.json').write_text(json.dumps(rows,indent=2)+'\n')
# Evaluate exported STL, not the unexported Boolean solid. Offset sections avoid
# coincidence with exact horizontal faces; precision is 0.00001 model mm.
layer=.2;heights=np.arange(.01337,m.bounds[1,2]-.0001,layer);layers=[];last=None;fail=[]
for z in heights:
 seg=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,z]);seg=np.round(seg[:,:,:2],5);nonzero=np.linalg.norm(seg[:,1]-seg[:,0],axis=1)>1e-7;seg=seg[nonzero]
 degree=collections.Counter(tuple(q)for edge in seg for q in edge);bad=sum(v!=2 for v in degree.values());polys=list(polygonize([LineString(s)for s in seg]));shape=unary_union(polys)
 if bad or not polys or not shape.is_valid:fail.append({'z_mm':float(z),'non_degree_two_vertices':bad,'polygons':len(polys),'valid':bool(shape.is_valid)})
 count=len(shape.geoms)if hasattr(shape,'geoms')else 1
 # A 45 degree build-up cone at the layer step, not a bridging/adhesion solver.
 newly=shape.difference(last.buffer(layer,join_style=2)).area if last is not None else 0
 disconnected=sum(p.intersection(last).area<1e-5 for p in polys)if last is not None else 0
 layers.append({'z_mm':round(float(z),5),'closed_polygons':len(polys),'connected_regions':count,'area_mm2':round(shape.area,6),'non_degree_two_vertices':bad,'new_area_beyond_45deg_mm2':round(newly,6),'new_regions_without_previous_layer_overlap':disconnected})
 last=shape
p=json.loads((root/'parameters.json').read_text());screen={'mesh':'exported model.stl','units':'millimeter','layer_height_mm':layer,'phase_offset_mm':.01337,'layers_tested':len(layers),'section_failures':fail,'all_sections_closed_valid':not fail,'min_connected_regions':min(q['connected_regions']for q in layers),'max_connected_regions':max(q['connected_regions']for q in layers),'layers_with_disconnected_new_regions':[q for q in layers if q['new_regions_without_previous_layer_overlap']],'overhang_flagged_layers':[q for q in layers if q['new_area_beyond_45deg_mm2']>.01],'features_at_100pct':{'base_thickness_mm':p['base_thickness'],'solid_wing_depth_mm':p['depth'],'upper_frame_width_mm':p['frame_width'],'glazing_recess_depth_mm':p['recess_depth'],'canopy_thickness_mm':p['canopy_thickness'],'canopy_projection_mm':p['canopy_projection'],'entry_step_rise_mm':p['plinth_height']/p['entry_steps'],'entry_step_tread_mm':p['entry_step_tread'],'louver_recess_depth_mm':.45,'louver_slot_height_mm':.8},'limits':['Not an actual Cura/Prusa/Orca slicer run, G-code generation or physical print. No machine/material temperature/adhesion certification.','0.4 mm nozzle and 0.2 mm layers are screening assumptions only. 0.9 mm frames/canopy are approximately two lines but slicer line width differs.','Canopy underside projects 3 mm: inspect local support/bridging in the chosen slicer. Recess heads may need bridging support.','No hidden interior, loose roof or detachable shell; no infill assumed by geometric volume. Infill and perimeter choices affect material usage.','Downscaling below 100% makes canopy/frame 0.9 mm thinner; 50% gives 0.45 mm. Revalidate every scaled print.','Base-flat orientation only was screened. Face-color 3MF is not a printer profile or guaranteed multi-material toolpath.','The observed accessible ramp remains deliberately omitted; entry steps are not an accessibility claim.','212 mm model length plus 5 mm brim at both ends requires 222 mm, exceeding a nominal 220 mm bed dimension; check actual usable bed area.']}
assert not fail and not screen['layers_with_disconnected_new_regions']
(out/'slice-feature-screen.json').write_text(json.dumps(screen,indent=2)+'\n');(out/'slice-layers.json').write_text(json.dumps(layers,indent=2)+'\n')
print(json.dumps({k:v for k,v in screen.items()if k!='limits'},indent=2))
