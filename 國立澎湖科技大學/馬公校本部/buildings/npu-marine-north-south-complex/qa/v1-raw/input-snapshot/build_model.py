"""Original normalized reconstruction of NPU Marine Science & Technology group.
All geometry coordinates and STL numbers are millimetres. No source pixels embedded.
Run: python source/build_model.py (numpy, trimesh, shapely, manifold3d required).
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon,box as sbox
from shapely.ops import triangulate

ROOT=Path(__file__).resolve().parents[1]
for d in ['models','qa']: (ROOT/d).mkdir(exist_ok=True)
COLORS={'cream':[0.80,0.78,0.66,1],'slate':[0.19,0.30,0.34,1],'ochre':[0.87,0.60,0.10,1],'terracotta':[0.71,0.25,0.10,1]}
regions=[]
def box(x0,x1,y0,y1,z0,z1):
 m=tm.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m
def uni(ms): return tm.boolean.union(ms,engine='manifold',check_volume=True)
def diff(m,ms):return tm.boolean.difference([m,uni(ms)],engine='manifold',check_volume=True) if ms else m
def prism(poly,z0,z1):
 p=Polygon(poly) if not isinstance(poly,Polygon) else poly
 verts=[];faces=[];lookup={}
 for tri in triangulate(p):
  if not p.covers(tri.representative_point()):continue
  ids=[]
  for xy in list(tri.exterior.coords)[:3]:
   xy=tuple(xy)
   if xy not in lookup:lookup[xy]=len(verts);verts.append(xy)
   ids.append(lookup[xy])
  faces.append(ids)
 m=tm.creation.extrude_triangulation(np.array(verts),np.array(faces),z1-z0);m.apply_translation([0,0,z0]);return m
def region(part,col,bounds,reason):regions.append({'part':part,'color':col,'bounds_mm':bounds,'reason':reason})
def facade_x(part,x0,x1,y,levels,inward):
 # recesses are blind, 0.8mm deep. No unremovable internal supports.
 cuts=[];rails=[]
 for z in levels:
  for x in np.arange(x0+2,x1-3,6.0):
   ya,yb=(y-0.02,y+0.8) if inward==1 else (y-0.8,y+0.02)
   cuts.append(box(x,x+3.6,ya,yb,z+2.2,z+6.5))
   region(part,'slate',[[x-0.02,min(ya,yb)-0.03,z+2.18],[x+3.62,max(ya,yb)+0.03,z+6.52]],'blind window recess from photos; repeated rhythm simplified')
   # short solid rail ribbon below window; enlarged to 0.9mm high.
   ya,yb=(y-0.45,y+0.2) if inward==1 else (y-0.2,y+0.45)
   rails.append(box(x,x+3.6,ya,yb,z+1.25,z+2.15))
   region(part,'ochre',[[x-0.01,ya-0.01,z+1.24],[x+3.61,yb+0.01,z+2.16]],'solid enlarged rail band, not miniature individual bars')
 return cuts,rails
def facade_y(part,y0,y1,x,levels,inward):
 cuts=[];rails=[]
 for z in levels:
  for y in np.arange(y0+2,y1-3,6.):
   xa,xb=(x-0.02,x+0.8) if inward==1 else (x-0.8,x+0.02)
   cuts.append(box(xa,xb,y,y+3.6,z+2.2,z+6.5))
   region(part,'slate',[[min(xa,xb)-0.03,y-0.02,z+2.18],[max(xa,xb)+0.03,y+3.62,z+6.52]],'blind photo window rhythm, approximate')
   xa,xb=(x-0.45,x+0.2) if inward==1 else (x-0.2,x+0.45)
   rails.append(box(xa,xb,y,y+3.6,z+1.25,z+2.15))
   region(part,'ochre',[[xa-0.01,y-0.01,z+1.24],[xb+0.01,y+3.61,z+2.16]],'enlarged solid railing ribbon')
 return cuts,rails
N=[(0,0),(100,0),(100,48),(87.2,48),(87.2,34.1),(0,34.1)]
NU=[(0,0),(100,0),(100,48),(87.2,48),(87.2,34.1),(22,34.1),(22,48),(0,48)]
S=[(106.2,80.7),(159.8,80.7),(159.8,93.6),(159.5,93.6),(159.5,149.6),(145.7,149.6),(145.7,162.8),(140,162.8),(140,149.6),(125.4,149.6),(125.4,102.7),(106.2,102.7)]
H=[(-41.2,7),(-24,-4.4),(-3.6,4),(0,4),(0,30),(-3.6,30),(-24,38.3),(-41.2,27)]
B=[(86.7,48),(91.1,48),(91.1,88.9),(106.2,88.9),(106.2,93.3),(91.1,93.3),(91.1,97.8),(86.7,97.8),(86.7,93.3),(82.1,93.3),(82.1,88.9),(86.7,88.9)]
meshes={};assembly={}
def save(id,m,offset=(0,0,0),quantity=1,notes=''):
 m.process(validate=True);tm.repair.fix_normals(m,multibody=True)
 origin=np.array(m.bounds[0]);m.apply_translation(-origin)
 file=f'models/{id}.stl';m.export(ROOT/file)
 trans=np.eye(4);trans[:3,3]=origin+np.array(offset)
 meshes[id]=m;assembly[id]={'id':id,'stl':file,'assembly_transform':trans.tolist(),'expected_components':1,'min_feature_mm':0.9,'quantity':quantity,'supports':'none','notes':notes,'bounds_print_mm':m.extents.tolist(),'sha256':hashlib.sha256((ROOT/file).read_bytes()).hexdigest()}
 # color selectors remain in assembled coordinates before origin removal.
 return m

# North two body pieces. Upper footprint can rest directly on the print bed,
# while assembled it spans the open two-level entrance on six columns.
id='01-north-lower';m=prism(N,0,18);cuts=[];rails=[]
for y,a,b,dr in [(0,0,100,1),(34.1,22,87.2,-1)]:
 c,r=facade_x(id,a,b,y,[0,9],dr);cuts+=c;rails+=r
m=uni([diff(m,cuts),*rails,prism(H,0,11),box(-2,1,5,29,0,11)])
for x in [1.2,11,20.8]:
 for y in [36.2,46.4]:m=uni([m,box(x-0.9,x+0.9,y-0.9,y+0.9,0,18),box(x-1.2,x+1.2,33.9,y+0.9,0,1.2)])
save(id,m,notes='Includes north hall single low body and open entrance piloti; no auditorium upstairs rooms.')
id='02-north-upper';m=prism(NU,18,36);cuts=[];rails=[]
for y,a,b,dr in [(0,0,100,1),(34.1,22,87.2,-1),(48,0,22,-1)]:
 c,r=facade_x(id,a,b,y,[18,27],dr);cuts+=c;rails+=r
m=uni([diff(m,cuts),*rails])
# Thin roof parapets and raised stair fins, explicit estimated heights.
for a,b,y in [(0,100,0),(22,87.2,34.1),(0,22,48)]:
 m=uni([m,box(a,b,y-0.1,y+1.1,35.9,37.2)])
for x in [1,22,43,64,85]:m=uni([m,box(x,x+9,0,2.6,37.1,38.3)])
for x in [87.2,98.8]:
 # convex sloping fin y37..48, roof heights40..43
 verts=[[x,y,z] for x in [x,x+1.2] for y,z in [(36,35.9),(48,35.9),(48,43),(36,39.5)]]
 m=uni([m,tm.convex.convex_hull(verts)])
region(id,'terracotta',[[0,47.8,18],[1.3,49.2,36]],'entry bay orange accent approximation')
save(id,m,notes='Print upright on expanded footprint; joins lower at z18. Roof/stair heights estimated, not common real floor height.')

# South 3F L body. Floors are represented by blind recess rhythms only.
id='03-south-body';m=prism(S,0,27);cuts=[];rails=[]
for y,a,b,dr in [(80.7,106.2,159.8,1),(93.6,116.5,125.4,-1),(149.6,125.4,159.5,-1)]:
 c,r=facade_x(id,a,b,y,[0,9,18],dr);cuts+=c;rails+=r
for x,a,b,dr in [(125.4,102.7,149.6,1),(159.5,93.7,149.6,-1)]:
 c,r=facade_y(id,a,b,x,[0,9,18],dr);cuts+=c;rails+=r
m=uni([diff(m,cuts),*rails])
for a,b,y in [(106.2,159.8,80.7),(125.4,159.5,149.6)]:m=uni([m,box(a,b,y-0.1,y+1.1,26.9,28.2)])
for y in [101,120,139]:m=uni([m,box(125.4,128,y,y+8,28.1,29.3)])
for x in [106.2,114.6]:
 verts=[[x,y,z] for x in [x,x+1.2] for y,z in [(91,26.9),(103,26.9),(103,34),(91,30.5)]]
 m=uni([m,tm.convex.convex_hull(verts)])
save(id,m,notes='3F L body and terminal stair projection; 9mm model storey pitch is a display estimate, no surveyed heights.')

# Polygon roof of single-storey conference hall: flat underside and low peak.
id='04-hall-roof';base=prism(H,11,12.2)
v=[[x,y,12.1] for x,y in H]+[[-22,17,15.0]]
m=uni([base,tm.convex.convex_hull(v)])
save(id,m,notes='Low polygon/fan roof; slope and peak are estimated. Separate roof avoids hidden supports in hall.')

# L bridge split into an open tray and a flat removable lid; never fill below.
id='05-bridge-tray';poly=Polygon(B);inner=poly.buffer(-1.2,join_style=2)
wall=prism(poly,10.6,16.3)
wall=diff(wall,[prism(inner,10.5,16.4)])
m=uni([prism(poly,9,10.6),wall]);cuts=[]
for y in np.arange(53,87,6):
 cuts += [box(86.6,88.0,y,y+2,12.2,14.5),box(89.8,91.2,y,y+2,12.2,14.5)]
for x in [94,100]:cuts += [box(x,x+2,88.8,90.2,12.2,14.5),box(x,x+2,92.0,93.4,12.2,14.5)]
m=diff(m,cuts)
save(id,m,notes='Upright open tray, 1.2mm walls and 1.6mm floor, accessible inside; no ceiling bridge during print.')
id='06-bridge-lid';save(id,prism(poly,16.3,17.5),notes='Print flat. Glue onto open tray after clearing window openings. No support trapped inside.')
id='07-bridge-pier';m=uni([box(-1.7,1.7,-1.7,1.7,0,1.2),box(-0.9,0.9,-0.9,0.9,1.1,9)])
save(id,m,notes='Repeat three times, upright; post locations approximated from exterior photographs.')
# Replace single prototype location with three assembled instances.
base=assembly.pop(id)
for i,(x,y) in enumerate([(88.9,62),(88.9,78),(94,91.1)],1):
 item=dict(base);item['id']=f'07-pier-instance-{i}';T=np.eye(4);T[:3,3]=[x-1.7,y-1.7,0];item['assembly_transform']=T.tolist();item['prototype']='07-bridge-pier';assembly[item['id']]=item

parts=list(assembly.values());contacts=[]
for a,b in [('01-north-lower','02-north-upper'),('01-north-lower','04-hall-roof'),('01-north-lower','05-bridge-tray'),('03-south-body','05-bridge-tray'),('05-bridge-tray','06-bridge-lid')]+[(f'07-pier-instance-{i}','05-bridge-tray') for i in range(1,4)]:
 contacts.append({'a':a,'b':b,'max_intersection_mm3':0.002,'min_clearance_mm':0,'max_clearance_mm':0.02,'kind':'designed planar butt/glue joint, no press fit'})
manifest={'units':'mm','model_scale':'Normalized plan proportions, north main bar100mm; no measured real-world scale asserted.','parts':parts,'expected_contacts':contacts,'section_heights_mm':[0.6,5,9.5,12.5,17,18.5,25,28,35,40],'colors':COLORS,'color_regions':regions,'floor_pitch_model_mm':9,'physical_part_count':9,'distinct_stl_count':7,'minimum_constructed_rail_mm':0.9,'minimum_wall_mm':1.2,'assembly_notes':'No base slab. Open courtyard, 9mm bridge clearance; two-level entrance void below north upper left wing. All joins are planar adhesive contacts; physical fit untested.'}
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n','utf-8')
(ROOT/'source/color-regions.json').write_text(json.dumps({'materials':COLORS,'regions':regions},indent=2)+'\n','utf-8')
(ROOT/'source/plan-trace.json').write_text(json.dumps({'coordinate_system':'x right/y down on official PDF; display coordinates only, not geographic north','north_main_plan_100mm':N,'north_upper':NU,'south':S,'hall':H,'bridge':B,'north_2F_reference_px':{'origin':[265,499],'pixels_per_model_mm':4.05},'south_2F_to_north_2F_translation_px':[217,261],'registration_uncertainty_px':2,'sources':'Official north and south 2F, matched bridge width; exterior photos for elevations.'},ensure_ascii=False,indent=2)+'\n','utf-8')
whole=[]
for item in parts:
 m=meshes[item.get('prototype',item['id'])].copy();m.apply_transform(item['assembly_transform']);whole.append(m)
tm.util.concatenate(whole).export(ROOT/'models/assembly-reference-do-not-print.stl')
print(json.dumps({'parts':len(parts),'stls':len(meshes),'bounds_mm':tm.util.concatenate(whole).bounds.tolist()},indent=2))
