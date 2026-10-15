"""Classify the exact original fixed-parity after probe against positive boundary intervals.
A surface winding value is diagnostic only, irrespective of whether it equals 0 or 1.
"""
from pathlib import Path
import json,gzip,hashlib
R=Path(__file__).resolve().parent
a=json.loads((R/'dense-short-chords.json').read_text());b=json.loads(gzip.open(R/'boundary-witnesses.json.gz','rt').read());bm={(q['face'],q['sample']):q for q in b['rows']};rows=[]
for q in a['flags']:
 key=(int(q['face']),int(q['sample']));r=bm[key];t=float(q['entry'])+float(q['first_solid'])+min(1e-5,float(q['air_after'])/2) if float(q['air_after'])>0 else float(q['entry'])+float(q['first_solid'])+1e-5
 intervals=[x for x in r['positive_length_boundary_intervals']if x['clipped_a']<t<x['clipped_b']]
 rows.append(dict(face=key[0],sample=key[1],original_raw=q,after_probe_t_mm=t,containing_original_triangle_intervals=intervals,classification='positive_length_external_surface_boundary'if intervals else'unresolved',before_mid_and_side_controls_passed=r['all_nonboundary_controls_passed']))
checks=dict(all_flags_have_exact_after_probe_on_positive_surface_interval=all(q['containing_original_triangle_intervals']for q in rows),all_original_side_controls_pass=all(q['before_mid_and_side_controls_passed']for q in rows))
out=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,rows=rows,limits='Does not erase original parity or strict first-chord failures. Surface winding 0/1 is not a bulk-material classification. Original flag-winding report retained without promoting its confirmed count to proof.')
(R/'flag-boundary-classification.json').write_text(json.dumps(out,indent=2));print(checks);assert all(checks.values())
