"""Photo-interpreted Guoding Library miniature. Units: mm. No surveyed dimensions."""
import os, math,json
import numpy as np
import manifold3d as m
import trimesh
OUT=os.path.dirname(os.path.abspath(__file__))
def cube(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def ellipse(rx,ry,z,h):return m.Manifold.cylinder(h,1,circular_segments=256).scale((rx,ry,1)).translate((0,0,z))
def union(a):return m.Manifold.batch_boolean(a,m.OpType.Add)
# Continuous printable mass and low display base; front is negative Y.
add=[cube(0,0,1.5,150,104,3),ellipse(67,38,2.5,2.5),ellipse(62,31,4.8,46.2)]
# Foundation follows hillside. Facade ground level and upper floor bands.
add += [ellipse(62.7,31.7,15,1.6),ellipse(62.6,31.6,49.8,1.6)]
# Characteristic raised oval roof ring, with stout columns.
ring=ellipse(65,34,56,2.0)-ellipse(58.0,27.0,55.8,2.5)
add += [ring]
for a in np.linspace(0,2*math.pi,18,endpoint=False):
 add += [cube(61*math.cos(a),30*math.sin(a),53.5,2.0,2.0,6.0)]
# Distinct tall left stair/sign tower.
add += [cube(-42,-22,32.3,17.5,24,57.5)]
# Front portal and entrance canopy with connected columns.
add += [cube(-22,-31,13.7,40,12,18.0), cube(-21,-37,23.2,44,9,2.5)]
add += [cube(1,-38,15.3,89,8,1.5)]
for x in [-41,-26,-11,4,19,34,44]:add += [cube(x,-40.5,9.8,1.5,1.5,11.2)]
# Main projecting dark-framed square feature, reproduced in relief, not paint.
add += [cube(26,-28.5,33.1,20.5,8.5,19.7)]
# Approach steps, terrace and flanking planters. No fragile trees or lamp posts.
for i in range(5):add += [cube(-3,-47+i*1.7,3.2+i*.38,30,5.5,1.1+i*.75)]
for x in [-35,29]:add += [cube(x,-45,4.1,21,5,2.4)]
body=union(add)
cut=[]
# Radial relief windows, not through-openings: keep closed printable walls.
def window_arc(a,z,w,h,depth=.9):
 x,y=62*math.cos(a),31*math.sin(a)
 w=min(w, .70*2*math.pi/100*math.sqrt((62*math.sin(a))**2+(31*math.cos(a))**2))
 normal=np.array([math.cos(a)/62,math.sin(a)/31]);normal/=np.linalg.norm(normal)
 angle=math.degrees(math.atan2(normal[1],normal[0]))
 return m.Manifold.cube((depth*2,w,h),True).rotate((0,0,angle)).translate((x+normal[0]*.1,y+normal[1]*.1,z))
# Top ribbon encircles the volume. Side/back windows on lower floors.
for a in np.linspace(0,2*math.pi,100,endpoint=False):
 cut.append(window_arc(a,47.9,2.7,2.8))
 if math.sin(a)>-.48 or abs(math.cos(a))>.87:
  for z in [21.0,29.0,37.0]:cut.append(window_arc(a,z,2.7,3.4))
# Lower-level windows along curved side/back.
for a in np.linspace(0,2*math.pi,74,endpoint=False):
 if math.sin(a)>-.45 or abs(math.cos(a))>.88:cut.append(window_arc(a,10.6,3.7,7.4))
# Front wall horizontal windows positioned to follow oval curve.
for xs,z in [([-28,-24,-20,-16,-12],36.5), ([-9,-5,-1,3,7],36.5), ([-28,-24,-20,-16,-12],28.0)]:
 for x in xs:
  y=-31*math.sqrt(max(0,1-(x/62)**2))
  cut.append(cube(x,y-.05,z,3.3,1.9,2.5))
for x,z,h in [(12,35,6),(18,27,5),(7,23,5),(-2,25,5)]:
 y=-31*math.sqrt(1-(x/62)**2);cut.append(cube(x,y-.1,z,1.4,1.8,h))
# Tower vertical glass strip, discretized with robust crosspieces.
for z in np.arange(9.0,56.0,5.0):cut.append(cube(-48,-34.1,z,1.8,1.7,4.3))
# Entrance glazing backed by a solid body.
for x in np.arange(-39,-3,4.0):cut.append(cube(x,-37.05,13.2,3.2,1.6,15.5))
# Projecting frame face: two-storey opening with thick center mullion.
for x in [21.5,26,30.5]:
 for z in [28.5,36.8]:cut.append(cube(x,-32.8,z,3.7,1.6,6.5))
# Attached curtain-wall panel just right of the square feature.
for x in [39,42,45]:
 for z in [26,30,34,38]:
  y=-31*math.sqrt(1-(x/62)**2)
  cut.append(cube(x,y-.1,z,2.25,1.8,3.2))
body=body-union(cut)
print('Boolean status:',body.status())
mesh=body.to_mesh(); tm=trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:,:3],faces=np.array(mesh.tri_verts),process=True)
# Remove fully enclosed relief pockets hidden behind facade additions.
components=tm.split(); tm=max(components,key=lambda c:c.volume)
tm.export(OUT+'/guoding_library_150mm.stl')
report={'dimensions_mm':tm.extents.tolist(),'watertight':bool(tm.is_watertight),'winding_consistent':bool(tm.is_winding_consistent),'connected_components':len(tm.split()),'volume_mm3':float(tm.volume),'faces':len(tm.faces),'units':'millimeters','basis':'Photo interpretation; dimensions are not a measured architectural survey. Main front and side details modeled; unseen rear simplified.','printing':'Flat base on bed; 0.4 mm nozzle, 0.16–0.20 mm layers. Roof ring and canopy may need support; inspect slicer preview. No physical print test.'}
open(OUT+'/validation.json','w').write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
