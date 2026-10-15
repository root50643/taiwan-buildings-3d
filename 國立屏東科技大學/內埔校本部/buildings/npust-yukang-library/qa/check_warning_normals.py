from pathlib import Path
P=Path(__file__).parent/'dense/classify_short.py';__file__=str(P);s=P.read_text();exec(s[:s.index('helper=')])
from shapely import wkt
QA=R.parent;rows=json.loads(gzip.decompress((QA/'warning-corners-original.json.gz').read_bytes()))['rows'];out=[]
for r in rows:
 g=wkt.loads(r['original_polygon_wkt']);q=g.representative_point();p=np.array([q.x,q.y,r['z_mm']]);probes=[]
 for direction in [np.array([1.,0,0]),np.array([0.,1.,0])]:
  hh=sorted(solid.ray_cast(p,p+direction*1000),key=lambda h:h.distance);hh=[h for h in hh if h.distance>1e-12];h=hh[0];f=remap[h.face_id];surface=p+direction*h.distance*1000;n=nn[f];o=surface+n*1e-5
  rh=sorted(solid.ray_cast(o,o-n*1000),key=lambda h:h.distance);rh=[h for h in rh if h.distance>1e-12];first=(rh[1].distance-rh[0].distance)*1000 if len(rh)>=2 else None
  probes.append({'source_direction':direction.tolist(),'actual_original_face':int(f),'surface_mm':surface.tolist(),'actual_normal':n.tolist(),'ray_start_mm':o.tolist(),'normal_first_solid_mm':first,'hits':[{'distance_mm':x.distance*1000,'original_face':int(remap[x.face_id])}for x in rh]})
 out.append({'z_mm':r['z_mm'],'original_component_index':r['original_component_index'],'family':r['family'],'probes':probes})
with gzip.open(QA/'warning-original-normal-probes.json.gz','wt')as f:json.dump({'stl_sha256':hashlib.sha256(raw).hexdigest(),'method':'Each original high-loss Polygon representative point sends +X/+Y to its actual original mesh boundary; then probe actual hit-face inward normal. This is 2 representatives per sampled Polygon, NOT global family minimum thickness.','rows':out},f)
s={k:{'component_samples':sum(r['family']==k for r in out),'probes':sum(2 for r in out if r['family']==k),'minimum_representative_actual_normal_mm':min(p['normal_first_solid_mm']for r in out if r['family']==k for p in r['probes'] if p['normal_first_solid_mm']is not None),'under_0_8_probes':sum(p['normal_first_solid_mm']is None or p['normal_first_solid_mm']<.8 for r in out if r['family']==k for p in r['probes'])}for k in set(r['family']for r in out)}
(QA/'warning-original-normal-summary.json').write_text(json.dumps(s,indent=2));print(s)
