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
def model_root(title,palette):
    root=ET.Element(TAG('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
    sub(root,'metadata',name='Title').text=title
    sub(root,'metadata',name='Application').text='WZU geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed front brick bands, green-cyan upper glazing and cream columns on unchanged WZU library model; unseen surfaces neutral, physical print untested.'
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

def classify(vs):
    x,y,z=[sum(v[j] for v in vs)/3 for j in range(3)]
    a=[vs[1][j]-vs[0][j] for j in range(3)];b=[vs[2][j]-vs[0][j] for j in range(3)]
    n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    length=math.sqrt(sum(t*t for t in n));n=[t/length for t in n]
    def plane(axis,value):return all(abs(v[axis]-value)<.0001 for v in vs)
    index=0;role='unverified neutral: side/rear, roof tops and unclassified faces'
    if z<=3.00001:return 7,'nonarchitectural display base'
    # Model front is y-negative, not a geographic direction. No color wrapping
    # onto the unobserved side/rear elevations. Whole original faces only.
    if plane(1,-28.5) and n[1]<-.9 and 52<=z<=95:
        index=1;role='observed front red-brick bands, approximate flat terracotta'
    for level in [55,66,77,88]:
        if level-.0001<=z<=level+4.4001:
            if plane(1,-27.2) and n[1]<-.9:
                index=2;role='observed upper front glazing on existing recessed backing only'
            if -29.6001<=y<=-27.1999 and any(abs(x-c)<=.4501 for c in range(-63,64,6)):
                index=4;role='existing upper front fused mullions, approximate gray metal'
    # Front colonnade, gallery piers/beams and approach steps share a light
    # stone proxy. Circumference of these visible columns is conservatively
    # assigned the same material; no unseen facade inference follows.
    if 3<z<52 and y<=-17.0001:
        index=3;role='visible front column/gallery/step stone, whole component proxy'
    for level in [6,18]:
        if plane(1,-17.1) and n[1]<-.9 and level<=z<=level+7:
            index=5;role='observed lower dark glazing on original recessed back planes'
    if plane(1,-12.5) and n[1]<-.9 and 41<z<53:
        index=3;role='visible recessed mid-level front wall, light stone proxy'
    if plane(1,-11) and n[1]<-.9 and 44<z<50:
        index=5;role='observed mid-level dark glazing on original recessed back planes'
    # Original backed plaque has no lettering. Do not fake gold words/texture.
    if abs(x)<=16.0001 and -31.7501<=y<=-28.5001 and 78<=z<=93:
        index=3;role='observed front plaque frame, original geometry without lettering'
        if plane(1,-31.15) and n[1]<-.9 and abs(x)<14 and 80<z<91:
            index=6;role='observed dark sign backing, lettering omitted as originally modeled'
    if plane(1,-25.5) and n[1]<-.9 and 94.5<z<100:
        index=3;role='front clerestory piers, light stone proxy'
    if plane(1,-24.55) and n[1]<-.9 and 96<z<98.8:
        index=5;role='front clerestory recesses, dark glazing/shadow proxy'
    if plane(1,-31) and n[1]<-.9 and 100<=z<=102:
        index=3;role='observed front roof eave edge, top and rear remain neutral'
    if plane(1,-3) and n[1]<-.9 and 102<z<107.5:
        index=3;role='visible central rooftop block front; cap color not added to unsplit face'
    if abs(x)<3.201 and 7.099<y<8.901 and z>107.1:
        index=3;role='visible existing cross, same light stone proxy on whole component'
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='46fd8857dab8dadca6bc429ef697d4dbfe4a797c0b541347d331480a664c0a3c'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('WZU Library Building - editable appearance surface colors',palette)
    add_mesh(res,1,'WZU original 6898 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'wzu-appearance.3mf',root)
    report={'base_commit':'06a04a9e83882108726abde1e3560a7df38e3012','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','front_scope':'model y-negative only; observed columns/cross use whole-component stone proxy','roof':'tops and unobserved sides remain neutral; no new sign letters or courtyard skylights'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
