"""Read actual linear positive-extrusion motions; no printer execution."""
import collections
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

WORK=Path(__file__).resolve().parent
PATH=WORK/'reference-NOT-MACHINE-READY.gcode'
XYZ=[0.,0.,0.]
E=0.
relative_xyz=False
relative_e=False
role='Custom'
layer=-1
roles={}
support_layers=set()
bridge_layers=set()
unknown=[]
config={}
estimates=[]

def item(role):
    return roles.setdefault(role,{'positive_xy_extrusion_segments':0,
        'positive_filament_mm':0.,'xy_path_mm':0.,'min_xyz':[math.inf]*3,
        'max_xyz':[-math.inf]*3,'layer_indices':set()})

for number,line in enumerate(PATH.open(encoding='utf-8-sig'),1):
    line=line.strip()
    if line==';LAYER_CHANGE': layer+=1
    if line.startswith(';TYPE:'): role=line[6:].strip()
    if 'estimated printing time' in line or 'filament used' in line: estimates.append(line)
    setting=re.match(r';\s*([a-z][a-z0-9_]*)\s*=\s*(.*)$',line)
    if setting: config[setting[1]]=setting[2]
    code=line.partition(';')[0].strip()
    if not code: continue
    cmd=code.split()[0].upper()
    vals={m[1].upper():float(m[2]) for m in re.finditer(r'([XYZEF])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)',code)}
    if cmd=='M82': relative_e=False
    elif cmd=='M83': relative_e=True
    elif cmd=='G90': relative_xyz=False
    elif cmd=='G91': relative_xyz=True
    elif cmd=='G92':
        for i,axis in enumerate('XYZ'):
            if axis in vals: XYZ[i]=vals[axis]
        E=vals.get('E',E)
    elif cmd in ('G0','G00','G1','G01'):
        nxt=[XYZ[i]+vals.get(axis,0.) if relative_xyz else vals.get(axis,XYZ[i]) for i,axis in enumerate('XYZ')]
        de=vals.get('E',0.) if relative_e else vals.get('E',E)-E
        if 'E' in vals: E=E+vals['E'] if relative_e else vals['E']
        dist=math.dist(XYZ[:2],nxt[:2])
        if de>1e-7 and dist>1e-7:
            row=item(role)
            row['positive_xy_extrusion_segments']+=1
            row['positive_filament_mm']+=de
            row['xy_path_mm']+=dist
            row['layer_indices'].add(layer)
            for p in (XYZ,nxt):
                for i in range(3):
                    row['min_xyz'][i]=min(row['min_xyz'][i],p[i])
                    row['max_xyz'][i]=max(row['max_xyz'][i],p[i])
            if 'support' in role.lower(): support_layers.add(layer)
            if 'bridge' in role.lower(): bridge_layers.add(layer)
        XYZ=nxt
    elif cmd in ('G2','G02','G3','G03'):
        unknown.append({'line':number,'code':code})

for row in roles.values():
    row['layer_indices']=sorted(row['layer_indices'])
    row['model_coordinate_min_xyz']=[row['min_xyz'][0]-110,row['min_xyz'][1]-110,row['min_xyz'][2]]
    row['model_coordinate_max_xyz']=[row['max_xyz'][0]-110,row['max_xyz'][1]-110,row['max_xyz'][2]]
    row['note']='Bounds are centerlines of actual positive XY extrusion, excluding deposited bead width and hardware effects.'

project={}
with zipfile.ZipFile(WORK/'reference-NOT-MACHINE-READY.3mf') as zf:
    project['members']=zf.namelist()
    model=ET.fromstring(zf.read('3D/3dmodel.model'))
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    project['unit']=model.attrib.get('unit')
    vertices=[[float(v.attrib[a]) for a in ('x','y','z')] for v in model.findall('.//m:vertex',ns)]
    project['mesh_vertex_bounds']=[[min(v[i] for v in vertices) for i in range(3)],
                                    [max(v[i] for v in vertices) for i in range(3)]]
    project['build_items']=[v.attrib for v in model.findall('.//m:build/m:item',ns)]
    for name in zf.namelist():
        if 'config' in name.lower():
            project.setdefault('config_members',[]).append(name)
            text=zf.read(name).decode('utf-8',errors='replace')
            if name.endswith('Slic3r_PE.config'):
                settings={m[1]:m[2] for line in text.splitlines()
                          if (m:=re.match(r';\s*([a-z][a-z0-9_]*)\s*=\s*(.*)$',line))}
                project['selected_settings']={key:settings.get(key) for key in (
                    'layer_height','nozzle_diameter','support_material','support_material_auto',
                    'support_material_buildplate_only','support_material_style',
                    'support_material_threshold','dont_support_bridges','fill_density')}

result={'gcode_sha256':hashlib.sha256(PATH.read_bytes()).hexdigest(),
    'parser':'Tracks G90/G91, M82/M83, G92 and G0/G1; counts positive E only with nonzero XY motion. Roles are actual slicer TYPE comments, not sampled mesh ray flags.',
    'gcode_layer_changes':layer+1,'actual_role_summary':roles,
    'support_layer_count':len(support_layers),'bridge_layer_count':len(bridge_layers),
    'unsupported_arc_commands':unknown,'selected_effective_gcode_config':{
        key:config.get(key) for key in ('layer_height','first_layer_height','nozzle_diameter',
        'perimeter_generator','fill_density','support_material','support_material_auto',
        'support_material_style','support_material_threshold','support_material_buildplate_only',
        'support_material_closing_radius','support_material_with_sheath',
        'support_material_contact_distance','support_material_xy_spacing',
        'support_material_interface_layers','dont_support_bridges')},
    'slicer_estimates_only':estimates,'project_3mf':project,
    'limitations':['Actual support deposition count is not an inaccessible-cavity or removability proof.',
        'Bridge paths are not support material; their anchor and span review remains separate.',
        'Reference G-code has not been sent to a printer. Temperature, firmware, start/end code and clearance are not hardware validated.']}
(WORK/'actual-role-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'roles':{k:{kk:v for kk,v in row.items() if kk not in ('layer_indices','note')} for k,row in roles.items()},
                  'support_layers':len(support_layers),'bridge_layers':len(bridge_layers),
                  'arc_commands':len(unknown),'project':project},ensure_ascii=False,indent=2))
