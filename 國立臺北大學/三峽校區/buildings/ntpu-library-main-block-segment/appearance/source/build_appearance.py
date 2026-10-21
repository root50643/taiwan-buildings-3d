"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1c3e243f7690ccdc48492d27094a98953972df12517fda30827776a750450ac4'
PALETTE=[('neutral_mixed_curtainwalls_bridges_roof_and_ground','#AAA79F'),('source_offwhite_outer_curved_ribbons','#D9DAD5')]
def classify(tri):
 import math
 t=tri;candidate=np.flatnonzero(np.all(abs(t[:,:,0])>=58.29,axis=1)&np.all((t[:,:,2]>=3.9999)&(t[:,:,2]<=65.0001),axis=1));C=t[candidate]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_curtainwall_glass_opaque_panels_frames_bridges_roof_ground_neutral',dtype=object)
 def inside(r,points):
  u=r[1]-r[0];v=r[2]-r[0];d=points-r[0];uu=u@u;vv=v@v;uv=u@v;den=uu*vv-uv*uv
  a=((d@u)*vv-(d@v)*uv)/den;b=((d@v)*uu-(d@u)*uv)/den
  return (a>=-5e-5)&(b>=-5e-5)&(a+b<=1+5e-5)
 for side,spec in [(-1,[(-29,7.5,.1,4),(-13,7.8,2.4,6),(5,9.7,.2,5.7),(25,7.1,2.6,4.2)]),(1,[(-28,6.5,2.5,3),(-11,8.6,.2,4.9),(8,8,2.7,5.4),(28,6.1,.1,3.1)])]:
  for ri,(y0,width,phase,amp) in enumerate(spec):
   verts=[]
   for z in np.linspace(4,65,81):
    h=(z-4)/61;yc=y0+amp*math.sin(2*math.pi*h+phase);w=width*(1+.12*math.sin(2*math.pi*h+phase*.7));bow=3.2+2.2*math.sin(math.pi*h)**2;twist=1.4*math.sin(2*math.pi*h+phase)
    ring=[(side*58.3,yc-w/2,z),(side*(60+bow+twist),yc-w/2,z),(side*(60+bow-twist),yc+w/2,z),(side*58.3,yc+w/2,z)];verts.extend(ring[::-1] if side<0 else ring)
   faces=[[0,2,1],[0,3,2]]
   for k in range(80):
    for j in range(4):
     a=k*4+j;b=k*4+(j+1)%4;c=(k+1)*4+j;d=(k+1)*4+(j+1)%4;faces.extend([[a,b,d],[a,d,c]])
   faces.extend([[320,321,322],[320,322,323]])
   R=np.asarray(verts,dtype=np.float32).astype(float)[faces]
   for r in R:
    if np.all(abs(abs(r[:,0])-58.3)<1e-4):continue
    n=np.cross(r[1]-r[0],r[2]-r[0]);n/=np.linalg.norm(n);loc=np.flatnonzero(np.all(abs((C-r[0])@n)<5e-5,axis=1))
    ids=candidate[loc[np.all(inside(r,C[loc]),axis=1)]];color[ids]=1;why[ids]='original_float32_ribbon_triangle_plane_and_full_vertex_barycentric_side_'+str(side)
   for qi in range(0,len(R),2):
    rr=R[qi:qi+2]
    if np.all(abs(abs(rr[:,:,0])-58.3)<1e-4):continue
    n=np.cross(rr[0,1]-rr[0,0],rr[0,2]-rr[0,0]);n/=np.linalg.norm(n)
    if np.max(abs((rr.reshape(-1,3)-rr[0,0])@n))>5e-5:continue
    # Verify convex planar union before accepting Boolean retriangulation across its old diagonal.
    points=np.unique(rr.reshape(-1,3),axis=0);assert len(points)==4
    u=rr[0,1]-rr[0,0];u/=np.linalg.norm(u);v=np.cross(n,u);center=points.mean(axis=0);xy=np.stack(((points-center)@u,(points-center)@v),axis=1);xy=xy[np.argsort(np.arctan2(xy[:,1],xy[:,0]))]
    edges=np.roll(xy,-1,axis=0)-xy;cross=edges[:,0]*np.roll(edges,-1,axis=0)[:,1]-edges[:,1]*np.roll(edges,-1,axis=0)[:,0];assert np.all(cross>0)
    area=.5*abs(np.sum(xy[:,0]*np.roll(xy,-1,axis=0)[:,1]-xy[:,1]*np.roll(xy,-1,axis=0)[:,0]));areas=sum(np.linalg.norm(np.cross(r[1]-r[0],r[2]-r[0]))/2 for r in rr);assert abs(area-areas)<1e-4
    loc=np.flatnonzero(np.all(abs((C-rr[0,0])@n)<5e-5,axis=1));ok=np.all(inside(rr[0],C[loc])|inside(rr[1],C[loc]),axis=1);ids=candidate[loc[ok]];color[ids]=1;why[ids]='original_convex_planar_ribbon_quad_union_full_vertex_inside_side_'+str(side)
 assert (color==1).sum()==4379,int((color==1).sum())
 return color,why

def writezip(path,files):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files:
   info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
def main():
 (A/'qa').mkdir(exist_ok=True);(A/'previews').mkdir(exist_ok=True)
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
 tri=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)],dtype=np.float64).reshape(n,3,3)
 v,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
 colors,why=classify(tri);assert set(colors)==set(range(len(PALETTE)))
 # .17g exactly roundtrips every source float32 value as float64.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 model=E.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=E.SubElement(model,'resources');bm=E.SubElement(res,'basematerials',{'id':'20'})
 for name,color in PALETTE:E.SubElement(bm,'base',{'name':name,'displaycolor':color+'FF'})
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTPU Library Outer White Ribbons Only original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntpulib-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Five complete original designer photos on Liao architect library project page, no EXIF dates. Footer2015 is not photography date. Offwhite external S ribbons only','scope':'Eight original volumetric outer ribbons matched to original float32 loft triangle planes and convex planar quad unions, z4..65, whole triangles. Backing planes x+-58.3 excluded;4379facets. All mixed glass/opaque/frosted/metal curtainwalls, three mixed glass/solid bridges, roof tops, vestibule and ground neutral. No exact panel seams or extra geometry. Not entire IT complex or verified current2026 condition.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
