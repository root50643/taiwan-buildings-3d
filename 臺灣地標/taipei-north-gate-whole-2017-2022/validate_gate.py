#!/usr/bin/env python3
"""Source-contract geometric invariants of the actual North Gate mesh, not a survey."""
import pathlib,argparse,json,hashlib
import numpy as np,trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();r=a.out
parts=json.loads((r/'construction-parts.json').read_text());info=json.loads((r/'editable-parts.json').read_text());by={x['name']:x for x in parts};ops={x['name']:x for x in info['features']}
m=trimesh.load_mesh(r/'taipei-north-gate-whole-2017-2022.stl',process=True)
roof=by['One connected terracotta tiled roof envelope'];rm=trimesh.Trimesh(roof['vertices'],roof['faces'],process=True);assert len(rm.split(only_watertight=False))==1 and rm.is_watertight
required=['Lower continuous stone body with true through vault','Upper red four-face envelope and actual openings','same end tall arched brick reveal','other end tall arched brick reveal','same upper gable and lower hip join','other upper gable and lower hip join','left longitudinal raised ridge span','middle longitudinal raised ridge span','right longitudinal raised ridge span','Separator descending raised band -38','Separator descending raised band 38']
assert all(n in by for n in required)
assert len([n for n in by if n.startswith('Terminal hip seam')])==4
assert by['Front plaque field only'] and ops['Front plaque field only']['bounds_model_mm'][4]<-73
assert not any('reverse plaque' in n.lower()for n in by)
# Orthographic downward rays test coverage of the connected tiled envelope itself.
xy=np.array([[x,y]for x in np.linspace(-122,122,31)for y in np.linspace(-76,76,21)])
starts=np.c_[xy,np.full(len(xy),220.)];directions=np.tile([0.,0.,-1.],(len(xy),1));hits,ids,tri=rm.ray.intersects_location(starts,directions,multiple_hits=False)
assert len(set(ids))==len(xy),'Missing roof envelope surface'
assert hits[:,2].min()>147 and hits[:,2].max()<205
# Source-relative broad ratios are authored approximations, not measurements.
assert np.allclose(np.ptp(m.vertices,axis=0),[249.7321167,157.7767944,204.4546204],atol=.01)
# Generic flat roof negative fixture must fail the established two-slope profile.
def tops(mesh,xy):
 out=[]
 for x,y in xy:
  loc,_,_=mesh.ray.intersects_location([[x,y,230]],[[0,0,-1]],multiple_hits=True)
  assert len(loc);out.append(float(loc[:,2].max()))
 return out
samples=[[-15,-70],[-15,-55],[-15,-40],[-15,-25],[-15,-8]];z=tops(m,samples);assert np.all(np.diff(z)>.02)
flat=trimesh.creation.box([248,156,2]);flat.apply_translation([0,0,155]);zz=tops(flat,samples);assert not np.all(np.diff(zz)>.02)
report={'all_pass':True,'stl_sha256':hashlib.sha256((r/'taipei-north-gate-whole-2017-2022.stl').read_bytes()).hexdigest(),'whole_building':True,'single_connected_closed_roof_construction_shell':True,'roof_downward_coverage_rays':len(xy),'roof_coverage_complete':True,'required_source_grounded_components':required,'terminal_diagonal_hip_seams':4,'three_longitudinal_ridge_spans':3,'intermediate_descending_separator_bands_both_slopes':2,'front_plaque_not_mirrored_to_reverse':True,'four_facades_and_true_openings':'Independent reloaded STL rays in open-ray-validation.json; same-end correction is explicit in component evidence.','flat_prism_roof_negative_control_detected':True,'dimension_policy':'Normalized model millimetres and broad photo proportions only; not surveyed dimensions, exact roof curvature or current as-built.'}
(r/'qa/gate-layout-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
