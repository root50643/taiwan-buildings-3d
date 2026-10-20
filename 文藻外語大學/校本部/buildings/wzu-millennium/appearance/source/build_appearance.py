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
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed front brick, gray belts, dark recesses and three narrow forward roof slopes on unchanged WZU Millennium Hall model; unseen surfaces neutral, physical print untested.'
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
            item=zipfile.ZipInfo(name,(2026,10,20,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
            z.writestr(item,data)

def classify(vs):
    x,y,z=[sum(v[j] for v in vs)/3 for j in range(3)]
    a=[vs[1][j]-vs[0][j] for j in range(3)];b=[vs[2][j]-vs[0][j] for j in range(3)]
    n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    length=math.sqrt(sum(t*t for t in n));n=[t/length for t in n]
    def plane(axis,value):return all(abs(v[axis]-value)<.0001 for v in vs)
    def between(axis,low,high):return all(low-.0001<=v[axis]<=high+.0001 for v in vs)
    if max(v[2] for v in vs)<=3.00001:return 5,'nonarchitectural display base'
    index=0;role='unverified side/rear/roof or unclassified surface: neutral'
    if plane(1,-15.5) and n[1]<-.9:
        index=1;role='observed front main red-brick field, plain color without brick joints'
    # Recesses in the original mesh, not newly filled window openings.
    for level in [8,17,26,35,44,53,62,71]:
        for cx in [-58,-47,-36,-25,12,23,34,45,57]:
            if between(0,cx-2.75,cx+2.75) and between(1,-15.5,-14) and between(2,level,level+4.5):
                index=2;role='existing front window reveals: gray proxy, no new frame geometry'
                if plane(1,-14):index=3;role='existing front recess back: opaque dark glazing/shadow proxy'
    for level in [14,23,32]:
        if between(2,level,level+2.3) and between(1,-16.75,-15.25):
            index=2;role='existing lower front horizontal belt: gray; original narrow width retained'
    # Cylinder front only. Side/rear arc above the original roof remains neutral.
    rr=math.hypot(x+8,y+10)
    if between(1,-20.5001,-10) and z>3 and z<=85.0001 and -18.6<=x<=2.6:
        radial=(n[0]*(x+8)+n[1]*(y+10))/max(rr,1e-6)
        if radial>.85 and n[1]<0 and abs(rr-10)<.03:
            index=1;role='visible rounded bay front red-brick proxy; existing faceting retained'
        for level in [16,27,38,49,60,71]:
            if between(2,level,level+2) and rr>8.9:
                index=2;role='existing visible rounded belt gray proxy; not a measured full gray window band'
            if between(2,level+3,level+7) and rr<10.01 and radial<.5 and n[2]==0:
                index=3;role='original cylindrical pane-mark recess: dark shadow/glazing proxy'
    # The original tower boxes omit the photograph's finer brick/gray transitions.
    # Whole existing front faces use a gray proxy, never a false diagonal boundary.
    if (plane(1,-4.5) and z>=77.3999 and (x<-49 or x>50)) or (plane(1,-3.5) and z>=77):
        if n[1]<-.9:index=2;role='visible roof-tower front: whole-face gray proxy; original box simplification retained'
    # Only original forward slopes of the three narrow caps are photo-supported.
    for cx,cz in [(-58,90),(58,90),(-8,99.8)]:
        if between(0,cx-12.6,cx+12.6) and min(v[2] for v in vs)>=cz-.0001 and n[2]>.1 and n[1]<-.05 and y<9:
            index=4;role='existing narrow tower roof forward slope: terracotta proxy; other slopes neutral'
    # Entry is partly tree-obscured; retain neutral structure, rather than guessing
    # the photograph's orange canopy belongs to this modeled central portico.
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='ba8cec3cadb311a60aad2ea0efd669c761f98a9f73b4df87c5ffbf29009d216a'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('WZU Millennium Hall - editable appearance surface colors',palette)
    add_mesh(res,1,'WZU original 5340 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'millennium-appearance.3mf',root)
    report={'base_commit':'a6e2c25dbfe64cdce1f598dc292b92d60ea233b8','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','front_scope':'model y-negative; original belt widths and tower-box simplifications retained; no invented diagonal material boundaries','roof':'only three existing forward cap slopes terracotta; remaining roof and rear neutral; entry canopy unverified neutral'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
