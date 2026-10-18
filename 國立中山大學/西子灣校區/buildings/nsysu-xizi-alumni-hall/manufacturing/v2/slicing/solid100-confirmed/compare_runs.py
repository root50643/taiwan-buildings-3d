"""Compare untouched exploratory and conservative actual G-code footers."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent


def run(folder):
    rows=[]
    for p in sorted(folder.glob('0[1-6]-*/geometry-review-NOT-MACHINE-READY.gcode')):
        text=p.read_text(encoding='utf-8-sig')
        mm=float(re.search(r'^; filament used \[mm\] = ([\d.]+)$',text,re.M).group(1))
        cm3=float(re.search(r'^; filament used \[cm3\] = ([\d.]+)$',text,re.M).group(1))
        raw=re.search(r'^; estimated printing time \(normal mode\) = (.+)$',text,re.M).group(1)
        seconds=sum(int(n)*{'d':86400,'h':3600,'m':60,'s':1}[unit] for n,unit in re.findall(r'(\d+)([dhms])',raw))
        rows.append({'id':p.parent.name,'estimated_filament_mm':mm,'estimated_filament_cm3':cm3,
            'estimated_normal_time_text':raw,'estimated_normal_seconds':seconds})
    totalmm=sum(r['estimated_filament_mm'] for r in rows)
    totalcm=sum(r['estimated_filament_cm3'] for r in rows)
    totalsec=sum(r['estimated_normal_seconds'] for r in rows)
    return {'parts':rows,'total_filament_mm':totalmm,'total_filament_m':totalmm/1000,
        'total_filament_cm3':totalcm,'total_normal_seconds':totalsec,
        'total_normal_time_text':f'{totalsec//3600}h {(totalsec%3600)//60}m {totalsec%60}s'}


a=run(ROOT.parent/'slicer-review-staging');b=run(ROOT)
report={'exploratory_15percent_gyroid':a,'conservative_100percent_rectilinear':b,
    'solid_to_exploratory_filament_ratio':b['total_filament_mm']/a['total_filament_mm'],
    'solid_to_exploratory_time_ratio':b['total_normal_seconds']/a['total_normal_seconds'],
    'interpretation':'Both are actual slices of the same fixed six STL files; 15% exploratory run is retained as an alternative, not classified as failure. Time and material are slicer estimates for generic review settings, not physical print observations. Filament density was unspecified; g=0 is unavailable weight, not zero material.'}
(ROOT/'exploratory-vs-solid-estimates.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
