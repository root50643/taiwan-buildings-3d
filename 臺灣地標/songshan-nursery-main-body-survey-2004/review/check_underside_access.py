import pathlib,sys,json,numpy as np,manifold3d as mf

r=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);d=np.load(r/'mesh-data.npz')
visible=mf.Manifold(mf.Mesh64(np.asarray(d['vertices'],dtype=np.float64),np.asarray(d['faces'],dtype=np.uint64)))
parts=json.loads((r/'construction-parts.json').read_text());cutters=[p for p in parts if p.get('operation')=='subtract']
manufacturing=json.loads((r/'manufacturing-review.json').read_text())
checks={'exactly_three_documented_subtractive_cutters':len(cutters)==3,'disclosed_nonhistoric':manufacturing['underside_access']['authored_not_historic'] is True,'disclosed_through_floor_and_base':'AND north-gallery floor' in manufacturing['underside_access']['penetration']}
holes=[]
for i,(p,x) in enumerate(zip(cutters,[30.0,67.44,105.0])):
    v=np.asarray(p['vertices']);lo=v.min(axis=0);hi=v.max(axis=0)
    checks[f'cutter{i+1}_xy_dimensions']=bool(np.allclose((hi-lo)[:2],[4.8,4.56],rtol=0,atol=1e-6))
    checks[f'cutter{i+1}_xy_centre']=bool(np.allclose((hi+lo)[:2]/2,[x,6.6],rtol=0,atol=1e-6))
    checks[f'cutter{i+1}_starts_below_base_and_ends_above_gallery_floor']=bool(lo[2]<0 and hi[2]>6.3)
    # A half-millimetre-wide vertical tube from outside base to gallery interior.
    probe=mf.Manifold.cube([.5,.5,21.0]).translate([x-.25,6.35,-1.0])
    occupied=mf.Manifold.batch_boolean([visible,probe],mf.OpType.Intersect).volume()
    checks[f'cutter{i+1}_clear_continuous_path_into_gallery']=abs(occupied)<1e-8
    # Verify broad gallery depth remains void rather than being filled for connectivity.
    cavity=mf.Manifold.cube([.6,10.0,1.0]).translate([x-.3,1.5,12.0])
    cavity_occupied=mf.Manifold.batch_boolean([visible,cavity],mf.OpType.Intersect).volume()
    checks[f'gallery_segment{i+1}_depth_remains_empty']=abs(cavity_occupied)<1e-8
    checks[f'cutter{i+1}_nonhistoric_evidence']='NOT a historic feature' in p['evidence']
    holes.append({'name':p['name'],'bounds_mm':[lo.tolist(),hi.tolist()],'clear_path_intersection_volume_mm3':occupied,'depth_probe_intersection_volume_mm3':cavity_occupied})
report={'passed':all(checks.values()),'checks':checks,'holes':holes,'scope':'Independent cutter bounds and Boolean occupancy probes verify all three nonhistoric underside holes connect exterior to real retained gallery cavities. No trial print; aperture removal is explicitly authorized and documented.'}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['passed']
