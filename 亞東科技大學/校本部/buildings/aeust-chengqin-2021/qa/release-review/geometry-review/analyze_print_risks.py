"""Post-review interpretation; original strict failed gate is retained verbatim.

No input repair, movement or re-export. Uses the exact STL coordinates and the
new independently generated section evidence. Human print-risk decision is kept
separate from the deliberately much-stricter-than-package 1e-5 mm2 gate.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,math,os
import check_chengqin_independent as m

root=Path(__file__).parent
stl=Path(os.environ['CHENGQIN_PACKAGE']).resolve()/'models/v1/model.stl'
r=json.loads((root/'independent-stl-results.json').read_text(encoding='utf8'))
data,v,f,iv,scale,sn,attrs=m.read_binary_stl(stl)
assert hashlib.sha256(data).hexdigest()==r['sha256']=='4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a'
flagged=[q for q in r['analytic_print_review']['nonbase_downward_faces'] if not q['exact_within_45_degrees']]
rows=[]
for q in flagged:
    t=[iv[j] for j in f[q['face']]];n=m.cross(m.sub(t[1],t[0]),m.sub(t[2],t[0]))
    assert n[0]==0 and n[1]<0 and n[2]<0
    dy=max(p[1] for p in t)-min(p[1] for p in t)
    dz=max(p[2] for p in t)-min(p[2] for p in t)
    # All these are planar front-window chamfers, horizontal along X. Therefore
    # DY-DZ is the exact outward excess across their full sloped height.
    excess=Q(dy-dz,scale)
    assert excess>0
    rows.append({'face':q['face'],'vertices_mm':q['vertices_mm'],
       'exact_dy_mm':str(Q(dy,scale)),'exact_dz_mm':str(Q(dz,scale)),
       'exact_full_facet_outward_excess_mm':str(excess),'outward_excess_mm':float(excess),
       'angle_from_vertical_deg':q['angle_from_vertical_deg']})
sec=r['sections']; max_excess=max(Q(t['exact_full_facet_outward_excess_mm']) for t in rows)
nonbase=r['analytic_print_review']['nonbase_downward_faces']
result={
 'fixed_commit':'4116148c135d8a67a444ce8bf33fb64aba3e06a3','stl_sha256':r['sha256'],
 'strict_run_exit_code':1,'strict_run_digital_geometry_go':r['digital_geometry_go'],
 'strict_support_area_threshold_mm2':1e-5,'strict_flagged_sections':len(sec['support_violations_over_1e_5_mm2']),
 'strict_flagged_downward_facets':len(rows),
 'independent_findings':{
   'topology_pass':r['topology']['passes'],'exact_stored_coordinate_pair_check_pass':r['triangle_pairs']['passes'],
   'all_1796_sampled_sections_closed':not sec['invalid_or_open_sections'],
   'all_individual_0_8mm_component_cores_survive_without_split':not sec['component_core_failures'],
   'maximum_section_components':sec['max_components'],
   'maximum_section_support_excess_area_mm2':sec['maximum_outside_support_envelope_mm2'],
   'nonbase_downward_facet_count':len(nonbase),
   'maximum_angle_from_vertical_deg':max(q['angle_from_vertical_deg'] for q in nonbase),
   'all_80_strict_over_45_faces_are_front_window_chamfers':True,
   'exact_maximum_outward_excess_across_full_chamfer_mm':str(max_excess),
   'maximum_outward_excess_across_full_chamfer_mm':float(max_excess),
   'no_other_downward_facets_exceed_45_degrees':True,
 },
 'geometry_decision':'GO with disclosed shallow-relief/tall-print risks; no geometric blocker found',
 'reason':'The strict 1e-5 mm2 gate inherited from the earlier independent APOLLO review flags binary32 quantization of nominal 45-degree front-window chamfers. Exact coordinate inspection bounds their total outward excess across a full 0.65 mm chamfer to 1/131072 mm = 0.00000762939453125 mm. This is a reported microscopic departure, not an unsupported shelf or bridge. The original failed output is preserved; no checker threshold, stored coordinate or STL was changed. This decision does not claim a mathematically exact <=45-degree mesh or a slicer/physical-print pass.',
 'thin_feature_interpretation':[
   'Front recesses are shallow indentations in a filled 42.24 mm deep slab. They are not 0.65 mm free-standing walls.',
   'Ten connector recesses are shallow perimeter bands; outer return uses a 0.6 mm chamfer. The 1796 independent sections (including all vertex event intervals) retain a single core per actual material component.',
   'The 12 x 27 x 11 mm rooftop boxes lie on the main roof; the two separated components above z=148 mm are vertically supported by the main body and do not indicate two STL shells.',
   'Component erosion is not a pointwise thickness guarantee. Attached tapered joints/corner tips or shallow relief may be lost or softened by the nozzle and layer quantization.',
   'The 3 mm plinth is flat at z=0. A tall 159 mm model, material shrinkage, warping, bed adhesion, shell/infill settings and precise nozzle/path behavior require target-slicer inspection and physical confirmation.',
 ],
 'limit':'Only this candidate geometry was independently checked. Finite sections and algorithmic exact-coordinate triangle checks are not a machine-verified formal proof, printer-specific slice/G-code review or a physical test print.',
 'flagged_facets':rows,
}
(root/'print-risk-analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='flagged_facets'},indent=2,ensure_ascii=False))
