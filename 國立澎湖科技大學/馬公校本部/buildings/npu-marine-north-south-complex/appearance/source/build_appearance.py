"""Repackage unchanged STL meshes as editable, surface-colored core 3MF.

Standard-library only. Run from any directory: python appearance/source/build_appearance.py
No geometry generator, remeshing, source photos, machine profile or G-code involved.
Edit ../palette.json and rerun; then regenerate previews with render_appearance.py.
"""
from pathlib import Path
import collections,hashlib,json,math,struct,zipfile,xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',CORE)
TAG=lambda name:'{'+CORE+'}'+name
def sub(parent,node,**attrs):return ET.SubElement(parent,TAG(node),{k:str(v) for k,v in attrs.items()})
def read_stl(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n
    vertices=[];faces=[];lookup={}
    for i in range(n):
        xyz=struct.unpack_from('<9f',data,96+50*i);face=[]
        for j in range(0,9,3):
            point=xyz[j:j+3];assert all(math.isfinite(x) for x in point)
            if point not in lookup:lookup[point]=len(vertices);vertices.append(point)
            face.append(lookup[point])
        faces.append(face)
    return vertices,faces
def world_point(v,T):return [sum(T[i][j]*v[j] for j in range(3))+T[i][3] for i in range(3)]
def select_colors(vertices,faces,part,regions):
    indices=[];roles=[]
    relevant=[r for r in regions if r['part']==part['id']]
    for face in faces:
        v=world_point([sum(vertices[i][j] for i in face)/3 for j in range(3)],part['assembly_transform'])
        index=0;role='default surface; unseen roofs/joins remain approximate'
        for r in relevant:
            a,b=r['bounds_mm']
            if all(a[j]-1e-4<=v[j]<=b[j]+1e-4 for j in range(3)):
                index={'slate':1,'ochre':3,'terracotta':4}[r['color']]
                if 'stair tower glazed' in r['reason']:index=2
                role=r['reason']
        indices.append(index);roles.append(role)
    return indices,roles
def model_root(title,palette):
    root=ET.Element(TAG('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
    sub(root,'metadata',name='Title').text=title
    sub(root,'metadata',name='Application').text='NPU geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Approximate undated-photo appearance; physical print and fit untested.'
    res=sub(root,'resources');mats=sub(res,'basematerials',id=20)
    for p in palette:sub(mats,'base',name=p['id'],displaycolor=p['srgb']+'FF')
    return root,res
def add_mesh(res,oid,name,vertices,faces,colors):
    obj=sub(res,'object',id=oid,type='model',name=name,pid=20,pindex=0)
    mesh=sub(obj,'mesh');vs=sub(mesh,'vertices');ts=sub(mesh,'triangles')
    for v in vertices:sub(vs,'vertex',**{k:format(x,'.17g') for k,x in zip(('x','y','z'),v)})
    for f,c in zip(faces,colors):sub(ts,'triangle',v1=f[0],v2=f[1],v3=f[2],pid=20,p1=c,p2=c,p3=c)
def matrix_string(T):
    # 3MF's row-vector convention is the transpose of assembly.json's column-vector convention.
    return ' '.join(format(T[i][j],'.17g') for j in range(4) for i in range(3))
CONTENT_TYPES='''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
RELS='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
def write_zip(path,root):
    files={'[Content_Types].xml':CONTENT_TYPES.encode(),'_rels/.rels':RELS.encode(),'3D/3dmodel.model':ET.tostring(root,encoding='utf8',xml_declaration=True)}
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in files.items():
            item=zipfile.ZipInfo(name,(2026,10,19,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
            z.writestr(item,data)
def main():
    assembly=json.loads((ROOT/'assembly.json').read_text());palette=json.loads((OUT/'palette.json').read_text())['materials']
    (OUT/'parts').mkdir(parents=True,exist_ok=True);(OUT/'qa').mkdir(exist_ok=True)
    root,res=model_root('NPU marine complex ASSEMBLED appearance master - do not print assembled',palette)
    prototypes={};records={}
    for p in assembly['parts']:
        path=p['stl']
        if path in prototypes:continue
        vertices,faces=read_stl(ROOT/path);colors,roles=select_colors(vertices,faces,p,assembly['color_regions'])
        oid=len(prototypes)+1;prototypes[path]=oid;name=Path(path).stem
        add_mesh(res,oid,name,vertices,faces,colors)
        single,resources=model_root('NPU '+name+' - native separate-part orientation, surface colors only',palette)
        add_mesh(resources,oid,name,vertices,faces,colors);sub(sub(single,'build'),'item',objectid=oid)
        write_zip(OUT/'parts'/(name+'.3mf'),single)
        records[name]={'object_id':oid,'source_stl':path,'source_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles))}
    parent=sub(res,'object',id=100,type='model',name='NPU ten-piece assembled APPEARANCE - not a print layout')
    components=sub(parent,'components')
    for p in assembly['parts']:sub(components,'component',objectid=prototypes[p['stl']],transform=matrix_string(p['assembly_transform']))
    sub(sub(root,'build'),'item',objectid=100)
    write_zip(OUT/'npu-appearance-ASSEMBLED.3mf',root)
    manifest={'base_commit':'338bd45fa1a1437798f5406648e6a5ffbb443ba2','units':'millimeter','mesh_resources':8,'physical_instances':10,'palette_entries':len(palette),'color_limit':None,'geometry_policy':'Original float32 STL vertex values and triangle order preserved exactly; only material identities and assembly packaging added.','printer_mapping':None,'core_display_colors_are_not_print_color_guarantees':True,'color_regions_are_surfaces_not_closed_color_volumes':True,'original_STLs_scene_and_raw_QA_untouched':True,'source_region_count':len(assembly['color_regions']),'parts':records,'assembly':assembly['parts']}
    (OUT/'face-materials.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Created one assembled exchange and eight native-orientation part 3MF files; no printer settings.')
if __name__=='__main__':main()
