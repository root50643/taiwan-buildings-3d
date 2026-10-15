#!/usr/bin/env python3
"""Exact original-triangle sections; every positive polygon tested independently."""
from pathlib import Path
import numpy as np,json,gzip,hashlib,argparse
from shapely.geometry import Polygon
from shapely import is_valid_reason

def polygon_count(q):
    if q.is_empty:return 0
    if q.geom_type=='Polygon':return 1
    if q.geom_type=='MultiPolygon':return len(q.geoms)
    return -1

def check_sections(path,out):
    path,out=Path(path),Path(out);out.mkdir(exist_ok=True,parents=True)
    b=path.read_bytes();n=int.from_bytes(b[80:84],'little')
    t=np.frombuffer(b,offset=84,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),count=n)['v'].astype(np.float64)
    hi=t[:,:,2].max(axis=1);lo=t[:,:,2].min(axis=1);records=[];layers=[];failures=[]
    grids=[('offset071',np.arange(.071,float(hi.max()),.2)),('author_grid',np.r_[np.arange(.2,float(hi.max()),.2),float(hi.max())-.001])]
    for grid,levels in grids:
      for z in levels:
        adj={};segments=set();coplanar=0
        for f in t[(lo<=z)&(hi>=z)]:
            pts=[]
            for a,bb in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
                if tuple(a)>tuple(bb):a,bb=bb,a
                if a[2]==z and bb[2]==z:coplanar+=1;continue
                if a[2]==z:pts.append(tuple(a[:2]))
                elif bb[2]==z:pts.append(tuple(bb[:2]))
                elif min(a[2],bb[2])<z<max(a[2],bb[2]):pts.append(tuple((a+(bb-a)*(z-a[2])/(bb[2]-a[2]))[:2]))
            pts=list(dict.fromkeys(pts))
            if len(pts)==2 and pts[0]!=pts[1]:segments.add(tuple(sorted(pts)))
        for a,bb in sorted(segments):adj.setdefault(a,[]).append(bb);adj.setdefault(bb,[]).append(a)
        layer={'grid':grid,'z_mm':float(z),'original_segments':len(segments),'coplanar_edges':coplanar,'bad_degrees':sum(len(q)!=2 for q in adj.values())}
        if not adj or layer['bad_degrees'] or coplanar:
            layer['failure']='non_regular_section_requires_exact_special_case';layer['segments_xy']=sorted(segments);failures.append(layer);layers.append(layer);continue
        rem=set(adj);shape=Polygon();loopbad=[]
        while rem:
            seed=min(rem);a=seed;last=None;loop=[]
            while True:
                loop.append(a);rem.discard(a);opts=adj[a];bb=opts[0] if opts[0]!=last else opts[1];last,a=a,bb
                if a==seed or len(loop)>len(adj):break
            poly=Polygon(loop)
            if a!=seed or not poly.is_valid or poly.area<=0:loopbad.append({'reason':is_valid_reason(poly),'original_loop_xy':loop});continue
            shape=shape.symmetric_difference(poly)
        layer['individual_loop_invalid']=loopbad;layer['combined_valid']=shape.is_valid
        if loopbad or not shape.is_valid or shape.is_empty or shape.geom_type not in ['Polygon','MultiPolygon']:
            layer['failure']='invalid_original_contour';layer['combined_wkb_hex']=shape.wkb_hex;failures.append(layer);layers.append(layer);continue
        comps=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
        comps.sort(key=lambda p:(*p.bounds,p.area));layer['components']=len(comps);layer['failures']=0
        for i,c in enumerate(comps):
            e=c.buffer(-.4,quad_segs=16);o=e.buffer(.4,quad_segs=16);lost=c.difference(o);loss=lost.area/c.area
            row={'grid':grid,'z_mm':float(z),'component':i,'area_mm2':c.area,'bounds_mm':list(c.bounds),'eroded_components':polygon_count(e),'opened_components':polygon_count(o),'opening_loss_fraction':loss,'passed':polygon_count(e)==1 and polygon_count(o)==1 and loss<=.01,'original_wkb_hex':c.wkb_hex,'eroded_wkb_hex':e.wkb_hex,'opened_wkb_hex':o.wkb_hex,'lost_wkb_hex':lost.wkb_hex};records.append(row)
            if not row['passed']:layer['failures']+=1
        layers.append(layer)
    reduced=lambda r:{k:v for k,v in r.items() if not k.endswith('wkb_hex')}
    summary={'stl_sha256':hashlib.sha256(b).hexdigest(),'passed':not failures and all(r['passed'] for r in records),'method':'Exact original float32 STL coordinates promoted to float64; canonical unrounded original-edge interpolation. Valid simple loops are nested by symmetric difference. Each original positive Polygon separately eroded and opened by radius 0.4 mm, quad_segs 16. Each must remain exactly one Polygon at both stages and lose at most 1% original area. No rounding, repair, whole-layer averaging, or automatic exemption. Full original/eroded/opened/lost WKB geometry retained.','layers':len(layers),'section_failures':failures,'components':len(records),'component_failures':sum(not r['passed'] for r in records),'split_or_vanished':sum(r['eroded_components']!=1 or r['opened_components']!=1 for r in records),'maximum_opening_loss_fraction':max(r['opening_loss_fraction'] for r in records),'worst_components':[reduced(r) for r in sorted(records,key=lambda r:r['opening_loss_fraction'],reverse=True)[:30]]}
    (out/'qa-sections.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'qa-sections-full.json.gz').write_bytes(gzip.compress(json.dumps({'stl_sha256':summary['stl_sha256'],'layers':layers,'components':records},separators=(',',':')).encode(),mtime=0))
    (out/'qa-sections-details.json.gz').write_bytes(gzip.compress(json.dumps({'stl_sha256':summary['stl_sha256'],'layers':layers,'components':[reduced(r) for r in records]},separators=(',',':')).encode(),mtime=0))
    (out/'qa-sections-failed-polygons.json.gz').write_bytes(gzip.compress(json.dumps({'stl_sha256':summary['stl_sha256'],'failed_components':[r for r in records if not r['passed']]},separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k:v for k,v in summary.items() if k not in ['worst_components','section_failures']},indent=2),flush=True)
    return summary
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('stl',type=Path);a.add_argument('out',type=Path);x=a.parse_args();r=check_sections(x.stl,x.out);raise SystemExit(0 if r['passed'] else 1)
