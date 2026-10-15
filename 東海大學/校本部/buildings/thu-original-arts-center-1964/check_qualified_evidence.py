#!/usr/bin/env python3
"""Author-qualified evidence only. Strict morphology failures stay false.
Independent review/publication approval is a separate decision, never inferred.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,json
from shapely import from_wkb
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 if str(p).endswith('.gz'):
  with gzip.open(p,'rt') as f:return json.load(f)
 return json.loads(Path(p).read_text())
def key(r):return (r['grid'],r['z_mm'],r['component'])
def evaluate(top,sections,metrics,failed,roots,link,detail,connection,connection_detail,complete,complete_detail,clearance,dense,dense_minimum,blend,privacy,curvature,reproduction,bindings):
 fs=[r for r in metrics['components'] if not r['passed']];fmap={key(r):r for r in failed['failed_components']};mapped=detail['component_records'];mkeys=[key(r['strict_original_record']) for r in mapped]
 exact=[];pieces=[]
 for r in mapped:
  k=key(r['strict_original_record']);src=fmap.get(k)
  exact.append(src is not None and src==r['strict_original_record'] and not r['geometric_failure_reasons'] and r['checks']['unique_source_root_and_contained_fan_disk'] and r['checks']['all_original_boundary_midpoint_intervals_pass'] and r['checks']['all_material_air_winding_controls_pass'])
  if src is None:pieces.append(False);continue
  loss=from_wkb(bytes.fromhex(src['lost_wkb_hex']));parts=list(loss.geoms) if hasattr(loss,'geoms') else [loss]
  actual=[detail['loss_piece_records'][i] for i in r['loss_piece_ids']]
  pieces.append(sorted(p.wkb_hex for p in parts)==sorted(p['loss_piece_wkb_hex'] for p in actual))
 checks={
 'all_reports_bound_to_exact_stl':bindings,
 'raw_topology_size_volume_normals_pass':top['passed'] and all(top['gates'].values()),
 'strict_morphology_false_preserved':sections['passed'] is False and link['strict_morphology_passed'] is False and detail['strict_original_morphology_passed'] is False,
 'all_unrounded_sections_valid':not sections['section_failures'],
 'no_eroded_or_opened_component_split_or_disappearance':sections['split_or_vanished']==0 and all(r['eroded_components']==1 and r['opened_components']==1 for r in metrics['components']),
 'every_strict_failure_retained_once':len(fs)==sections['component_failures']==len(fmap)==len(mapped)==len(set(mkeys)) and set(mkeys)==set(fmap)=={key(r) for r in fs},
 'every_exact_failed_polygon_and_loss_geometry_certified':bool(exact) and all(exact) and all(pieces),
 'every_actual_root_certificate_pass':roots['passed'] and all(roots['checks'].values()) and all(r['passed'] for r in roots['per_instance_summary']) and roots['minimum_certified_material_core_diameter_mm']>=.8,
 'bounded_loss_geometry_and_interval_evidence_pass':not link['unclassified_components'] and not link['failed_or_unclassified_ray_ids'] and not link['failed_winding_controls'],
 'all_retained_boundary_overlap_diagnostics_have_separate_complete_piece_proofs':complete['complete_loss_piece_linkage_evidence_passed'] and complete['negative_controls_passed'] and not complete['failed_piece_linkages'] and len(complete_detail['component_fan_proofs'])==len(fs) and all(p['complete_loss_piece_linkage_passed'] and all(p['checks'].values()) for p in complete_detail['all_loss_piece_linkage_proofs']) and sorted(p['loss_piece_wkb_hex'] for p in complete_detail['all_loss_piece_linkage_proofs'])==sorted(p['loss_piece_wkb_hex'] for p in detail['loss_piece_records']),
 'every_exact_z_section_disk_connected_to_certified_3d_core':connection['passed'] and connection['negative_controls_passed'] and not connection['failed_connections'] and connection['exact_failed_component_disk_connections']==len(fs) and all(v['passed'] for v in connection_detail['disk_connections']) and {tuple(v['component_key']) for v in connection_detail['disk_connections']}==set(fmap),
 'no_automatic_strict_morphology_exemption':link['automatic_morphology_exemption_applied'] is False,
 'independent_original_triangle_root_clearance_pass':clearance['passed'] and not clearance['failed_paths'] and clearance['minimum_independent_continuous_diameter_lower_bound_mm']>=.8,
 'shortest_normal_intervals_independently_winding_checked':dense_minimum['passed'] and dense_minimum['point_controls']==150 and all(c['passed'] for row in dense_minimum['rows'] for c in row['controls']),
 'dense_original_normals_pass':dense['passed'] and all(dense['checks'].values()) and dense['samples']==10*top['triangles'] and dense['flagged_or_short_samples']==0 and dense['minimum_first_material_mm']>=.8,
 'saved_scene_privacy_pass':privacy['passed'] and all(privacy['checks'].values()),
 'saved_blend_exact_oriented_geometry_pass':blend['passed'] and blend['canonical_oriented_triangle_bytes_equal_to_STL'],
 'illustrative_curvature_checks_pass':curvature['passed'],
 'independent_rebuild_and_render_pixels_pass':reproduction['passed'] and all(reproduction['checks'].values())}
 return {'author_qualified_evidence_passed':all(checks.values()),'checks':checks,'strict_morphology_passed':False,'strict_failed_component_count':sections['component_failures'],'maximum_strict_opening_loss_fraction':sections['maximum_opening_loss_fraction'],'retained_false_exact_boundary_overlap_diagnostics':complete['exact_boundary_overlap_diagnostics_false'],'retained_false_exact_covers_diagnostics':complete['exact_covers_false_diagnostic_count'],'declared_loss_excursion_envelope_mm':complete['declared_original_boundary_containment_precision_mm'],'independent_review_status':'not_implied_by_author_evidence','publication_approved':False,'scope':'Every exact retained strict opening-loss case must have bounded original-geometry root linkage. This does not change strict morphology passed=false, establish global minimum thickness, or constitute independent release approval.'}

def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=HERE);a.add_argument('--dense',type=Path,default=Path('dense_evidence'));a.add_argument('--roots',type=Path,default=Path('root_evidence'));x=a.parse_args();r=x.root.resolve();o=r/'output';d=r/x.dense;rt=r/x.roots
 paths={'top':o/'qa-topology.json','sections':o/'qa-sections.json','metrics':o/'qa-sections-details.json.gz','failed':o/'qa-sections-failed-polygons.json.gz','roots':rt/'root_support_report.json','link':rt/'root_loss_report.json','detail':rt/'root_loss_details.json.gz','connection':rt/'root_section_connection_report.json','connection_detail':rt/'root_section_connection_details.json.gz','complete':rt/'root_complete_loss_linkage_report.json','complete_detail':rt/'root_complete_loss_linkage_details.json.gz','clearance':rt/'root_clearance_report.json','dense':d/'dense-audit.json','dense_minimum':d/'dense-minimum-winding.json','blend':o/'qa-blend.json','privacy':o/'qa-scene-privacy.json','curvature':o/'qa-curvature.json','reproduction':o/'qa-reproduction.json'}
 missing=[str(p.relative_to(r)) for p in paths.values() if not p.exists()]
 if missing:
  report={'author_qualified_evidence_passed':False,'missing_evidence':missing,'strict_morphology_passed':False,'publication_approved':False};(o/'qa-author-qualified.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return False
 data={k:read(p) for k,p in paths.items()};stlsha=sha(o/'model.stl');bindings=[]
 for k,v in data.items():bindings.append(v.get('stl_sha256',v.get('sha256'))==stlsha)
 bindings.append(data['privacy']['blend_sha256']==sha(o/'model.blend'))
 bindings += [sha(o/v['file'])==v['sha256'] for v in data['privacy']['pngs']]
 bindings += [sha(r/'parameters.json')==data['roots']['source_parameters_sha256'],sha(o/'build-manifest.json')==data['roots']['source_manifest_sha256'],sha(rt/data['roots']['detail_file'])==data['roots']['detail_sha256'],sha(rt/data['link']['detail_file'])==data['link']['detail_sha256'],sha(paths['roots'])==data['link']['source_root_report_sha256']]
 bindings += [sha(rt/data['connection']['detail_file'])==data['connection']['detail_sha256'],data['connection']['source_support_details_sha256']==data['roots']['detail_sha256'],data['connection']['source_loss_details_sha256']==data['link']['detail_sha256']]
 bindings += [sha(rt/data['clearance']['detail_file'])==data['clearance']['detail_sha256'],sha(paths['roots'])==data['clearance']['source_support_report_sha256'],data['clearance']['source_support_details_sha256']==data['roots']['detail_sha256']]
 bindings.append(sha(rt/data['complete']['detail_file'])==data['complete']['detail_sha256'])
 for name,digest in data['complete']['source_evidence_sha256'].items():bindings.append(sha(rt/name)==digest)
 for name,info in data['dense']['artifacts'].items():bindings.append((d/name).exists() and sha(d/name)==info['sha256'])
 report=evaluate(**data,bindings=all(bindings))
 fixtures=[o/'qa-regression.json',r/'dense-regression-summary.json',r/'root_tests/root_controls_report.json']
 report['checks']['all_synthetic_gate_regressions_pass']=all(p.exists() and read(p)['passed'] for p in fixtures)
 report['author_qualified_evidence_passed'] &= report['checks']['all_synthetic_gate_regressions_pass']
 report['stl_sha256']=stlsha;report['evidence_sha256']={k:sha(v) for k,v in paths.items()}
 controls=[]
 if report['author_qualified_evidence_passed']:
  bad=copy.deepcopy(data);bad['detail']['component_records'].pop();q=evaluate(**bad,bindings=True);controls.append({'case':'unlinked_failed_polygon','must_reject':True,'rejected':not q['author_qualified_evidence_passed']})
  bad=copy.deepcopy(data);bad['roots']['passed']=False;q=evaluate(**bad,bindings=True);controls.append({'case':'failed_root_certificate','must_reject':True,'rejected':not q['author_qualified_evidence_passed']})
 report['negative_controls']=controls;report['negative_controls_passed']=len(controls)==2 and all(c['rejected'] for c in controls);report['author_qualified_evidence_passed'] &= report['negative_controls_passed']
 (o/'qa-author-qualified.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report['author_qualified_evidence_passed']
if __name__=='__main__':raise SystemExit(0 if main() else 1)
