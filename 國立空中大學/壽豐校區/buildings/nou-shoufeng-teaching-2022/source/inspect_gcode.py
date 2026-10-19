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
    +0.15 mm fixed lateral growth allowance permits direct comparison of .15/.20 profiles.
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
    return {'method':'Rasterized previous actual deposited bead footprints at 0.1 mm; path samples <=0.1 mm; fixed 0.15 mm lateral growth allowance for comparison across profiles. Excludes brim.',
            'resolution_mm':resolution,'raster_error_estimate_mm':.15,'horizontal_growth_allowance_mm':allowance,
            'maximum_sampled_unsupported_run_mm':round(worst,4),'worst_run_location':worst_detail,
            'total_sampled_unsupported_length_mm':round(all_unsupported,4),'extrusion_segments_with_unsupported_samples':unsupported_count,
            'layers':support_layers,'limitation':'Screening only; overlap, cooling, sagging, adhesion, strength, and physical bridging are unverified.'}

def lateral_followup(bylayer,extent,screen,resolution=.1):
    """Additional measurement for previously flagged layers, kept apart from run length.
    A long path parallel to a shallow window lip is not an equally long free bridge.
    """
    targets=[v['layer_index'] for v in screen['layers'] if v['maximum_sampled_run_mm']>0]
    xmin,ymin,xmax,ymax=extent;shape=(math.ceil((ymax-ymin)/resolution)+10,math.ceil((xmax-xmin)/resolution)+10)
    maximum=0.;worst=None;features={}
    for lid in targets:
        if lid-1 not in bylayer:continue
        canvas=Image.new('1',(shape[1],shape[0]),0);draw=ImageDraw.Draw(canvas)
        for s in bylayer[lid-1]:
            coords=[(int(round((s[2]-xmin)/resolution))+4,int(round((s[3]-ymin)/resolution))+4),
                    (int(round((s[4]-xmin)/resolution))+4,int(round((s[5]-ymin)/resolution))+4)]
            draw.line(coords,fill=1,width=max(1,math.ceil(s[8]/resolution)))
        dist=distance_transform_edt(~np.array(canvas,dtype=bool))*resolution
        for s in bylayer[lid]:
            length=math.hypot(s[4]-s[2],s[5]-s[3]);n=max(1,math.ceil(length/resolution));t=(np.arange(n)+.5)/n
            xs=s[2]+(s[4]-s[2])*t;ys=s[3]+(s[5]-s[3])*t
            xi=np.clip(np.rint((xs-xmin)/resolution).astype(int)+4,0,shape[1]-1)
            yi=np.clip(np.rint((ys-ymin)/resolution).astype(int)+4,0,shape[0]-1)
            distances=dist[yi,xi];value=float(distances.max());j=int(distances.argmax())
            features[s[1]]=max(features.get(s[1],0.),value)
            if value>maximum:maximum=value;worst={'layer_index':lid,'z_mm':s[6],'type':s[1],'sample_xy_mm':[float(xs[j]),float(ys[j])]}
    return {'supplement_to':'unsupported_path_screen; same G-code, no geometry or slicer change',
            'measurement':'Shortest in-plane distance from each sampled current-layer extrusion centerline to rasterized previous-layer bead footprint. Distinct from along-path unsupported run length.',
            'screened_flagged_layer_indices':targets,'maximum_lateral_distance_mm':maximum if targets else None,
            'maximum_lateral_distance_upper_bound_mm':None if targets else .15,
            'maximum_lateral_distance_by_feature_mm':features,'worst_location':worst,
            'raster_error_estimate_mm':.15,'sampling_interval_max_mm':.1,
            'interpretation':'Window-lip path can be long along the facade while shallow laterally. This is not a test of bridge sag or adhesion.'}

def inspect(path,expected,prior=None):
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
    sweptbounds=[[min(min(s[2],s[4])-s[8]/2 for s in deposited),min(min(s[3],s[5])-s[8]/2 for s in deposited),0.],
                 [max(max(s[2],s[4])+s[8]/2 for s in deposited),max(max(s[3],s[5])+s[8]/2 for s in deposited),zs[-1]]]
    counts=collections.Counter(s[1] for s in segments)
    lengths=collections.Counter()
    for s in segments:lengths[s[1]]+=math.hypot(s[4]-s[2],s[5]-s[3])
    extent=[centerbounds[0][0]-.6,centerbounds[0][1]-.6,centerbounds[1][0]+.6,centerbounds[1][1]+.6]
    screen=prior['unsupported_path_screen'] if prior and prior.get('gcode_sha256')==sha(path) else unsupported_screen(bylayer,extent)
    nominal_layer=float(meta.get('layer_height','.15'))
    result={'gcode_sha256':sha(path),'gcode_bytes':path.stat().st_size,'layer_count_declared':len(layers),
            'layers_with_model_extrusion':len(bylayer),'empty_model_layer_indices':[l for l in layers if not bylayer[l]],
            'extrusion_segment_count':len(segments),'feature_segment_counts':dict(counts),
            'feature_deposited_lengths_mm':{k:round(v,4) for k,v in lengths.items()},
            'support_feature_present':any('support' in k.lower() for k in counts),
            'bridge_or_overhang_features':{k:v for k,v in counts.items() if 'bridge' in k.lower() or 'overhang' in k.lower()},
            'model_extrusion_centerline_bounds_mm':centerbounds,'conservative_model_bead_bounds_mm':beadbounds,
            'model_bead_sweep_bounds_mm':sweptbounds,
            'bed_centering_mm':[110,110],'original_print_envelope_mm':expected,
            'xy_envelope_size_error_mm':[round(beadbounds[1][i]-beadbounds[0][i]-(expected[1][i]-expected[0][i]),4) for i in [0,1]],
            'first_extrusion_z_mm':zs[0],'last_extrusion_z_mm':zs[-1],
            'maximum_vertical_deposition_gap_mm':float(max(z_gaps)) if len(z_gaps) else 0,
            'nominal_layer_height_mm':nominal_layer,
            'vertical_gap_threshold_mm':nominal_layer+.001,
            'vertical_gap_over_profile_tolerance':bool(len(z_gaps) and max(z_gaps)>nominal_layer+.001),
            'positive_E_filament_mm':sum(s[7] for s in segments),'filament_volume_from_positive_E_mm3':sum(s[7] for s in segments)*math.pi*(1.75/2)**2,
            'slicer_filament_volume_mm3':meta.get('filament used [mm3]'),
            'slicer_filament_volume_cm3':meta.get('filament used [cm3]'),
            'slicer_filament_used_mm':meta.get('filament used [mm]'),
            'estimated_print_time':meta.get('estimated printing time (normal mode)'),
            'temperature_commands':temps,
            'nonzero_temperature_command':any(re.search(r'S([1-9]\d*|0*\.\d*[1-9])',x) for x in temps),
            'unsupported_path_screen':screen,
            'lateral_support_distance_followup':lateral_followup(bylayer,extent,screen)}
    return result,segments,bylayer

def interface_check(bylayer,name,expected,layer_height):
    """Check actual boundary deposition Z and footprint before/after a planar slab.
    The probe is safely inside the open corridor for lower/cap pieces, or bare roof
    interior for roof. 100% infill makes the below/above footprint comparison useful.
    This tests slicing of planar geometry, not physical flatness or assembly fit.
    """
    zitems={round(items[0][6],5):items for items in bylayer.values() if items}
    if 'ceiling' in name:
        slab=1.2;probe=[70.,4.];required=[1.2,3.2];expected_slab_layers=6
    elif name.startswith('09'):
        slab=1.2;probe=[70.,15.];required=[1.2,3.4,6.0];expected_slab_layers=6
    elif name.startswith('01'):
        slab=3.6;probe=[70.,26.];required=[2.0,3.6,10.8];expected_slab_layers=18
    else:
        slab=1.6;probe=[70.,26.];required=[1.6,8.8];expected_slab_layers=8
    translation=[110-(expected[0][i]+expected[1][i])/2 for i in (0,1)]
    xy=np.array(probe)+translation
    def distance_to_bead(items):
        best=float('inf')
        for s in items:
            a=np.array([s[2],s[3]]);b=np.array([s[4],s[5]]);v=b-a
            t=np.clip(np.dot(xy-a,v)/np.dot(v,v),0.,1.)
            best=min(best,float(np.linalg.norm(xy-(a+t*v)))-s[8]/2)
        return best
    boundary=round(slab,5);nextz=round(slab+layer_height,5)
    lower_distance=distance_to_bead(zitems.get(boundary,[]))
    upper_distance=distance_to_bead(zitems.get(nextz,[]))
    count=sum(z<=slab+1e-5 for z in zitems)
    planes=[{'required_z_mm':z,'present_as_actual_deposition_z':round(z,5) in zitems,
             'nearest_actual_z_mm':min(zitems,key=lambda a:abs(a-z))} for z in required]
    return {'method':'Actual G-code deposition-layer Z values plus 100%-infill slab-interior probe footprint immediately below/above its top plane.',
            'required_print_z_planes':planes,'slab_top_z_mm':slab,'slab_layer_count':count,
            'expected_slab_layer_count_for_0p20mm':expected_slab_layers,
            'probe_stl_xy_mm':probe,'probe_gcode_xy_mm':xy.tolist(),
            'probe_at_slab_top':{'actual_z_mm':boundary,'signed_distance_to_actual_bead_edge_mm':lower_distance,
                                 'covered_by_deposited_bead':lower_distance<=.001},
            'probe_next_layer':{'actual_z_mm':nextz,'signed_distance_to_actual_bead_edge_mm':upper_distance,
                                'covered_by_deposited_bead':upper_distance<=.001},
            'primary_interface_z_matches_stl':all(v['present_as_actual_deposition_z'] for v in planes),
            'slab_footprint_transition_confirmed':lower_distance<=.001 and upper_distance>.1,
            'limitation':'Toolpath Z/footprint checks only; no physical flatness, glue-gap or fit verification.'}

def preview(path,bylayer,name,screen):
    lids=sorted(bylayer)
    selected=sorted(set([lids[0],lids[min(len(lids)-1,7)],screen['worst_run_location']['layer_index'] if screen['worst_run_location'] else lids[len(lids)//2],lids[-1]]))
    for fallback in [lids[len(lids)//2],lids[len(lids)//4],lids[3*len(lids)//4]]:
        if len(selected)>=4:break
        if fallback not in selected:selected.append(fallback);selected.sort()
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--reuse-screening',action='store_true',help='Reuse exact-G-code-SHA matched previous all-layer screen; recompute parse, lateral follow-up and previews.');a=p.parse_args()
    qa=a.root/'qa';record=json.loads((qa/'slicer-run-record.json').read_text(encoding='utf-8'))
    summary={k:v for k,v in record.items() if k!='runs'};summary['parts']=[]
    for run in record['runs']:
        if run['exit_code']!=0 or not run['gcode']:summary['parts'].append(run);continue
        oldpath=qa/'slicer'/(run['part']+'-inspection.json')
        prior=json.loads(oldpath.read_text(encoding='utf-8')) if a.reuse_screening and oldpath.exists() else None
        result,segments,bylayer=inspect(qa/run['gcode'],run['source_print_bounds_mm'],prior)
        imagepath=qa/'slicer'/(run['part']+'-paths.png');preview(imagepath,bylayer,run['part'],result['unsupported_path_screen'])
        result['mesh_flags']={'slicer_reported_manifold':run['model_info'].get('manifold'),
                              'slicer_reported_number_of_parts':run['model_info'].get('number_of_parts'),
                              'repair_log_messages':[s for s in run['warnings'] if 'repair' in s.lower()],
                              'needed_repair_flag_available_in_cli_info':False,
                              'limitation':'CLI --info exposes manifold/part count but no explicit needed_repair boolean; absence of repair messages is not proof no internal repair occurred.'}
        _,_,profile,_=parse(qa/run['gcode'])
        keys=['layer_height','first_layer_height','nozzle_diameter','extrusion_width','first_layer_extrusion_width',
              'perimeters','fill_density','fill_pattern','top_solid_layers','bottom_solid_layers','brim_width',
              'support_material','support_material_auto','raft_layers','temperature','first_layer_temperature',
              'bed_temperature','first_layer_bed_temperature','autoemit_temperature_commands']
        result['embedded_profile_verification']={
            'actual_gcode_footer_settings':{k:profile.get(k) for k in keys},
            'mismatches_against_qa_config':[{ 'key':k,'actual':profile.get(k),'expected':record['settings'].get(k)}
                                           for k in keys if profile.get(k)!=record['settings'].get(k)],
            'print_orientation_evidence':'Original STL orientation; no rotate/cut transform in recorded command; --scale 100%; --info bounds match original STL and deposited envelope preserves size.'}
        result['planar_interface_verification']=interface_check(bylayer,run['part'],run['source_print_bounds_mm'],float(profile['layer_height']))
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
