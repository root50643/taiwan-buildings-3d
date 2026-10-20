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
    sub(root,'metadata',name='Application').text='DILA geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed visible concrete, lower gym glazing and existing rail/frame surfaces on unchanged DILA Yangsheng Hall model; unseen surfaces neutral, physical print untested.'
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
    # Invert the ORIGINAL generator's plan-pixel coordinate system; not a new
    # measurement. Geometric source precision and original STL remain unchanged.
    P=.0603*1.7
    vv=[(v[0]/P+550,850-v[1]/P,(v[2]-1.6)/1.7) for v in vs]
    x,y,h=[sum(v[j] for v in vv)/3 for j in range(3)]
    a=[vs[1][j]-vs[0][j] for j in range(3)];b=[vs[2][j]-vs[0][j] for j in range(3)]
    n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    length=math.sqrt(sum(t*t for t in n));n=[t/length for t in n]
    def plane(axis,value):return all(abs(v[axis]-value)<.002 for v in vv)
    def between(axis,low,high):return all(low-.002<=v[axis]<=high+.002 for v in vv)
    def box(x0,y0,x1,y1,lo,hi):return between(0,x0,x1) and between(1,y0,y1) and between(2,lo,hi)
    if max(v[2] for v in vs)<=1.60001:return 4,'nonarchitectural display base'
    index=0;role='unverified west gym/east or rear elevation,roof,bridge or unclassified surface: neutral'
    # Photo-facing gym front and the single solid projecting-box face. The
    # five western boxes/returns are NOT assigned the photograph's front color.
    if n[1]<-.9 and (plane(1,1000) or plane(1,1005) or plane(1,1040)) and between(0,220,650):
        index=1;role='visible gym front concrete and south box solid front; plain untextured gray'
    # Only the existing six backed lower front glazing bays, not dark-painted walls.
    for aa,bb in [(280,380),(402,503),(525,625)]:
        for lo,hi in [(4.65,7.5),(8.8,11.8)]:
            if box(aa,988,bb,1008,lo,hi):
                index=1;role='visible lower gym window reveals remain concrete'
                if plane(1,990) and n[1]<-.9:index=2;role='original lower gym recess backing: opaque dark glazing proxy'
            for cx in [aa+15+(bb-aa-30)*i/3 for i in range(4)]:
                if box(cx-4,988,cx+4,995,lo,hi):
                    index=3;role='existing thickened front glazing mullion: gray metal proxy'
    # Long-block circulation face and south deep frame stay concrete EVEN IN
    # SHADOW. No shaded recess is converted into a black solid or glass wall.
    if box(687,395,746,1380,3.9,26.7) and n[2]<.1:
        index=1;role='visible long-block corridor piers/reveals/soffits: same concrete gray in shade'
    if box(687,1302,895,1380,3.9,26.7) and n[2]<.1:
        index=1;role='visible south long-block frame/recess/soffits: same concrete gray in shade'
    for lo,hi in zip([0,4.1,8.6,13.3,17.9],[4.1,8.6,13.3,17.9,22.7]):
        end=1330 if lo<13 else 1380
        bays=[395,480,596,718,838,958,1100,1223,1344,1380]
        for aa,bb in zip(bays[:-1],bays[1:]):
            bb=min(bb,end)
            if aa>=end or bb-aa<35:continue
            if box(688,aa+6,697,bb-6,4+lo+.45,4+lo+1.05):
                index=3;role='existing simplified low corridor rail band: gray metal proxy, not new balusters'
    for floor,rail0,rail1 in [(13,13.55,14.05),(18.15,18.65,19.15)]:
        if box(747,1368,831,1377,4+rail0,4+rail1) or box(784,1367,794,1377,4+floor-.1,4+rail0+.2):
            index=3;role='existing south frame inset rail top/post: gray metal proxy; original printable thickening retained'
    # Visible arrival stairs and bounded flanks; no grass/other campus geometry.
    if box(205,1098,700,1522,-.05,6.5) and n[2]>-.9:
        index=1;role='visible south steps and retaining flanks: concrete proxy on original grade simplification'
    # Explicitly exclude the unobserved north end cap; corridor-side bounds
    # alone would otherwise include twelve triangles on that outer end wall.
    if plane(1,395) and n[1]>.9:return 0,'unseen north outer end wall: neutral'
    if plane(0,895) and n[0]>.9:return 0,'unseen east outer wall: neutral'
    return index,role
def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='6911fef40511720dfc947c740e96094c3d993fdba473bc3369af1914b850eb7f'
    vertices,faces=read_stl(ROOT/'model.stl');palette=json.loads((OUT/'palette.json').read_text())['materials']
    choices=[classify([vertices[i] for i in f]) for f in faces];colors=[v[0] for v in choices];roles=[v[1] for v in choices]
    root,res=model_root('DILA Yangsheng Hall - editable appearance surface colors',palette)
    add_mesh(res,1,'DILA original 4276 triangles',vertices,faces,colors);sub(sub(root,'build'),'item',objectid=1)
    write_zip(OUT/'yangsheng-appearance.3mf',root)
    report={'base_commit':'2249681ba2bf2fe00181c90183138a614f9974b7','source_stl':'../model.stl','source_sha256':hashlib.sha256(raw).hexdigest(),'units':'millimeter','vertices':len(vertices),'triangles':len(faces),'face_material_indices':colors,'material_face_counts':{palette[k]['id']:v for k,v in sorted(collections.Counter(colors).items())},'role_face_counts':dict(collections.Counter(roles)),'geometry_policy':'Exact original float32 STL triangles and order, no remesh/repair/addition; surface properties only.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unknown_backside':'neutral, no new details','front_scope':'visible south-facing gym/long-block frame and long-block circulation face only; model coordinates are source mapping, not new geographic measurements','roof':'roof and unseen rear/east/gym-west surfaces neutral; no green roofs or brown rails from other campus buildings'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='face_material_indices'},ensure_ascii=False))
if __name__=='__main__':main()
