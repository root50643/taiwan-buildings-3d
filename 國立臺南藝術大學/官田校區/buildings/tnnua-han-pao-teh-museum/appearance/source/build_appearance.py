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
    sub(root,'metadata',name='Application').text='HAN geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed concrete gray, exterior red projecting box and dark glazing on unchanged museum model; unseen surfaces neutral, physical print untested.'
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
    normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    length=math.sqrt(sum(t*t for t in normal));normal=[t/length for t in normal]
    index=0;role='unverified neutral: flat roof, unobserved flank, reveals and unclassified surfaces'
    if z<=3.00001:return 6,'nonarchitectural display base'
    # The main front, staircase side and reverse balcony facade are photographed.
    if abs(normal[2])<.1 and ((abs(y+45)<.0001 and normal[1]<-.9) or (abs(x-45)<.0001 and normal[0]>.9) or (abs(y-45)<.0001 and normal[1]>.9)):
        index=1;role='observed exposed concrete facade, approximate gray'
    # Existing projecting prism: the large outer face remains concrete. The
    # oblique return and exposed bottom alone are visibly red in article5/6.
    on_red_plane=all(abs(17*(v[0]+8)+21*(v[1]+43))<.003 for v in vs)
    on_concrete_plane=all(abs(10*(v[0]-13)-19*(v[1]+60))<.003 for v in vs)
    if 60-.0001<=z<=94.0001 and y<-44.9999:
        if on_concrete_plane:index=1;role='projecting box observed concrete outer face'
        elif on_red_plane:index=2;role='projecting box observed red oblique side, not interior gallery'
        elif all(abs(v[2]-60)<.0001 for v in vs) and normal[2]<-.9:
            index=2;role='projecting box observed red underside, original geometry only'
    # Glass is assigned to existing recessed back planes, never a painted hole.
    if abs(y+41)<.0001 and -27<x<37 and 3.2<z<14.2 and normal[1]<-.9:
        index=3;role='observed ground-floor glazing backing, dark neutral proxy'
    if abs(y+42)<.0001 and -10.5<x<20.5 and 58<z<93 and normal[1]<-.9:
        index=3;role='observed tall glazing slit backing next to projecting box'
    # Existing ground glazing mullions; actual shadow remains lighting-dependent.
    if -45.2501<=y<-40.9999 and 3<z<15 and any(abs(x-c)<.7001 for c in [-24,-12,0,12,24,36]):
        index=4;role='ground-floor existing fused window frames, approximate gray metal'
    # Existing exterior stair concrete versus thickened rail/stringer details.
    if 45.0001<x<=53.001 and -35<=y<=36 and 20<z<65:
        index=1;role='observed exterior concrete stair, original thickened treads/stringer retained'
    stair_rail_lo=28+(y+34)*41/68
    if x>=52.64 and ((stair_rail_lo-.01<z<stair_rail_lo+1.5) or any(abs(y-c)<.651 and lo<z<lo+7.001 for c,lo in [(-33,22),(-19,30),(-5,38),(9,46),(23,54),(34,62)])):
        index=4;role='photographed exterior stair rail, existing thickened model geometry'
    for level in [12,70]:
        if -.501<x<12.501 and 45<y<=51 and level<z<level+1.801:
            index=1;role='photographed reverse balcony concrete slab'
        elif -.501<x<12.501 and 49.399<y<50.601 and level+1.7<z<level+5.001:
            index=4;role='photographed reverse balcony rail, retained solid simplified model panel'
    if normal[2]>.8 and y<-45 and z<13:
        index=5;role='existing approach steps/platform, approximate paving gray; no new pool'
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='e4f25a2d8c02e58a57a263ee7ac93289e8818c456be86c251a1a26f9e0337e8e'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('HAN Han Pao-Teh Memorial Museum - editable appearance surface colors',palette)
    add_mesh(res,1,'HAN original 1532 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'han-appearance.3mf',root)
    report={'base_commit':'d4737820a2b0714a133f3e530458bafd4f1b037c','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','red_scope':'observed exterior projecting prism return and underside only; no interior reconstruction','roof':'original solid flat roof retained; visible parapet/skylight-slot details not represented or painted in'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
