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
    sub(root,'metadata',name='Application').text='CES geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photograph-informed daylight-neutral facade and glass appearance on unchanged chapel model; unseen surfaces neutral, physical print untested.'
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
    px=x/.248+485;py=320-y/.248;h=(z-1.6)/2
    index=0;role='unverified neutral: hidden/rear/roof/cross or unclassified surface'
    # The rectangular display base has no real-world material claim.
    if z<=1.60002:return 5,'display base, nonarchitectural neutral'
    # Source photo1 establishes the gray south-facing chapel/wing envelope.
    # Photo4 establishes west facade material boundaries only, not daylight hue.
    west=px<242 and 203<=py<=325 and normal[0]<-.65
    tower=202<=px<=288 and 325<=py<=405 and (normal[0]<-.65 or normal[1]<-.65)
    south=310<=px<=550 and 364.9<=py<=408 and normal[1]<-.8
    wing=550<=px<=737 and 391.9<=py<=403 and normal[1]<-.8
    stair_wall=543<=px<=550 and 367<=py<=432 and abs(normal[0])>.9
    if abs(normal[2])<.15 and (west or tower or south or wing or stair_wall):
        index=1;role='visible gray faux-concrete envelope; daylight approximate, coating assignment not laboratory identification'
    # Preserve existing thin tower cross as neutral. Night light is not pigment.
    if 209<=px<=231 and 399<=py<=413 and h>17.7:
        index=0;role='tower cross: neutral finish unconfirmed; no emitted-light material'
    # West curtain wall: exact original oblique recess plane and fused frames.
    vx,vy=17.,80.;ln=math.hypot(vx,vy);nx,ny=-vy/ln,vx/ln
    t=((px-218)*vx+(py-245)*vy)/(ln*ln);depth=(px-218)*nx+(py-245)*ny
    in_glass_height=(.45<h<3.0 or 3.45<h<14.3)
    if 0<t<1 and -.151<depth<-.149 and .4<h<14.4:
        index=3;role='visible west curtain-wall existing fused frame front, approximate gray metal'
    if 0<t<1 and -1.199<depth<-.151 and .45<h<14.3:
        index=3;role='existing west frame sides, same approximate frame material'
    if 0<t<1 and abs(depth+1.2)<.0001 and in_glass_height:
        index=2;role='existing west glazing backing, neutral dark gray-blue proxy; night hue excluded'
    # Daylight photo1 shows the south ground-floor glazed strip. Only backing
    # planes receive glass, not whole voids or their shadows.
    if 579<px<710 and .6<h<3.8 and abs(py-392)<.0001 and normal[1]<-.9:
        index=2;role='visible south low-wing existing glazing backing'
    if 579<px<710 and .5<h<3.9 and 392.0001<py<=401.0001:
        index=3;role='visible south low-wing existing frame surfaces'
    # Small recessed panes within the deep south passage: back plane only.
    if 311<px<546 and 5.45<h<6.4 and abs(py-364)<.0001 and normal[1]<-.9:
        index=2;role='south passage existing small recessed panes; surrounding passage left geometry-shadowed'
    if 310<px<551 and .65<h<2.65 and abs(py-369)<.0001 and normal[1]<-.9:
        index=2;role='south main-body existing recessed ground-floor panes'
    if normal[2]>.8 and ((py>402 and 310<px<550 and h<5.1) or (abs(h-.22)<.0001 and py>402)):
        index=4;role='visible south platform and stair treads, approximate neutral gray'
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0cb993bbdbb9d3bdb84bd31f8b8da3a66b60263da47efb821e2989ff4760fade'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('CES Trinity chapel - editable appearance surface colors',palette)
    add_mesh(res,1,'CES original 3576 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'ces-appearance.3mf',root)
    report={'base_commit':'3a7c89b32805babd718376a006fa31a656476e8e','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','dark_passage':'shadow from original recessed geometry, not a claim of black paint','night_lighting':'not used as pigment color; cross remains neutral'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
