"""Independent CSU raw-STL probes and actual G-code manufacture audit."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import gzip,hashlib,json,math,re
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely.affinity import translate
import manifold3d as md

OUT=Path(__file__).resolve().parent
PKG=Path(r'<MODEL_ROOT>')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
def readstl(path):return np.frombuffer(path.read_bytes(),offset=84,dtype=dtype)['v'].astype(float)
BODY=PKG/'models/v2/parts/body.stl';ROOF=PKG/'models/v2/parts/roof.stl'
body=readstl(BODY);roof=readstl(ROOF)
def make_solid(tri):
 v,idx=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True)
 s=md.Manifold(md.Mesh64(v,idx.reshape(-1,3).astype(np.uint64)))
 assert s.status()==md.Error.NoError
 return s
solid=make_solid(body)
def contour(s,z):
 pos=[];neg=[]
 for c in s.slice(z).to_polygons():
    p=Polygon(c)
    (pos if p.exterior.is_ccw else neg).append(p)
 return unary_union(pos).difference(unary_union(neg))
def hits(tri,p,d):
 p=np.asarray(p);d=np.asarray(d);a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a
 h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
 ok=np.abs(det)>1e-12;inv=np.zeros(len(det));inv[ok]=1/det[ok]
 q0=p-a;u=np.einsum('ij,ij->i',q0,h)*inv;q=np.cross(q0,e1);v=np.einsum('j,ij->i',d,q)*inv
 t=np.einsum('ij,ij->i',e2,q)*inv;ok&=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
 values=[]
 for x in sorted(t[ok]):
    if not values or abs(x-values[-1])>1e-6:values.append(float(x))
 return values
probes={}
for name,p,d in [('door_mid',[0,0,15],[0,1,0]),('porch_above_door',[0,0,21],[0,1,0]),
 ('wing_front_window',[-76,0,10.5],[0,1,0]),('wing_above_window',[-76,0,12.1],[0,1,0]),
 ('end_recess',[0,1,14],[1,0,0]),('end_above_recess',[0,1,17.2],[1,0,0])]:
 vals=hits(body,p,d);probes[name]={'point_mm':p,'direction':d,'full_line_surface_parameters_mm':vals}
door_depth=probes['door_mid']['full_line_surface_parameters_mm'][0]-probes['porch_above_door']['full_line_surface_parameters_mm'][0]

# Preserve all original short sample coordinates; use raw triangles directly.
flags=json.load(gzip.open(PKG/'qa/v1/roof/manufacturing/normal-chord-short.json.gz','rt'))
roofrows=[]
normals=np.cross(roof[:,1]-roof[:,0],roof[:,2]-roof[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
halfspace=float(max(np.max((roof.reshape(-1,3)-t[0])@n) for t,n in zip(roof,normals)))
for r in flags:
 p=np.array(r['surface_point_mm']);d=-np.array(r['original_outward_unit_normal'])
 positive=[t for t in hits(roof,p,d) if t>1e-8];t=min(positive)
 end=p+d*t
 roofrows.append({'original_face':r['original_face_index'],'sample_index':r['sample_index'],'original_point_mm':p.tolist(),
 'independent_first_exit_mm':t,'original_chord_mm':r['first_solid_chord_mm'],'exit_mm':end.tolist(),
 'difference_mm':t-r['first_solid_chord_mm']})

# Fixed original Y section through all six body ambiguity points.
amb=json.load(gzip.open(PKG/'qa/v2/body/manufacturing/normal-chord-flags.json.gz','rt'))
rot=body[:,:,[0,2,1]].copy();rot[:,:,2]*=-1 # right-handed X,Z,-Y
xzsolid=make_solid(rot);bodysections=[]
for y in sorted({r['surface_point_mm'][1] for r in amb}):
 region=contour(xzsolid,-y)
 boundary=region.boundary.intersection(LineString([(-100,68),(100,68)]))
 bodysections.append({'fixed_original_y_mm':y,'section_wkt_XZ':region.wkt,'original_z68_boundary_intersection_wkt':boundary.wkt,'valid':region.is_valid})

# Exact original-ray coplanar clipping using raw STL vertices. No shifted rays.
def exact_clip(p,d,t):
 p=[F(float(x)) for x in p];d=[F(float(x)) for x in d];t=[[F(float(x)) for x in row] for row in t]
 sub=lambda a,b:[x-y for x,y in zip(a,b)]
 cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
 dot=lambda a,b:sum(x*y for x,y in zip(a,b))
 e1=sub(t[1],t[0]);e2=sub(t[2],t[0]);n=cross(e1,e2)
 if dot(n,d)!=0 or dot(n,sub(p,t[0]))!=0:return None
 drop=max(range(3),key=lambda i:abs(n[i]));ids=[i for i in range(3) if i!=drop]
 def det(a,b):return a[ids[0]]*b[ids[1]]-a[ids[1]]*b[ids[0]]
 den=det(e1,e2);q=sub(p,t[0]);u0=det(q,e2)/den;ud=det(d,e2)/den;v0=det(e1,q)/den;vd=det(e1,d)/den
 lo=F(0);hi=None
 for a,b in [(u0,ud),(v0,vd),(1-u0-v0,-ud-vd)]:
    if b==0:
        if a<0:return None
    elif b>0:lo=max(lo,-a/b)
    else:hi=-a/b if hi is None else min(hi,-a/b)
 if hi is None or hi<=lo:return None
 return [str(lo),str(hi)]
coplanar=[]
for r in amb:
 p=r['surface_point_mm'];d=-np.array(r['original_outward_unit_normal']);found=[]
 for i,t in enumerate(body):
    interval=exact_clip(p,d,t)
    if interval:found.append({'raw_face':i,'exact_t_interval_mm':interval})
 coplanar.append({'source_face':r['original_face_index'],'sample':r['sample_index'],'original_point_mm':p,'exact_coplanar_intervals':found})

# Independent fixed-artifact parser: accepts/reports actual absolute-mm modes;
# maintains retraction debt, carries every WIDTH/HEIGHT and ignores travel/reprime.
word=re.compile(r'([XYZEF])([-+\d.eE]+)')
def parse(path):
 pos={k:0. for k in 'XYZE'};debt=0.;role='unknown';w=h=None;roles=Counter();esums=Counter();segs=[];commands=Counter();special=[]
 with path.open(encoding='utf8') as stream:
  for lineno,raw in enumerate(stream,1):
    command,_,comment=raw.partition(';');comment=comment.strip();command=command.strip()
    if comment.startswith('TYPE:'):role=comment[5:]
    if comment.startswith('WIDTH:'):w=float(comment[6:])
    if comment.startswith('HEIGHT:'):h=float(comment[7:])
    if not command:continue
    op=command.split()[0];commands[op]+=1
    assert op not in ['G91','M83','G20','G2','G3']
    f={k:float(v) for k,v in word.findall(command)}
    if op=='G92':
        assert not any(k in f for k in 'XYZ')
        if 'E' in f:pos['E']=f['E']
    elif op=='G28':
        for k in 'XYZ':pos[k]=0.
    elif op in ['G0','G1']:
        old=pos.copy()
        for k in 'XYZE':
            if k in f:pos[k]=f[k]
        de=pos['E']-old['E']
        if de<0:debt-=de;net=0.
        elif de>0:net=max(0.,de-debt);debt=max(0.,debt-de)
        else:net=0.
        if net>1e-9 and math.hypot(pos['X']-old['X'],pos['Y']-old['Y'])>1e-9:
            roles[role]+=1;esums[role]+=net
            if role in ['Support material','Support material interface','Bridge infill','Overhang perimeter']:
                v={'line':lineno,'role':role,'a':[old['X']-110,old['Y']-110],'b':[pos['X']-110,pos['Y']-110],
                   'z':pos['Z'],'z0':old['Z'],'w':w,'h':h,'E':net}
                segs.append(v)
 return {'path':str(path),'sha256':sha(path),'roles':dict(roles),'filament_by_role_mm':dict(esums),'actual_mode_commands':{k:v for k,v in commands.items() if k in ['G90','G21','M82']}},segs
parsed={};support=[]
for name,path in [('body_auto45',PKG/'qa/v2/slicing/body-auto45/QA-NOT-MACHINE-READY.gcode'),
 ('body_no_support',PKG/'qa/v2/slicing/body/QA-NOT-MACHINE-READY.gcode'),('roof_no_support',PKG/'qa/v1/slicing/roof/QA-NOT-MACHINE-READY.gcode')]:
 summary,ss=parse(path);parsed[name]=summary
 if name=='body_auto45':support=[v for v in ss if v['role'] in ['Support material','Support material interface']]
 summary['special_role_segments']=[v for v in ss if v['role'] not in ['Support material','Support material interface']]

# Actual deposited-width intersections in representative shallow recesses.
def capsule(s):return LineString([s['a'],s['b']]).buffer(s['w']/2)
def subset(bb):
 lo,hi=bb;rect=box(*lo[:2],*hi[:2]);rows=[]
 for v in support:
    if v['z']>=hi[2]-1e-10 or v['z']-v['h']<=lo[2]+1e-10:continue
    a,b=v['a'],v['b'];r=v['w']/2
    if max(a[0],b[0])+r<=lo[0] or min(a[0],b[0])-r>=hi[0] or max(a[1],b[1])+r<=lo[1] or min(a[1],b[1])-r>=hi[1]:continue
    if LineString([a,b]).distance(rect)<r-1e-10:rows.append(v)
 return rows
regions=[('entrance_door',[[-8.5,-29.20001,7],[8.5,-28.55,20]],(0,-8)),
 ('left_wing_front_pane',[[-77.81,-11.00001,9.4],[-74.19,-10.59999,11.8]],(0,-8)),
 ('left_wing_rear_pane',[[-77.81,15.59999,9.4],[-74.19,16.00001,11.8]],(0,8)),
 ('center_front_pane',[[-21.21,-18.00001,37],[-16.79,-17.59999,40.8]],(0,-8)),
 ('center_rear_pane',[[-20.71,17.59999,10],[-15.29,18.00001,13.3]],(0,8)),
 ('left_end_recess',[[-92.00001,-9,12],[-91.59999,11,17]],(-8,0)),
 ('right_end_recess',[[91.59999,-9,12],[92.00001,11,17]],(8,0)),
 ('clerestory_front',[[-2.71,-14.00001,80],[2.71,-13.59999,83]],(0,-8))]
sectioncache={}
def at(z):
 key=round(z,8)
 if key not in sectioncache:sectioncache[key]=contour(solid,z)
 return sectioncache[key]
routes=[]
for name,bb,shift in regions:
 found=subset(bb);rect=box(*bb[0][:2],*bb[1][:2]);layers=[]
 zs=sorted({s['z'] for s in found})
 # Necessary finite spot checks: lowest, middle and highest actual stratum.
 selected=sorted({zs[0],zs[len(zs)//2],zs[-1]}) if zs else []
 for z in selected:
    group=[s for s in found if s['z']==z];pieces=[capsule(s).intersection(rect) for s in group];pieces=[p for p in pieces if not p.is_empty]
    sweep=unary_union([unary_union([p,translate(p,xoff=shift[0],yoff=shift[1])]).convex_hull for p in pieces])
    lo=max(bb[0][2],z-max(s['h'] for s in group));hi=min(bb[1][2],z)
    ztest=[lo+1e-5,(lo+hi)/2,hi-1e-5]
    layers.append({'z_top':z,'z_samples':ztest,'obstruction_area_mm2':[sweep.intersection(at(zz)).area for zz in ztest],
        'actual_patch_bounds':list(unary_union(pieces).bounds),'original_lines':[s['line'] for s in group]})
 routes.append({'region':name,'bbox':bb,'direction_mm':shift,'actual_capsule_overlapping_segments':len(found),'actual_strata':len(zs),
   'checked_strata':layers,'limitation':'Clipped, separated local material portions only; tool, fragmentation, force and all other support portions unproven.'})

report={'fixed_candidate_from_parent':'76681c5dcedc88d684946780e795d7914a88c075','script_sha256':sha(Path(__file__)),
 'body_sha256':sha(BODY),'roof_sha256':sha(ROOF),'body_raw_probes':probes,'actual_entrance_door_recess_depth_mm':door_depth,
 'roof_original_short_sample_count':len(roofrows),'roof_original_short_samples':roofrows,
 'roof_max_original_chord_difference_mm':max(abs(r['difference_mm']) for r in roofrows),
 'roof_max_vertex_outside_outward_halfspaces_mm':halfspace,
 'roof_downward_face_normals_above_base_count':int(sum(n[2]<-1e-8 and t[:,2].max()>1e-8 for t,n in zip(roof,normals))),
 'body_original_ambiguity_fixed_sections':bodysections,'body_original_ambiguity_exact_coplanar_intervals':coplanar,
 'actual_gcode':parsed,'actual_support_segment_count':len(support),'actual_support_filament_mm':sum(s['E'] for s in support),
 'support_widths_mm':sorted({s['w'] for s in support}),'support_heights_mm':sorted({s['h'] for s in support}),
 'selected_finite_support_outward_routes':routes,
 'all_support_removal_or_tool_force_proven':False,'no_second_slice_or_geometry_change':True,
 'read_only_hash_after':{'body':sha(BODY),'roof':sha(ROOF)}}
(OUT/'independent-csu-manufacturing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'body':sha(BODY),'roof':sha(ROOF),'door_depth':door_depth,'roofflags':len(roofrows),'roof_chord_max_difference':report['roof_max_original_chord_difference_mm'],
 'modes_and_roles':{k:{'roles':v['roles'],'modes':v['actual_mode_commands']} for k,v in parsed.items()},'support_segments':len(support),'support_E':report['actual_support_filament_mm'],
 'regions':[{'name':r['region'],'segments':r['actual_capsule_overlapping_segments'],'strata':r['actual_strata'],
 'max_sample_obstruction':max((max(q['obstruction_area_mm2']) for q in r['checked_strata']),default=None)} for r in routes]},indent=2))
