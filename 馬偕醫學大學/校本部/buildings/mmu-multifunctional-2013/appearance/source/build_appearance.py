"""Repackage unchanged STL meshes as editable, surface-colored core 3MF.

Requires numpy and shapely 2.2+. Run from any directory: python appearance/source/build_appearance.py
Original envelope preserved with conforming surface subdivision for large color regions. No new volumes, photos, printer settings or G-code.
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
    sub(root,'metadata',name='Application').text='MMU geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed downhill brick/white-frame regions and dark glazing; surface-only subdivision of original MMU K 2013 model; unseen surfaces neutral, physical print untested.'
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

import numpy as np
from shapely.geometry import Polygon, box as rect
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
SOURCE_SHA='5b36ea5d35e43d2b6467279a88beb9ee71a582aa977373642fbb92f1a2c693e9'
def local(v):return np.asarray(v,dtype=float)
# The one planar color mask follows the original right end window width.
# It is a photograph-proportional strip, not a measured material-joint survey.
MASKS={'right_end_white_strip':rect(-65.95,21.0,-62.45,37.9)}
SNAP_X=[-65.95,-62.45];SNAP_Z=[21.,37.9]
def plane(t,axis,value):return np.max(np.abs(t[:,axis]-value))<.0001
def normal(t):
    n=np.cross(t[1]-t[0],t[2]-t[0]);return n/np.linalg.norm(n)
def classify(t):
    t=np.asarray(t);x,y,z=t.mean(axis=0);n=normal(t)
    def between(axis,a,b):return np.all((t[:,axis]>=a-.0001)&(t[:,axis]<=b+.0001))
    def box(x0,x1,y0,y1,z0,z1):return between(0,x0,x1) and between(1,y0,y1) and between(2,z0,z1)
    if max(t[:,2])<=3.00001:return 5,'nonarchitectural display base',None
    c=0;role='unseen roof/rear/long side or unclassified surface neutral'
    # y+ is the downhill front in the original model coordinate convention.
    if (plane(t,1,46.5) or plane(t,1,46.4)) and n[1]>.9 and between(0,-69.9,-58.5):return 1,'right end brick front and approximate white window strip','right_end_white_strip'
    if box(-58.6,13,46.1,46.5,3,14.8):c=1;role='existing downhill lower-storey brick wall; same-wall continuation through foliage-obscured parts'
    if box(-59.4,13.8,46.2,47.8,14.8,37.8):c=2;role='existing projected main white frame and reveals'
    if box(-57.3,11.7,46.3,46.8,17,35.4):c=4;role='existing fine main glazing bars, charcoal metal proxy'
    for cx in np.linspace(-57,11.4,6):
        if box(cx-.6,cx+.6,46.2,47,17,35.4):c=2;role='existing broad main glazing structural column, light proxy behind glass'
    if plane(t,1,46.3) and n[1]>.9 and box(-57.3,11.7,46.3,46.3,17,35.4):c=3;role='main long glazing original solid recessed backing'
    if plane(t,1,46.1) and n[1]>.9 and between(2,5,13.8):c=3;role='lower-storey front window solid backing'
    for cx in np.linspace(-50.2,4.6,5):
        for dx in [-3.8,0,3.8]:
            if box(cx+dx-.3,cx+dx+.3,46,46.5,9.6,13.8):c=4;role='existing lower front glazing bars, charcoal metal proxy'
    if box(-65.95,-62.45,45.8,46.5,23.2,36):
        c=2;role='right end existing window reveal, light surround proxy'
        if plane(t,1,45.8) and n[1]>.9:c=3;role='right end two front window backings'
    # The short oblique auditorium edge is seen at photo left. Only that front
    # and its original recesses are assigned, not the long pentagonal sides.
    a=np.array([29.952,35.022]);b=np.array([44.382,45.006]);u=(b-a)/np.linalg.norm(b-a);inside=np.array([u[1],-u[0]]);mid=(a+b)/2
    depth=(t[:,:2]-mid)@inside;along=(t[:,:2]-mid)@u;length=np.linalg.norm(b-a)
    if np.min(depth)>-.0001 and np.max(depth)<5.1001 and np.max(np.abs(along))<=length/2+.0001 and between(2,10,38.2) and abs(n[2])<.99:
        c=2;role='visible short auditorium front and original deep reveals: white proxy'
        if (np.max(np.abs(depth-5.1))<.0001 or np.max(np.abs(depth-3.5))<.0001) and np.dot(n[:2],inside)<-.9:c=3;role='auditorium original oblique tall/small glass backing'
        if np.min(depth)>4.6249 and np.max(depth)<5.2751 and between(2,20.4,35.1):
            c=4;role='existing backed auditorium glazing bars, charcoal metal proxy'
            if np.max(np.abs(depth-5.1))<.0001:c=3;role='auditorium tall glass backing'
    return c,role,None

def subdivide(vertices,faces):
    V=[tuple(v) for v in vertices];F=[];C=[];parents=[];edge_nodes={};edge_lookup={};inside_lookup={};roles=collections.Counter()
    def vertex(uv,src,domain,fi):
        weights=np.linalg.solve(np.vstack((domain.T,np.ones(3))),np.array([uv[0],uv[1],1.]))
        weights[np.abs(weights)<1e-9]=0.;weights[np.abs(weights-1)<1e-9]=1.;weights/=weights.sum();assert weights.min()>-1e-7
        fixed=np.where(weights==1)[0]
        if len(fixed):return faces[fi][int(fixed[0])]
        zeros=np.where(weights==0)[0]
        if len(zeros):
            ids=[j for j in range(3) if j!=zeros[0]];a,b=sorted(faces[fi][j] for j in ids);ib=faces[fi].index(b);t=round(float(weights[ib]),11);key=(a,b,t)
            if key not in edge_lookup:
                edge_lookup[key]=len(V);V.append(tuple((1-t)*np.array(vertices[a])+t*np.array(vertices[b])));edge_nodes.setdefault((a,b),[]).append((t,edge_lookup[key]))
            return edge_lookup[key]
        key=(fi,round(float(uv[0]),10),round(float(uv[1]),10))
        if key not in inside_lookup:inside_lookup[key]=len(V);V.append(tuple(weights@src))
        return inside_lookup[key]
    for fi,f in enumerate(faces):
        src=np.array([vertices[i] for i in f]);c,role,kind=classify(src);roles[role]+=1
        if kind is None:F.append(f);C.append(c);parents.append(fi);continue
        projected=local(src) if kind.startswith('main') else src
        domain=projected[:,[0,2]].copy()
        for row in domain:
            for axis,levels in enumerate([SNAP_X,SNAP_Z]):
                closest=min(levels,key=lambda v:abs(v-row[axis]))
                if abs(closest-row[axis])<1e-4:row[axis]=closest
        polygon=Polygon(domain);assert polygon.is_valid and polygon.area>1e-9
        mask=MASKS[kind];regions=[(polygon.intersection(mask),2),(polygon.difference(mask),1)];area=0
        for geo,ci in regions:
            for tr in constrained_delaunay_triangles(geo).geoms:
                if tr.area<1e-12:continue
                points=list(tr.exterior.coords)[:3];idx=[vertex(p,src,domain,fi) for p in points];tt=np.array([V[i] for i in idx])
                if np.dot(np.cross(tt[1]-tt[0],tt[2]-tt[0]),np.cross(src[1]-src[0],src[2]-src[0]))<0:idx.reverse()
                assert len(set(idx))==3;F.append(idx);C.append(ci);parents.append(fi);area+=tr.area
        assert abs(area-polygon.area)<1e-7
    # Propagate every added original-edge point to its adjacent faces. This
    # prevents T-junctions where a color boundary meets a window reveal/side.
    result=[];colors=[];origins=[]
    for f,c,fi in zip(F,C,parents):
        orig=faces[fi];poly=[]
        for k in range(3):
            i,j=f[k],f[(k+1)%3];poly.append(i);p,q=np.array(V[i]),np.array(V[j]);extra=[]
            for oe in range(3):
                a,b=sorted((orig[oe],orig[(oe+1)%3]));nodes=edge_nodes.get((a,b),[])
                if not nodes:continue
                aa,bb=np.array(vertices[a]),np.array(vertices[b]);d=bb-aa;dd=np.dot(d,d);pi=np.dot(p-aa,d)/dd;pj=np.dot(q-aa,d)/dd
                if np.linalg.norm(aa+pi*d-p)>1e-7 or np.linalg.norm(aa+pj*d-q)>1e-7:continue
                for t,vi in nodes:
                    if min(pi,pj)+1e-9<t<max(pi,pj)-1e-9:extra.append(((t-pi)/(pj-pi),vi))
            poly += [vi for t,vi in sorted(set(extra))]
        if len(poly)==3:result.append(poly);colors.append(c);origins.append(fi)
        else:
            vi=len(V);V.append(tuple(np.mean([V[i] for i in poly],axis=0)))
            for i,j in zip(poly,poly[1:]+poly[:1]):result.append([i,j,vi]);colors.append(c);origins.append(fi)
    return V,result,colors,origins,dict(roles)

def main():
    raw=(ROOT/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    ov,of=read_stl(ROOT/'model.stl');v,f,c,parents,roles=subdivide(ov,of);pal=json.loads((OUT/'palette.json').read_text())['materials']
    r,res=model_root('MMU Multifunctional Center K - 2013 - surface-subdivided appearance',pal);add_mesh(res,1,'Original envelope, conforming color subdivision',v,f,c);sub(sub(r,'build'),'item',objectid=1);write_zip(OUT/'mmu-appearance.3mf',r)
    report={'base_commit':'df04211493ae1118c0c8fd1d03253ef3ad093767','source_stl':'../model.stl','source_sha256':SOURCE_SHA,'original_vertices':len(ov),'original_triangles':len(of),'vertices':len(v),'triangles':len(f),'face_material_indices':c,'original_triangle_for_each_output_face':parents,'material_face_counts':{pal[k]['id']:n for k,n in sorted(collections.Counter(c).items())},'original_role_face_counts':roles,'geometry_policy':'Conforming subdivision of existing triangular surfaces; no new volume or spatial structure. Original STL unchanged, output topology and face order differ.','color_regions':'Downhill right end white window strip follows original window width; visible major colors only, approximate and not surveyed brick courses.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unverified':'unseen long sides, uphill rear and roofs neutral; no extra structures or text'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:x for k,x in report.items() if k not in ['face_material_indices','original_triangle_for_each_output_face']},ensure_ascii=False))
if __name__=='__main__':main()
