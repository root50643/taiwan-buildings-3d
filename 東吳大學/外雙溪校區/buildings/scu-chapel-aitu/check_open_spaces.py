"""Original STL surface probes for split roofs, low annex, doors and passage."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
from check_root_rays import ray,point,S,BASE
R=Path(__file__).resolve().parent;rows=[]
for name,x,y,z in [('gray_front_flat',-14,-16,12.35),('red_ridge',-14,4,13.4),('red_slope_left',-19,4,12+3.5/8.25*1.4),('red_slope_right',-9,4,12+3.5/8.25*1.4),('aitu_flat',5,-13,11.9),('low_rear_annex',-3,15,4.6),('rear_clear_passage',10,-2,0),('rear_low_retaining_wall',10,-.4,2.4)]:
 o=point(x,y,25);h=ray(o,[0,0,-1]);actual=o[2]-h;assert abs(actual-(BASE+z*S))<.025,(name,actual,BASE+z*S);rows.append({'feature':name,'origin_mm':o,'original_surface_z_mm':actual,'expected_z_mm':BASE+z*S})
doors=[]
for name,x,front,back in [('chapel',-15.2,-22,-20.9),('aitu',14.2,-21,-20.1)]:
 o=point(x,front-1,2);h=ray(o,[0,1,0]);actual=o[1]+h;assert abs(actual-back*S)<.02;doors.append({'feature':name,'origin_mm':o,'actual_backing_y_mm':actual,'recess_from_facade_mm':actual-front*S})
j={'passed':True,'checks':{'north_flat_and_south_shallow_two_slope_roof_distinct':True,'aitu_flat_and_rear_annex_low':True,'rear_passage_clear_to_base_between_wall_and_wing':True,'two_entrances_have_actual_recess':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'roof_and_passage_samples':rows,'entry_samples':doors,'limits':'Specified raw surface probes only. Model roof heights/annex/steps are bounded assumptions, not survey dimensions. Roof ridge has a 1.25mm flat landing for nonvanishing sampled sections; historical ridge detail is not measured.'}
(R/'open-space-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k not in ['roof_and_passage_samples','entry_samples']})
