#!/usr/bin/env python3
"""Independent exported-STL topology and approximate slice screen. Not a slicer/toolpath/physical print test."""
import pathlib,json,argparse,hashlib,subprocess,tempfile
from collections import defaultdict,Counter
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();root=a.out;(root/'qa').mkdir(parents=True,exist_ok=True);source_dir=pathlib.Path(__file__).resolve().parent
D=np.load(root/'mesh-data.npz');mesh=trimesh.load_mesh(root/'nqu-roundhouse-entrance-facade.stl',process=True);faces=mesh.faces
# Combinatorial two-manifold checks, independent of builder's assertions.
edges=Counter(tuple(sorted((int(f[i]),int(f[(i+1)%3])))) for f in faces for i in range(3))
vertex_links=defaultdict(list)
for f in faces:
 for i in range(3):vertex_links[int(f[i])].append((int(f[(i+1)%3]),int(f[(i+2)%3])))
bad_vertices=[]
for v,es in vertex_links.items():
 adj=defaultdict(set)
 for x,y in es:adj[x].add(y);adj[y].add(x)
 seen=set();todo=[next(iter(adj))]
 while todo:
  x=todo.pop()
  if x in seen:continue
  seen.add(x);todo.extend(adj[x]-seen)
 if len(seen)!=len(adj) or any(len(ns)!=2 for ns in adj.values()):bad_vertices.append(v)
report={'artifact':'nqu-roundhouse-entrance-facade.stl','units':'millimetres of authored print model; not measured scale','vertices':len(mesh.vertices),'edges':len(edges),'triangles':len(faces),'closed_shells':len(mesh.split(only_watertight=False)),'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad_vertices),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'euler_characteristic':int(mesh.euler_number),'positive_volume_mm3':float(mesh.volume),'degenerate_triangles':int((mesh.area_faces<1e-9).sum()),'duplicate_triangles':len(faces)-len(np.unique(np.sort(faces,axis=1),axis=0)),'bounds_mm':mesh.bounds.tolist(),'size_mm':mesh.extents.tolist(),'independent_triangle_self_intersection_test':'not run; manifold Boolean construction and closed oriented export checked'}
print(json.dumps(report,indent=2))
assert report['closed_shells']==1 and report['nonmanifold_edges']==report['nonmanifold_vertex_links']==report['degenerate_triangles']==report['duplicate_triangles']==0
assert report['watertight'] and report['winding_consistent'] and mesh.volume>0
(root/'qa'/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
solid=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
assert solid.status()==mf.Error.NoError
records=[];prev=None
for z in np.arange(.1,145.15,.2):
 geom=GeometryCollection()
 for poly in solid.slice(float(z)).to_polygons():
  if len(poly)>2:geom=geom.symmetric_difference(Polygon(poly))
 assert geom.is_valid and not geom.is_empty
 comps=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
 lost08=geom.difference(geom.buffer(-.4).buffer(.4)).area
 lost12=geom.difference(geom.buffer(-.6).buffer(.6)).area
 overhang=0 if prev is None else geom.difference(prev.buffer(.4)).area
 records.append({'z_mm':round(float(z),3),'area_mm2':round(geom.area,4),'contours_or_regions':len(comps),'opening_lost_area_at_0_8mm_mm2':round(lost08,4),'opening_lost_area_at_1_2mm_mm2':round(lost12,4),'outside_previous_layer_plus_0_4mm_mm2':round(overhang,4)})
 prev=geom
screen={'type':'geometric horizontal section screen, NOT a slicer or physical print','layer_step_mm':.2,'sections':len(records),'nonempty_valid_sections':len(records),'minimum_section_area_mm2':min(r['area_mm2']for r in records),'maximum_separate_regions_in_slice':max(r['contours_or_regions']for r in records),'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(r['outside_previous_layer_plus_0_4mm_mm2']for r in records),'maximum_opening_lost_area_0_8mm_mm2':max(r['opening_lost_area_at_0_8mm_mm2']for r in records),'maximum_opening_lost_area_1_2mm_mm2':max(r['opening_lost_area_at_1_2mm_mm2']for r in records),'designed_free_feature_minimum_mm':1.0,'thin_color_skin_not_standalone_wall':'Shallow brick relief and inset glazing intersect structural material; not isolated walls','warnings':['Supports/bridging need assessment at the 68 mm entrance lintel, arch recess, upper gallery rail and projecting front eave.','Railing/mullions are thickened to approximately 1 mm; do not downscale without slicing again.','The rear wall, 27 mm backing depth and display plinth are artificial support/crop conventions, not the rear building.','Morphological section tests do not certify global wall thickness or printable overhangs.','No slicer toolpath or physical print test has been performed.','3MF has base-material colors, not printer-specific extruder or filament assignments.','Model is 146 x 41 x 145.15 mm; confirm bed margins. Geometry volume is not filament usage.'],'records':records}
(root/'qa'/'slice-thickness-screen.json').write_text(json.dumps(screen,indent=2)+'\n')
# A fresh process rebuild; geometry, connectivity and face materials must match, STL bytes match too.
with tempfile.TemporaryDirectory(prefix='nqu-facade-rebuild-') as tmp:
 subprocess.run([__import__('sys').executable,str(source_dir/'build_model.py'),'--out',tmp],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ('vertices','faces','materials')}
 stlsame=(root/'nqu-roundhouse-entrance-facade.stl').read_bytes()==(pathlib.Path(tmp)/'nqu-roundhouse-entrance-facade.stl').read_bytes()
 assert all(same.values()) and stlsame
 rebuild={'fresh_process':True,'array_identity':same,'stl_byte_identity':stlsame,'builder_sha256':hashlib.sha256((source_dir/'build_model.py').read_bytes()).hexdigest()}
(root/'qa'/'rebuild-validation.json').write_text(json.dumps(rebuild,indent=2)+'\n')
print(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in screen.items() if k!='records'},indent=2));print(json.dumps(rebuild,indent=2))
