#!/usr/bin/env python3
"""Original approximate 2008–2009 Puli Paper Dome hall. Numeric public inputs only."""
import argparse,pathlib,json,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Point,Polygon,LineString,box as rect
PALETTE=[
 {'id':'membrane','name':'Neutral off-white membrane','hex':'#F0F0E9','evidence':'A01/A02 exterior and A05 interior; neutral daylight, not night amber'},
 {'id':'metal_frame','name':'Pale silver-white panel framing','hex':'#BCC4C8','evidence':'A01/A02/A04 and C01; approximate daylight metal'},
 {'id':'translucent_sheet','name':'Pale grey translucent-sheet colour proxy','hex':'#C7CFD0','evidence':'A02 and C01 translucent sheets; solid-color geometry, no image texture'},
 {'id':'paper_tubes','name':'Warm tan paper tubes','hex':'#C6A777','evidence':'A02/A05 paper columns; uncalibrated approximate tan'},
 {'id':'wood_underside','name':'Warm brown wood roof underside and ring','hex':'#89633D','evidence':'A02/A05 exposed timber roof perimeter'},
 {'id':'deck_timber','name':'Dark weathered timber deck','hex':'#544D43','evidence':'A01/A02/C01 Taiwan replacement deck, not Kobe floor'},
 {'id':'floor_finish','name':'Neutral grey interior floor proxy','hex':'#9E9F95','evidence':'A02 pale interior floor distinct from dark outside deck; replacement finish approximate'},
 {'id':'cable','name':'Subdued metal cable and suspended mast','hex':'#787B78','evidence':'K06 suspended mast / cable system, A05 radial cables; miniature thickening'}]
def union(parts):
 q=[x for x in parts if not x.is_empty()];return mf.Manifold.batch_boolean(q,mf.OpType.Add)if q else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type=='MultiPolygon':return union([solid(x,z0,z1)for x in poly.geoms])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(x.coords)[:-1]for x in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def rod(a,b,d,n=10):
 a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);zz=v/L;xx=np.cross([0,0,1.],zz)
 if np.linalg.norm(xx)<.001:xx=np.array([1.,0,0])
 xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return mf.Manifold.cylinder(L,d/2,d/2,n).transform(np.column_stack([xx,yy,zz,a]))
def cable(a,b,d):
 # Closed low-poly tube along a tiny catenary-like sag approximation. Short bands
 # avoid the ill-conditioned metre-long sliver triangles of a single skinny rod.
 a=np.asarray(a,float);b=np.asarray(b,float);zz=(b-a)/np.linalg.norm(b-a);xx=np.cross([0,0,1.],zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx);N=8;steps=16;v=[];f=[]
 for u in np.linspace(0,1,steps+1):
  c=a*(1-u)+b*u;c[2]-=.85*np.sin(np.pi*u)
  for t in np.linspace(0,2*np.pi,N,endpoint=False):v.append(c+d/2*(np.cos(t)*xx+np.sin(t)*yy))
 for k in range(steps):
  for i in range(N):
   j=(i+1)%N;aa=k*N+i;bb=k*N+j;cc=(k+1)*N+j;dd=(k+1)*N+i;f.extend([[aa,bb,cc],[aa,cc,dd]])
 for i in range(1,N-1):f.extend([[0,i+1,i],[steps*N,steps*N+i,steps*N+i+1]])
 return mf.Manifold(mf.Mesh(np.asarray(v,np.float32),np.asarray(f,np.uint32)))

def ellipse(a,b,n=128):return Polygon([(a*math.cos(t),b*math.sin(t))for t in np.linspace(0,2*math.pi,n,endpoint=False)])
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.column_centres=[]
 def add(self,name,m,mat,evidence):
  assert not m.is_empty() and m.status()==mf.Error.NoError,(name,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(m.bounding_box())})
 def roof(self):
  p=self.p;N=p['roof_angular_segments'];a,b=p['ellipse_semi_axes_mm'];wx=p['hall_width_mm']/2+1;wy=p['hall_depth_mm']/2+1
  # Closed shell: one raised ellipse-covered tent transitioning to rectangular eaves.
  ts=np.linspace(0,2*np.pi,N,endpoint=False);ct=np.cos(ts);st=np.sin(ts)
  radii=np.linspace(.015,1,p['roof_radial_segments']);rings=[]
  for r in radii:
   h=p['roof_ring_z_mm']+(p['roof_apex_z_mm']-p['roof_ring_z_mm'])*(1-r)**2
   rings.append(np.c_[a*r*ct,b*r*st,np.full(N,h)])
  outside=np.minimum(wx/np.maximum(abs(a*ct),1e-12),wy/np.maximum(abs(b*st),1e-12))
  for u in [.33,.67,1.0]:
   rr=1+(outside-1)*u;h=p['roof_ring_z_mm']+(p['roof_edge_z_mm']-p['roof_ring_z_mm'])*u;rings.append(np.c_[a*rr*ct,b*rr*st,np.full(N,h)])
  top=np.concatenate(rings);bottom=top.copy();bottom[:,2]-=p['membrane_thickness_mm'];v=np.concatenate([top,bottom,[[0,0,p['roof_apex_z_mm']],[0,0,p['roof_apex_z_mm']-p['membrane_thickness_mm']]]]);M=len(top);f=[]
  for k in range(len(rings)-1):
   for i in range(N):
    j=(i+1)%N;aa=k*N+i;bb=k*N+j;cc=(k+1)*N+j;dd=(k+1)*N+i;f.extend([[aa,dd,cc],[aa,cc,bb],[M+aa,M+cc,M+dd],[M+aa,M+bb,M+cc]])
  for i in range(N):
   j=(i+1)%N;f.extend([[2*M,i,j],[2*M+1,M+j,M+i]])
   aa=(len(rings)-1)*N+i;bb=(len(rings)-1)*N+j;f.extend([[aa,M+aa,M+bb],[aa,M+bb,bb]])
  return mf.Manifold(mf.Mesh(np.asarray(v,np.float32),np.asarray(f,np.uint32)))
 def panel(self,name,cx,cy,w,rotation,ev):
  p=self.p;z0=p['floor_datum_mm']-.1;z1=p['wall_top_mm'];fw=p['frame_width_mm'];th=p['sheet_thickness_mm']
  def trans(m):return m.rotate([0,0,rotation]).translate([cx,cy,0])
  self.add(name+' sheet',trans(box((-w/2+.22,w/2-.22),(-th/2,th/2),(z0,z1-.15))),2,ev)
  frames=[box((-w/2,-w/2+fw),(-.65,.65),(z0,z1)),box((w/2-fw,w/2),(-.65,.65),(z0,z1))]
  for z in [z0+.3,z0+(z1-z0)*.38,z1-.5]:frames.append(box((-w/2,w/2),(-.65,.65),(z-.42,z+.42)))
  self.add(name+' frame',trans(union(frames)),1,ev)
 def fixed_wall(self,name,axis,fixed,lo,hi,n,ev):
  p=self.p;z0=p['floor_datum_mm']-.1;z1=p['wall_top_mm'];th=p['sheet_thickness_mm']
  def trans(m):return m.translate([0,fixed,0])if axis=='x'else m.rotate([0,0,90]).translate([fixed,0,0])
  self.add(name+' continuous sheet',trans(box((lo,hi),(-th/2,th/2),(z0,z1))),2,ev)
  frames=[]
  for u in np.linspace(lo,hi,n+1):frames.append(box((u-.42,u+.42),(-.7,.7),(z0,z1+.3)))
  for z in [z0+.4,z0+(z1-z0)*.38,z1-.4]:frames.append(box((lo-.4,hi+.4),(-.7,.7),(z-.5,z+.5)))
  self.add(name+' fixed framing',trans(union(frames)),1,ev)
  # Two diagonal braces, source-bounded rhythm only; no hidden hinge replication.
  for j,(u,v)in enumerate([(lo,lo+(hi-lo)/2),(lo+(hi-lo)/2,hi)]):
   aa=(u,0,z0+1);bb=(v,0,z1-1)
   if j%2:aa=(u,0,z1-1);bb=(v,0,z0+1)
   self.add(name+' diagonal brace %d'%j,trans(rod(aa,bb,.55,6)),1,ev)
 def build(self):
  p=self.p;wx=p['hall_width_mm']/2;wy=p['hall_depth_mm']/2;floor=p['floor_datum_mm'];a,b=p['ellipse_semi_axes_mm'];ev='A01/A02/C01 Taiwan deck; normalized outline, site ramps/pond/landscape outside hall scope'
  self.add('Taiwan dark timber deck',solid(rect(*p['deck_bounds_mm']),0,3.1),5,ev)
  # Thin plank grooves are authored relief, not photo texture or exact board count.
  for i,y in enumerate(np.arange(-99,88,4.5)):
   for side,(x0,x1)in enumerate([(-118,-110.3),(110.3,118)]):self.add('Deck board strip %02d %d'%(i,side),box((x0,x1),(y,min(y+4.12,89)),(3.0,3.22)),5,ev)
  for i,y in enumerate([-99,-94.5,-90]):self.add('Front deck board strip %02d'%i,box((-118,118),(y,min(y+4.12,89)),(3,3.22)),5,ev)
  self.add('Taiwan interior floor proxy',box((-110.2,110.2),(-89.3,80.3),(3.0,floor)),6,'A02 Taiwan floor; finish and thin step approximate, not reused Kobe floor')
  # Equal rear arc pitch and wider front arc pitch, two deliberately unequal densities.
  dense_t=np.linspace(0,np.pi,4001);xy=np.c_[a*np.cos(dense_t),b*np.sin(dense_t)];length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
  rear=np.interp(np.linspace(0,length[-1],p['rear_half_columns_including_endpoints']),length,dense_t)
  front=np.pi+np.interp(np.linspace(0,length[-1],p['front_half_columns_excluding_endpoints']+2)[1:-1],length,dense_t)
  for i,t in enumerate(np.r_[rear,front]):
   x=a*np.cos(t);y=b*np.sin(t);self.column_centres.append([float(x),float(y)])
   self.add('Paper column %02d'%(i+1),mf.Manifold.cylinder(82.2-floor,p['column_diameter_mm']/2,p['column_diameter_mm']/2,20).translate([x,y,floor-.15]),3,'Owner 58-column reassembly; K06 nonuniform ellipse + A02/A05 Taiwan; dimensions approximate')
  assert len(self.column_centres)==58
  # Outside ellipse: wood underside. Inside ellipse: covered membrane, never an open-sky hole.
  hole=ellipse(a-2.6,b-2.6);outer=rect(-wx-.2,-wy-.2,wx+.2,wy+.2)
  self.add('Timber perimeter roof underside',solid(outer.difference(hole),80.0,81.55),4,'A02/A05 wood perimeter and ellipse; K06 roof axon; authored thickened timber display layer')
  ring=ellipse(a+2.8,b+2.8).difference(ellipse(a-2.6,b-2.6));self.add('Continuous timber ellipse ring',solid(ring,79.7,83.0),4,'A05 continuous wood inner ring, K06 retained frame; exact joinery not resolved')
  for j,y in enumerate(np.arange(-76,80,12.8)):
   q=rect(-wx+.3,y-.45,wx-.3,y+.45).difference(ellipse(a+1.3,b+1.3));self.add('Exposed perimeter joist %02d'%j,solid(q,79.0,80.5),4,'A02/A05 visible brown perimeter underside; reduced beam rhythm')
  self.add('Single raised rectangular membrane roof',self.roof(),0,'A01 one raised roof + A05 covered inner ellipse; K06 section/roof axon historical comparator. Curvature approximate')
  # Pale metal perimeter edge, no extra roof or annex.
  rim=rect(-wx-1.1,-wy-1.1,wx+1.1,wy+1.1).difference(rect(-wx+.1,-wy+.1,wx-.1,wy-.1));self.add('Rectangular pale roof edge',solid(rim,81.5,83.0),1,'A01/A02/C01 rectangular light roof edge')
  self.fixed_wall('Rear long wall','x',wy,-wx,wx,22,'C01 whole rear + K06 retained frame; continuous fixed translucent panel wall')
  for sign,label in [(-1,'Pond short side'),(1,'Nonpond short side')]:
   ev='A04/C01 same pond short face + K06 fixed rear / open forward partition'if sign<0 else'K06 complete retained-frame plan + A01 edge / A02 through-interior corroboration; no standalone fourth exterior photo; hidden details approximate'
   self.fixed_wall(label+' rear half','y',sign*wx,0,wy,8,ev)
   n=p['short_front_pivot_panel_count'];w=wy/n
   for i in range(n):self.panel(label+' pivot %02d'%(i+1),sign*wx,-wy+(i+.5)*w,w,0,ev)
  n=p['front_pivot_panel_count'];w=2*wx/n
  for i in range(n):self.panel('Front pivot %02d'%(i+1),-wx+(i+.5)*w,-wy,w,90,'A01/A02 documented fully open front; authored panel count/hinge simplification, not surveyed operation angle')
  # Suspended central mast and radial cables DO NOT create a floor-to-roof central column.
  self.add('Suspended central roof mast',rod([0,0,p['suspended_mast_bottom_mm']],[0,0,p['roof_apex_z_mm']-.3],1.25,12),7,'K06 section shows mast suspended above floor; A05 central roof system; exact hardware approximate')
  self.add('Simplified suspended cable hub',mf.Manifold.sphere(1.5,16).translate([0,0,p['suspended_mast_bottom_mm']+.3]),7,'Simplified small cable-to-mast hub; exact hidden connector not reconstructed')
  for i,t in enumerate(np.linspace(0,2*np.pi,16,endpoint=False)):
   self.add('Suspension radial cable %02d'%i,cable([0,0,p['suspended_mast_bottom_mm']+.3],[a*np.cos(t),b*np.sin(t),82.0],p['cable_diameter_mm']),7,'K06 radial structural system; A05 fine cables, thickened miniature proxy with 0.85 mm schematic sag; count and curvature approximate')
  return union(self.items)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build();assert s.status()==mf.Error.NoError,s.status()
 s=s.set_tolerance(.003).simplify(.003);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,5),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.004).simplify(.004)
 parts=canonical.decompose();filled=len([q for q in parts if q.volume()<=0]);canonical=union([q for q in parts if q.volume()>0]);cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/(p['model_id']+'.stl'));np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops,'paper_column_centres_mm':b.column_centres},ensure_ascii=False,indent=2)+'\n')
 partdata=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();partdata.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(partdata,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(partdata),'paper_columns':len(b.column_centres),'closed_hidden_roof_layer_voids_filled':filled,'float_canonical_tolerance_mm':.004,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
