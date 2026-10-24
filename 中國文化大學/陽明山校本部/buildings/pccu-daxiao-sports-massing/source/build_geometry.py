#!/usr/bin/env python3
"""Independently authored historical approximate envelope, no image textures.
Boolean union preserves categorical source-face IDs, not nearest-pixel colors.
"""
import argparse, json, math
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh
P=argparse.ArgumentParser();P.add_argument('--out',type=Path,required=True);P.add_argument('--parameters',type=Path);a=P.parse_args()
root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
source=Path(__file__).resolve().parent.parent
params=json.loads((a.parameters or source/'parameters.json').read_text());palette=json.loads((source/'palette.json').read_text())
(root/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2)+'\n');(root/'palette.json').write_text(json.dumps(palette,ensure_ascii=False,indent=2)+'\n')
E=params['fitted']['ellipse']; O=params['observation_map']; I=params['implementation']; rules=[]
def rule(name,classification,evidence,note):
 rules.append(dict(index=len(rules),name=name,classification=classification,evidence=evidence,note=note));return len(rules)-1
R_UNKNOWN=rule('Plain hidden closure','inferred',[],'No window or equipment reconstruction; neutral is uncertainty, not observed material.')
R_SPORT=rule('Two sports hall zones','observed form / photo-fitted dimensions',['H2005','H2019','JJP'],'Two tall hall spaces 2–4 and 5–7; decorative grids are not floors.')
R_CROWN=rule('Inset sports crown and terrace','observed form / inferred sector placement',['J02','J03','H2019'],'Opaque and glazed segments; missing locations stay plain.')
R_CAP=rule('Shallow elliptical roof','observed envelope / inferred mathematical continuation',['H2005','H2019','J02'],'No exact ribs, seams, fittings or repaired roof condition claim.')
R_WING=rule('Orthogonal teaching arms','observed / inferred 10-and-8 height mapping',['H2017','J01','JJP'],'Coarse glazing and belts only on photographed outward faces; no exact pane counts.')
R_CORE=rule('Tall tan core','observed / photo-fitted',['H2019','J01'],'Simple core envelope; no unverified slit-window counts.')
R_WROOF=rule('Muted sloping teaching roof','observed envelope / inferred closure',['H2017','J01'],'Projecting shallow hip; geometry is not surveyed.')

def mesh(v,f,mats,rs):
    v=np.array(v,np.float32);f=np.array(f,np.uint32);tags=np.array(mats,np.uint32)+32*np.array(rs,np.uint32)
    t=trimesh.Trimesh(v,f,process=False)
    if t.volume<0: f=f[:,::-1].copy()
    s=mf.Manifold(mf.Mesh(v,np.ascontiguousarray(f),face_id=tags))
    assert s.status()==mf.Error.NoError, s.status()
    return s

def labeled(s,mat,r):
    mm=s.to_mesh();return mesh(mm.vert_properties,mm.tri_verts,[mat]*len(mm.tri_verts),[r]*len(mm.tri_verts))

def box(xy,z0,z1,mat=0,r=0):
    x0,y0,x1,y1=xy;return labeled(mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0)),mat,r)

def angworld(t,rad=1,z=0):
    t=math.radians(t);q=math.radians(E['rotation_deg']);u=E['radii'][0]*rad*math.cos(t);v=E['radii'][1]*rad*math.sin(t)
    return [E['center'][0]+u*math.cos(q)-v*math.sin(q), E['center'][1]+u*math.sin(q)+v*math.cos(q),z]

def sports_mat(t,z,crown=False):
    if not O['sports_observed_sector_degrees'][0]<=t<=O['sports_observed_sector_degrees'][1]:return 0,R_UNKNOWN
    if crown:
        if O['crown_glazed_sector_degrees'][0]<=t<=O['crown_glazed_sector_degrees'][1]:return 4,R_CROWN
        if O['crown_opaque_sector_degrees'][0]<=t<=O['crown_opaque_sector_degrees'][1]:return 2,R_CROWN
        return 0,R_UNKNOWN
    if z<E['base_top'] or E['hall1_top']<=z<=E['belt_top'] or z>=E['hall2_top']:return 2,R_SPORT
    if any(abs(t-c)<O['sports_pale_pier_half_width_degrees'] for c in O['sports_pale_piers_center_degrees']):return 2,R_SPORT
    if t%I['mullion_period_degrees']<I['mullion_width_degrees']+1e-5:return 5,R_SPORT
    if any(abs(z-q)<I['horizontal_mullion_thickness']/2+1e-5 for q in list(np.arange(E['base_top']+4.2,E['hall1_top'],4.6))+list(np.arange(E['belt_top']+4.2,E['hall2_top'],4.6))):return 5,R_SPORT
    return 3,R_SPORT

def ellipse(rings,crown=False,roof=False):
    angles=set(np.arange(0,360,I['ellipse_segment_degrees']).tolist())
    for t in np.arange(0,360,I['mullion_period_degrees']):angles.add(round(float(t+I['mullion_width_degrees']),5))
    for t in [120,355,145,200,205,350]+[c+d for c in O['sports_pale_piers_center_degrees'] for d in [-2.3,2.3]]:angles.add(t)
    angles=sorted(angles);n=len(angles);verts=[angworld(t,rad,z) for z,rad in rings for t in angles];faces=[];mats=[];rs=[]
    def tri(f,m,r):faces.append(f);mats.append(m);rs.append(r)
    for j in range(len(rings)-1):
        for i,t in enumerate(angles):
            k=(i+1)%n;mid=(t+(angles[k] if k else 360))/2;z=(rings[j][0]+rings[j+1][0])/2
            m,r=(6,R_CAP) if roof else sports_mat(mid,z,crown)
            # Unseen roof continuation deliberately neutral rather than asserted observed metal.
            if roof and not 120<=mid<=355:m,r=8,R_UNKNOWN
            tri([j*n+i,j*n+k,(j+1)*n+k],m,r);tri([j*n+i,(j+1)*n+k,(j+1)*n+i],m,r)
    # flat closed caps as fans, zero radius is intentionally avoided.
    for j,up in [(0,False),(len(rings)-1,True)]:
        ci=len(verts);verts.append([*E['center'],rings[j][0]])
        for i in range(n):
            k=(i+1)%n;f=[ci,j*n+i,j*n+k] if up else [ci,j*n+k,j*n+i]
            m,r=(8,R_UNKNOWN) if roof and up else (0,R_UNKNOWN)
            tri(f,m,r)
    return mesh(verts,faces,mats,rs)

zbreak=[0,E['base_top'],E['hall1_top'],E['belt_top'],E['hall2_top'],E['terrace_top']]
for q in list(np.arange(E['base_top']+4.2,E['hall1_top'],4.6))+list(np.arange(E['belt_top']+4.2,E['hall2_top'],4.6)):
    zbreak += [float(q-I['horizontal_mullion_thickness']/2),float(q+I['horizontal_mullion_thickness']/2)]
solids=[ellipse([(z,1)for z in sorted(zbreak)]),ellipse([(E['terrace_top']-.3,E['crown_radius_fraction']),(E['crown_top']+.2,E['crown_radius_fraction'])],crown=True)]
# Shallow continuous cap: thickness at edge plus a low paraboloidal rise.
roofedge=E['crown_top']+E['roof_edge_thickness'];rings=[(E['crown_top'],E['roof_radius_fraction']),(roofedge,E['roof_radius_fraction'])]
for rad in [0.90,0.78,0.64,0.48,0.30,0.12]:rings.append((roofedge+E['roof_rise']*(1-(rad/E['roof_radius_fraction'])**2),rad))
solids.append(ellipse(rings,roof=True))
# A few source-supported pale columns in the inset glazed sector; not a full invented ring.
for t in [150,167,184,197]:
    x,y,_=angworld(t,0.922);solids.append(labeled(mf.Manifold.cylinder(E['crown_top']-E['terrace_top']+.5,I['upper_column_radius'],I['upper_column_radius'],16).translate((x,y,E['terrace_top']-.2)),2,R_CROWN))

# Box shells contain color boundary topology; panel lines have no fragile protruding relief.
def wing(arm,axis):
    x0,y0,x1,y1=arm['xy'];top=arm['body_top'];ct=arm['crown_top'];zs={0.,5.,top}
    levels=9 if axis=='y' else 7
    bands=np.linspace(5,top-3,levels)
    for z in bands:zs.update([float(z),float(z+0.8)])
    zs=sorted(zs);v=[];f=[];m=[];r=[]
    # Surfaces are generated as a shared grid then welded. Face properties are categorical.
    sides=[((x0,y0),(x1,y0),False),((x1,y0),(x1,y1),True),((x1,y1),(x0,y1),axis=='y'),((x0,y1),(x0,y0),False)]
    for (ax,ay),(bx,by),obs in sides:
        length=math.hypot(bx-ax,by-ay);ss={0.,length}
        if obs:
            for s in np.arange(2.3,length,4.6):ss.update([float(s),float(min(s+.23,length))])
        ss=sorted(ss);start=len(v)
        for z in zs:
            for s in ss:v.append([ax+(bx-ax)*s/length,ay+(by-ay)*s/length,z])
        nn=len(ss)
        for j in range(len(zs)-1):
            for i in range(nn-1):
                zz=(zs[j]+zs[j+1])/2;ssmid=(ss[i]+ss[i+1])/2
                mat=0;rr=R_UNKNOWN
                if obs:
                    rr=R_WING;mat=3
                    if any(q<=zz<=q+.8 for q in bands):mat=4
                    if any(q<=ssmid<=q+.23 for q in np.arange(2.3,length,4.6)):mat=5
                    if zz<5:mat=4
                ids=[start+j*nn+i,start+j*nn+i+1,start+(j+1)*nn+i+1,start+(j+1)*nn+i]
                f.extend([[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]]);m.extend([mat,mat]);r.extend([rr,rr])
    # Top/bottom planar closure with boundary vertices, triangulated as fans.
    for z,up in [(0,False),(top,True)]:
        boundary=[]
        for (ax,ay),(bx,by),obs in sides:
            length=math.hypot(bx-ax,by-ay);ss={0.,length}
            if obs:
                for s in np.arange(2.3,length,4.6):ss.update([float(s),float(min(s+.23,length))])
            for s in sorted(ss)[:-1]:boundary.append([ax+(bx-ax)*s/length,ay+(by-ay)*s/length,z])
        ci=len(v);v.append([(x0+x1)/2,(y0+y1)/2,z]);start=len(v);v+=boundary
        for i in range(len(boundary)):
            ids=[ci,start+i,start+(i+1)%len(boundary)];f.append(ids if up else ids[::-1]);m.append(0);r.append(R_UNKNOWN)
    # Merge vertices at identical box edges without reordering triangles.
    arr=np.round(np.array(v),6);vv,inv=np.unique(arr,axis=0,return_inverse=True);s=mesh(vv,inv[np.array(f)],m,r)
    result=[s]
    inset=3.0
    # Upper recess is a plain solid, its visible surface is dark source-supported glass.
    upperxy=[x0+inset,y0+inset,x1-inset,y1-inset]
    upper=box(upperxy,top-.2,ct+.2,0,R_UNKNOWN)
    # A supported facade skin on the inset outward plane, with short return sides left neutral.
    if axis=='x':skin=[x1-inset-.3,y0+inset,x1-inset+.02,y1-inset]
    else:skin=[x0+inset,y1-inset-.3,x1-inset,y1-inset+.02]
    result += [upper,box(skin,top,ct,4,R_WING)]
    if axis=='x':cs=[(x1-1.4,y) for y in np.arange(y0+5,y1-3,10)]
    else:cs=[(x,y1-1.4) for x in np.arange(x0+5,x1-3,10)]
    for x,y in cs:result.append(labeled(mf.Manifold.cylinder(ct-top+.6,.9,.9,16).translate((x,y,top-.2)),2,R_WING))
    # Low hipped roof envelope, not a traditional tiled roof or exact structural section.
    e=I['wing_eave_projection'];z0=ct;z1=ct+I['wing_roof_edge_thickness'];z2=z1+arm['roof_rise']
    corners=lambda xx0,yy0,xx1,yy1,z:[[xx0,yy0,z],[xx1,yy0,z],[xx1,yy1,z],[xx0,yy1,z]]
    vv=corners(x0-e,y0-e,x1+e,y1+e,z0)+corners(x0-e,y0-e,x1+e,y1+e,z1)+corners(x0+5,y0+5,x1-5,y1-5,z2)
    ff=[[0,2,1],[0,3,2]];mm=[0,0];rr=[R_UNKNOWN,R_UNKNOWN]
    for j in [0,1]:
        for i in range(4):
            k=(i+1)%4;ff += [[4*j+i,4*j+k,4*(j+1)+k],[4*j+i,4*(j+1)+k,4*(j+1)+i]];mm += [7,7];rr += [R_WROOF,R_WROOF]
    ff += [[8,9,10],[8,10,11]];mm += [9,9];rr += [R_UNKNOWN,R_UNKNOWN]
    result.append(mesh(vv,ff,mm,rr));return result
solids+=wing(params['fitted']['north_arm'],'y');solids+=wing(params['fitted']['east_arm'],'x')
C=params['fitted']['core'];core=box(C['xy'],0,C['height']);cm=core.to_mesh();ct=trimesh.Trimesh(cm.vert_properties,cm.tri_verts,process=False)
observed=(ct.face_normals[:,2]**2<.1)&((ct.face_normals[:,0]<-.5)|(ct.face_normals[:,1]<-.5))
solids.append(mesh(cm.vert_properties,cm.tri_verts,np.where(observed,1,0),np.where(observed,R_CORE,R_UNKNOWN)))
# No base terrain, no backstage window duplication, no inferred equipment.
result=mf.Manifold.batch_boolean(solids,mf.OpType.Add)
# Simplified entrance recess visible in J01; solid dark backing, no invented door/window parts.
entry=params['fitted']['entrance_recess'];result=result-box(entry['xy'],-.1,entry['top'],4,R_WING)
for yy in [-2,16]:
    result=result+labeled(mf.Manifold.cylinder(entry['top']+.2,.9,.9,16).translate((77.3,yy,0)),2,R_WING)
assert result.status()==mf.Error.NoError
mm=result.to_mesh();vertices=np.array(mm.vert_properties[:,:3],np.float32);faces=np.array(mm.tri_verts,np.int32);tags=np.array(mm.face_id,np.int32)
# Manifold uses shared topology; material/source IDs attach to actual output faces.
materials=tags%32;rule_indices=tags//32
assert materials.max()<len(palette) and rule_indices.max()<len(rules)
t=trimesh.Trimesh(vertices,faces,process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
assert len(t.split(only_watertight=False))==1
np.savez_compressed(root/'mesh-data.npz',vertices=vertices,faces=faces,materials=materials,rule_indices=rule_indices)
t.export(root/'model.stl')
(root/'mapping-rules.json').write_text(json.dumps({'method':'Categorical source face IDs propagated through exact Boolean union; no pixels or textures. Face ids may subdivide but never nearest-neighbor paint.', 'rules':rules},ensure_ascii=False,indent=2)+'\n')
np.savetxt(root/'face-materials.csv',np.c_[np.arange(len(faces)),materials,rule_indices],fmt='%d',delimiter=',',header='triangle_index,material_index,evidence_rule_index',comments='')
report={'vertices':len(vertices),'triangles':len(faces),'bounds_display_mm':t.bounds.tolist(),'volume_display_mm3':float(t.volume),'surface_area_display_mm2':float(t.area),'one_connected_component':True,'watertight':True,'winding_consistent':True,'materials':{palette[i]['id']:int((materials==i).sum()) for i in range(len(palette))},'source_solids':len(solids),'physical_scale_claim':False}
(root/'qa'/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
