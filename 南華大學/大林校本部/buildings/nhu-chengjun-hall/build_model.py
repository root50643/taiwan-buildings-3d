#!/usr/bin/env python3
"""Independently authored, source-bounded Chengjun Hall exterior. All units are model mm, not surveyed dimensions.
Requires numpy, trimesh, manifold3d. Use Blender render_model.py for the editable blend and previews.
No source image is embedded or required to rebuild. Source archive is private and immutable.
"""
import argparse, json, pathlib, hashlib
import numpy as np
import trimesh
import manifold3d as mf

PALETTE=[
 {'id':'neutral_unknown','name':'Unverified / pale neutral closure','hex':'#C1BFC1','evidence':'Display-neutral, NOT verified paint on unseen surfaces'},
 {'id':'mauve_front','name':'Observed dusty rose front','hex':'#987E87','evidence':'Official front photographs; uncalibrated'},
 {'id':'wing_pale','name':'Observed pale lavender gray','hex':'#BDBBC0','evidence':'PDF p12 side foreground wing'},
 {'id':'light_frame','name':'Observed light frame / eaves','hex':'#DDDCD5','evidence':'Front rails and side gallery / eaves'},
 {'id':'red_panel','name':'Observed muted red parapet','hex':'#9A615F','evidence':'Official side gallery and upper front parapets'},
 {'id':'roof_purple','name':'Observed muted purple red roof','hex':'#786774','evidence':'PDF p12 pitched foreground wing roof; other roof surfaces inferred continuation'},
 {'id':'recess_dark','name':'Dark recess / approximate glazing','hex':'#454D50','evidence':'Front and foreground end openings; not calibrated transparency'},
 {'id':'step_stone','name':'Approximate pale entrance steps','hex':'#B7ACA0','evidence':'Official front steps; uncalibrated'},
 {'id':'display_base','name':'Display base, not terrain','hex':'#868E8B','evidence':'Authored display aid only'},
]
class Builder:
 def __init__(self):self.items=[];self.ops=[];self.ids={}
 def add(self,name,solid,mat,certainty,source):
  solid=solid.as_original();self.ids[int(solid.original_id())]=mat
  self.items.append(solid);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'certainty':certainty,'source':source,'original_id':int(solid.original_id()),'bounds_model_mm':list(solid.bounding_box())})
 def box(self,n,x,y,z,mat=0,certainty='inferred',source='plan topology / conservative closure'):
  self.add(n,mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]]),mat,certainty,source)
 def build(self):
  # A thin display plinth, never a site terrain or basement reconstruction.
  self.box('Display plinth',(-98,98),(-92,92),(0,3),8,'display-only','independently authored display base')
  # Two 3-band wings; open H courts are not filled with building volume.
  for side in (-1,1):
   x0,x1=sorted([side*53,side*89])
   # Observed outer gallery on local-right wing. The opposite facade remains deliberately plain.
   if side==1:
    self.box('Right wing enclosed body',(53,79),(-80,80),(3,43),2,'observed-family; proportions inferred','PDF p12 side, BF–4F topology')
    for z in (3,16,29,42): self.box(f'Right outer gallery slab {z}',(78,90),(-80,80),(z,z+1.4),3,'observed-family; pitch/count simplified','General Affairs side photos 3/4')
    for j,y in enumerate(np.linspace(-79,79,13)):
     self.box(f'Right gallery pier {j}',(88.2,89.8),(float(y)-.8,float(y)+.8),(3,43.4),3,'observed-family; count simplified','General Affairs side photos 3/4')
    # Subdivide solid parapets into short panels with light frame, omit unprintable lattice holes.
    for floor,z in enumerate((3,16,29)):
     self.box(f'Right gallery lower rail {floor}',(88.3,90),(-80,80),(z+1.2,z+1.9),3,'observed-family; details simplified','side photos')
     self.box(f'Right gallery top rail {floor}',(88.3,90),(-80,80),(z+5.2,z+6.3),3,'observed-family; details simplified','side photos')
     for j in range(12):
      ya=-79+j*158/12+.6; yb=-79+(j+1)*158/12-.6
      self.box(f'Right red panel {floor}-{j}',(88.5,89.6),(ya,yb),(z+1.8,z+5.3),4,'observed-family; solid print simplification','side photos; lattice holes omitted')
    # Gallery back is shadowed wall, not glass; face is recessed 10 mm from rail.
    for z in (10,23,36):
     self.box(f'Right gallery shadowed wall band {z}',(78.9,79.2),(-78,78),(z-2,z+3),0,'unknown-neutral','occluded corridor wall: no detailed windows invented')
   else:
    self.box('Left wing neutral closure',(x0,x1),(-80,80),(3,43),0,'inferred','plans establish volume, complete outer elevation not verified')
    for z in (16,29):self.box(f'Left neutral story band {z}',(x0-.3,x1+.3),(-80,80),(z,z+1.2),0,'inferred','low-detail closure, not mirrored observed facade')
   self.box(f'Wing {side} pale eave',(x0-1.5,x1+1.5),(-81.5,81.5),(42.5,44.1),3 if side==1 else 0,'observed family/inferred extent','PDF p12 gable and eaves')
   # A simple gabled roof family, not an asserted measured roof/junction reconstruction.
   pts=[]
   for y in (-81.5,81.5):
    pts += [[x0-1.5,y,43.9],[x1+1.5,y,43.9],[(x0+x1)/2,y,51.5]]
   roof=mf.Manifold.hull_points(pts)
   self.add(f'Wing {side} simple gabled roof',roof,5,'observed-family; slope and hidden continuation inferred','PDF p12 foreground gable; left roof continuation approximate')
  # Four-storey core, separate from 3-storey wings. No BF footprint extrusion.
  core=mf.Manifold.cube([106,62,56]).translate([-53,-27,3])
  # Recessed front windows: 2 lower upper levels and 4F long slots.
  cuts=[]
  for z in (24,38):
   for x in (-26,26):cuts.append(mf.Manifold.cube([21,4,6]).translate([x-10.5,-28,z]))
  for x in (-26,26):cuts.append(mf.Manifold.cube([31,5,7]).translate([x-15.5,-28,49]))
  # Lower recessed glazing behind porch.
  cuts.append(mf.Manifold.cube([83,4,10]).translate([-41.5,-28,6]))
  core=core-mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
  self.add('Four storey central core',core,0,'plan-supported topology; dimensions inferred','1F–4F plans and PDF front photo')
  # Thin, intersecting color-bearing facade; cut the same openings, no texture projection.
  skin=mf.Manifold.cube([106,.9,56]).translate([-53,-27.2,3])-mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
  self.add('Front dusty rose facade',skin,1,'observed-family; coverage approximate','official front photos')
  for z in (24,38):
   for x in (-26,26):
    self.box(f'Front inset glass {x} {z}',(x-10.5,x+10.5),(-24.3,-23.8),(z,z+6),6,'observed-family; bay width approximate','front photo')
    for zz in (z+.5,z+2.7,z+4.9):
     self.box(f'Front white louver {x} {zz}',(x-11.4,x+11.4),(-29.1,-26.6),(zz,zz+1.0),3,'observed; thickened simplification','front external screens')
    for xx in (x-11,x,x+11):self.box(f'Front screen upright {xx} {z}',(xx-.55,xx+.55),(-29.3,-26.5),(z-.5,z+6.5),3,'observed; thickened simplification','front external screens')
  for x in (-26,26):
   self.box(f'Upper long recess back {x}',(x-15.5,x+15.5),(-23.3,-22.8),(49,56),6,'observed-family; simplified','PDF front photo upper dark openings')
   self.box(f'Upper red front panel {x}',(x-9,x+9),(-27.3,-25.9),(49,51.8),4,'observed-family; solid lattice simplification','PDF front photo')
  self.box('Entrance glazing inset',(-41.5,41.5),(-24.3,-23.8),(6,16),6,'observed-family; simplified','front entrance photos')
  for x in np.linspace(-40,40,9):self.box(f'Entrance mullion {x:.1f}',(float(x)-.55,float(x)+.55),(-25.1,-23.6),(6,16),3,'observed-family; count approximate','front entrance photos')
  # Broad approach stair is a model-specific stair abstraction, not measured riser count.
  for i in range(6):
   self.box(f'Approach step {i+1}',(-45,45),(-47+i*1.7,-24),(3+i*.5,3+(i+1)*.5),7,'observed-family; riser count/depth approximate','front photographs')
  for j,x in enumerate((-39,-13,13,39)):
   col=mf.Manifold.cylinder(12,1.7,1.7,32).translate([x,-36,5.5])
   self.add(f'Entrance round pier {j+1}',col,1,'observed 4 piers; proportions approximate','front photographs')
  self.box('Broad projecting entrance canopy',(-47,47),(-39,-26),(16.8,20.5),1,'observed-family; dimensions approximate','front canopy photographs')
  # Two robust side guard beams omit tiny handrail hardware.
  for x in (-45,45):self.box(f'Entrance simplified side guard {x}',(x-.65,x+.65),(-45,-27),(6,7.2),3,'observed-family; conservative simplified rail','front approach photos')
  # Unverified central roof closed simply, no white framework, no invented lift/machinery.
  self.box('Core conservative neutral roof cap',(-54,54),(-28,36),(58.6,60.0),0,'unverified roof closure','topology only; exact central roof/junction unknown')
  # Matched foreground wing end: 2 large and 1 narrow window per visible level, approximate layout.
  for z in (9,22,35):
   for x,w in ((63,7),(76,7),(55.7,1.4)):
    self.box(f'Foreground end opening {x} {z}',(x-w/2,x+w/2),(-80.35,-79.8),(z,z+4.6),6,'observed-family; placement approximate','PDF p12 foreground wing end')
  final=mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
  return final

def run(out):
 out.mkdir(parents=True,exist_ok=True)
 b=Builder();s=b.build();assert s.status()==mf.Error.NoError,s.status()
 m=s.to_mesh(); v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts)
 mats=np.zeros(len(f),dtype=np.int32)
 for i,oid in enumerate(m.run_original_id):mats[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 mesh=trimesh.Trimesh(v,f,process=False)
 # Gable end infill is pale, not red roofing; sloped roof faces keep source roof family.
 roof=(mats==5); endface=np.abs(mesh.face_normals[:,1])>.99
 mats[roof & endface & (mesh.triangles_center[:,0]>0)]=2
 mats[roof & endface & (mesh.triangles_center[:,0]<0)]=0
 mesh.export(out/'nhu-chengjun-hall.stl')
 np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mats)
 (out/'editable-parts.json').write_text(json.dumps({'units':'model millimetres','palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 # Editable construction objects retain each authored solid, in addition to final manifold mesh.
 parts=[]
 for op,item in zip(b.ops,b.items):
  pm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(pm.vert_properties)[:,:3].tolist(),'faces':np.asarray(pm.tri_verts).tolist(),'material':next(i for i,p in enumerate(PALETTE) if p['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 res={'vertices':len(v),'triangles':len(f),'volume_mm3':float(mesh.volume),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'bounds_model_mm':mesh.bounds.tolist(),'components':len(mesh.split(only_watertight=False)),'material_triangles':{p['id']:int((mats==i).sum()) for i,p in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);run(p.parse_args().out)
