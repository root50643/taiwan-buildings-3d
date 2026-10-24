#!/usr/bin/env python3
"""Original procedural historical exterior approximation; no tracing or image texture.
Categorical source-face IDs survive manifold Boolean union into real face materials.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text());S=P['display_scale_mm'];F=P['front'];H=P['hall'];M=P['main']
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules=[]
def rule(name,classification,evidence,note):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
U=rule('Unobserved closure / manufacture','inferred',[],'Plain rear-central lower closure, capped uncertain roof rectangles, underside and abstract base. No observed finish asserted.')
B=rule('Broad connected brick wings','observed form / approximate dimensions',['S01','S02','S04','S05'],'Outer brick mass extends laterally beyond towers. Library one-wing outline is not a mirrored administration floor plan.')
C=rule('Shallow concave front colonnade','observed / repeated count conventional',['S02','S03','S04','S05'],'Shallow concavity and tall freestanding columns; no exact flutes, capitals, bay counts or decoration claim.')
T=rule('Colonnade-end towers','observed / proportions approximate',['S02','S03','S04'],'Square tower inside total width, open lantern-like simplified cap; outer brick blocks remain.')
D=rule('Central circular hall and windowed drum','observed / hidden junction inferred',['S01','S02','S04','S05'],'Central interface between deep wings, not an outward scallop on each wing end; drum bay count conventional.')
R=rule('Green convex dome and lantern','observed / profile approximate',['S01','S02','S04'],'Rounded dome profile, not a measured hemisphere. Fine ribs and historical repair state omitted.')
W=rule('Rear brick and cream grid','observed rhythm / count approximate',['S01'],'Straight rear, not copied front gallery. Tree-hidden central lower wall deliberately plain.')
G=rule('Visible shallow roof zones','observed / depths inferred',['S04','S06'],'Two broad elongated zones with shallow green bands; ambiguous internal rectangles are closed neutral pads, not courtyards.')
E=rule('Raised front approach','observed / manufactured thickness',['S02','S03','S04'],'Approximate broad stairs and platform, not a surveyed tread count or actual site grading.')

def mesh(v,f,ma,rr):
 v=np.array(v,dtype=np.float32,order="C",copy=True);f=np.array(f,np.uint32,order="C",copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 solid=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert solid.status()==mf.Error.NoError,solid.status();return solid

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma,rr):return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def cyl(x,y,z0,z1,r,ma,rr,n=24,r2=None):return label(mf.Manifold.cylinder(z1-z0,r,r if r2 is None else r2,n).translate((x,y,z0)),ma,rr)
def front(x):return F['center_y']+F['end_rise']*(x/F['half_span'])**2

def poly_solid(poly,zs,side_color,topmat=0,toprule=U):
 # CCW contour, shared boundary rings; cap triangulation preserves every boundary vertex.
 poly=np.asarray(poly,float);n=len(poly);v=[[x,y,z]for z in zs for x,y in poly];f=[];m=[];r=[]
 for j in range(len(zs)-1):
  for i in range(n):
   k=(i+1)%n;mid=(poly[i]+poly[k])/2;ma,rr=side_color(mid,(zs[j]+zs[j+1])/2,i)
   f += [[j*n+i,j*n+k,(j+1)*n+k],[j*n+i,(j+1)*n+k,(j+1)*n+i]];m += [ma]*2;r += [rr]*2
 cap=np.array(mf.triangulate([poly],allow_convex=False))
 f += cap[:,::-1].tolist();m += [0]*len(cap);r += [U]*len(cap)
 f += (cap+(len(zs)-1)*n).tolist();m += [topmat]*len(cap);r += [toprule]*len(cap)
 return mesh(v,f,m,r)
# Shared display plinth. It is not campus landscape, surveyed apron or foundation.
solids=[box(-53,53,-3,43,0,1.1,0,U)]
# Main footprint: straight rear/outer edges, concave front only between tower positions.
# Color changes occur on actual topology, not textures or nearest-neighbor samples.
xs=np.arange(-50,50.0001,.5);ys=np.arange(.5,33.5001,.5)
poly=[(float(x),0)for x in xs]+[(50,float(y))for y in ys]
poly += [(float(x),front(x)-F['wall_setback'] if abs(x)<=35 else 33.5)for x in xs[-2::-1]]
poly += [(-50,float(y))for y in ys[-2::-1]]
zs=sorted(set([1.,5.2,6.,6.2,9.1,9.3,10.0,10.5,11.2,11.4,14.3,14.5,15.2,15.7,16.8,17.0,19.9,20.1,22.1,22.5,23.]))
def wall_color(q,z,i):
 x,y=q
 if z<5.2:return 1,B
 # Rear tree-hidden lower center is deliberately an inferred blank, not a fabricated grid.
 rear=y<.01;side=abs(x)>49.99
 if rear and abs(x)<24 and z<14.5:return 6,U
 rr=W if rear else B
 if not rear and not side and abs(x)<35:
  if z>18.6:return 1,C
  # Tall observed glazing rhythm behind columns; count is explicitly conventional.
  return (5 if (abs(x)+1.3)%4.0<2.1 and 6<z<18.6 else 3),C
 if any(lo<z<hi for lo,hi in [(10.0,10.5),(15.2,15.7)]) or z>22.1:return 2,rr
 u=y if side else x;bay=(u+50)%4.5
 if bay<.5:return 2,rr
 # Three deliberately conventional window rows; smaller panes retain brick-dominant walls.
 for lo,hi in [(6.2,9.1),(11.4,14.3),(17.,19.9)]:
  if lo-.2<z<hi+.2 and 1.0<bay<3.0:
   return (5 if lo<z<hi and 1.4<bay<2.7 else 2),rr
 return 3,rr
solids.append(poly_solid(poly,zs,wall_color,0,U))
# Gallery platform follows the single shallow concavity and joins brick wall.
xg=np.linspace(-35,35,141)
def ribbon(back,forward,z0,z1,ma,rr,decor=False):
 pp=[(float(x),front(x)+back)for x in xg]+[(float(x),front(x)+forward)for x in xg[::-1]]
 if not decor:return poly_solid(pp,[z0,z1],lambda q,z,i:(ma,rr),ma,rr)
 return poly_solid(pp,sorted(set([z0,19.65,21.35,z1])),lambda q,z,i:((5 if i>=len(xg) and 19.65<z<21.35 and (q[0]+35)%4.8<1.15 else ma),rr),ma,rr)
solids += [ribbon(-4.0,1.15,1.0,5.25,1,E),ribbon(-4.0,1.1,18.1,18.7,2,C),ribbon(-.4,.72,18.5,23.1,1,C,True),ribbon(-.6,1.,23.1,23.5,2,C)]
# Conventional 22 columns, including clear central stair alignment. Each is connected at foot and head.
for x in np.linspace(-32,32,F['column_count_convention']):
 y=front(x)
 solids += [cyl(x,y,5.12,5.65,.91,2,C),cyl(x,y,5.5,17.75,F['column_radius'],2,C),cyl(x,y,17.6,18.25,.88,2,C)]
# Broad central stair: four intentionally coarse step masses, not exact tread count.
for i in range(4):
 solids.append(box(-13,13,front(0)-2,47.5-3*i,1.05,1.8+1.15*i,1,E))
# Square towers terminate gallery inside overall building width; outer blocks remain substantial.
for sign in [-1,1]:
 x=sign*F['tower_center_x'];y=F['tower_center_y'];w=F['tower_width']/2
 solids.append(box(x-w,x+w,y-w,y+w,1,25.1,1,T))
 # front window-like shallow recess relief, deliberately not fine door ornament.
 for z0,z1,ww in [(7,10.3,1.4),(13.5,16.5,1.2),(20.8,22.3,.8)]:
  solids.append(box(x-ww/2,x+ww/2,y+w-.02,y+w+.035,z0,z1,5,T))
 solids += [box(x-w-.28,x+w+.28,y-w-.28,y+w+.28,25.0,25.55,2,T),box(x-2.4,x+2.4,y-2.4,y+2.4,25.5,25.9,4,T)]
 # Lower open lantern and roof, then small open cap. No hidden ornament invented.
 for xx in [-1.85,1.85]:
  for yy in [-1.85,1.85]:solids.append(box(x+xx-.4,x+xx+.4,y+yy-.4,y+yy+.4,25.7,28.1,2,T))
 solids += [box(x-2.45,x+2.45,y-2.45,y+2.45,28.,28.55,2,T),box(x-2.2,x+2.2,y-2.2,y+2.2,28.5,28.8,4,T)]
 for xx in [-.88,.88]:
  for yy in [-.88,.88]:solids.append(box(x+xx-.35,x+xx+.35,y+yy-.35,y+yy+.35,28.7,30.2,2,T))
 solids.append(cyl(x,y,30.05,31.1,1.5,4,T,n=32,r2=.15))
# Straight rear modest pale projection and dark entrance; no second curved portico.
solids += [box(-7,7,-1.7,.4,1.0,8.1,1,W),box(-7.4,7.4,-2.0,.5,8.,8.55,2,W),box(-4,4,-1.73,-1.69,2.1,5.3,5,W)]
# Central hall embedded between wings. Drum colors segmented by modeled topology.
cx,cy=H['center'];n=120;angles=np.linspace(0,2*math.pi,n,endpoint=False)
pp=[(cx+H['radius']*math.cos(t),cy+H['radius']*math.sin(t))for t in angles]
def drumcol(q,z,i):
 if z<23.7 or z>28.5:return 2,D
 return (5 if i%8 in [2,3,4] else 1),D
solids.append(poly_solid(pp,[22.5,23.7,28.5,29.3],drumcol,1,D))
solids += [cyl(cx,cy,28.95,29.6,11.0,2,D,n=120)]
# Dome profile rings: convex but not a claim of measured curvature. Flat hidden cap below.
v=[];rings=[(29.45,10.8)]+[(29.5+H['dome_rise']*math.sin(t),10.8*math.cos(t))for t in np.linspace(.06,1.48,19)]
for z,rad in rings:v.extend([[cx+rad*math.cos(t),cy+rad*math.sin(t),z]for t in angles])
f=[]
for j in range(len(rings)-1):
 for i in range(n):k=(i+1)%n;f += [[j*n+i,j*n+k,(j+1)*n+k],[j*n+i,(j+1)*n+k,(j+1)*n+i]]
for j,up in [(0,False),(len(rings)-1,True)]:
 c=len(v);v.append([cx,cy,rings[j][0]])
 for i in range(n):k=(i+1)%n;ff=[c,j*n+i,j*n+k];f.append(ff if up else ff[::-1])
solids.append(mesh(v,f,[4]*len(f),[R]*len(f)))
# Central small open lantern. Posts and cap are thickened for model continuity.
solids.append(cyl(cx,cy,39.25,39.85,1.45,2,R,n=32))
for t in np.linspace(0,2*math.pi,8,endpoint=False):solids.append(cyl(cx+1.1*math.cos(t),cy+1.1*math.sin(t),39.75,42.5,.3,2,R,n=16))
solids += [cyl(cx,cy,42.4,42.85,1.5,2,R,n=32),cyl(cx,cy,42.8,43.8,1.4,4,R,n=32,r2=.15)]
# Shallow capped roof zones. Their rectangular interior pads are NOT courtyard voids.
for sign in [-1,1]:
 x0,x1=(13,48) if sign>0 else (-48,-13)
 solids.append(box(x0,x1,1.0,19.8,22.8,23.75,4,G))
 solids.append(box(x0+3,x1-3,5.2,16.4,23.7,24.2,0,U))
 # Cream edge parapets contain no invented detailed balusters.
 solids += [box(x0,x1,1.,1.6,23.6,24.35,2,G),box(x0,x1,19.2,19.8,23.6,24.35,2,G)]
# Connected union, retaining only exposed faces with their semantic labels.
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.asarray(mm.vert_properties[:,:3],np.float32)*np.float32(S);faces=np.asarray(mm.tri_verts,np.int32);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
assert materials.max()<len(palette) and rule_indices.max()<len(rules)
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0;assert len(t.split(only_watertight=False))==1
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Categorical source-face tags propagated through Boolean union, with real face colors; no image samples or textures.','rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'source_solids':len(solids),'physical_scale_claim':False,'front_towers_are_inside_outer_wing_limits':True,'open_courtyard_voids':0,'exact_admin_floorplan_claim':False}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
