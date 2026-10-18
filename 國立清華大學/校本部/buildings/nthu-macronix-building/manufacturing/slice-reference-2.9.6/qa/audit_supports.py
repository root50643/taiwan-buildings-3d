"""Audit one existing PrusaSlicer G-code; never invoke a slicer or alter STL.

Coordinates in exported segments are physical G-code XYZ minus (110,110,0).
Extrusion requires positive E after repayment of outstanding retraction and a
nonzero XY move. Deposited z interval is [Z-HEIGHT,Z]. Region tests include an
XY-width capsule and positive vertical overlap, not only endpoint containment.
"""
from __future__ import annotations
import collections, csv, gzip, hashlib, json, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
WORK = ROOT / 'slicing-work'
GCODE = WORK / 'reference-NOT-MACHINE-READY.gcode'
EXPECTED = '7f614cbe4a31e59cfed5e843f90b797f1032984c173da044284fc36ab18219de'
REGIONS = ROOT / 'candidate-repo/國立清華大學/校本部/buildings/nthu-macronix-building/manufacturing/regions.json'
NUM = re.compile(r'([A-Za-z])([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def parse(lines):
    logical = {k: 0.0 for k in 'XYZE'}
    offsets = {k: 0.0 for k in 'XYZ'}
    xyz_absolute = e_absolute = True
    units = 1.0
    debt = 0.0
    role, width, height, layer = 'unknown', None, None, -1
    commands = collections.Counter()
    roles = collections.Counter()
    modes = collections.Counter()
    ignored_positive = collections.Counter()
    segments = []
    for n, line in enumerate(lines, 1):
        body, _, comment = line.partition(';')
        comment = comment.strip()
        if comment == 'LAYER_CHANGE': layer += 1
        if comment.startswith('TYPE:'): role = comment[5:].strip()
        if comment.startswith('WIDTH:'): width = float(comment[6:])
        if comment.startswith('HEIGHT:'): height = float(comment[7:])
        words = NUM.findall(body.strip())
        if not words: continue
        cmd = words[0][0].upper() + str(int(float(words[0][1])))
        params = {k.upper(): float(v) for k,v in words[1:]}
        commands[cmd] += 1
        if cmd == 'G20': units = 25.4
        elif cmd == 'G21': units = 1.0
        elif cmd in ('G90','G91'):
            xyz_absolute = e_absolute = cmd == 'G90'
            modes[cmd] += 1
        elif cmd in ('M82','M83'):
            e_absolute = cmd == 'M82'
            modes[cmd] += 1
        elif cmd == 'G92':
            for k, v in params.items():
                if k in offsets: offsets[k] += logical[k] - v * units
                if k in logical: logical[k] = v * units
            modes['G92'] += 1
        elif cmd == 'G28':
            # G28 only occurs before audited print coordinates in this artifact.
            for k in 'XYZ': logical[k], offsets[k] = 0.0, 0.0
        elif cmd in ('G0','G1'):
            before = [logical[k]+offsets[k] for k in 'XYZ']
            old_e = logical['E']
            for k,v in params.items():
                if k in logical:
                    absolute = e_absolute if k == 'E' else xyz_absolute
                    logical[k] = v*units if absolute else logical[k]+v*units
            after = [logical[k]+offsets[k] for k in 'XYZ']
            de = logical['E']-old_e
            if de < 0: debt += -de
            actual_e = max(0.0, de-debt) if de>0 else 0.0
            if de>0: debt = max(0.0,debt-de)
            xy = math.dist(before[:2],after[:2])
            if actual_e>1e-9 and xy>1e-9:
                if width is None or height is None:
                    raise ValueError(f'Missing WIDTH/HEIGHT at extrusion line {n}')
                seg = dict(line=n, layer=layer, role=role, width=width, height=height,
                    p0=[before[0]-110,before[1]-110,before[2]],
                    p1=[after[0]-110,after[1]-110,after[2]],
                    length=math.dist(before,after), e=actual_e)
                segments.append(seg); roles[role]+=1
            elif de>0: ignored_positive['stationary_or_retraction_repayment'] += 1
        elif cmd in ('G2','G3'):
            raise ValueError('Arc encountered; this parser deliberately rejects unsupported arcs')
    return segments,dict(commands=commands,roles=roles,modes=modes,
                         ignored_positive=ignored_positive,final_retraction_debt=debt)

def selftest():
    lines = ['G21','G90','M82','G92 E0',';HEIGHT:0.2',';WIDTH:0.45',
      ';TYPE:Support material','G1 X110 Y110 Z1','G1 E-1','G92 E0','G1 E1',
      'G1 X111 E2','G91','M83','G1 X1 E0.5','G92 X0 E0','G90','M82',
      'G1 X1 E0.5','M83','G1 X2 E-0.5','G1 X3 E0.5','G1 X4 E0.2']
    s,m = parse(lines)
    assert len(s)==4, s
    assert [round(t['p1'][0],6) for t in s]==[1,2,3,6], s
    assert [round(t['e'],6) for t in s]==[1,.5,.5,.2], s
    return dict(passed=True,cases=['absolute XYZ/E','relative XYZ/E','G92 XYZ physical offset',
         'G92 E origin','retraction debt','stationary unretract not extrusion',
         'XY motion without net material not extrusion','TYPE WIDTH HEIGHT comments'])

def clip_interval(a,b,lo,hi):
    t0,t1=0.,1.
    for i in range(len(a)):
        d=b[i]-a[i]
        if abs(d)<1e-12:
            if a[i]<lo[i] or a[i]>hi[i]: return None
        else:
            u,v=(lo[i]-a[i])/d,(hi[i]-a[i])/d
            t0,t1=max(t0,min(u,v)),min(t1,max(u,v))
            if t1<t0: return None
    return t0,t1

def stats(segs):
    if not segs: return dict(segments=0,length_mm=0,roles={},z_top_layers=[],bbox_centerline=None)
    pts=[p for s in segs for p in (s['p0'],s['p1'])]
    return dict(segments=len(segs),length_mm=sum(s['length'] for s in segs),
      roles=dict(collections.Counter(s['role'] for s in segs)),
      z_top_layers=sorted(set(s['p1'][2] for s in segs)),
      bbox_centerline=[[min(p[i] for p in pts) for i in range(3)],
                       [max(p[i] for p in pts) for i in range(3)]],
      line_range=[min(s['line'] for s in segs),max(s['line'] for s in segs)],
      extrusion_widths_mm=sorted(set(s['width'] for s in segs)),
      extrusion_heights_mm=sorted(set(s['height'] for s in segs)))

def in_box(s, bbox, local=None):
    from shapely.geometry import LineString, box
    a,b = s['p0'],s['p1']
    if local:
        angle=math.radians(-local['rotation_z_deg']); ca,sa=math.cos(angle),math.sin(angle)
        x0,y0,_=local['translation']
        def inv(p):
            x,y=p[0]-x0,p[1]-y0
            return [ca*x-sa*y,sa*x+ca*y,p[2]]
        a,b=inv(a),inv(b)
    low,high=bbox
    # Nonzero deposition volume must overlap the finite z region.
    if min(a[2],b[2])>=high[2]-1e-10 or max(a[2],b[2])-s['height']<=low[2]+1e-10:
        return False
    radius=s['width']/2
    # Fast rejection then precise 2D capsule vs rectangle; round cap convention.
    if not clip_interval(a[:2],b[:2], [low[i]-radius for i in range(2)],
                         [high[i]+radius for i in range(2)]): return False
    return LineString([a[:2],b[:2]]).distance(box(*low[:2],*high[:2]))<radius-1e-10

def main():
    assert sha(GCODE)==EXPECTED
    tests=selftest()
    segs,parser = parse(GCODE.read_text(encoding='utf-8').splitlines())
    supports=[s for s in segs if s['role'] in ('Support material','Support material interface')]
    with gzip.open(OUT/'positive-extrusion-segments.jsonl.gz','wt',encoding='utf-8') as f:
        for s in segs: f.write(json.dumps(s,separators=(',',':'))+'\n')
    with gzip.open(OUT/'support-segments.csv.gz','wt',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['line','layer','role','width_mm','height_mm',
          'x0_model','y0_model','z0_top','x1_model','y1_model','z1_top','length_mm','positive_E_mm'])
        for s in supports: w.writerow([s['line'],s['layer'],s['role'],s['width'],s['height'],
          *s['p0'],*s['p1'],s['length'],s['e']])
    regions=json.loads(REGIONS.read_text(encoding='utf-8'))
    reports={}
    for r in regions['regions']:
        if r['id']=='F':
            sub=[]
            f=r['local_bbox_per_level']
            for wing in regions['local_wings']:
                for z0,z1 in f['z_ranges']:
                    bbox=[[f['x_range'][0],f['y_range'][0],z0],
                          [f['x_range'][1],f['y_range'][1],z1]]
                    hit=[s for s in supports if in_box(s,bbox,wing)]
                    sub.append(dict(wing=wing['name'],z_range=[z0,z1],bbox_local=bbox,**stats(hit)))
            reports['F']=dict(method='width capsules in both rotated local-wing finite microgap volumes',
                              per_gap=sub,segments=sum(x['segments'] for x in sub))
            continue
        bbox=r['view_bbox']
        hit=[s for s in supports if in_box(s,bbox)]
        reports[r['id']]=dict(bbox=bbox,**stats(hit))
        for sub in r.get('subregions',[]):
            lo,hi=sub['downface_bbox']
            bbox=[list(lo),list(hi)];bbox[0][2]=3.0;bbox[1][2]=hi[2]
            hit=[s for s in supports if in_box(s,bbox)]
            reports[sub['id']]=dict(method='under-face projected column down to model-base top',
                                    bbox=bbox,**stats(hit))
    # Fills hidden fin-back slots: support must not be deposited in this solid volume.
    c=next(r for r in regions['regions'] if r['id']=='C')
    fin_results=[]
    for xr in c['original_back_slots']['x_ranges']:
        for zr in c['window_z_ranges']:
            bbox=[[xr[0],-20.9,zr[0]],[xr[1],-19.1,zr[1]]]
            hit=[s for s in supports if in_box(s,bbox)]
            fin_results.append(dict(bbox=bbox,**stats(hit)))
    # The actual open bay prisms, not the entire C façade inspection bbox.
    bay_results=[]
    for xr in [[37.5,42.5],[43.5,48.5],[49.5,54.5],[55.5,60.0]]:
        for zr in c['window_z_ranges']:
            bbox=[[xr[0],-22.5,zr[0]],[xr[1],-19.1,zr[1]]]
            hit=[s for s in supports if in_box(s,bbox)]
            bay_results.append(dict(bbox=bbox,**stats(hit)))
    report=dict(schema='actual-one-slice-support-audit-v1',gcode=GCODE.name,
      gcode_sha256=EXPECTED,input_stl_sha256=sha(WORK/'input-model.stl'),
      parser_selftest=tests,parser=parser,
      transform=dict(model_from_print='(X-110,Y-110,Z)',translation_only=True),
      role_stats={role:stats([s for s in segs if s['role']==role]) for role in parser['roles']},
      supports=stats(supports),regions=reports,filled_C_back_slots=fin_results,C_open_bays=bay_results,
      interpretation=['Region lists are not disjoint. A-E are inspection envelopes; counts are capsule overlaps, not trapped-support counts.',
        'C0 and D0 are under-face projected columns from Z=3, to avoid counting only the support-free contact gap at the target plane.',
        'A path centerline plus nominal WIDTH/HEIGHT is a deposited-path approximation, not measured physical filament.',
        'No second slicing run, geometry change, physical print or support-removal trial occurred.',
        'Generic Marlin2 reference G-code is NOT MACHINE READY.'])
    (OUT/'support-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(segments=len(segs),supports=len(supports),regions={k:v['segments'] for k,v in reports.items()},
            c_slots=sum(x['segments'] for x in fin_results),c_bays=[x['segments'] for x in bay_results]),indent=2))

if __name__=='__main__': main()
