#!/usr/bin/env python3
"""NQU roundhouse CENTRAL ENTRANCE FACADE only. Authored photographic approximation.
No source pixels or measured architectural data are required by this reproducible builder.
Coordinates are millimetres of a printable display model, NOT survey dimensions.
"""
import argparse, json, pathlib
import numpy as np
import trimesh
import manifold3d as mf
SLUG='nqu-roundhouse-entrance-facade'
PALETTE=[
 {'id':'artificial_cut','name':'Neutral artificial cut and backing','hex':'#B0B3B3','evidence':'Display convention, not actual rear wall'},
 {'id':'brick_red','name':'Muted orange red masonry','hex':'#A35F44','evidence':'S1/S2/S3 front photographs; uncalibrated'},
 {'id':'brick_warm','name':'Authored warm brick variation','hex':'#B57755','evidence':'Authored variation of observed masonry family, not photo texture'},
 {'id':'lower_gray','name':'Gray stone-like lower band','hex':'#9E9F96','evidence':'S1/S2/S3 entrance surround'},
 {'id':'pale_trim','name':'Warm pale columns railing and frames','hex':'#D8D3BB','evidence':'S1/S2/S3 front photographs; uncalibrated'},
 {'id':'dark_recess','name':'Dark recess and opaque glazing proxy','hex':'#424B49','evidence':'Shadow/reflection proxy, not measured glass'},
 {'id':'eave_gray','name':'Medium gray front tile strip','hex':'#777B78','evidence':'Directly visible front eave in S1/S2/S3; full roof omitted'},
 {'id':'display_base','name':'Display plinth','hex':'#707A77','evidence':'Authored support; not terrain or foundation'},
]
W=68.; R=160.; BACK=27.
def front(x):return R-np.sqrt(R*R-x*x)
def box(x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
def band(x0,x1,y0,y1,z0,z1,n=96):
 # Curved front + optional parallel curved rear; deliberate radius, never measured.
 xs=np.linspace(x0,x1,n+1)
 pts=[[float(x),float(front(x)+y0)] for x in xs]
 pts+=[[float(x),float(front(x)+y1)] for x in xs[::-1]]
 return mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0])
def facade_body(z0,z1):
 xs=np.linspace(-W,W,97)
 pts=[[float(x),float(front(x))]for x in xs]+[[W,BACK],[-W,BACK]]
 return mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0])
def xz_poly(points,y0,y1):
 # Original polygon XY interpreted as XZ, extrusion oriented toward -Y.
 return mf.CrossSection([points]).extrude(y1-y0).rotate([90,0,0]).translate([0,y1,0])
def arch(w=35,bottom=43,edge=60,crown=69):
 return [[-w,bottom],[w,bottom]]+[[float(x),float(edge+(crown-edge)*(1-(x/w)**2))]for x in np.linspace(w,-w,65)]
class Builder:
 def __init__(self):self.items=[];self.ops=[];self.ids={}
 def add(self,name,solid,mat,certainty='photographic approximation',source='S1/S2/S3 front photographs'):
  assert solid.status()==mf.Error.NoError,(name,solid.status())
  solid=solid.as_original();self.ids[int(solid.original_id())]=mat;self.items.append(solid)
  self.ops.append({'name':name,'material':PALETTE[mat]['id'],'certainty':certainty,'source':source,'original_id':int(solid.original_id()),'bounds_model_mm':list(solid.bounding_box())})
 def build(self):
  self.add('Display plinth — not actual pavement',box((-73,73),(-9,32),(0,3)),7,'display-only','Authored support convention')
  entrance=box((-34,34),(-3,10),(3,36))
  archcut=xz_poly(arch(),-4,10)
  upper=[]
  for x,w in ((0,22),(-21,4),(-31,4),(21,4),(31,4)):
   upper.append(box((x-w/2,x+w/2),(-4,11),(88,107)))
  cutters=mf.Manifold.batch_boolean([entrance,archcut]+upper,mf.OpType.Add)
  body=facade_body(3,114)-cutters
  self.add('Central segment structural closure',body,0,'unmeasured photographic proportions; artificial depth and cuts','S1/S2/S3 front; no hidden building geometry asserted')
  self.add('Gray lower entrance band',band(-W,W,-.35,1.3,3,43)-cutters,3)
  self.add('Curved red masonry field',band(-W,W,-.35,1.3,43,114)-cutters,1)
  # Authored brick relief: individually bounded, intersecting and shallow. No source pixels.
  for row,z in enumerate(np.arange(44.0,113.,2.15)):
   for col,x in enumerate(np.arange(-70+(row%2)*3.1,68,6.2)):
    x0=max(-W,float(x));x1=min(W,float(x+5.6))
    if x1<=x0:continue
    solid=band(x0,x1,-.52,.3,float(z),min(114,float(z+1.35)),n=4)-cutters
    if solid.volume()>.001 and (row*13+col*7)%5 in (0,1):self.add(f'Authored brick variation {row:02d}-{col:02d}',solid,2,'invented bond and relief, observed color family','Authored brick motif, not as-built brick positions')
  # Recess backing planes connect to the main body; actual negative depth remains readable.
  self.add('Recessed entrance dark closure',box((-34,34),(9.8,10.5),(3,36)),5)
  self.add('Recessed broad arch glazing proxy',xz_poly(arch(),9.8,10.5),5)
  # Frames follow the actual arched outline at the front skin, not a colored rectangle.
  self.add('Pale shallow arch perimeter', (xz_poly(arch(36.2,41.9,60.6,70.2),-2,8)-archcut)^band(-W,W,-.85,1.2,3,114),4)
  for x in np.linspace(-34,34,9):
   self.add(f'Arch vertical mullion {x:.2f}',box((float(x)-.5,float(x)+.5),(9.0,10.3),(43,70))^xz_poly(arch(),8.7,10.6),4,'thickened 1 mm mullions; count simplified')
  for z in (44,50,56,62):
   self.add(f'Arch horizontal mullion {z}',box((-35,35),(9,10.3),(z,z+1))^xz_poly(arch(),8.7,10.6),4,'thickened 1 mm mullions; count simplified')
  for x in np.linspace(-33,33,7):self.add(f'Entrance vertical frame {x:.1f}',box((float(x)-.55,float(x)+.55),(9,10.3),(3,31)),4,'thickened frames; exact panes simplified')
  for z in (4,24,29,33):self.add(f'Entrance horizontal frame {z}',box((-34,34),(9,10.3),(z,z+1.05)),4,'thickened frames; exact panes simplified')
  for x,w in ((0,22),(-21,4),(-31,4),(21,4),(31,4)):
   opening=box((x-w/2,x+w/2),(-4,11),(88,107))
   self.add(f'Upper opening dark inset {x}',box((x-w/2,x+w/2),(10.8,11.5),(88,107)),5)
   ring=box((x-w/2-1,x+w/2+1),(-3,7),(87,108))-opening
   self.add(f'Upper opening pale surround {x}',ring^band(-W,W,-.9,1.2,3,114),4)
  # Central upper recess includes a small rail, not transparent interior reconstruction.
  for z in (89,93):self.add(f'Central upper inset horizontal rail {z}',box((-11,11),(9.8,11.4),(z,z+1)),4,'simplified visible internal rail')
  for x in (-10,0,10):self.add(f'Central upper inset upright {x}',box((x-.5,x+.5),(9.8,11.4),(88,96)),4,'simplified visible internal rail')
  # Deliberately straight, neutral rear support above balcony: never the actual rear elevation.
  self.add('ARTIFICIAL REAR CUT — upper neutral support',box((-W,W),(24,27),(113,143.5)),0,'display-only hidden-depth closure','No actual rear or full roof is modeled')
  self.add('Visible curved balcony sill',band(-W,W,-1.1,6.0,113.4,115.2),4)
  self.add('Visible curved rail handrail',band(-W,W,-.8,1.3,121,122.4),4)
  for i,x in enumerate(np.linspace(-67,67,65)):
   y=float(front(x))
   self.add(f'Balustrade {i+1:02d}',box((float(x)-.5,float(x)+.5),(y-.35,y+.8),(114.7,121.5)),4,'thickened 1 mm bars; count/spacing simplified')
  # Four directly visible columns: two pairs only, never a continued colonnade.
  for x in (-59,-44,44,59):
   self.add(f'Observed paired column {x:+}',mf.Manifold.cylinder(27,2.7,2.7,48).translate([x,float(front(x)+2.3),114.2]),4,'four columns observed; thickness and spacing approximate')
  # A shallow visible front eave strip only. Rear portion stays explicitly neutral cut.
  self.add('Pale front eave underside strip',band(-W,W,-3.2,9,140.6,143.2),4)
  self.add('Visible front gray tile-strip substrate',band(-W,W,-3.4,8.2,143.0,144.7),6)
  for i,x in enumerate(np.linspace(-67.3,67.3,73)):
   y=float(front(x))
   # Low rounded authored ribs evoke tile rhythm; not individual surveyed tiles.
   rib=mf.Manifold.cylinder(9.8,.6,.6,16).rotate([90,0,0]).translate([float(x),y+7.4,144.55])
   self.add(f'Front eave tile rib {i+1:02d}',rib,6,'authored robust tile rhythm; exact count unknown')
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
def run(out):
 out.mkdir(parents=True,exist_ok=True);b=Builder();s=b.build().simplify(1e-4);assert s.status()==mf.Error.NoError,s.status()
 m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mats=np.zeros(len(f),dtype=np.int32)
 for i,oid in enumerate(m.run_original_id):mats[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 mesh=trimesh.Trimesh(v,f,process=False)
 # Explicit side cuts/back are neutral, independent of surface family.
 cuts=(np.abs(mesh.triangles_center[:,0])>W-.0001)&(np.abs(mesh.face_normals[:,0])>.999)
 mats[cuts]=0
 # Remove sub-0.0001 mm Boolean slivers before float32 STL quantization.
 # Preserve material assignments and then independently check edge AND vertex links.
 mesh.merge_vertices(digits_vertex=4)
 keep=(mesh.faces[:,0]!=mesh.faces[:,1])&(mesh.faces[:,1]!=mesh.faces[:,2])&(mesh.faces[:,2]!=mesh.faces[:,0])
 mesh.update_faces(keep);mats=mats[keep];mesh.remove_unreferenced_vertices()
 v=np.asarray(mesh.vertices,dtype=np.float32);f=np.asarray(mesh.faces,dtype=np.uint32)
 mesh=trimesh.Trimesh(v,f,process=False)
 mesh.export(out/f'{SLUG}.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mats)
 (out/'editable-parts.json').write_text(json.dumps({'units':'model millimetres; NOT surveyed scale','palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  pm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(pm.vert_properties)[:,:3].tolist(),'faces':np.asarray(pm.tri_verts).tolist(),'material':next(i for i,p in enumerate(PALETTE)if p['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 report={'vertices':len(v),'triangles':len(f),'volume_mm3':float(mesh.volume),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'bounds_model_mm':mesh.bounds.tolist(),'components':len(mesh.split(only_watertight=False)),'material_triangles':{p['id']:int((mats==i).sum())for i,p in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);run(p.parse_args().out)
