"""Preserve strict warning evidence by actual spatial family; no exception authorization."""
from pathlib import Path
import json,hashlib
R=Path(__file__).parent
c=json.loads((R/'component-detail.json').read_text());b=json.loads((R/'corner-backing.json').read_text());s=json.loads((R/'surface-chords.json').read_text());sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
assert c['stl_sha256']==b['stl_sha256']==s['stl_sha256']==sha
warnings=[q for q in c['original_component_checks']if q['opening_loss_fraction']>.01];groups={}
for q in warnings:
 x0,y0,x1,y1=q['bounds'];x=(x0+x1)/2;y=(y0+y1)/2
 key=('corner_lantern_'+('east'if x>0 else'west')+'_'+('rear'if y>0 else'front')) if abs(x)>15 else 'central_steel_crown'
 groups.setdefault(key,[]).append(q)
families=[]
for name,rows in groups.items():
 families.append({'family':name,'warning_polygons':len(rows),'z_range_mm':[min(q['z_mm']for q in rows),max(q['z_mm']for q in rows)],'maximum_individual_loss_fraction':max(q['opening_loss_fraction']for q in rows),'maximum_loss_outside_0p41mm_vertex_disks_mm2':max(q['loss_outside_0p41_vertex_mm2']for q in rows),'all_eroded_and_opened_single':all(q['eroded_components']==q['opened_components']==1 for q in rows),'section_bbox_is_not_wall_thickness':True,'rows':rows})
report={'stl_sha256':sha,'strict_surface_passed':s['passed'],'strict_individual_polygon_passed':c['passed'],'exception_status':'pending independent review; not approved','families':families,'all_original_short_chord_samples':b['samples'],'short_chord_count':b['count'],'minimum_continuous_bisector_first_exit_mm':b['minimum_continuous_bisector_first_exit_mm'],'corner_checks':b['checks'],'checks':{'all_328_warning_polygons_accounted':sum(q['warning_polygons']for q in families)==len(warnings)==328,'all_83_short_chords_preserved':len(b['samples'])==s['under_0p8mm_count']==83,'all_evidence_same_original_sha':True},'limits':'Rotated section bounds and inward-bisector finite rays are not true global minimum wall thickness. Original short first-normal chords and material/air checks remain present. No strict warning is silently passed.'}
assert all(report['checks'].values());(R/'warning-families.json').write_text(json.dumps(report,indent=2));print([(q['family'],q['warning_polygons'])for q in families])
