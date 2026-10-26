#!/usr/bin/env python3
"""Actual generated parts + independently reloaded STL evidence-bound topology checks."""
import argparse,pathlib,json,hashlib
import numpy as np,trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();r=a.out;cfg=json.loads(pathlib.Path(__file__).with_name('parameters.json').read_text());parts=json.loads((r/'construction-parts.json').read_text());D=np.load(r/'mesh-data.npz');m=trimesh.load_mesh(r/(cfg['model_id']+'.stl'),process=True)
cols=[x for x in parts if x['name'].startswith('Paper column ')];assert len(cols)==58
centres=np.array([(np.array(x['vertices']).min(axis=0)+np.array(x['vertices']).max(axis=0))/2 for x in cols])[:,:2]
a0,b0=cfg['ellipse_semi_axes_mm'];ellipse_error=float(np.abs((centres[:,0]/a0)**2+(centres[:,1]/b0)**2-1).max());assert ellipse_error<2e-6
rear=int((centres[:,1]>=-1e-5).sum());front=int((centres[:,1]<-1e-5).sum());assert (rear,front)==(44,14)
dist=np.linalg.norm(centres-np.roll(centres,1,axis=0),axis=1);assert dist.max()/dist.min()>2.5 and a0/b0>1.4
samples=[]
for x in np.linspace(-108,108,19):
 for y in np.linspace(-78,78,15):
  loc,_,_=m.ray.intersects_location([[x,y,115]],[[0,0,-1]],multiple_hits=True);assert len(loc);z=float(loc[:,2].max());assert 82.35<z<=104.001;samples.append(z)
assert len(samples)==285
# A real roof-hole negative mutant: remove all membrane triangles from actual final arrays.
mutant=trimesh.Trimesh(D['vertices'],D['faces'][D['materials']!=0],process=False)
hits,_,_=mutant.ray.intersects_location([[12,5,85]],[[0,0,1]],multiple_hits=True);assert len(hits)==0
hits,_,_=m.ray.intersects_location([[12,5,85]],[[0,0,1]],multiple_hits=True);assert len(hits)>=1
# Naive circular/uniform-column substitution demonstrably violates authored layout contract.
t=np.linspace(0,2*np.pi,58,endpoint=False);u=np.c_[a0*np.cos(t),a0*np.sin(t)];uniform_error=np.abs((u[:,0]/a0)**2+(u[:,1]/b0)**2-1).max();assert uniform_error>.5
mast=next(x for x in parts if x['name']=='Suspended central roof mast');mv=np.array(mast['vertices']);assert mv[:,2].min()>60
report={'all_pass':True,'stl_sha256':hashlib.sha256((r/(cfg['model_id']+'.stl')).read_bytes()).hexdigest(),'paper_columns':58,'rear_half_columns_including_endpoints':rear,'front_half_columns_excluding_endpoints':front,'ellipse_semi_axes_model_mm':[a0,b0],'maximum_ellipse_equation_residual':ellipse_error,'adjacent_column_spacing_range_mm':[float(dist.min()),float(dist.max())],'roof_grid_rays':285,'roof_grid_min_max_z_mm':[min(samples),max(samples)],'single_maximum_roof_height_mm':float(m.vertices[:,2].max()),'suspended_mast_min_z_mm':float(mv[:,2].min()),'negative_controls':{'actual_membrane_triangle_removal_detected_as_roof_hole':True,'uniform_circle_rejected':True,'deliverable_not_modified':True},'scope':'Tests topology and declared approximate ratios, not measured Taiwan dimensions or hidden connections.'}
(r/'qa/hall-layout-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
