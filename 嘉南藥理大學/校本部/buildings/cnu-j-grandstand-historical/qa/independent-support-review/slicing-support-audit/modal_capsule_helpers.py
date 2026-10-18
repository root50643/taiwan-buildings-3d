from pathlib import Path
from collections import Counter, defaultdict
import math,re,hashlib
WORDS = re.compile(r"([A-Za-z])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))")

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_gcode(p):
    txt = p.read_text(encoding='utf-8-sig')
    xyz = [0., 0., 0.]; e = 0.; absxyz = True; abse = True
    unit = 1.; typ = 'Unclassified'; width = .45; height = .15; tool = 0
    segs = []; types_seen = Counter(); commands = Counter(); tools = set()
    e_only_pos = 0.; unsupported = []; resets = 0; motion_z = []; layer_comments=[]
    config = {}; in_config = False; layer=-1
    for ln, raw in enumerate(txt.splitlines(), 1):
        if raw.startswith('; prusaslicer_config = begin'): in_config=True; continue
        if raw.startswith('; prusaslicer_config = end'): in_config=False; continue
        if in_config:
            m = re.match(r'; ([^=]+?) = (.*)$', raw)
            if m: config[m[1]] = m[2]
            continue
        if raw.startswith(';TYPE:'):
            typ=raw[6:].strip(); types_seen[typ]+=1
        if raw.startswith(';WIDTH:'): width=float(raw[7:])
        if raw.startswith(';HEIGHT:'): height=float(raw[8:])
        if raw.startswith(';LAYER_CHANGE'): layer+=1
        if raw.startswith(';Z:'): layer_comments.append(float(raw[3:]))
        code = raw.split(';',1)[0].strip()
        if not code: continue
        ws=WORDS.findall(code)
        if not ws: continue
        cmd=ws[0][0].upper()+ws[0][1]
        vals={k.upper():float(v) for k,v in ws[1:]}
        commands[cmd]+=1
        if cmd=='G20': unit=25.4
        elif cmd=='G21': unit=1.
        elif cmd=='G90': absxyz=True
        elif cmd=='G91': absxyz=False
        elif cmd=='M82': abse=True
        elif cmd=='M83': abse=False
        elif cmd=='G92':
            resets+=1
            for i,k in enumerate('XYZ'):
                if k in vals: xyz[i]=vals[k]*unit
            if 'E' in vals: e=vals['E']*unit
        elif cmd=='G28':
            axes=[k for k in 'XYZ' if k in vals] or list('XYZ')
            for k in axes: xyz['XYZ'.index(k)]=0.
        elif cmd in ('G0','G1'):
            old=xyz.copy(); olde=e
            for i,k in enumerate('XYZ'):
                if k in vals: xyz[i]=(vals[k]*unit if absxyz else xyz[i]+vals[k]*unit)
            if 'E' in vals: e=(vals['E']*unit if abse else e+vals['E']*unit)
            de=e-olde; motion_z.append(xyz[2])
            length=math.dist(old[:2],xyz[:2])
            if de>1e-9 and length>1e-9:
                segs.append(dict(line=ln,a=old,b=xyz.copy(),de=de,length=length,
                                 type=typ,width=width,height=height,tool=tool,layer=layer))
            elif de>1e-9: e_only_pos+=de
        elif cmd in ('G2','G3'): unsupported.append(dict(line=ln,code=code))
        elif cmd.startswith('T'):
            tool=int(float(cmd[1:])); tools.add(tool)
    bytype=defaultdict(lambda:dict(segments=0,positive_filament_mm=0.,xy_length_mm=0.))
    byz=defaultdict(list)
    for s in segs:
        t=bytype[s['type']]; t['segments']+=1; t['positive_filament_mm']+=s['de'];t['xy_length_mm']+=s['length']
        byz[round(s['b'][2],6)].append(s)
    bounds=[[min(s[k][i] for s in segs for k in ('a','b')) for i in range(3)],
            [max(s[k][i] for s in segs for k in ('a','b')) for i in range(3)]]
    return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,config=config,
                commands=dict(commands),type_comments=dict(types_seen),extrusion_by_type=dict(bytype),
                positive_xy_segments=len(segs),positive_xy_filament_mm=sum(s['de'] for s in segs),
                excluded_positive_e_only_mm=e_only_pos,g92_count=resets,selected_tools=sorted(tools),
                unsupported_motion_commands=unsupported,extrusion_centerline_bounds_mm=bounds,
                extruding_layers_z_mm=sorted(byz),extruding_layer_count=len(byz),
                layer_comment_z_mm=layer_comments,max_motion_z_mm=max(motion_z),
                _segments=segs,_byz=byz)

def intersect_linear(lo,hi,c,d,mn,mx):
    if abs(d)<1e-14: return (lo,hi) if mn-1e-12<=c<=mx+1e-12 else None
    a,b=(mn-c)/d,(mx-c)/d
    if a>b: a,b=b,a
    lo=max(lo,a);hi=min(hi,b)
    return (lo,hi) if hi>=lo else None

def capsule_intervals(a,b,c,d,r):
    # Exact intersections of query line a+t(b-a), 0<=t<=1, with a support
    # segment's round-ended swept disk: rectangle + two analytic circles.
    q=(b[0]-a[0],b[1]-a[1]); v=(d[0]-c[0],d[1]-c[1])
    vv=v[0]*v[0]+v[1]*v[1]; qq=q[0]*q[0]+q[1]*q[1]; ans=[]
    if vv>1e-20:
        l=math.sqrt(vv); ac=(a[0]-c[0],a[1]-c[1])
        u=(ac[0]*v[0]+ac[1]*v[1])/vv;du=(q[0]*v[0]+q[1]*v[1])/vv
        n=(v[0]*ac[1]-v[1]*ac[0])/l;dn=(v[0]*q[1]-v[1]*q[0])/l
        z=intersect_linear(0.,1.,u,du,0.,1.)
        if z: z=intersect_linear(*z,n,dn,-r,r)
        if z: ans.append(z)
    for o in (c,d):
        v0=(a[0]-o[0],a[1]-o[1]);bb=2*(q[0]*v0[0]+q[1]*v0[1]);cc=v0[0]**2+v0[1]**2-r*r
        disc=bb*bb-4*qq*cc
        if disc>=-1e-9 and qq>1e-20:
            rt=math.sqrt(max(0.,disc));lo=max(0.,(-bb-rt)/(2*qq));hi=min(1.,(-bb+rt)/(2*qq))
            if hi>=lo: ans.append((lo,hi))
    return ans

def coverage(s,prev,nominal):
    iv=[]; a,b=s['a'],s['b']
    for p in prev:
        r=(.45 if nominal else p['width'])/2
        # Fast but exact bounding-box rejection.
        if max(a[0],b[0])+r<min(p['a'][0],p['b'][0]) or min(a[0],b[0])-r>max(p['a'][0],p['b'][0]) or max(a[1],b[1])+r<min(p['a'][1],p['b'][1]) or min(a[1],b[1])-r>max(p['a'][1],p['b'][1]): continue
        iv.extend(capsule_intervals(a,b,p['a'],p['b'],r))
    merged=[]
    for lo,hi in sorted(iv):
        if merged and lo<=merged[-1][1]+1e-11: merged[-1][1]=max(hi,merged[-1][1])
        else: merged.append([lo,hi])
    gaps=[];cur=0.
    for lo,hi in merged:
        if lo>cur+1e-10: gaps.append((cur,lo))
        cur=max(cur,hi)
    if cur<1-1e-10:gaps.append((cur,1.))
    return [dict(length_mm=(hi-lo)*s['length'],t=[lo,hi],xy=[[a[i]+t*(b[i]-a[i]) for i in (0,1)] for t in (lo,hi)]) for lo,hi in gaps]
