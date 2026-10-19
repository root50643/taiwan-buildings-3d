"""Bounded CCT gatehouse/name-pylon exterior approximation, model millimeters.
Requires existing Python numpy/trimesh/manifold3d plus OpenSCAD and Noto Sans CJK TC.
No source photo pixels are read or embedded. All dimensions are visual estimates.
Four separate fabrication candidates; glue/contact surfaces are not fit-tested.
"""
from pathlib import Path
import collections,hashlib,json,math,os,subprocess,tempfile
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh64,CrossSection,OpType

ROOT=Path(__file__).resolve().parents[1]
PALETTE=[
 ('stone_gray','#B4B8B8','可見灰色石質外觀，無材料規格'),
 ('metal_charcoal','#353D39','門框、格柵、細柱與門片'),
 ('roof_gray','#62655F','薄頂蓋近似灰色'),
 ('glazing_gray_green','#4F6058','玻璃／反射不透明近似'),
 ('blind_warm_brown','#B17E53','可見暖棕窗簾近似'),
 ('brick_red_brown','#A36650','窗下磚紅貼面'),
 ('letter_dark','#243039','校名字體近似深色'),
 ('badge_slate_blue','#536487','不可辨校徽僅保留圓形位置及近似色'),
 ('display_base','#A5A49C','製造展示底板，非實測路面')]
MID={p[0]:i for i,p in enumerate(PALETTE)}
def color(s,c):return s.set_properties(1,lambda pos,props:[float(MID[c])])
def box(x0,x1,y0,y1,z0,z1,c='stone_gray'):
 return color(Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0]),c)
def union(parts):return Manifold.batch_boolean(parts,OpType.Add)
def prism(poly,z0,z1,c):return color(CrossSection([poly]).extrude(z1-z0).translate([0,0,z0]),c)
def bar(a,b,width,z0,z1,c='metal_charcoal'):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);angle=math.degrees(math.atan2(dy,dx))
 return color(Manifold.cube([length,width,z1-z0]).translate([0,-width/2,0]).rotate([0,0,angle]).translate([a[0],a[1],z0]),c)
def arrays(s):
 assert s.status().name=='NoError'
 m=s.to_mesh64();v=np.asarray(m.vert_properties);f=np.asarray(m.tri_verts,dtype=np.int64)
 properties=v[f,3];assert np.max(np.ptp(properties,axis=1))<1e-8
 ids=np.rint(properties[:,0]).astype(int);assert np.all(np.abs(properties[:,0]-ids)<1e-8)
 # Canonical printable values are explicit float32 coordinates, identical to STL.
 xyz=v[:,:3].astype(np.float32).astype(np.float64);lookup={};verts=[];faces=[]
 for face in f:
  out=[]
  for i in face:
   key=tuple(xyz[i])
   if key not in lookup:lookup[key]=len(verts);verts.append(key)
   out.append(lookup[key])
  faces.append(out)
 return np.asarray(verts),np.asarray(faces,dtype=np.int64),ids

def main():
 for d in ['parts','qa','previews']: (ROOT/d).mkdir(exist_ok=True)
 B=2.4
 # Solid exterior mass. Door/glazing are shallow representational insets, no invented room plan.
 booth=box(-66,-21,0,27,B,B+30)
 doorcut=box(-51.1,-39.9,-.5,1.3,B-.01,B+24.8)
 booth=booth-doorcut
 bay=[[-39,-3.2],[-23,-3.2],[-19,.8],[-19,17],[-21,19],[-39,19]]
 objects=[
  prism([[-73,-6],[-71,-8],[81,-8],[83,-6],[83,32],[81,34],[-71,34],[-73,32]],0,B,'display_base'),booth,
  prism(bay,B,B+6.6,'brick_red_brown'),
  prism(bay,B+6.6,B+25,'glazing_gray_green'),
  color(CrossSection([bay]).offset(.5).extrude(5).translate([0,0,B+25]),'stone_gray'),
  color(CrossSection([bay]).offset(.7).extrude(.85).translate([0,0,B+6.5]),'stone_gray'),
  # Plain facade band and opaque door; opening locations are photograph-supported, not interior geometry.
  box(-66.4,-20.5,-.5,27,B+25,B+30),
  box(-50.6,-40.4,.55,1.4,B+.4,B+24.4,'glazing_gray_green'),
  box(-51.1,-50.3,-.15,1.5,B,B+24.8,'metal_charcoal'),
  box(-40.7,-39.9,-.15,1.5,B,B+24.8,'metal_charcoal'),
  box(-51.1,-39.9,-.15,1.5,B+24.0,B+24.8,'metal_charcoal'),
  box(-51.1,-39.9,-.15,1.5,B,B+.65,'metal_charcoal'),
  box(-38.5,-29.1,-3.5,-3.1,B+7.5,B+24.2,'blind_warm_brown'),
  # Visible pylon/main face and offset narrow rear fin, not a surveyed structural section.
  box(69,75.5,0,5.5,B,B+60),
  box(76.1,78.1,1.2,7,B,B+58.8),
  box(54,69.5,0,3.2,B,B+22.4),
  # Low gate-side pier; surrounding long wall is deliberately omitted.
  box(-5.1,-1.1,-.65,5.1,B,B+23.2),
 ]
 # Window-frame boundaries, including the projecting diagonal corner.
 edges=[([-39,-3.2],[-23,-3.2]),([-23,-3.2],[-19,.8]),([-19,.8],[-19,17])]
 for a,b in edges:
  objects += [bar(a,b,.65,B+7.25,B+8.0),bar(a,b,.65,B+24.25,B+25.1)]
 for x,y in [(-39,-3.2),(-29,-3.2),(-23,-3.2),(-19,.8),(-19,9),(-19,17)]:
  objects.append(box(x-.35,x+.35,y-.35,y+.35,B+7.25,B+25.1,'metal_charcoal'))
 # Right canopy-side narrow posts, exaggerated to 1.4 mm for a model, representative rhythm.
 for y in [1.3,7.3,13.3,19.3,25.3]:objects.append(box(-7.2,-5.8,y-.7,y+.7,B-.05,B+40,'metal_charcoal'))
 # Rear wall is an explicitly estimated plain mass; no invented doors, equipment or facade pattern.
 # Exposed primary left canopy supports align with the observed slatted upper band.
 for x in [-64.2,-39.3]:objects.append(box(x-.7,x+.7,.1,1.5,B+29.8,B+40,'metal_charcoal'))
 # School-name relief generated from an installed font. Raw font files are not distributed.
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);out=td/'letters.stl';env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen';env['XDG_CACHE_HOME']=str(td/'cache')
  proc=subprocess.run(['openscad','-o',str(out),str(ROOT/'source/lettering.scad')],env=env,capture_output=True,text=True,check=True)
  tm=trimesh.load(out,force='mesh',process=True);letters=Manifold(Mesh64(np.asarray(tm.vertices),np.asarray(tm.faces,dtype=np.uint64)));assert letters.status().name=='NoError'
  objects.append(color(letters,'letter_dark'))
 # Simplified badge location only: no invented emblem details.
 disk=Manifold.cylinder(.36,2.0,circular_segments=40).rotate([90,0,0]).translate([72.25,.10,58.8]);objects.append(color(disk,'badge_slate_blue'))
 body=union(objects)
 roof=union([box(-70,-2,-5,32,B+40,B+40.85,'metal_charcoal'),box(-70,-2,-5,32,B+40.85,B+41.6,'roof_gray')])
 # One fixed, closed-position gate depiction, not a working gate mechanism.
 gateparts=[box(-1.1,54,-.65,.65,B+.6,B+2.0,'metal_charcoal'),box(-1.1,54,-.65,.65,B+22.0,B+23.4,'metal_charcoal')]
 for x in [-1.1,26.2,52.6]:gateparts.append(box(x,x+1.4,-.65,.65,B+.6,B+23.4,'metal_charcoal'))
 # Align bar rear faces with the frame so all flat-laid native undersides are on z=0.
 for x in np.arange(1.8,52.0,2.15):gateparts.append(box(float(x),float(x)+.95,-.35,.65,B+1.8,B+22.2,'metal_charcoal'))
 gate=union(gateparts)
 # Separate flat-laid louver insert; six representative rails, explicitly not an exact count survey.
 louvers=[box(-63.5,-62.3,-.1,1.1,B+30,B+40,'metal_charcoal'),box(-41.2,-40,-.1,1.1,B+30,B+40,'metal_charcoal')]
 for z in [33.0,34.6,36.2,37.8,39.4,41.0]:louvers.append(box(-63.5,-40,-.1,1.1,z,z+.8,'metal_charcoal'))
 louver=union(louvers)
 definitions=[
  ('01-base-gatehouse-pylon',body,np.array([[1,0,0,-73],[0,1,0,-8],[0,0,1,0],[0,0,0,1.]]),'upright; base on bed'),
  ('02-thin-canopy',roof,np.array([[1,0,0,-70],[0,1,0,-5],[0,0,1,B+40],[0,0,0,1.]]),'flat underside on bed; align to visible posts and slatted band'),
  ('03-fixed-gate-panel',gate,np.array([[1,0,0,-1.1],[0,0,-1,.65],[0,1,0,B+.6],[0,0,0,1.]]),'flat panel on bed; fixed closed appearance only'),
  ('04-upper-louver-panel',louver,np.array([[1,0,0,-63.5],[0,0,-1,1.1],[0,1,0,B+30],[0,0,0,1.]]),'flat panel on bed; glue into upper band')]
 result=[];allpoints=[]
 for name,world,T,note in definitions:
  assert world.status().name=='NoError'
  # Remove construction-scale near-collinear slivers before float32 export; source images are approximate.
  world=world.simplify(0.0001)
  v,f,colors=arrays(world)
  native=(v-T[:3,3])@T[:3,:3];native=native.astype(np.float32).astype(np.float64)
  origin_adjustment=native.min(axis=0);native=(native-origin_adjustment).astype(np.float32).astype(np.float64);T=T.copy();T[:3,3]+=T[:3,:3]@origin_adjustment
  assert np.array_equal(native.min(axis=0),[0,0,0])
  # Match exported STL values. Rotation/translation itself is retained separately for assembly.
  tm=trimesh.Trimesh(native,f,process=False);cross=np.cross(native[f[:,1]]-native[f[:,0]],native[f[:,2]]-native[f[:,0]])
  zero=int(np.count_nonzero(np.linalg.norm(cross,axis=1)==0))
  if zero:print('DEGENERATE',name,[(int(i),PALETTE[colors[i]][0],native[f[i]].tolist()) for i in np.where(np.linalg.norm(cross,axis=1)==0)[0]],flush=True)
  assert zero==0,(name,'zero triangle',zero)
  assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0,(name,'mesh invalid')
  valid=Manifold(Mesh64(native,np.asarray(f,dtype=np.uint64)));assert valid.status().name=='NoError'
  stl=ROOT/'parts'/(name+'.stl');tm.export(stl)
  record={'id':name,'stl':str(stl.relative_to(ROOT)),'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest(),'vertices':native.tolist(),'triangles':f.tolist(),'material_indices':colors.tolist(),'assembly_transform':T.tolist(),'native_bounds_mm':tm.bounds.tolist(),'assembly_note':note,'float32_native_origin_adjustment_mm':origin_adjustment.tolist(),'geometry_check':{'triangles':len(f),'vertices':len(native),'watertight':True,'winding_consistent':True,'positive_volume_mm3':float(tm.volume),'connected_components':len(valid.decompose()),'zero_area_triangles':zero,'pre_export_simplification_tolerance_mm':0.0001},'material_triangle_counts':dict(collections.Counter(PALETTE[i][0] for i in colors))}
  result.append(record);allpoints.append(native@T[:3,:3].T+T[:3,3])
 pts=np.concatenate(allpoints)
 report={'units':'millimeter','real_world_scale':'not measured; all model dimensions are proportional estimates','materials':[{'id':n,'srgb':c,'interpretation':d} for n,c,d in PALETTE],'parts':result,'assembled_bounds_mm':[pts.min(axis=0).tolist(),pts.max(axis=0).tolist()],'assembled_dimensions_mm':np.ptp(pts,axis=0).tolist(),'source_scope':'Two complete official street-side views; rear simple closure and roof upper surface estimated. Third known photo not fully retrieved.','manufacturing':'Four separate candidates; no calibrated tolerances, support-free or physical-print claim. All details below real facade scale are model approximations.'}
 (ROOT/'geometry.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n')
 summary={k:v for k,v in report.items() if k!='parts'};summary['parts']=[{k:v for k,v in p.items() if k not in ['vertices','triangles','material_indices']} for p in result]
 (ROOT/'qa/build-geometry.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'dimensions_mm':report['assembled_dimensions_mm'],'parts':[(p['id'],p['geometry_check']) for p in result]},ensure_ascii=False))
if __name__=='__main__':main()
