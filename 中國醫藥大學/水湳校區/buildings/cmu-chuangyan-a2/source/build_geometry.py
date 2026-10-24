#!/usr/bin/env python3
"""Original normalized whole A2 exterior. Source pixels are never build inputs."""
import argparse,json,math
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as mf
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);a=p.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
src=Path(__file__).resolve().parent.parent;P=json.loads((a.parameters or src/'parameters.json').read_text());palette=json.loads((src/'palette.json').read_text())
for n,d in [('parameters.json',P),('palette.json',palette)]: (root/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
B=P['body'];F=P['fins'];E=P['eye'];R=P['roof'];RS=P['raised_screen'];G=P['ground'];W=P['windows'];ZS=P['base']['thickness'];H=B['roof_z']
rules=[]
def rule(name,ev,note,classification='observed organization / approximate proportions'):
 rules.append(dict(index=len(rules),name=name,evidence=ev,note=note,classification=classification));return len(rules)-1
U=rule('Neutral unverified closures',[],'Opaque room filling and hidden surfaces are model simplifications, not observed material.','inferred / simplification')
GR=rule('Separately modeled ground supports and through-passage',['S02-1F','S14'],'Asymmetric west/east room blocks, north projections, offset core and oval foyer mass. No copied rooftop extrusion; no interior stair reconstruction.')
BD=rule('Whole twelve-numbered-level envelope',['S02','S16'],'Complete four-sided body; 12 numbered levels, not occupancy. Dimensions normalized, unsurveyed. Upper court-side projection interpolated within observed bounds.')
SF=rule('South paired waving bands and glazing',['S02','S14-09'],'Offset western eye and lower middle entry wave, rounded short-end returns. Counts and widths simplified for display.')
EY=rule('Open recessed reflective eye with closed back',['S02-062'],'Concave faceted silver recess, not blue painted disk and not a full-building tunnel. Depth and curvature approximate.')
NF=rule('Court side vertical service screens and curved bands',['S14-01','S14-03','S14-06'],'Observed lower screen rhythm; upper unseen rhythm is an explicitly bounded extrapolation. No mirrored south eye.','observed lower / inferred upper repetition')
EN=rule('Unequal short ends',['S02-060','S14-06'],'Horizontal bands turn rounded corners; east broad glazing and west narrower neutral groups differ; obscured openings simplified.')
RF=rule('Roof outline distinct from ground and raised screen',['S11','S09-102'],'Roof/court projection is mildly undulating; high screen is a separate continuous long double-lobed enclosure. Not two detached elliptical towers.')
PV=rule('Three main PV fields plus south long strip',['S11','S09-102'],'2022 visible distribution; panel subdivisions and low mounting height are model simplification, not panel count or HVAC evidence.')
BA=rule('Small own base and landing',['S02-1F','S14'],'Manufacturing base bounded to own envelope; not a full court, street network, A1 or A3.','observed contact / model base')

def mesh(v,f,ma,rr):
 v=np.array(v,dtype=np.float32,order='C',copy=True);f=np.array(f,np.uint32,order='C',copy=True);t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:f=f[:,::-1].copy()
 so=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=np.asarray(ma,np.uint32)+32*np.asarray(rr,np.uint32)));assert so.status()==mf.Error.NoError,so.status();return so

def label(s,ma,rr):
 m=s.to_mesh();return mesh(m.vert_properties[:,:3],m.tri_verts,[ma]*len(m.tri_verts),[rr]*len(m.tri_verts))
def box(x0,x1,y0,y1,z0,z1,ma,rr):
 assert x1>x0 and y1>y0 and z1>z0
 return label(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),ma,rr)
def poly(points,z0,z1,ma,rr):
 pp=np.asarray(points,float);ar=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-np.roll(pp[:,0],-1)*pp[:,1]);pp=pp if ar>0 else pp[::-1];n=len(pp)
 cap=np.array(mf.triangulate([pp],allow_convex=False));v=[[x,y,z]for z in[z0,z1]for x,y in pp];f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def xzpoly(points,y0,y1,ma,rr):
 pp=np.asarray(points);n=len(pp);cap=np.array(mf.triangulate([pp],allow_convex=False));v=[[x,y,z]for y in[y0,y1]for x,z in pp];f=cap[:,::-1].tolist()+(cap+n).tolist()
 for i in range(n):j=(i+1)%n;f += [[i,j,j+n],[i,j+n,i+n]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def rounded_rect(x0,x1,y0,y1,r,n=8):
 out=[]
 for cx,cy,start in[(x1-r,y0+r,-90),(x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180)]:
  out.extend((cx+r*np.cos(t),cy+r*np.sin(t))for t in np.linspace(math.radians(start),math.radians(start+90),n+1)[:-1])
 return np.asarray(out)
def north(x,roof=False,z=None):
 value=B['north_y'];lobes=R['north_lobes']if roof else B['north_lobes'];taper=max(0,1-(abs(x)/(B['half_length']-B['corner_radius']))**12)
 for cx,amp,sd in lobes:value+=amp*math.exp(-((x-cx)/sd)**2)*taper
 if z is not None:value+=B['upper_profile_variation']*math.sin(math.pi*(z-B['first_upper_z'])/(H-B['first_upper_z']))*taper
 return value

def outline(offset=0,roof=False,z=None):
 L=B['half_length'];r=B['corner_radius'];xmax=L-r;ys=B['south_y'];yn=B['north_y'];rad=r+offset;n=F['corner_segments'];pts=[]
 pts.extend((x,ys-offset)for x in np.linspace(-xmax,xmax,F['samples_long']))
 pts.extend((xmax+rad*np.cos(t),ys+r+rad*np.sin(t))for t in np.linspace(-math.pi/2,0,n+1)[1:])
 pts.append((L+offset,yn-r))
 pts.extend((xmax+rad*np.cos(t),yn-r+rad*np.sin(t))for t in np.linspace(0,math.pi/2,n+1)[1:])
 pts.extend((x,north(x,roof,z)+offset)for x in np.linspace(xmax,-xmax,F['samples_long'])[1:])
 pts.extend((-xmax+rad*np.cos(t),yn-r+rad*np.sin(t))for t in np.linspace(math.pi/2,math.pi,n+1)[1:])
 pts.append((-L-offset,ys+r))
 pts.extend((-xmax+rad*np.cos(t),ys+r+rad*np.sin(t))for t in np.linspace(math.pi,3*math.pi/2,n+1)[1:-1])
 return np.asarray(pts)

def loft(sections,ma,rr):
 n=len(sections[0]);v=np.concatenate(sections);cap0=np.asarray(mf.triangulate([np.asarray(sections[0])[:,:2]],allow_convex=False));cap1=np.asarray(mf.triangulate([np.asarray(sections[-1])[:,:2]],allow_convex=False));f=cap0[:,::-1].tolist()+(cap1+(len(sections)-1)*n).tolist()
 for k in range(len(sections)-1):
  for i in range(n):j=(i+1)%n;a=k*n+i;b=k*n+j;c=(k+1)*n+j;d=(k+1)*n+i;f += [[a,b,c],[a,c,d]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def ring(outer,inner,zfunc,thick,ma,rr):
 n=len(outer);v=[]
 for dz,curve in[(0,outer),(0,inner),(thick,outer),(thick,inner)]:v.extend([x,y,zfunc(x,y)+dz]for x,y in curve)
 f=[]
 for i in range(n):
  j=(i+1)%n
  for aa,bb,cc,dd in[(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(i,n+i,n+j,j),(2*n+j,3*n+j,3*n+i,2*n+i)]:f += [[aa,bb,cc],[aa,cc,dd]]
 return mesh(v,f,[ma]*len(f),[rr]*len(f))
def ellipse(cx,cy,rx,ry,n=None):
 return np.array([[cx+rx*math.cos(t),cy+ry*math.sin(t)]for t in np.linspace(0,2*math.pi,n or P['tessellation']['ellipse_segments'],endpoint=False)])
def wave(x,y,z):
 # Front eye deflection dies out toward short ends; rear has only lower entry arch.
 front=max(0,min(1,(-y+10)/30));eye=math.copysign(1,z-E['center_z'])*E['fin_deflection']*math.exp(-((x-E['center_x'])/E['influence_width_x'])**2-((z-E['center_z'])/E['influence_height_z'])**2)*front
 entry=F['entry_lift']*math.exp(-((x-F['entry_center_x'])/F['entry_width'])**2-(z/F['entry_decay_z'])**2)
 rw=F['rear_observed_wave'];rear=max(0,min(1,(y-5)/24))*rw['deflection']*math.exp(-((x-rw['center_x'])/rw['width'])**2-((z-rw['center_z'])/rw['height_decay'])**2)
 return z+eye+entry+rear
solids=[]
def add(*q):solids.extend(q)
# Small integral base, no surrounding campus or neighboring buildings.
b=P['base'];add(poly(rounded_rect(*b['x'],b['south_y'],b['north_y'],b['corner_radius']),-ZS,0,3,BA))
# Separately traced ground rooms, asymmetric service projections and offset cores.
for key in['west_room_rect','east_room_rect','offset_core_rect']:add(box(*G[key],0,G['core_height']+.25,0,GR))
for key in['west_services_polygon','east_services_polygon']:add(poly(G[key],0,G['core_height']+.25,1,GR))
add(poly(ellipse(*G['oval_core_center'],*G['oval_core_radii']),0,G['core_height']+.25,1,GR))
# Upper whole envelope varies gently by height, unlike the aerial projected outline.
sections=[]
for z in np.linspace(B['first_upper_z'],H,7):
 q=outline(z=z);sections.append(np.c_[q,np.full(len(q),z)])
body=loft(sections,2,BD)
# Court side is an opaque service mass behind dark slots, not front glazing.
rearsections=[]
for z in np.linspace(B['first_upper_z'],H,7):
 xs=np.linspace(-116,116,121);q=[(-116,19),(116,19)]+[(x,north(x,z=z)+.15)for x in xs[::-1]];rearsections.append(np.c_[q,np.full(len(q),z)])
add(body,loft(rearsections,4,NF))
# Distinct short-end surface groups, neutral west with fewer window strips.
add(box(-120.25,-119.5,-24,24,14,H-.3,1,EN))
for level in range(B['numbered_levels']):
 z0=level*B['level_pitch'];z1=z0+B['level_pitch']
 # Ground windows only where actual rooms stand; upper glass mass already exists.
 if level==0:
  for x0,x1 in[(-115,-66),(44,115)]:add(box(x0,x1,-28.5,-27.7,2,12.6,2,GR))
 # Flat underlying frame grid; shade bands are separately waved, not painted lines.
 for x in np.arange(-114,115,W['mullion_pitch']):
  if level==0 and not(x<-64 or x>42):continue
  add(box(x-W['mullion_width']/2,x+W['mullion_width']/2,-29-W['mullion_projection'],-28.8,max(1,z0),z1,3,SF))
 if level>0:add(box(-116,116,-29-W['mullion_projection'],-28.8,z0-.25,z0+W['transom_thickness'],3,SF))
 for x,ys,ye,ma in[(120.1,*W['east_inset_y'],2),(-120.55,*W['west_inset_y'],2)]:
  if level==0:continue
  add(box(x-.35,x+.35,ys,ye,z0+2.4,z1-2,ma,EN))
  for y in np.arange(ys,ye,W['mullion_pitch']):add(box(x-.5,x+.5,y,y+W['mullion_width'],z0+2.2,z1-1.8,3,EN))
# Court-side vertical service fins, including rounded projection rhythm.
for x in np.arange(-115,116,P['rear_screen']['pitch']):
 ny=north(x);lo=0 if (x<-29 or x>23)else B['first_upper_z'];add(box(x-P['rear_screen']['bar_width']/2,x+P['rear_screen']['bar_width']/2,ny-.5,ny+P['rear_screen']['projection'],lo,H,1,NF))
# Paired perimeter shade rims with physical brackets to the opaque main mass.
for level in range(1,B['numbered_levels']+1):
 for delta in[0,-F['paired_separation']]:
  zz=level*B['level_pitch']+delta;add(ring(outline(F['outer_offset']),outline(F['outer_offset']-F['rim_width']),lambda x,y:wave(x,y,zz),F['thickness'],1,SF))
  for x in np.arange(-114,115,F['bracket_pitch']):
   zf=wave(x,-33,zz);zr=wave(x,north(x)+3,zz);bw=F['bracket_width']
   add(box(x-bw/2,x+bw/2,-35.2,-28.6,zf-.15,zf+F['thickness']+.15,1,SF),box(x-bw/2,x+bw/2,north(x)-.5,north(x)+6.1,zr-.15,zr+F['thickness']+.15,1,NF))
  for side in[-1,1]:
   for y in np.arange(-21,23,7):
    za=wave(side*120,y,zz);add(box(119.5 if side>0 else -126.1,126.1 if side>0 else -119.5,y-.55,y+.55,za-.15,za+F['thickness']+.15,1,EN))
# Roof slab/parapet is a separate footprint with stronger north undulation.
add(poly(outline(R['outer_offset'],True),H-.3,H+R['slab_thickness'],6,RF))
add(ring(outline(R['outer_offset'],True),outline(R['outer_offset']-R['parapet_width'],True),lambda x,y:H+R['slab_thickness']-.2,R['parapet_height'],1,RF))
# Continuous double-lobed raised screen. One perimeter, not two ellipse towers.
theta=np.linspace(0,2*math.pi,RS['segments'],endpoint=False)
def screen_shape(inset=0):
 pts=[]
 for t in theta:
  x=RS['half_length']*math.cos(t);ax=abs(x);lc=abs(RS['lobe_centers'][0]);half=RS['lobe_half_width']
  if ax>=lc:ww=half*math.sqrt(max(0,1-((ax-lc)/(RS['half_length']-lc))**2))
  else:ww=RS['waist_half_width']+(half-RS['waist_half_width'])*.5*(1-math.cos(math.pi*ax/lc))
  y=RS['center_y']+math.copysign(ww,math.sin(t))
  # Radial normalized inset preserves a common topology for ring lofting.
  pts.append((x*(1-inset/RS['half_length']),RS['center_y']+(y-RS['center_y'])*(1-inset/22)))
 return np.array(pts)
so=screen_shape();si=screen_shape(RS['rim_width']);bottom=H+R['slab_thickness'];top=lambda x,y:bottom+RS['height']+RS['top_variation']*(abs(x)/RS['half_length'])**2
add(ring(so,si,lambda x,y:bottom-.3,RS['rim_height'],1,RF),ring(so,si,top,RS['rim_height'],1,RF))
# Fine screen bars sampled by perimeter distance; spaced and thickened for display.
acc=0.;last=-1e6
for i,q in enumerate(so):
 if i:acc+=np.linalg.norm(q-so[i-1])
 if acc-last<RS['bar_pitch_perimeter']:continue
 last=acc;qi=si[i];xx,yy=(q+qi)/2;ww=RS['bar_width'];add(box(xx-ww/2,xx+ww/2,yy-ww/2,yy+ww/2,bottom-.2,top(xx,yy)+RS['rim_height'],1,RF))
# 2022 photovoltaic distribution; actual panel counts and mount heights unknown.
for rect in P['pv']['central_fields']+[P['pv']['south_strip']]:
 x0,x1,y0,y1=rect;z=H+R['slab_thickness'];add(box(x0,x1,y0,y1,z-.1,z+P['pv']['field_height'],5,PV));d=P['pv']['divider_width']
 for x in np.arange(x0,x1,P['pv']['divider_pitch_x']):add(box(x,min(x+d,x1),y0,y1,z+.9,z+P['pv']['field_height']+.1,1,PV))
 for y in np.arange(y0,y1,P['pv']['divider_pitch_y']):add(box(x0,x1,y,min(y+d,y1),z+.9,z+P['pv']['field_height']+.1,1,PV))
print('Boolean union',len(solids),'solids',flush=True)
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add)
# Real arched ground passage cut above (not through) integral base.
x0,x1=G['passage_x'];cx=(x0+x1)/2;rx=(x1-x0)/2;arc=[(cx+rx*math.cos(t),G['passage_spring_z']+(G['passage_arch_peak_z']-G['passage_spring_z'])*math.sin(t))for t in np.linspace(0,math.pi,49)];arch=[(x0,-.01),(x1,-.01)]+arc
result=result-xzpoly(arch,-50,55,0,GR)
# Closed-back concave cavity. Ellipsoid intersects only south 20 mm of body.
cutter=label(mf.Manifold.sphere(1,E['facets']).scale((E['radius_x'],E['depth_radius_y'],E['radius_z'])).translate((E['center_x'],E['center_y'],E['center_z'])),7,EY)
result=result-cutter
# Elliptic lip around the cavity, with actual thickness and no spanning disk.
outer=ellipse(E['center_x'],E['center_z'],E['radius_x']+E['lip_radial_width'],E['radius_z']+E['lip_radial_width']);inner=ellipse(E['center_x'],E['center_z'],E['radius_x'],E['radius_z']);n=len(outer);v=[]
for y,curve in[(E['lip_front_y'],outer),(E['lip_front_y'],inner),(E['lip_back_y'],outer),(E['lip_back_y'],inner)]:v.extend([x,y,z]for x,z in curve)
f=[]
for i in range(n):
 j=(i+1)%n
 for aa,bb,cc,dd in[(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(i,n+i,n+j,j),(2*n+j,3*n+j,3*n+i,2*n+i)]:f += [[aa,bb,cc],[aa,cc,dd]]
result=result+mesh(v,f,[1]*len(f),[EY]*len(f))
result=result.simplify(P['tessellation']['numerical_cleanup_mm']);assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.array(mm.vert_properties[:,:3],np.float32,copy=True);vertices[:,2]+=np.float32(ZS);vertices*=np.float32(P['display_main_length_mm']/240.0);faces=np.array(mm.tri_verts,np.int32,copy=True);tags=np.asarray(mm.face_id,np.int32);materials=tags%32;rule_indices=tags//32
# Remove numerical zero-area triangles using adjacent edge retriangulation, without
# moving or smoothing any source geometry or changing actual material attribution.
zero=0
for attempt in range(200):
 tri=vertices[faces].astype(float);areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;bad=np.where(areas<1e-10)[0]
 if not len(bad):break
 bi=int(bad[0]);ff=faces[bi];le=[np.linalg.norm(vertices[ff[i]]-vertices[ff[(i+1)%3]])for i in range(3)];j=int(np.argmax(le));u,vv,m=int(ff[j]),int(ff[(j+1)%3]),int(ff[(j+2)%3]);adj=np.where(np.sum(np.isin(faces,[u,vv]),axis=1)==2)[0];adj=[int(q)for q in adj if q!=bi];assert len(adj)==1
 ai=adj[0];af=faces[ai]
 for k in range(3):
  aa,bb,dd=int(af[k]),int(af[(k+1)%3]),int(af[(k+2)%3])
  if{aa,bb}=={u,vv}:break
 nf=np.array([[aa,m,dd],[m,bb,dd]],np.int32);ma=int(materials[ai]);rr=int(rule_indices[ai]);keep=np.ones(len(faces),bool);keep[[bi,ai]]=False;faces=np.concatenate([faces[keep],nf]);materials=np.r_[materials[keep],[ma,ma]];rule_indices=np.r_[rule_indices[keep],[rr,rr]];zero+=1
else:raise RuntimeError('Unresolved numerical degenerate faces')
t=trimesh.Trimesh(vertices,faces,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
parts=t.split(only_watertight=False);assert len(parts)==1,[(len(q.faces),q.bounds.tolist())for q in parts]
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices);t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Original face tags retained through Boolean union/difference; actual per-face colors, no image textures.','rules':rules},ensure_ascii=False,indent=2)+'\n');np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'source_solids':len(solids),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum())for i in range(len(palette))},'zero_area_triangle_edge_pairs_retessellated':zero,'physical_scale_claim':'None; normalized display dimensions, not surveyed','source_scope':'2020 completed exterior with 2022 roof PV distribution; not 2026 survey','numbered_aboveground_levels':12,'occupancy_claim':False,'separate_ground_upper_roof_and_raised_screen':True,'eye_closed_back_recess_not_full_tunnel':True}
(root/'qa/build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
