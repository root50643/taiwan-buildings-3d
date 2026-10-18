"""Render a compact view of actual diagnostic G-code paths (not a model render).
Set PRIVATE_SLICE_DIR to the external directory containing diagnostic G-code.
"""
from pathlib import Path
import os,re,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle

HERE=Path(__file__).resolve().parent
PRIVATE=Path(os.environ['PRIVATE_SLICE_DIR'])

def paths(name):
    xyz=np.zeros(3);e=0.;role='';out=[]
    for line in (PRIVATE/(name+'-DIAGNOSTIC-ONLY.gcode')).read_text().splitlines():
        if line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        c=line.split(';',1)[0].strip();cmd=c.split()[0] if c else ''
        vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',c)}
        if cmd=='G92':e=vals.get('E',e);continue
        if cmd not in ['G0','G1']:continue
        q=xyz.copy()
        for i,k in enumerate('XYZ'):q[i]=vals.get(k,xyz[i])
        en=vals.get('E',e)
        if en-e>1e-7 and np.linalg.norm(q[:2]-xyz[:2])>1e-7:out.append((role,float(q[2]),np.array([xyz[:2],q[:2]])))
        xyz=q;e=en
    return out

def main():
    a=paths('main_body');b=paths('roof')
    # Highest front support path below the balcony and its first object layer.
    sz=max(z for role,z,p in a if role.startswith('Support') and p[:,1].min()<80 and z<12.4)
    fig,axes=plt.subplots(1,2,figsize=(12,4.2),constrained_layout=True)
    ax=axes[0]
    for support,color,lw in [(False,'#596574',.55),(True,'#d76c17',1.0)]:
        seg=[p-np.array([125,111]) for role,z,p in a if (role.startswith('Support') if support else not role.startswith('Support')) and abs(z-(sz if support else 12.6))<.001 and p[:,1].min()<83]
        ax.add_collection(LineCollection(seg,colors=color,linewidths=lw))
    ax.set_xlim(-96,96);ax.set_ylim(-40,-27);ax.set_aspect('equal');ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm)')
    ax.set_title(f'Front balcony: support Z={sz:.2f} mm\nOrange support; grey first ledge layer Z=12.60 mm',fontsize=10)
    ax.axhline(-31,color='#344955',ls='--',lw=.6);ax.text(0,-30.4,'front wall Y=-31',ha='center',fontsize=8)
    ax=axes[1]
    for bridge,color,lw in [(False,'#a3aab2',.7),(True,'#226dc4',1.2)]:
        seg=[]
        for role,z,p in b:
            if abs(z-1.)>.001 or (role=='Bridge infill')!=bridge:continue
            q=p.copy();q[:,0]-=125;q[:,1]=105-q[:,1]
            if q[:,0].max()>77 and q[:,0].min()<85 and q[:,1].max()>10 and q[:,1].min()<20:seg.append(q)
        ax.add_collection(LineCollection(seg,colors=color,linewidths=lw))
    ax.add_patch(Rectangle((79.7,13.1),2.6,3.8,fill=False,edgecolor='#d76c17',linestyle='--',linewidth=1.3))
    ax.set_xlim(77,85);ax.set_ylim(10,20);ax.set_aspect('equal');ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm)')
    ax.set_title('Canopy top down: actual Z=1.00 mm paths\nBlue bridge closes 2.6 x 3.8 mm blind socket',fontsize=10)
    fig.suptitle('PrusaSlicer 2.9.6 diagnostic paths | 0.4 mm nozzle, 0.2 mm layers | no physical print test',fontsize=11)
    fig.savefig(HERE/'slice-evidence.png',dpi=170,facecolor='white');plt.close(fig)
    (HERE/'slice-evidence.json').write_text(json.dumps({'main_front_support_z_mm':sz,'main_object_layer_z_mm':12.6,'roof_socket_bridge_z_mm':1.0,'roof_socket_opening_mm':[2.6,3.8],'source':'Actual positive-E XY segments from hashed diagnostic G-code; coordinate map is inverted to original assembly coordinates.'},indent=2)+'\n')
    print('front support Z',sz)

if __name__=='__main__':main()
