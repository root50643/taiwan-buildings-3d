"""Tie final STL hashes to completed slice trials without discarding prior flags."""
import argparse,json,hashlib,shutil
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
 p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('--mesh-report',default='qa/v4-raw/mesh_qa.json');args=p.parse_args();root=Path(args.package)
 final=json.loads((root/'assembly.json').read_text());mesh=json.loads((root/args.mesh_report).read_text())
 assert mesh['manifest_sha256']==sha(root/'assembly.json'),'Final manifest changed after QA snapshot; review before rebinding.'
 sources=['slicing/v5-access-01/slicer_qa.json','slicing/v4-new-and-brim-01/slicer_qa.json','slicing/v3-trial-01/slicer_qa.json']
 evidence=[]
 for part in final['parts']:
  actual=sha(root/part['stl']);assert actual==part['sha256']
  found=None
  for path in sources:
   if not (root/path).exists():continue
   report=json.loads((root/path).read_text())
   for r in report['parts']:
    if r['id']==part['id'] and r['input_sha256']==actual:
     found=dict(r);found['source_report']=path
     found['log_path']=(Path(path).parent/r['log']).as_posix()
     if r.get('gcode'):found['gcode_path']=(Path(path).parent/r['gcode']).as_posix()
     found['log_sha256']=sha((root/path).parent/r['log'])
     if r.get('gcode'):found['gcode_sha256']=sha((root/path).parent/r['gcode'])
     break
   if found:break
  assert found and found['slice_success'],part['id']
  found['binding']='Exact physical STL SHA-256 match; no rescale or geometry substitution.'
  evidence.append(found)
 result={'manifest_sha256':sha(root/'assembly.json'),'mesh_report':args.mesh_report,'parts':evidence,
         'physical_instances':len(evidence),'distinct_stl_count':len(set(x['input_sha256'] for x in evidence)),
         'all_parts_have_actual_successful_slice':all(x['slice_success'] for x in evidence),
         'all_selected_slice_logs_warning_free':all(not x['raw_flags'] for x in evidence),
         'machine_ready':False,'physical_print_performed':False,'trial_fit_performed':False,
         'manufacturing_status':'Conditional digital candidate; physical print, adhesion, short-ledge detail and trial fit remain unverified.',
         'retained_prior_warnings':'v3-trial-01 pier low-bed-adhesion warning remains in the original report and logs. Selected v4 pier trial adds 3 mm outer brim; no warning is not proof of physical adhesion.'}
 write(root/'qa/final_slice_evidence.json',result)
 v1={'run_status':'Interrupted at parent request before assembly stage; all nine per-instance mesh analyses had completed.','reason':'Source footprint registration revisions were in progress.','raw_report':'qa/v1-raw/mesh_qa.json','exact_original_inputs':'qa/history/v1-reproduction','sha_comparison':'qa/v1-raw/reproduction_sha_comparison.json','failures_retained':['03-south-body: seven disconnected shells/components, including three roof eyebrows unsupported by the main roof and three enclosed window-cutter shells.','04-hall-roof: thin convex-hull overhang wedges; minimum face-centroid normal thickness 0.03369833 mm.'],'fixed_in_v3_and_retested_v4':['03 moved recess to actual exterior, connected roof eyebrows with support wall; now one component.','04 convex hull clipped to hall footprint; current face-centroid normal minimum 1.19999981 mm.'],'partial_early_snapshot_note':'v1-raw/input-snapshot contains only the files whose hashes still matched at early snapshot time. Its manifest was already revised; use the complete, SHA-verified history/v1-reproduction instead.'}
 write(root/'qa/v1-raw/run-status.json',v1)
 paircount=sum(x['triangle_contact_counts']['aabb_pairs'] for x in mesh['parts'])
 totalfaces=sum(x['faces'] for x in mesh['parts'])
 rows=[]
 for x in mesh['parts']:
  sliced=next(r for r in evidence if r['id']==x['id']);t=sliced['toolpath']
  rows.append(f"| {x['id']} | {x['faces']} | {x['components']} | {x['thickness_summary']['minimum_mm']:.6f} | {t['layer_count']} | {t['z_max_mm']:g} |")
 sectionsteps=sum(x['sections']['count'] for x in mesh['parts'])
 body='''# Manufacturing QA evidence

This candidate has **8 distinct physical STL types and 10 physical instances**.
All ten instance meshes are watertight, consistently wound, positive-volume and
single-component. No duplicate or degenerate faces were found. The all-triangle
contact check found no non-topological self-contact or surface intersection.
All 45 assembled part pairs passed the declared contact rules, with zero computed
intersection volume. This is a digital candidate: no print or physical fit test
has been performed.

## Exact evidence

'''+f"- Final assembly manifest SHA-256: `{sha(root/'assembly.json')}`.\n- {totalfaces:,} instance triangles and {paircount:,} AABB triangle-pair candidates examined, with no sampling or pair cap.\n- {sectionsteps:,} per-instance horizontal sections at 0.2 mm increments plus explicit heights.\n"+'''- Full raw mesh report: `v4-raw/mesh_qa.json`; all pair, thickness and section detail files sit beside it.
- Actual PrusaSlicer 2.9.6 reports: `../slicing/v3-trial-01/slicer_qa.json` and `../slicing/v4-new-and-brim-01/slicer_qa.json`.
- `final_slice_evidence.json` binds each final STL SHA-256 to the actual completed slice. New 01/02/08 and brimmed piers were sliced for v4. Unchanged 03–06 are bound to their identical v3 STL hashes.
- The selected actual slices all exited 0, contain extrusion and layers, remain within the 220 mm QA bed, and have no warning lines. The three v3 pier adhesion warnings remain in their original report and logs.
- `metadata_redactions.json` records before/after SHA-256 for local path metadata redaction. Warning content and G-code commands remain unchanged. Final log and G-code hashes are rebound in each slice report and final evidence record.
- `control-tests.json` records nine executed known positives/negatives for the self-contact algorithm: true closed-box and triangle crossings, coplanar overlap, non-topological point/edge contacts, legal shared edge/vertex, and ordinary/separated boxes. All nine controls passed. This validates those controls without proving every degenerate configuration.
- `contact-patches.json` records all-triangle mating surface area per contact plane for each expected adhesive pair; it is not a glue-strength or physical-fit test.
- `vertex-links.json` checks every merged vertex for a single connected degree-two link cycle, supplementing edge watertightness so pinched/disconnected local vertex fans cannot pass silently.

| Instance | Faces | Components | Minimum centroid-ray hit (mm) | Actual sliced layers | Last nominal Z (mm) |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

The thickness column is the minimum of the tested inward face-centroid normal
rays, not a proof of the minimum at every point. Exact STL dimensions and hashes
are recorded in the manifest and raw report. Nominal 0.2 mm slicing quantizes the
7.3 mm bridge tray to a last toolpath Z of 7.2 mm; the small difference must not
be misreported as physical fit validation.

## Raw flags and their limits

- **02 `THICKNESS_RAY_MISS` remains**: one exact centroid ray fell through an opposing triangle seam. Four tangential offsets of 0.0001 mm hit at approximately 34.1 mm. Original miss and supplemental ray distances are both retained in its thickness JSON. This is numerical supplemental evidence, not removal of the original flag.
- **02/03 `SECTION_THIN_OPENING_SCREEN` remains**: the 0.8 mm morphological opening leaves 0.82286 mm² at the last 0.1 mm section below each pair of sloping stair-fin tips (print Z 24.9 / 33.9 mm). The fins have 1.2 mm crosswise thickness but taper longitudinally near the peak. The successful last layers provide toolpath evidence; the small caps remain a detail-quality risk.
- **01/02/03/05 `SECTION_45DEG_OVERHANG_SCREEN` remains**: abrupt window headers, projecting rail bands and roof eyebrow ledges exceed the screening allowance. Window recesses are 0.8 mm deep and 3.6 mm wide; bridge openings are 2 mm wide; facade bands project approximately 0.45 mm. The north roof eyebrows include approximately 1.5 mm short cantilevers. No support material was requested or generated in the selected slices. These short ledges can droop or lose detail and require physical validation.
- **08 small decorative relief**: the final short steps have levels 1.2 / 1.6 / 2.0 mm, with 0.4 mm rises. They are supported by the underlying mass. Face-centroid inward rays must not be interpreted as a 0.9 mm lower bound on decorative feature height. The earlier v4 platform geometry and its results remain in history; v5 makes both sets of steps explicit and rechecks that changed STL.
- **Pier adhesion**: v3 without brim produced `Low bed adhesion`. v4 adds a 3 mm outer brim, slices with a first-layer brim, and emits no stability warning. This is a slicer mitigation; real bed adhesion remains untested.

## Assembly and support access

Each building body rests on its own flat underside in the provided STL orientation.
The north upper mass prints separately on its full footprint, then joins the lower
mass at assembled Z 18 mm. The low conference roof prints separately on its flat
underside; its reconstructed roof now remains inside the hall footprint.

The bridge prints as an upright open tray with a 1.6 mm floor and 1.2 mm walls.
Its 1.2 mm lid prints flat and is glued after any window cleanup. The tray interior
is accessible from above before lid attachment. Three piers print upright with
the recommended brim. The assembly is not printed across the courtyard in place;
there is no 40 mm airborne print span or support trapped under a closed bridge lid.
All joining faces are adhesive butt contacts without press-fit keys; no clearance
or glue-gap claim has been physically tested.

`v4-raw/assembly_sections.png` is original model geometry, visually inspected at
nine levels. Numeric probes in the matching JSON show the courtyard sample open
at all tested levels, the bridge sample open at Z 5 mm / occupied by floor at
Z 9.5 mm / hollow at Z 12.5 mm / occupied by lid at Z 16.9 mm. The entrance sample
is open at Z 5 mm and occupied by the separately printed upper mass at Z 18.5 mm.
The entrance ground tie beams occupy the Z 0.6 mm sample, which is explicitly
shown rather than calling the whole ground plane empty. These are selected point
probes plus complete planar sections, not a site-wide accessibility certification.

## Retained failures and reproduction

`v1-raw` retains the original failed component/thickness findings and the interrupted
run boundary. `history/v1-reproduction` reproduces all nine original per-instance
input hashes exactly (nine out of nine matches). The disconnected roof eyebrows
and internal recess shells were corrected, and the hall roof's sub-0.07 mm convex
hull wedges were clipped to the footprint. Both changes were rechecked in v3 and
v4. v3 raw flags and unbrimmed pier warning logs remain intact.

## QA slicing profile and reuse

Actual PrusaSlicer executable SHA-256:
`7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704`.

The generic single-material PLA QA profile uses a 0.4 mm nozzle, 0.2 mm layers,
three perimeters, 15% infill, a 220 × 220 mm bed and Arachne perimeters. Piers add
a 3 mm outer brim. The logs, profile, G-code hashes and parsed extrusion/layer
statistics are retained in each trial directory. All G-code is **QA ONLY** and
has no machine start/end sequence; it must not be sent directly to a printer.
No multi-toolhead or four-color print configuration was tested. Scene colors do
not establish multi-color manufacturing readiness.

Portable rerun sources are in `../source/qa-tools/`. Supply a local PrusaSlicer
console executable through `--slicer` or `PRUSASLICER_EXE`. No global configuration,
credentials, Library artifact or other task was modified.
'''
 body=body.replace('v4-raw/',str(Path(args.mesh_report).parent.name)+'/')
 body=body.replace('`../slicing/v4-new-and-brim-01/slicer_qa.json`.','`../slicing/v4-new-and-brim-01/slicer_qa.json`, plus `../slicing/v5-access-01/slicer_qa.json` when present.')
 body=body.replace('New 01/02/08 and brimmed piers were sliced for v4.','New 01/02 and brimmed piers were sliced for v4; the final changed 08 was sliced again for v5.')
 (root/'qa/MANUFACTURING_QA.md').write_text(body,encoding='utf-8')
 for name in ['manufacturing_qa.py','slice_qa.py','assembly_sections.py','compile_evidence.py','control_tests.py','contact_patches.py','vertex_links.py','README.md']:
  target='QA-METHODS.md' if name=='README.md' else name
  source=Path(__file__).parent/name
  if not source.exists() and name=='README.md':source=Path(__file__).parent/'QA-METHODS.md'
  destination=root/'source/qa-tools'/target
  if source.resolve()!=destination.resolve():shutil.copyfile(source,destination)
 print(json.dumps({'instances':len(evidence),'distinct':result['distinct_stl_count'],'all_sliced':result['all_parts_have_actual_successful_slice'],'selected_logs_clear':result['all_selected_slice_logs_warning_free'],'assembly':mesh['assembly']['pass'],'triangle_faces':totalfaces,'candidate_pairs':paircount,'sections':sectionsteps}))
if __name__=='__main__':main()
