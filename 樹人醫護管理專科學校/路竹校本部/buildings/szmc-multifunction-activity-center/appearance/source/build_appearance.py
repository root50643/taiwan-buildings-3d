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
    sub(root,'metadata',name='Application').text='SZMC geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Approximate 2017 photograph appearance on unchanged 2016 building model; unseen surfaces neutral, physical print untested.'
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

PX=1.18/22.9
def inside(x,y,poly):
    yes=False
    for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:yes=not yes
    return yes
def classify(vs):
    x,y,z=[sum(v[j] for v in vs)/3 for j in range(3)]
    a=[vs[1][j]-vs[0][j] for j in range(3)];b=[vs[2][j]-vs[0][j] for j in range(3)]
    n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];l=math.sqrt(sum(t*t for t in n));n=[t/l for t in n]
    px=x/PX+2000;py=1400-y/PX;zm=(z-1.6)/1.18
    index=0;role='unverified or neutral display surface'
    # Only already-modeled street/grass-side white folds. Opposite pond-facing
    # facade is deliberately left neutral: the new aerial does not establish it.
    folds=[('x',1020,6.0,-.12,[(680,13.6),(1800,12),(1800,10.8),(1350,6.3),(1100,1),(930,1)]),
      ('y',1990,5.37,.13,[(1255,3),(1390,11.2),(2380,10.5),(2460,1.8),(2340,1.8),(2310,3)]),
      ('y',1980,4.86,.08,[(2890,11),(3310,11.8),(3400,1),(3260,1)]),
      ('x',3250,5.20,0,[(1610,11.65),(2060,11.8),(2060,.8),(1990,.8)])]
    for axis,p,th,sh,poly in folds:
        depth=(x-(p-2000)*PX-sh*z) if axis=='x' else ((1400-p)*PX+sh*z-y)
        if -.0002<=depth<=th+.0002 and inside(py if axis=='x' else px,zm,poly):
            index=1;role='visible-side continuous white folded envelope; approximate'
    def height(v):
        xx=v[0]/PX+2000;yy=1400-v[1]/PX
        return 1.6+1.18*(18-3.5*(xx-890)/1540-4*max(1800-yy,0)/1120)
    if all(abs(v[2]-height(v))<.0002 for v in vs) or (abs(z-22.604)<.0002 and n[2]>.9):
        index=1;role='continuous white main and long-wing roof'
    elif all(-.0002<=height(v)-v[2]<=1.1502 for v in vs) and zm>8 and n[2]<.3:
        index=2;role='roof slab edge/underside gray-white approximation'
    # Existing recess backing planes only: no new pane geometry or facade holes.
    if abs(px-1081.918644)<.02 and n[0]<-.9 and inside(py,zm,[(1300,4.4),(1745,4.4),(1745,10),(1350,6.1),(1300,5.1)]):
        index=3;role='grass-facing recessed glazing'
    if abs(py-2040)<.02 and n[1]<-.9 and ((1615<px<2385 and 6<zm<8.2) or (1300<px<2400 and .55<zm<2.65)):
        index=3;role='field-facing recessed glazing bands'
    if abs(py-1970)<.02 and n[1]<-.9 and inside(px,zm,[(2470,.55),(3220,.55),(3220,1.90),(2990,8.15),(2470,8.15)]):
        index=3;role='right-wing existing recessed glazing'
    if abs(px-1069)<.02 and n[0]<-.9 and 1310<py<1730 and 4.4<zm<10:
        index=4;role='existing grass-side fine frames'
    if abs(py-2049)<.02 and n[1]<-.9 and ((1620<px<2380 and 6<zm<8.2) or (1300<px<1890 and .55<zm<2.65)):
        index=4;role='existing field-side fine frames'
    if abs(py-1979)<.02 and n[1]<-.9 and inside(px,zm,[(2470,.55),(3220,.55),(3220,1.90),(2990,8.15),(2470,8.15)]):
        index=4;role='existing right-wing fine frames'
    if py>2060 and z>1.6002 and n[2]>.8:
        index=5;role='visible-side existing platform and stair tread approximation'
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='a763cee5febe34c80b4bbe36d19dca5fb1b2d9fd65d956aa310a06e5a993e902'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('SZMC 2016 activity center - editable appearance surface colors',palette)
    add_mesh(res,1,'SZMC original 3172 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'szmc-appearance.3mf',root)
    report={'base_commit':'5f60b3fd6b7c3534747ff89cbe51f2293a033ba4','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','dark_passage':'shadow from original recessed geometry, not a claim of black paint'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
