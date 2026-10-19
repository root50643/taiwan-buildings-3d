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
    sub(root,'metadata',name='Application').text='WZU geometry-preserving appearance exchange'
    sub(root,'metadata',name='Description').text='Editable surface material display colors; no printer-tool mapping. Photo-informed major front brick/stone regions, short terracotta porch roofs and dark glazing; surface-only subdivision of original Huayu/Yong-Su model; unseen surfaces neutral, physical print untested.'
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

import numpy as np
from shapely.geometry import Polygon, box as rect
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
SOURCE_SHA='f00727291f2ad83bf84b95f260ab252fa5089c47b2a0d52b6fd8ee97d038382e'
def local(v):
    v=np.asarray(v,dtype=float);r=v.copy();r[...,0]=((v[...,0]-6)+(v[...,1]+10))/math.sqrt(2);r[...,1]=(-(v[...,0]-6)+(v[...,1]+10))/math.sqrt(2);return r
# Major photograph-supported regions only. Approximate coordinates are model
# millimetres, not surveyed brick courses or geographic directions.
STEP=[(-23,62),(-23,65),(-19,65),(-19,68),(-15,68),(-15,71),(-11,71),(-11,74),(-7,74),(-7,77),(-2,77),(-2,85),(6,85),(6,77),(11,77),(11,74),(15,74),(15,71),(19,71),(19,68),(23,68),(23,65),(25,65),(25,62)]
GABLE=Polygon(STEP)
CHAPEL=unary_union([rect(-63,46,-29,54),rect(-52,22,-40,44),rect(-63,3,-29,23.8)])
MASKS={'main_gable':GABLE,'main_window_band':rect(-25,54,25,62),'chapel_front':CHAPEL}
SNAP_X=sorted({p[0] for p in STEP}|{-25,25,-63,-29,-52,-40});SNAP_Z=sorted({p[1] for p in STEP}|{3,22,23.8,44,46,54})
def plane(t,axis,value):return np.max(np.abs(t[:,axis]-value))<.0001
def normal(t):
    n=np.cross(t[1]-t[0],t[2]-t[0]);return n/np.linalg.norm(n)
def classify(t):
    t=np.asarray(t);l=local(t);x,y,z=l.mean(axis=0);wx,wy,wz=t.mean(axis=0);n=normal(t);ln=normal(l)
    if wz<=3.00001:return 6,'display base',None
    if plane(l,1,-21.1):return 2,'main stepped gable stone/brick major region','main_gable'
    if plane(l,1,-18.5) and ln[1]<-.9 and abs(x)<24.501 and z<64.801:return 2,'main front wall and upper brick window band','main_window_band'
    if plane(t,1,-46.5) and n[1]<-.9 and -62.001<wx<-29.999:return 2,'chapel front major brick/stone regions','chapel_front'
    c=0;role='unobserved side/rear/roof or unclassified surface neutral'
    if abs(x)<20 and -35<y<-18.5 and 3<z<25:c=2;role='main original entry frame/steps light stone proxy'
    if -59.6<wx<-32.4 and wy<-46.5 and 3<wz<7:c=2;role='chapel original approach steps light stone proxy'
    if abs(x)<18.501 and -30.001<y<-15.999 and 24.499<z<28.201 and ln[2]>.05:c=3;role='main existing short porch roof terracotta proxy'
    if -58.501<wx<-33.499 and -54.001<wy<-43.999 and 15.999<wz<18.801 and n[2]>.05:c=3;role='chapel existing short porch roof terracotta proxy'
    if plane(l,1,-16.25) and ln[1]<-.9 and abs(x)<19.001 and 27<z<48:c=4;role='main tall window original recessed backing'
    if plane(l,1,-17.5) and ln[1]<-.9 and 54<z<62 and abs(x)<24:c=4;role='main upper row original recessed window backing'
    if plane(l,1,-18.5) and (x-2)**2+(z-81)**2<9.01:c=4;role='main round window original backing'
    if plane(l,1,-26.5) and abs(x)<12.001 and 3<z<19:c=4;role='main entry original dark recessed backing'
    if -21.201<y<-15.999 and 26.799<z<48.201 and abs(x)<19.501:
        if any(abs(x-q)<.5501 for q in range(-15,16,5)) or any(q-.0001<z<q+1.1001 for q in [33,40]):c=5;role='main existing thickened glazing frame'
    if plane(t,1,-45) and 46<wz<54 and -61<wx<-31:c=4;role='chapel upper row original window backing'
    if plane(t,1,-44.5) and ((24<wz<40 and (abs(wx+56)<3.001 or abs(wx+36)<3.001)) or (3<wz<14 and abs(wx+46)<5.001)):c=4;role='chapel tall window/door original backing'
    if plane(t,1,-45.3) and any((wx-q)**2+(wz-11)**2<3.2**2+.01 for q in [-56,-36]):c=4;role='chapel round opening original backing'
    if -48.751<wy<-44.249 and 23.799<wz<40.201 and any(abs(wx-q)<.5501 for q in [-56,-36]):c=5;role='chapel existing thickened tall window frame'
    if -47.701<wy<-46.299 and -49.001<wx<-42.999 and 31.999<wz<40.001:c=2;role='chapel existing shallow cross light stone proxy'
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
        mask=MASKS[kind];regions=[(polygon.intersection(mask),1),(polygon.difference(mask),2)];area=0
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
    r,res=model_root('WZU Huayu Hall and Yong-Su Chapel - surface-subdivided appearance',pal);add_mesh(res,1,'Original envelope, conforming color subdivision',v,f,c);sub(sub(r,'build'),'item',objectid=1);write_zip(OUT/'huayu-appearance.3mf',r)
    report={'base_commit':'47148e04ad2323c8c50f0fa9f069116865d31162','source_stl':'../model.stl','source_sha256':SOURCE_SHA,'original_vertices':len(ov),'original_triangles':len(of),'vertices':len(v),'triangles':len(f),'face_material_indices':c,'original_triangle_for_each_output_face':parents,'material_face_counts':{pal[k]['id']:n for k,n in sorted(collections.Counter(c).items())},'original_role_face_counts':roles,'geometry_policy':'Conforming subdivision of existing triangular surfaces; no new volume or spatial structure. Original STL unchanged, output topology and face order differ.','color_regions':'Main stepped brick/stone and chapel large front panels are photo-proportional approximations, not surveyed brick joints.','color_limit':None,'closed_color_volumes':False,'printer_tool_mapping':None,'unverified':'side/rear/large roof tops neutral; no green roof or text added'}
    (OUT/'face-materials.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:x for k,x in report.items() if k not in ['face_material_indices','original_triangle_for_each_output_face']},ensure_ascii=False))
if __name__=='__main__':main()
