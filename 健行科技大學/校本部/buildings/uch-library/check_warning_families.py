from pathlib import Path
import json,hashlib,numpy as np
R=Path(__file__).parent;d=json.loads((R/'component-detail.json').read_text());S=150/52
centres=[('main',x*S,-19.45*S)for x in [-9.65,9.65]]+[('main',x*S,-9.45*S)for x in [-19.45,19.45]]+[('canopy',x*S,y*S)for x in [-23.5,-20,-16,-11.5]for y in [-10.6,-1.6]];groups={'main':[],'canopy':[]}
for row in d['original_component_checks']:
 if row['opening_loss_fraction']<=.01:continue
 b=row['bounds'];x=(b[0]+b[2])/2;y=(b[1]+b[3])/2;family,cx,cy=min(centres,key=lambda q:(q[1]-x)**2+(q[2]-y)**2);assert abs(x-cx)<1e-4 and abs(y-cy)<1e-4
 rect=(b[2]-b[0])*(b[3]-b[1]);assert abs(rect-row['original_area_mm2'])<1e-5;assert row['eroded_components']==1 and row['opened_components']==1;assert row['loss_outside_0p41_vertex_mm2']<1e-9
 groups[family].append(row)
out={}
for family,rows in groups.items():
 peak=max(rows,key=lambda x:x['opening_loss_fraction']);out[family]={'warning_original_polygons':len(rows),'z_range_mm':[min(x['z_mm']for x in rows),max(x['z_mm']for x in rows)],'minimum_original_width_mm':min(x['rotated_bbox_min_width']for x in rows),'peak_loss_fraction':peak['opening_loss_fraction'],'peak_retained_fraction':peak['retained_fraction'],'peak_record':peak,'maximum_loss_outside_true_rectangle_vertex_0p41mm':max(x['loss_outside_0p41_vertex_mm2']for x in rows),'all_records':rows}
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'families':out,'checks':{'all_warnings_match_original_post_centres_and_rectangles':True,'all_erosion_opening_preserve_one_original_polygon':True,'all_over_one_percent_loss_inside_0p41mm_actual_corner_neighbourhood':True},'status':'Specific evidence for independent exception review; strict component-detail remains false/exit1 and no exception is self-approved.'};(R/'warning-families.json').write_text(json.dumps(r,indent=2));print({k:{a:b for a,b in v.items()if a not in ['all_records','peak_record']}for k,v in out.items()})
