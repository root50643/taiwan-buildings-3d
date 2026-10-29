import pathlib,sys,json,numpy as np,manifold3d as mf

r=pathlib.Path(sys.argv[1]);target=pathlib.Path(sys.argv[2]);parts=json.loads((r/'construction-parts.json').read_text());d=np.load(r/'mesh-data.npz')
# Independent fresh union in final millimetre units, rather than trusting builder
# component/evidence counts. Numerical re-triangulation is allowed, missing volume is not.
all_parts=[];cutters=[]
for p in parts:
    solid=mf.Manifold(mf.Mesh64(np.asarray(p['vertices'],dtype=np.float64),np.asarray(p['faces'],dtype=np.uint64)))
    if p.get('operation','add')=='subtract':cutters.append(solid)
    else:all_parts.append(solid)
union=mf.Manifold.batch_boolean(all_parts,mf.OpType.Add)
if cutters:union=union-mf.Manifold.batch_boolean(cutters,mf.OpType.Add)
visible=mf.Manifold(mf.Mesh64(np.asarray(d['vertices'],dtype=np.float64),np.asarray(d['faces'],dtype=np.uint64)))
extra=visible-union;missing=union-visible
dv=abs(visible.volume()-union.volume())
extra_v=abs(extra.volume());missing_v=abs(missing.volume())
relative=(extra_v+missing_v)/max(abs(union.volume()),1)
out={'passed':relative<1e-6,'parts':len(parts),'positive_parts':len(all_parts),'subtractive_cutters':len(cutters),'independent_union_volume_mm3':union.volume(),'visible_volume_mm3':visible.volume(),'absolute_volume_difference_mm3':dv,'extra_visible_volume_mm3':extra_v,'missing_visible_volume_mm3':missing_v,'symmetric_difference_relative_volume':relative,'tolerance_relative':1e-6,'meaning':'All authored additive parts freshly boolean-unioned and documented subtractive cutters applied. Visible volume must match to one part per million, allowing disclosed tiny numerical simplification. This is not a print trial.'}
target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
