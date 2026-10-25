"""Independent reloaded-STL topology, layers, thin-feature screen and bounded ray controls.
python validate_model.py [--out DIRECTORY]. Not an FFF toolpath or physical print certificate.
"""
import argparse,pathlib,json,hashlib
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();r=a.out;(r/'qa').mkdir(exist_ok=True)
m=trimesh.load_mesh(r/'model.stl',process=True);edges=Counter(tuple(sorted((int(f[i]),int(f[(i+1)%3]))))for f in m.faces for i in range(3));links=defaultdict(list)
for f in m.faces:
 for i in range(3):links[int(f[i])].append((int(f[(i+1)%3]),int(f[(i+2)%3])))
bad=[]
for v,es in links.items():
 adj=defaultdict(set)
 for x,y in es:adj[x].add(y);adj[y].add(x)
 seen=set();todo=[next(iter(adj))]
 while todo:
  x=todo.pop()
  if x in seen:continue
  seen.add(x);todo.extend(adj[x]-seen)
 if len(seen)!=len(adj)or any(len(s)!=2 for s in adj.values()):bad.append(v)
mesh={'artifact':'model.stl','sha256':hashlib.sha256((r/'model.stl').read_bytes()).hexdigest(),'vertices':len(m.vertices),'triangles':len(m.faces),'shells':len(m.split(only_watertight=False)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'volume_mm3':float(m.volume),'edge_incidence':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'bounds_mm':m.bounds.tolist(),'euler_characteristic':m.euler_number}
assert mesh['shells']==1 and mesh['watertight'] and mesh['winding_consistent'] and mesh['volume_mm3']>0
assert not any(mesh[k] for k in ['nonmanifold_edges','nonmanifold_vertex_links','degenerate_triangles','duplicate_triangles'])
(r/'qa/mesh-validation.json').write_text(json.dumps(mesh,indent=2)+'\n')
s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)));assert s.status()==mf.Error.NoError
records=[];prev=None
for z in np.arange(.071,m.bounds[1,2],.2):
 g=GeometryCollection()
 for poly in s.slice(float(z)).to_polygons():
  if len(poly)>2:g=g.symmetric_difference(Polygon(poly))
 assert g.is_valid and not g.is_empty
 loss=g.difference(g.buffer(-.4).buffer(.4)).area
 records.append({'z_mm':round(float(z),3),'area_mm2':round(g.area,5),'regions':len(g.geoms)if hasattr(g,'geoms')else 1,'opening_0_8mm_loss_mm2':round(loss,5),'opening_0_8mm_loss_percent':round(100*loss/g.area,5),'growth_beyond_previous_plus_0_4mm_mm2':0 if prev is None else round(g.difference(prev.buffer(.4)).area,5)})
 prev=g
section={'method':'Every 0.2mm section from z=0.071mm, no polygon repairs; morphological 0.8mm opening is not minimum-wall metrology or slicer proof','sections':len(records),'all_valid_nonempty':True,'max_regions':max(x['regions']for x in records),'max_opening_loss_percent':max(x['opening_0_8mm_loss_percent']for x in records),'max_growth_mm2':max(x['growth_beyond_previous_plus_0_4mm_mm2']for x in records),'warnings':['Two-level portico soffits, crown overhangs and arches require support/bridge assessment.','Window/sill relief ribs are backed by solid mass, but some are only about 0.3–0.4mm wide; entry mullions about 0.44mm. Fine relief may be lost at coarse nozzle settings.','Roof rim nominal thickness is 1.0mm; a real slicer, machine-specific reslice and physical test remain required.','No support-removal, adhesion, strength, dimensional or full wall-thickness certification.'],'records':records}
(r/'qa/section-screen.json').write_text(json.dumps(section,indent=2)+'\n')
checks=[]
# Both halves of every named gap test: open segment followed by its solid backing/soffit.
for face,axis,side,coord in [('south',1,-1,0),('north',1,1,0),('east',0,1,18.48),('west',0,-1,18.48)]:
 start=[0.,0.,86.77];start[axis]=side*80.;start[1-axis]=coord;direction=[0.,0.,0.];direction[axis]=-side
 surface=66.3 if axis==1 else 38.2;backing=surface-4.3
 checks.append((face+'_arch_open',start,direction,80-surface+2,True));checks.append((face+'_arch_backing',start,direction,80-backing+1,False))
for side,face in [(-1,'south'),(1,'north')]:
 checks +=[(face+'_portico_open',[0,side*70,6],[0,-side,0],20,True),(face+'_portico_entry_backing',[0,side*70,6],[0,-side,0],26,False),(face+'_portico_open_below_soffit',[0,side*55,8],[0,0,1],6,True),(face+'_portico_soffit',[0,side*55,8],[0,0,1],12,False),(face+'_column_occupied_control',[11.25,side*70,6],[0,-side,0],12,False)]
checks +=[('east_3F_connector_scope_cap',[40,-10.6,21],[-1,0,0],8,False),('west_3F_connector_scope_cap',[-40,-10.6,21],[1,0,0],8,False),('east_crown_center_pair_separator',[45,0,86.77],[-1,0,0],9,False),('west_crown_center_pair_separator',[-45,0,86.77],[1,0,0],9,False),('roof_single_machine_occupied',[0,6.6,110],[0,0,-1],10,False),('roof_no_displaced_second_machine',[0,40,110],[0,0,-1],12,True),('roof_deck_backing',[0,40,110],[0,0,-1],16,False)]
results=[]
for name,start,direction,length,clear in checks:
 loc,_,_=m.ray.intersects_location([start],[direction],multiple_hits=True);dist=np.linalg.norm(np.asarray(loc).reshape((-1,3))-np.asarray(start),axis=1);hits=dist[(dist>1e-5)&(dist<length)];actual=len(hits)==0;assert actual==clear,(name,hits)
 results.append({'name':name,'start_mm':start,'direction':direction,'length_mm':length,'expected_clear':clear,'actual_clear':actual,'within_segment_hits':len(hits)})
# Actual exported mesh must retain complete round columns, including the inner portico half.
param=json.loads((r/'params.json').read_text());inside=[];outside=[]
for side in [-1,1]:
 for x in param['column_x_m']:
  for theta in np.linspace(0,2*np.pi,32,endpoint=False):
   inside.append([2*x+1.15*np.cos(theta),2*side*param['column_y_m']+1.15*np.sin(theta),6.0])
   outside.append([2*x+1.50*np.cos(theta),2*side*param['column_y_m']+1.50*np.sin(theta),6.0])
assert m.contains(inside).all(),'A portico column was clipped or hollowed'
assert not m.contains(outside).any(),'Unexpected occupied area outside round portico columns'
(r/'qa/column-section-controls.json').write_text(json.dumps({'all_pass':True,'columns':8,'section_z_mm':6.0,'inside_samples':len(inside),'inside_radius_mm':1.15,'outside_samples':len(outside),'outside_radius_mm':1.50,'meaning':'Actual mesh full-circle inclusion/exclusion tests, including inner portico halves'},indent=2)+'\n')
(r/'qa/ray-controls.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Independent STL ray/triangle intersections bounded to stated segments; includes occupied controls','checks':results},indent=2)+'\n')
print(json.dumps(mesh));print('sections',len(records),'max 0.8mm loss%',section['max_opening_loss_percent'],'rays',len(results))
