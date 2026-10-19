"""Write deterministic core/component and Prusa-specific multipart 3MF candidates.

Display colors and Prusa volume tool assignments are separate data. The generic
core file does not promise slicer-specific tool mapping. No machine G-code.
"""
from pathlib import Path
import hashlib, json, zipfile, xml.etree.ElementTree as ET
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64, OpType

CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
NS={'m':CORE}
ET.register_namespace('',CORE)
HEX={1:'#D8D6CF',2:'#A96754',3:'#566166',4:'#248E91'}
def tag(n):return '{'+CORE+'}'+n
def xml(element):return ET.tostring(element,encoding='utf-8',xml_declaration=True)
def element(parent,node_name,**attrs):return ET.SubElement(parent,tag(node_name),{k:str(v) for k,v in attrs.items()})
def model_root(native=False):
    r=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
    element(r,'metadata',name='Application').text='A1 geometry-preserving four-tool candidate builder'
    element(r,'metadata',name='Title').text='NUU Bajia A1 approximate four-tool color candidate'
    if native:
        r.set('xmlns:slic3rpe','http://schemas.slic3r.org/3mf/2017/06')
        element(r,'metadata',name='slic3rpe:Version3mf').text='1'
    return r,element(r,'resources')
def palette(resources):
    mats=element(resources,'basematerials',id=20)
    for tool in range(1,5):element(mats,'base',name='Logical tool '+str(tool),displaycolor=HEX[tool]+'FF')
def mesh_arrays(shape):
    m=shape.to_mesh64()
    return np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts,dtype=np.int64)
def add_mesh(obj,vertices,faces,tools):
    m=element(obj,'mesh');vs=element(m,'vertices');ts=element(m,'triangles')
    for v in vertices:element(vs,'vertex',**{k:format(float(x),'.17g') for k,x in zip(('x','y','z'),v)})
    for f,t in zip(faces,tools):element(ts,'triangle',v1=int(f[0]),v2=int(f[1]),v3=int(f[2]),pid=20,p1=int(t)-1)
def zip_write(path,files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in files.items():
            item=zipfile.ZipInfo(name,date_time=(2026,10,19,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(item,data.encode('utf8') if isinstance(data,str) else data)
CONTENT_TYPES='''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="text/plain"/></Types>'''
RELS='''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
def base_files(root):return {'[Content_Types].xml':CONTENT_TYPES,'_rels/.rels':RELS,'3D/3dmodel.model':xml(root)}
def reference_config():
    return '''# File-import reference only. Not a real printer profile. Do not print from this.
# Four physical tools; offsets, nozzle/filament diameters and bed are placeholders.
printer_technology = FFF
nozzle_diameter = 0.4,0.4,0.4,0.4
single_extruder_multi_material = 0
extruder_offset = 0x0,0x0,0x0,0x0
extruder_colour = #D8D6CF;#A96754;#566166;#248E91
filament_colour = #D8D6CF;#A96754;#566166;#248E91
filament_diameter = 1.75,1.75,1.75,1.75
bed_shape = -80x-80,80x-80,80x80,-80x80
max_print_height = 100
layer_height = 0.2
first_layer_height = 0.2
support_material = 0
printer_model = GENERIC_4_TOOL_FILE_CHECK_ONLY
printer_variant = NOT_A_MACHINE_PROFILE
printer_notes = Import and tool-assignment reference only. No machine compatibility or print validation.
'''
def to_manifold(v,f):return Manifold(Mesh64(np.asarray(v,dtype=np.float64),np.asarray(f,dtype=np.uint64)))
def write_four_group_native(path,groups):
    """Union equal-tool regions for a simpler print file; retain the fine edit file."""
    root,res=model_root(native=True);palette(res)
    obj=element(res,'object',id=1,type='model',name='A1_four_tool_PRINT',pid=20,pindex=0)
    vertices=[];faces=[];tools=[];ranges=[]
    for tool,(name,s) in enumerate(groups.items(),1):
        v,f=mesh_arrays(s);first=len(faces);offset=len(vertices)
        vertices.extend(v);faces.extend(f+offset);tools.extend([tool]*len(f));ranges.append((name,first,len(faces)-1,tool))
    add_mesh(obj,vertices,faces,tools);element(element(root,'build'),'item',objectid=1)
    cfg=ET.Element('config');oc=ET.SubElement(cfg,'object',id='1',instances_count='1')
    ET.SubElement(oc,'metadata',type='object',key='name',value='A1_four_tool_PRINT')
    for name,first,last,tool in ranges:
        volume=ET.SubElement(oc,'volume',firstid=str(first),lastid=str(last))
        ET.SubElement(volume,'metadata',type='volume',key='name',value=name)
        ET.SubElement(volume,'metadata',type='volume',key='extruder',value=str(tool))
    files=base_files(root);files['Metadata/Slic3r_PE_model.config']=xml(cfg)
    files['Metadata/Slic3r_PE.config']='; Generic file-check settings, not a machine print profile\n'+''.join('; '+line+'\n' for line in reference_config().splitlines() if line and not line.startswith('#'))
    zip_write(path,files)
def validate_component_3mf(path,mother):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP CRC error')
        root=ET.fromstring(z.read('3D/3dmodel.model'))
    if root.get('unit')!='millimeter':raise RuntimeError('Missing explicit mm unit')
    shapes=[];records={}
    for o in root.findall('m:resources/m:object',NS):
        m=o.find('m:mesh',NS)
        if m is None:continue
        v=np.asarray([[float(q.get(k)) for k in ('x','y','z')] for q in m.findall('m:vertices/m:vertex',NS)])
        f=np.asarray([[int(q.get(k)) for k in ('v1','v2','v3')] for q in m.findall('m:triangles/m:triangle',NS)],dtype=np.uint64)
        s=to_manifold(v,f);t=trimesh.Trimesh(v,f,process=False);comps=s.decompose()
        if s.status().name!='NoError' or not t.is_watertight or not t.is_winding_consistent or any(c.volume()<=0 for c in comps):raise RuntimeError('Invalid closed part '+o.get('name',''))
        records[o.get('name')]={'object_id':int(o.get('id')),'triangles':len(f),'components':len(comps),'watertight':True,'winding_consistent':True,'all_component_volumes_positive':True,'volume_mm3':s.volume(),'bounds_mm':t.bounds.tolist()}
        shapes.append(s)
    pairs={}
    for i,a in enumerate(shapes):
        for j,b in enumerate(shapes[i+1:],i+1):pairs[f'{i+1}/{j+1}']=(a^b).volume()
    u=Manifold.batch_boolean(shapes,OpType.Add)
    return {'unit':'millimeter','build_items':len(root.findall('m:build/m:item',NS)),'parts':records,'pairwise_overlap_mm3':pairs,'union_missing_mm3':(mother-u).volume(),'union_extra_mm3':(u-mother).volume(),'volume_sum_error_mm3':sum(s.volume() for s in shapes)-mother.volume(),'union_bounds_mm':trimesh.Trimesh(*mesh_arrays(u),process=False).bounds.tolist(),'method':'Double-precision Manifold numerical CSG; values near zero are floating-point residuals, not an exact rational proof.'}
def write_outputs(out,fine,toolmap,groups,mother,report,role_counts):
    out=Path(out);out.mkdir(exist_ok=True);(out/'parts').mkdir(exist_ok=True);(out/'qa').mkdir(exist_ok=True)
    config=reference_config();(out/'generic-four-tool-REFERENCE.ini').write_text(config,encoding='utf8')
    manifest={'source_stl_sha256':report['source_sha256'],'source_main_commit':'4923f28803b51be6da8c4017f412be9592719c14','source_stl_unchanged':True,'coordinate_unit':'millimeter','original_coordinates_retained':True,'print_tools':{str(k):{'approximate_srgb':v,'physical_printer_mapping':'unassigned; unknown four-nozzle machine'} for k,v in HEX.items()},'fine_regions':{},'selector_role_counts':role_counts,'note':'Semantic fine regions remain separately editable; multiple regions share one of four logical tools. Components are for simultaneous co-printing, not separate bed-laid assembly.'}
    for i,(name,s) in enumerate(fine.items(),1):manifest['fine_regions'][name]={'object_id':i,'logical_tool':toolmap[name],'triangles':s.num_tri(),'volume_mm3':s.volume(),'approximate_srgb':HEX[toolmap[name]]}
    # Generic core exchange: eight closed fine meshes, one assembly instance.
    root,res=model_root();palette(res)
    for i,(name,s) in enumerate(fine.items(),1):
        v,f=mesh_arrays(s);obj=element(res,'object',id=i,type='model',name=name,pid=20,pindex=toolmap[name]-1)
        add_mesh(obj,v,f,[toolmap[name]]*len(f))
    parent=element(res,'object',id=10,type='model',name='A1_single_multipart_assembly');cs=element(parent,'components')
    for i in range(1,len(fine)+1):element(cs,'component',objectid=i)
    element(element(root,'build'),'item',objectid=10)
    core=out/'a1-four-tool-core.3mf';zip_write(core,base_files(root))
    # Native Prusa-specific model-volume metadata, matching documented 2.9.6 storage.
    root,res=model_root(native=True);palette(res)
    obj=element(res,'object',id=1,type='model',name='A1_four_tool_reference',pid=20,pindex=0)
    vertices=[];faces=[];tools=[];ranges=[]
    for name,s in fine.items():
        v,f=mesh_arrays(s);start=len(faces);offset=len(vertices)
        vertices.extend(v);faces.extend(f+offset);tools.extend([toolmap[name]]*len(f));ranges.append((name,start,len(faces)-1,toolmap[name]))
    add_mesh(obj,vertices,faces,tools);element(element(root,'build'),'item',objectid=1)
    cfg=ET.Element('config');oc=ET.SubElement(cfg,'object',id='1',instances_count='1')
    ET.SubElement(oc,'metadata',type='object',key='name',value='A1_four_tool_reference')
    for name,first,last,tool in ranges:
        volume=ET.SubElement(oc,'volume',firstid=str(first),lastid=str(last))
        ET.SubElement(volume,'metadata',type='volume',key='name',value=name)
        ET.SubElement(volume,'metadata',type='volume',key='extruder',value=str(tool))
    files=base_files(root);files['Metadata/Slic3r_PE_model.config']=xml(cfg)
    files['Metadata/Slic3r_PE.config']='; Generic file-check settings, not a machine print profile\n'+''.join('; '+line+'\n' for line in config.splitlines() if line and not line.startswith('#'))
    native=out/'a1-four-tool-prusaslicer.3mf';zip_write(native,files)
    primary=out/'a1-four-tool-PRINT.3mf';write_four_group_native(primary,groups)
    stl_roundtrip={};sums=[]
    for name,s in groups.items():
        v,f=mesh_arrays(s);path=out/'parts'/(name+'.stl');trimesh.Trimesh(v,f,process=False).export(path)
        m=trimesh.load(path,force='mesh',process=True);sm=to_manifold(m.vertices,m.faces)
        if not m.is_watertight or not m.is_winding_consistent or sm.status().name!='NoError':
            raise RuntimeError('Float32 compatibility STL is not closed: '+name)
        stl_roundtrip[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(m.faces),'watertight':bool(m.is_watertight),'bounds_mm':m.bounds.tolist(),'missing_vs_double_group_mm3':(s-sm).volume(),'extra_vs_double_group_mm3':(sm-s).volume(),'note':'STL stores float32 coordinates and no encoded tool/color metadata; use the 3MF as the primary double-precision model.'};sums.append(sm)
    su=Manifold.batch_boolean(sums,OpType.Add)
    stl_roundtrip['union']={'missing_mm3':(mother-su).volume(),'extra_mm3':(su-mother).volume(),'bounds_mm':trimesh.Trimesh(*mesh_arrays(su),process=False).bounds.tolist()}
    (out/'qa'/'stl-compatibility-quantization.json').write_text(json.dumps(stl_roundtrip,indent=2),encoding='utf8')
    check=validate_component_3mf(core,mother)
    if abs(check['union_missing_mm3'])>1e-6 or abs(check['union_extra_mm3'])>1e-6 or any(abs(v)>1e-6 for v in check['pairwise_overlap_mm3'].values()):raise RuntimeError('3MF union/overlap validation failed')
    manifest['primary_3mf']={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in [primary,core,native]}
    manifest['primary_print_file']=primary.name
    manifest['editable_fine_file']=native.name
    manifest['same_tool_interface_merge']='The PRINT file unions fine regions sharing a tool; the eight-region edit file remains unchanged, including documented f32 interface flags.'
    (out/'color-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    (out/'qa'/'core-reimport-validation.json').write_text(json.dumps(check,indent=2),encoding='utf8')
    (out/'qa'/'partition-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return manifest
