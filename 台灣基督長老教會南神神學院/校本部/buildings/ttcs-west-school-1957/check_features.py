"""Actual exported triangles: air/solid probes, through rays, local sections. No healing."""
from pathlib import Path
import json,struct,hashlib
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection
A=Path(__file__).resolve().parent
raw=(A/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False)
def coord(p):return (np.array(p)-[4.25,16.35,0])*5.5
samples=[]
def probe(label,p,solid):
 actual=bool(m.contains([coord(p)])[0]);assert actual==solid,(label,actual);samples.append(dict(label=label,point_mm=coord(p).tolist(),expected_solid=solid,actual_solid=actual))
for i in range(9):
 y=1.75+3.5*i;probe('east gallery bay '+str(i),(7.2,y,1.7),False)
 if i!=4:probe('east arch mouth '+str(i),(8.35,y,1.7),False)
for x in [.2,2,4,6,7.5,8.35]:probe('central east west passage '+str(x),(x,15.75,1.8),False)
probe('south gallery mouth',(7.3,.15,1.8),False)
for y in [32,33,34]:
 probe('north connector lower open '+str(y),(7.3,y,1.7),False)
 probe('north connector upper open '+str(y),(7.3,y,6.2),False)
for p,label in [((1,8,2),'office volume'),((8.35,7,2),'arcade pier'),((4,10,6),'upper interior simplified'),((7.3,33,4.2),'connector floor'),((4,16,9),'single roof')]:probe(label,p,True)
probe('north upper D2 doorway proxy',(7.4,31.60,5.2),True)
probe('north upper flanking window proxy',(6.52,31.60,6.2),True)
rays=[]
for label,start,direction,length in [('central complete east west',(-1,15.75,1.8),(1,0,0),11),('south gallery along length',(7.3,-1,1.8),(0,1,0),32.5),('north open terminal',(7.3,32,6.2),(0,1,0),3.5)]:
 loc,_,_=m.ray.intersects_location([coord(start)],[direction],multiple_hits=True);ds=np.dot(np.asarray(loc).reshape(-1,3)-coord(start),np.array(direction));hits=ds[(ds>1e-5)&(ds<length*5.5)];assert len(hits)==0,(label,hits);rays.append(dict(label=label,start_mm=coord(start).tolist(),direction=direction,clear_length_mm=length*5.5,hits_within_clear_segment=len(hits)))
rawman=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)))
sections=[]
# Local gallery and passage rectangles intersect exact raw-STL horizontal sections.
from shapely.geometry import box
for z in [1.0,1.8,2.5,3.0,4.2,5.0,6.2]:
 geom=GeometryCollection()
 for p in rawman.slice(z*5.5).to_polygons():geom=geom.symmetric_difference(Polygon(p))
 assert geom.is_valid
 for label,bounds in [('central_passage',(0,8.5,14.6,16.9)),('east_gallery',(6.5,8.0,.5,31.0)),('north_connector',(6.6,8.1,31.7,34.0))]:
  a,b,c,d=bounds;lo=coord((a,c,z));hi=coord((b,d,z));q=geom.intersection(box(lo[0],lo[1],hi[0],hi[1]));sections.append(dict(label=label,z_mm=z*5.5,solid_area_mm2=q.area,valid=q.is_valid))
report=dict(stl_sha256=hashlib.sha256(raw).hexdigest(),method='Raw exported STL exact-coordinate welding, trimesh parity contains and multi-hit ray intersection; manifold raw horizontal slice local intersections',samples=samples,rays=rays,local_sections=sections,source_features={'east_upper_arch_windows':9,'west_upper_arch_windows':8,'west_north_small_rectangles':3,'east_ground_arches':8,'east_gallery_doors':5,'east_gallery_windows':8,'north_upper_D2_and_flanking_window':True,'central_flat_top_passage':1,'single_hip_roof':1,'north_connector_bays':1},thin_features_mm={'window_grille':.33,'downpipe':.715,'tile_course':.3025},supports_required=['8 arcade arches and south arch','north connector arches and upper lintels','shallow canopies','hip roof eaves'],physical_print_tested=False,minimum_wall_certification=False,limitations='Fine grilles tile texture and pipes are visual miniature approximations. Slices are not full wall-normal thickness certification; horizontal roofs and unsupported arches need slicer-specific supports.')
(A/'qa/feature-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FEATURES PASS',len(samples),len(rays),len(sections))
