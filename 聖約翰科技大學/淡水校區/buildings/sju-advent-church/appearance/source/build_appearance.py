"""Bounded face annotations, not geometry generation. Run with Python 3 + lib3mf 2.5.
Uses the original ../model.stl. Never rewrites it, splits faces, or copies photo textures.
All coordinates in selectors are original design units: mm / 4.55 after subtracting base z=3.
"""
from pathlib import Path
import json, math, hashlib, collections, zipfile, xml.etree.ElementTree as ET
import lib3mf
from geometry_io import read_original, triangle_coordinate_sha, normal, area, EXPECTED_STL_SHA256
OUT=Path(__file__).resolve().parents[1]
EPS=2e-5
MATERIALS=[
 {'id':'unknown_neutral','hex':'#B4BDBB','evidence_status':'unverified placeholder'},
 {'id':'base_neutral','hex':'#74848A','evidence_status':'unverified model-base display contrast'},
 {'id':'shell_offwhite','hex':'#ECEBE5','evidence_status':'source-observed color family; display approximation'},
 {'id':'wall_pale_cream','hex':'#DAD5BB','evidence_status':'source-observed color family; display approximation'},
 {'id':'trim_light_gray','hex':'#AEB4B1','evidence_status':'source-observed color family; display approximation'},
 {'id':'front_glazing_dark','hex':'#38403F','evidence_status':'source-observed dark recess; not measured glass'},
 {'id':'upper_slot_dark','hex':'#41433D','evidence_status':'source-observed dark recess; not measured glass'},
 {'id':'lower_slot_dark','hex':'#41433D','evidence_status':'source-observed dark recess; not measured glass'},
]
REGIONS={}
def reg(key,material,sources,evidence,rule):
    REGIONS[key]={'material':material,'sources':sources,'evidence':evidence,'rule':rule}
reg('unmatched_original_faces','unknown_neutral',[],'No unique source registration or material boundary available.','Default; original face retained without subdivision.')
reg('abstract_base','base_neutral',[],'Original abstract model base, not an observed pavement color.','All three vertices z_mm <= 3.')
reg('cross_unresolved','unknown_neutral',[],'S1/S5 light versus S2/S3 brown appearance is unresolved; no metallic/bronze inference.','Original cross above design z=15; every vertex >=15.')
reg('crown_top_unseen','unknown_neutral',[],'Crown top unobserved in supplied views.','Horizontal surface at design z=15, upward normal.')
reg('undersides_unseen','unknown_neutral',[],'No paint inference from cast shadow.','Downward-facing building faces.')
reg('rear_door_unregistered','unknown_neutral',[],'S2 red service door lacks one-to-one registration; no red assignment.','Original cut back plane y=11.8, x=-3.9..-2.5, z=0.2..2.8.')
for label,axis,sign,sources in [('front',1,-1,['S1']),('rear',1,1,['S2','S3']),('side_minus_x',0,-1,['S1','S2']),('side_plus_x',0,1,['S3'])]:
    reg('shell_'+label,'shell_offwhite',sources,'Exposed white/warm-offwhite curved exterior; broad family only.','All vertices on original piecewise curved outer envelope and outward-facing; excludes slot interiors and undersides.')
    reg('crown_side_'+label,'shell_offwhite',sources,'Visible short square crown side continues pale shell.','All vertices on signed exterior plane at 1.6, z=14.4..15, outward normal; excludes horizontal top.')
    reg('upper_slot_back_'+label,'upper_slot_dark',sources,'Three narrow dark upper recesses; pale/unknown reveals are not darkened.','All vertices match original slot cut back curve a(z)-0.25, within one 0.4-wide slot and z=10.65..12.45; outward normal.')
    reg('fascia_outer_'+label,'trim_light_gray',sources,'Exposed light-gray fascia front face; weathering and exact shade omitted.','All vertices on outer plane at 14.5, z=4.2..4.55, outward horizontal normal; no soffit/top blanket.')
    reg('lower_wall_'+label,'wall_pale_cream',sources,'Source-exposed pale cream lower wall planes; no tile texture.','Exterior plane y=+/-12.1 or x=+/-12.1, bounded by original cross-plan body, z=0..4.2; no returns.')
reg('portal_front_frame','trim_light_gray',['S1'],'Light front portal/frame around dark entry; exact material composition not asserted.','Original outward plane y=-12.65, x=-6.4..6.4, z=0..3.6; reveals remain unknown.')
reg('canopy_front_edge','trim_light_gray',['S1'],'Visible light gray front canopy edge.','Original front plane y=-13, x=-8.3..8.3, z=3.6..4.2; top/soffit excluded.')
reg('portal_pier_fronts','trim_light_gray',['S1'],'Visible front faces of two major entrance supports.','Original front plane y=-12.85, x near +/-7.8 within 0.23, z=0..3.6; side/rear pier faces excluded.')
reg('front_center_glazing_backs','front_glazing_dark',['S1'],'Four horizontal rows with central division visibly dark; side doors not automatically equated.','Original back plane y=-12.25; all vertices within one central glazing cell; reveals/frame excluded.')
for label in ['rear','side_minus_x','side_plus_x']:
    reg('lower_slot_back_'+label,'lower_slot_dark',{'rear':['S2','S3'],'side_minus_x':['S1','S2'],'side_plus_x':['S3']}[label],'Source-matched narrow lower vertical recess backs; no glass tint claim.','Only exact original slot back planes and opening extents; no rear-door or reveal assignment.')

def inrange(values,lo,hi):return min(values)>=lo-EPS and max(values)<=hi+EPS
def plane(p,axis,v):return all(abs(q[axis]-v)<=EPS for q in p)
def bound(p,axis,lo,hi):return inrange([q[axis] for q in p],lo,hi)
def envelope(z):return 1.6+12.9*(1-(z-4.4)/10)**2.55

def interp(z,lo,step,count):
    k=max(0,min(count-1,int(math.floor((z-lo)/step+1e-9))))
    z0=lo+k*step;z1=z0+step;t=(z-z0)/step
    return envelope(z0)*(1-t)+envelope(z1)*t

DIRECTIONS=[('front',1,-1),('rear',1,1),('side_minus_x',0,-1),('side_plus_x',0,1)]
def classify(mm):
    p=[(q[0]/4.55,q[1]/4.55,(q[2]-3)/4.55) for q in mm]; n=normal(p)
    if max(q[2] for q in mm)<=3+EPS:return 'abstract_base'
    if min(q[2] for q in p)>=15-EPS and max(q[2] for q in p)>15+EPS:return 'cross_unresolved'
    if plane(p,2,15) and n[2]>.99:return 'crown_top_unseen'
    if n[2]<-.0001:return 'undersides_unseen'
    for label,axis,sign in DIRECTIONS:
        other=1-axis
        if n[axis]*sign<.05:continue
        if bound(p,2,4.4,14.4) and all(abs(sign*q[axis]-interp(q[2],4.4,.1,100))<EPS for q in p):return 'shell_'+label
        if bound(p,2,14.4,15) and plane(p,axis,sign*1.6):return 'crown_side_'+label
        if bound(p,2,10.65,12.45):
            for offset in [-.9,0,.9]:
                if bound(p,other,offset-.2,offset+.2) and all(abs(sign*q[axis]-(interp(q[2],10.65,.06,30)-.25))<EPS for q in p):return 'upper_slot_back_'+label
        if bound(p,2,4.2,4.55) and plane(p,axis,sign*14.5):return 'fascia_outer_'+label
        span=10.6 if axis==1 else 8.4
        if plane(p,axis,sign*12.1) and bound(p,2,0,4.2) and bound(p,other,-span,span):return 'lower_wall_'+label
    if n[1]<-.99:
        if plane(p,1,-12.65) and bound(p,0,-6.4,6.4) and bound(p,2,0,3.6):return 'portal_front_frame'
        if plane(p,1,-13) and bound(p,0,-8.3,8.3) and bound(p,2,3.6,4.2):return 'canopy_front_edge'
        if plane(p,1,-12.85) and bound(p,2,0,3.6) and any(bound(p,0,x-.23,x+.23) for x in [-7.8,7.8]):return 'portal_pier_fronts'
        if plane(p,1,-12.25):
            for xa,xb in [(-2.6,-.12),(.12,2.6)]:
                for za,zb in [(.3,.88),(1.08,1.66),(1.86,2.44),(2.64,3.15)]:
                    if bound(p,0,xa,xb) and bound(p,2,za,zb):return 'front_center_glazing_backs'
    if n[1]>.99:
        if plane(p,1,11.8) and bound(p,0,-3.9,-2.5) and bound(p,2,.2,2.8):return 'rear_door_unregistered'
        if plane(p,1,11.77) and bound(p,2,.55,3.6) and any(bound(p,0,x-.32,x+.32) for x in [-7,2.1,7]):return 'lower_slot_back_rear'
    for label,sign in [('side_minus_x',-1),('side_plus_x',1)]:
        if n[0]*sign>.99 and plane(p,0,sign*11.78) and bound(p,2,.65,3.55) and any(bound(p,1,y-.35,y+.35) for y in [-6.2,5.8]):return 'lower_slot_back_'+label
    return 'unmatched_original_faces'

def main():
    verts,faces=read_original(OUT.parent/'model.stl')
    groups={k:[] for k in REGIONS};labels=[];mat_ids={m['id']:i for i,m in enumerate(MATERIALS)};indices=[]
    for i,f in enumerate(faces):
        label=classify([verts[v] for v in f]); labels.append(label);groups[label].append(i);indices.append(mat_ids[REGIONS[label]['material']])
    for key,ids in groups.items():
        REGIONS[key]['face_count']=len(ids);REGIONS[key]['face_ids']=ids
        REGIONS[key]['area_mm2']=sum(area([verts[v] for v in faces[i]]) for i in ids)
    counts=collections.Counter(indices)
    for i,m in enumerate(MATERIALS):m['index']=i;m['face_count']=counts[i]
    payload={'schema':'original-face-material-annotation/1','source_stl_sha256':EXPECTED_STL_SHA256,'triangle_coordinate_sha256':triangle_coordinate_sha(verts,faces),'triangle_count':len(faces),'vertex_count_exact_deduplicated':len(verts),'geometry_changes':False,'material_indices':indices,'region_by_face':labels}
    (OUT/'face-materials.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    manifest={'scope':'Circa-2014 main church; bounded original-face appearance, no geometry/scale/printability change','coordinates':{'front':'-Y; not geodetic bearing','rear':'+Y','scale_mm_per_design_unit':4.55,'base_z_mm':3},'original_stl_sha256':EXPECTED_STL_SHA256,'triangle_coordinate_sha256':payload['triangle_coordinate_sha256'],'triangle_count':len(faces),'vertex_count':len(verts),'materials':MATERIALS,'regions':REGIONS,'unknown_faces':counts[0]+counts[1],'known_color_faces':len(faces)-counts[0]-counts[1],'rules':'All triangle vertices must satisfy the finite region selector; no centroid-only painting, triangle splitting, new geometry or texture. Unmatched faces are explicit unknown neutral.','palette_warning':'sRGB display choices are not calibrated reflectance or pigment, and are not an assertion of current 2026 paint.'}
    (OUT/'material-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    w=lib3mf.get_wrapper();model=w.CreateModel();model.SetUnit(lib3mf.ModelUnit.MilliMeter)
    mesh=model.AddMeshObject();mesh.SetName('SJU Advent Church - unchanged original triangles')
    v3=[];t3=[]
    for v in verts:
        a=lib3mf.Position();a.Coordinates[:]=v;v3.append(a)
    for f in faces:
        a=lib3mf.Triangle();a.Indices[:]=f;t3.append(a)
    mesh.SetGeometry(v3,t3)
    group=model.AddBaseMaterialGroup();pids=[]
    for m in MATERIALS:
        c=lib3mf.Color();rgb=bytes.fromhex(m['hex'][1:]);c.Red,c.Green,c.Blue,c.Alpha=*rgb,255
        pids.append(group.AddMaterial(m['id'],c))
    mesh.SetObjectLevelProperty(group.GetResourceID(),pids[0])
    for i,mi in enumerate(indices):
        prop=lib3mf.TriangleProperties();prop.ResourceID=group.GetResourceID();prop.PropertyIDs[:]=[pids[mi]]*3
        mesh.SetTriangleProperties(i,prop)
    assert mesh.IsManifoldAndOriented()
    model.AddBuildItem(mesh,w.GetIdentityTransform())
    writer=model.QueryWriter('3mf')
    target=OUT/'sju-advent-church-materials.3mf';writer.WriteToFile(str(target))
    # lib3mf's decimal formatter may introduce tiny rounding. Restore the exact
    # STL float32 coordinate values as round-trip decimal literals, without
    # changing any vertex, index, topology or material property. Deterministic ZIP.
    with zipfile.ZipFile(target) as z: entries={n:z.read(n) for n in z.namelist()}
    core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    ET.register_namespace('',core)
    root=ET.fromstring(entries['3D/3dmodel.model'])
    exported=root.findall('.//{'+core+'}vertex');assert len(exported)==len(verts)
    for element,v in zip(exported,verts):
        for axis,value in zip(('x','y','z'),v):element.set(axis,repr(value))
    # Optional random UUIDs are not needed for this single-object core file.
    for element in root.iter():
        for key in list(element.attrib):
            if key.endswith('}UUID'):del element.attrib[key]
    entries['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries.items()):
            info=zipfile.ZipInfo(name,(2026,10,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(json.dumps({'faces':len(faces),'materials':{m['id']:m['face_count'] for m in MATERIALS},'unknown':manifest['unknown_faces'],'3mf_written':True},indent=2))
if __name__=='__main__':main()
