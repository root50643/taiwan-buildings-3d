"""Seven-material appearance core 3MF; preserve original XML geometry verbatim.
Standard-library only. Edit appearance/palette.json, then run this script.
No mesh repair, float32 conversion, slicing, printer profile, or photo embedding.
A color edit here does not automatically recolor the separate Blender scene/previews.
"""
from pathlib import Path
import argparse,json,re,zipfile,xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parents[1]
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
NS={'m':CORE}
ET.register_namespace('',CORE)
def tag(n):return '{'+CORE+'}'+n
def build(source,palette,output):
    p=json.loads(Path(palette).read_text(encoding='utf8'));mats=p['materials'];ids=[m['id'] for m in mats]
    assert len(set(ids))==len(ids) and all(re.fullmatch(r'#[0-9A-Fa-f]{6}',m['srgb']) for m in mats)
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        files={n:z.read(n) for n in z.namelist()};root=ET.fromstring(files['3D/3dmodel.model'])
    assert set(files)=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'} and root.get('unit')=='millimeter'
    res=root.find('m:resources',NS);group=res.find('m:basematerials',NS);pid=group.get('id')
    group.clear();group.set('id',pid)
    for m in mats:ET.SubElement(group,tag('base'),name=m['id'],displaycolor=m['srgb'].upper()+'FF')
    actual=set()
    for obj in res.findall('m:object',NS):
        mesh=obj.find('m:mesh',NS)
        if mesh is None:continue
        name=obj.get('name');index=str(ids.index(p['mesh_materials'][name]));actual.add(name)
        obj.set('pid',pid);obj.set('pindex',index)
        for t in mesh.findall('m:triangles/m:triangle',NS):
            t.set('pid',pid)
            for k in ['p1','p2','p3']:t.set(k,index)
    assert actual==set(p['mesh_materials'])
    for m in root.findall('m:metadata',NS):
        if m.get('name')=='Application':m.text='A1 geometry-preserving appearance exchange builder'
        elif m.get('name')=='Title':m.text='NUU Bajia A1 seven-material approximate appearance master'
    ET.SubElement(root,tag('metadata'),name='Description').text='Editable named display materials; no printer mapping. Existing geometry and quantization limitations retained; not a validated seven-tool print project.'
    # Core child order: metadata precedes resources/build.
    meta=root[-1];root.remove(meta);root.insert(2,meta)
    files['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in files.items():
            entry=zipfile.ZipInfo(name,(2026,10,19,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16
            z.writestr(entry,data)
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=OUT.parent/'multicolor/a1-four-tool-core.3mf');p.add_argument('--palette',type=Path,default=OUT/'palette.json');p.add_argument('--output',type=Path,default=OUT/'a1-appearance-core.3mf');a=p.parse_args()
    print(build(a.source,a.palette,a.output).name)
