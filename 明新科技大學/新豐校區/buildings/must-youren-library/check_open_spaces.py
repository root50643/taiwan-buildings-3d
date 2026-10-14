"""Actual surface rays verify 9 deep glass / 8 shallow solid bays and canopy."""
from pathlib import Path
import json,hashlib,numpy as np
import sys
sys.dont_write_bytecode=True
from check_root_rays import ray,point,S,BASE
R=Path(__file__).resolve().parent
bays=[]
for i,x in enumerate(np.linspace(-17.1,17.1,17)):
 o=point(x+.5,-23,12);hit=ray(o,[0,1,0]);y=o[1]+hit;expected=-21.45 if i%2==0 else -22.30;assert abs(y-expected*S)<.02,(i,y)
 bays.append({'index':i,'type':'deep_glass' if i%2==0 else 'shallow_solid','origin_mm':o,'surface_y_mm':y,'recess_from_arch_front_mm':y+22.38*S})
o=point(.5,-23,2.5);h=ray(o,[0,1,0]);assert abs(o[1]+h-(-20.7*S))<.02
entry={'origin_mm':o,'backing_y_mm':o[1]+h,'recess_from_body_front_mm':o[1]+h+22*S}
o=point(0,-24.3,3);h=ray(o,[0,0,1]);assert abs(o[2]+h-(BASE+5.6*S))<.02
canopy={'origin_mm':o,'underside_z_mm':o[2]+h}
skylight=[]
for x,y in [(0,0),(-5,0),(5,0),(0,-5),(0,5)]:
 o=point(x,y,30);h=ray(o,[0,0,-1]);z=o[2]-h;assert BASE+20.7*S<z<=BASE+23.5*S+.02;skylight.append({'origin_mm':o,'surface_z_mm':z})
j={'passed':True,'checks':{'nine_deep_glazed_bays_eight_shallow_opaque_bays':True,'entry_recess_has_real_depth':True,'canopy_has_clear_under_space':True,'four_pitch_skylight_is_closed':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'alternating_bays':bays,'entry':entry,'canopy':canopy,'skylight':skylight,'limits':'Nominated original STL intersections only. Depths and heights are bounded model assumptions, not building measurements. Internal floor void is not reproduced as a hidden sealed cavity.'}
(R/'open-space-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k not in ['alternating_bays','entry','canopy','skylight']})
