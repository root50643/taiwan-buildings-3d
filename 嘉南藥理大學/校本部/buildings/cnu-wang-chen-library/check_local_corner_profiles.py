from pathlib import Path
import numpy as np,json,trimesh
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;T=trimesh.load(O/'model.stl',process=False).triangles;E=T[:,1]-T[:,0];F=T[:,2]-T[:,0];norm=np.cross(E,F);norm/=np.linalg.norm(norm,axis=1)[:,None]
def hits(o,d):
 p=np.cross(d,F);det=np.einsum('ij,ij->i',E,p);good=abs(det)>1e-13;iv=np.zeros(len(T));iv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*iv;q=np.cross(s,E);v=q@d*iv;t=np.einsum('ij,ij->i',F,q)*iv;ix=np.flatnonzero(good&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-9));ix=ix[np.argsort(t[ix])];ix=ix[np.r_[True,np.diff(t[ix])>1e-7]] if len(ix) else ix;return [(float(t[i]),int(i)) for i in ix]
def probe(p,n):
 o=p+n*1e-5;h=hits(o,-n);r={'surface_point':p.tolist(),'normal':n.tolist(),'hits_distance_face':h}
 if len(h)>1:
  r.update(first_solid=h[1][0]-h[0][0],exit_point=(o-n*h[1][0]).tolist(),exit_face_vertices=T[h[1][1]].tolist(),after_air=h[2][0]-h[1][0] if len(h)>2 else None,air_end_point=(o-n*h[2][0]).tolist() if len(h)>2 else None)
  dd=np.array([.713123,.431977,.552111]);r['controls']=[len(hits(q,dd))%2 for q in [p-n*min(1e-5,r['first_solid']/4),o,o-n*((h[0][0]+h[1][0])/2),o-n*(h[1][0]+min(1e-5,r['after_air']/2 if r['after_air'] else 1e-5))]]
 return r
OLD=T.copy();result={};fig,axes=plt.subplots(2,2,figsize=(13,12));mesh=trimesh.Trimesh(T.reshape(-1,3),np.arange(len(T)*3).reshape(-1,3),process=False)
for slot,face in enumerate([16042,14622,62655,3549]):
 t=OLD[face];p=t.mean(0);n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n);edges=[(np.linalg.norm(t[j]-t[i]),i,j) for i,j in [(0,1),(1,2),(2,0)]];_,i,j=min(edges);edge=(t[j]-t[i]);edge/=np.linalg.norm(edge);rows=[]
 for fraction in [.1,.33,.5,.67,.9]:
  k=3-i-j;origin=(t[i]+t[j])*.5*(1-fraction)+t[k]*fraction
  for shift in [-.8,-.4,-.2,-.1,-.01,-.001,0,.001,.01,.1,.2,.4,.8]:
   q=origin+edge*shift;hh=hits(q+n,-n)
   if not hh:continue
   pp=q+n-n*hh[0][0];fi=hh[0][1];r=probe(pp,norm[fi]);r.update(projected_surface_face=fi,long_fraction=fraction,tangential_offset_mm=shift);rows.append(r)
 hh=hits(p+n,-n);pp=p+n-n*hh[0][0];center=probe(pp,norm[hh[0][1]]);center["new_face"]=hh[0][1];result[str(face)]={'vertices':t.tolist(),'short_edge_length':min(edges)[0],'long_edge_length':max(edges)[0],'center':center,'cross_groove_surface_profiles':rows,'profile_method':'Move from short-edge midpoint toward opposite vertex by fraction, offset in short-edge direction. Project to actual first surface from 1mm exterior along reference face normal; then use true cross normal of hit original facet. Offsets can change facets; no claim all shifts lie in original narrow face.'}
 z=p[2];sec=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1]);ax=axes.flat[slot]
 if sec:
  for entity in sec.entities:
   curve=sec.vertices[entity.points];ax.plot(curve[:,0],curve[:,1],color='black',lw=.7)
 ax.plot(p[0],p[1],'ro',ms=4);ep=np.array(center.get('exit_point',p));ax.plot([p[0],ep[0]],[p[1],ep[1]],'r-',lw=2)
 ap=center.get('air_end_point');
 if ap:ax.plot([ep[0],ap[0]],[ep[1],ap[1]],'b--',lw=1)
 radius=1.2 if slot<2 else 1;ax.set_xlim(p[0]-radius,p[0]+radius);ax.set_ylim(p[1]-radius,p[1]+radius);ax.set_aspect('equal');ax.grid();ax.set_title(f'Original face {face}, Z={z:.6f} mm\nred first-solid; blue next-air');ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
import hashlib
report={'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'limits':'Original-face local convex-corner profiles, not a minimum wall guarantee. Tiny first chords approaching vertices are retained; no summation over later air gaps. Entry face14622 spans beyond entry height; its centroid is not an entry-only result.','profiles':result}
(O/'local-corner-profiles.json').write_text(json.dumps(report,indent=2));fig.tight_layout();fig.savefig(O/'local-corner-sections.png',dpi=180)
print('saved')
for face,r in result.items():
 print(face, 'shortedge',r['short_edge_length'],'center',r['center']['first_solid']);print([(x['tangential_offset_mm'],x['projected_surface_face'],round(x.get('first_solid',0),6),x.get('after_air')) for x in r['cross_groove_surface_profiles'] if x['long_fraction']==.5])
