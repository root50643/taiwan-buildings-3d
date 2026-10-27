#!/usr/bin/env python3
"""Original NUK humanities C geometry. Inputs are editable source-derived parameters, not A/B meshes.
Use Python with numpy, trimesh and manifold3d. All authoring dimensions below are design metres.
Final dimensions are miniature millimetres. No network and no third-party images are embedded.
"""
import pathlib,json,argparse,math,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh,manifold3d as mf
ROOT=pathlib.Path(__file__).resolve().parent
PALETTE=[
 {'id':'ochre','name':'Warm ochre wall and fascia','hex':'#C5A66A','evidence':'C-labelled official 2011 exterior photographs; approximate uncalibrated warm finish'},
 {'id':'grass','name':'Planted roof and end slopes','hex':'#70844C','evidence':'C roof section planted roof with 30 cm soil; C-labelled side photographs show grass'},
 {'id':'glazing','name':'Opaque blue grey glazing','hex':'#354B53','evidence':'C elevations and 2011 photo window bands; opaque print proxy, no interior'},
 {'id':'metal','name':'Silver grey rails and frames','hex':'#A1A9AA','evidence':'C 2011 photo horizontal metallic rails, fine members intentionally thickened'},
 {'id':'steps','name':'Grey aggregate outdoor seating','hex':'#999C91','evidence':'C section explicitly indicates exposed aggregate on front terraces; simplified finish'},
 {'id':'paving','name':'Walkway and canopy soffit','hex':'#BCB7A7','evidence':'Drawing-derived path/canopy form; neutral tonal approximation'},
 {'id':'base','name':'Display-only neutral support','hex':'#CECFCA','evidence':'Authored model support, not reconstructed terrain'}]
def box(x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
def solid(poly,z0,z1):return mf.CrossSection([np.asarray(poly,float)],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def slab(poly,low,high):
 s=solid(poly,0,1)
 return s.warp(lambda v:(v[0],v[1],low(v[0],v[1])+(high(v[0],v[1])-low(v[0],v[1]))*v[2]))
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.g=p['base_thickness_mm']/p['model_mm_per_design_m']
 def add(self,name,s,mat,evidence):
  assert s.status()==mf.Error.NoError and not s.is_empty(),name
  s=s.translate([0,0,self.g]).warp(lambda v:tuple(round(float(q)*32)/32 for q in v)).as_original();self.ids[int(s.original_id())]=mat;self.items.append(s);self.ops.append({'name':name,'material':mat,'evidence':evidence})
 def bx(self,n,x,y,z,m=0,e='C-specific plan/elevations; miniature dimensions simplified'):self.add(n,box(x,y,z),m,e)
 def rail(self,name,points,zfunc,spacing=3.0):
  # Two horizontal bars are a deliberate downsample of the photographic multi-bar rail.
  w=self.p['min_rail_width_m'];h=1.2
  for k,(aa,bb) in enumerate(zip(points,points[1:])):
   a=np.array(aa,float);b=np.array(bb,float);d=b-a;L=np.linalg.norm(d);n=np.array([-d[1],d[0]])/L*w/2;poly=[a+n,b+n,b-n,a-n]
   for lev in [.52,1.12]:self.add(name+f' bar {k}-{lev}',slab(poly,lambda x,y: zfunc(x,y)+lev-w/2,lambda x,y:zfunc(x,y)+lev+w/2),3,'Actual horizontal metal railing; count and thickness reduced/enlarged for miniature')
   for i,t in enumerate(np.linspace(0,1,max(2,int(L/spacing)+1))):
    x,y=a+d*t;z=zfunc(x,y);self.bx(name+f' post {k}-{i}',(x-w*.65,x+w*.65),(y-w*.65,y+w*.65),(z-.16,z+h),3)
 def build(self):
  p=self.p;L=p['axis_length_m'];left,right=p['end_lengths_m'];D=p['classroom_depth_m'];R=p['roof_structure_z_m'];G=p['roof_grass_z_m'];front=D+p['front_step_depth_m']
  self.bx('Display-only supporting base',(-left-2,L+right+2),(-5,front+2),(-self.g,0),6,'Authored support; not campus/site survey')
  self.bx('Rear continuous exterior paving',(-left,L+right),(-3.5,.2),(-.06,.20),5)
  self.bx('C single-level classroom and service shell',(0,L),(0,D),(-.05,R-.3),0,'105.50 m CA–CM and 12.80 m teaching-room depth; solid exterior proxy, no interior')
  self.bx('Continuous roof structural fascia',(-.3,L+.3),(-.3,D+.2),(R-.45,R),0,'RF +400 cm; C photographic warm edge band')
  self.bx('Planted flat roof',(0.20,L-.20),(.30,D-.25),(R-.02,G),1,'CAD roof +445 and section planted roof 30 cm soil; soil/drainage depth abstracted')
  # Two end slopes are part of C itself. Not the unrelated A/B campus landscape.
  for side,x0,x1,fn in [('left',-left,0,lambda x,y:G*(x+left)/left),('right',L,L+right,lambda x,y:G*(L+right-x)/right)]:
   poly=[(x0,0),(x1,0),(x1,D),(x0,D)]
   self.add(side+' integral end ramp/earth mass',slab(poly,lambda x,y:-.04,lambda x,y: max(.12,fn(x,y))),0,'Official end dimensions and C-specific sloping grass photographs')
   grass=[(x0+.12,1.3),(x1-.12,1.3),(x1-.12,D-.20),(x0+.12,D-.20)]
   self.add(side+' planted inclined roof',slab(grass,lambda x,y:max(.08,fn(x,y)-.18),lambda x,y:max(.20,fn(x,y)+.03)),1,'2011 C side photographs show planted inclined earth/roof plane')
   walk=[(x0,-.05),(x1,-.05),(x1,1.30),(x0,1.30)]
   self.add(side+' roof-access ramp ribbon',slab(walk,lambda x,y:max(.01,fn(x,y)-.16),lambda x,y:max(.18,fn(x,y)+.06)),5,'C side photographs show narrow accessible sloped walkway beside grass')
   self.rail(side+' end ramp outer rail',[(x0,0),(x1,0)],lambda x,y,fn=fn:max(.18,fn(x,y)+.06))
  self.rail('Rear roof edge',[(0,.05),(L,.05)],lambda x,y:G)
  # Narrow facade eave indicated by sections; no invented freestanding support colonnade.
  poly=[(0,-3.0),(L,-3.0),(L,.12),(0,.12)]
  self.add('Narrow continuous rear projecting eave',slab(poly,lambda x,y:3.0+.055*(y+3),lambda x,y:3.28+.055*(y+3)),5,'C sections show a thin rear overhang, not A/B colonnade')
  # Rear classroom elevations are not copied onto the spectator-stand front.
  grids=p['grid_x_m']
  for i,(a,b) in enumerate(zip(grids,grids[1:])):
   if i==4:continue
   self.bx(f'Rear bay {i+1} window',(a+.65,b-2.25),(-.14,.05),(1.10,2.72),2)
   self.bx(f'Rear bay {i+1} transom',(a+.65,b-.60),(-.16,.05),(2.88,3.34),2)
   self.bx(f'Rear bay {i+1} door',(b-2.05,b-.65),(-.18,.04),(.21,2.67),2)
   for x in [a+.6,b-2.15,b-.52]:self.bx(f'Rear bay {i+1} frame {x:.2f}',(x-.16,x+.16),(-.23,.08),(.20,3.45),3)
   x=(a+b-1.6)/2;self.bx(f'Rear bay {i+1} window mullion',(x-.14,x+.14),(-.22,.06),(1.05,2.80),3)
   self.bx(f'Rear bay {i+1} sill',(a+.45,b-2.10),(-.24,.08),(.91,1.13),0)
  for x in [42.6,46.2]:self.bx('Service core high window '+str(x),(x-.7,x+.7),(-.17,.03),(1.4,2.75),2)
  self.bx('Service core rear door',(36.9,39.0),(-.17,.03),(.20,2.55),2)
  # Long front spectator terraces, not an opaque mirrored window facade.
  ztops=[4.0,3.7,3.4,3.1,2.7,2.25,1.8,1.35,.9,.45]
  depths=[.9,.9,.9,.9,1.8,.9,.9,.9,.9,.9]
  yy=D
  for i,(zt,dep) in enumerate(zip(ztops,depths)):
   yn=yy+dep
   xl=-left*max(0,(yn-D)/(front-D));xr=L+right*max(0,(yn-D)/(front-D))
   self.bx(f'Left outdoor spectator tier {i+1}',(xl,36.25),(yy-.02,yn+.02),(-.03,zt),4,'Split front grandstand from roof plan; tier and tread profiles simplified')
   self.bx(f'Right outdoor spectator tier {i+1}',(65.75,xr),(yy-.02,yn+.02),(-.03,zt),4)
   yy=yn
  # Access stair strips subdivision across broad seating tiers; riser relief not line textures.
  for x in [0,18.0,35.5,66.5,81.5,104.0]:
   for i in range(27):
    ya=D+(front-D)*i/27;yb=D+(front-D)*(i+1)/27;zt=4*(1-i/27)+.10
    self.bx(f'Seating access stair {x:g} tread {i+1}',(x-.55,x+.55),(ya-.015,yb+.015),(-.02,zt),5,'Small stair subdivision represented by geometric relief; no as-built tread-count claim')
  self.bx('Central under-stand service enclosure',(36.25,65.75),(D-.1,17.45),(-.03,2.70),0,'C central entry/service mass below C201 platform, exterior-only proxy')
  self.bx('Central C201 raised platform',(36.25,65.75),(D-.15,17.75),(2.50,2.76),4)
  self.bx('Central entrance dark doors',(43.2,46.1),(17.36,17.56),(.20,2.35),2)
  self.bx('Central front room window',(52.0,58.5),(17.36,17.56),(1.05,2.32),2)
  self.bx('Central entry apron',(36.25,65.75),(17.45,front+.1),(-.03,.18),5)
  # Upward-tilted central canopy from the displaced roof-plan view, reattached at C201.
  c0,c1=p['canopy_levels_m'];y0,y1=12.3,18.6
  cf=lambda x,y:c0+(c1-c0)*(y-y0)/(y1-y0)
  poly=[(36.0,y0),(66.0,y0),(66.0,y1),(36.0,y1)]
  self.add('Central outward-rising spectator canopy',slab(poly,lambda x,y:cf(x,y)-.36,cf),0,'C elevations +608.7/+738.4 and A/C sections; displaced plan projection put back over C201')
  for x in [36.5,49.5,65.5]:self.bx('Canopy rear support '+str(x),(x-.25,x+.25),(12.45,12.95),(2.65,c0),0)
  self.rail('C201 front edge left',[(36.4,17.65),(42.8,17.65)],lambda x,y:2.76)
  self.rail('C201 front edge right',[(46.4,17.65),(65.6,17.65)],lambda x,y:2.76)
  # Four natural ventilation roof monitors explicitly present on the roof drawing.
  for x in [44.3,48.0]:
   for y in [2.0,5.1]:
    self.bx(f'Natural vent {x}-{y} curb',(x-.5,x+.5),(y-1.3,y+1.3),(4.25,5.05),0)
    self.bx(f'Natural vent {x}-{y} dark face',(x-.40,x+.40),(y+1.15,y+1.40),(4.60,5.24),2)
    poly=[(x-.65,y-1.46),(x+.65,y-1.46),(x+.65,y+1.46),(x-.65,y+1.46)]
    h=lambda xx,yy,y=y:5.05+.65*(yy-y+1.46)/2.92
    self.add(f'Natural vent {x}-{y} inclined cap',slab(poly,lambda xx,yy:h(xx,yy)-.25,h),5,'C roof four natural ventilation outlets; small details simplified')
  groups=[];self.ids={}
  for mat in range(len(PALETTE)):
   group=mf.Manifold.batch_boolean([item for item,op in zip(self.items,self.ops) if op['material']==mat],mf.OpType.Add).as_original().simplify(.005)
   self.ids[int(group.original_id())]=mat;groups.append(group)
  return mf.Manifold.batch_boolean(groups,mf.OpType.Add)

def export_3mf(path,v,f,mi):
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
 E=lambda tag: '{'+ns+'}'+tag
 root=ET.Element(E('model'),unit='millimeter',attrib={'{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
 for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
 obj=ET.SubElement(res,E('object'),id='2',type='model',name='NUK humanities C — independent source-derived exterior');mesh=ET.SubElement(obj,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
 for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(x):.7f}' for k,x in zip('xyz',row)})
 for row,m in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(m),p2=str(m),p3=str(m))
 build=ET.SubElement(root,E('build'));ET.SubElement(build,E('item'),objectid='2')
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))

def main(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().set_tolerance(.005).simplify(.005);assert s.status()==mf.Error.NoError,s.status();m=s.to_mesh();scale=p['model_mm_per_design_m'];v=np.asarray(m.vert_properties)[:,:3]*scale;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),dtype=np.int32)
 for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'model.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi);export_3mf(out/'model.3mf',v,f,mi)
 parts=[]
 for op,item in zip(b.ops,b.items):
  a=item.to_mesh();parts.append({**op,'vertices':(np.asarray(a.vert_properties)[:,:3]*scale).tolist(),'faces':np.asarray(a.tri_verts).tolist()})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')))
 (out/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2))
 r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'volume_mm3':float(t.volume),'bounds_mm':t.bounds.tolist(),'dimensions_mm':t.extents.tolist(),'components':len(s.decompose()),'authored_components':len(parts),'material_triangle_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_scope':'C only; no A/B geometry inputs'}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=pathlib.Path,default=ROOT);a.add_argument('--params',type=pathlib.Path,default=ROOT/'parameters.json');n=a.parse_args();main(n.out,n.params)
