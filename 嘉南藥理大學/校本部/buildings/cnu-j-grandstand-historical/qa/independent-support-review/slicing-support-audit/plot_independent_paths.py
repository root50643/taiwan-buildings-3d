from pathlib import Path
import json,sys
sys.path.insert(0,'${PYTHON_AUDIT_DEPS}')
import numpy as np,trimesh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from audit_slices import parse
R=Path(__file__).resolve().parent
old=Path('${ORIGINAL_DIAGNOSTIC_GCODE_DIR}')
_,a=parse(old/'main_body-DIAGNOSTIC-ONLY.gcode',True)
_,b=parse(R/'raw-reslice-private/REVIEW-ONLY-main-short-axis-DO-NOT-PRINT.gcode',True)
_,roof=parse(old/'roof-DIAGNOSTIC-ONLY.gcode',True)
fig,axs=plt.subplots(2,2,figsize=(14,8.2),layout='constrained')
for ax,paths,title in [(axs[0,0],a,'Original auto bridge direction: NOT accepted as print process'),(axs[0,1],b,'Review-only: short-axis bridge + support bridges')]:
    for what,color in [('object','#999999'),('support','#df8c29'),('bridge','#2573b6')]:
        seg=[]
        for p,q,role,line,de in paths:
            match=(role=='Bridge infill' and abs(q[2]-12.6)<.001) if what=='bridge' else ((role.startswith('Support') and 11.99<=q[2]<=12.21) if what=='support' else (not role.startswith('Support') and abs(q[2]-12.4)<.001))
            if match and min(p[1],q[1])<84:seg.append(np.array([p[:2],q[:2]])-[125,111])
        ax.add_collection(LineCollection(seg,colors=color,linewidths=.7 if what!='support' else .8,label=what))
    ax.set(xlim=(-92,92),ylim=(-36.5,-27.5),xlabel='Assembly X (mm)',ylabel='Assembly Y (mm)',title=title)
    ax.legend(loc='upper right',fontsize=7)
axs[0,0].text(-85,-35.9,'Longitudinal centerline gap up to 174.289 mm',fontsize=8,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
axs[0,1].text(-85,-35.9,'At Z12.6: longest planned gap 1.704 mm',fontsize=8,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
ax=axs[1,0]
for z,color,label in [(1.6,'#999999','previous extrusion at Z1.6'),(1.8,'#2573b6','bridge at Z1.8')]:
    seg=[np.array([p[:2],q[:2]]) for p,q,role,line,de in roof if abs(q[2]-z)<.001 and (z==1.6 or role=='Bridge infill')]
    ax.add_collection(LineCollection(seg,colors=color,linewidths=1,label=label))
d=json.loads((R/'all-bridge-coverage.json').read_text());maximum=d['parts'][1]['gaps_declared_width_top20'][0]['gap']['xy'];xy=np.array(maximum)
ax.plot(xy[:,0],xy[:,1],color='#bc2935',lw=3,label='8.036 mm actual centerline gap')
ax.set(xlim=(170,181),ylim=(87,93),xlabel='G-code X (mm)',ylabel='G-code Y (mm)',title='Canopy sparse-infill closure: more than 2.6 mm sockets');ax.set_aspect('equal');ax.legend(fontsize=7)
ax=axs[1,1]
body=trimesh.load_mesh(R.parent/'candidate/parts/main_body-assembly.stl',process=True)
section=body.section(plane_origin=[0,0,8],plane_normal=[0,0,1])
for segment in section.discrete:ax.plot(segment[:,0],segment[:,1],color='#888888',lw=1)
d=json.loads((R/'support-access-and-bridge.json').read_text());pts=np.array(d['no_eight_direction_points']);ax.scatter(pts[:,0],pts[:,1],s=2,c='#bc2935',label='580 original horizontal-ray flags')
for sign in [-1,1]:
    p=np.array([sign*37,-30.25]);route=np.array([p,[sign*37,-33],[sign*65,-33],[sign*65,-48]])
    ax.plot(route[:,0],route[:,1],color='#23875b',lw=2)
ax.set(xlim=(-70,70),ylim=(-48,-26),xlabel='Assembly X (mm)',ylabel='Assembly Y (mm)',title='Z8 body section: exterior 4.5 mm corridor / point route')
ax.legend(loc='lower center',fontsize=7)
fig.suptitle('Independent actual-path evidence | 0.4 nozzle / 0.2 layers | finite toolpath and point checks; no physical print/removal test',fontsize=11)
fig.savefig(R/'independent-path-evidence.png',dpi=160,facecolor='white')
plt.close(fig)
