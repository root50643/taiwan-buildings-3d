"""Four actual fixed-plane mesh sections, not perspective renders."""
from pathlib import Path
import json, sys, hashlib
import numpy as np
import trimesh
from shapely import wkt
from shapely.geometry import box
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
Q=Path(__file__).resolve().parent
sys.path.insert(0,str(Q.parent))
from geometry_delta import section

old=trimesh.load(Q/'input-original.stl',force='mesh',process=True)
new=trimesh.load(Q.parents[1]/'model.stl',force='mesh',process=True)
orig=json.loads((Q/'input-original-extended.json').read_text(encoding='utf-8'))
origshort=min(orig['normal_chord_thickness_screen']['flagged_samples'],key=lambda r:r['distance_mm'])
xy_z=origshort['start_mm'][2]
info,oldxy=section(old,xy_z)
assert info['closed'] and info['polygon_valid']
data=json.loads((Q/'thin_r2_fixed_sections.json').read_text(encoding='utf-8'))
newinfo,newxy=section(new,xy_z)
assert newinfo['closed'] and newinfo['polygon_valid']
yz=wkt.loads(data['new_shortest_ray_fixed_X_YZ_section']['actual_STL_section_WKT'])
rows=json.loads((Q/'r2-extended-checks.json').read_text(encoding='utf-8'))['normal_chord_thickness_screen']['flagged_samples']
short=min(rows,key=lambda r:r['distance_mm'])

def draw(ax,g,color):
    if g.is_empty:return
    for p in [g] if g.geom_type=='Polygon' else list(g.geoms):
        if p.geom_type!='Polygon':continue
        a=np.asarray(p.exterior.coords);ax.fill(a[:,0],a[:,1],facecolor=color,edgecolor='#273549',lw=.8)
        for hole in p.interiors:
            a=np.asarray(hole.coords);ax.fill(a[:,0],a[:,1],color='white')

fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for ax in axes.flat:ax.grid(alpha=.2);ax.set_aspect('equal',adjustable='box');ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)')
draw(axes[0,0],oldxy.intersection(box(-41,-12,-3,-4)),'#f0b9ac')
axes[0,0].set(xlim=(-41,-3),ylim=(-12,-4),title=f'Previous candidate: XY at original Z={xy_z:.6f} mm')
draw(axes[0,1],newxy.intersection(box(-41,-12,-3,-4)),'#a6d7cc')
axes[0,1].set(xlim=(-41,-3),ylim=(-12,-4),title='R2: same Z; flat ends and shallow recess')
p=np.array(origshort['start_mm']);e=p+np.array(origshort['inward_direction'])*origshort['distance_mm']
draw(axes[1,0],oldxy.intersection(box(-12.95,-6.6,-12.65,-6.35)),'#f0b9ac')
axes[1,0].plot([p[0],e[0]],[p[1],e[1]],'r.-',lw=2,label='Original 0.006248 mm chord')
axes[1,0].set(xlim=(-12.95,-12.65),ylim=(-6.6,-6.35),title='Original fixed source XY location: crescent tip')
axes[1,0].legend(fontsize=8,loc='lower left')
draw(axes[1,1],yz,'#a6d7cc')
p=np.array(short['start_mm']);e=p+np.array(short['inward_direction'])*short['distance_mm']
axes[1,1].plot([p[1],e[1]],[p[2],e[2]],'r.-',lw=2,label='R2 0.181054 mm normal chord')
axes[1,1].plot([-7,-7],[50.55,51.85],'b-',lw=2,label='Actual end face: 1.299999 mm Z')
axes[1,1].set(xlim=(-9.3,-6.8),ylim=(49.9,52.2),xlabel='Y (mm)',ylabel='Z (mm)',title='R2 fixed X=-36.552914 mm: plate end corner')
axes[1,1].legend(fontsize=8,loc='lower left')
fig.suptitle('Thin-feature interpretation from actual STL sections; no shifted sample planes',fontsize=14)
out=Q/'fixed-sections.png';fig.savefig(out,dpi=150);plt.close(fig)
print(json.dumps({'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'old_stl_sha256':hashlib.sha256((Q/'input-original.stl').read_bytes()).hexdigest(),'r2_stl_sha256':hashlib.sha256((Q.parents[1]/'model.stl').read_bytes()).hexdigest(),'planes':[f'XY Z={xy_z}','YZ X=-36.5529137'],'no_perspective_render':True}))
