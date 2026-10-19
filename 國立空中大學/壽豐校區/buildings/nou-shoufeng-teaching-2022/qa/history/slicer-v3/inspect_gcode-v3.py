"""Inspect actual deposited G-code and render true multilayer toolpath previews.

Dependencies: numpy, scipy, Pillow, matplotlib. No machine is controlled.
Unsupported-run screening is a raster approximation, not a physical bridge test.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

WORD = re.compile(r'([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))')
COLORS = {'External perimeter':'#155e75','Perimeter':'#0891b2','Solid infill':'#a3a3a3',
          'Top solid infill':'#7c3aed','Internal infill':'#a3a3a3','Bridge infill':'#f97316',
          'Overhang perimeter':'#e11d48','Gap fill':'#ca8a04','Skirt/Brim':'#94a3b8'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def parse(path):
    pos = dict(X=0.,Y=0.,Z=0.,E=0.); relative_e=False; relative_xyz=False
    typ='Unspecified'; width=.45; layer=-1; lines=path.read_text(encoding='utf-8').splitlines()
    segments=[]; layers={}; meta={}; temp_commands=[]; path_id=0
    for line in lines:
        if line.startswith(';LAYER_CHANGE'):
            layer+=1; layers[layer]=None
        if line.startswith(';TYPE:'): typ=line[6:].strip()
        if line.startswith(';WIDTH:'): width=float(line[7:].strip())
        if line.startswith(';Z:') and layer>=0: layers[layer]=float(line[3:])
        if line.startswith(';') and '=' in line:
            k,v=line[1:].split('=',1);meta[k.strip()]=v.strip()
        code=line.split(';',1)[0].strip()
        if not code: continue
        command=code.split()[0]; words={k:float(v) for k,v in WORD.findall(code)}
        if command=='M82':relative_e=False
        if command=='M83':relative_e=True
        if command=='G90':relative_xyz=False
        if command=='G91':relative_xyz=True
        if command in ('M104','M109','M140','M190'): temp_commands.append(code)
        if command=='G92':
            for k in pos:
                if k in words:pos[k]=words[k]
        if command in ('G0','G1'):
            new=pos.copy()
            for k in ('X','Y','Z'):
                if k in words:new[k]=(pos[k] if relative_xyz else 0.)+words[k]
            if 'E' in words:new['E']=(pos['E'] if relative_e else 0.)+words['E']
            length=math.hypot(new['X']-pos['X'],new['Y']-pos['Y']); de=new['E']-pos['E']
            if de>1e-8 and length>1e-6:
                segments.append((layer,typ,pos['X'],pos['Y'],new['X'],new['Y'],new['Z'],de,width,path_id))
            else:path_id+=1
            pos=new
    return segments,layers,meta,temp_commands

def unsupported_screen(bylayer,extent,resolution=.1,allowance=.15):
    """Previous-layer bead occupancy, sampled every <=0.1 mm along each path.
    +0.15 mm lateral growth allowance corresponds to 45 degrees at 0.15 mm layers.
    Reports unsupported sampled run of each contiguous path, excluding brim.
    Rasterization error is approximately +/- 0.15 mm; no interbead physics modeled.
    """
    xmin,ymin,xmax,ymax=extent; shape=(math.ceil((ymax-ymin)/resolution)+10,math.ceil((xmax-xmin)/resolution)+10)
    previous=None; worst=0.; all_unsupported=0.; unsupported_count=0; worst_detail=None
    support_layers=[]
    for lid,items in sorted(bylayer.items()):
        if not items:continue
        canvas=Image.new('1',(shape[1],shape[0]),0);draw=ImageDraw.Draw(canvas)
        if previous is not None:dist=distance_transform_edt(~previous)*resolution
        last_pid=None;run=0.
        layerworst=0.;layerlength=0.
        for s in items:
            _,typ,x1,y1,x2,y2,z,de,width,pid=s
            coords=[(int(round((x1-xmin)/resolution))+4,int(round((y1-ymin)/resolution))+4),
                    (int(round((x2-xmin)/resolution))+4,int(round((y2-ymin)/resolution))+4)]
            draw.line(coords,fill=1,width=max(1,math.ceil(width/resolution)))
            if previous is None:continue
            length=math.hypot(x2-x1,y2-y1);n=max(1,math.ceil(length/resolution));step=length/n
            t=(np.arange(n)+.5)/n
            xi=np.clip(np.rint((x1+(x2-x1)*t-xmin)/resolution).astype(int)+4,0,shape[1]-1)
            yi=np.clip(np.rint((y1+(y2-y1)*t-ymin)/resolution).astype(int)+4,0,shape[0]-1)
            unsupported=dist[yi,xi]>allowance+1e-7
            if pid!=last_pid:run=0.
            for val in unsupported:
                run=run+step if val else 0.
                if run>worst:
                    worst=run;worst_detail={'layer_index':lid,'z_mm':z,'type':typ,'path_id':pid}
                layerworst=max(layerworst,run)
            last_pid=pid
            value=float(unsupported.sum()*step);all_unsupported+=value;layerlength+=value
            unsupported_count+=int(unsupported.any())
        previous=np.array(canvas,dtype=bool)
        support_layers.append({'layer_index':lid,'maximum_sampled_run_mm':round(layerworst,4),
                               'unsupported_sampled_path_length_mm':round(layerlength,4)})
    return {'method':'Rasterized previous actual deposited bead footprints at 0.1 mm; path samples <=0.1 mm; 0.15 mm lateral growth allowance. Excludes brim.',
            'resolution_mm':resolution,'raster_error_estimate_mm':.15,'horizontal_growth_allowance_mm':allowance,
            'maximum_sampled_unsupported_run_mm':round(worst,4),'worst_run_location':worst_detail,
            'total_sampled_unsupported_length_mm':round(all_unsupported,4),'extrusion_segments_with_unsupported_samples':unsupported_count,
            'layers':support_layers,'limitation':'Screening only; overlap, cooling, sagging, adhesion, strength, and physical bridging are unverified.'}

def inspect(path,expected):
    segments,layers,meta,temps=parse(path)
    deposited=[s for s in segments if s[1]!='Skirt/Brim']
    arr=np.array([[s[2],s[3],s[4],s[5],s[6]] for s in deposited])
    bylayer=collections.defaultdict(list)
    for s in deposited:bylayer[s[0]].append(s)
    zs=sorted(set(s[6] for s in deposited)); z_gaps=np.diff(zs)
    centerbounds=[[float(min(arr[:,0].min(),arr[:,2].min())),float(min(arr[:,1].min(),arr[:,3].min())),float(arr[:,4].min())],
                  [float(max(arr[:,0].max(),arr[:,2].max())),float(max(arr[:,1].max(),arr[:,3].max())),float(arr[:,4].max())]]
    max_width=max(s[8] for s in deposited)
    beadbounds=[[centerbounds[0][0]-max_width/2,centerbounds[0][1]-max_width/2,0.],
                [centerbounds[1][0]+max_width/2,centerbounds[1][1]+max_width/2,centerbounds[1][2]]]
    counts=collections.Counter(s[1] for s in segments)
    lengths=collections.Counter()
    for s in segments:lengths[s[1]]+=math.hypot(s[4]-s[2],s[5]-s[3])
    extent=[centerbounds[0][0]-.6,centerbounds[0][1]-.6,centerbounds[1][0]+.6,centerbounds[1][1]+.6]
    result={'gcode_sha256':sha(path),'gcode_bytes':path.stat().st_size,'layer_count_declared':len(layers),
            'layers_with_model_extrusion':len(bylayer),'empty_model_layer_indices':[l for l in layers if not bylayer[l]],
            'extrusion_segment_count':len(segments),'feature_segment_counts':dict(counts),
            'feature_deposited_lengths_mm':{k:round(v,4) for k,v in lengths.items()},
            'support_feature_present':any('support' in k.lower() for k in counts),
            'bridge_or_overhang_features':{k:v for k,v in counts.items() if 'bridge' in k.lower() or 'overhang' in k.lower()},
            'model_extrusion_centerline_bounds_mm':centerbounds,'conservative_model_bead_bounds_mm':beadbounds,
            'bed_centering_mm':[110,110],'original_print_envelope_mm':expected,
            'xy_envelope_size_error_mm':[round(beadbounds[1][i]-beadbounds[0][i]-(expected[1][i]-expected[0][i]),4) for i in [0,1]],
            'first_extrusion_z_mm':zs[0],'last_extrusion_z_mm':zs[-1],
            'maximum_vertical_deposition_gap_mm':float(max(z_gaps)) if len(z_gaps) else 0,
            'vertical_gap_over_0p151mm':bool(len(z_gaps) and max(z_gaps)>.151),
            'positive_E_filament_mm':sum(s[7] for s in segments),'filament_volume_from_positive_E_mm3':sum(s[7] for s in segments)*math.pi*(1.75/2)**2,
            'slicer_filament_volume_mm3':meta.get('filament used [mm3]'),
            'slicer_filament_used_mm':meta.get('filament used [mm]'),
            'estimated_print_time':meta.get('estimated printing time (normal mode)'),
            'temperature_commands':temps,
            'nonzero_temperature_command':any(re.search(r'S([1-9]\d*|0*\.\d*[1-9])',x) for x in temps),
            'unsupported_path_screen':unsupported_screen(bylayer,extent)}
    return result,segments,bylayer

def preview(path,bylayer,name):
    lids=sorted(bylayer); selected=sorted(set([lids[0],lids[min(len(lids)-1,7)],lids[len(lids)//2],lids[-1]]))
    fig,axes=plt.subplots(2,2,figsize=(14,11),facecolor='#f8fafc')
    for ax,lid in zip(axes.flat,selected):
        groups=collections.defaultdict(list)
        for s in bylayer[lid]:groups[s[1]].append([[s[2],s[3]],[s[4],s[5]]])
        for typ,ss in groups.items():ax.add_collection(LineCollection(ss,colors=COLORS.get(typ,'#475569'),linewidths=.32,label=typ))
        ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)')
        ax.set_title(f'Layer {lid+1} / {len(lids)} | Z {bylayer[lid][0][6]:.2f} mm',fontsize=10);ax.grid(alpha=.13)
    for ax in list(axes.flat)[len(selected):]:ax.axis('off')
    handles={}
    for ax in axes.flat:
        hh,ll=ax.get_legend_handles_labels();handles.update(zip(ll,hh))
    fig.legend(handles.values(),handles.keys(),loc='lower center',ncol=4,fontsize=8)
    fig.suptitle(f'{name}\nActual G-code deposited paths | original orientation, 100% scale | QA ONLY',fontsize=13)
    fig.tight_layout(rect=[0,.055,1,.95]);fig.savefig(path,dpi=150);plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    qa=a.root/'qa';record=json.loads((qa/'slicer-run-record.json').read_text(encoding='utf-8'))
    summary={k:v for k,v in record.items() if k!='runs'};summary['parts']=[]
    for run in record['runs']:
        if run['exit_code']!=0 or not run['gcode']:summary['parts'].append(run);continue
        result,segments,bylayer=inspect(qa/run['gcode'],run['source_print_bounds_mm'])
        imagepath=qa/'slicer'/(run['part']+'-paths.png');preview(imagepath,bylayer,run['part'])
        result['path_preview']='slicer/'+imagepath.name;result['path_preview_sha256']=sha(imagepath)
        result.update(run)
        (qa/'slicer'/(run['part']+'-inspection.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
        summary['parts'].append(result)
        print(json.dumps({'part':run['part'],'layers':result['layers_with_model_extrusion'],
                          'features':result['feature_segment_counts'],'max_vertical_gap_mm':result['maximum_vertical_deposition_gap_mm'],
                          'max_unsupported_run_mm':result['unsupported_path_screen']['maximum_sampled_unsupported_run_mm']}),flush=True)
    summary['all_nine_inspected']=len(summary['parts'])==9 and all('layers_with_model_extrusion' in r for r in summary['parts'])
    summary['physical_validation']='No physical print, support removal, or fit test performed.'
    (qa/'slicer-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

if __name__=='__main__':main()
