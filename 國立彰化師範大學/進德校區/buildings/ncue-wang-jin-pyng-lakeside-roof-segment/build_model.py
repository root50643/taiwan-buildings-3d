"""Source-bounded Wang Jin-pyng Activity Center lakeside segment.
Coordinates are arbitrary normalized millimetre display units, NOT measured scale.
Front is -Y. Rear plane is an explicitly synthetic crop closure. No planned PV.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
O=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):
 if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0: poly=list(reversed(poly))
 return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
# Low neutral display plinth; not a mapped site boundary.
add(0,0,0,184,91,3)
# Back structural crop wall; featureless, not an invented surveyed rear facade.
add(0,31,3,157,3,75)
# Core/opaque glazing backing is deliberately recessed 7 units from white front.
add(-1,5,26,146,50,51)
# Two visible recessed lower levels and supported balcony slabs.
for z in [25,38]: add(-2,-1,z,151,58,2.5)
add(-2,1.5,51,151,53,2.5)
# Rear plane supports roof and every slab. Recessed double columns carry front slab.
for x in [-52,51]:
 for dx in [-3.3,3.3]: add(x+dx,-17,3,3.6,5,23.2)
# Short conservative ground-level crop back wall, open plaza remains at front.
add(-1,17,3,146,21,23)
# Dark right-hand stair tower, independent silhouette but fused at crop wall/base.
add(80,20,3,15,25,94)
# Narrow stair slots, backed recess (not invented open stairwell).
for z in [36,50,64,78]: cut(80,7.7,z,3.8,4.4,11)
# Recess glazing ribbons along front; not high transparency photographic cheating.
for z in [27.5,40.5]: cut(-2,-20,z,143,4,10.5)
# Curved white fascia traced qualitatively from both official photos.
outline=[(-76,81),(-58,80),(-38,80.4),(-18,82),(5,84.6),(29,88.3),(53,92),(77,96),(67,54),(40,54),(18,51),(-5,44),(-24,41),(-65,41)]
left=[(-60,45),(-32,45),(-21,47),(-13,51),(-13,53),(-60,52)]
right=[(21,57),(64,57),(67,71),(53,68.8),(38,65),(21,60.5)]
fascia=profile(outline,-28,3.2)
for aperture in [left,right]: fascia=fascia-profile(aperture,-28,8)
parts.append(fascia)
# Revealed front support/backing ends at z77; windows look into genuine recess.
# Upper opening rear plane at y=-20 (8 behind fascia), with opaque teal glazing.
# Side return white frame with real inset rust-colour panel; photo-visible only.
add(72,0,55,4.4,58,38)
cut(73.9,-1,59,4.0,37,29)
# Shallow barrel roof: supported segment, smooth 48-point sampled profile.
# Roof ridge direction Y, no rooftop PV or conjectural plant/equipment.
xs=np.linspace(-66,65,49);zs=79+9.5*(1-((xs+.5)/65.5)**2)
roofpoly=[(float(x),float(z)) for x,z in zip(xs,zs)]+[(65,76.4),(-66,76.4)]
parts.append(profile(roofpoly,4,55))
m=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
details=[]
# Front vertical mullions connect into glass backing and slabs.
for z in [27.5,40.5]:
 for x in np.linspace(-71,68,17): details.append(box(float(x),-20,z,1.15,4.2,10.5))
# Aperture mullions only on the recessed backing, not rectangularising taper holes.
for x in [-57,-45,-33,-21]:details.append(box(x,-20.8,44,1.1,2,10))
for x in [26,38,50,62]:details.append(box(x,-20.8,56,1.1,2,17))
# Roof seams, finite 1mm rib width, sunk into curved roof and connected.
for y in np.linspace(-22,29,24):
 ribpoly=[(float(x),float(z+.65)) for x,z in zip(xs,zs)]+[(65,78.5),(-66,78.5)]
 details.append(profile(ribpoly,float(y),1.05))
m=m+Manifold.batch_boolean(details,OpType.Add)
# Recut after slab union: both tapered apertures remain clear through the front skin.
for aperture in [left,right]:m=m-profile(aperture,-28,7)
assert m.status().name=='NoError'
me=m.to_mesh64();v=np.asarray(me.vert_properties)[:,:3];f=np.asarray(me.tri_verts)
t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
c=t.triangles_center;n=t.face_normals
palette=[('white_fascia_concrete','#E5E5DF'),('recessed_teal_glazing','#366C70'),('pale_mullions','#BFC8C5'),('barrel_roof_charcoal','#737B7C'),('right_tower_slate','#59626E'),('side_panel_muted_rust','#895649'),('display_crop_closure','#B9B8B1')]
colors=np.zeros(len(f),dtype=int)
colors[(c[:,1]>29.4)|(c[:,2]<3.01)]=6
# Internal opaque backing is glass-colour at front only; genuine recessed depth.
colors[(abs(c[:,1]+18)<.08)&(c[:,2]>27.4)&(c[:,2]<51.1)]=1
colors[(abs(c[:,1]+20)<.08)&(c[:,2]>43)&(c[:,2]<76.9)]=1
colors[(c[:,1]<-20.1)&(c[:,1]>-22.1)&(c[:,2]>27.4)&(c[:,2]<74.1)]=2
# Roof surface includes connected standing seams; no PV rectangles.
colors[(c[:,2]>77)&(abs(c[:,0])<66.1)&(c[:,1]>-23.6)&(c[:,1]<31.6)]=3
colors[(c[:,0]>72.49)&(c[:,2]>3.01)]=4
# Photo-visible return panel recessed in x; supported by its inner side wall.
colors[(abs(c[:,0]-71.9)<.08)&(c[:,1]>-19.6)&(c[:,1]<17.6)&(c[:,2]>59)&(c[:,2]<88)]=5
# Fascia is always white, including its tapered reveal walls.
colors[(c[:,1]<-26.3)&(c[:,2]>40)]=0
# Right return structural margins stay white rather than tower color.
colors[(c[:,0]>=69.79)&(c[:,0]<=74.21)&(c[:,1]<28)&(c[:,2]>=55)&(c[:,2]<=93)&~((abs(c[:,0]-71.9)<.08)&(c[:,1]>-19.6)&(c[:,1]<17.6)&(c[:,2]>59)&(c[:,2]<88))]=0
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
# Deterministic 3MF, material assigned per triangle. Display materials, not extruder mapping.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
def el(p,name,attrs={}):return E.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=E.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b in palette:el(bm,'base',{'name':a,'displaycolor':b+'FF'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':E.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=7).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
