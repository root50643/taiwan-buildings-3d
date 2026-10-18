"""Draw geometric risk locations from the fixed original STL, not a slicer."""
from pathlib import Path
import json, math, hashlib
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle, Polygon as PatchPolygon
from manifold3d import Manifold, Mesh64
from shapely.geometry import Polygon, box

M=Path(__file__).resolve().parent
P=M.parent
regions=json.loads((M/'regions.json').read_text(encoding='utf-8'))
original=trimesh.load(P/'model.stl',process=True)
variant=trimesh.load(M/'fill-hidden-gaps/model.stl',process=True)
assert hashlib.sha256((P/'model.stl').read_bytes()).hexdigest()==regions['source_stl_sha256']
assert hashlib.sha256((M/'fill-hidden-gaps/model.stl').read_bytes()).hexdigest()=='6801f9c41c9fd986df4167523ec36195e715d6a38a680c09aff002cba1351b2a'
colors=dict(A='#c68400',B='#9b6b18',C='#ab760c',D='#ab760c',E='#a47300',F='#d02030',G='#126ca5')
fig=plt.figure(figsize=(15,11),layout='constrained')
gs=fig.add_gridspec(2,2,height_ratios=[1.2,1])
top=fig.add_subplot(gs[0,0]);front=fig.add_subplot(gs[0,1]);cax=fig.add_subplot(gs[1,0]);fax=fig.add_subplot(gs[1,1])
tri=original.triangles
top.add_collection(PolyCollection(tri[tri[:,:,2].max(axis=1)>3.01][:,:,[0,1]],facecolors='#dfdfdf',edgecolors='none'))
front.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors='#dfdfdf',edgecolors='none'))
for ax in (top,front):
 ax.set_aspect('equal');ax.set_xlim(-77,77);ax.grid(alpha=.15);ax.set_xlabel('model X (mm)')
top.set_ylim(-64,64);top.set_ylabel('model Y (mm)');top.set_title('1  Top: original STL + inspection zones')
front.set_ylim(-2,71);front.set_ylabel('model Z (mm)');front.set_title('2  Front (-Y): original STL + zones')
top.text(-73,-59,'FRONT = -Y',fontsize=9)
top.annotate('',(-66,-48),(-66,-36),arrowprops=dict(arrowstyle='->',color='black'))
offsets=dict(A=(-54,-34),B=(-48,-1),C=(62,-25),D=(-57,-50),E=(-61,53),G=(15,-31))
for row in regions['regions']:
 k=row['id']
 if 'view_bbox' not in row:continue
 lo,hi=np.array(row['view_bbox']);color=colors[k]
 # Whole C inspection includes ground arcade; D includes exterior stair platform.
 if k=='C':lo=np.minimum(lo,[33.5,-22.5,3.2])
 if k=='D':lo=np.minimum(lo,[-50.5,-55.3,14]);hi=np.maximum(hi,[7,-36.774,30.3])
 for ax,i in ((top,1),(front,2)):
  ax.add_patch(Rectangle((lo[0],lo[i]),hi[0]-lo[0],hi[i]-lo[i],fill=False,edgecolor=color,linewidth=1.5,linestyle='--'))
 tx,ty=offsets[k];anchor=row['label_anchor'];top.annotate(k,(anchor[0],anchor[1]),(tx,ty),color=color,fontweight='bold',fontsize=12,arrowprops=dict(arrowstyle='-',color=color))
 xloc={'A':-53,'B':-43,'C':65,'D':-59,'E':-67,'G':13}[k]
 zloc={'A':43,'B':59,'C':45,'D':20,'E':65,'G':9}[k]
 front.annotate(k,(anchor[0],anchor[2]),(xloc,zloc),color=color,fontweight='bold',fontsize=12,arrowprops=dict(arrowstyle='-',color=color))
for wing in regions['local_wings']:
 a=math.radians(wing['rotation_z_deg']);R=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
 uv=np.array([[-27.5,-9.8],[27.5,-9.8]])
 xy=uv@R.T+np.array(wing['translation'][:2]);top.plot(xy[:,0],xy[:,1],color=colors['F'],lw=3)
 origin=np.array(wing['translation'][:2])+R@np.array([0,-13.5]);d=np.array(wing['outward'][:2])*9
 top.annotate('',origin+d,origin,arrowprops=dict(arrowstyle='->',color=colors['E'],lw=1.5))
top.annotate('F (4 levels / wing; 8 gaps)',(-38,30),(-70,4),color=colors['F'],fontsize=9,arrowprops=dict(arrowstyle='-',color=colors['F']))
for ax,anchor,label,where in [(front,(48,13.2),'C0',(66,14)),(front,(5.5,28),'D0',(10,34)),(top,(48,-20.5),'C0',(60,-35)),(top,(5.5,-47),'D0',(15,-52))]:
 ax.annotate(label,anchor,where,color='#946800',fontweight='bold',fontsize=9,arrowprops=dict(arrowstyle='-',color='#946800'))
for z in [18,29,40,51]:front.plot([-64,64],[z+.05,z+.05],color=colors['F'],alpha=.35,lw=1)
front.text(8,60,'F: red lines locate sill levels;\nsee each rotated wing frame.',color=colors['F'],fontsize=8)

def section(mesh,z):
 solid=Manifold(Mesh64(np.ascontiguousarray(mesh.vertices),np.ascontiguousarray(mesh.faces,dtype=np.uint64)))
 out=Polygon()
 for ring in solid.slice(z).to_polygons():out=out.symmetric_difference(Polygon(ring))
 return out
def draw_region(ax,poly,face,edge='none',hatch=None):
 if poly.is_empty:return
 if hasattr(poly,'geoms'):
  for p in poly.geoms:draw_region(ax,p,face,edge,hatch)
  return
 ax.add_patch(PatchPolygon(np.array(poly.exterior.coords),facecolor=face,edgecolor=edge,hatch=hatch,lw=.8))
 for ring in poly.interiors:ax.add_patch(PatchPolygon(np.array(ring.coords),facecolor='white',edgecolor='none'))
crop=box(35.6,-22.6,44,-18.7)
old=section(original,28.5)&crop;new=section(variant,28.5)&crop
draw_region(cax,old,'#b9b9b9');draw_region(cax,new-old,'#efb79f','#d04435','///')
cax.set_xlim(35.6,44);cax.set_ylim(-22.6,-18.7);cax.set_aspect('equal');cax.grid(alpha=.18)
cax.set_xlabel('model X (mm)');cax.set_ylabel('model Y (mm)')
cax.set_title('3  C: actual XY section at unchanged Z = 28.5 mm')
cax.annotate('original fin front\nY = -21.95', (37,-21.95),(38.1,-22.35),fontsize=8,arrowprops=dict(arrowstyle='->'))
cax.annotate('added solid behind fin\nold air depth 1.8 mm',(37,-20),(38.1,-19.65),fontsize=9,color=colors['C'],arrowprops=dict(arrowstyle='->',color=colors['C']))
cax.text(38.2,-20.9,'open bay retained',fontsize=9)
cax.text(35.8,-18.95,'grey = old solid; hatch = variant added section',fontsize=8)

fax.set_title('4  F: each wing local Y/Z detail (strongly exaggerated)')
fax.set_xlabel('wing local Y (mm)');fax.set_ylabel('Z relative to sill start z (mm)')
fax.add_patch(Rectangle((-9.9,-.08),.1,.18,facecolor='#b9b9b9'))
fax.add_patch(Rectangle((-9.75,-.08),.12,.32,facecolor='#b9b9b9'))
fax.add_patch(Rectangle((-9.81,0),.11,.1,facecolor='#efb79f',edgecolor='#d04435',hatch='///'))
fax.add_patch(Rectangle((-9.8,0),.05,.1,fill=False,edgecolor='#c00018',lw=2))
fax.annotate('original gap: 0.05 x 0.10 mm\nNO support / interface allowed',(-9.775,.05),(-9.98,.18),fontsize=9,color=colors['F'],arrowprops=dict(arrowstyle='->',color=colors['F']))
fax.text(-9.98,-.06,'sill front lip -13 unchanged; fill reaches -9.70\n0.01 sill overlap + 0.05 wall overlap',fontsize=8)
fax.set_xlim(-10,-9.6);fax.set_ylim(-.09,.26);fax.grid(alpha=.18)
fax.text(-9.98,.13,'z = 18, 29, 40, 51; both wings\nleft: rotate -14°, translate (-30,30,0)\nright: rotate +14°, translate (30,30,0)',fontsize=8)
fig.suptitle('NTHU Macronix — manufacturing inspection map\nOriginal 00f6bbdd / optional infill 6801f9c4; 150 x 124 x 68 mm; no slicing or print validation',fontsize=14)
fig.savefig(M/'region-map.png',dpi=150)
(M/'regions.json').write_text(json.dumps(regions,ensure_ascii=False,indent=2),encoding='utf-8')
print('saved',M/'region-map.png')
