"""Original bounded CMU Guanhuai exterior. Metres E/N/up; no third-party mesh.
Student association 1–13F schematic topology, architect completed photos,
CMU official roof/back/ground images and NLSC2024. Visual candidate only.
"""
from pathlib import Path
import numpy as np,math,json,trimesh
from manifold3d import Manifold,Mesh,CrossSection,OpType
R=Path(__file__).resolve().parent
BASE=2.;S=148/55.2;N=128
parts=[]
def box(x0,x1,y0,y1,z0,z1):return Manifold.cube(((x1-x0)*S,(y1-y0)*S,(z1-z0)*S)).translate((x0*S,y0*S,BASE+z0*S))
def contour(rx,ry,n=3.15,cx=0,cy=0):
 t=np.arange(N)*2*math.pi/N;c=np.cos(t);s=np.sin(t)
 return np.array([cx+rx*np.sign(c)*abs(c)**(2/n),cy+ry*np.sign(s)*abs(s)**(2/n)]).T
def loft(levels,n=3.15):
 # levels (z,rx,ry,cx,cy), closed, consistently wound original triangulation
 v=[]
 for z,rx,ry,cx,cy in levels:
  pp=contour(rx,ry,n,cx,cy);v.extend([[x*S,y*S,BASE+z*S] for x,y in pp])
 faces=[]
 for j in range(len(levels)-1):
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=(j+1)*N+k;d=(j+1)*N+(k+1)%N
   faces.extend([[a,b,d],[a,d,c]])
 for k in range(1,N-1):faces.append([0,k+1,k]);faces.append([(len(levels)-1)*N,(len(levels)-1)*N+k,(len(levels)-1)*N+k+1])
 return Manifold(Mesh(np.array(v,dtype=np.float32),np.array(faces,dtype=np.uint32)))
def oval(rx,ry,z,h,cx=0,cy=0,n=3.15):return loft([(z,rx,ry,cx,cy),(z+h,rx,ry,cx,cy)],n)
def sphere(cx,cy,cz,rx,ry,rz):return Manifold.sphere(1,80).scale((rx*S,ry*S,rz*S)).translate((cx*S,cy*S,BASE+cz*S))
def mouth_tunnel(cy,cz,ry,rz,xback):
 t=np.linspace(0,2*math.pi,129)[:-1]
 poly=np.array([[cy+ry*math.cos(a),cz+rz*math.sin(a)] for a in t])*S
 return CrossSection([poly]).extrude((xback+30)*S).transform(np.array([[0,0,1,-30*S],[1,0,0,0],[0,1,0,BASE]]))
def union(p):return Manifold.batch_boolean(p,OpType.Add)
def slant(x,y,z1,z2,dx,dy,w=1.05):return loft([(z1,w/2,w/2,x,y),(z2,w/2,w/2,x+dx,y+dy)],4)
# restrained real base, all extents <=150mm, source grade landscaping omitted.
parts.append(Manifold.cube((42*S,51*S,BASE)).translate((-21*S,-25.5*S,0)))
# Three low-floor volumes follow asymmetric stepped curve lobes. East side has
# two rounded wings, west entrance notch; transparent glass simplified backed.
low=[]
for i,z in enumerate([0,4.35,8.7]):
 rx=[14.0,14.8,15.4][i];ry=[19.5,20.3,20.8][i]
 core=oval(rx-2.4,ry-1.8,z,4.55)
 # East ground approach remains deeply recessed between two low curved lobes.
 core-=box(5.2,24,-3.1,3.1,z-.05,z+4.60)
 # approach open recess on west, varying depth, real back remains.
 core-=box(-24,-3.7,-3.4,3.4,z-.05,z+4.60)
 # setbacks at north-west corner produce continuous but unequal lobes.
 core-=box(-24,-7.0,13.0,24,z-.05,z+4.60)
 # shallow panel reveals only; retain broad glass backs rather than lattices
 for side in [-1,1]:
  for yy in np.arange(-17,18,4):
   if abs(yy)<4:continue
   xx=side*(rx-1.1); core-=box(xx-.2,xx+.2,yy,yy+2.6,z+.7,z+3.45)
 low.append(core)
 floor=oval(rx,ry,z,1.00)
 floor-=box(5.2,24,-3.1,3.1,z-.05,z+1.05)
 floor-=box(-24,-3.7,-3.4,3.4,z-.05,z+1.05)
 floor-=box(-24,-7,13,24,z-.05,z+1.05)
 low.append(floor)
 # varied west curved lobes sweep outward, slab-backed broad guard profile.
 for cy,rry in [(-11.2,8.4),(10,7.2)]:
  if cy>0 and i==2:continue
  extension=oval(7.4,rry,z+.0,1.0,-11.0,cy,2.3)
  low.append(extension)
  # protected solid glass/parapet core, recessed above broad slab
  low.append(oval(5.4,rry-1.5,z+1.0,2.3,-9.4,cy,2.3))
 # East photograph shows two lower lobes, with recessed glass rather than
 # the upper envelope extruded to ground. Heights bounded by 1–2F plan.
 if i<2:
  for cy,rry in [(-10.2,7.5),(10.2,7.0)]:
   low.append(oval(6.0,rry,z,1.0,10.5,cy,2.5))
   low.append(oval(4.5,rry-1.1,z+1.0,3.4,9.7,cy,2.5))
parts+=low
# Broad front slanted columns visible in completed low-angle source.
for y,dy in [(-3.8,-1.7),(4.3,1.7)]:parts.append(slant(-18.1,y,0,13.45,1.72,dy,1.60))
# Central entrance staircase is solid and has a real deep recessed back.
for j in range(7):parts.append(box(-20.5+j*.8,-3.65,-2.7,2.7,0,.25+j*.20))
# Main 4–13F ten storeys, gently narrowing upper profile. Long axis N/S.
floors=[13.05+i*3.65 for i in range(11)]
def dims(z):
 # schematic floor scale + high-angle photographic taper; not measured survey
 t=np.clip((z-13.05)/(49.55-13.05),0,1)
 factor=1-.12*t**3
 return 16.7*factor,21.7*factor
def shell(a,b,inset=0):
 lev=[]
 for z in np.linspace(a,b,max(2,int((b-a)/.7)+1)):
  x,y=dims(z);lev.append((z,x-inset,y-inset,0,0))
 return loft(lev)
# Western voids: two enclosed-height hollows and one high north-side terrace.
# Mouth positions follow independent floor groups, not mirrored onto east.
voids=[(-20.0,7.7,18.6,9.2,5.7,6.0),(-20.0,-6.8,29.55,9.2,5.7,6.0),(-16.4,20.5,42.6,9.0,7.0,8.0)]
# Separate floor-specific terrace landings. The opening is a backed exterior
# recess, not a smooth spherical indentation. Width/depth remain photo bounds.
terrace_specs={0:(7.7,2.0,4.7,10.7),1:(7.7,5.3,5.6,11.5),2:(7.7,4.8,2.5,10.6),
 3:(-6.8,2.0,4.7,10.7),4:(-6.8,5.3,5.6,11.5),5:(-6.8,4.8,2.5,10.6),
 6:(19.5,3.8,5.7,12.4),7:(19.5,5.5,6.4,12.8),8:(19.5,6.8,6.6,12.8),9:(19.5,6.3,5.8,12.2)}
# Single uninterrupted primary body avoids near-coincident inside faces from
# separately unioned floor/band shells. All recesses subtract from this body.
main=shell(13.00,50.12,0)
for i in range(10):
 z=floors[i];top=floors[i+1]
 window_ring=box(-30,30,-30,30,z+2.12,top)-shell(z+2.10,top+.02,1.05)
 main-=window_ring
 if i in terrace_specs:
  cy,w0,w1,depth=terrace_specs[i]
  cx=-20 if cy<15 else -16.4
  # Smooth continuous outer mouth envelope in elevation, with independently
  # recessed floor bands in plan. This is not a spherical bowl surface.
  def mouth_width(zz):
   if i<6:
    start=13.05 if i<3 else 24.0
    u=(zz-(start+5.475))/5.9
    return 5.7*math.sqrt(max(.025,1-u*u))
   u=(zz-42.5)/8.4
   return 7.1*math.sqrt(max(.16,1-u*u))
  zzs=np.linspace(z+.38,top+.02,33)
  cut=loft([(zz,depth,mouth_width(zz),cx,cy) for zz in zzs],2.0)
  main-=cut
  # Deep backing follows the same continuous envelope. Floor-specific depth
  # keeps each terrace legible rather than joining all levels into one bowl.
  main-=loft([(zz,depth+1.45,mouth_width(zz)+.4,cx,cy) for zz in np.linspace(z+2.10,top+.02,15)],2.0)
 # The original solid below each opening forms the landing and back root.
parts.append(main)
# Continuous top storey parapet joins roof gap supporting central mechanical core.
rx,ry=dims(49.55) # top parapet now integral to the continuous main body
parts.append(box(-4.7,4.7,-7.0,6.5,49.5,53.0))
# Actual roof ventilation slot, substantial columns with true feet on roof slab.
# Visible-photo support layout is intentionally sparse and non-periodic.
# Hidden positions are bounded structural simplifications, not a surveyed ring.
for x,y in [(-10,-10),(-10,4),(-7,13),(9,-11),(10,2),(6,13)]:
 parts.append(oval(.48,.48,49.7,2.5,x,y,2.0))
# Covered fusiform roof: shallow dome with underside cut, minimum edge thickness
# 0.65m. Central glazing represented by grooves on closed material, no empty eye.
cap=loft([(51.6,14.0,18.2,0,0),(52.2,12.9,16.6,0,0),(53.0,11.0,14.2,0,0),(53.8,8.7,11.2,0,0),(54.7,5.1,6.6,0,0),(55.2,.8,1.0,0,0)],3.15)
# retain solid core under opaque/glass surface, no sealed hollow interior.
# Upper steel/glass grid follows roof: shallow relief grooves across central zone.
# Fine roof grid omitted from printable geometry after section failure.
# Roof glazing area is tonal preview metadata only; no painted structural bars.
parts.append(cap)
print('building union',len(parts),flush=True)
m=union(parts);mm=m.to_mesh();t=trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts),process=False)
t.export(R/'model.stl');print('mesh',len(t.faces),'watertight',t.is_watertight,'extents',t.extents,flush=True)
(R/'parameters.json').write_text(json.dumps({'school':'中國醫藥大學','campus':'水湳校區','building':'關懷大樓','scale_mm_per_m':S,'base_mm':BASE,'nominal_height_m':55.2,'height_photo_bound_m':[50,58],'nominal_main_NS_EW_m':[43.4,33.4],'footprint_source':'student association scale schematic; orthophoto parallax not resolved to survey','upper_floor_z_m':floors,'west_floor_terraces':terrace_specs,'main_superellipse_exponent':3.15,'roof_base_NS_EW_m':[36.4,28.0],'roof_supports':'six non-periodic supports and rectangular core; hidden layout bounded approximation','fine_roof_grid':'omitted from printable geometry after tiny section islands; no preview bars','roof':'covered dome with ventilation slot, backed solid core; no hidden cavity','status':'unapproved visual candidate; QA not run'},ensure_ascii=False,indent=2))
