"""Read-only audit of the actual candidate G-code against the STL.

Run with numpy, trimesh, shapely>=2 and matplotlib. Outputs start with
``slicer-analysis``. This never executes G-code or changes the model/profile.
All accessibility checks are digital horizontal strand-corridor checks, not
physical support removal tests or a machine-ready print qualification.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse, gzip, hashlib, json, math, re, sys, time
import numpy as np
import trimesh
import shapely
from shapely.geometry import LineString, Polygon, GeometryCollection
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

QA = Path(__file__).resolve().parent
ROOT = QA.parent
TYPES = ['Perimeter','External perimeter','Internal infill','Solid infill',
         'Top solid infill','Support material','Support material interface',
         'Bridge infill','Overhang perimeter','Custom']
SUPPORT = {'Support material','Support material interface'}
NUM = re.compile(r'([A-Z])\s*([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)')

def sha(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def open_gcode(path):
    return gzip.open(path,'rt',encoding='utf8') if path.suffix=='.gz' else path.open(encoding='utf8')

def raw_gcode_sha(path):
    h=hashlib.sha256();size=0
    f=gzip.open(path,'rb') if path.suffix=='.gz' else path.open('rb')
    with f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b);size+=len(b)
    return h.hexdigest(),size

class Parser:
    def __init__(self):
        self.xyz=np.zeros(3); self.e=0.; self.abs_xyz=True; self.abs_e=True
        self.units=1.; self.count=Counter(); self.unsupported=Counter()
    def move(self,line):
        code=line.split(';',1)[0].strip().upper()
        if not code:return None
        words=NUM.findall(code)
        if not words:return None
        cmd=words[0][0]+str(int(float(words[0][1])))
        v={k:float(n) for k,n in words[1:]}
        self.count[cmd]+=1
        if cmd=='M82':self.abs_e=True
        elif cmd=='M83':self.abs_e=False
        elif cmd=='G90':self.abs_xyz=True
        elif cmd=='G91':self.abs_xyz=False
        elif cmd=='G20':self.units=25.4
        elif cmd=='G21':self.units=1.
        elif cmd=='G92':
            for i,k in enumerate('XYZ'):
                if k in v:self.xyz[i]=v[k]*self.units
            if 'E' in v:self.e=v['E']*self.units
        elif cmd in ('G0','G1'):
            a=self.xyz.copy(); new=self.xyz.copy()
            for i,k in enumerate('XYZ'):
                if k in v:new[i]=v[k]*self.units+(0. if self.abs_xyz else self.xyz[i])
            de=0.
            if 'E' in v:
                ne=v['E']*self.units+(0. if self.abs_e else self.e)
                de=ne-self.e; self.e=ne
            self.xyz=new
            return a,new.copy(),de
        elif cmd in ('G2','G3','G5','G10','G11'):
            self.unsupported[cmd]+=1
        return None

def parser_fixture():
    p=Parser(); result=[]
    for l in ['G90','M82','G92 E0','G0 X1 Y2 Z.2','G1 X3 E1',
              'G92 E0','G1 Y4 E.5','M83','G1 X4 E.25','G1 E-.2',
              'G91','G0 X1 Z.2','G1 Y1 E.1','G90','M82','G92 E4','G1 X7 E4.3']:
        r=p.move(l)
        if r is not None:result.append([*r[1],r[2]])
    expected=np.array([[1,2,.2,0],[3,2,.2,1],[3,4,.2,.5],[4,4,.2,.25],
                       [4,4,.2,-.2],[5,4,.4,0],[5,5,.4,.1],[7,5,.4,.3]])
    ok=bool(np.allclose(np.array(result),expected,atol=1e-10))
    if not ok:raise AssertionError((result,expected.tolist()))
    return {'passed':ok,'cases':'G0/G1, absolute/relative XYZ, M82/M83, G92 E, retract/unretract, coordinate-only travel'}

def section(mesh,z):
    path=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if path is None:return GeometryCollection(),0
    result=GeometryCollection(); unclosed=0
    for curve in path.discrete:
        xy=np.asarray(curve)[:,:2]
        if np.linalg.norm(xy[0]-xy[-1])>1e-5:unclosed+=1;continue
        poly=Polygon(xy)
        if not poly.is_valid:poly=shapely.make_valid(poly)
        result=result.symmetric_difference(poly)
    return result,unclosed

def polys(g):
    if g.geom_type=='Polygon':return [g]
    return [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon']

def slab_projection(mesh,lo,hi):
    """Continuous XY shadow of the solid in a Z slab.

    Every occupied vertical line meets a slab-end solid section or a boundary
    triangle. Union their projections after clipping triangles to this slab.
    """
    lo+=1e-6;hi-=1e-6
    parts=[section(mesh,lo)[0],section(mesh,hi)[0]]
    tri=np.asarray(mesh.triangles)
    active=tri[(tri[:,:,2].min(1)<=hi)&(tri[:,:,2].max(1)>=lo)]
    for t in active:
        points=list(t)
        for z,above in [(lo,True),(hi,False)]:
            new=[]
            for a,b in zip(points,points[1:]+points[:1]):
                ia=a[2]>=z if above else a[2]<=z
                ib=b[2]>=z if above else b[2]<=z
                if ia:new.append(a)
                if ia!=ib:new.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
            points=new
            if not points:break
        if len(points)>=3:
            poly=Polygon(np.asarray(points)[:,:2])
            if poly.area>1e-12:parts.append(poly)
    return unary_union(parts)

def ranges(numbers):
    groups=[]
    for v in sorted(set(numbers)):
        if not groups or v>groups[-1][-1]+1:groups.append([v])
        else:groups[-1].append(v)
    return [[g[0],g[-1]] for g in groups]

def plot_layer(layer,shape,translation,out):
    fig,ax=plt.subplots(figsize=(11,8))
    for poly in polys(shape):
        x,y=poly.exterior.xy;ax.fill(np.array(x)+translation[0],np.array(y)+translation[1],color='#dddddd',alpha=.9,zorder=0)
        ax.plot(np.array(x)+translation[0],np.array(y)+translation[1],color='#333333',lw=.7)
        for ring in poly.interiors:
            x,y=ring.xy;ax.fill(np.array(x)+translation[0],np.array(y)+translation[1],color='white')
    colors={'Support material':'#ed8b23','Support material interface':'#d12893','Overhang perimeter':'#09a5bf','Bridge infill':'#6b41bc'}
    for kind,arr in layer['paths'].items():
        if not arr:continue
        a=np.asarray(arr)
        if kind in colors:color=colors[kind];lw=1.1;label=kind
        elif kind=='External perimeter':color='#235ab6';lw=.45;label=kind
        else:continue
        ax.add_collection(LineCollection(a[:,:4].reshape(-1,2,2),colors=color,linewidths=lw,label=label))
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('G-code X (mm)');ax.set_ylabel('G-code Y (mm)')
    ax.set_title(f"Actual G-code layer {layer['index']} | Z={layer['z']:.3f} mm | mesh section Z={layer['sample_z']:.3f} mm")
    ax.legend(loc='upper right',fontsize=8);ax.grid(alpha=.15)
    fig.tight_layout();fig.savefig(out,dpi=150);plt.close(fig)

def inspect_outliers(gcode,model):
    """Retain exact exceptions from the section comparison, including lines."""
    report=json.loads((QA/'slicer-analysis.json').read_text(encoding='utf8'))
    rows=json.loads((QA/'slicer-analysis-layers.json').read_text(encoding='utf8'))['layers']
    wanted={r['layer'] for r in rows if r['model_paths_outside_section_plus_0_30mm_segments']}
    mesh=trimesh.load_mesh(model,process=True);shift=np.asarray(report['xy_translation_model_to_gcode_mm'])
    parser=Parser();no=0;z=0.;height=.2;width=.45;kind='Custom';events=[];cache={}
    for ln,line in enumerate(open_gcode(gcode),1):
        s=line.strip()
        if s==';LAYER_CHANGE':no+=1
        elif s.startswith(';Z:'):z=float(s[3:])
        elif s.startswith(';HEIGHT:'):height=float(s[8:])
        elif s.startswith(';WIDTH:'):width=float(s[7:])
        elif s.startswith(';TYPE:'):kind=s[6:]
        move=parser.move(line)
        if no not in wanted or move is None or kind in SUPPORT or kind=='Custom':continue
        a,b,e=move
        if e<=1e-9 or np.linalg.norm(a-b)<1e-8:continue
        key=(z,.2)
        if key not in cache:
            # Bridge HEIGHT describes its circular extrusion cross-section;
            # mesh slicing planes still follow the model's 0.2mm schedule.
            sample=z-.1
            nominal=shapely.affinity.translate(section(mesh,sample)[0],xoff=shift[0],yoff=shift[1])
            neighbour=unary_union([shapely.affinity.translate(section(mesh,sample+d)[0],xoff=shift[0],yoff=shift[1]) for d in [-.0001,0,.0001]])
            cache[key]=(nominal,neighbour)
        nominal,neighbour=cache[key];linegeo=LineString([a[:2],b[:2]])
        outside=linegeo.difference(nominal.buffer(.3)).length
        if outside<=1e-5:continue
        dxy=b[:2]-a[:2];n=max(2,int(math.ceil(np.linalg.norm(dxy)/.05))+1)
        points=shapely.points(a[:2]+np.linspace(0,1,n)[:,None]*dxy)
        events.append({'line':ln,'raw_gcode_line':s,'layer':no,'gcode_z_mm':z,'active_height_mm':height,
                       'active_width_mm':width,'type':kind,'from_xyz_mm':a.tolist(),'to_xyz_mm':b.tolist(),
                       'positive_e_mm':e,'outside_tolerated_section_length_mm':outside,
                       'max_sampled_distance_to_nominal_section_mm':float(shapely.distance(points,nominal).max()),
                       'outside_tolerated_plus_minus_0_0001mm_sections_length_mm':linegeo.difference(neighbour.buffer(.3)).length})
    data={'gcode_sha256':report['gcode_sha256'],'model_sha256':report['model_sha256'],
          'events':events,'purpose':'Keep original 0.30mm comparison exceptions visible; do not erase failures as numerical error without review.'}
    (QA/'slicer-analysis-outliers.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data,indent=2),flush=True)
    return data

def main():
    default_gcode=QA/'slicer/candidate-support-auto.gcode.gz'
    if not default_gcode.exists():default_gcode=default_gcode.with_suffix('')
    ap=argparse.ArgumentParser();ap.add_argument('--gcode',type=Path,default=default_gcode)
    ap.add_argument('--model',type=Path,default=ROOT/'models/v1/model.stl')
    ap.add_argument('--outliers-only',action='store_true')
    args=ap.parse_args()
    if args.outliers_only:inspect_outliers(args.gcode,args.model);return 0
    start=time.time();fixture=parser_fixture()
    p=Parser();layers=[];layer=None;feature='Custom';allstats=defaultdict(lambda:defaultdict(float));line_no=0
    active_height=.2;active_width=.45;footer={}
    positive_stationary_e=0.;negative_e=0.;unlayered_positive_spatial=0;nonplanar=[]
    heights=[]
    with open_gcode(args.gcode) as f:
        for line_no,line in enumerate(f,1):
            s=line.strip()
            if s.startswith('; filament used [mm] ='):footer['filament_used_mm']=float(s.split('=',1)[1])
            elif s.startswith('; estimated printing time (normal mode) ='):footer['estimated_normal_time']=s.split('=',1)[1].strip()
            if s==';LAYER_CHANGE':
                layer={'index':len(layers)+1,'z':None,'initial_height':None,'paths':defaultdict(list),'stats':defaultdict(lambda:defaultdict(float))}
                layers.append(layer)
            elif s.startswith(';Z:') and layer is not None:layer['z']=float(s[3:])
            elif s.startswith(';HEIGHT:') and layer is not None:
                active_height=float(s[8:])
                if layer['initial_height'] is None:layer['initial_height']=active_height
            elif s.startswith(';WIDTH:'):active_width=float(s[7:])
            elif s.startswith(';TYPE:'):feature=s[6:]
            r=p.move(line)
            if r is None:continue
            a,b,de=r;length=float(np.linalg.norm(b-a))
            if de<0:negative_e+=de
            if de<=1e-9:continue
            if length<=1e-8:positive_stationary_e+=de;continue
            if layer is None:unlayered_positive_spatial+=1;continue
            if abs(a[2]-b[2])>1e-5:nonplanar.append({'line':line_no,'a':a.tolist(),'b':b.tolist(),'e':de})
            if feature not in TYPES:TYPES.append(feature)
            row=[a[0],a[1],b[0],b[1],de,length,active_height,active_width]
            layer['paths'][feature].append(row)
            for d in [layer['stats'][feature],allstats[feature]]:
                d['segments']+=1;d['length_mm']+=length;d['positive_e_mm']+=de
    print(f'Parsed {line_no} lines / {len(layers)} layers; comparing sections',flush=True)
    mesh=trimesh.load_mesh(args.model,process=True)
    first=layers[0];first_ext=np.asarray(first['paths']['External perimeter'])
    pts=first_ext[:,:4].reshape(-1,2)
    translation=(pts.min(0)+pts.max(0))/2-(mesh.bounds[0,:2]+mesh.bounds[1,:2])/2
    nominal=np.array([l['z'] for l in layers]);layer_rows=[];sections={};support_records=[]
    support_global={};failure_events=[];support_lines=[]
    # Store both centreline and actual 0.45mm strand-sized digital corridors.
    corridor_radii=[0.,.225,.5]
    slab_cache={}
    for li,l in enumerate(layers):
        ep=l['paths'].get('External perimeter',[])
        hs=[r[6] for a in l['paths'].values() for r in a]
        has_model=any(k not in SUPPORT and k!='Custom' and a for k,a in l['paths'].items())
        reference_height=.2 if has_model else min(hs)
        l['sample_z']=l['z']-reference_height/2
        shape,unclosed=section(mesh,l['sample_z']);sections[li]=shape
        material=shapely.affinity.translate(shape,xoff=float(translation[0]),yoff=float(translation[1])) if not shape.is_empty else shape
        holes=sum(len(q.interiors) for q in polys(shape))
        model_paths=[np.asarray(a) for k,a in l['paths'].items() if k not in SUPPORT and k!='Custom' and a]
        support_paths=[(k,np.asarray(a)) for k,a in l['paths'].items() if k in SUPPORT and a]
        row={'layer':l['index'],'gcode_z_mm':l['z'],'initial_height_comment_mm':l['initial_height'],
             'active_extrusion_heights_mm':sorted(set(hs)),'reference_height_mm':reference_height,'mesh_sample_z_mm':l['sample_z'],
             'mesh_section_area_mm2':float(shape.area),'mesh_section_polygons':len(polys(shape)),
             'mesh_enclosed_void_rings':holes,'mesh_unclosed_curves':unclosed,
             'gcode_model_segments':sum(len(a) for a in model_paths),'gcode_support_segments':sum(len(a) for k,a in support_paths),
             'types':{k:{n:float(v) if n!='segments' else int(v) for n,v in d.items()} for k,d in l['stats'].items()}}
        if model_paths:
            a=np.concatenate(model_paths);coords=a[:,:4].reshape(-1,2,2)
            # Full model extrusion centreline must lie in the matching solid section,
            # allowing 0.30mm for perimeter placement/rounding at sloped surfaces.
            lines=shapely.linestrings(coords)
            lens=shapely.length(shapely.difference(lines,material.buffer(.30)))
            neighbours=unary_union([section(mesh,l['sample_z']+dz)[0] for dz in [-.0001,0,.0001]])
            nm=shapely.affinity.translate(neighbours,xoff=float(translation[0]),yoff=float(translation[1]))
            robust_lens=shapely.length(shapely.difference(lines,nm.buffer(.30)))
            row['model_paths_outside_section_plus_0_30mm_segments']=int(np.count_nonzero(lens>1e-5))
            row['model_paths_outside_section_plus_0_30mm_length_mm']=float(lens.sum())
            row['model_paths_outside_adjacent_sections_plus_0_30mm_segments']=int(np.count_nonzero(robust_lens>1e-5))
            row['model_paths_outside_adjacent_sections_plus_0_30mm_length_mm']=float(robust_lens.sum())
            row['model_extrusion_xy_bounds_mm']=[coords.reshape(-1,2).min(0).tolist(),coords.reshape(-1,2).max(0).tolist()]
            ext=np.asarray(l['paths'].get('External perimeter',[]))
            if len(ext):
                ex=ext[:,:4].reshape(-1,2);bb=np.array([ex.min(0),ex.max(0)])
                row['external_perimeter_bounds_max_delta_mm']=float(np.max(np.abs(bb-np.array(material.bounds).reshape(2,2))))
        else:
            row['model_paths_outside_section_plus_0_30mm_segments']=0
            row['model_paths_outside_section_plus_0_30mm_length_mm']=0.
            row['model_paths_outside_adjacent_sections_plus_0_30mm_segments']=0
            row['model_paths_outside_adjacent_sections_plus_0_30mm_length_mm']=0.
        if support_paths:
            records=[];names=[]
            for k,a in support_paths:
                records.append(a);names.extend([k]*len(a))
            a=np.concatenate(records);coords=a[:,:4].reshape(-1,2,2);lines=shapely.linestrings(coords)
            # Compare against model material across the complete active support
            # HEIGHT slab, not a single optimistic midpoint section.
            obstacles={}
            for h in np.unique(a[:,6]):
                key=(round(l['z']-h,6),round(l['z'],6))
                if key not in slab_cache:slab_cache[key]=slab_projection(mesh,*key)
                obstacles[h]=shapely.affinity.translate(slab_cache[key],xoff=float(translation[0]),yoff=float(translation[1]))
            coll=np.zeros(len(a))
            for h,m in obstacles.items():
                mask=a[:,6]==h;coll[mask]=shapely.length(shapely.intersection(lines[mask],m))
            row['support_centerline_in_model_segments']=int(np.count_nonzero(coll>1e-5))
            row['support_centerline_in_model_length_mm']=float(coll.sum())
            row['support_xy_bounds_mm']=[coords.reshape(-1,2).min(0).tolist(),coords.reshape(-1,2).max(0).tolist()]
            row['support_active_height_range_mm']=[float(a[:,6].min()),float(a[:,6].max())]
            row['support_active_width_range_mm']=[float(a[:,7].min()),float(a[:,7].max())]
            # A full segment is translated horizontally beyond mesh bounds.
            # Its convex swept area, buffered by a chosen strand/probe radius,
            # may not intersect model material at this section. This is an exact
            # 2D continuous segment sweep, not point sampling.
            access={};direction_results={};L=500.
            for radius in corridor_radii:
                open_any=np.zeros(len(a),dtype=bool);dirs={}
                for name,offset in [('left',[-L,0]),('right',[L,0]),('front',[0,-L]),('rear',[0,L])]:
                    off=np.asarray(offset);quads=np.stack([coords[:,0],coords[:,1],coords[:,1]+off,coords[:,0]+off],axis=1)
                    # Degenerate parallel sweeps become lines via convex_hull.
                    swept=shapely.convex_hull(shapely.multipoints(quads))
                    if radius:swept=shapely.buffer(swept,radius,quad_segs=4)
                    # A microscopic inward allowance avoids contact-only false collisions.
                    clear=np.zeros(len(a),dtype=bool)
                    for h,m in obstacles.items():
                        mask=a[:,6]==h
                        interior=m.buffer(-1e-6)
                        clear[mask]=~shapely.intersects(swept[mask],interior)
                    dirs[name]=int(clear.sum());open_any|=clear
                key=f'radius_{radius:.3f}_mm'
                access[key]={'clear_segments':int(open_any.sum()),'blocked_segments':int((~open_any).sum()),'clear_by_direction':dirs}
                direction_results[key]=open_any
            row['support_horizontal_corridors']=access
            for i in range(len(a)):
                support_records.append([l['index'],l['z'],TYPES.index(names[i]),*a[i].tolist(),
                    int(direction_results['radius_0.000_mm'][i]),int(direction_results['radius_0.225_mm'][i]),int(direction_results['radius_0.500_mm'][i])])
            support_lines.append(l['index'])
        layer_rows.append(row)
        if (li+1)%40==0:print(f'Compared {li+1}/{len(layers)} layers',flush=True)
    # Export all support/interface segments and their continuous corridor results.
    support_arr=np.asarray(support_records,dtype=np.float64).reshape(-1,14)
    np.savez_compressed(QA/'slicer-analysis-support-segments.npz',segments=support_arr,
        columns=np.array(['layer','z','type_index','x1','y1','x2','y2','positive_e_mm','length_mm','active_height_mm','active_width_mm','centreline_access','strand_0.45mm_access','probe_1mm_access']),types=np.array(TYPES))
    model_layers=[r['layer'] for r in layer_rows if r['gcode_model_segments']]
    support_layers=[r['layer'] for r in layer_rows if r['gcode_support_segments']]
    nonempty_mesh=[r['layer'] for r in layer_rows if r['mesh_section_area_mm2']>1e-6]
    support_only_layers=[r['layer'] for r in layer_rows if not r['gcode_model_segments'] and r['gcode_support_segments']]
    expected_model_z=np.arange(.2,float(mesh.bounds[1,2])+.0001,.2)
    actual_model_z=np.array([r['gcode_z_mm'] for r in layer_rows if r['gcode_model_segments']])
    missing_model_z=[float(z) for z in expected_model_z if not np.any(np.abs(actual_model_z-z)<1e-4)]
    empty_blocks=[r['layer'] for r in layer_rows if not r['gcode_model_segments'] and not r['gcode_support_segments']]
    unexpected_model_without_mesh=[r['layer'] for r in layer_rows if r['mesh_section_area_mm2']<=1e-6 and r['gcode_model_segments']]
    profile=QA/'slicer/qa-generic-0.4mm-0.2mm-support-auto.ini'
    invocation=json.loads((QA/'slicer/invocation.json').read_text())
    npz=QA/'slicer-analysis-support-segments.npz'
    rawsha,rawsize=raw_gcode_sha(args.gcode)
    summary={'status':'DIGITAL_QA_COMPLETE_PHYSICAL_PRINT_UNVERIFIED','gcode_purpose':'QA only; not machine-ready; never sent to a printer',
      'gcode_sha256':rawsha,'gcode_size_bytes':rawsize,
      'gcode_storage_path':args.gcode.name,'gcode_storage_sha256':sha(args.gcode),'gcode_storage_size_bytes':args.gcode.stat().st_size,
      'model_sha256':sha(args.model),'profile_sha256':sha(profile),
      'slicer_invocation_returncode':invocation['returncode'],'parser_fixture':fixture,'parser_line_count':line_no,
      'input_hashes_match_invocation':{'model':sha(args.model)==invocation['model_sha256'],'profile':sha(profile)==invocation['profile_sha256']},
      'slicer_footer':footer,
      'positive_spatial_e_total_mm':sum(d['positive_e_mm'] for d in allstats.values()),
      'e_total_minus_rounded_slicer_footer_mm':sum(d['positive_e_mm'] for d in allstats.values())-footer.get('filament_used_mm',0),
      'commands':dict(p.count),'unsupported_motion_commands':dict(p.unsupported),'nonplanar_positive_extrusion_moves':nonplanar,
      'positive_stationary_e_mm':positive_stationary_e,'negative_e_mm':negative_e,'positive_spatial_without_layer':unlayered_positive_spatial,
      'positive_spatial_by_type':{k:{n:int(v) if n=='segments' else v for n,v in d.items()} for k,d in allstats.items()},
      'layer_change_block_count':len(layers),'model_extrusion_layer_count':len(model_layers),
      'support_only_layer_count':len(support_only_layers),'support_only_layer_ranges':ranges(support_only_layers),
      'gcode_z_range_mm':[float(nominal.min()),float(nominal.max())],
      'model_height_mm':float(mesh.bounds[1,2]),'expected_layer_count_at_0_2mm':int(round(mesh.bounds[1,2]/.2)),
      'z_monotone':bool(np.all(np.diff(nominal)>0)),
      'active_extrusion_height_range_mm':[min(min(r['active_extrusion_heights_mm']) for r in layer_rows),max(max(r['active_extrusion_heights_mm']) for r in layer_rows)],
      'xy_translation_model_to_gcode_mm':translation.tolist(),'translation_method':'centre of first-layer external perimeter bounds minus centre of STL base bounds',
      'model_extrusion_layer_ranges':ranges(model_layers),'support_extrusion_layer_ranges':ranges(support_layers),
      'missing_expected_model_z_mm':missing_model_z,'empty_layer_change_blocks':empty_blocks,
      'model_layers_without_mesh':unexpected_model_without_mesh,
      'mesh_section_unclosed_curve_total':sum(r['mesh_unclosed_curves'] for r in layer_rows),
      'mesh_enclosed_void_rings_all_layer_sections':sum(r['mesh_enclosed_void_rings'] for r in layer_rows),
      'mesh_watertight':bool(mesh.is_watertight),'mesh_surface_components':len(mesh.split(only_watertight=False)),
      'mesh_euler_number':int(mesh.euler_number),'mesh_winding_consistent':bool(mesh.is_winding_consistent),
      'model_paths_outside_section_plus_0_30mm_segments':sum(r['model_paths_outside_section_plus_0_30mm_segments'] for r in layer_rows),
      'model_paths_outside_section_plus_0_30mm_length_mm':sum(r['model_paths_outside_section_plus_0_30mm_length_mm'] for r in layer_rows),
      'model_paths_outside_adjacent_sections_plus_0_30mm_segments':sum(r['model_paths_outside_adjacent_sections_plus_0_30mm_segments'] for r in layer_rows),
      'model_paths_outside_adjacent_sections_plus_0_30mm_length_mm':sum(r['model_paths_outside_adjacent_sections_plus_0_30mm_length_mm'] for r in layer_rows),
      'model_comparison_method':'Model nominal slice plane is G-code Z minus 0.1mm for this fixed 0.2mm model-layer profile. Bridge HEIGHT 0.4mm describes extrusion cross-section, not a different model slice plane. Strict-plane and union of +/-0.0001mm adjacent sections are both retained.',
      'retained_initial_method_failure':'slicer-analysis-initial-check.py / initial-comparison.json / initial-outliers.json preserve the first method that incorrectly used bridge extrusion HEIGHT to locate the model slicing plane; 13 of its 18 exceptions were due to that method error.',
      'external_perimeter_bounds_max_delta_mm':max(r.get('external_perimeter_bounds_max_delta_mm',0) for r in layer_rows),
      'support_centerline_in_model_segments':sum(r.get('support_centerline_in_model_segments',0) for r in layer_rows),
      'support_centerline_in_model_length_mm':sum(r.get('support_centerline_in_model_length_mm',0) for r in layer_rows),
      'support_horizontal_corridors':{f'radius_{rad:.3f}_mm':{
           'clear_segments':sum(r.get('support_horizontal_corridors',{}).get(f'radius_{rad:.3f}_mm',{}).get('clear_segments',0) for r in layer_rows),
           'blocked_segments':sum(r.get('support_horizontal_corridors',{}).get(f'radius_{rad:.3f}_mm',{}).get('blocked_segments',0) for r in layer_rows)} for rad in corridor_radii},
      'support_segment_archive':{'path':npz.name,'sha256':sha(npz),'count':len(support_arr),'type_table':TYPES},
      'limitations':[
        'No physical print, support removal, machine fit, adhesion, cooling, warping, surface quality or strength test.',
        'Support is present. Do not describe this candidate as support-free.',
        'Continuous horizontal sweeps test every full support centreline against model material projected across that segment actual HEIGHT slab, using clipped mesh boundary triangles plus end sections. They ignore other support strands and tool/hand geometry.',
        '0.45mm strand and 1.0mm probe corridor checks are bounded digital clearance checks; they do not prove a branched 3D support mass can be extracted intact.',
        'The single watertight connected oriented STL boundary and absence of section holes support no sealed internal support cavity; infill voids created by slicing are intentional.',
        'A 0.30mm tolerance for model centreline/section comparison covers extrusion width and small slicing approximations; this is not a dimensional calibration.',
        'Generic 0.4mm-nozzle, 0.2mm-layer profile and G-code are QA evidence only, not approved for any actual printer.'
      ],'elapsed_seconds':time.time()-start}
    # Keep failures visible and machine-readable; do not suppress unexpected geometry.
    if p.unsupported:failure_events.append('Unsupported motion commands prevent complete spatial interpretation')
    if nonplanar:failure_events.append('Positive nonplanar extrusion is not covered by planar section tests')
    if missing_model_z or empty_blocks or unexpected_model_without_mesh:failure_events.append('Model/mesh empty-layer mismatch')
    if summary['model_paths_outside_section_plus_0_30mm_segments']:failure_events.append('Strict-plane centreline/section differences retained; consult exact outlier lines and adjacent-section comparison')
    if summary['model_paths_outside_adjacent_sections_plus_0_30mm_segments']:failure_events.append('Some model extrusion centrelines leave tolerated adjacent mesh sections')
    if summary['support_centerline_in_model_segments']:failure_events.append('Some support centreline length intersects model section')
    if summary['support_horizontal_corridors']['radius_0.000_mm']['blocked_segments']:failure_events.append('Some support centrelines have no clear cardinal horizontal corridor')
    summary['observed_failures_or_limits_requiring_review']=failure_events
    (QA/'slicer-analysis-layers.json').write_text(json.dumps({'layers':layer_rows},indent=2)+'\n',encoding='utf8')
    # Representative support layers across height plus maximum support count.
    selected=set()
    if support_layers:
        for q in [0,.2,.4,.6,.8,1]:selected.add(support_layers[int(round(q*(len(support_layers)-1)))])
        selected.add(max(layer_rows,key=lambda r:r['gcode_support_segments'])['layer'])
    selected.add(next((r['layer'] for r in layer_rows if 'Bridge infill' in r['types']),1))
    plots=[]
    for no in sorted(selected):
        name=f'slicer-analysis-layer-{no:03d}.png';plot_layer(layers[no-1],sections[no-1],translation,QA/name);plots.append(name)
    summary['layer_plots']=plots
    fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    axes[0].plot(nominal,[r['mesh_section_area_mm2'] for r in layer_rows],label='mesh solid cross-section area (mm2)',color='#444444')
    axes[0].set_ylabel('Mesh area (mm2)');ax2=axes[0].twinx();ax2.plot(nominal,[r['gcode_model_segments'] for r in layer_rows],label='model extrusion segments',color='#235ab6',lw=.8);ax2.set_ylabel('Model segments',color='#235ab6')
    for kind,col in [('Support material','#ed8b23'),('Support material interface','#d12893'),('Bridge infill','#6b41bc'),('Overhang perimeter','#09a5bf')]:
        axes[1].plot(nominal,[r['types'].get(kind,{}).get('positive_e_mm',0) for r in layer_rows],label=kind,color=col)
    axes[1].set_xlabel('G-code layer Z (mm)');axes[1].set_ylabel('Positive spatial E (filament mm)');axes[1].legend(fontsize=8)
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('All actual G-code layers compared with STL sections');fig.tight_layout();fig.savefig(QA/'slicer-analysis-all-layers.png',dpi=160);plt.close(fig)
    summary['elapsed_seconds']=time.time()-start
    (QA/'slicer-analysis.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    inspect_outliers(args.gcode,args.model)
    print(json.dumps(summary,indent=2),flush=True)
    return 0

if __name__=='__main__':sys.exit(main())
